# ppt-report

把 Markdown 实验记录一键生成技术汇报 PPT。

## AI Agent 自动安装

以下步骤可供 AI 代理（Codex 等）自动执行：

```bash
# 步骤 1：克隆仓库
git clone <repo-url> /tmp/ppt-report

# 步骤 2：安装 Python 依赖
pip3 install python-pptx matplotlib numpy

# 注意：如果遇到 --break-system-packages 错误，改用：
# pip3 install --break-system-packages python-pptx matplotlib numpy

# 步骤 3：验证安装
python3 /tmp/ppt-report/scripts/generate_ppt.py --help
```

安装完成后即可生成 PPT：

```bash
python3 /tmp/ppt-report/scripts/generate_ppt.py \
  -i experiments.md \
  -o report.pptx \
  --presenter "报告人"
```

## 安装（手动）

```bash
git clone <repo-url> ppt-report
cd ppt-report
pip3 install python-pptx matplotlib numpy
```

如果权限不足，加 `--break-system-packages`。

## 用法

```bash
python3 scripts/generate_ppt.py -i 实验记录.md -o 汇报.pptx

# 带姓名
python3 scripts/generate_ppt.py -i exp.md -o r.pptx --presenter "张三"

# 覆盖标题
python3 scripts/generate_ppt.py -i exp.md -o r.pptx --title "7.2 阶段汇报"
```

脚本不包含任何绝对路径，迁移到其他设备无需修改。

## Markdown 写法

```markdown
# 7.2 实验进度汇报         ← 标题页（第一个 #）

## 模型设计                ← ## 新建一页

采用 ViT-Large（ImageNet 预训练）

在内部数据集上 fine-tune，40K iter

### 评测口径               ← ### 当前页内粗体标题

- 结果：**Acc@0.5 = 0.974**   ← 粗体高亮
  - 同时惩罚漏检与误检          ← 次级 bullet

![可视化结果](result.png)       ← 嵌入图片

---                            ← 手动分页

## 后续计划
```

### Bullet 层级

| 写法 | 效果 |
|------|------|
| 无缩进文字 | 无 bullet（标题） |
| `- 文字` | ● 实心圆 |
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
  --title "准确率对比"
```

生成表格图：
```bash
python3 scripts/render_table.py \
  --data "模型|mIoU\nA|0.97\nB|0.94" \
  --output table.png
```

## 设计原则

- **字体**：可编辑文字默认统一宋体，同时设置主题、母版与默认文字样式，避免新增文字字体不一致；接收设备需安装宋体，图片内文字不受此设置影响
- **路径**：零绝对路径，脚本全凭 `__file__` 自定位
- **语言**：直球、数字先行、不说空话

## 许可

MIT
