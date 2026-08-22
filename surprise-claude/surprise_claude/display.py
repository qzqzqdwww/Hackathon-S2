"""Terminal-native display engine for Surprise Claude.

Provides:
- ASCII art Claude figure with animated expressions
- Frame-based whip animation system (multiple styles)
- Rich terminal output for plan display
- Windows-safe: uses Rich markup tags instead of raw ANSI
"""

import time
import sys
import os
import re
from typing import List, Tuple

# ─── ANSI helpers (for animation system only) ──────────────
# These are written directly to sys.stdout and go through colorama on Windows.

def _ansi(code: str) -> str:
    return f"\033[{code}m"

RESET = _ansi("0")
BOLD = _ansi("1")
DIM = _ansi("2")
RED = _ansi("91m")
GREEN = _ansi("92m")
YELLOW = _ansi("93m")
BLUE = _ansi("94m")
MAGENTA = _ansi("95m")
CYAN = _ansi("96m")
WHITE = _ansi("97m")
ORANGE = _ansi("38;5;208m")

# Cursor control
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CURSOR_HOME = "\033[H"
CLEAR_SCREEN = "\033[2J"
CURSOR_UP = "\033[F"
SAVE_CURSOR = "\033[s"
RESTORE_CURSOR = "\033[u"

# ─── Rich markup tags (for console output) ─────────────────
# Use these with console.print() — Rich handles them cross-platform.
# DO NOT use raw ANSI constants (BOLD, RED, etc.) with console.print().

_TAG_MAP = {
    "BOLD": "bold",
    "DIM": "dim",
    "RED": "red",
    "GREEN": "green",
    "YELLOW": "yellow",
    "BLUE": "blue",
    "MAGENTA": "magenta",
    "CYAN": "cyan",
    "WHITE": "white",
    "ORANGE": "orange1",
    "RESET": "reset",
}


def rprint(text: str = "") -> None:
    """Print text with Rich markup, safely on all platforms."""
    try:
        from rich.console import Console
        console = Console()
        console.print(text)
    except ImportError:
        # Fallback: strip Rich tags and print plain
        plain = re.sub(r'\[/?[a-z ]+\]', '', text)
        print(plain)


def rpanel(text: str, border: str = "dim", title: str = "") -> None:
    """Print text in a Rich panel."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        console = Console()
        console.print(Panel(text, border_style=border, title=title, padding=(0, 1)))
    except ImportError:
        print(text)


# ─── ASCII Art ─────────────────────────────────────────────

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


# ─── Animation Helpers ─────────────────────────────────────

def _center(text: str, width: int = 40) -> str:
    lines = text.split("\n")
    return "\n".join(line.center(width) for line in lines)


def _whip_line(x_offset: int, length: int = 4, color: str = YELLOW) -> str:
    lines = []
    base = " " * x_offset
    lines.append(f"{color}{base}|{RESET}")
    for i in range(1, length):
        lines.append(f"{color}{base}{' ' * i}|{RESET}")
    if length > 1:
        lines.append(f"{color}{base}{' ' * (length - 1)}\\{RESET}")
    return "\n".join(lines)


def _particles(count: int = 6, color: str = YELLOW) -> str:
    symbols = ["*", "+", ".", ":", "o", "O"]
    parts = []
    for i in range(count):
        sym = symbols[i % len(symbols)]
        spacing = " " * (i * 3)
        parts.append(f"{color}{spacing}{sym}{RESET}")
    return "\n".join(parts)


def _speed_line(offset: int, color: str = YELLOW) -> str:
    return f"{color}{' ' * offset}======={RESET}"


# ─── Animation Frames ──────────────────────────────────────

def get_animation(name: str) -> List[Tuple[str, int]]:
    name = name.lower().strip()
    if name in ("lightning", "闪电"):
        return _lightning_frames()
    elif name in ("chain", "链条"):
        return _chain_frames()
    elif name in ("laser", "激光"):
        return _laser_frames()
    else:
        return _default_frames()


def _default_frames() -> List[Tuple[str, int]]:
    return [
        (f"{_center(_whip_line(22, 5))}\n{_center(CLAUDE_NORMAL)}", 150),
        (f"{_speed_line(14)}\n{_center(_whip_line(18, 3))}\n{_center(CLAUDE_NORMAL)}", 80),
        (f"{_center(_whip_line(14, 2))}\n{_center(CLAUDE_NORMAL)}", 60),
        (f"{BOLD}{RED}{_center('* BOOM *')}{RESET}\n{_center(CLAUDE_HIT)}", 200),
        (f"{_center(CLAUDE_DAZED)}\n{_center(_particles(4))}", 120),
        (f"{CYAN}{_center('* * *')}{RESET}\n{_center(CLAUDE_SPARKLE)}", 250),
        (f"{_center(CLAUDE_NORMAL)}\n{DIM}{_center('  *')}{RESET}", 150),
    ]


def _lightning_frames() -> List[Tuple[str, int]]:
    return [
        (f"{_center(CLAUDE_NORMAL)}", 80),
        (f"{RED}{_speed_line(10)}{RESET}\n{_center(CLAUDE_NORMAL)}", 60),
        (f"{YELLOW}{_speed_line(14)}{RESET}\n{CYAN}{_center('ZZAP')}{RESET}\n{_center(CLAUDE_NORMAL)}", 50),
        (f"{BOLD}{WHITE}{_center('ZAP * BOOM * ZAP')}{RESET}\n{_center(CLAUDE_HIT)}", 180),
        (f"{_center(CLAUDE_DAZED)}\n{CYAN}{_center('ZAP  *')}{RESET}", 100),
        (f"{CYAN}{_center('* * *')}{RESET}\n{_center(CLAUDE_SPARKLE)}", 250),
        (f"{_center(CLAUDE_NORMAL)}", 150),
    ]


def _chain_frames() -> List[Tuple[str, int]]:
    chain_color = DIM + WHITE
    return [
        (f"{_center(_whip_line(22, 6, chain_color))}\n{_center(CLAUDE_NORMAL)}", 150),
        (f"{_center(_whip_line(16, 4, chain_color))}\n{_center(CLAUDE_NORMAL)}", 80),
        (f"{_center(_whip_line(12, 3, chain_color))}\n{_center(CLAUDE_NORMAL)}", 60),
        (f"{BOLD}{WHITE}{_center('### * BOOM * ###')}{RESET}\n{_center(CLAUDE_HIT)}", 200),
        (f"{_center(CLAUDE_DAZED)}\n{_center(_particles(4, WHITE))}", 120),
        (f"{_center(CLAUDE_SPARKLE)}\n{DIM}{_center('  ###')}{RESET}", 250),
        (f"{_center(CLAUDE_NORMAL)}", 150),
    ]


def _laser_frames() -> List[Tuple[str, int]]:
    laser_color = CYAN
    return [
        (f"{laser_color}{_center('==========')}{RESET}\n{_center(CLAUDE_NORMAL)}", 80),
        (f"{laser_color}{_center('============')}{RESET}\n{BOLD}{_center('[TARGETING...]')}{RESET}\n{_center(CLAUDE_NORMAL)}", 100),
        (f"{BOLD}{laser_color}{_center('===============')}{RESET}\n{RED}{_center('*')}{RESET}\n{_center(CLAUDE_HIT)}", 150),
        (f"{laser_color}{_center('=====')}{RESET}\n{_center(CLAUDE_DAZED)}\n{_center(_particles(3, laser_color))}", 100),
        (f"{CYAN}{_center('* * *')}{RESET}\n{_center(CLAUDE_SPARKLE)}", 250),
        (f"{_center(CLAUDE_NORMAL)}\n{DIM}{_center('  *')}{RESET}", 150),
    ]


# ─── Animation Player ──────────────────────────────────────

def play_animation(name: str = "default", speed: float = 1.0) -> None:
    """Play a terminal animation using raw ANSI (goes through colorama on Windows)."""
    frames = get_animation(name)
    if not frames:
        return

    try:
        sys.stdout.write(HIDE_CURSOR + SAVE_CURSOR)
        sys.stdout.flush()

        for frame_text, duration_ms in frames:
            sys.stdout.write(RESTORE_CURSOR + CURSOR_HOME + "\033[J")
            sys.stdout.write(frame_text)
            sys.stdout.flush()
            time.sleep((duration_ms / 1000.0) / speed)

    finally:
        sys.stdout.write(RESTORE_CURSOR + CURSOR_HOME + "\033[J" + SHOW_CURSOR)
        sys.stdout.flush()


# ─── Plan Display ──────────────────────────────────────────

def display_plan(data: dict) -> None:
    """Display a generated plan using Rich formatting (cross-platform safe)."""
    plan = data.get("plan", {})
    domain = plan.get("domain", data.get("picked_domain", "?"))
    tagline = plan.get("tagline", "")
    why = plan.get("why_interesting", "")
    connections = plan.get("connections", [])
    learning_path = plan.get("learning_path", [])
    surprise = plan.get("surprise_factor", "")

    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text

        console = Console()

        # Header
        header = Text()
        header.append(f"\n[TARGET] {domain}\n", style="bold orange1")
        if tagline:
            header.append(f"{tagline}\n", style="italic red")
        console.print(Panel(header, border_style="orange1", padding=(1, 2)))

        # Why interesting
        console.print(f"\n[bold yellow][SEARCH] 为什么学这个[/bold yellow]")
        console.print(Panel(why, border_style="dim", padding=(0, 1)))

        # Connections
        if connections:
            console.print(f"\n[bold yellow][BRIDGE] 与你兴趣的意外关联[/bold yellow]")
            for conn in connections:
                console.print(f"  [cyan]->[/cyan] {conn}")

        # Learning path
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

        # Surprise factor
        if surprise:
            console.print(f"\n[bold magenta][SPARK] 意外之喜[/bold magenta]")
            console.print(Panel(
                Text(surprise, style="italic light_goldenrod1"),
                border_style="magenta",
                padding=(0, 1),
            ))

        console.print()

    except ImportError:
        _display_plan_plain(plan, domain, tagline, why, connections, learning_path, surprise)


def _display_plan_plain(plan, domain, tagline, why, connections, learning_path, surprise):
    """Plain text fallback for plan display."""
    print(f"\n{'=' * 50}")
    print(f"  [TARGET] {domain}")
    if tagline:
        print(f"  {tagline}")
    print(f"{'=' * 50}")

    print(f"\n[SEARCH] 为什么学这个")
    print(f"{why}")

    if connections:
        print(f"\n[BRIDGE] 与你兴趣的意外关联")
        for conn in connections:
            print(f"  -> {conn}")

    if learning_path:
        print(f"\n[MAP] 四周学习路径")
        for week in learning_path:
            print(f"\n  第 {week.get('week', '?')} 周：{week.get('theme', '')}")
            for act in week.get("activities", []):
                print(f"    - {act}")
            if week.get("resources"):
                print(f"    [BOOK] {'；'.join(week['resources'])}")

    if surprise:
        print(f"\n[SPARK] 意外之喜")
        print(f"  {surprise}")

    print()


# ─── Utility Functions ─────────────────────────────────────

def clear_line() -> None:
    sys.stdout.write("\033[2K\r")
    sys.stdout.flush()


def move_up(lines: int = 1) -> None:
    sys.stdout.write(f"\033[{lines}F")
    sys.stdout.flush()


def clear_screen() -> None:
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()


def print_centered(text: str, color: str = "") -> None:
    """Print centered text with optional ANSI color."""
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80
    for line in text.split("\n"):
        padded = line.center(width)
        if color:
            print(f"{color}{padded}{RESET}")
        else:
            print(padded)
