"""
RedWinged V2 — Communication Module
======================================
Gmail verification and phone OSINT tools.
"""
from __future__ import annotations
from core.ui import console, print_panel, print_info, print_warning


async def verify_gmail(email: str) -> None:
    """
    Verify Gmail address existence via SMTP handshake.
    Uses RCPT TO probe without sending actual mail.
    """
    import smtplib
    import asyncio
    import dns.resolver
    
    print_panel(f"Gmail Verification for: [rw.accent]{email}[/rw.accent]", title="📧 GMAIL VERIFIER")
    
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

    print_info(f"Initiating SMTP handshake with Google servers for {email}...")
    try:
        is_valid, msg = await asyncio.to_thread(_smtp_check)
        if is_valid:
            print_success(f"[rw.success]Address verified:[/] {email} - {msg}")
        else:
            print_error(f"[rw.error]Address invalid:[/] {email} - {msg}")
    except Exception as e:
        print_error(f"Execution error: {e}")


async def phone_osint(number: str) -> None:
    """
    Perform OSINT on a phone number.

    Args:
        number: Phone number in E.164 format.
    """
    # TODO: Phase 2 — Implement phone carrier lookup + number validation
    print_info(f"Phone OSINT for: {number}")
    print_panel(
        "Phone OSINT module is under development.\n"
        "Will implement:\n"
        "  • Carrier identification\n"
        "  • Number format validation (E.164)\n"
        "  • Line type detection (mobile/landline/VoIP)\n"
        "  • Country/region lookup",
        title="📱 PHONE OSINT — Coming Soon",
    )
