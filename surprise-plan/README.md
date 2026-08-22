# Surprise-Plan

[English](#surprise-plan) | [中文](#中文)

**打破算法茧房 · 随机学习计划生成器**  
大工黑客松 S2 — Track 03 · 开放原子

---

## 这是什么

Surprise-Plan 是一个终端原生 CLI 工具。你输入自己的兴趣领域，系统**刻意避开**它们，随机选出一个你从未涉猎的领域，生成一份 4 周学习计划，并画出与你的兴趣之间的意外关联桥。

**最好的发现，往往来自意外。**

## English

Surprise-Plan is a terminal-native CLI tool that breaks you out of your algorithmic filter bubble.

You tell it your interests — it **deliberately excludes** them, then randomly selects an unfamiliar domain and generates a structured 4-week learning plan with creative bridges drawn back to what you already love.

**The best discoveries come from accidents.**

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-plan

# 安装
pip install -e .

# 安装 AI 引擎 SDK（至少选一个）
pip install ".[openai]"      # DeepSeek / 智谱 / 阶跃 / 豆包 / OpenAI
pip install ".[anthropic]"   # Claude
```

---

## 配置 API

支持任意 OpenAI 兼容 API：Claude、DeepSeek、智谱 GLM、阶跃星辰、豆包、SiliconFlow、OpenAI 等。

```bash
# 交互式配置（推荐）
surprise-plan config set

# 或直接设置环境变量
export DEEPSEEK_API_KEY="sk-..."
```

配置优先级：环境变量 > 配置文件 > 内置默认值

---

## 使用

```bash
# 交互模式（可持续生成）
surprise-plan

# 直接输入兴趣
surprise-plan "AI, 音乐, 摄影"

# 演示模式（无需 API Key）
surprise-plan main --demo

# 列出 159 个可选领域
surprise-plan --list-domains

# 列出动画样式
surprise-plan --list-animations
```

### 交互模式快捷键

- `Enter` — 重新生成
- `n` — 切换动画样式
- `s` — 设置 API
- `q` — 退出

---

## 运行测试

```bash
python -m pytest tests/ -v
```

68 个 mock 测试，覆盖领域选取、配置管理、API 调用、CLI 入口，无需真实 API Key。

---

## 架构

```
surprise-plan/
├── surprise_plan/
│   ├── __init__.py
│   ├── __main__.py           # python -m surprise_plan
│   ├── cli.py                # Typer CLI 入口
│   ├── display.py            # 终端动画 + 计划展示
│   └── backend/
│       ├── __init__.py
│       ├── config.py         # 持久化配置 (~/.surprise-plan/config.json)
│       ├── domain_picker.py  # 159 领域池 + 加权随机选取
│       ├── provider.py       # 多 provider LLM 客户端
│       └── mcp_server.py     # MCP stdio 服务器
├── tests/                    # 68 个 pytest mock 测试
├── pyproject.toml
└── README.md
```

### 核心模块

| 模块 | 职责 |
|------|------|
| `cli.py` | Typer CLI：交互模式、直接模式、config 子命令 |
| `display.py` | Rich 面板渲染 + 4 种 ASCII  whip 动画（default/lightning/chain/laser） |
| `backend/domain_picker.py` | 159 个细分领域池，按学术分类组织；加权随机 + 语义距离评分 |
| `backend/provider.py` | 多 provider 抽象：Anthropic + 所有 OpenAI 兼容 API |
| `backend/config.py` | 8 个内置 provider 默认值 + JSON 持久化 + env 优先级 |

---

## 支持的 AI 引擎

| 引擎 | 默认模型 | 环境变量 |
|------|---------|---------|
| Anthropic Claude | claude-sonnet-4-20250514 | `ANTHROPIC_API_KEY` |
| OpenAI | gpt-4o-mini | `OPENAI_API_KEY` |
| DeepSeek | deepseek-chat | `DEEPSEEK_API_KEY` |
| 智谱 GLM | glm-4-plus | `ZHIPU_API_KEY` |
| 阶跃星辰 | step-2-16k | `STEPFUN_API_KEY` |
| 豆包 | doubao-pro-32k | `DOUBAO_API_KEY` |
| SiliconFlow | Qwen/Qwen2.5-72B-Instruct | `SILICONFLOW_API_KEY` |
| Custom | (你指定) | `API_KEY` |

---

## 隐私

- API Key 存储在 `~/.surprise-plan/config.json`，已加入 `.gitignore`
- 仅向用户选择的 AI 引擎发送请求，不记录或分享任何数据
- Key 在界面中仅显示前 4 位 + 后 4 位

---

## 动画样式

| 样式 | 效果 |
|------|------|
| `default` | 藤条（经典鞭挞 + 金色粒子爆发） |
| `lightning` | 闪电（红色电流 + 瞬间打击） |
| `chain` | 链条（金属质感 + 沉稳打击） |
| `laser` | 激光（瞄准 + 瞬间命中 + 残影） |

---

## 历史版本

| 版本 | 说明 | 下载方式 |
|------|------|---------|
| **v1** | 159 领域池 + 全 provider 支持 + 68 个 mock 测试 + README 重写 | `git clone` 默认获取（`main` 分支） |
| **v0** | 初始版本（49 领域池，仅 Claude API，无测试） | `git clone --branch v1` 下载 v0 标签 |

### 下载指定版本

```bash
# 下载最新版本（main 分支）
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-plan

# 下载 v1（旧版本，49 领域池）
git clone --branch v1 https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-plan

# 在已克隆的仓库中查看所有标签
git tag
git checkout v1   # 切换到 v1
```

> GitHub Releases 页面也会提供每个版本的 ZIP 下载：
> `https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v1`

---

## License

MIT — 自由使用、修改、分发。
