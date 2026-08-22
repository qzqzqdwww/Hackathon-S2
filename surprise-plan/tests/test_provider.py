"""Tests for surprise_plan.backend.provider — API call mocking."""
import json
from unittest.mock import MagicMock, patch

import pytest


# ─── Fake API response payload ─────────────────────────────────

FAKE_PLAN = {
    "domain": "真菌学 (Mycology)",
    "tagline": "From AI to mushrooms — the mycelium network is nature's neural net",
    "why_interesting": "真菌是自然界最古老的分布式计算系统...",
    "connections": [
        "菌丝网络与神经网络的拓扑结构惊人相似",
        "AI 图像识别可直接用于蘑菇分类",
    ],
    "learning_path": [
        {
            "week": 1, "theme": "真菌世界入门",
            "activities": ["了解真菌分类学", "显微镜观察练习"],
            "resources": ["《Mycelium Running》— Paul Stamets"],
        },
        {
            "week": 2, "theme": "菌丝网络生态",
            "activities": ["研究菌根共生关系", "野外采样"],
            "resources": ["《Entangled Life》— Merlin Sheldrake"],
        },
        {
            "week": 3, "theme": "真菌与AI",
            "activities": ["用CNN识别蘑菇种类", "绘制菌丝网络图"],
            "resources": ["Kaggle: Mushroom Classification"],
        },
        {
            "week": 4, "theme": "整合与实践",
            "activities": ["制作菌种培养皿", "撰写兴趣交汇报告"],
            "resources": ["本地真菌学社"],
        },
    ],
    "surprise_factor": "当你发现蘑菇的菌丝网络和你的神经网络本质上是同一套设计...",
}


# ─── Tests ─────────────────────────────────────────────────────


class TestGeneratePlanOpenAICompatible:
    """Test plan generation for all non-Anthropic providers (DeepSeek, etc.)."""

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_deepseek_plan(self, mock_cfg, mock_call):
        """DeepSeek provider should call OpenAI-compatible endpoint."""
        mock_cfg.return_value = {
            "provider": "deepseek",
            "api_key": "sk-test-deepseek",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        plan = generate_plan(["AI", "音乐"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"
        mock_call.assert_called_once_with(
            "sk-test-deepseek", "deepseek-chat", "https://api.deepseek.com/v1",
            "My current interests are: AI, 音乐.\nSurprise me with a learning plan for: 真菌学 (Mycology)",
        )

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_openai_provider(self, mock_cfg, mock_call):
        """OpenAI provider should work via OpenAI-compatible API."""
        mock_cfg.return_value = {
            "provider": "openai",
            "api_key": "sk-test-openai",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        plan = generate_plan(["编程"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_zhipu_provider(self, mock_cfg, mock_call):
        """Zhipu GLM provider should work."""
        mock_cfg.return_value = {
            "provider": "zhipu",
            "api_key": "sk-test-zhipu",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-plus",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        plan = generate_plan(["数学"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_custom_provider(self, mock_cfg, mock_call):
        """Custom provider with any OpenAI-compatible endpoint."""
        mock_cfg.return_value = {
            "provider": "custom",
            "api_key": "sk-custom-key",
            "base_url": "https://my-api.example.com/v1",
            "model": "my-model",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        plan = generate_plan(["艺术"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_openai_client_receives_correct_args(self, mock_cfg, mock_call):
        """Verify the OpenAI-compatible function is called with correct parameters."""
        mock_cfg.return_value = {
            "provider": "deepseek",
            "api_key": "sk-test-key",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        generate_plan(["AI", "音乐", "摄影"], "真菌学 (Mycology)")

        mock_call.assert_called_once()
        args = mock_call.call_args[0]
        assert args[0] == "sk-test-key"          # api_key
        assert args[1] == "deepseek-chat"        # model
        assert args[2] == "https://api.deepseek.com/v1"  # base_url
        assert "AI" in args[3]                    # user_message
        assert "真菌学" in args[3]


class TestGeneratePlanAnthropic:
    """Test Anthropic Claude API path."""

    @patch("surprise_plan.backend.provider._call_anthropic")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_anthropic_plan(self, mock_cfg, mock_call):
        """Anthropic provider should call messages.create API."""
        mock_cfg.return_value = {
            "provider": "anthropic",
            "api_key": "sk-ant-test-key",
            "base_url": "",
            "model": "claude-sonnet-4-20250514",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        plan = generate_plan(["AI", "音乐"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"
        mock_call.assert_called_once()
        args = mock_call.call_args[0]
        assert args[1] == "claude-sonnet-4-20250514"


class TestErrorHandling:
    """Test error paths in generate_plan."""

    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_missing_api_key_raises(self, mock_cfg):
        """Empty API key should raise EnvironmentError."""
        mock_cfg.return_value = {
            "provider": "deepseek",
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        }

        from surprise_plan.backend.provider import generate_plan
        with pytest.raises(EnvironmentError, match="API Key"):
            generate_plan(["AI"], "真菌学")

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_missing_base_url_for_non_anthropic(self, mock_cfg, mock_call):
        """Non-Anthropic provider uses known base_url when not configured."""
        mock_cfg.return_value = {
            "provider": "deepseek",
            "api_key": "sk-test",
            "base_url": "",
            "model": "deepseek-chat",
        }
        mock_call.return_value = json.dumps(FAKE_PLAN)

        from surprise_plan.backend.provider import generate_plan
        plan = generate_plan(["AI"], "真菌学 (Mycology)")
        # deepseek has a built-in base_url, so it should still work
        assert plan["domain"] == "真菌学 (Mycology)"

    @patch("surprise_plan.backend.provider._call_openai_compatible")
    @patch("surprise_plan.backend.provider.get_effective_config")
    def test_api_error_propagates(self, mock_cfg, mock_call):
        """API errors should propagate to caller."""
        from openai import APIError

        mock_cfg.return_value = {
            "provider": "deepseek",
            "api_key": "sk-test",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        }
        mock_call.side_effect = APIError("API error", request=MagicMock(), body=None)

        from surprise_plan.backend.provider import generate_plan
        with pytest.raises(APIError):
            generate_plan(["AI"], "真菌学")


class TestStripMarkdownFences:
    """Test the markdown fence stripper."""

    def test_strips_triple_backticks(self):
        from surprise_plan.backend.provider import _strip_markdown_fences
        raw = "```json\n{\"key\": \"val\"}\n```"
        assert _strip_markdown_fences(raw) == '{"key": "val"}'

    def test_no_fences_unchanged(self):
        from surprise_plan.backend.provider import _strip_markdown_fences
        raw = '{"key": "val"}'
        assert _strip_markdown_fences(raw) == raw

    def test_only_opening_fence(self):
        from surprise_plan.backend.provider import _strip_markdown_fences
        raw = '```\n{"key": "val"}'
        assert _strip_markdown_fences(raw) == '{"key": "val"}'
