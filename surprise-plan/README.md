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

- `Enter` — 重新生成（换一个陌生领域）
- `d` — 深入探索（对当前 PLAN 的某个主题展开）
- `e` — 导出 PLAN 到文件（.json / .md / .txt / .html）
- `n` — 切换动画样式
- `c` — 修改兴趣领域
- `q` — 退出

---

## 运行测试

```bash
python -m pytest tests/ -v
```

80 个 mock 测试，覆盖领域选取、配置管理、API 调用、CLI 入口、导出功能，无需真实 API Key。

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
│       ├── plan_exporter.py  # 多格式导出 (.json / .md / .txt / .html)
│       ├── provider.py       # 多 provider LLM 客户端
│       └── mcp_server.py     # MCP stdio 服务器
├── tests/                    # 80 个 pytest mock 测试
├── pyproject.toml
└── README.md
```

### 核心模块

| 模块 | 职责 |
|------|------|
| `cli.py` | Typer CLI：交互模式、直接模式、config 子命令、导出功能 |
| `display.py` | Rich 面板渲染 + 4 种 ASCII whip 动画（default/lightning/chain/laser） |
| `backend/domain_picker.py` | 159 个细分领域池，按学术分类组织；加权随机 + 语义距离评分 |
| `backend/plan_exporter.py` | PLAN 导出：自动检测格式，支持 json/md/txt/html |
| `backend/provider.py` | 多 provider 抽象：Anthropic + 所有 OpenAI 兼容 API，8k max_tokens |
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

| 版本 | 领域数 | 测试数 | 核心特性 | 下载方式 |
|------|--------|--------|----------|---------|
| **v2** (最新) | 159 | 80 | 8k token 深度生成 + 随机 seed + 多格式导出 + 交互导出 | `git clone` 默认获取 |
| **v1** | 159 | 68 | 回答"内容少+无互动"：丰富生成内容 + 交互模式 + 难度选择 + 随机 demo | `git clone --branch v1 <url>` |
| **v0** | 49 | 0 | 基础版本，固定内容，无交互 | `git clone --branch v0 <url>` |

### v2 更新内容（对比 v1）

#### 生成质量再提升

- **`max_tokens` 翻倍**：4096 → 8192，给模型更大输出空间
- **System Prompt 全面强化**，每个字段要求更具体、更深入：
  - `why_interesting`：4-5 句 → 6-8 句，要求开头有 vivid hook
  - `connections`：3-4 条 → 4-5 条，每条必须点明用户兴趣领域里的**具体概念**并解释精确映射关系
  - `key_terms`：5-6 个 → 6-8 个，每个带反直觉细节
  - `fun_fact`：1 句 → 2-3 句，必须是大多数人不知道的事实
  - `activities`：3-4 个/周 → 4-5 个/周，拒绝泛泛建议（如"读本书"），要求具体步骤 + 对照用户兴趣写对比笔记
  - `resources`：2-3 个/周 → 3-4 个/周，要求有具体书名/章节/视频标题
  - `surprise_factor`：1 句 → 2-3 句，回扣用户兴趣并留下新视角
  - Week 4 必须包含 **signature project**，综合四周内容并明确回连用户原始兴趣
- **随机 Seed 注入**：每次生成时注入 `1~999999` 随机数到 prompt，奇数 seed 从历史轶事切入，偶数从现代应用切入，确保每次生成角度不同、内容随机

#### 新增 PLAN 导出功能

- 支持 **4 种导出格式**：`.json`、`.md`（Markdown）、`.txt`（纯文本）、`.html`（带样式）
- 格式**自动检测**（根据文件扩展名）
- 自动创建目标文件的父目录
- 两种使用方式：
  - 命令行：`surprise-plan main --output plan.md "AI, 音乐"`
  - 交互模式：生成后按 `e` 键，输入文件路径即可导出

#### 交互模式增强

- 新增 `e`（导出）快捷键
- `_run()` 返回 `(pick, plan)` 元组，交互循环复用上次结果用于导出

#### 测试覆盖

- 从 68 个增至 **80 个** pytest mock 测试
- 新增导出功能测试（格式检测、文件创建、内容正确性、父目录创建）
- 新增随机 seed 测试（验证不同调用产生不同 prompt）

---

### v1 更新内容（对比 v0）

v1 直接回答了"Token消耗少、生成内容少、用户无互动"的反馈：

- **生成内容更丰富**：增加更多字段要求，每个字段输出更多细节
- **交互模式**：进入 `surprise-plan` 无参数即可进入交互 REPL，可持续生成新领域
- **难度选择**：支持 轻松入门 / 标准 / 深入挑战 三档
- **演示模式**：`--demo` 模式无需 API Key，内置随机模板生成演示 PLAN
- **动画系统**：4 种 whip 动画（default / lightning / chain / laser）
- **68 个 mock 测试**：覆盖领域选取、配置管理、API 调用、CLI 入口

---

### v0 → v1 → v2 完整对比

| 方面 | v0 | v1 | v2 |
|------|----|----|----|
| 领域池 | 49 | 159 | 159 |
| 测试数 | 0 | 68 | 80 |
| max_tokens | 4096 | 4096 | 8192 |
| why_interesting | 4-5 句 | 4-5 句 | 6-8 句 |
| connections | 3-4 条 | 3-4 条 | 4-5 条 |
| key_terms | 5-6 个 | 5-6 个 | 6-8 个 |
| fun_fact | 1 句 | 1 句 | 2-3 句 |
| activities/周 | 3-4 个 | 3-4 个 | 4-5 个 |
| resources/周 | 2-3 个 | 2-3 个 | 3-4 个 |
| surprise_factor | 1 句 | 1 句 | 2-3 句 |
| 随机性 | 无 | 无 | 随机 seed 注入 |
| 交互模式 | 无 | 有 | 有 + 导出 |
| 导出功能 | 无 | 无 | .json / .md / .txt / .html |
| 难度选择 | 无 | 有 | 有 |
| 演示模式 | 无 | 有 | 有 |

---

### 下载指定版本

```bash
# 下载最新版本（v2，即 main 分支）
git clone https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-plan

# 下载 v1（丰富内容 + 交互模式，159 领域池）
git clone --branch v1 https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-plan

# 下载 v0（基础版，49 领域池）
git clone --branch v0 https://github.com/qzqzqdwww/Hackathon-S2.git
cd Hackathon-S2/surprise-plan

# 在已克隆的仓库中切换
git tag                    # 查看所有可用版本
git checkout v1            # 切换到 v1
```

> 也可在 GitHub Releases 页面下载 ZIP：
> - [v2 (最新)](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v2)
> - [v1](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v1)
> - [v0](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v0)

---

## License

MIT — 自由使用、修改、分发。
