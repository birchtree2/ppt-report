---
name: ppt-report
description: >
  Generate concise, data-driven PowerPoint presentations from Markdown experiment records.
  Use when Codex needs to create technical PPTs for ML/AI research reporting — especially
  for internal team syncs, model training progress, evaluation results, and ablation studies.
  The output follows a proven style: direct facts, no fluff, precise metrics prominently shown,
  with charts and visualizations embedded. Triggers: user asks to "make a PPT", "生成汇报",
  "总结成PPT", or provides experiment Markdown records that need slide formatting.
---

# PPT Report Skill

Generates PowerPoint presentations from markdown experiment notes, following a concise,
fact-first reporting style with consistent formatting and embedded visualizations.

## Script Path Resolution

Scripts are bundled in the skill directory:

- `$CODEX_HOME/skills/ppt-report/scripts/generate_ppt.py` — Main PPT generator
- `$CODEX_HOME/skills/ppt-report/scripts/generate_chart.py` — Matplotlib chart generator
- `$CODEX_HOME/skills/ppt-report/scripts/render_table.py` — Table-to-image renderer

Always use absolute paths when calling these scripts. The skill root is
`/Users/ypy/.codex/skills/ppt-report/`.

## Font Strategy (Matching Original PPTs)

| Role | Font Name | Source |
|------|-----------|--------|
| Latin body | `Anthropic Sans` | 7.2-ypy.pptx |
| East Asian | `Microsoft YaHei` | 6.18-ypy.pptx |
| Code | `Courier` | 6.18-ypy.pptx |
| Title slides | `+mn-lt` (theme) | 6.18-ypy.pptx |

These are stored as font metadata in the PPTX. On devices without `Anthropic Sans`,
PowerPoint/Keynote automatically substitutes. East Asian text uses `Microsoft YaHei`
for Chinese readability on Windows/Mac.

## Style Guide

### Language (copy the boss)
- **No filler words**: never write "我们来看一下", "从图中可以看出", "这里展示的是"
- **Direct structure**: Model → Data → Train → Results → Analyze → Next
- **Numbers first**: Lead every result slide with concrete metrics
- **Short bullets**: One fact per line, max ~20 words

### Slide Structure
```
┌─────────────────────────────────────┐
│  Topic Title  (24pt, bold-ish)      │
│  ─────────────────────────────────  │
│  ● Main point (L1, 20pt)           │
│  ○ Detail (L2, 18pt)               │
│                                     │
│  [chart / result image]             │
└─────────────────────────────────────┘
```

### PPT-Style Lists
- L0 = section heading (no bullet, bold preferred)
- L1 = filled circle ● (main facts)
- L2 = hollow circle ○ (supporting detail)
- Indentation and bullet char are set explicitly in the PPTX XML

## Usage

```bash
python3 /Users/ypy/.codex/skills/ppt-report/scripts/generate_ppt.py \
  --input experiment.md \
  --output report.pptx

# With custom title
python3 .../generate_ppt.py -i exp.md -o r.pptx --title "7.2进度汇报"
```

## Markdown Format

```markdown
# Title Slide Text

## Section Title (new slide)

### Sub-heading (renders as L0 bold heading on same slide)

Key metric: **mIoU@0.5 = 0.974** (bold = highlighted)

- Bullet text (indent 0 → L1 bullet ●)
  - Sub bullet (indent 4 → L2 bullet ○)
    - Detail (indent 8 → L2 bullet ○)

![Visualization](path/to/image.png)

Code path: /home/notebook/code/REPRODUCE.md (renders in Courier)

---
(manual slide break)
```

## Dependency Setup

```bash
pip3 install --break-system-packages python-pptx matplotlib numpy
```

## Chart Helper

```bash
python3 .../generate_chart.py \
  --type bar \
  --data "单人:0.974,多人:0.935,val_2q:0.930" \
  --output chart.png \
  --title "mIoU@0.5 对比"
```

## Table Helper

```bash
python3 .../render_table.py \
  --data "模型|mIoU\nA|0.97\nB|0.94" \
  --output table.png
```
