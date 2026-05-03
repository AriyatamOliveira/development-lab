from __future__ import annotations
import aiohttp
import asyncio
from core.style import info, success, error, RED, WHITE, STONE, GREEN
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

async def dns_recon(domain: str) -> None:
    if not domain: return
    
    info(f"Performing DNS Recon for: {domain}")
    
    try:
        import dns.resolver
    except ImportError:
        error("dnspython is not installed. Please run: pip install dnspython")
        return
        
    table = Table(title=f"[red]DNS Records: {domain}[/red]", style="red", title_style="bold red", border_style="red")
    table.add_column("Type", style="red")
    table.add_column("Value", style="white")
    
    def _resolve() -> list[tuple[str, str]]:
        results = []
        for qtype in ["A", "MX", "TXT", "NS"]:
            try:
                answers = dns.resolver.resolve(domain, qtype)
                for rdata in answers:
                    results.append((qtype, str(rdata)))
            except Exception as e:
                results.append((qtype, f"[bright_black]None or Error: {type(e).__name__}[/bright_black]"))
        return results

    info(f"Querying DNS records for {domain}...")
    try:
        records = await asyncio.to_thread(_resolve)
        for qtype, val in records:
            table.add_row(qtype, val)
    except Exception as e:
        error(f"DNS query failed: {e}")
        return
                
    console.print()
    console.print(table)
    console.print()
    success("DNS Recon completed.")

async def verify_gmail(email: str) -> None:
    """
    Verify Gmail address existence via SMTP handshake.
    Uses RCPT TO probe without sending actual mail.
    """
    import smtplib
    import dns.resolver
    
    info(f"Initiating Gmail Verification for: {email}")
    
    def _smtp_check() -> tuple[bool, str]:
        domain = email.split("@")[-1]
        try:
            # Get MX records
            records = dns.resolver.resolve(domain, 'MX')
            mx_record = sorted(records, key=lambda x: x.preference)[0].exchange.to_text()
        except Exception as e:
            return False, f"DNS resolution failed: {e}"
            
        try:
            server = smtplib.SMTP(mx_record, 25, timeout=10)
            server.helo()
            server.mail("admin@example.com")
            code, message = server.rcpt(email)
            server.quit()
            
            if code == 250:
                return True, "Valid (250 OK)"
            elif code == 550:
                return False, "Invalid (550 User Not Found)"
            else:
                return False, f"Unknown response: {code} {message.decode('utf-8', 'ignore')}"
        except Exception as e:
            return False, f"SMTP Connection failed: {e}"

    info(f"Initiating SMTP handshake with Google servers for {email}...")
    try:
        is_valid, msg = await asyncio.to_thread(_smtp_check)
        if is_valid:
            success(f"Address verified: {email} - {msg}")
        else:
            error(f"Address invalid: {email} - {msg}")
    except Exception as e:
        error(f"Execution error: {e}")
