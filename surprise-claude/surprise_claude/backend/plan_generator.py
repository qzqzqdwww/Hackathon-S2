"""Call Claude API to generate a structured surprise learning plan.

The prompt is engineered to:
1. Present the randomly-picked domain as an unexpected gift
2. Force Claude to draw creative bridges to the user's stated interests
3. Structure output as a 4-week learning path with concrete activities
"""

import os
import json

# Model config — override via env var for flexibility
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


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


def generate_plan(interests: list, picked_domain: str) -> dict:
    """Generate a surprise learning plan via Claude API.

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
        If ANTHROPIC_API_KEY is not set.
    """
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. "
            "Export it or add it to a .env file."
        )

    client = anthropic.Anthropic(api_key=api_key)

    user_message = (
        f"My current interests are: {', '.join(interests)}.\n"
        f"Surprise me with a learning plan for: {picked_domain}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ],
    )

    content = response.content[0].text.strip()

    # Strip markdown fences if Claude adds them despite instructions
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
    if content.endswith("```"):
        content = content[:-3]

    return json.loads(content)
