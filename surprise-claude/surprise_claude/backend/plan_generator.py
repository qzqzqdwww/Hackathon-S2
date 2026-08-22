"""LLM provider abstraction — supports Anthropic Claude and OpenAI-compatible APIs.

Provider is selected via LLM_PROVIDER env var:
  - "anthropic" (default): uses ANTHROPIC_API_KEY
  - "openai": uses OPENAI_API_KEY, calls OPENAI_BASE_URL if set
"""

import os
import json


def _get_provider() -> str:
    return os.getenv("LLM_PROVIDER", "anthropic").lower().strip()


def _get_api_key(provider: str) -> str:
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise EnvironmentError(
                "LLM_PROVIDER=openai 但 OPENAI_API_KEY 未设置。"
            )
        return key
    # anthropic (default)
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. "
            "Export it or set LLM_PROVIDER=openai with OPENAI_API_KEY."
        )
    return key


def _get_model(provider: str) -> str:
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def _get_base_url(provider: str) -> str | None:
    if provider == "openai":
        return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return None


# Same prompt for all providers — engineered for JSON output
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
            "resources": ["string", ...] — 1-2 specific resources (books, videos, tools)
        },
        {
            "week": 2,
            ...
        },
        {
            "week": 3,
            ...
        },
        {
            "week": 4,
            "theme": "string — integration / connecting back to user's interests",
            "activities": ["string", ...],
            "resources": ["string", ...]
        }
    ],
    "surprise_factor": "string — a final, memorable line that drives home the unexpected connection"
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


def _call_openai(api_key: str, model: str, base_url: str, user_message: str) -> str:
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


def generate_plan(interests: list, picked_domain: str) -> dict:
    """Generate a surprise learning plan via LLM API.

    Supports Anthropic Claude (default) and OpenAI-compatible APIs.
    Set LLM_PROVIDER=openai to use OpenAI instead.

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
        If the required API key for the selected provider is not set.
    """
    provider = _get_provider()
    api_key = _get_api_key(provider)
    model = _get_model(provider)
    base_url = _get_base_url(provider)

    user_message = (
        f"My current interests are: {', '.join(interests)}.\n"
        f"Surprise me with a learning plan for: {picked_domain}"
    )

    if provider == "openai":
        content = _call_openai(api_key, model, base_url, user_message)
    else:
        content = _call_anthropic(api_key, model, user_message)

    content = _strip_markdown_fences(content)
    return json.loads(content)
