import sys
import time
import os
from colorama import Fore, Style, init

# Initialize colorama with strip for non-TTY
init(autoreset=True, strip=not sys.stdout.isatty())

# Red & Stone Theme
RED = Fore.RED
STONE = Fore.LIGHTBLACK_EX
WHITE = Fore.WHITE
CYAN = Fore.CYAN
GREEN = Fore.GREEN

import re

ANSI_ESCAPE = re.compile(r'(?:\x1B[@-Z\\-_]|[\x80-\x9F]|\x1B\[[0-?]*[ -/]*[@-~])')

def get_visible_len(text: str) -> int:
    """Strips ANSI codes to calculate actual visual length."""
    return len(ANSI_ESCAPE.sub('', text))

def clear_screen():
    """Clear the terminal screen on macOS."""
    os.system('clear' if os.name == 'posix' else 'cls')

def typewriter_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_banner():
    """Display visually aggressive RedTiger style banner restricted to 84 chars."""
    banner = f"""
{RED}╔══════════════════════════════════════════════════════════════════════════════════╗
{RED}║  {WHITE}__________           {STONE}._____      __.__                          .___{RED}            ║
{RED}║  {WHITE}\______   \ ____   __{STONE}| _/  \    /  \__| ____    ____   ____   __| _/{RED}            ║
{RED}║  {WHITE} |       _// __ \ / __{STONE} |\   \/\/   /  |/    \  / ___\_/ __ \ / __ |{RED}             ║
{RED}║  {WHITE} |    |   \  ___// /_{STONE}/ | \        /|  |   |  \/ /_/  >  ___// /_/ |{RED}             ║
{RED}║  {WHITE} |____|_  /\___  >____{STONE} |  \__/\  / |__|___|  /\___  / \___  >____ |{RED}             ║
{RED}║  {WHITE}       \/     \/     {STONE}\/       \/          \//_____/      \/     \/|{RED}             ║
{RED}╚══════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_menu_box(menu_items: dict[str, str]):
    """Print the menu options using box drawing characters with perfect alignment."""
    print(f"{RED}╔═══ {WHITE}MODULE SELECTION {RED}═════════════════════════════════════════════════════════════╗")
    for key, desc in menu_items.items():
        line = f"║  {RED}[{WHITE}{key:>2}{RED}] {STONE}─ {WHITE}{desc}"
        # Total fixed width is 84. Left border = 1. Pad = 84 - visible_len - 1 (right border)
        pad = max(0, 84 - get_visible_len(line) - 1)
        print(f"{RED}║  [{WHITE}{key:>2}{RED}] {STONE}─ {WHITE}{desc}" + " " * pad + f"{RED}║")
    print(f"{RED}╚══════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def success(msg):
    print(f"{GREEN}[+] {WHITE}{msg}{Style.RESET_ALL}")

def error(msg):
    print(f"{RED}[-] {WHITE}{msg}{Style.RESET_ALL}")

def info(msg):
    print(f"{CYAN}[*] {WHITE}{msg}{Style.RESET_ALL}")

def get_input(prompt: str = "") -> str:
    """Aggressive RedWinged input style."""
    if prompt:
        return input(f"{RED}RedWinged {STONE}~# {WHITE}{prompt}: {Style.RESET_ALL}").strip()
    return input(f"{RED}RedWinged {STONE}~# {Style.RESET_ALL}").strip()

def press_enter() -> None:
    """Helper function to pause execution until the user presses Enter."""
    input(f"{RED}RedWinged {STONE}~# {WHITE}Press Enter to return to menu...{Style.RESET_ALL}")
