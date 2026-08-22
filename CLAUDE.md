# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **planning repository** for the 大工黑客松 S2 (Hackathon S2) challenge. It currently contains no application code — only a challenge brief and project planning documents.

## Current Contents

- `resouce/大工黑客松S2-赛题发布.pdf` — The hackathon challenge brief (Chinese). Read this first for the full challenge specification.
- `PLAN/plan.md` — Project planning document with track analysis, selection strategy, and tech stack recommendations. This is the primary planning artifact.
- `surprise-claude/` — Track 03 implementation: a terminal-native CLI tool "Surprise Claude" that generates random-domain learning plans to break filter bubbles.

## Track Choice

**Track 03** (开放原子 — 制造一点意外) has been selected.

Product: **Surprise Claude** — a terminal CLI tool. When the user inputs their interests, the system deliberately EXCLUDES them and randomly whips out a structured learning plan for an unfamiliar domain, with creative bridges drawn back to the user's stated interests.

## Surprise Claude Architecture

```
surprise-claude/
├── surprise_claude/
│   ├── __init__.py
│   ├── __main__.py          # python -m surprise_claude
│   ├── cli.py               # Typer CLI entry point (interactive + direct mode)
│   ├── display.py           # Terminal animations (ASCII art) + plan display (Rich)
│   └── backend/
│       ├── __init__.py
│       ├── domain_picker.py  # 49-domain pool + weighted random (excludes user interests)
│       ├── plan_generator.py # Claude API + engineered system prompt
│       └── mcp_server.py     # MCP stdio server (for Claude Desktop integration)
├── pyproject.toml           # Package config (pip installable)
├── requirements.txt         # Dependencies
├── README.md                # GitHub-facing documentation
└── LICENSE                  # MIT
```

### Key design decisions

- **Terminal-native**: Pure ASCII art animations, no browser needed. Works on Windows/macOS/Linux.
- **Domain picker**: Weighted random selection — domains in the same semantic field as user interests get lower weight, ensuring surprise.
- **Plan generator**: Engineered system prompt forces Claude to draw explicit creative bridges between random domain and user's interests.
- **4 animation styles**: default (whip), lightning, chain, laser — all frame-based ASCII art with ANSI colors.
- **Windows-safe**: All output uses ASCII-safe characters (no emoji in terminal output). UTF-8 encoding enforced on Windows.

### Running

```bash
cd surprise-claude
pip install -e .
export ANTHROPIC_API_KEY="sk-ant-..."
surprise-claude "AI, 音乐, 摄影"
```

Or:
```bash
python -m surprise_claude "AI, 音乐, 摄影"
```

### Publishing to GitHub

```bash
# Build and upload
pip install build twine
cd surprise-claude
python -m build
twine upload dist/*
```

## Environment & Permissions

- Claude Code settings (`.claude/settings.local.json`) allow `Bash(python *)` commands.
- `ANTHROPIC_API_KEY` environment variable is required for plan generation.
- No API keys or secrets should be committed to the repo.
