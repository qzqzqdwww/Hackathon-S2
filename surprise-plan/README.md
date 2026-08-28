# Surprise-Plan

[English](#english) | [中文](#中文)

**打破算法茧房 · 随机学习计划生成器**  
大工黑客松 S2 — Track 03 · 开放原子

---

## English

Surprise-Plan is a terminal-native CLI tool that breaks you out of your algorithmic filter bubble.

You tell it your interests — it **deliberately excludes** them, then randomly selects an unfamiliar domain and generates a structured 4-week learning plan with creative bridges drawn back to what you already love.

**The best discoveries come from accidents.**

---

## 中文

Surprise-Plan 是一个终端原生 CLI 工具。你输入自己的兴趣领域，系统**刻意避开**它们，随机选出一个你从未涉猎的领域，生成一份 4 周学习计划，并画出与你的兴趣之间的意外关联桥。

**最好的发现，往往来自意外。**

---

## 快速开始

**推荐方式**：下载 Release ZIP（不含 `.git` 文件夹）  
→ [GitHub Releases](https://github.com/qzqzqdwww/Hackathon-S2/releases)

```bash
# 1. 下载最新版本的 ZIP 并解压
# 2. 进入 surprise-plan 目录
cd surprise-plan

# 安装
pip install -e .

# 安装 AI 引擎 SDK（至少选一个）
pip install ".[openai]"      # DeepSeek / 智谱 / 阶跃 / 豆包 / OpenAI / SiliconFlow
pip install ".[anthropic]"   # Claude
```

> **注意**：请使用 GitHub Releases 下载的 ZIP 包，不要直接 `git clone`。  
> `git clone` 会下载 `.git` 文件夹（包含完整提交历史），占用额外空间且暴露提交记录。

### 配置 API

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

| 按键 | 功能 |
|------|------|
| `Enter` | 重新生成（换一个陌生领域） |
| `d` | 深入探索（对当前 PLAN 的某个主题展开） |
| `e` | 导出 PLAN 到文件（.json / .md / .txt / .html） |
| `n` | 切换动画样式 |
| `c` | 修改兴趣领域 |
| `q` | 退出 |

### 导出 PLAN

交互模式中按 `e` 键导出，系统会提示格式和路径示例：

```
e 导出

导出格式: .json 结构化数据 · .md Markdown · .txt 纯文本 · .html 网页（带样式）
示例: Documents\plan.md 或 Desktop\plan.html
导出文件路径 [plan.md]:
```

命令行直接导出：

```bash
surprise-plan main --output ~/Documents/plan.md "AI, 音乐"
surprise-plan main --output plan.json "AI, 音乐"
```

## 运行测试

```bash
python -m pytest tests/ -v
```

94 个 pytest mock 测试，覆盖领域选取、配置管理、API 调用、CLI 入口、导出功能、连接测试，无需真实 API Key。

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
├── tests/                    # 94 个 pytest mock 测试
├── pyproject.toml
└── README.md
```

### 核心模块

| 模块 | 职责 |
|------|------|
| `cli.py` | Typer CLI：交互模式、直接模式、config 子命令、导出功能 |
| `display.py` | Rich 面板渲染 + 4 种 ASCII whip 动画（default/lightning/chain/laser） |
| `backend/domain_picker.py` | 159 个细分领域池，按学术分类组织；加权随机 + 语义距离评分 |
| `backend/plan_exporter.py` | PLAN 导出：自动检测格式，支持 json/md/txt/html，HTML 转义防 XSS |
| `backend/provider.py` | 多 provider 抽象：Anthropic + 所有 OpenAI 兼容 API，8k max_tokens，连接测试 |
| `backend/config.py` | 8 个内置 provider 默认值 + JSON 持久化 + env 优先级 |
| `backend/mcp_server.py` | MCP stdio 服务器，供 Claude Desktop 等客户端调用 |

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
- 导出文件时自动转义 HTML 特殊字符，防止 XSS

---

## 动画样式

| 样式 | 效果 |
|------|------|
| `default` | 藤条（经典鞭挞 + 金色粒子爆发） |
| `lightning` | 闪电（红色电流 + 瞬间打击） |
| `chain` | 链条（金属质感 + 沉稳打击） |
| `laser` | 激光（瞄准 + 瞬间命中 + 残影） |

---

## 版本历史

| 版本 | 测试数 | 核心特性 |
|------|--------|----------|
| **v2** (最新) | 94 | 8k token 深度生成 + 随机 seed + 多格式导出 + API 连接测试 + XSS 防护 |
| **v1** | 68 | 丰富生成内容 + 交互模式 + 难度选择 + 随机 demo + 4 种动画 |
| **v0** | 0 | 基础版本，49 领域池，固定内容 |

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
- HTML 导出自动转义，防止 LLM 生成内容中的 XSS 攻击
- 两种使用方式：
  - 命令行：`surprise-plan main --output plan.md "AI, 音乐"`
  - 交互模式：生成后按 `e` 键，输入文件路径即可导出

#### API 连接测试

- 配置向导保存后自动询问是否测试 API 连接
- `provider.py` 新增 `test_api_connection()` 函数，发送 lightweight 请求（max_tokens=1）并测量延迟
- 错误自动分类：`auth` / `network` / `model` / `unknown`，并给出 actionable 建议

#### 代码质量

- API 调用增加 **120s 超时**，防止无限挂起
- 空响应 guard，防止 API 返回空内容时崩溃
- 全局状态不再被 demo 模式 mutate
- 修复 20+ 代码审查发现的问题（XSS、难度传递、deprecation warnings 等）
- **94 个 mock 测试**全部通过

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

### 全版本对比

| 方面 | v0 | v1 | v2 |
|------|----|----|----|
| 领域池 | 49 | 159 | 159 |
| 测试数 | 0 | 68 | 94 |
| max_tokens | 4096 | 4096 | 8192 |
| 超时保护 | 无 | 无 | 120s |
| 随机性 | 无 | 无 | 随机 seed 注入 |
| 交互模式 | 无 | 有 | 有 + 导出 |
| 导出功能 | 无 | 无 | .json / .md / .txt / .html |
| 难度选择 | 无 | 有 | 有 |
| 演示模式 | 无 | 有 | 有 |
| API 连接测试 | 无 | 无 | 有（内置配置向导） |
| XSS 防护 | 无 | 无 | 有 |

---

### 下载指定版本

所有版本均可在 [GitHub Releases](https://github.com/qzqzqdwww/Hackathon-S2/releases) 页面下载 ZIP 包（不含 `.git`）：

- [最新版本 (v2)](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v2)
- [v1](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v1)
- [v0](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v0)
> - [最新版本](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v2)
> - [v1](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v1)
> - [v0](https://github.com/qzqzqdwww/Hackathon-S2/releases/tag/v0)

---

## License

MIT — 自由使用、修改、分发。
