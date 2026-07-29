---
name: ppt-report
description: >
  从 Markdown 实验记录生成简洁、数据驱动的技术汇报 PPT。
  用于 ML/AI 研究汇报场景：模型训练进展、评测结果、消融实验、中期/阶段验收。
  输出风格：不说空话、数字先行、结论明确、可视化嵌入。
  触发词：用户说"做个PPT"、"生成汇报"、"总结成PPT"、或给出实验记录的 Markdown 文件。
---

# PPT 汇报生成 Skill

把 Markdown 实验记录转成排版规范的 PPTX。全设备可迁移。

## 快速开始

```bash
# 克隆到任意位置
git clone <仓库地址> ppt-report
cd ppt-report

# 安装依赖（仅一次）
pip3 install python-pptx matplotlib numpy

# 生成 PPT
python3 scripts/generate_ppt.py -i experiments.md -o report.pptx
```

## 文件路径说明

- 脚本内不包含任何绝对路径，全凭 `__file__` 自定位
- 图片路径相对于输入的 markdown 文件解析
- 脚本在任意目录都能运行

```bash
python3 /path/to/ppt-report/scripts/generate_ppt.py -i my_exp.md -o my_report.pptx
```

## 字体策略（跨设备兼容）

| 角色 | 字体名 | 说明 |
|------|--------|------|
| 英文字体 | `+mn-lt` | PowerPoint 主题字体，Calibri Light |
| 中文字体 | `+mn-ea` | PowerPoint 主题东亚字体，Windows 上邓显/Mac 上苹方 |
| 代码路径 | `Courier New` | 全平台通用 |

使用 **PowerPoint 主题字体**，不是硬编码的具体字体名。PPT 在任何设备打开时，PowerPoint/Keynote 会自动使用当前主题的最合适字体，不会报缺字体。

图表（matplotlib）运行时自动检测系统中最好的中文字体（Mac 上 PingFang、Windows 上 微软雅黑、Linux 上 Noto Sans CJK）。

## 排版规范

### 语言风格（模仿老板的写法）
- **禁止空话**：不写"我们来看一下"、"从图中可以看出"、"这里展示的是"
- **直球结构**：模型 → 数据 → 训练 → 结果 → 分析 → 下一步
- **数字先行**：每页结果页第一句就摆具体数值
- **短句**：一行一条事实，不超过 20 字

### 幻灯片结构
```
┌─────────────────────────────────────┐
│ 主题标题（24pt）                    │
│ ─────────────────────────────────── │
│ ● 主要结论（L1，20pt）             │
│ ○ 细节说明（L2，18pt）             │
│ ○ 更多细节                         │
│                                     │
│ [图表 / 结果截图]                   │
└─────────────────────────────────────┘
```

### Bullet 层级
| Markdown 写法 | PPT 层级 | 显示效果 |
|---------------|----------|----------|
| 无缩进的文字 | L0 | 无 bullet（节标题） |
| `- 文字` 或 ` 文字` | L1 | ● 实心圆 |
| `  - 文字`（2空格+横杠） | L2 | ○ 空心圆 |

## Markdown 格式

```markdown
# 7.2 人像多实例进度         ← 标题页（第一个 #）

## 模型设计                  ← ## 新建幻灯片

采用 Mask2Former（Swin-Large COCO instance 预训练）

在 Seg_data_39528 上以 1024×1024 fine-tune，40K iter

### 评测口径                 ← ### 同级内 L0 粗体标题

- 预测实例与 GT 贪心匹配（IoU 0.5）
  - 同时惩罚漏检与误检       ← 次级 bullet

代码路径：/home/notebook/code/REPRODUCE.md  ← 自动 Courier 字体

**mIoU@0.5 = 0.974**        ← 粗体高亮关键数字

![可视化](result.png)        ← 嵌入图片

---                          ← 手动分页

## 后续计划                  ← 新幻灯片
```

## 依赖安装

```bash
pip3 install python-pptx matplotlib numpy
```

## 生成图表

```bash
python3 scripts/generate_chart.py \
  --type bar \
  --data "单人:0.974,多人:0.935,val_2q:0.930" \
  --output chart.png \
  --title "mIoU@0.5 对比"
```

## 生成表格图

```bash
python3 scripts/render_table.py \
  --data "模型|mIoU|FPS\nA|0.97|30\nB|0.94|45" \
  --output table.png
```
