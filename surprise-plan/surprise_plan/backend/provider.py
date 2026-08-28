"""LLM provider abstraction — supports ANY OpenAI-compatible API.

Works with:
- Anthropic Claude (messages.create API)
- OpenAI (chat.completions API)
- DeepSeek, Zhipu GLM, StepFun, Doubao, SiliconFlow, etc.
- Any custom OpenAI-compatible endpoint

Priority: env vars > config file > built-in defaults
"""

import json
import random
import re
import time

from .config import get_effective_config, get_provider_config, mask_key


SYSTEM_PROMPT = """\
You are the "Surprise-Plan" — a mischievous learning guide whose mission is to \
break people out of their algorithmic filter bubbles. When a user tells you their \
interests, you NEVER recommend more of the same. Instead, you reach into an \
unexpected domain and show them something they didn't know they wanted to learn.

Your tone: enthusiastic, slightly conspiratorial, like you're sharing a secret. \
Use vivid language. Make the unfamiliar feel irresistible. Write in Chinese.

## Randomness Requirement (CRITICAL)
Each request includes a random seed number. Use it to pick a UNIQUE angle, \
specific examples, and a distinct narrative voice. If seed is odd: start from \
a surprising historical anecdote. If seed is even: start from a surprising \
modern application. NEVER produce generic textbook content — every plan should \
feel hand-crafted and one-of-a-kind.

## Content Depth Requirements
- why_interesting: 6-8 sentences. Open with a vivid hook, explain 2-3 concrete \
  reasons this domain matters TODAY, connect each reason to the user's interests.
- connections: 4-5 creative bridges. Each bridge must name a SPECIFIC concept or \
  technique from the user's interests and explain EXACTLY how it maps to this domain.
- key_terms: 6-8 terms. Each term gets a one-line explanation that includes a \
  surprising or counter-intuitive detail.
- fun_fact: 2-3 sentences. Must be something most people in this domain don't know.
- learning_path: 4 weeks. Each week has:
  - theme: evocative title, not "Week 1 basics"
  - activities: 4-5 concrete, step-by-step actions. NOT generic advice like \
    "read a book" — instead "阅读《XXX》第2-3章，重点看作者如何解释YYY概念， \
    对比你在ZZZ领域的经验，写出300字对比笔记"
  - resources: 3-4 specific resources with titles and why they matter. \
    Prefer specific chapters/segments when possible.
  - Week 4 must include a "signature project" that synthesizes everything and \
    explicitly ties back to the user's original interests.

Output MUST be valid JSON matching this exact schema:
{
    "domain": "string — the picked domain name (Chinese + English)",
    "tagline": "string — one punchy sentence selling this domain",
    "why_interesting": "string — 6-8 sentences, vivid hook + 2-3 concrete reasons",
    "connections": ["string", ...] — 4-5 bridges naming specific concepts from user's interests,
    "key_terms": ["string", ...] — 6-8 terms with one-line explanations including surprising details,
    "fun_fact": "string — 2-3 sentences, something most people don't know",
    "learning_path": [
        {
            "week": 1,
            "theme": "string — evocative title",
            "activities": ["string", ...] — 4-5 concrete step-by-step actions,
            "resources": ["string", ...] — 3-4 specific resources with titles and rationale
        },
        {
            "week": 2, "theme": "...",
            "activities": ["...", ...],
            "resources": ["...", ...]
        },
        {
            "week": 3, "theme": "...",
            "activities": ["...", ...],
            "resources": ["...", ...]
        },
        {
            "week": 4,
            "theme": "string — integration / connecting back to user's interests",
            "activities": ["string", ...] — must include a signature synthesis project,
            "resources": ["string", ...]
        }
    ],
    "surprise_factor": "string — 2-3 sentences that tie the whole journey together \
    and leave the user with a fresh perspective on their own interests"
}

Be GENEROUS with content. Each week should feel like a real, detailed plan.
Do NOT include any text outside the JSON. No markdown fences. Raw JSON only."""


def _call_anthropic(api_key: str, model: str, user_message: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key, timeout=120.0)
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    if not response.content:
        raise ValueError("AI 返回了空响应，请重试。")
    return response.content[0].text.strip()


def _call_openai_compatible(api_key: str, model: str, base_url: str, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
    response = client.chat.completions.create(
        model=model,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    text = response.choices[0].message.content
    if not text:
        raise ValueError("AI 返回了空内容，请重试。")
    return text.strip()


def test_api_connection(provider: str, api_key: str, model: str, base_url: str = "") -> dict:
    """Lightweight API connectivity test. Returns status dict.

    Keys:
        ok: bool — whether the connection succeeded
        provider: str
        model: str
        base_url: str
        latency_ms: float (if ok)
        error: str (if not ok)
        error_type: str (if not ok) — "auth", "network", "model", "unknown"
    """
    cfg = get_effective_config()
    provider = provider or cfg.get("provider", "anthropic")
    api_key = api_key or cfg.get("api_key", "")
    model = model or cfg.get("model", "")
    base_url = base_url or cfg.get("base_url", "")

    if not api_key:
        return {"ok": False, "provider": provider, "error": "API Key 未设置",
                "error_type": "auth"}

    known = get_provider_config(provider)
    if provider != "anthropic" and not base_url:
        base_url = known["base_url"]

    target_model = model or known["model"]
    start = time.monotonic()
    try:
        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key, timeout=30.0)
            client.messages.create(
                model=target_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}],
            )
        else:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)
            client.chat.completions.create(
                model=target_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}],
            )
        latency = (time.monotonic() - start) * 1000
        return {
            "ok": True,
            "provider": provider,
            "model": target_model,
            "base_url": base_url or "(default)",
            "latency_ms": round(latency, 1),
        }
    except Exception as e:
        elapsed = time.monotonic() - start
        err_msg = str(e)
        error_type = _classify_api_error(err_msg)
        return {
            "ok": False,
            "provider": provider,
            "model": target_model,
            "base_url": base_url or "(default)",
            "latency_ms": round(elapsed * 1000, 1),
            "error": err_msg,
            "error_type": error_type,
        }


def _classify_api_error(err_msg: str) -> str:
    """Classify API error into a human-readable category."""
    lower = err_msg.lower()
    if any(k in lower for k in ("401", "403", "auth", "invalid api key", "unauthorized")):
        return "auth"
    if any(k in lower for k in ("timeout", "timed out", "connection", "network", "dns")):
        return "network"
    if any(k in lower for k in ("model", "not found", "404")):
        return "model"
    return "unknown"


_FENCE_RE = re.compile(r'(?s)^.*?```(?:json)?\s*\n?|\n?\s*```.*')


def _strip_markdown_fences(content: str) -> str:
    """Strip markdown code fences and any surrounding preamble/epilogue from LLM response."""
    return _FENCE_RE.sub('', content).strip()


def get_current_provider() -> str:
    return get_effective_config()["provider"]


def get_config_summary() -> dict:
    cfg = get_effective_config()
    provider = cfg["provider"]
    known = get_provider_config(provider)
    return {
        "provider": provider,
        "api_key": mask_key(cfg["api_key"]),
        "base_url": cfg["base_url"] or known["base_url"] or "(not set)",
        "model": cfg["model"] or known["model"] or "(not set)",
        "config_file": cfg.get("config_file", ""),
    }


def generate_plan(interests: list[str], picked_domain: str, difficulty: str = "2") -> dict:
    """Generate a surprise learning plan via LLM API.

    Supports: Claude, OpenAI, DeepSeek, Zhipu GLM, StepFun, Doubao,
    SiliconFlow, and any OpenAI-compatible API.

    Settings priority: env vars > config file > built-in defaults.
    """
    cfg = get_effective_config()
    provider = cfg["provider"]
    api_key = cfg["api_key"]
    model = cfg["model"]
    base_url = cfg["base_url"]

    if not api_key:
        known = get_provider_config(provider)
        raise EnvironmentError(
            f"API Key 未设置。\n"
            f"  方式一：surprise-plan config set\n"
            f"  方式二：设置环境变量 {known['key_env']}=YOUR_KEY"
        )

    if provider != "anthropic" and not base_url:
        known = get_provider_config(provider)
        base_url = known["base_url"]
        if not base_url:
            raise EnvironmentError(
                f"API 地址未设置。\n"
                f"  运行 surprise-plan config set --provider {provider} --base-url YOUR_URL"
            )

    difficulty_map = {
        "1": "平衡 — 理论与实践兼顾，适合自学",
        "2": "深入 — 硬核内容，大量实践项目，适合有基础的学习者",
        "3": "深入 — 硬核内容，大量实践项目，适合有基础的学习者",
    }
    diff_note = difficulty_map.get(str(difficulty), difficulty_map["1"])

    max_retries = 2
    last_err = None
    for attempt in range(1, max_retries + 1):
        seed = random.randint(1, 999999)
        angle_hint = "奇数种子：从令人惊讶的历史轶事切入" if seed % 2 == 1 else "偶数种子：从令人惊讶的现代应用切入"

        user_message = (
            f"[random_seed={seed}]\n"
            f"My current interests are: {', '.join(interests)}.\n"
            f"Surprise me with a learning plan for: {picked_domain}\n"
            f"Difficulty level: {diff_note}\n"
            f"Angle hint ({angle_hint})"
        )

        try:
            if provider == "anthropic":
                content = _call_anthropic(api_key, model, user_message)
            else:
                content = _call_openai_compatible(api_key, model, base_url, user_message)
        except ValueError:
            last_err = "empty"
            if attempt < max_retries:
                continue
            raise ValueError(
                "AI 返回了空内容，多次重试后仍然失败。\n"
                "  可能原因：\n"
                "  1. 模型 max_tokens 限制不足（当前模型：{}）\n"
                "  2. API 限流或服务暂时不可用\n"
                "  建议：\n"
                "  - 尝试切换到更强的模型（如 gpt-4o-mini、deepseek-chat）\n"
                "  - 运行 surprise-plan config set 更换模型\n"
                "  - 稍后再试".format(model)
            )
        except Exception as e:
            last_err = str(e)
            if attempt < max_retries:
                continue
            raise RuntimeError(f"AI 调用失败 [{provider}]: {last_err}") from e
        else:
            break  # success

    try:
        return json.loads(_strip_markdown_fences(content))
    except json.JSONDecodeError:
        raise ValueError("AI 返回的内容无法解析为 JSON，请重试或更换模型。")
