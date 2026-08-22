"""Surprise Claude — CLI entry point.

Usage:
    surprise-claude                           # Interactive mode
    surprise-claude "AI, 音乐, 摄影"          # Direct mode
    surprise-claude --list-domains            # Show all domains
    surprise-claude --animation lightning     # Use lightning animation
"""

import os
import sys
import time

# ─── Platform setup (must be first, before any output) ────

if sys.platform == "win32":
    # Fix encoding
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

    # Init colorama — converts ANSI to Win32 calls on older Windows
    import colorama
    colorama.init()

import typer
from rich.console import Console
from rich.prompt import Prompt

from .display import (
    play_animation,
    display_plan,
    clear_screen,
    print_centered,
    GREEN,
    RED,
    YELLOW,
    RESET,
    BOLD,
    DIM,
    CLEAR_SCREEN,
    CURSOR_HOME,
    HIDE_CURSOR,
    SHOW_CURSOR,
)
from .backend.domain_picker import DOMAINS, pick_domain
from .backend.plan_generator import generate_plan

# Rich Console — colorama.init() already patches sys.stdout on Windows,
# so Rich will write through colorama's ANSI-to-Win32 converter.
console = Console(safe_box=True)

app = typer.Typer(
    name="surprise-claude",
    add_completion=False,
    no_args_is_help=False,
)


# ─── Core workflow ─────────────────────────────────────────

def _run(interests: list, animation: str, speed: float, regenerate: bool = False, demo_mode: bool = False):
    """Core generation workflow: animation -> API call -> display plan."""
    if not interests:
        console.print("[red]错误：请至少提供一个兴趣领域。[reset]")
        console.print("[green]示例: surprise-claude \"AI, 音乐, 摄影\"[reset]")
        raise typer.Exit(1)

    # Step 1: Pick a surprise domain
    try:
        pick = pick_domain(interests)
        picked_domain = pick["domain"]
    except Exception as e:
        console.print(f"[red]领域选择失败: {e}[reset]")
        raise typer.Exit(1)

    # Step 2: Play animation
    if not regenerate:
        clear_screen()
        print_centered("[TARGET] Surprise Claude", color=BOLD + YELLOW)
        print_centered("打破算法茧房 · 制造意外", color=DIM)
        console.print()
        print_centered(f"你的兴趣: {', '.join(interests)}", color=GREEN)
        console.print()
        print_centered("即将为你随机揭示一个陌生领域...", color=YELLOW)
        console.print()
        time.sleep(0.8)

    play_animation(animation, speed)
    time.sleep(0.3)

    # Step 3: Generate plan
    console.print(f"\n{BOLD}{YELLOW}正在生成学习 PLAN...{RESET}\n")

    try:
        if demo_mode:
            plan = _generate_demo_plan(interests, picked_domain)
        else:
            plan = generate_plan(interests, picked_domain)
    except EnvironmentError as e:
        console.print(f"[red]{e}[reset]")
        console.print()
        console.print("[green]$env:ANTHROPIC_API_KEY = \"sk-ant-...\"[reset]")
        console.print("[green]surprise-claude \"AI, 音乐\"[reset]")
        raise typer.Exit(1)
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "forbidden" in error_msg.lower():
            console.print("[red]API 调用失败 (403 Forbidden)[reset]")
            console.print()
            console.print("可能的原因:")
            console.print("  1. API Key 无效或已过期")
            console.print("  2. 账号未开通 Claude API 访问权限")
            console.print("  3. 账号余额不足")
            console.print()
            console.print("请检查:")
            console.print("  - 前往 https://console.anthropic.com/ 确认 key 状态")
            console.print("  - 确认账号有可用的 API 额度")
        else:
            console.print(f"[red]生成失败: {e}[reset]")
        raise typer.Exit(1)

    # Step 4: Display plan
    display_plan({
        "status": "success",
        "picked_domain": picked_domain,
        "surprise_score": pick.get("surprise_score", 0),
        "plan": plan,
    })


# ─── Help ──────────────────────────────────────────────────

def show_help():
    """Show styled help."""
    clear_screen()
    console.print(f"\n{BOLD}{YELLOW}[TARGET] Surprise Claude[reset]")
    console.print(f"{DIM}打破算法茧房 · 随机学习计划生成器[reset]")
    console.print(f"{DIM}大工黑客松 S2 — Track 03 · 开放原子[reset]\n")
    console.print(f"\n{BOLD}用法:[reset]")
    console.print(f"  {GREEN}surprise-claude[reset]                          交互模式（提示输入兴趣领域）")
    console.print(f"  {GREEN}surprise-claude[reset] {YELLOW}<兴趣>[reset]                 直接生成（逗号分隔）")
    console.print(f"  {GREEN}surprise-claude[reset] {YELLOW}--list-domains[reset]           列出所有可选领域")
    console.print(f"  {GREEN}surprise-claude[reset] {YELLOW}--animation <name>[reset]       选择鞭挞动画样式")
    console.print(f"  {GREEN}surprise-claude[reset] {YELLOW}--speed <n>[reset]              动画速度倍率（默认 1.0）")
    console.print(f"  {GREEN}surprise-claude[reset] {YELLOW}--demo[reset]                  演示模式（无需 API Key）")
    console.print(f"  {GREEN}surprise-claude[reset] {YELLOW}--help[reset]                  显示此帮助")
    console.print(f"\n{BOLD}动画样式:[reset]")
    console.print(f"  {GREEN}default[reset]    藤条（默认）")
    console.print(f"  {GREEN}lightning[reset]  闪电")
    console.print(f"  {GREEN}chain[reset]      链条")
    console.print(f"  {GREEN}laser[reset]      激光")
    console.print()
    raise typer.Exit()


def show_list_domains():
    """Show all available domains."""
    clear_screen()
    console.print(f"\n{BOLD}{YELLOW}[BOOK] 领域池 ({len(DOMAINS)} 个可选领域)[reset]\n")
    categories = {
        "工艺与制作": [],
        "自然世界": [],
        "历史与文化": [],
        "科学": [],
        "运动与实践": [],
        "食物与发酵": [],
        "抽象与游戏": [],
    }
    for d in DOMAINS:
        assigned = False
        for cat, keywords in {
            "工艺与制作": ["陶艺", "折纸", "皮革", "面具", "微缩", "绳结", "琥珀", "玻璃", "制琴", "Wheel"],
            "自然世界": ["养蜂", "真菌", "鸟类", "火山", "化石", "樱花", "海洋", "树木", "Bee", "Bird", "Volcano"],
            "历史与文化": ["密码学", "占星", "茶道", "古琴", "制图", "古文字", "香料", "活字"],
            "科学": ["天文", "声学", "材料", "气象", "神经美学", "量子", "合成生物"],
            "运动与实践": ["潜水", "驯鹰", "杂技", "太极", "跳绳"],
            "食物与发酵": ["发酵", "康普茶", "奶酪", "sourdough", "味噌"],
            "抽象与游戏": ["游戏设计", "谜题", "城市漫游", "Poetry", "声音景观", "Gardening"],
        }.items():
            if any(kw in d for kw in keywords):
                categories[cat].append(d)
                assigned = True
                break
        if not assigned:
            categories.setdefault("其他", []).append(d)

    for cat, items in categories.items():
        if items:
            console.print(f"  {BOLD}{cat}[reset]")
            for item in items:
                console.print(f"    {DIM}-[reset] {item}")
            console.print()
    raise typer.Exit()


def show_list_animations():
    """Show available animation styles."""
    clear_screen()
    console.print(f"\n{BOLD}{YELLOW}[ART] 可用动画样式[reset]\n")
    for name, desc in [
        ("default", "藤条（经典鞭挞 + 金色粒子爆发）"),
        ("lightning", "闪电（红色电流 + 瞬间打击）"),
        ("chain", "链条（金属质感 + 沉稳打击）"),
        ("laser", "激光（瞄准 + 瞬间命中 + 残影）"),
    ]:
        console.print(f"  {GREEN}{name:<12}[reset] {desc}")
    console.print()
    raise typer.Exit()


# ─── Demo Plan Generator ──────────────────────────────────

_DEMO_PLANS = {
    "养蜂 (Beekeeping)": {
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
                "week": 1,
                "theme": "蜂巢的社会结构与蜜蜂语言",
                "activities": [
                    "阅读《The Honey Bee》前3章",
                    "观看蜜蜂摇摆舞纪录片",
                    "画出蜂群信息传递流程图",
                ],
                "resources": [
                    "《The Honey Bee》— James L. Gould",
                    "BBC Earth: The Waggle Dance",
                ],
            },
            {
                "week": 2,
                "theme": "蜂箱解剖与养蜂工具",
                "activities": [
                    "研究Langstroth蜂箱的结构设计",
                    "观看开箱检查实操视频",
                    "用纸板制作迷你蜂箱模型",
                ],
                "resources": [
                    "Beekeeper's Handbook",
                    "YouTube: First Hive Inspection",
                ],
            },
            {
                "week": 3,
                "theme": "蜂蜜提取与品鉴",
                "activities": [
                    "学习离心提取器原理",
                    "参观本地养蜂场",
                    "品鉴3种不同花源的蜂蜜",
                ],
                "resources": [
                    "National Honey Board: Honey Varietals Guide",
                    "《蜂蜜: 自然界的液态黄金》",
                ],
            },
            {
                "week": 4,
                "theme": "蜂群算法与你的兴趣交汇",
                "activities": [
                    "研究粒子群优化（PSO）算法",
                    "用Python实现简易蜂群觅食模拟",
                    "写短文：如果你要为蜜蜂创作一首音乐，它会是什么节奏？",
                ],
                "resources": [
                    "《Swarm Intelligence》— Kennedy & Eberhart",
                    "Processing: Boids sketch",
                ],
            },
        ],
        "surprise_factor": (
            "当你用摄影师的眼光观察蜂巢，用算法工程师的思维理解蜂群，"
            "养蜂就不再是农业——它是一种你从未想过的、融合了艺术与科技的活体实验。"
        ),
    },
}


def _generate_demo_plan(interests: list, picked_domain: str) -> dict:
    """Generate a demo plan without calling Claude API."""
    return _DEMO_PLANS.get(picked_domain, _DEMO_PLANS["养蜂 (Beekeeping)"])


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
    demo: bool = typer.Option(False, "--demo", help="演示模式（无需 API Key，使用模拟 PLAN）"),
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
        console.print("[red]错误：请提供有效的兴趣领域。[reset]")
        raise typer.Exit(1)

    valid_animations = {"default", "lightning", "chain", "laser"}
    if animation not in valid_animations:
        console.print(f"[red]未知动画: {animation}[reset]")
        console.print(f"可用动画: {', '.join(valid_animations)}")
        raise typer.Exit(1)

    _run(interest_list, animation, speed, demo_mode=demo)


def _interactive():
    """Interactive REPL mode."""
    clear_screen()
    console.print(f"\n{BOLD}{YELLOW}[TARGET] Surprise Claude[reset]")
    console.print(f"{DIM}打破算法茧房 · 随机学习计划生成器[reset]")
    console.print(f"{DIM}输入你的兴趣领域，Claude 会刻意避开它们[reset]")
    console.print(f"{DIM}输入 q 退出，n 换动画，c 换兴趣[reset]\n")

    animation = "default"
    raw = Prompt.ask(f"\n{GREEN}你的兴趣领域[reset]（逗号分隔）", default="")
    if not raw or raw.lower() in ("q", "quit", "exit"):
        console.print(f"\n{DIM}再见！[reset]")
        raise typer.Exit(0)

    interests = [s.strip() for s in raw.replace("，", ",").split(",") if s.strip()]

    anim_choice = Prompt.ask(
        f"\n{YELLOW}动画样式[reset] (default / lightning / chain / laser)",
        default="default",
    )
    if anim_choice.lower() not in ("q", "quit", "exit"):
        if anim_choice in {"default", "lightning", "chain", "laser"}:
            animation = anim_choice

    _run(interests, animation, 1.0)

    while True:
        console.print()
        action = Prompt.ask(
            f"{DIM}按 {GREEN}Enter[reset]{DIM} 重新鞭挞，{CYAN}n[reset]{DIM} 换动画，{CYAN}c[reset]{DIM} 换兴趣，{RED}q[reset]{DIM} 退出[reset]",
            default="",
        ).strip().lower()

        if action in ("q", "quit", "exit"):
            console.print(f"\n{DIM}再见！[reset]")
            raise typer.Exit(0)
        elif action == "c":
            raw = Prompt.ask(f"\n{GREEN}新兴趣领域[reset]（逗号分隔）", default="")
            if raw and raw.lower() not in ("q", "quit", "exit"):
                interests = [s.strip() for s in raw.replace("，", ",").split(",") if s.strip()]
        elif action == "n":
            anim_choice = Prompt.ask(
                f"\n{YELLOW}动画样式[reset] (default / lightning / chain / laser)",
                default=animation,
            )
            if anim_choice in {"default", "lightning", "chain", "laser"}:
                animation = anim_choice

        _run(interests, animation, 1.0, regenerate=True)


if __name__ == "__main__":
    app()
