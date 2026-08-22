"""Tests for surprise_plan.backend.config."""
import pytest
from surprise_plan.backend.config import (
    KNOWN_PROVIDERS, clear_config, get_effective_config,
    get_provider_config, load_config, mask_key, save_config,
)


class TestMaskKey:
    def test_empty(self): assert mask_key("") == "(未设置)"
    def test_short(self): assert mask_key("12345678") == "12****"
    def test_normal(self): assert mask_key("sk-ant-1234567890abcdef") == "sk-a****cdef"
    def test_8_chars(self): assert mask_key("abcdefgh") == "ab****"
    def test_9_chars(self): assert mask_key("abcdefghi") == "abcd****fghi"


class TestProviderConfig:
    PROVIDERS = ["anthropic", "openai", "deepseek", "zhipu",
                 "stepfun", "doubao", "siliconflow", "custom"]

    def test_all_known(self):
        assert set(self.PROVIDERS) == set(KNOWN_PROVIDERS)
        assert len(KNOWN_PROVIDERS) == 8

    def test_deepseek(self):
        p = get_provider_config("deepseek")
        assert p == {"base_url": "https://api.deepseek.com/v1",
                      "model": "deepseek-chat", "key_env": "DEEPSEEK_API_KEY"}

    def test_anthropic(self):
        assert "claude" in get_provider_config("anthropic")["model"]

    def test_custom_fallback(self):
        p = get_provider_config("nonexistent")
        assert p["base_url"] == "" and p["model"] == "" and p["key_env"] == "API_KEY"

    def test_case_insensitive(self):
        assert get_provider_config("DEEPSEEK") == get_provider_config("deepseek")


class TestConfigFileIO:
    def test_load_empty(self):
        assert load_config() == {}

    def test_save_and_load(self):
        save_config({"provider": "openai", "api_key": "sk-abc"})
        c = load_config()
        assert c["provider"] == "openai" and c["api_key"] == "sk-abc"

    def test_clear(self):
        save_config({"provider": "test"})
        clear_config()
        assert load_config() == {}
        clear_config()  # idempotent


class TestGetEffectiveConfig:
    def test_defaults(self, monkeypatch):
        cfg = get_effective_config()
        assert cfg["provider"] == "anthropic"
        assert "claude" in cfg["model"]

    def test_file_values(self, monkeypatch):
        save_config({"provider": "deepseek", "api_key": "sk-file",
                      "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"})
        c = get_effective_config()
        assert c["provider"] == "deepseek" and c["api_key"] == "sk-file"

    def test_env_overrides_file(self, monkeypatch):
        save_config({"api_key": "sk-file", "provider": "deepseek"})
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-env")
        assert get_effective_config()["api_key"] == "sk-env"

    def test_generic_api_key_env(self, monkeypatch):
        save_config({"provider": "custom", "base_url": "https://example.com/v1"})
        monkeypatch.setenv("API_KEY", "sk-generic")
        assert get_effective_config()["api_key"] == "sk-generic"

    def test_no_key_empty(self):
        assert get_effective_config()["api_key"] == ""

    def test_config_file_path_in_output(self):
        assert ".surprise-plan" in get_effective_config()["config_file"]
