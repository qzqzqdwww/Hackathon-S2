# Surprise Claude

[English](#surprise-claude) | [中文](#中文)

**打破算法茧房 · 随机学习计划生成器**
大工黑客松 S2 — Track 03 · 开放原子

---

## English

### What it does

Surprise Claude is a terminal-native CLI tool that breaks you out of your algorithmic filter bubble.

You tell it your interests — it **deliberately excludes** them, then randomly selects an unfamiliar domain and generates a structured 4-week learning plan with creative bridges drawn back to what you already love.

**The best discoveries come from accidents.**

### Privacy

API keys are stored locally in `~/.surprise-claude/config.json` (plaintext, git-ignored).
No data is sent anywhere except to your chosen AI provider's API. Your interests
and generated plans are never logged or shared.

### Install

```bash
# Direct install (requires git)
pip install git+https://github.com/qzqzqdwww/Hackathon-S2.git

# Or clone and install
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-claude
pip install -e .
```

### Configure API

Works with **any OpenAI-compatible API**: Claude, DeepSeek, Zhipu GLM, StepFun, Doubao, SiliconFlow, OpenAI, etc.

**Recommended — interactive setup:**
```bash
surprise-claude config set
# Follow prompts: select engine → enter API Key → save
```

**Or set environment variable directly:**
```bash
export DEEPSEEK_API_KEY="sk-..."
```

Install the OpenAI SDK (needed for all non-Claude providers):
```bash
pip install ".[openai]"     # DeepSeek, Zhipu, StepFun, Doubao, etc.
pip install ".[anthropic]"  # Claude only
pip install ".[all]"        # both
```

### Usage

```bash
# Interactive mode (recommended)
surprise-claude

# Direct mode
surprise-claude "AI, 音乐, 摄影"

# Demo mode (no API key needed)
surprise-claude --demo "AI, 音乐, 摄影"

# List all 70 domains
surprise-claude --list-domains

# List animation styles
surprise-claude --list-animations

# Manage API config
surprise-claude config set
surprise-claude config show
surprise-claude config clear
```

### Demo

```
$ surprise-claude "AI, 音乐, 摄影"

                            [TARGET] Surprise Claude
                           打破算法茧房 · 制造意外

                         你的兴趣: AI, 音乐, 摄影

                      即将为你随机揭示一个陌生领域...

                               |
                                |
                                 |
                                  |
                                   |
                                    \
                      /\_/
                    ( o.o )         =======
                      > ^ <                |
                    /|   |\                |
                   (_|   |_)               \
                                            |
                                            |
                                            |
                               * BOOM *
                      /\_/
                    ( >o< )
                      > w <
                    /|   |\
                   (_|   |_)
                *   +   .   :       * * *
                      ( *.* )
                        > ^ <
                      /|   |\
                     (_|   |_)
                               *

[TARGET] 养蜂 (Beekeeping)
"The rhythm of a hive is the tempo your music practice has been missing"

[SEARCH] 为什么学这个
┌──────────────────────────────────────────────┐
│ 养蜂是自然界最精密的分布式系统。一个蜂群由上 │
│ 万只蜜蜂组成，却没有任何中央控制——它们通过  │
│ "摇摆舞"传递信息，通过信息素协调行动。如果你 │
│ 对AI感兴趣，你会惊叹于这套没有算法的智能；如 │
│ 果你对音乐感兴趣，你会发现蜂群振翅的频率本身 │
│ 就是一首交响乐。                              │
└──────────────────────────────────────────────┘

[BRIDGE] 与你兴趣的意外关联
  -> 养蜂的"摇摆舞"通信协议是自然界最原始的舞蹈形式
  -> 微距摄影技巧可以直接迁移到蜂巢内部拍摄
  -> AI蜂群算法（Swarm Intelligence）正是受此启发

[MAP] 四周学习路径
┌──────────────────────────────────────────────┐
│ 第 1 周：蜂巢的社会结构与蜜蜂语言             │
│   - 阅读《The Honey Bee》前3章               │
│   - 观看蜜蜂摇摆舞纪录片                      │
│   - 画出蜂群信息传递流程图                    │
└──────────────────────────────────────────────┘

[SPARK] 意外之喜
┌──────────────────────────────────────────────┐
│ 当你用摄影师的眼光观察蜂巢，用算法工程师的思  │
│ 维理解蜂群，养蜂就不再是农业——它是一种你从未 │
│ 想过的、融合了艺术与科技的活体实验。          │
└──────────────────────────────────────────────┘
```

### Supported AI Providers

| Provider | Default model |
|----------|---------------|
| Anthropic Claude | claude-sonnet-4-20250514 |
| OpenAI | gpt-4o-mini |
| DeepSeek | deepseek-chat |
| Zhipu GLM | glm-4-plus |
| StepFun | step-2-16k |
| Doubao | doubao-pro-32k |
| SiliconFlow | Qwen/Qwen2.5-72B-Instruct |
| Custom OpenAI-compatible | (you specify) |

### Architecture

```
surprise-claude/
├── surprise_claude/
│   ├── __init__.py
│   ├── __main__.py          # python -m surprise_claude
│   ├── cli.py               # Typer CLI entry point
│   ├── display.py           # Terminal animations + plan display
│   └── backend/
│       ├── __init__.py
│       ├── config.py        # Persistent config (~/.surprise-claude/config.json)
│       ├── domain_picker.py # 70-domain pool + weighted random
│       ├── provider.py      # Multi-provider LLM client
│       └── mcp_server.py    # MCP stdio server
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 中文

### 这是什么

Surprise Claude 是一个**终端原生**的 CLI 工具，专门用来打破你的算法茧房。

你输入自己感兴趣的领域——系统会**刻意避开**它们，随机选出一个你从未涉猎过的领域，并生成一份结构化的 4 周学习计划，同时画出与你的兴趣之间的意外关联桥。

**最好的发现，往往来自意外。**

### 快速开始

```bash
# 克隆项目
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-claude
pip install -e .

# 安装 AI 引擎 SDK（至少选一个）
pip install ".[openai]"       # DeepSeek / 智谱 / 阶跃 / 豆包 / OpenAI
pip install ".[anthropic]"    # Claude
```

### 配置 API

支持任意 AI 引擎：Claude、DeepSeek、智谱 GLM、阶跃星辰、豆包、SiliconFlow 等。

**推荐 — 交互式配置：**
```bash
surprise-claude config set
# 按提示选择引擎 → 输入 API Key → 保存
```

**查看配置：**
```bash
surprise-claude config show
```

**清除配置：**
```bash
surprise-claude config clear
```

**或直接设置环境变量：**
```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY = "sk-..."

# macOS / Linux
export DEEPSEEK_API_KEY="sk-..."
```

### 运行

```bash
# 交互模式（推荐，可持续生成）
surprise-claude

# 直接输入兴趣
surprise-claude "AI, 音乐, 摄影"

# 演示模式（无需 API Key）
surprise-claude --demo "AI, 音乐, 摄影"

# 列出所有领域
surprise-claude --list-domains

# 列出动画样式
surprise-claude --list-animations
```

### 技术栈

| 组件 | 技术 |
|------|------|
| CLI 框架 | Typer |
| 终端 UI | Rich |
| AI 引擎 | 任意 API（Claude / DeepSeek / 智谱 / 阶跃 / 豆包 等） |
| 动画系统 | 纯终端 ANSI 字符动画 |
| MCP 集成 | stdio JSON-RPC 2.0 |

### 动画样式

| 样式 | 说明 |
|------|------|
| `default` | 藤条（经典鞭挞 + 金色粒子爆发） |
| `lightning` | 闪电（红色电流 + 瞬间打击） |
| `chain` | 链条（金属质感 + 沉稳打击） |
| `laser` | 激光（瞄准 + 瞬间命中 + 残影） |

### License

MIT — 自由使用、修改、分发。
