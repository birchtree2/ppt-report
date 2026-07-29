# ppt-report

把 Markdown 实验记录一键生成技术汇报 PPT。

## 安装

```bash
# 1. 克隆
git clone <repo-url> ppt-report
cd ppt-report

# 2. 安装依赖
pip3 install python-pptx matplotlib numpy

# 3. 生成 PPT
python3 scripts/generate_ppt.py -i experiments.md -o report.pptx [--presenter "姓名"]
```

> 如果遇到 `pip3 install` 权限问题，加 `--break-system-packages`。

## 用法

```bash
# 基本用法
python3 scripts/generate_ppt.py -i 实验记录.md -o 汇报.pptx

# 指定姓名
python3 scripts/generate_ppt.py -i exp.md -o r.pptx --presenter "张三"

# 覆盖主标题
python3 scripts/generate_ppt.py -i exp.md -o r.pptx --title "7.2 阶段汇报"
```

脚本不包含任何绝对路径，迁移到其他设备无需修改。

## Markdown 写法

```markdown
# 7.2 人像多实例进度       ← 标题页（第一个 #）

## 模型设计                ← ## 新建一页

采用 Mask2Former（Swin-Large COCO 预训练）mmdet 框架

在 Seg_data_39528 上 fine-tune，40K iter

### 评测口径               ← ### 当前页内粗体标题

- 结果：**mIoU@0.5 = 0.974**  ← 粗体高亮
  - 同时惩罚漏检与误检          ← 次级 bullet

![可视化结果](result.png)       ← 嵌入图片

---                            ← 手动分页

## 后续计划
```

### Bullet 层级

| 写法 | 效果 |
|------|------|
| 无缩进文字 | 无 bullet（标题） |
| `- 文字` 或 ` 文字` | ● 实心圆 |
| `  - 文字` | ○ 空心圆 |

### 特殊语法

- `**数字**` → PPT 中加粗高亮
- `![alt](path)` → 嵌入图片
- 带 `/home/`、`.md`、`.py` 的行 → 自动 Courier 字体渲染
- `---` → 手动分页

## 辅助工具

生成图表：
```bash
python3 scripts/generate_chart.py \
  --type bar \
  --data "单人:0.974,多人:0.935,val_2q:0.930" \
  --output chart.png \
  --title "mIoU@0.5 对比"
```

生成表格图：
```bash
python3 scripts/render_table.py \
  --data "模型|mIoU\nA|0.97\nB|0.94" \
  --output table.png
```

## 设计原则

- **字体**：使用 PowerPoint 主题字体（`+mn-lt` / `+mn-ea`），不依赖具体字体文件，任何设备打开都不报缺字体
- **路径**：零绝对路径，脚本全凭 `__file__` 自定位
- **语言**：直球、数字先行、不说空话

## 许可

MIT
