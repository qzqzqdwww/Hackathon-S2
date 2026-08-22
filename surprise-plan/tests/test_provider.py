"""Tests for surprise_plan.backend.provider — API calls fully mocked."""
import json
from unittest.mock import MagicMock, patch

import pytest
from surprise_plan.backend.provider import _strip_markdown_fences, generate_plan

FAKE_PLAN = {
    "domain": "真菌学 (Mycology)",
    "tagline": "From AI to mushrooms",
    "why_interesting": "...",
    "connections": ["菌丝网络 = 神经网络", "AI 图像识别用于蘑菇分类"],
    "learning_path": [
        {"week": 1, "theme": "t1", "activities": ["a1"], "resources": ["r1"]},
        {"week": 2, "theme": "t2", "activities": ["a2"], "resources": ["r2"]},
        {"week": 3, "theme": "t3", "activities": ["a3"], "resources": ["r3"]},
        {"week": 4, "theme": "t4", "activities": ["a4"], "resources": ["r4"]},
    ],
    "surprise_factor": "...",
}


def _cfg(**overrides):
    """Build a config dict; caller should always specify provider + model + base_url."""
    base = {"provider": "openai", "api_key": "sk-test",
            "base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"}
    base.update(overrides)
    return base


PROVIDERS = [
    ("deepseek",  "https://api.deepseek.com/v1",       "deepseek-chat"),
    ("openai",    "https://api.openai.com/v1",          "gpt-4o-mini"),
    ("zhipu",     "https://open.bigmodel.cn/api/paas/v4", "glm-4-plus"),
    ("stepfun",   "https://api.stepfun.com/v1",         "step-2-16k"),
    ("doubao",    "https://ark.cn-beijing.volces.com/api/v3", "doubao-pro-32k"),
    ("siliconflow", "https://api.siliconflow.cn/v1",    "Qwen/Qwen2.5-72B-Instruct"),
    ("custom",    "https://my-api.example.com/v1",      "my-model"),
]


class TestGeneratePlanOpenAICompatible:
    @pytest.mark.parametrize("provider,url,model", PROVIDERS)
    def test_generates_plan(self, provider, url, model):
        with patch("surprise_plan.backend.provider.get_effective_config") as cfg, \
             patch("surprise_plan.backend.provider._call_openai_compatible") as call:
            cfg.return_value = _cfg(provider=provider, base_url=url, model=model)
            call.return_value = json.dumps(FAKE_PLAN)
            plan = generate_plan(["AI"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"
        assert len(plan["learning_path"]) == 4

    def test_args_passed_through(self):
        interests = ["AI", "音乐"]
        domain = "真菌学 (Mycology)"
        expected_msg = f"My current interests are: {', '.join(interests)}.\nSurprise me with a learning plan for: {domain}"

        with patch("surprise_plan.backend.provider.get_effective_config") as cfg, \
             patch("surprise_plan.backend.provider._call_openai_compatible") as call:
            c = _cfg()
            cfg.return_value = c
            call.return_value = json.dumps(FAKE_PLAN)
            generate_plan(interests, domain)

        args = call.call_args[0]
        assert args == (c["api_key"], c["model"], c["base_url"], expected_msg)


class TestGeneratePlanAnthropic:
    def test_anthropic_plan(self):
        with patch("surprise_plan.backend.provider.get_effective_config") as cfg, \
             patch("surprise_plan.backend.provider._call_anthropic") as call:
            cfg.return_value = _cfg(provider="anthropic", base_url="",
                                     model="claude-sonnet-4-20250514")
            call.return_value = json.dumps(FAKE_PLAN)
            plan = generate_plan(["AI"], "真菌学 (Mycology)")
        assert plan["domain"] == "真菌学 (Mycology)"
        assert call.call_args[0][1] == "claude-sonnet-4-20250514"


class TestErrorHandling:
    def test_missing_api_key(self):
        with patch("surprise_plan.backend.provider.get_effective_config") as cfg:
            cfg.return_value = _cfg(api_key="")
            with pytest.raises(EnvironmentError, match="API Key"):
                generate_plan(["AI"], "真菌学")

    def test_api_error_propagates(self):
        from openai import APIError
        with patch("surprise_plan.backend.provider.get_effective_config") as cfg, \
             patch("surprise_plan.backend.provider._call_openai_compatible") as call:
            cfg.return_value = _cfg()
            call.side_effect = APIError("fail", request=MagicMock(), body=None)
            with pytest.raises(APIError):
                generate_plan(["AI"], "真菌学")


class TestStripMarkdownFences:
    def test_strips_fences(self):
        assert _strip_markdown_fences("```json\n{a}\n```") == "{a}"

    def test_no_fences(self):
        raw = '{"a": 1}'
        assert _strip_markdown_fences(raw) == raw

    def test_partial_fence(self):
        assert _strip_markdown_fences('```\n{"a": 1}') == '{"a": 1}'
