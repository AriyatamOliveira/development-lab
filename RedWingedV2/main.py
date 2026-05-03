import os
os.environ["AIOHTTP_NO_EXTENSIONS"] = "1"
import aiohttp.http_parser
aiohttp.http_parser.HttpParser.max_line_size = 131072
aiohttp.http_parser.HttpParser.max_field_size = 131072

#!/usr/bin/env python3
"""
RedWinged V2 — Main Entry Point (Vanguard Update)
===================================================
Red & Stone themed CLI interface with modular dispatch.
"""

import sys
import asyncio
from core.style import clear_screen, print_banner, print_menu_box, get_input, error, info, success

# ── Route Map (Metadata Dispatch) ─────────────────────────────────────────────

ROUTES = {
    "1": {"name": "Username Tracker        ─ Scan 100+ platforms", "module": "modules.social", "func": "dispatch_platform_scan", "prompt": "Enter Username"},
    "2": {"name": "Roblox Account Lookup   ─ UserID, RAP, Avatar", "module": "modules.gaming", "func": "dispatch_lookup", "prompt": "Enter Roblox Username", "arg2": "roblox"},
    "3": {"name": "Gmail Verifier          ─ SMTP handshake check", "module": "modules.network", "func": "verify_gmail", "prompt": "Enter Gmail Address"},
    "4": {"name": "DNS Recon               ─ A, MX, TXT, NS records", "module": "modules.network", "func": "dns_recon", "prompt": "Enter Domain"},
    "5": {"name": "Minecraft Tracker       ─ Mojang UUID & NameMC", "module": "modules.gaming", "func": "dispatch_lookup", "prompt": "Enter Minecraft Username", "arg2": "minecraft"},
    "6": {"name": "Subdomain Finder        ─ crt.sh certificate logs", "module": "modules.web", "func": "find_subdomains", "prompt": "Enter Domain"},
    "7": {"name": "Instagram Recon         ─ Public profile data", "module": "modules.social", "func": "instagram_recon", "prompt": "Enter Instagram Username"},
    "8": {"name": "Dark Web Directory      ─ Educational .onion index", "module": "modules.darkweb", "func": "show_directory", "prompt": None},
    "9": {"name": "Glitch-Killer Demo      ─ Test false-positive detection", "module": "core.validator", "func": "_demo", "prompt": None},
    "0": {"name": "Exit", "module": None, "func": None, "prompt": None},
}

# ── Main Loop ─────────────────────────────────────────────────────────────────

async def main() -> None:
    """Main application loop."""
    clear_screen()
    print_banner()
    info("RedWinged V2 initialized. Secure connections established.")

    # Generate menu layout specifically for the style box
    menu_items = {key: val["name"] for key, val in ROUTES.items()}

    while True:
        print()
        print_menu_box(menu_items)
        
        choice = get_input()
        
        if not choice:
            continue
            
        if choice == "0":
            success("Exiting RedWinged V2. Stay secure.")
            break

        if choice not in ROUTES:
            error("Invalid choice. Try again.")
            continue

        route = ROUTES[choice]
        module_name = route["module"]
        func_name = route["func"]
        prompt_text = route["prompt"]
        
        info(f"Launching module: {route['name'].split('─')[0].strip()}")
        print()
        
        target = None
        if prompt_text:
            target = get_input(prompt_text)
            if not target:
                continue
                
        # ── Safe-Call Wrapper ──
        try:
            import importlib
            try:
                mod = importlib.import_module(module_name)
            except ImportError as e:
                error(f"Module {module_name} failed to initialize: {e}")
                continue
                
            try:
                func = getattr(mod, func_name)
            except AttributeError as e:
                error(f"Function {func_name} missing in {module_name}.")
                continue
            
            # Execute dynamically based on passenger signature
            if prompt_text and "arg2" in route:
                await func(target, route["arg2"])
            elif prompt_text:
                await func(target)
            else:
                await func()
                
        except KeyboardInterrupt:
            error("\nModule interrupted by user.")
        except Exception as e:
            error(f"\nCritical Error during execution: {e}")

        print()
        from core.style import press_enter
        press_enter()
        clear_screen()
        print_banner()

if __name__ == "__main__":
    if sys.version_info[:2] < (3, 11):
        error("This tool requires Python 3.11+.")
        sys.exit(1)
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        error("Exiting RedWinged V2.")
        sys.exit(0)
