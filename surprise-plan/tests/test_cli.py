"""Tests for surprise_plan CLI — all API calls mocked."""
from typer.testing import CliRunner
from unittest.mock import patch
import pytest

from surprise_plan.cli import app

runner = CliRunner()

def _plan():
    return {
        "domain": "真菌学 (Mycology)", "tagline": "From AI to mushrooms",
        "why_interesting": "...",
        "connections": ["菌丝 = 神经网络"],
        "learning_path": [
            {"week": 1, "theme": "t1", "activities": ["a1"], "resources": ["r1"]},
            {"week": 2, "theme": "t2", "activities": ["a2"], "resources": ["r2"]},
            {"week": 3, "theme": "t3", "activities": ["a3"], "resources": ["r3"]},
            {"week": 4, "theme": "t4", "activities": ["a4"], "resources": ["r4"]},
        ],
        "surprise_factor": "...",
    }

def _pick():
    return {"domain": "真菌学 (Mycology)", "surprise_score": 10}


class TestListDomains:
    def test_outputs_header(self):
        r = runner.invoke(app, ["--list-domains"])
        assert r.exit_code == 0 and "领域池" in r.output

    def test_shows_159_count(self):
        assert "159" in runner.invoke(app, ["--list-domains"]).output

    def test_all_categories_present(self):
        cats = ["人文科学", "社会科学", "自然科学", "数学与计算机科学",
                "艺术与设计", "音乐与表演", "建筑与空间", "经济与管理",
                "医学与健康", "农业与生命科学", "传统技艺", "自然与野外",
                "历史与文献", "工程与材料", "运动与实践", "食物与发酵",
                "抽象与游戏", "跨学科前沿"]
        out = runner.invoke(app, ["--list-domains"]).output
        assert all(c in out for c in cats)

    def test_no_duplicate_immunology(self):
        out = runner.invoke(app, ["--list-domains"]).output
        assert out.count("免疫学 (Immunology)") == 1


class TestListAnimations:
    def test_outputs_header(self):
        r = runner.invoke(app, ["--list-animations"])
        assert r.exit_code == 0 and "动画样式" in r.output

    def test_all_styles(self):
        out = runner.invoke(app, ["--list-animations"]).output
        for s in ["default", "lightning", "chain", "laser"]:
            assert s in out


class TestDemoMode:
    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    def test_runs_without_api(self, *mocks):
        result = runner.invoke(app, ["main", "--demo", "AI, 音乐"])
        assert result.exit_code == 0

    @patch("surprise_plan.cli.generate_plan")
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    def test_does_not_call_generate(self, mock_pick, mock_gen):
        runner.invoke(app, ["main", "--demo", "AI, 音乐"])
        mock_gen.assert_not_called()


class TestMainWithMockedAPI:
    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_plan())
    def test_success(self, gen, pick, clear, anim, display):
        r = runner.invoke(app, ["main", "AI, 音乐"])
        assert r.exit_code == 0
        gen.assert_called_once_with(["AI", "音乐"], "真菌学 (Mycology)")
        args = display.call_args[0][0]
        assert args["picked_domain"] == "真菌学 (Mycology)"

    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    def test_missing_api_key(self, mock_pick):
        with patch("surprise_plan.cli.generate_plan",
                   side_effect=EnvironmentError("API Key 未设置")):
            r = runner.invoke(app, ["main", "AI, 音乐"])
        assert r.exit_code == 1

    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    def test_api_forbidden(self, mock_pick):
        with patch("surprise_plan.cli.generate_plan",
                   side_effect=Exception("403 Forbidden")):
            r = runner.invoke(app, ["main", "AI, 音乐"])
        assert r.exit_code == 1

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_plan())
    def test_animation_option(self, gen, pick, anim, display):
        r = runner.invoke(app, ["main", "--animation", "lightning", "AI, 音乐"])
        assert r.exit_code == 0
        anim.assert_called_once_with("lightning", 1.0)

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_plan())
    def test_speed_option(self, gen, pick, anim, display):
        r = runner.invoke(app, ["main", "--speed", "2.0", "AI, 音乐"])
        assert r.exit_code == 0
        anim.assert_called_once_with("default", 2.0)


class TestInteractiveMode:
    def test_header_appears(self):
        r = runner.invoke(app, [], input="q\n")
        assert "Surprise-Plan" in r.output

    def test_invalid_animation(self):
        r = runner.invoke(app, ["main", "--animation", "xyz", "AI"])
        assert r.exit_code != 0


class TestConfigCommands:
    def test_show(self):
        r = runner.invoke(app, ["config", "show"])
        assert r.exit_code == 0

    def test_set(self):
        runner.invoke(app, ["config", "set", "--provider", "deepseek",
                            "--api-key", "sk-test-1234567890", "--model", "deepseek-chat"])
        assert "deepseek" in runner.invoke(app, ["config", "show"]).output

    def test_clear_confirms(self):
        r = runner.invoke(app, ["config", "clear"], input="n\n")
        assert r.exit_code == 0

    def test_set_persists(self):
        runner.invoke(app, ["config", "set", "--provider", "openai",
                            "--api-key", "sk-openai-test-12345678"])
        assert "openai" in runner.invoke(app, ["config", "show"]).output
