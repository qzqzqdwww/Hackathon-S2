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

### Install

```bash
pip install git+https://github.com/qzqzqdwww/Hackathon-S2.git
```

Or clone and install:

```bash
# 1. Clone
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-claude

# 2. Install with your preferred AI provider
pip install -e .
pip install ".[anthropic]"   # Claude API (default)
pip install ".[openai]"       # OpenAI / compatible API
```

### Usage

```bash
# Interactive mode (recommended)
surprise-claude

# Direct mode with interests
surprise-claude "AI, 音乐, 摄影"

# Use OpenAI instead of Claude
surprise-claude --provider openai "AI, 音乐, 摄影"

# Choose animation style
surprise-claude -a lightning "编程, 设计"

# Adjust animation speed
surprise-claude -s 2.0 "烹饪, 旅行"

# List all available domains
surprise-claude --list-domains

# List animation styles
surprise-claude --list-animations

# List AI providers
surprise-claude --list-providers
```

### Set API Key

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
$env:OPENAI_API_KEY = "sk-..."
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
  -> AI 蜂群算法（Swarm Intelligence）正是受此启发

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

### Animation Styles

| Style | Description |
|-------|-------------|
| `default` | 藤条 (classic whip + golden particles) |
| `lightning` | 闪电 (electric bolts + instant strike) |
| `chain` | 链条 (metallic chain + heavy impact) |
| `laser` | 激光 (targeting + instant hit + trail) |

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
│       ├── domain_picker.py  # 49-domain pool + weighted random
│       ├── plan_generator.py # Multi-provider LLM (Claude / OpenAI)
│       └── mcp_server.py     # MCP stdio server
├── pyproject.toml
├── requirements.txt
└── README.md
```

### AI Providers

Surprise Claude supports multiple LLM backends:

| Provider | Env vars | Default model |
|----------|----------|---------------|
| **Anthropic Claude** (default) | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| **OpenAI / compatible** | `OPENAI_API_KEY` + optional `OPENAI_BASE_URL` | `gpt-4o-mini` |

```bash
# Use Claude (default)
surprise-claude "AI, 音乐, 摄影"

# Use OpenAI
surprise-claude --provider openai "AI, 音乐, 摄影"

# Or set via env var
$env:LLM_PROVIDER = "openai"
$env:OPENAI_API_KEY = "sk-..."
surprise-claude "AI, 音乐, 摄影"
```

Install with provider support:
```bash
pip install "surprise-claude[anthropic]"    # Claude only
pip install "surprise-claude[openai]"       # OpenAI only
pip install "surprise-claude[anthropic,openai]"  # Both
```

### Track 03 Alignment

| Requirement | Implementation |
|-------------|----------------|
| 对抗算法茧房 | Algorithm deliberately excludes user interests |
| 制造意外 | Weighted random favors "distant" domains |
| 轻量 | Single pip install, no ML framework needed |
| 真实场景 | Terminal-native, immediately usable by anyone |
| 开放原子 | Multi-provider support (Claude + OpenAI + compatible) |

---

## 中文

### 这是什么

Surprise Claude 是一个**终端原生**的 CLI 工具，专门用来打破你的算法茧房。

你输入自己感兴趣的领域——系统会**刻意避开**它们，随机选出一个你从未涉猎过的领域，并生成一份结构化的 4 周学习计划，同时画出与你的兴趣之间的意外关联桥。

**最好的发现，往往来自意外。**

### 快速开始

```bash
# 方式一：直接安装（需要 git）
pip install git+https://github.com/qzqzqdwww/Hackathon-S2.git

# 方式二：克隆后安装
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-claude
pip install -e .

# 安装 AI 引擎支持（至少选一个）
pip install ".[anthropic]"   # Claude API
pip install ".[openai]"      # OpenAI API
```

### 设置 API Key

```bash
# Claude (默认)
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
# macOS / Linux
export OPENAI_API_KEY="sk-..."
```

### 运行

```bash
# 使用 Claude（默认）
surprise-claude "AI, 音乐, 摄影"

# 使用 OpenAI
surprise-claude --provider openai "AI, 音乐, 摄影"

# 演示模式（无需 API Key）
surprise-claude --demo "AI, 音乐, 摄影"
```

### 使用方法

```bash
# 交互模式（推荐，可持续生成）
surprise-claude

# 直接输入兴趣
surprise-claude "AI, 音乐, 摄影"

# 使用 OpenAI 引擎
surprise-claude --provider openai "AI, 音乐, 摄影"

# 选择动画
surprise-claude -a lightning "编程, 设计"

# 列出所有领域
surprise-claude --list-domains
```

### 技术栈

| 组件 | 技术 |
|------|------|
| CLI 框架 | Typer |
| 终端 UI | Rich |
| AI 引擎 | Claude API / OpenAI API（可切换） |
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
