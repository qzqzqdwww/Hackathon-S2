"""Tests for surprise_plan.backend.config."""
import json
import os

import pytest

from surprise_plan.backend.config import (
    KNOWN_PROVIDERS,
    clear_config,
    get_effective_config,
    get_provider_config,
    load_config,
    mask_key,
    save_config,
)


class TestMaskKey:
    """Test API key masking for safe display."""

    def test_empty_key(self):
        assert mask_key("") == "(未设置)"

    def test_none_key(self):
        assert mask_key("") == "(未设置)"

    def test_short_key(self):
        """Keys <= 8 chars: show first 2 + ****"""
        assert mask_key("12345678") == "12****"

    def test_normal_key(self):
        """Normal keys: first 4 + **** + last 4"""
        assert mask_key("sk-ant-1234567890abcdef") == "sk-a****cdef"

    def test_exactly_8_chars(self):
        """8-char key uses short format."""
        assert mask_key("abcdefgh") == "ab****"

    def test_9_char_key(self):
        """9-char key uses long format (first 4 + last 4)."""
        assert mask_key("abcdefghi") == "abcd****fghi"


class TestProviderConfig:
    """Test built-in provider defaults."""

    def test_known_providers_exist(self):
        assert "anthropic" in KNOWN_PROVIDERS
        assert "openai" in KNOWN_PROVIDERS
        assert "deepseek" in KNOWN_PROVIDERS
        assert "zhipu" in KNOWN_PROVIDERS
        assert "stepfun" in KNOWN_PROVIDERS
        assert "doubao" in KNOWN_PROVIDERS
        assert "siliconflow" in KNOWN_PROVIDERS
        assert "custom" in KNOWN_PROVIDERS
        assert len(KNOWN_PROVIDERS) == 8

    def test_deepseek_defaults(self):
        p = get_provider_config("deepseek")
        assert p["base_url"] == "https://api.deepseek.com/v1"
        assert p["model"] == "deepseek-chat"
        assert p["key_env"] == "DEEPSEEK_API_KEY"

    def test_anthropic_defaults(self):
        p = get_provider_config("anthropic")
        assert p["base_url"] == ""
        assert "claude" in p["model"]

    def test_custom_provider_fallback(self):
        """Unknown provider should return custom defaults."""
        p = get_provider_config("nonexistent")
        assert p["base_url"] == ""
        assert p["model"] == ""
        assert p["key_env"] == "API_KEY"

    def test_case_insensitive(self):
        """Provider lookup should be case-insensitive."""
        assert get_provider_config("DEEPSEEK") == get_provider_config("deepseek")
        assert get_provider_config("Anthropic") == get_provider_config("anthropic")


class TestConfigFileIO:
    """Test config file read/write (uses temp dir from conftest)."""

    def test_load_empty_when_no_file(self):
        config = load_config()
        assert config == {}

    def test_save_and_load(self):
        data = {"provider": "openai", "api_key": "sk-abc"}
        save_config(data)
        loaded = load_config()
        assert loaded["provider"] == "openai"
        assert loaded["api_key"] == "sk-abc"

    def test_save_overwrites(self):
        save_config({"provider": "deepseek"})
        save_config({"provider": "openai"})
        assert load_config()["provider"] == "openai"

    def test_clear_removes_file(self):
        save_config({"provider": "test"})
        clear_config()
        assert load_config() == {}
        # Calling again should not raise
        clear_config()


class TestGetEffectiveConfig:
    """Test the merged config (env vars > file > defaults)."""

    def test_defaults_with_no_config(self, monkeypatch):
        cfg = get_effective_config()
        assert cfg["provider"] == "anthropic"  # default
        assert cfg["model"].startswith("claude")

    def test_file_values_used(self, monkeypatch):
        save_config({
            "provider": "deepseek",
            "api_key": "sk-file-key",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        })
        cfg = get_effective_config()
        assert cfg["provider"] == "deepseek"
        assert cfg["api_key"] == "sk-file-key"
        assert cfg["base_url"] == "https://api.deepseek.com/v1"
        assert cfg["model"] == "deepseek-chat"

    def test_env_var_overrides_file(self, monkeypatch):
        """Env var should take priority over config file."""
        save_config({"api_key": "sk-file-key", "provider": "deepseek"})
        # Set the correct env var for the configured provider (deepseek)
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-env-key")
        cfg = get_effective_config()
        assert cfg["api_key"] == "sk-env-key"

    def test_api_key_env_var_fallback(self, monkeypatch):
        """Generic API_KEY env var should work as fallback."""
        save_config({"provider": "custom", "base_url": "https://example.com/v1"})
        monkeypatch.setenv("API_KEY", "sk-generic-env")
        cfg = get_effective_config()
        assert cfg["api_key"] == "sk-generic-env"

    def test_no_api_key_returns_empty(self):
        """When no key set anywhere, api_key should be empty string."""
        cfg = get_effective_config()
        # No env vars, no config file — api_key should be ""
        assert cfg["api_key"] == ""

    def test_config_file_path_in_output(self):
        """Effective config should include the config file path."""
        cfg = get_effective_config()
        assert "config_file" in cfg
        assert ".surprise-plan" in cfg["config_file"]
