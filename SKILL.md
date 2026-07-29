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

Convert markdown experiment records into styled PPTX. Portable across devices.

## Quick Start

```bash
# Clone anywhere
git clone <repo-url> ppt-report
cd ppt-report

# Install deps (one-time)
pip3 install python-pptx matplotlib numpy

# Generate PPT
python3 scripts/generate_ppt.py -i experiments.md -o report.pptx
```

## How to Use

Place your markdown experiment record anywhere, then:

```bash
python3 path/to/ppt-report/scripts/generate_ppt.py \
  -i your_experiment.md \
  -o report.pptx
```

Scripts resolve their own location via `__file__` — no hardcoded paths.
All file references (images, charts) are resolved relative to the input markdown file,
so you can keep everything in one folder.

## Font Strategy (Cross-Device)

| Role | Font | Strategy |
|------|------|----------|
| Latin text | `+mn-lt` | Theme major font — Calibri Light on Office, auto on others |
| East Asian | `+mn-ea` | Theme EA font — DengXian/Yu Gothic on Office |
| Code | `Courier New` | Available on every OS |

The scripts use **PowerPoint theme fonts**, not hardcoded font names.
When opened on any device, PowerPoint/Keynote uses its own theme fonts —
no missing font warnings, consistent rendering.

Charts (matplotlib) auto-detect the best available CJK font at runtime
(PingFang on Mac, Microsoft YaHei on Windows, Noto on Linux).

## Style Guide

### Language
- **No filler words**: don't write "我们来看一下", "从图中可以看出", "这里展示的是"
- **Direct structure**: Model → Data → Train → Results → Analyze → Next
- **Numbers first**: lead every result with concrete metrics, not vague statements
- **Short bullets**: one fact per line, max ~20 words

### Slide Structure
```
┌─────────────────────────────────────┐
│ Topic Title (24pt)                  │
│ ─────────────────────────────────── │
│ ● Main point (L1, 20pt)            │
│ ○ Detail (L2, 18pt)                │
│ ○ Detail                           │
│                                     │
│ [chart / result image]              │
└─────────────────────────────────────┘
```

### Bullet Levels
| Markdown | PPT Level | Bullet |
|----------|-----------|--------|
| Plain text (no indent) | L0 | No bullet (section heading) |
| `- text` or `  text` | L1 | ● filled circle |
| `  - text` (2 spaces + dash) | L2 | ○ hollow circle |

## Markdown Format

```markdown
# 7.2 人像多实例进度         ← 标题页（第一个 #）

## 模型设计                  ← 新幻灯片

采用 Mask2Former（Swin-Large COCO instance 预训练）mmdet 框架

在内部数据集 Seg_data_39528 上 fine-tune，40K iter

### 评测口径                 ← L0 粗体子标题（同一页内）

- 预测实例与 GT 贪心匹配（IoU 0.5）
  - 同时惩罚漏检与误检       ← 次级 bullet

代码路径：/home/notebook/code/REPRODUCE.md  ← Courier 字体渲染

结果：**mIoU@0.5 = 0.974**  ← 粗体高亮关键数字

![可视化]($SKILL_HOME/assets/result.png)  ← 嵌入图片

---                          ← 手动分页

## 后续计划
```

## Dependencies

```bash
pip3 install python-pptx matplotlib numpy
```

## Chart Helper

```bash
python3 scripts/generate_chart.py \
  --type bar \
  --data "单人:0.974,多人:0.935,val_2q:0.930" \
  --output chart.png \
  --title "mIoU@0.5 对比"
```

## Table Renderer

```bash
python3 scripts/render_table.py \
  --data "模型|mIoU|FPS\nA|0.97|30\nB|0.94|45" \
  --output table.png
```
