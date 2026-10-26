# myproject

[![CI](https://github.com/Nava123799/myproject/actions/workflows/ci.yml/badge.svg)](https://github.com/Nava123799/myproject/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> 一句话说清这个项目解决什么问题。

`myproject` 把任意文本转换成 URL 友好的 slug：`Hello, World!` → `hello-world`。

## 特性

- 纯标准库实现，零运行时依赖
- 完整类型标注（自带 `py.typed`）
- pytest 测试 + Ruff 检查，GitHub Actions 多版本矩阵 CI
- src 布局，可 `pip install` 也可 `python -m` 直接跑

## 安装

```bash
git clone git@github.com:Nava123799/myproject.git
cd myproject
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## 使用

命令行：

```bash
$ myproject "Hello, World!"
hello-world

$ echo "Café au Lait" | myproject
cafe-au-lait

$ myproject --version
myproject 0.1.0
```

作为库调用：

```python
from myproject import slugify

slugify("Hello, World!")  # 'hello-world'
slugify("naïve résumé")  # 'naive-resume'
```

或者不安装直接运行：

```bash
python -m myproject "Hello, World!"
```

## 开发

```bash
pytest                        # 跑测试
pytest --cov                  # 带覆盖率
ruff check .                  # 静态检查
ruff format .                 # 格式化
```

## 项目结构

```
.
├── .github/workflows/ci.yml   # CI：3.10–3.13 矩阵，lint + format + test
├── src/myproject/
│   ├── __init__.py            # 包入口，导出公共 API
│   ├── __main__.py            # 支持 python -m myproject
│   ├── cli.py                 # 命令行界面
│   ├── core.py                # 核心逻辑（无 I/O，易测试）
│   └── py.typed               # PEP 561 类型标记
├── tests/                     # 与 src 镜像对应的测试
├── pyproject.toml             # 项目元数据与工具配置
└── LICENSE
```

## 贡献

欢迎提 Issue 和 PR。提交前请确保 `ruff check .` 与 `pytest` 全部通过。

## 许可证

[MIT](LICENSE) © 2026 Gong Zhuoer
