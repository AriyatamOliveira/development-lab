from __future__ import annotations
import concurrent.futures
import requests
import random
import asyncio
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from rich.panel import Panel
from colorama import Style
from core.style import info, success, error, STONE, RED, WHITE, GREEN, get_input, get_visible_len

# ── Dynamic User-Agent Rotator ────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def fetch_sites_database() -> dict:
    """Fetch Sherlock's massive data.json for a 300+ platform dictionary."""
    urls = [
        "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json",
        "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/resources/data.json"
    ]
    
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            continue
            
    # Ultimate fallback hardcoded list if offline/blocked
    return {
        "Instagram": {"url": "https://www.instagram.com/{}", "errorType": "status_code"},
        "Reddit": {"url": "https://www.reddit.com/user/{}", "errorType": "status_code"},
        "GitHub": {"url": "https://github.com/{}", "errorType": "status_code"},
        "TikTok": {"url": "https://www.tiktok.com/@{}", "errorType": "status_code"},
        "Pinterest": {"url": "https://www.pinterest.com/{}/", "errorType": "status_code"},
        "Steam": {"url": "https://steamcommunity.com/id/{}", "errorType": "message", "errorMsg": "The specified profile could not be found."},
        "Spotify": {"url": "https://open.spotify.com/user/{}", "errorType": "status_code"},
        "Twitch": {"url": "https://www.twitch.tv/{}", "errorType": "status_code"},
        "Patreon": {"url": "https://www.patreon.com/{}", "errorType": "status_code"},
        "Roblox": {"url": "https://www.roblox.com/user.aspx?username={}", "errorType": "response_url"}
    }

def _scan_site(args: tuple[str, dict, str]) -> tuple[str, str, bool]:
    """Worker function for ThreadPoolExecutor. Implements Glitch-Killer Anti-False Positives."""
    platform, site_data, username = args
    url_template = site_data.get("url", "")
    
    if "{}" in url_template:
        url = url_template.replace("{}", username)
    else:
        url = url_template.format(username)
        
    error_type = site_data.get("errorType", "")
    error_msg = site_data.get("errorMsg", "")
    
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    # ── Task 3: Direct API Hard-Coding for Gaming Platforms ──
    if platform == "Roblox":
        roblox_url = "https://users.roblox.com/v1/usernames/users"
        try:
            with requests.Session() as s:
                res = s.post(roblox_url, json={"usernames": [username], "excludeBannedUsers": True}, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("data") and len(data["data"]) > 0:
                        profile_url = f"https://www.roblox.com/users/{data['data'][0]['id']}/profile"
                        return platform, profile_url, True
            return platform, url, False
        except Exception:
            return platform, url, False

    if platform == "Minecraft":
        mc_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        try:
            with requests.Session() as s:
                res = s.get(mc_url, headers=headers, timeout=5)
                if res.status_code == 200 and res.json().get("id"):
                    return platform, mc_url, True
            return platform, url, False
        except Exception:
            return platform, url, False
            
    try:
        with requests.Session() as s:
            res = s.get(url, headers=headers, timeout=5, allow_redirects=True)
            
            is_valid = False
            
            if error_type == "status_code":
                if res.status_code == 200:
                    is_valid = True
            elif error_type == "message":
                if res.status_code == 200:
                    if error_msg and error_msg not in res.text:
                        is_valid = True
            elif error_type == "response_url":
                if res.status_code == 200:
                    # If redirected to a generic search or 404 landing page, fail
                    if res.url == url or res.url == url + "/":
                        is_valid = True
            else:
                # Fallback naive check
                if res.status_code == 200:
                    is_valid = True
                    
            if not is_valid:
                return platform, url, False
                
            # ── Glitch-Killer V5: Multi-Language "Not Found" Detection ──
            lower_text = res.text.lower()
            
            FORBIDDEN_STRINGS = [
                "parece que esta página não existe",
                "user not found",
                "profile not found",
                "page not found",
                "this account has been deleted",
                "username available",
                "not foundir para a página principal",
                "login", "sign up", "create account"
            ]
            
            lower_user = username.lower()
            for guard_word in FORBIDDEN_STRINGS:
                if guard_word in lower_text:
                    if guard_word in ["login", "sign up", "create account"]:
                        # Keyword guard
                        if lower_user not in lower_text:
                            return platform, url, False
                    else:
                        # Absolute False Positive string match
                        return platform, url, False

            # ── Glitch-Killer V5: Exact Match Canary Title Check ──
            import re
            def get_title(html: str) -> str:
                match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                return match.group(1).strip() if match else ""

            fake_username = "redwinged_void_test"
            if "{}" in url_template:
                fake_url = url_template.replace("{}", fake_username)
            else:
                fake_url = url_template.format(fake_username)
                
            canary_res = s.get(fake_url, headers=headers, timeout=5, allow_redirects=True)
            if canary_res.status_code == 200:
                canary_title = get_title(canary_res.text)
                real_title = get_title(res.text)
                if canary_title and real_title and canary_title == real_title:
                    return platform, url, False
            
            return platform, url, True
            
    except Exception:
        return platform, url, False

async def dispatch_platform_scan(username: str) -> None:
    """High-Scale Multi-Threaded OSINT Engine."""
    if not username: return
    
    info("Fetching massive platform database...")
    sites_db = await asyncio.to_thread(fetch_sites_database)
    
    # Vanguard Upgrade: Explicit Roblox and Minecraft precise API hooks
    sites_db["Roblox"] = {
        "url": "https://www.roblox.com/user.aspx?username={}",
        "errorType": "response_url"
    }
    sites_db["Minecraft"] = {
        "url": "https://api.mojang.com/users/profiles/minecraft/{}",
        "errorType": "status_code"
    }
    
    # Filter valid platforms safely
    scan_args = []
    for p, data in sites_db.items():
        if isinstance(data, dict) and "url" in data and "{}" in data["url"]:
            scan_args.append((p, data, username))
            
    total = len(scan_args)
    info(f"Loaded {total} platforms. Initiating High-Scale Engine (100 Threads)...")
    print()
    
    found_list = []
    not_found_list = []
    
    def run_engine() -> tuple[list, list]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(_scan_site, arg) for arg in scan_args]
            
            with Progress(
                SpinnerColumn(style="red"),
                TextColumn("[white]{task.description}"),
                BarColumn(complete_style="red", finished_style="green"),
                TaskProgressColumn(),
                TextColumn("[bright_black]Found:[/bright_black] [green]{task.fields[found]}[/green]"),
                console=Console(),
                transient=True,
            ) as progress:
                
                task_id = progress.add_task("Scanning Platforms...", total=total, found=0)
                
                for future in concurrent.futures.as_completed(futures):
                    platform, url, is_found = future.result()
                    if is_found:
                        found_list.append((platform, url))
                        progress.console.print(f"[green][+][/green] [white][{platform}][/white] [bright_black]{url}[/bright_black]")
                    else:
                        not_found_list.append((platform, url))
                        
                    progress.update(task_id, advance=1, found=len(found_list))
                    
        return found_list, not_found_list

    f_list, nf_list = await asyncio.to_thread(run_engine)
    
    print()
    info("Scan Complete. Generating Summary...")
    
    # ── UI Polish: Rich Panel Summary ──
    console = Console()
    summary_text = (
        f"[bright_black]Total Scanned :[/bright_black] [white]{total}[/white]\n"
        f"[bright_black]Total Found   :[/bright_black] [white]{len(f_list)}[/white]"
    )
    
    panel = Panel(
        summary_text,
        title=f"[red]OSINT SUMMARY: {username}[/red]",
        border_style="red",
        expand=False
    )
    console.print(panel)
    
    if nf_list:
        info(f"Logged {len(nf_list)} false-positives/missing profiles to temporary buffer.")

async def instagram_recon(username: str) -> None:
    """Standalone Instagram scraper pulling public metadata."""
    import aiohttp
    import re
    from rich.table import Table
    from rich.console import Console
    console = Console()
    
    info(f"Starting standalone Instagram Recon for {username}...")
    
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "x-ig-app-id": "936619743392459"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = data.get("data", {}).get("user")
                    
                    if not user:
                        error(f"Instagram profile '{username}' not found or blocked by login wall.")
                        return
                        
                    full_name = user.get("full_name", username)
                    bio = user.get("biography", "No bio provided.").replace("\n", " ")
                    followers = user.get("edge_followed_by", {}).get("count", 0)
                    following = user.get("edge_follow", {}).get("count", 0)
                    is_private = "🔒 Yes" if user.get("is_private") else "✅ No"
                    
                    table = Table(title=f"[red]Instagram Profile: {username}[/red]", style="red", title_style="bold red", border_style="red")
                    table.add_column("Field", style="red")
                    table.add_column("Data", style="white")
                    
                    table.add_row("Full Name", full_name)
                    table.add_row("Followers", f"{followers:,}")
                    table.add_row("Following", f"{following:,}")
                    table.add_row("Private", is_private)
                    table.add_row("Biography", bio[:100] + ("..." if len(bio) > 100 else ""))
                    table.add_row("URL", f"https://www.instagram.com/{username}/")
                    
                    console.print()
                    console.print(table)
                    success(f"Instagram data extracted for @{username}.")
                elif resp.status == 404:
                    error(f"Instagram profile @{username} does not exist (HTTP 404).")
                else:
                    error(f"Failed to extract metadata for @{username}. Instagram rate-limiting (HTTP {resp.status}).")
    except Exception as e:
        error(f"Error connecting to Instagram: {e}")
