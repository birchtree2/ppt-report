#!/usr/bin/env python3
"""
Generate styled PPTX from markdown experiment records.

Portable design:
  - No hardcoded paths (scripts resolve via __file__)
  - Theme fonts (+mn-lt / +mn-ea) delegate to PowerPoint's theme —
    works on any device without specific font installation
  - Bullet styles: ● L1 / ○ L2 (PowerPoint-native)
  - Matplotlib charts auto-detect CJK fonts

Usage:
  python3 scripts/generate_ppt.py -i experiments.md -o report.pptx
"""

import argparse, os, re, sys, datetime
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

# ── Layout (16:9, matched to boss's template) ──
SLIDE_W, SLIDE_H = 12192000, 6858000
TITLE_L, TITLE_T, TITLE_W, TITLE_H = 838200, 365125, 10515600, 1325563
BODY_L, BODY_T, BODY_W, BODY_H = 838200, 1825625, 10515600, 4351338

# ── Fonts: use theme fonts for cross-device compatibility ──
# +mn-lt = theme major Latin font (Calibri Light in Office)
# +mn-ea = theme major East-Asian font (DengXian Light / Yu Gothic)
# These let PowerPoint pick the right font on any device.
LATIN_FONT = "+mn-lt"
EA_FONT = "+mn-ea"
CODE_FONT = "Courier New"
TEXT_COLOR = RGBColor(0x0A, 0x0A, 0x0A)
SIZES = {0: Pt(24), 1: Pt(20), 2: Pt(18)}

# ── Bullet characters by level ──
BULLET = {0: None, 1: "●", 2: "○"}
INDENT = {0: Emu(0), 1: Emu(254000), 2: Emu(508000)}


# ── Font helpers ──

def _rPr(run):
    rPr = run._r.find(qn("a:rPr"))
    if rPr is None:
        rPr = run._r.makeelement(qn("a:rPr"), {})
        run._r.insert(0, rPr)
    return rPr


def set_font(run, size=Pt(24), bold=False, latin=LATIN_FONT, ea=EA_FONT):
    """Set both Latin and East-Asian fonts on a run."""
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = TEXT_COLOR
    run.font.name = latin
    rPr = _rPr(run)
    for tag, val in [("a:latin", latin), ("a:ea", ea)]:
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", val)


def set_code_font(run):
    """Set code/reference font."""
    set_font(run, Pt(14), latin=CODE_FONT, ea="")


def set_bullet(para, level):
    """Set bullet character + indent on a paragraph. level=0 → no bullet."""
    pPr = para._p.find(qn("a:pPr"))
    if pPr is None:
        pPr = parse_xml('<a:pPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
        para._p.insert(0, pPr)

    # Clear old bullets
    for tag in ("a:buChar", "a:buNone"):
        for el in list(pPr.findall(qn(tag))):
            pPr.remove(el)

    # Apply new bullet
    ch = BULLET.get(level)
    if ch:
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": ch}))
    else:
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))

    # Indent
    marL = pPr.find(qn("a:marL"))
    if marL is None:
        marL = pPr.makeelement(qn("a:marL"), {})
        pPr.append(marL)
    marL.set("val", str(INDENT.get(level, Emu(0))))


# ── Slide builders ──

def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def title_slide(prs, main, presenter=""):
    """Centered title slide with presenter name."""
    s = _blank(prs)
    tb = s.shapes.add_textbox(Emu(0), Emu(2000000), SLIDE_W, Emu(1500000))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]
    p.alignment = 2  # CENTER
    r = p.add_run()
    r.text = main
    set_font(r, Pt(44), True)

    tb2 = s.shapes.add_textbox(Emu(0), Emu(4200000), SLIDE_W, Emu(500000))
    p2 = tb2.text_frame.paragraphs[0]
    p2.alignment = 2
    r2 = p2.add_run()
    r2.text = presenter
    set_font(r2, Pt(16))
    # Date line (Chinese format)
    tb3 = s.shapes.add_textbox(Emu(0), Emu(4450000), SLIDE_W, Emu(400000))
    p3 = tb3.text_frame.paragraphs[0]
    p3.alignment = 2
    r3 = p3.add_run()
    r3.text = datetime.date.today().strftime("%Y年%m月%d日")
    set_font(r3, Pt(12))


def content_slide(prs, title, bullets, images=None):
    """Content slide: title bar + gray divider + bullet list + images."""
    s = _blank(prs)

    # Title bar
    tb = s.shapes.add_textbox(TITLE_L, TITLE_T, TITLE_W, TITLE_H)
    tb.text_frame.word_wrap = True
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = title
    set_font(r, Pt(24))

    # Gray divider under title
    ln = s.shapes.add_shape(1, TITLE_L, TITLE_T + TITLE_H - Emu(12000),
                            TITLE_W, Emu(12000))
    ln.fill.background()
    ln.line.color.rgb = RGBColor(0xD0, 0xD0, 0xD0)
    ln.line.width = Pt(0.5)

    # Body bullets
    if bullets:
        tb2 = s.shapes.add_textbox(BODY_L, BODY_T, BODY_W, BODY_H)
        tb2.text_frame.word_wrap = True
        for i, (text, level) in enumerate(bullets):
            p = tb2.text_frame.paragraphs[0] if i == 0 else tb2.text_frame.add_paragraph()
            p.space_after = Pt(6)
            set_bullet(p, level)

            # Detect code/reference lines
            is_code = any(text.startswith(c) for c in ["code", "代码"]) or \
                      any(p in text for p in ["/home/", "REPRODUCE", ".md", ".py"])

            # Parse **bold** markers
            parts = re.split(r"(\*\*.*?\*\*)", text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run()
                    run.text = part[2:-2]
                    set_font(run, SIZES.get(level, Pt(20)), True)
                else:
                    run = p.add_run()
                    run.text = part
                    set_code_font(run) if is_code else set_font(run, SIZES.get(level, Pt(20)))

    # Images
    if images:
        for img_path in images:
            if os.path.exists(img_path):
                try:
                    s.shapes.add_picture(
                        img_path,
                        BODY_L, int(BODY_T + BODY_H * 0.55),
                        BODY_W, int(BODY_H * 0.4))
                except Exception as e:
                    print(f"  ⚠ image skip ({e})", file=sys.stderr)


# ── Markdown parser ──

def parse_md(path):
    """Parse markdown → list of slide dicts.
    
    Returns: [{"type":"title"|"content", "title":str, "bullets":[(text,lvl)],
               "images":[path], "presenter":str}]
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()

    slides, in_code = [], False
    cur = {"type": None, "title": "", "bullets": [], "images": []}

    def flush():
        if cur["type"]:
            slides.append(dict(cur))

    for raw in text.split("\n"):
        s = raw.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s:
            continue

        if re.match(r"^# [^#]", s):       # # → title slide
            flush()
            cur = {"type": "title", "title": s[2:].strip(),
                   "presenter": "", "bullets": [], "images": []}
            continue

        if s == "---":                     # manual break
            flush()
            cur = {"type": None, "title": "", "bullets": [], "images": []}
            continue

        if re.match(r"^## [^#]", s):       # ## → content slide
            flush()
            cur = {"type": "content", "title": s[3:].strip(),
                   "bullets": [], "images": []}
            continue

        if re.match(r"^### ", s):          # ### → L0 heading inside slide
            cur["bullets"].append((s[4:].strip(), 0))
            continue

        m = re.match(r"!\[(.*?)\]\((.+?)\)", s)   # image
        if m:
            p = m.group(2)
            if not os.path.isabs(p):
                candidate = os.path.join(os.path.dirname(path), p)
                if os.path.exists(candidate):
                    p = candidate
            cur["images"].append(p)
            continue

        # Bullet level from leading whitespace
        marker_len = len(raw) - len(raw.lstrip())
        level = min(2, marker_len // 2)
        text_clean = re.sub(r"^[\s\-*+.]+\s*", "", s)
        cur["bullets"].append((text_clean, level))

    flush()
    return slides


# ── Main ──

def generate(slides, prs):
    for s in slides:
        if s["type"] == "title":
            title_slide(prs, s["title"], s.get("presenter", ""))
        elif s["type"] == "content":
            content_slide(prs, s["title"], s.get("bullets", []), s.get("images", []))


def main():
    ap = argparse.ArgumentParser(description="从 Markdown 实验记录生成 PPT 汇报")
    ap.add_argument("-i", "--input", required=True, help="输入的 Markdown 文件路径")
    ap.add_argument("-o", "--output", default="report.pptx", help="输出的 PPTX 文件路径")
    ap.add_argument("--title", default="", help="覆盖标题页的主标题")
    ap.add_argument("--presenter", default="", help="报告人姓名（显示在标题页）")
    a = ap.parse_args()

    if not os.path.exists(a.input):
        print(f"Error: {a.input} not found", file=sys.stderr)
        sys.exit(1)

    slides = parse_md(a.input)
    if not slides:
        print("Error: no slides generated", file=sys.stderr)
        sys.exit(1)

    if a.title:
        for s in slides:
            if s["type"] == "title":
                s["title"] = a.title
    if a.presenter:
        for s in slides:
            if s["type"] == "title":
                s["presenter"] = a.presenter

    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    generate(slides, prs)
    prs.save(a.output)
    print(f"✓ {a.output} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
