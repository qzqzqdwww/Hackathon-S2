"""Shared pytest fixtures for Surprise-Plan tests."""
import pytest


ENV_VARS = [
    "LLM_PROVIDER", "LLM_BASE_URL", "LLM_MODEL",
    "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL",
    "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "ZHIPU_API_KEY",
    "STEPFUN_API_KEY", "DOUBAO_API_KEY", "SILICONFLOW_API_KEY", "API_KEY",
]


@pytest.fixture(autouse=True)
def isolate_config(tmp_path, monkeypatch):
    """Isolate config to temp dir and clear env vars."""
    import surprise_plan.backend.config as config_mod

    fake_dir = tmp_path / ".surprise-plan"
    fake_dir.mkdir()
    monkeypatch.setattr(config_mod, "CONFIG_DIR", fake_dir)
    monkeypatch.setattr(config_mod, "CONFIG_FILE", fake_dir / "config.json")
    for key in ENV_VARS:
        monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def fake_config():
    return {
        "provider": "deepseek",
        "api_key": "sk-test-key-12345678",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    }
