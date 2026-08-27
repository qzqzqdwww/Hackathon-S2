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
import random
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

def _run(interests: list[str], animation: str, speed: float, regenerate: bool = False, demo_mode: bool = False, difficulty: str = "2", output: str = None):
    """Animation -> domain pick -> API call -> display plan -> optional export.

    Returns (pick, plan) dicts so the interactive loop can reuse them.
    """
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
        console.print(f"\n[bold yellow][TARGET] Surprise-Plan[/bold yellow]")
        console.print(f"[dim]打破算法茧房 · 制造意外[/dim]")
        console.print()
        console.print(f"[green]你的兴趣: {', '.join(interests)}[/green]")
        console.print(f"[yellow]难度: {'轻松入门' if difficulty == '1' else '深入挑战' if difficulty == '3' else '标准'}[/yellow]")
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
            plan = generate_plan(interests, pick["domain"], difficulty=difficulty)
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

    if output:
        _export_plan(output, {
            "status": "success",
            "picked_domain": pick["domain"],
            "surprise_score": pick.get("surprise_score", 0),
            "plan": plan,
        })

    return pick, plan


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
    difficulty: str = typer.Option("2", "--difficulty", "-d", help="难度: 1=轻松, 2=标准, 3=深入"),
    output: str = typer.Option(None, "--output", "-o", help="导出文件路径（.json / .md / .txt / .html）"),
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

    if difficulty not in ("1", "2", "3"):
        console.print(f"[red]难度必须是 1、2 或 3[/red]")
        raise typer.Exit(1)

    _run(interest_list, animation, speed, demo_mode=demo, difficulty=difficulty, output=output)


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
        console.print(f"\n[dim]已取消。[/dim]")
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

    # Offer to test the connection
    test_choice = Prompt.ask(
        f"\n[yellow]测试 API 连接？[/yellow]",
        choices=["y", "n"],
        default="y",
    )
    if test_choice == "y":
        _run_connection_test(cfg)


def _parse_provider_choice(choice: str, names: list[str]) -> str:
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
    raise typer.BadParameter(f"未知引擎: {choice}，请输入序号或名称")


def _export_plan(filepath: str, plan_data: dict):
    """Export plan to file with format auto-detected from extension."""
    from .backend.plan_exporter import export_plan
    try:
        out_path = export_plan(plan_data, filepath)
        console.print(f"\n[green]计划已导出至: {out_path}[/green]")
    except Exception as e:
        console.print(f"\n[red]导出失败: {e}[/red]")


def _print_config():
    from .backend.provider import get_config_summary
    s = get_config_summary()
    console.print(f"\n  引擎: [green]{s['provider']}[/green]")
    console.print(f"  Key:   {s['api_key']}")
    console.print(f"  地址: {s['base_url']}")
    console.print(f"  模型: {s['model']}\n")


def _run_connection_test(cfg: dict):
    """Test API connectivity and display results."""
    from rich.panel import Panel
    from .backend.provider import test_api_connection

    console.print(f"\n[dim]正在测试连接...[/dim]")
    result = test_api_connection(
        provider=cfg.get("provider", ""),
        api_key=cfg.get("api_key", ""),
        model=cfg.get("model", ""),
        base_url=cfg.get("base_url", ""),
    )

    if result["ok"]:
        console.print(f"\n[green][PASS] 连接成功！[/green]")
        console.print(f"  引擎:    [cyan]{result['provider']}[/cyan]")
        console.print(f"  模型:    [cyan]{result['model']}[/cyan]")
        console.print(f"  地址:    [dim]{result['base_url']}[/dim]")
        console.print(f"  延迟:    [yellow]{result['latency_ms']} ms[/yellow]")
    else:
        error_type_label = {
            "auth": "认证失败",
            "network": "网络/连接错误",
            "model": "模型不可用",
            "unknown": "未知错误",
        }.get(result.get("error_type", "unknown"), "错误")
        console.print(f"\n[red][FAIL] 连接失败 — {error_type_label}[/red]")
        console.print(f"  引擎:  [cyan]{result['provider']}[/cyan]")
        console.print(f"  模型:  [cyan]{result['model']}[/cyan]")
        console.print(f"  地址:  [dim]{result['base_url']}[/dim]")
        console.print(f"  延迟:  [dim]{result['latency_ms']} ms[/dim]")
        console.print(f"  错误:  [red]{result['error'][:200]}[/red]")
        console.print()
        console.print(f"[yellow]建议:[/yellow]")
        if result.get("error_type") == "auth":
            console.print(f"  - 检查 API Key 是否正确")
            console.print(f"  - 运行 surprise-plan config set 重新设置")
        elif result.get("error_type") == "network":
            console.print(f"  - 检查网络连接")
            console.print(f"  - 检查 API 地址是否正确")
            console.print(f"  - 如使用代理，检查代理设置")
        elif result.get("error_type") == "model":
            console.print(f"  - 模型名称可能不正确，检查拼写")
            console.print(f"  - 确认账号有权限访问该模型")
        else:
            console.print(f"  - 查看上方错误信息")
            console.print(f"  - 运行 surprise-plan config show 确认配置")


# ─── Demo Plan Generator ─────────────────────────────────────

_DEMO_TEMPLATES = {
    "activities": [
        "阅读入门指南前3章，整理核心概念笔记",
        "观看入门纪录片/公开课，记录3个最让你惊讶的事实",
        "搜索该领域的经典案例，分析其成功或失败的关键因素",
        "尝试一次基础实践操作（实验/创作/模拟），记录过程与感受",
        "阅读领域内的经典著作/论文，写出200字读后感",
        "加入一个线上社区（论坛/Discord/Reddit），观察社区讨论热点",
        "制作一张该领域的知识地图，标注核心概念关系",
        "采访一位从业者（或观看访谈视频），总结他们的日常工作",
        "对比该领域与你熟悉领域的异同，列出5个关键差异",
        "尝试将该领域的核心方法应用到你的兴趣领域",
        "参加一个线上讲座或 workshop，做结构化笔记",
        "用思维导图梳理该领域的历史发展脉络",
    ],
    "resources": [
        "Wikipedia 相关条目（多读几遍，注意引用来源）",
        "YouTube / Bilibili 系列视频（搜索'领域名 + 入门'）",
        "Coursera / edX 入门课程（旁听免费版本）",
        "该领域经典著作（搜索'领域名 + 必读书单'）",
        "TED 演讲（搜索领域名，筛选高评分）",
        "Kaggle 入门项目（如适用）",
        "GitHub 开源项目（搜索领域名 + tutorial）",
        "arXiv 近3年综述论文（搜索'领域名 + survey'）",
        "行业博客/Substack（搜索领域名 + newsletter）",
        "在线交互式教程（如适用，如 Codecademy、Brilliant）",
    ],
    "connections": [
        "该领域的核心思想可以用你熟悉的领域来类比理解",
        "两种领域的底层方法论惊人地相似，只是应用场景不同",
        "你已有的技能可以直接迁移到这个新领域",
        "这个领域的历史发展与你的兴趣领域有交汇点",
        "该领域正在使用的工具/技术，你在其他场景中见过",
        "两者的理论基础都源于同一学科的早期思想",
    ],
    "surprise_factors": [
        "当你用全新的视角审视熟悉的事物，你会发现——世界远比你想象的有趣。",
        "学习一门新领域最有趣的部分，不是掌握知识，而是发现旧知识的全新应用场景。",
        "每一个'冷门'领域，都藏着通往下一个大突破的钥匙。",
        "跨界的灵感往往来自最意想不到的地方——保持好奇心。",
        "你以为自己只是在学一个新领域，其实你在构建一个全新的思维模型。",
    ],
}


def _generate_demo_plan() -> dict:
    """Generate a random demo plan without calling any API."""
    domain = random.choice(DOMAINS)
    raw_name = domain.split("(")[0].strip()
    activities_pool = list(_DEMO_TEMPLATES["activities"])
    resources_pool = list(_DEMO_TEMPLATES["resources"])
    connections_pool = list(_DEMO_TEMPLATES["connections"])
    surprise_pool = list(_DEMO_TEMPLATES["surprise_factors"])

    random.shuffle(activities_pool)
    random.shuffle(resources_pool)
    random.shuffle(connections_pool)

    activities_per_week = 3
    resources_per_week = 2

    learning_path = []
    for week_num in range(1, 5):
        week_activities = activities_pool[week_num * activities_per_week : (week_num + 1) * activities_per_week]
        week_resources = resources_pool[week_num * resources_per_week : (week_num + 1) * resources_per_week]
        if week_num == 4:
            theme = f"整合：{raw_name} 与你的兴趣交汇"
            week_activities = activities_pool[-activities_per_week:]
            week_resources = resources_pool[-resources_per_week:]
        else:
            themes = [f"{raw_name} 基础入门", f"{raw_name} 核心概念", f"{raw_name} 进阶实践"]
            theme = themes[week_num - 1]
        learning_path.append({
            "week": week_num,
            "theme": theme,
            "activities": week_activities,
            "resources": week_resources,
        })

    key_terms_pool = [
        f"{raw_name}的核心定义与边界",
        "该领域的基础术语体系",
        "该领域的历史起源与关键转折点",
        "当前主流方法论与前沿方向",
        "该领域与其他学科的交叉点",
        "实践中的常见误区与最佳实践",
    ]
    random.shuffle(key_terms_pool)

    return {
        "domain": domain,
        "tagline": f"一次意外的相遇：{raw_name}，也许就是你一直在寻找的新方向",
        "why_interesting": (
            f"{raw_name}是一个充满惊喜的领域。"
            f"它融合了理论与实践，既有深厚的理论基础，又有广泛的应用场景。"
            f"无论你是追求知识深度，还是寻找新的灵感来源，"
            f"{raw_name}都能给你带来意想不到的收获。"
            f"让我们一起踏上这段探索之旅。"
        ),
        "connections": connections_pool[:3],
        "key_terms": key_terms_pool[:5],
        "fun_fact": (
            f"Did you know? {raw_name} 领域每年都有大量新发现，"
            f"而你此刻正在探索的，正是人类知识的前沿。"
        ),
        "learning_path": learning_path,
        "surprise_factor": random.choice(surprise_pool),
    }


# ─── Interactive REPL ──────────────────────────────────────

def _interactive(default_anim: str = "default", demo: bool = False):
    """Interactive REPL mode."""
    clear_screen()
    console.print(f"\n[bold yellow][TARGET] Surprise-Plan[/bold yellow]")
    console.print(f"[dim]打破算法茧房 · 随机学习计划生成器[/dim]")
    console.print(f"[dim]输入你的兴趣领域，AI 会刻意避开它们[/dim]")
    console.print()
    console.print(f"[bold]难度选择:[/bold]")
    console.print(f"  [green]1[/green]. 轻松入门 (浅显易懂，趣味为主)")
    console.print(f"  [green]2[/green]. 标准 (平衡理论与实践)")
    console.print(f"  [green]3[/green]. 深入挑战 (硬核内容，大量实践)")

    difficulty = Prompt.ask(
        f"\n[yellow]选择难度[/yellow]",
        choices=["1", "2", "3"],
        default="2",
    )

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

    # First plan generation
    last_pick, last_plan = _run(interests, animation, 1.0, demo_mode=demo, difficulty=difficulty)

    while True:
        console.print()
        action = Prompt.ask(
            f"[dim]Enter 换领域 · [yellow]d[/yellow][dim] 深入 · [cyan]n[/cyan][dim] 动画 · "
            f"[green]e[/green][dim] 导出 · [magenta]c[/magenta][dim] 改兴趣 · [red]q[/red][dim] 退出[/dim]",
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
        elif action == "d":
            _dive_deeper(interests, difficulty=difficulty, demo_mode=demo)
            continue
        elif action == "e":
            filepath = Prompt.ask(
                f"\n[green]导出文件路径[/green]",
                default="plan.md",
            )
            if filepath:
                from .backend.plan_exporter import detect_format, export_plan
                plan_data = {
                    "status": "success",
                    "picked_domain": last_pick["domain"],
                    "surprise_score": last_pick.get("surprise_score", 0),
                    "plan": last_plan,
                }
                try:
                    out = export_plan(plan_data, filepath)
                    fmt = detect_format(filepath)
                    console.print(f"\n[green]已导出 ({fmt}) -> {out}[/green]")
                except Exception as ex:
                    console.print(f"\n[red]导出失败: {ex}[/red]")
            continue
        elif action == "":
            pass  # Enter = regenerate with new domain

        last_pick, last_plan = _run(interests, animation, 1.0, regenerate=True, demo_mode=demo, difficulty=difficulty)


def _dive_deeper(interests: list[str], difficulty: str = "2", demo_mode: bool = False):
    """Generate an extended deep-dive plan for a specific week/topic."""
    console.print(f"\n[bold yellow][DIVE] 深入探索[/bold yellow]")
    console.print(f"[dim]输入你想深入了解的主题（例如：'真菌的菌丝网络'）[/dim]")

    topic = Prompt.ask(f"\n[green]主题[/green]", default="")
    if not topic or topic.lower() in ("q", "quit", "exit"):
        return

    clear_screen()
    console.print(f"\n[bold yellow][DIVE] 深入: {topic}[/bold yellow]\n")
    console.print(f"[dim]正在生成深度探索内容...[/dim]\n")

    try:
        if demo_mode:
            plan = _generate_demo_plan()
        else:
            plan = generate_plan(interests, topic, difficulty=difficulty)
    except Exception as e:
        console.print(f"[red]生成失败: {e}[/red]")
        return

    display_plan({
        "status": "success",
        "picked_domain": topic,
        "surprise_score": 0,
        "plan": plan,
    })


if __name__ == "__main__":
    app()
