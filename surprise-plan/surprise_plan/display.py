"""Terminal-native display engine for Surprise-Plan.

Provides:
- ASCII art Claude figure with animated expressions
- Frame-based whip animation system (multiple styles)
- Rich terminal output for plan display
- Windows-safe: uses Rich console for all output
"""

import time
import sys

# ─── ASCII Art ──────────────────────────────────────────────

CLAUDE_NORMAL = """\
     /\\_/\\
    ( o.o )
     > ^ <
    /|   |\\
   (_|   |_)"""

CLAUDE_HIT = """\
     /\\_/\\
    ( >o< )
     > w <
    /|   |\\
   (_|   |_)"""

CLAUDE_DAZED = """\
     /\\_/\\
    ( @.@ )
     > ~ <
    /|   |\\
   (_|   |_)"""

CLAUDE_SPARKLE = """\
     /\\_/\\
    ( *.* )
     > ^ <
    /|   |\\
   (_|   |_)"""


# ─── Animation Helpers ──────────────────────────────────────

def _center(text: str, width: int = 40) -> str:
    lines = text.split("\n")
    return "\n".join(line.center(width) for line in lines)


def _whip_line(x_offset: int, length: int = 4) -> str:
    lines = []
    base = " " * x_offset
    lines.append(f"{base}|")
    for i in range(1, length):
        lines.append(f"{base}{' ' * i}|")
    if length > 1:
        lines.append(f"{base}{' ' * (length - 1)}\\")
    return "\n".join(lines)


def _particles(count: int = 6) -> str:
    symbols = ["*", "+", ".", ":", "o", "O"]
    parts = []
    for i in range(count):
        sym = symbols[i % len(symbols)]
        spacing = " " * (i * 3)
        parts.append(f"{spacing}{sym}")
    return "\n".join(parts)


def _speed_line(offset: int) -> str:
    return f"{' ' * offset}======="


# ─── Animation Frames ───────────────────────────────────────

def get_animation(name: str):
    name = name.lower().strip()
    if name in ("lightning", "闪电"):
        return _lightning_frames()
    elif name in ("chain", "链条"):
        return _chain_frames()
    elif name in ("laser", "激光"):
        return _laser_frames()
    return _default_frames()


def _default_frames():
    return [
        (f"{_center(_whip_line(22, 5))}\n{_center(CLAUDE_NORMAL)}", 150),
        (f"{_speed_line(14)}\n{_center(_whip_line(18, 3))}\n{_center(CLAUDE_NORMAL)}", 80),
        (f"{_center(_whip_line(14, 2))}\n{_center(CLAUDE_NORMAL)}", 60),
        (f"{_center('* BOOM *')}\n{_center(CLAUDE_HIT)}", 200),
        (f"{_center(CLAUDE_DAZED)}\n{_center(_particles(4))}", 120),
        (f"{_center('* * *')}\n{_center(CLAUDE_SPARKLE)}", 250),
        (f"{_center(CLAUDE_NORMAL)}\n{_center('  *')}", 150),
    ]


def _lightning_frames():
    return [
        (f"{_center(CLAUDE_NORMAL)}", 80),
        (f"{_speed_line(10)}\n{_center(CLAUDE_NORMAL)}", 60),
        (f"{_speed_line(14)}\n{_center('ZZAP')}\n{_center(CLAUDE_NORMAL)}", 50),
        (f"{_center('ZAP * BOOM * ZAP')}\n{_center(CLAUDE_HIT)}", 180),
        (f"{_center(CLAUDE_DAZED)}\n{_center('ZAP  *')}", 100),
        (f"{_center('* * *')}\n{_center(CLAUDE_SPARKLE)}", 250),
        (f"{_center(CLAUDE_NORMAL)}", 150),
    ]


def _chain_frames():
    return [
        (f"{_center(_whip_line(22, 6))}\n{_center(CLAUDE_NORMAL)}", 150),
        (f"{_center(_whip_line(16, 4))}\n{_center(CLAUDE_NORMAL)}", 80),
        (f"{_center(_whip_line(12, 3))}\n{_center(CLAUDE_NORMAL)}", 60),
        (f"{_center('### * BOOM * ###')}\n{_center(CLAUDE_HIT)}", 200),
        (f"{_center(CLAUDE_DAZED)}\n{_center(_particles(4))}", 120),
        (f"{_center(CLAUDE_SPARKLE)}\n{_center('  ###')}", 250),
        (f"{_center(CLAUDE_NORMAL)}", 150),
    ]


def _laser_frames():
    return [
        (f"{_center('==========')}\n{_center(CLAUDE_NORMAL)}", 80),
        (f"{_center('============')}\n{_center('[TARGETING...]')}\n{_center(CLAUDE_NORMAL)}", 100),
        (f"{_center('===============')}\n{_center('*')}\n{_center(CLAUDE_HIT)}", 150),
        (f"{_center('=====')}\n{_center(CLAUDE_DAZED)}\n{_center(_particles(3))}", 100),
        (f"{_center('* * *')}\n{_center(CLAUDE_SPARKLE)}", 250),
        (f"{_center(CLAUDE_NORMAL)}\n{_center('  *')}", 150),
    ]


# ─── Animation Player ───────────────────────────────────────

def play_animation(name: str = "default", speed: float = 1.0) -> None:
    """Play a terminal animation frame-by-frame."""
    from rich.console import Console
    console = Console()

    frames = get_animation(name)
    if not frames:
        return

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        for frame_text, duration_ms in frames:
            console.clear()
            console.print(frame_text)
            time.sleep((duration_ms / 1000.0) / speed)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


# ─── Plan Display ───────────────────────────────────────────

def display_plan(data: dict) -> None:
    """Display a generated plan using Rich formatting (cross-platform safe)."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    plan = data.get("plan", {})
    domain = plan.get("domain", data.get("picked_domain", "?"))
    tagline = plan.get("tagline", "")
    why = plan.get("why_interesting", "")
    connections = plan.get("connections", [])
    learning_path = plan.get("learning_path", [])
    surprise = plan.get("surprise_factor", "")

    console = Console()

    header = Text()
    header.append(f"\n[TARGET] {domain}\n", style="bold orange1")
    if tagline:
        header.append(f"{tagline}\n", style="italic red")
    console.print(Panel(header, border_style="orange1", padding=(1, 2)))

    console.print(f"\n[bold yellow][SEARCH] 为什么学这个[/bold yellow]")
    console.print(Panel(why, border_style="dim", padding=(0, 1)))

    if connections:
        console.print(f"\n[bold yellow][BRIDGE] 与你兴趣的意外关联[/bold yellow]")
        for conn in connections:
            console.print(f"  [cyan]->[/cyan] {conn}")

    if learning_path:
        console.print(f"\n[bold yellow][MAP] 四周学习路径[/bold yellow]")
        for week in learning_path:
            week_num = week.get("week", "?")
            theme = week.get("theme", "")
            activities = week.get("activities", [])
            resources = week.get("resources", [])

            week_text = f"[bold]第 {week_num} 周：{theme}[/bold]\n"
            for act in activities:
                week_text += f"  [cyan]-[/cyan] {act}\n"
            if resources:
                week_text += f"  [dim][BOOK] {'；'.join(resources)}[/dim]\n"

            console.print(Panel(week_text.strip(), border_style="blue", padding=(0, 1)))

    if surprise:
        console.print(f"\n[bold magenta][SPARK] 意外之喜[/bold magenta]")
        console.print(Panel(
            Text(surprise, style="italic light_goldenrod1"),
            border_style="magenta",
            padding=(0, 1),
        ))

    console.print()


# ─── Utility Functions ──────────────────────────────────────

def clear_screen() -> None:
    """Clear terminal screen using Rich (cross-platform safe)."""
    from rich.console import Console
    Console().clear()
