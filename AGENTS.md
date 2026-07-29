# Agent 安装指引

## 自动安装

```bash
# 1. 克隆
git clone <repo-url> /tmp/ppt-report

# 2. 安装 Python 依赖
pip3 install python-pptx matplotlib numpy

# 如果权限不足：
pip3 install --break-system-packages python-pptx matplotlib numpy

# 3. 完成
```

## 生成 PPT

```bash
python3 /tmp/ppt-report/scripts/generate_ppt.py \
  -i <markdown文件> \
  -o <输出.pptx> \
  --presenter "<报告人姓名>"
```
