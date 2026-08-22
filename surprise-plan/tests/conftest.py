"""Shared pytest fixtures for Surprise-Plan tests."""
import json
import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def isolate_config(tmp_path, monkeypatch):
    """Isolate all config to a temp directory and clear related env vars."""
    fake_dir = tmp_path / ".surprise-plan"
    fake_dir.mkdir()

    # Patch CONFIG_DIR and CONFIG_FILE in the config module
    import surprise_plan.backend.config as config_mod
    monkeypatch.setattr(config_mod, "CONFIG_DIR", fake_dir)
    monkeypatch.setattr(config_mod, "CONFIG_FILE", fake_dir / "config.json")

    # Clear any env vars that could leak in
    for key in [
        "LLM_PROVIDER", "LLM_BASE_URL", "LLM_MODEL",
        "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL",
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "ZHIPU_API_KEY",
        "STEPFUN_API_KEY",
        "DOUBAO_API_KEY",
        "SILICONFLOW_API_KEY",
        "API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)

    yield


@pytest.fixture()
def fake_config():
    """Return a minimal valid config dict."""
    return {
        "provider": "deepseek",
        "api_key": "sk-test-key-12345678",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    }
