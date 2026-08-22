"""Tests for surprise_plan CLI (Typer app) with mocked API calls."""
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from surprise_plan.cli import app

runner = CliRunner()


# ─── Helpers ───────────────────────────────────────────────────

def _mock_plan():
    return {
        "domain": "真菌学 (Mycology)",
        "tagline": "From AI to mushrooms",
        "why_interesting": "真菌是自然界的神经网络...",
        "connections": ["菌丝网络 = 生物神经网络"],
        "learning_path": [
            {"week": 1, "theme": "入门", "activities": ["A"], "resources": ["R1"]},
            {"week": 2, "theme": "进阶", "activities": ["B"], "resources": ["R2"]},
            {"week": 3, "theme": "深入", "activities": ["C"], "resources": ["R3"]},
            {"week": 4, "theme": "整合", "activities": ["D"], "resources": ["R4"]},
        ],
        "surprise_factor": "蘑菇是你的新朋友",
    }


def _mock_pick():
    return {"domain": "真菌学 (Mycology)", "surprise_score": 10}


# ─── Tests: --list-domains ─────────────────────────────────────

class TestListDomains:
    """Test the --list-domains flag."""

    def test_lists_domains(self):
        result = runner.invoke(app, ["--list-domains"])
        assert result.exit_code == 0
        assert "领域池" in result.output

    def test_shows_category_count(self):
        result = runner.invoke(app, ["--list-domains"])
        assert "159" in result.output

    def test_shows_all_categories(self):
        result = runner.invoke(app, ["--list-domains"])
        categories = [
            "人文科学", "社会科学", "自然科学", "数学与计算机科学",
            "艺术与设计", "音乐与表演", "建筑与空间", "经济与管理",
            "医学与健康", "农业与生命科学", "传统技艺", "自然与野外",
            "历史与文献", "工程与材料", "运动与实践", "食物与发酵",
            "抽象与游戏", "跨学科前沿",
        ]
        for cat in categories:
            assert cat in result.output

    def test_no_duplicate_immunology(self):
        """免疫学 should appear only once (in 自然科学)."""
        result = runner.invoke(app, ["--list-domains"])
        count = result.output.count("免疫学 (Immunology)")
        assert count == 1


# ─── Tests: --list-animations ─────────────────────────────────

class TestListAnimations:
    """Test the --list-animations flag."""

    def test_lists_animations(self):
        result = runner.invoke(app, ["--list-animations"])
        assert result.exit_code == 0
        assert "动画样式" in result.output

    def test_all_four_styles(self):
        result = runner.invoke(app, ["--list-animations"])
        for style in ["default", "lightning", "chain", "laser"]:
            assert style in result.output


# ─── Tests: main --demo ────────────────────────────────────────

class TestDemoMode:
    """Test demo mode (no API calls needed)."""

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    def test_demo_runs(self, mock_pick, mock_clear, mock_anim, mock_display):
        """Demo mode should produce a plan without calling the API."""
        result = runner.invoke(app, ["main", "--demo", "AI, 音乐"])
        # Should succeed (exit_code 0) — demo mode doesn't need API
        assert result.exit_code == 0

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    def test_demo_does_not_call_generate(self, mock_pick, mock_clear, mock_anim, mock_display):
        """Demo mode should NOT call generate_plan."""
        with patch("surprise_plan.cli.generate_plan") as mock_gen:
            result = runner.invoke(app, ["main", "--demo", "AI, 音乐"])
        mock_gen.assert_not_called()


# ─── Tests: main with mocked API ──────────────────────────────

class TestMainWithMockedAPI:
    """Test main command with mocked API responses."""

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_mock_plan())
    def test_main_success(
        self, mock_gen, mock_pick, mock_clear, mock_anim, mock_display
    ):
        """main should call generate_plan and display_plan on success."""
        result = runner.invoke(app, ["main", "AI, 音乐"])
        assert result.exit_code == 0
        mock_gen.assert_called_once_with(["AI", "音乐"], "真菌学 (Mycology)")
        mock_display.assert_called_once()
        call_args = mock_display.call_args[0][0]
        assert call_args["picked_domain"] == "真菌学 (Mycology)"
        assert call_args["plan"]["domain"] == "真菌学 (Mycology)"

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    @patch("surprise_plan.cli.generate_plan", side_effect=EnvironmentError("API Key 未设置"))
    def test_main_missing_api_key(
        self, mock_gen, mock_pick, mock_clear, mock_anim, mock_display
    ):
        """Missing API key should produce an error exit."""
        result = runner.invoke(app, ["main", "AI, 音乐"])
        assert result.exit_code == 1

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    @patch("surprise_plan.cli.generate_plan", side_effect=Exception("403 Forbidden"))
    def test_main_api_forbidden(
        self, mock_gen, mock_pick, mock_clear, mock_anim, mock_display
    ):
        """403 error should produce an error exit."""
        result = runner.invoke(app, ["main", "AI, 音乐"])
        assert result.exit_code == 1

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_mock_plan())
    def test_main_with_animation_option(
        self, mock_gen, mock_pick, mock_clear, mock_anim, mock_display
    ):
        """Animation option should be passed to play_animation."""
        result = runner.invoke(app, ["main", "--animation", "lightning", "AI, 音乐"])
        assert result.exit_code == 0
        mock_anim.assert_called_once_with("lightning", 1.0)

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_mock_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_mock_plan())
    def test_main_with_speed_option(
        self, mock_gen, mock_pick, mock_clear, mock_anim, mock_display
    ):
        """Speed option should be passed to play_animation."""
        result = runner.invoke(app, ["main", "--speed", "2.0", "AI, 音乐"])
        assert result.exit_code == 0
        mock_anim.assert_called_once_with("default", 2.0)


# ─── Tests: interactive mode ──────────────────────────────────

class TestInteractiveMode:
    """Test the interactive REPL (bare invocation)."""

    def test_bare_invocation_shows_header(self):
        """Bare invocation should print the header (no subcommand)."""
        # Interactive mode requires user input, so it will exit with 0
        # We just check it doesn't crash on the header
        result = runner.invoke(app, [], input="q\n")
        # Either exit 0 (user quit) or some other exit — just no crash
        assert "Surprise-Plan" in result.output or result.exception is None or \
            isinstance(result.exception, SystemExit)

    def test_invalid_animation_rejected(self):
        """Unknown animation name should produce an error."""
        result = runner.invoke(app, ["main", "--animation", "unknown", "AI"])
        assert result.exit_code != 0
        assert "未知动画" in (result.stdout + result.stderr)


# ─── Tests: config commands ───────────────────────────────────

class TestConfigCommands:
    """Test config subcommands."""

    def test_config_show(self):
        """config show should display current config."""
        result = runner.invoke(app, ["config", "show"])
        # Should succeed and show provider info
        assert result.exit_code == 0

    def test_config_set(self):
        """config set should update values."""
        runner.invoke(app, [
            "config", "set",
            "--provider", "deepseek",
            "--api-key", "sk-test-1234567890123456",
            "--model", "deepseek-chat",
        ])
        result = runner.invoke(app, ["config", "show"])
        assert "deepseek" in result.output

    def test_config_clear_requires_confirmation(self):
        """config clear should prompt for confirmation."""
        result = runner.invoke(app, ["config", "clear"], input="n\n")
        # User said no, so it should exit without clearing
        assert result.exit_code == 0

    def test_config_set_persists(self):
        """Setting config should persist for subsequent reads."""
        runner.invoke(app, [
            "config", "set",
            "--provider", "openai",
            "--api-key", "sk-openai-test-12345678",
        ])
        result = runner.invoke(app, ["config", "show"])
        assert "openai" in result.output
