"""Persistent configuration for Surprise Claude.

Config file: ~/.surprise-claude/config.json
Fields: provider, api_key, base_url, model

Environment variables take precedence over config file values.
"""

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".surprise-claude"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Known providers and their defaults
KNOWN_PROVIDERS = {
    "anthropic": {
        "base_url": "",
        "model": "claude-sonnet-4-20250514",
        "key_env": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_env": "OPENAI_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-plus",
        "key_env": "ZHIPU_API_KEY",
    },
    "stepfun": {
        "base_url": "https://api.stepfun.com/v1",
        "model": "step-2-16k",
        "key_env": "STEPFUN_API_KEY",
    },
    "doubao": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-pro-32k",
        "key_env": "DOUBAO_API_KEY",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "key_env": "SILICONFLOW_API_KEY",
    },
    "custom": {
        "base_url": "",
        "model": "",
        "key_env": "API_KEY",
    },
}


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load config from file. Returns empty dict if no config exists."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict) -> None:
    """Save config to file."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def clear_config() -> None:
    """Delete the config file."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def get_provider_config(provider: str) -> dict:
    """Get default config for a known provider."""
    return KNOWN_PROVIDERS.get(provider.lower().strip(), KNOWN_PROVIDERS["custom"])


def get_effective_config() -> dict:
    """Get config with env vars overriding file values.

    Returns dict with keys: provider, api_key, base_url, model
    """
    cfg = load_config()
    provider = os.getenv("LLM_PROVIDER", cfg.get("provider", "anthropic")).lower().strip()

    known = get_provider_config(provider)
    key_env = known["key_env"]

    api_key = os.getenv(key_env) or os.getenv("API_KEY", "") or cfg.get("api_key", "")
    base_url = os.getenv("OPENAI_BASE_URL", os.getenv("LLM_BASE_URL", "")) or cfg.get("base_url", known["base_url"])
    model = os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "")) or cfg.get("model", known["model"])

    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "config_file": str(CONFIG_FILE),
    }


def mask_key(key: str) -> str:
    """Mask an API key for display."""
    if not key:
        return "(未设置)"
    if len(key) <= 8:
        return key[:2] + "****"
    return key[:4] + "****" + key[-4:]
