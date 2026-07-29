#!/usr/bin/env python3
"""
Generate styled PPT from Markdown experiment records.

Font strategy (matching boss's original PPTs):
- Latin: Anthropic Sans
- East Asian: Microsoft YaHei
- Code: Courier
- Title slides: +mn-lt (theme font)
"""

import argparse
import os
import re
import sys

from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

# ── Layout (from boss's template) ──
SLIDE_W = 12192000
SLIDE_H = 6858000

TITLE_BAR_L = 838200
TITLE_BAR_T = 365125
TITLE_BAR_W = 10515600
TITLE_BAR_H = 1325563

BODY_L = 838200
BODY_T = 1825625
BODY_W = 10515600
BODY_H = 4351338

# ── Fonts (original PPT matching) ──
LATIN = "Anthropic Sans"
EA = "Microsoft YaHei"
CODE = "Courier"
TITLE_SLIDE_FONT = "+mn-lt"
TEXT_COLOR = RGBColor(0x0A, 0x0A, 0x0A)
SIZES = {0: Pt(24), 1: Pt(20), 2: Pt(18)}


def _rPr(run):
    rPr = run._r.find(qn("a:rPr"))
    if rPr is None:
        rPr = run._r.makeelement(qn("a:rPr"), {})
        run._r.insert(0, rPr)
    return rPr


def _set_font(run, size=Pt(24), bold=False, latin=LATIN, ea=EA):
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


def _set_code_font(run):
    _set_font(run, size=Pt(14), latin=CODE, ea="")


def _set_bullet(para, level):
    pPr = para._p.find(qn("a:pPr"))
    if pPr is None:
        pPr = parse_xml(f'<a:pPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
        para._p.insert(0, pPr)

    # Clear existing bullet settings
    for child in list(pPr.findall(qn("a:buChar"))):
        pPr.remove(child)
    for child in list(pPr.findall(qn("a:buNone"))):
        pPr.remove(child)

    # Map level to bullet char
    BCHAR = {0: None, 1: "●", 2: "○"}
    char = BCHAR.get(level, "●")
    if char:
        bu = pPr.makeelement(qn("a:buChar"), {"char": char})
        pPr.append(bu)
    else:
        bu = pPr.makeelement(qn("a:buNone"), {})
        pPr.append(bu)

    INDENT = {0: Emu(0), 1: Emu(254000), 2: Emu(508000)}
    marL = pPr.find(qn("a:marL"))
    if marL is None:
        marL = pPr.makeelement(qn("a:marL"), {})
        pPr.append(marL)
    marL.set("val", str(INDENT.get(level, Emu(0))))


# ── Slide builders ──

def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def title_slide(prs, main, presenter="杨培源"):
    s = _blank(prs)
    tb = s.shapes.add_textbox(Emu(0), Emu(2000000), SLIDE_W, Emu(1500000))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]
    p.alignment = 2
    r = p.add_run()
    r.text = main
    _set_font(r, Pt(44), True, TITLE_SLIDE_FONT)

    tb2 = s.shapes.add_textbox(Emu(0), Emu(4200000), SLIDE_W, Emu(500000))
    p2 = tb2.text_frame.paragraphs[0]
    p2.alignment = 2
    r2 = p2.add_run()
    r2.text = presenter
    _set_font(r2, Pt(16))


def content_slide(prs, title, bullets, images=None):
    s = _blank(prs)
    # Title bar
    tb = s.shapes.add_textbox(TITLE_BAR_L, TITLE_BAR_T, TITLE_BAR_W, TITLE_BAR_H)
    tb.text_frame.word_wrap = True
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = title
    _set_font(r, Pt(24))

    # Underline
    ln = s.shapes.add_shape(1, TITLE_BAR_L, TITLE_BAR_T + TITLE_BAR_H - Emu(10000),
                            TITLE_BAR_W, Emu(10000))
    ln.fill.background()
    ln.line.color.rgb = RGBColor(0xD0, 0xD0, 0xD0)
    ln.line.width = Pt(0.5)

    # Body
    if bullets:
        tb2 = s.shapes.add_textbox(BODY_L, BODY_T, BODY_W, BODY_H)
        tb2.text_frame.word_wrap = True
        for i, (text, level) in enumerate(bullets):
            p = tb2.text_frame.paragraphs[0] if i == 0 else tb2.text_frame.add_paragraph()
            p.space_after = Pt(6)
            _set_bullet(p, level)

            is_code = any(text.startswith(c) for c in ["code", "代码"]) or \
                      any(p in text for p in ["/home/", "REPRODUCE", ".md", ".py"])

            parts = re.split(r"(\*\*.*?\*\*)", text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run()
                    run.text = part[2:-2]
                    _set_font(run, SIZES.get(level, Pt(20)), True)
                else:
                    run = p.add_run()
                    run.text = part
                    if is_code:
                        _set_code_font(run)
                    else:
                        _set_font(run, SIZES.get(level, Pt(20)))

    # Images
    if images:
        for img_path in images:
            if os.path.exists(img_path):
                s.shapes.add_picture(img_path, BODY_L, int(BODY_T + BODY_H * 0.55),
                                     BODY_W, int(BODY_H * 0.4))


# ── Markdown parser ──

def parse_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    slides = []
    cur_type = None
    cur_title = ""
    cur_bullets = []
    cur_images = []
    in_code = False

    def flush():
        nonlocal cur_type, cur_title, cur_bullets, cur_images
        if cur_type == "title":
            slides.append(dict(type="title", title=cur_title, presenter="杨培源"))
        elif cur_type == "content":
            slides.append(dict(type="content", title=cur_title,
                               bullets=cur_bullets, images=cur_images))

    for raw in text.split("\n"):
        s = raw.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s:
            continue

        # # Title
        if re.match(r"^# [^#]", s):
            flush()
            cur_type = "title"
            cur_title = s[2:].strip()
            cur_bullets = []
            cur_images = []
            continue

        # Manual break
        if s == "---":
            flush()
            cur_type = None
            cur_title = ""
            cur_bullets = []
            cur_images = []
            continue

        # ## → new content slide
        if re.match(r"^## [^#]", s):
            flush()
            cur_type = "content"
            cur_title = s[3:].strip()
            cur_bullets = []
            cur_images = []
            continue

        # ### → L0 bullet (bold sub-heading)
        if re.match(r"^### ", s):
            cur_bullets.append((s[4:].strip(), 0))
            continue

        # Image
        m = re.match(r"!\[(.*?)\]\((.+?)\)", s)
        if m:
            p = m.group(2)
            if not os.path.isabs(p):
                base = os.path.dirname(path)
                c = os.path.join(base, p)
                if os.path.exists(c):
                    p = c
            cur_images.append(p)
            continue

        # Bullet level from leading whitespace
        lead = len(raw) - len(raw.lstrip())
        # Also count leading "- " or "* " markers
        text_only = re.sub(r"^[\s\-*+]*", "", raw)
        marker_len = len(raw) - len(text_only)
        # Use (marker_len // 2) to determine level
        level = min(2, marker_len // 2)

        text_clean = re.sub(r"^[\s\-*+.]+\s*", "", s)
        cur_bullets.append((text_clean, level))

    flush()
    return slides


# ── Main ──

def gen(slides, prs):
    for s in slides:
        if s["type"] == "title":
            title_slide(prs, s["title"], s.get("presenter", "杨培源"))
        else:
            content_slide(prs, s["title"], s.get("bullets", []), s.get("images", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True)
    ap.add_argument("-o", "--output", default="report.pptx")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    if not os.path.exists(a.input):
        print(f"Error: {a.input} not found", file=sys.stderr)
        sys.exit(1)
    slides = parse_md(a.input)
    if not slides:
        print("Error: no slides", file=sys.stderr)
        sys.exit(1)
    if a.title:
        for s in slides:
            if s["type"] == "title":
                s["title"] = a.title
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    gen(slides, prs)
    prs.save(a.output)
    print(f"✓ {a.output} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
