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
        "key_terms": ["term1", "term2"],
        "fun_fact": "蘑菇比人类早几亿年登上陆地。",
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
        gen.assert_called_once_with(["AI", "音乐"], "真菌学 (Mycology)", difficulty="3")
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

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.play_animation")
    @patch("surprise_plan.cli.clear_screen")
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    @patch("surprise_plan.cli.generate_plan", return_value=_plan())
    @patch("surprise_plan.backend.plan_exporter.export_plan")
    def test_export_in_interactive(self, mock_export, gen, pick, clear, anim, display):
        mock_export.return_value = "/tmp/plan.md"
        r = runner.invoke(
            app, [], input="1\nAI\n\n" + "e\n/tmp/plan.md\nq\n"
        )
        assert r.exit_code == 0
        mock_export.assert_called_once()
        args = mock_export.call_args[0]
        assert args[0]["picked_domain"] == "真菌学 (Mycology)"
        assert args[1].endswith("plan.md")
        # Verify format hint is shown
        assert "导出格式" in r.output
        assert ".json" in r.output
        assert ".md" in r.output
        assert ".txt" in r.output
        assert ".html" in r.output

    @patch("surprise_plan.cli.generate_plan", return_value=_plan())
    @patch("surprise_plan.cli.pick_domain", return_value=_pick())
    @patch("surprise_plan.backend.plan_exporter.export_plan")
    def test_output_flag(self, mock_export, mock_pick, mock_gen):
        r = runner.invoke(app, ["main", "--output", "/tmp/plan.json", "AI"])
        assert r.exit_code == 0
        mock_export.assert_called_once()
        assert mock_export.call_args[0][1].endswith("plan.json")

    def test_export_json_extension(self):
        from surprise_plan.backend.plan_exporter import detect_format
        assert detect_format("plan.json") == "json"

    def test_export_md_extension(self):
        from surprise_plan.backend.plan_exporter import detect_format
        assert detect_format("plan.md") == "md"

    def test_export_txt_extension(self):
        from surprise_plan.backend.plan_exporter import detect_format
        assert detect_format("plan.txt") == "txt"

    def test_export_html_extension(self):
        from surprise_plan.backend.plan_exporter import detect_format
        assert detect_format("plan.html") == "html"

    def test_export_unknown_falls_back_to_txt(self):
        from surprise_plan.backend.plan_exporter import detect_format
        assert detect_format("plan.doc") == "txt"

    def test_export_creates_file(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {
            "status": "success",
            "plan": {
                "domain": "测试领域",
                "why_interesting": "原因",
                "connections": [],
                "key_terms": [],
                "learning_path": [],
            },
        }
        out = tmp_path / "out.md"
        result = export_plan(data, str(out))
        assert out.exists()
        assert "测试领域" in out.read_text(encoding="utf-8")

    def test_export_json_format(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {"domain": "JSON测试", "plan": {"domain": "JSON测试", "why_interesting": "x"}}
        out = tmp_path / "out.json"
        result = export_plan(data, str(out))
        content = out.read_text(encoding="utf-8")
        assert '"domain"' in content
        assert "JSON测试" in content

    def test_export_html_format(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {
            "plan": {
                "domain": "HTML测试",
                "why_interesting": "why",
                "key_terms": ["term1"],
                "fun_fact": "fact",
                "connections": ["conn"],
                "learning_path": [
                    {"week": 1, "theme": "t1", "activities": ["a1"], "resources": ["r1"]},
                ],
                "surprise_factor": "surprise",
            },
        }
        out = tmp_path / "out.html"
        export_plan(data, str(out))
        content = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "HTML测试" in content
        assert "term1" in content

    def test_export_creates_parent_dirs(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {"plan": {"domain": "deep"}}
        out = tmp_path / "a" / "b" / "plan.txt"
        result = export_plan(data, str(out))
        assert out.exists()

    def test_export_directory_path_raises(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {"plan": {"domain": "test"}}
        with pytest.raises(PermissionError, match="目录"):
            export_plan(data, str(tmp_path))

    def test_export_html_escapes_special_chars(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {
            "plan": {
                "domain": "<script>alert(1)</script>",
                "tagline": "<em>tag</em>",
                "why_interesting": "normal <b>bold</b>",
                "key_terms": ["<term>"],
                "fun_fact": "<img src=x onerror=alert(1)>",
                "connections": ["<a href='#'>link</a>"],
                "learning_path": [
                    {"week": 1, "theme": "<h1>t</h1>",
                     "activities": ["<script>"], "resources": ["<r>"]},
                ],
                "surprise_factor": "<div>sf</div>",
            },
        }
        out = tmp_path / "xss.html"
        export_plan(data, str(out))
        content = out.read_text(encoding="utf-8")
        assert "<script>" not in content
        assert "&lt;script&gt;" in content
        assert "&lt;h1&gt;" in content
        assert "&lt;em&gt;" in content

    def test_export_markdown_escapes_special_chars(self, tmp_path):
        from surprise_plan.backend.plan_exporter import export_plan
        data = {
            "plan": {
                "domain": "<script>x</script>",
                "why_interesting": "<b>bold</b>",
                "key_terms": ["<term>"],
                "connections": ["<a>link</a>"],
                "learning_path": [
                    {"week": 1, "theme": "t",
                     "activities": ["<script>"], "resources": ["<r>"]},
                ],
                "surprise_factor": "<div>x</div>",
            },
        }
        out = tmp_path / "xss.md"
        export_plan(data, str(out))
        content = out.read_text(encoding="utf-8")
        assert "<script>" not in content
        assert "&lt;script&gt;" in content

    @patch("surprise_plan.cli.display_plan")
    @patch("surprise_plan.cli.generate_plan", return_value=_plan())
    def test_dive_deeper_passes_difficulty(self, mock_gen, mock_display):
        from surprise_plan.cli import _dive_deeper
        with patch("rich.prompt.Prompt.ask", return_value="test topic"):
            _dive_deeper(["AI"], difficulty="3", demo_mode=False)
        mock_gen.assert_called_once()
        assert mock_gen.call_args[0][1] == "test topic"
        assert mock_gen.call_args[1]["difficulty"] == "3"


class TestConfigCommands:
    def test_show(self):
        r = runner.invoke(app, ["config", "show"])
        assert r.exit_code == 0

    def test_set(self):
        runner.invoke(app, ["config", "set", "--provider", "deepseek",
                            "--api-key", "sk-test-1234567890", "--model", "deepseek-chat"])
        assert "deepseek" in runner.invoke(app, ["config", "show"]).output

    @patch("surprise_plan.cli._run_connection_test")
    def test_set_wizard_calls_connection_test(self, mock_test):
        r = runner.invoke(app, ["config", "set"], input="1\nsk-test-1234567890\n\n\nn\n")
        assert r.exit_code == 0
        mock_test.assert_called_once()

    def test_clear_confirms(self):
        r = runner.invoke(app, ["config", "clear"], input="n\n")
        assert r.exit_code == 0

    def test_set_persists(self):
        runner.invoke(app, ["config", "set", "--provider", "openai",
                            "--api-key", "sk-openai-test-12345678"])
        assert "openai" in runner.invoke(app, ["config", "show"]).output
