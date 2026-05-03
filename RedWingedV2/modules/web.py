from __future__ import annotations
import aiohttp
from core.style import info, success, error, RED, WHITE, STONE, GREEN
from rich.console import Console
from rich.table import Table

console = Console()

async def find_subdomains(domain: str) -> None:
    if not domain: return
    
    info(f"Finding Subdomains via crt.sh for: {domain}")
    
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    info("Querying crt.sh certificate transparency logs (this may take a moment)...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    subdomains = set()
                    for entry in data:
                        name = entry.get("name_value", "")
                        if name and not name.startswith("*"):
                            for sub in name.split("\n"):
                                if sub.endswith(domain):
                                    subdomains.add(sub)
                    
                    if subdomains:
                        table = Table(title=f"[red]Subdomains: {domain}[/red]", style="red", title_style="bold red", border_style="red")
                        table.add_column("Subdomain", style="white")
                        
                        for sub in sorted(subdomains):
                            table.add_row(sub)
                            
                        console.print()
                        console.print(table)
                        success(f"Found {len(subdomains)} unique subdomains.")
                    else:
                        error("No subdomains found.")
                else:
                    error(f"crt.sh returned HTTP {resp.status}")
        except Exception as e:
            error(f"Error querying crt.sh: {e}")
