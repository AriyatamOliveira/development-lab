from __future__ import annotations
import aiohttp
from core.ui import print_panel, print_success, print_error, create_results_table, console

async def minecraft_tracker() -> None:
    username = console.input("  [rw.accent]Enter Minecraft username[/] [rw.dim]➜[/]  ").strip()
    if not username: return
    
    print_panel(f"Tracking Minecraft player: [rw.accent]{username}[/rw.accent]", title="⛏️ MINECRAFT TRACKER")
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    uuid = data.get("id")
                    name = data.get("name", username)
                    
                    table = create_results_table(f"Minecraft: {name}", [("Field", "rw.accent"), ("Value", "white")])
                    table.add_row("Username", name)
                    table.add_row("UUID", uuid)
                    table.add_row("Skin URL", f"https://crafatar.com/skins/{uuid}")
                    table.add_row("NameMC Profile", f"https://namemc.com/profile/{name}")
                    
                    console.print()
                    console.print(table)
                    print_success("Lookup complete.")
                elif resp.status == 404:
                    print_error("Player not found on Mojang servers.")
                else:
                    print_error(f"API returned HTTP {resp.status}")
        except Exception as e:
            print_error(f"Error connecting to Mojang API: {e}")
