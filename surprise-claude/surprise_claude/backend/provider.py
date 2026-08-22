"""LLM provider abstraction — supports ANY OpenAI-compatible API.

Works with:
- Anthropic Claude (messages.create API)
- OpenAI (chat.completions API)
- DeepSeek, Zhipu GLM, StepFun, Doubao, SiliconFlow, etc. (OpenAI-compatible)
- Any custom OpenAI-compatible endpoint

Priority: env vars > config file > defaults
"""

import json
import os

from .config import get_effective_config, get_provider_config, mask_key


SYSTEM_PROMPT = """\
You are the "Surprise Claude" — a mischievous learning guide whose mission is to \
break people out of their algorithmic filter bubbles. When a user tells you their \
interests, you NEVER recommend more of the same. Instead, you reach into an \
unexpected domain and show them something they didn't know they wanted to learn.

Your tone: enthusiastic, slightly conspiratorial, like you're sharing a secret. \
Use vivid language. Make the unfamiliar feel irresistible.

Output MUST be valid JSON matching this exact schema:
{
    "domain": "string — the picked domain name",
    "tagline": "string — one punchy sentence selling this domain",
    "why_interesting": "string — 2-3 sentences on what makes this domain fascinating",
    "connections": ["string", ...] — 2-3 creative bridges to the user's stated interests,
    "learning_path": [
        {
            "week": 1,
            "theme": "string",
            "activities": ["string", ...] — 2-3 concrete things to do,
            "resources": ["string", ...] — 1-2 specific resources
        },
        {
            "week": 2, ...
        },
        {
            "week": 3, ...
        },
        {
            "week": 4,
            "theme": "string — integration / connecting back to user's interests",
            "activities": ["string", ...],
            "resources": ["string", ...]
        }
    ],
    "surprise_factor": "string — a final, memorable line"
}

Do NOT include any text outside the JSON. No markdown fences. Raw JSON only."""


def _call_anthropic(api_key: str, model: str, user_message: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def _call_openai_compatible(api_key: str, model: str, base_url: str, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        max_tokens=2048,
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
    """Get the currently configured provider name."""
    cfg = get_effective_config()
    return cfg["provider"]


def get_config_summary() -> dict:
    """Get a display-safe summary of current config."""
    cfg = get_effective_config()
    provider = cfg["provider"]
    known = get_provider_config(provider)

    return {
        "provider": provider,
        "api_key": mask_key(cfg["api_key"]),
        "base_url": cfg["base_url"] or known["base_url"] or "(default)",
        "model": cfg["model"] or known["model"] or "(not set)",
        "config_file": cfg.get("config_file", ""),
    }


def generate_plan(interests: list, picked_domain: str) -> dict:
    """Generate a surprise learning plan via LLM API.

    Supports:
    - Anthropic Claude (provider=anthropic)
    - OpenAI (provider=openai)
    - DeepSeek (provider=deepseek)
    - Zhipu GLM (provider=zhipu)
    - StepFun (provider=stepfun)
    - Doubao (provider=doubao)
    - SiliconFlow (provider=siliconflow)
    - Any custom OpenAI-compatible API (provider=custom, set base_url)

    Priority for settings: env vars > config file > defaults

    Parameters
    ----------
    interests : list[str]
        The user's stated areas of interest.
    picked_domain : str
        The randomly selected domain (from domain_picker).

    Returns
    -------
    dict
        Structured plan matching the JSON schema.

    Raises
    ------
    EnvironmentError
        If the required API key is not set.
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
            f"  方式一：surprise-claude config set\n"
            f"  方式二：设置环境变量 {known['key_env']}=YOUR_KEY"
        )

    user_message = (
        f"My current interests are: {', '.join(interests)}.\n"
        f"Surprise me with a learning plan for: {picked_domain}"
    )

    if provider == "anthropic":
        content = _call_anthropic(api_key, model, user_message)
    else:
        # All other providers use OpenAI-compatible API
        if not base_url:
            known = get_provider_config(provider)
            base_url = known["base_url"]
        content = _call_openai_compatible(api_key, model, base_url, user_message)

    content = _strip_markdown_fences(content)
    return json.loads(content)
