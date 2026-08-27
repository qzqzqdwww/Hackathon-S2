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
    "key_terms": ["mycelium", "spore"],
    "fun_fact": "蘑菇比植物更接近动物。",
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
        diff_note = "标准 — 理论与实践平衡，适合自学"

        with patch("surprise_plan.backend.provider.get_effective_config") as cfg, \
             patch("surprise_plan.backend.provider._call_openai_compatible") as call, \
             patch("surprise_plan.backend.provider.random.randint", return_value=42):
            c = _cfg()
            cfg.return_value = c
            call.return_value = json.dumps(FAKE_PLAN)
            generate_plan(interests, domain)

        seed = 42
        angle = "偶数种子：从令人惊讶的现代应用切入"
        expected_msg = (
            f"[random_seed={seed}]\n"
            f"My current interests are: {', '.join(interests)}.\n"
            f"Surprise me with a learning plan for: {domain}\n"
            f"Difficulty level: {diff_note}\n"
            f"Angle hint ({angle})"
        )

        args = call.call_args[0]
        assert args[0] == c["api_key"]
        assert args[1] == c["model"]
        assert args[2] == c["base_url"]
        assert args[3] == expected_msg

    def test_random_seed_changes(self):
        """Different calls produce different seeds, ensuring variety."""
        with patch("surprise_plan.backend.provider.get_effective_config") as cfg, \
             patch("surprise_plan.backend.provider._call_openai_compatible") as call, \
             patch("surprise_plan.backend.provider.random.randint", side_effect=[1, 2]):
            c = _cfg()
            cfg.return_value = c
            call.return_value = json.dumps(FAKE_PLAN)
            generate_plan(["AI"], "真菌学 (Mycology)")
            first_msg = call.call_args[0][3]
            generate_plan(["AI"], "真菌学 (Mycology)")
            second_msg = call.call_args[0][3]
        assert "[random_seed=1]" in first_msg
        assert "[random_seed=2]" in second_msg
        assert first_msg != second_msg


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

    def test_strips_fence_with_preamble(self):
        raw = "Here is the JSON:\n```json\n{\"a\": 1}\n```"
        assert _strip_markdown_fences(raw) == '{"a": 1}'

    def test_strips_fence_with_preamble_no_lang(self):
        raw = "Sure! Here you go:\n```\n{\"a\": 1}\n```"
        assert _strip_markdown_fences(raw) == '{"a": 1}'
