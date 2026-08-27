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

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def _call_openai_compatible(api_key: str, model: str, base_url: str, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()


def _strip_markdown_fences(content: str) -> str:
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


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


def generate_plan(interests: list, picked_domain: str, difficulty: str = "2") -> dict:
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
        "1": "轻松入门 — 用浅显有趣的方式讲解，少用专业术语，多用类比和故事",
        "2": "标准 — 理论与实践平衡，适合自学",
        "3": "深入挑战 — 硬核内容，大量实践项目，适合有基础的学习者",
    }
    diff_note = difficulty_map.get(str(difficulty), difficulty_map["2"])

    seed = random.randint(1, 999999)
    angle_hint = "odd seed: start from a surprising historical anecdote" if seed % 2 == 1 else "even seed: start from a surprising modern application"

    user_message = (
        f"[random_seed={seed}]\n"
        f"My current interests are: {', '.join(interests)}.\n"
        f"Surprise me with a learning plan for: {picked_domain}\n"
        f"Difficulty level: {diff_note}\n"
        f"Angle hint ({angle_hint})"
    )

    if provider == "anthropic":
        content = _call_anthropic(api_key, model, user_message)
    else:
        content = _call_openai_compatible(api_key, model, base_url, user_message)

    return json.loads(_strip_markdown_fences(content))
