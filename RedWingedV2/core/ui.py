"""
RedWinged V2 — UI Module
==========================
Custom Rich themes, banners, and console helpers for the
neon-crimson terminal experience.
"""

from __future__ import annotations

import os
import shutil
import time
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

# ── Custom Theme ──────────────────────────────────────────────────────────────

REDWINGED_THEME = Theme(
    {
        "rw.title": "bold bright_red",
        "rw.subtitle": "dim red",
        "rw.accent": "bright_magenta",
        "rw.success": "bold green",
        "rw.error": "bold bright_red on black",
        "rw.warning": "bold yellow",
        "rw.info": "bold cyan",
        "rw.dim": "dim white",
        "rw.highlight": "bold bright_white on red",
        "rw.menu.number": "bold bright_red",
        "rw.menu.label": "white",
        "rw.menu.sep": "dim red",
        "rw.banner": "bright_red",
        "rw.banner.glow": "red",
    }
)

# ── Console Singleton ─────────────────────────────────────────────────────────

console = Console(theme=REDWINGED_THEME, highlight=False, force_terminal=True)

# ── Terminal Width Helper ─────────────────────────────────────────────────────


def _term_width() -> int:
    """Get the current terminal width, clamped to a sane range."""
    cols = shutil.get_terminal_size((80, 24)).columns
    return max(cols, 60)


# ── ASCII Banner ──────────────────────────────────────────────────────────────

_BANNER_ART = r"""
[rw.banner]
    ██████╗ ███████╗██████╗ ██╗    ██╗██╗███╗   ██╗ ██████╗ ███████╗██████╗ 
    ██╔══██╗██╔════╝██╔══██╗██║    ██║██║████╗  ██║██╔════╝ ██╔════╝██╔══██╗
    ██████╔╝█████╗  ██║  ██║██║ █╗ ██║██║██╔██╗ ██║██║  ███╗█████╗  ██║  ██║
    ██╔══██╗██╔══╝  ██║  ██║██║███╗██║██║██║╚██╗██║██║   ██║██╔══╝  ██║  ██║
    ██║  ██║███████╗██████╔╝╚███╔███╔╝██║██║ ╚████║╚██████╔╝███████╗██████╔╝
    ╚═╝  ╚═╝╚══════╝╚═════╝  ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═════╝ [/]
[rw.banner.glow]                       ╔═══════════════════════════════╗
                       ║[rw.accent]   ▸ V2  ·  GLITCH-KILLER ENGINE [/rw.accent]║
                       ╚═══════════════════════════════╝[/]
[rw.dim]                   ⟨ OSINT Framework  ·  Async Core  ·  Python 3.12 ⟩[/]
"""

_CREDITS_LINE = (
    "[rw.dim]─── Built with [rw.accent]♦ RedWinged[/rw.accent] "
    "| [rw.subtitle]Educational Use Only[/rw.subtitle] ───[/rw.dim]"
)


def print_banner(*, animate: bool = True) -> None:
    """Print the RedWinged V2 banner with optional glitch animation."""
    clear_screen()
    if animate:
        _glitch_animation()
    # Force console width to match the real terminal for proper centering
    console.width = _term_width()
    console.print(_BANNER_ART, justify="center")
    console.print(_CREDITS_LINE, justify="center")
    console.print()


def _glitch_animation(frames: int = 3, delay: float = 0.08) -> None:
    """Quick glitch-flicker effect before the banner lands."""
    glitch_chars = "█▓▒░╬╫╪┼"
    import random

    width = min(_term_width(), 72)
    for _ in range(frames):
        line = "".join(random.choices(glitch_chars, k=width))
        console.print(f"[rw.banner.glow]    {line}[/]", justify="center")
        time.sleep(delay)
        # Move cursor up to overwrite
        console.print("\033[1A\033[2K", end="")


# ── Helper Printers ───────────────────────────────────────────────────────────


def print_panel(
    content: str,
    *,
    title: str = "",
    style: str = "rw.accent",
    border_style: str = "bright_red",
) -> None:
    """Print a Rich panel with RedWinged styling."""
    console.print(
        Panel(
            content,
            title=f"[rw.title]{title}[/]" if title else None,
            border_style=border_style,
            style=style,
            padding=(1, 2),
        )
    )


def print_success(message: str) -> None:
    """Print a success message with ✓ prefix."""
    console.print(f"  [rw.success]✓[/] {message}")


def print_error(message: str) -> None:
    """Print an error message with ✗ prefix."""
    console.print(f"  [rw.error]✗[/] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with ⚠ prefix."""
    console.print(f"  [rw.warning]⚠[/] {message}")


def print_info(message: str) -> None:
    """Print an info message with ► prefix."""
    console.print(f"  [rw.info]►[/] {message}")


def print_separator() -> None:
    """Print a styled horizontal rule."""
    console.print("[rw.menu.sep]" + "─" * 60 + "[/]", justify="center")


# ── Menu Builder ──────────────────────────────────────────────────────────────


def build_menu(options: list[tuple[str, str]]) -> None:
    """
    Render a numbered menu from a list of (number, label) tuples.

    Args:
        options: List of (display_number, label) pairs.
    """
    console.print()
    for num, label in options:
        console.print(
            f"   [rw.menu.number]〔{num}〕[/] [rw.menu.label]{label}[/]"
        )
    console.print()


def get_menu_choice(prompt: str = "⟩ Select") -> str:
    """Prompt the user for menu input with styled prefix."""
    return console.input(f"  [rw.accent]{prompt}[/] [rw.dim]➜[/]  ")


# ── Progress Bars ─────────────────────────────────────────────────────────────


def create_progress() -> Progress:
    """Create a RedWinged-styled progress bar."""
    return Progress(
        SpinnerColumn("dots", style="rw.accent"),
        TextColumn("[rw.info]{task.description}"),
        BarColumn(bar_width=30, style="red", complete_style="bright_red"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )


# ── Results Table ─────────────────────────────────────────────────────────────


def create_results_table(
    title: str,
    columns: list[tuple[str, str]],
) -> Table:
    """
    Create a styled Rich Table for displaying results.

    Args:
        title: Table title.
        columns: List of (column_name, style) tuples.

    Returns:
        Configured Rich Table instance.
    """
    table = Table(
        title=f"[rw.title]{title}[/]",
        border_style="bright_red",
        header_style="rw.accent",
        show_lines=True,
        padding=(0, 1),
    )
    for col_name, col_style in columns:
        table.add_column(col_name, style=col_style)
    return table


# ── Utilities ─────────────────────────────────────────────────────────────────


def clear_screen() -> None:
    """Clear the terminal screen (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def status_style(exists: bool, confidence: float) -> str:
    """Return a style string based on validation result."""
    if exists and confidence >= 0.8:
        return "rw.success"
    elif exists and confidence >= 0.5:
        return "rw.warning"
    else:
        return "rw.error"
