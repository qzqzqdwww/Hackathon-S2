"""Surprise-Plan — CLI entry point.

Usage:
    surprise-plan                           # Interactive mode
    surprise-plan "AI, 音乐, 摄影"          # Direct mode
    surprise-plan main --demo "AI, 音乐, 摄影"   # Demo mode (no API key)
    surprise-plan main --animation lightning      # Direct mode with animation
    surprise-plan config set                # Configure API settings
    surprise-plan config show               # Show current config
    surprise-plan config clear              # Clear saved config
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

config_app = typer.Typer(name="config", help="管理 API 配置")

app = typer.Typer(
    name="surprise-plan",
    add_completion=False,
    no_args_is_help=False,
)
app.add_typer(config_app, name="config")


# ─── Default callback: interactive mode when no subcommand ──

@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    list_domains: bool = typer.Option(False, "--list-domains", help="列出所有可选领域池"),
    list_animations: bool = typer.Option(False, "--list-animations", help="列出所有可用动画样式"),
):
    """Default entry point: interactive mode when no subcommand given."""
    if ctx.invoked_subcommand is not None:
        return
    if list_domains:
        show_list_domains()
    if list_animations:
        show_list_animations()
    _interactive()


# ─── Core workflow ─────────────────────────────────────────

def _run(interests: list, animation: str, speed: float, regenerate: bool = False, demo_mode: bool = False):
    """Animation -> domain pick -> API call -> display plan."""
    if not interests:
        console.print("[red]错误：请至少提供一个兴趣领域。[/red]")
        console.print("[green]示例: surprise-plan \"AI, 音乐, 摄影\"[/green]")
        raise typer.Exit(1)

    provider = get_current_provider()

    try:
        pick = pick_domain(interests)
    except Exception as e:
        console.print(f"[red]领域选择失败: {e}[/red]")
        raise typer.Exit(1)

    if not regenerate:
        clear_screen()
        console.print("[bold yellow][TARGET] Surprise-Plan[/bold yellow]")
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
        console.print(f"[dim]查看配置: surprise-plan config show[/dim]")
        console.print(f"[green]设置 API:  surprise-plan config set[/green]")
        raise typer.Exit(1)
    except Exception as e:
        msg = str(e)
        if "403" in msg or "forbidden" in msg.lower() or "401" in msg:
            console.print(f"[red]API 调用失败（认证失败）— [{provider}][/red]")
            console.print("  1. API Key 无效或已过期")
            console.print("  2. 账号未开通 API 访问权限")
            console.print("  3. 账号余额不足")
            console.print()
            console.print(f"[dim]运行 surprise-plan config set 更新 Key[/dim]")
        else:
            console.print(f"[red]生成失败: {e}[/red]")
        raise typer.Exit(1)

    display_plan({
        "status": "success",
        "picked_domain": pick["domain"],
        "surprise_score": pick.get("surprise_score", 0),
        "plan": plan,
    })


# ─── Direct command (surprise-plan "AI, 音乐, 摄影") ────

@app.command()
def main(
    interests: str = typer.Argument(
        None,
        help="你的兴趣领域（逗号分隔），例如: \"AI, 音乐, 摄影\"",
    ),
    demo: bool = typer.Option(False, "--demo", help="演示模式（无需 API Key）"),
    animation: str = typer.Option("default", "--animation", "-a", help="动画样式"),
    speed: float = typer.Option(1.0, "--speed", "-s", help="动画速度倍率"),
):
    """[TARGET] Surprise-Plan — 打破算法茧房，随机生成学习计划"""
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


# ─── Helpers ───────────────────────────────────────────────

def show_list_domains():
    clear_screen()
    console.print(f"\n[bold yellow][BOOK] 领域池 ({len(DOMAINS)} 个可选领域)[/bold yellow]\n")
    categories = {
        "人文科学": ["古典学", "比较文学", "逻辑学", "伦理学", "修辞学", "文献学", "符号学", "神话学"],
        "社会科学": ["社会心理学", "文化人类学", "发展经济学", "政治哲学", "性别研究", "传播学", "犯罪学", "社会网络分析"],
        "自然科学": ["分子生物学", "天体物理学", "量子力学", "有机化学", "地质学", "海洋学", "气象学", "神经科学", "免疫学", "生态学", "古气候学", "天体测量学"],
        "数学与计算机科学": ["密码学", "拓扑学", "数论", "计算语言学", "运筹学", "博弈论", "混沌理论", "微分几何", "信息论", "计算机图形学"],
        "艺术与设计": ["雕塑", "版画", "纤维艺术", "数字媒体艺术", "服装设计", "陶艺", "玻璃吹制", "漆艺", "织物设计", "概念艺术"],
        "音乐与表演": ["指挥学", "音乐治疗", "声音艺术", "爵士乐研究", "民族音乐学", "电子音乐作曲", "配音艺术", "默剧与肢体剧"],
        "建筑与空间": ["建筑声学", "室内设计", "园林设计", "城市规划", "舞台设计", "工业设计", "可持续建筑", "展览设计"],
        "经济与管理": ["金融学", "市场营销", "会计学", "国际法", "知识产权法", "供应链管理", "人力资源", "创业学", "公共政策"],
        "医学与健康": ["解剖学", "药理学", "公共卫生", "营养学", "运动生理学", "心理学", "睡眠科学", "康复医学"],
        "农业与生命科学": ["农艺学", "兽医学", "食品科学", "园艺学", "土壤学", "水产养殖", "发酵工程", "植物病理学"],
        "传统技艺": ["花道", "书道", "盆景", "缂丝", "景泰蓝", "篆刻", "榫卯工艺", "竹编", "蜡染", "漆器"],
        "自然与野外": ["养蜂", "真菌学", "鸟类学", "火山学", "古生物学", "樱花栽培", "海洋生物学", "树木年轮学", "陨石学", "潮间带生态"],
        "历史与文献": ["密码学历史", "占星学历史", "茶道", "古琴", "制图学历史", "古文字学", "香料调制", "活字印刷"],
        "工程与材料": ["声学", "材料科学", "机器人学", "航空航天", "生物医学工程", "环境工程", "核工程", "纳米技术"],
        "运动与实践": ["潜水", "驯鹰", "杂技", "太极推手", "花式跳绳", "风帆冲浪", "攀岩", "武术套路", "瑜伽哲学", "剑道"],
        "食物与发酵": ["发酵食品", "康普茶", "奶酪制作", "酸面团烘焙", "味噌制作", "分子料理", "咖啡烘焙", "巧克力制作"],
        "抽象与游戏": ["游戏设计哲学", "谜题设计", "城市漫游", "生成式诗歌", "声音景观", "数字园艺", "交互叙事", "角色扮演设计"],
        "跨学科前沿": ["认知科学", "生物信息学", "数字人文", "系统生物学", "仿生学", "复杂系统", "科学哲学", "技术伦理"],
    }
    # Remove duplicate keyword that matches a domain in an earlier category
    # "免疫学" is in 自然科学; remove from 医学与健康 to avoid double-assignment
    assigned = {d: False for d in DOMAINS}
    for cat, keywords in categories.items():
        matched = [d for d in DOMAINS if not assigned[d] and any(d.startswith(kw) for kw in keywords)]
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


# ─── Config Subcommands ────────────────────────────────────

@config_app.command("set")
def config_set(
    provider: str = typer.Option(None, "--provider", "-p", help="AI 引擎名称"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="API Key"),
    base_url: str = typer.Option(None, "--base-url", "-u", help="API 地址"),
    model: str = typer.Option(None, "--model", "-m", help="模型名称"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="交互式设置"),
):
    """设置 API 配置（保存到 ~/.surprise-plan/config.json）"""
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
        console.print(f"\n[dim]已取消。[dim]")
        raise typer.Exit(0)
    clear_config()
    console.print(f"\n[green]配置已清除。[/green]")


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
    api_key = Prompt.ask(f"\n[green]API Key[/green]{key_hint}")
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


# ─── Interactive REPL ──────────────────────────────────────

def _interactive(default_anim: str = "default", demo: bool = False):
    """Interactive REPL mode."""
    clear_screen()
    console.print(f"\n[bold yellow][TARGET] Surprise-Plan[/bold yellow]")
    console.print(f"[dim]打破算法茧房 · 随机学习计划生成器[/dim]")
    console.print(f"[dim]输入你的兴趣领域，AI 会刻意避开它们[/dim]")
    console.print(f"[dim]Enter 重新生成 · n 换动画 · s 设置 API · q 退出[/dim]\n")

    animation = default_anim
    raw = Prompt.ask(f"\n[green]你的兴趣领域[/green]（逗号分隔）", default="")
    if not raw or raw.lower() in ("q", "quit", "exit"):
        console.print(f"\n[dim]再见！[/dim]")
        raise typer.Exit(0)

    interests = [s.strip() for s in raw.replace("，", ",").split(",") if s.strip()]

    anim_choice = Prompt.ask(
        f"\n[yellow]动画样式[/yellow] (default / lightning / chain / laser)",
        default=animation,
    )
    if anim_choice in {"default", "lightning", "chain", "laser"}:
        animation = anim_choice

    _run(interests, animation, 1.0, demo_mode=demo)

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

        _run(interests, animation, 1.0, regenerate=True, demo_mode=demo)


if __name__ == "__main__":
    app()
