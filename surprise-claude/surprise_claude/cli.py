"""Surprise Claude — CLI entry point.

Usage:
    surprise-claude                           # Interactive mode
    surprise-claude "AI, 音乐, 摄影"          # Direct mode
    surprise-claude config set                # Configure API settings
    surprise-claude config show               # Show current config
    surprise-claude --list-domains            # Show all domains
    surprise-claude --animation lightning     # Use lightning animation
"""

import os
import sys
import time

# ─── Platform setup (must be first, before any output) ────

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

    import colorama
    colorama.init()

import typer
from rich.console import Console
from rich.prompt import Prompt

from .display import (
    play_animation,
    display_plan,
    clear_screen,
)
from .backend.domain_picker import DOMAINS, pick_domain
from .backend.provider import generate_plan, get_current_provider
from .backend.config import (
    load_config, save_config, clear_config, get_provider_config, KNOWN_PROVIDERS,
)

console = Console(safe_box=True)

app = typer.Typer(
    name="surprise-claude",
    add_completion=False,
    no_args_is_help=False,
)

# ─── Core workflow ─────────────────────────────────────────

def _run(interests: list, animation: str, speed: float, regenerate: bool = False, demo_mode: bool = False):
    """Animation -> domain pick -> API call -> display plan."""
    if not interests:
        console.print("[red]错误：请至少提供一个兴趣领域。[/red]")
        console.print("[green]示例: surprise-claude \"AI, 音乐, 摄影\"[/green]")
        raise typer.Exit(1)

    provider = get_current_provider()

    try:
        pick = pick_domain(interests)
    except Exception as e:
        console.print(f"[red]领域选择失败: {e}[reset]")
        raise typer.Exit(1)

    if not regenerate:
        clear_screen()
        console.print("[bold yellow][TARGET] Surprise Claude[/bold yellow]")
        console.print("[dim]打破算法茧房 · 制造意外[/dim]")
        console.print()
        console.print(f"[green]你的兴趣: {', '.join(interests)}[/green]")
        console.print()
        console.print(f"[dim]AI 引擎: {provider}[/dim]")
        console.print("[yellow]即将为你随机揭示一个陌生领域...[/yellow]")
        console.print()
        time.sleep(0.8)

    play_animation(animation, speed)
    time.sleep(0.3)

    console.print(f"\n[bold yellow]正在生成学习 PLAN...[/bold yellow]\n")

    try:
        if demo_mode:
            plan = _generate_demo_plan()
        else:
            plan = generate_plan(interests, pick["domain"])
    except EnvironmentError as e:
        console.print(f"[red]{e}[/red]")
        console.print()
        console.print(f"[dim]查看配置: surprise-claude config show[/dim]")
        console.print(f"[green]设置 API:  surprise-claude config set[/green]")
        raise typer.Exit(1)
    except Exception as e:
        msg = str(e)
        if "403" in msg or "forbidden" in msg.lower() or "401" in msg:
            console.print(f"[red]API 调用失败（认证失败）— [{provider}][/red]")
            console.print("  1. API Key 无效或已过期")
            console.print("  2. 账号未开通 API 访问权限")
            console.print("  3. 账号余额不足")
            console.print()
            console.print(f"[dim]运行 surprise-claude config set 更新 Key[/dim]")
        else:
            console.print(f"[red]生成失败: {e}[/red]")
        raise typer.Exit(1)

    display_plan({
        "status": "success",
        "picked_domain": pick["domain"],
        "surprise_score": pick.get("surprise_score", 0),
        "plan": plan,
    })


# ─── Helpers ───────────────────────────────────────────────

def show_help():
    clear_screen()
    console.print(f"\n[bold yellow][TARGET] Surprise Claude[/bold yellow]")
    console.print(f"[dim]打破算法茧房 · 随机学习计划生成器[/dim]")
    console.print(f"[dim]大工黑客松 S2 — Track 03 · 开放原子[/dim]\n")
    console.print(f"\n[bold]用法:[/bold]")
    console.print(f"  [green]surprise-claude[/green]                       交互模式")
    console.print(f"  [green]surprise-claude[/green] [yellow]<兴趣>[/yellow]              直接生成（逗号分隔）")
    console.print(f"  [green]surprise-claude[/green] [yellow]config set[/yellow]          设置 API 配置")
    console.print(f"  [green]surprise-claude[/green] [yellow]config show[/yellow]          查看当前配置")
    console.print(f"  [green]surprise-claude[/green] [yellow]config clear[/yellow]         清除配置")
    console.print(f"  [green]surprise-claude[/green] [yellow]--demo[/yellow]              演示模式")
    console.print(f"  [green]surprise-claude[/green] [yellow]--list-domains[/yellow]       列出领域池")
    console.print(f"  [green]surprise-claude[/green] [yellow]--list-animations[/yellow]    列出动画样式")
    console.print(f"  [green]surprise-claude[/green] [yellow]--help[/yellow]              显示此帮助")
    console.print(f"\n[bold]动画样式:[/bold]  default / lightning / chain / laser")
    console.print(f"\n[bold]AI 引擎:[/bold]   Claude / DeepSeek / 智谱 / 阶跃 / 豆包 等")
    console.print(f"            [dim]运行 config set 配置[/dim]")
    console.print()
    raise typer.Exit()


def show_list_domains():
    clear_screen()
    console.print(f"\n[bold yellow][BOOK] 领域池 ({len(DOMAINS)} 个可选领域)[/bold yellow]\n")
    categories = {
        "工艺与制作": ["陶艺", "折纸", "皮革", "面具", "微缩", "绳结", "琥珀", "玻璃", "制琴"],
        "自然世界": ["养蜂", "真菌", "鸟类", "火山", "化石", "樱花", "海洋", "树木"],
        "历史与文化": ["密码学", "占星", "茶道", "古琴", "制图", "古文字", "香料", "活字"],
        "科学": ["天文", "声学", "材料", "气象", "神经美学", "量子", "合成生物"],
        "运动与实践": ["潜水", "驯鹰", "杂技", "太极", "跳绳"],
        "食物与发酵": ["发酵", "康普茶", "奶酪", "sourdough", "味噌"],
        "抽象与游戏": ["游戏设计", "谜题", "城市漫游", "Poetry", "声音景观", "Gardening"],
    }
    assigned = {d: False for d in DOMAINS}
    for cat, keywords in categories.items():
        matched = [d for d in DOMAINS if not assigned[d] and any(kw in d for kw in keywords)]
        for d in matched:
            assigned[d] = True
        if matched:
            console.print(f"  [bold]{cat}[/bold]")
            for item in matched:
                console.print(f"    [dim]-[/dim] {item}")
            console.print()
    raise typer.Exit()


def show_list_animations():
    clear_screen()
    console.print(f"\n[bold yellow][ART] 可用动画样式[/bold yellow]\n")
    for name, desc in [
        ("default", "藤条（经典鞭挞 + 金色粒子爆发）"),
        ("lightning", "闪电（红色电流 + 瞬间打击）"),
        ("chain", "链条（金属质感 + 沉稳打击）"),
        ("laser", "激光（瞄准 + 瞬间命中 + 残影）"),
    ]:
        console.print(f"  [green]{name:<12}[/green] {desc}")
    console.print()
    raise typer.Exit()


# ─── Config Subcommand ────────────────────────────────────

config_app = typer.Typer(name="config", help="管理 API 配置")
app.add_typer(config_app, name="config")


@config_app.command("set")
def config_set(
    provider: str = typer.Option(None, "--provider", "-p", help="AI 引擎名称"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="API Key"),
    base_url: str = typer.Option(None, "--base-url", "-u", help="API 地址"),
    model: str = typer.Option(None, "--model", "-m", help="模型名称"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="交互式设置"),
):
    """设置 API 配置（保存到 ~/.surprise-claude/config.json）"""
    if interactive or not any([provider, api_key, base_url, model]):
        _config_wizard()
        return

    cfg = load_config()

    if provider:
        known = get_provider_config(provider)
        cfg["provider"] = provider
        cfg.setdefault("base_url", known["base_url"])
        cfg.setdefault("model", known["model"])
    if api_key:
        cfg["api_key"] = api_key
    if base_url:
        cfg["base_url"] = base_url
    if model:
        cfg["model"] = model

    save_config(cfg)
    console.print(f"\n[green]配置已保存！[/green]")
    _print_config()


@config_app.command("show")
def config_show():
    """显示当前 API 配置"""
    from .backend.provider import get_config_summary
    s = get_config_summary()
    console.print(f"\n[bold yellow][CONFIG] 当前 API 配置[/bold yellow]\n")
    console.print(f"  引擎:     [green]{s['provider']}[/green]")
    console.print(f"  API Key:  {s['api_key']}")
    console.print(f"  API 地址: {s['base_url']}")
    console.print(f"  模型:     {s['model']}")
    console.print(f"  配置文件: {s['config_file']}")
    console.print()


@config_app.command("clear")
def config_clear():
    """清除保存的 API 配置"""
    if not typer.confirm("确定要清除所有保存的 API 配置吗？"):
        console.print(f"\n[dim]已取消。[/dim]")
        raise typer.Exit(0)
    clear_config()
    console.print(f"\n[green]配置已清除。[reset]")


def _config_wizard():
    """Interactive config setup."""
    clear_screen()
    console.print(f"\n[bold yellow][CONFIG] API 配置向导[/bold yellow]\n")

    names = list(KNOWN_PROVIDERS.keys())
    console.print(f"\n[bold]选择 AI 引擎:[/bold]\n")
    for i, name in enumerate(names, 1):
        k = KNOWN_PROVIDERS[name]
        console.print(f"  [green]{i}[/green]. [bold]{name}[/bold]  (默认: {k['model']})")
    console.print(f"  [green]{len(names)+1}[/green]. [bold]custom[/bold]  (自定义 OpenAI 兼容 API)")

    choice = Prompt.ask(f"\n[yellow]选择引擎[/yellow]（序号或名称）", default="anthropic")
    provider = _parse_provider_choice(choice, names)

    known = get_provider_config(provider)
    cfg = {"provider": provider}

    key_hint = f"（{known['key_env']}）" if known["key_env"] != "API_KEY" else ""
    api_key = Prompt.ask(f"\n[green]API Key[/green]{key_hint}", password=True)
    if api_key:
        cfg["api_key"] = api_key

    if provider != "anthropic":
        cfg["base_url"] = Prompt.ask(f"\n[cyan]API 地址[/cyan]", default=known["base_url"])

    cfg["model"] = Prompt.ask(f"\n[yellow]模型名称[/yellow]", default=known["model"])

    save_config(cfg)
    console.print(f"\n[green]配置已保存！[/green]")
    _print_config()


def _parse_provider_choice(choice: str, names: list) -> str:
    try:
        idx = int(choice.strip()) - 1
        if 0 <= idx < len(names):
            return names[idx]
    except ValueError:
        pass
    c = choice.strip().lower()
    if c in KNOWN_PROVIDERS:
        return c
    if c in ("custom", str(len(KNOWN_PROVIDERS) + 1)):
        return "custom"
    return "anthropic"


def _print_config():
    from .backend.provider import get_config_summary
    s = get_config_summary()
    console.print(f"\n  引擎: [green]{s['provider']}[/green]")
    console.print(f"  Key:   {s['api_key']}")
    console.print(f"  地址: {s['base_url']}")
    console.print(f"  模型: {s['model']}\n")


# ─── Demo Plan ─────────────────────────────────────────────

_DEMO_PLAN = {
    "domain": "养蜂 (Beekeeping)",
    "tagline": "The rhythm of a hive is the tempo your music practice has been missing",
    "why_interesting": (
        "养蜂是自然界最精密的分布式系统。一个蜂群由上万只蜜蜂组成，"
        "却没有任何中央控制——它们通过'摇摆舞'传递信息，通过信息素协调行动。"
        "如果你对AI感兴趣，你会惊叹于这套没有算法的智能；"
        "如果你对音乐感兴趣，你会发现蜂群振翅的频率本身就是一首交响乐。"
    ),
    "connections": [
        "养蜂的'摇摆舞'通信协议是自然界最原始的舞蹈形式",
        "微距摄影技巧可以直接迁移到蜂巢内部拍摄",
        "AI蜂群算法（Swarm Intelligence）正是受此启发",
    ],
    "learning_path": [
        {
            "week": 1, "theme": "蜂巢的社会结构与蜜蜂语言",
            "activities": ["阅读《The Honey Bee》前3章", "观看蜜蜂摇摆舞纪录片", "画出蜂群信息传递流程图"],
            "resources": ["《The Honey Bee》— James L. Gould", "BBC Earth: The Waggle Dance"],
        },
        {
            "week": 2, "theme": "蜂箱解剖与养蜂工具",
            "activities": ["研究Langstroth蜂箱的结构设计", "观看开箱检查实操视频", "用纸板制作迷你蜂箱模型"],
            "resources": ["Beekeeper's Handbook", "YouTube: First Hive Inspection"],
        },
        {
            "week": 3, "theme": "蜂蜜提取与品鉴",
            "activities": ["学习离心提取器原理", "参观本地养蜂场", "品鉴3种不同花源的蜂蜜"],
            "resources": ["National Honey Board: Honey Varietals Guide", "《蜂蜜: 自然界的液态黄金》"],
        },
        {
            "week": 4, "theme": "蜂群算法与你的兴趣交汇",
            "activities": ["研究粒子群优化（PSO）算法", "用Python实现简易蜂群觅食模拟", "写短文：如果你要为蜜蜂创作一首音乐，它会是什么节奏？"],
            "resources": ["《Swarm Intelligence》— Kennedy & Eberhart", "Processing: Boids sketch"],
        },
    ],
    "surprise_factor": (
        "当你用摄影师的眼光观察蜂巢，用算法工程师的思维理解蜂群，"
        "养蜂就不再是农业——它是一种你从未想过的、融合了艺术与科技的活体实验。"
    ),
}


def _generate_demo_plan() -> dict:
    """Return a demo plan without calling any API."""
    return dict(_DEMO_PLAN)


# ─── CLI Entry Point ───────────────────────────────────────

@app.command()
def main(
    interests: str = typer.Argument(
        None,
        help="你的兴趣领域（逗号分隔），例如: \"AI, 音乐, 摄影\"",
    ),
    animation: str = typer.Option("default", "--animation", "-a", help="鞭挞动画样式"),
    speed: float = typer.Option(1.0, "--speed", "-s", help="动画速度倍率"),
    list_domains: bool = typer.Option(False, "--list-domains", help="列出所有可选领域池"),
    list_animations: bool = typer.Option(False, "--list-animations", help="列出所有可用动画样式"),
    demo: bool = typer.Option(False, "--demo", help="演示模式（无需 API Key）"),
):
    """[TARGET] Surprise Claude — 打破算法茧房，随机生成学习计划"""

    if list_domains:
        show_list_domains()
    if list_animations:
        show_list_animations()
    if interests is None:
        _interactive()
        return

    interest_list = [s.strip() for s in interests.replace("，", ",").split(",") if s.strip()]
    if not interest_list:
        console.print("[red]错误：请提供有效的兴趣领域。[/red]")
        raise typer.Exit(1)

    valid_anims = {"default", "lightning", "chain", "laser"}
    if animation not in valid_anims:
        console.print(f"[red]未知动画: {animation}[/red]")
        console.print(f"可用: {', '.join(valid_anims)}")
        raise typer.Exit(1)

    _run(interest_list, animation, speed, demo_mode=demo)


def _interactive():
    """Interactive REPL mode."""
    clear_screen()
    console.print(f"\n[bold yellow][TARGET] Surprise Claude[/bold yellow]")
    console.print(f"[dim]打破算法茧房 · 随机学习计划生成器[/dim]")
    console.print(f"[dim]输入你的兴趣领域，AI 会刻意避开它们[/dim]")
    console.print(f"[dim]Enter 重新生成 · n 换动画 · s 设置 API · q 退出[/dim]\n")

    animation = "default"
    raw = Prompt.ask(f"\n[green]你的兴趣领域[/green]（逗号分隔）", default="")
    if not raw or raw.lower() in ("q", "quit", "exit"):
        console.print(f"\n[dim]再见！[/dim]")
        raise typer.Exit(0)

    interests = [s.strip() for s in raw.replace("，", ",").split(",") if s.strip()]

    anim_choice = Prompt.ask(
        f"\n[yellow]动画样式[/yellow] (default / lightning / chain / laser)",
        default="default",
    )
    if anim_choice in {"default", "lightning", "chain", "laser"}:
        animation = anim_choice

    _run(interests, animation, 1.0)

    while True:
        console.print()
        action = Prompt.ask(
            f"[dim]Enter 重新生成 · [yellow]n[/yellow][dim] 换动画 · [cyan]s[/cyan][dim] 设置 API · [red]q[/red][dim] 退出[/dim]",
            default="",
        ).strip().lower()

        if action in ("q", "quit", "exit"):
            console.print(f"\n[dim]再见！[/dim]")
            raise typer.Exit(0)
        elif action == "c":
            raw = Prompt.ask(f"\n[green]新兴趣领域[/green]（逗号分隔）", default="")
            if raw and raw.lower() not in ("q", "quit", "exit"):
                interests = [s.strip() for s in raw.replace("，", ",").split(",") if s.strip()]
        elif action == "n":
            anim_choice = Prompt.ask(
                f"\n[yellow]动画样式[/yellow] (default / lightning / chain / laser)",
                default=animation,
            )
            if anim_choice in {"default", "lightning", "chain", "laser"}:
                animation = anim_choice
        elif action == "s":
            _config_wizard()

        _run(interests, animation, 1.0, regenerate=True)


if __name__ == "__main__":
    app()
