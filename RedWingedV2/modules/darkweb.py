"""
RedWinged V2 — Dark Web Module
=================================
Educational .onion link directory.

⚠ DISCLAIMER: This module is provided for EDUCATIONAL PURPOSES ONLY.
These links are publicly documented and indexed. Accessing .onion
sites requires the Tor browser. Always follow applicable laws.
"""
from __future__ import annotations
from core.ui import (
    console, print_panel, print_separator, print_warning,
    build_menu, create_results_table,
)


# ── Categorized Directory ────────────────────────────────────────────────────
# All links are well-known, publicly documented .onion addresses.

DIRECTORY: dict[str, list[tuple[str, str]]] = {
    "🔍 Search Engines": [
        ("DuckDuckGo (Onion)", "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion"),
        ("Ahmia", "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"),
        ("Torch", "http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion"),
    ],
    "📰 News & Media": [
        ("ProPublica", "http://p53lf57qovyuvwsc6xnrppyply3vtqm7l6pcobkmyqsiofyeznfu5uqd.onion"),
        ("BBC News (Tor)", "https://www.bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion"),
        ("The New York Times", "https://www.nytimesn7cgmftshazwhfgzm37qxb44r64ytbb2dj3x62d2lljsciiyd.onion"),
    ],
    "🔒 Privacy Tools": [
        ("OnionShare", "http://lldan5gahapx5k7iafb3s4ikijc4ni7gx5iywdflkba5y2ezyber6qid.onion"),
        ("SecureDrop (List)", "https://securedrop.org/directory"),
        ("Tails OS", "http://tails.net — clearnet (Tor-friendly)"),
    ],
    "📧 Encrypted Email": [
        ("ProtonMail", "https://protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion"),
        ("Tutanota", "Clearnet with Tor support"),
    ],
    "📚 Libraries & Archives": [
        ("The Hidden Wiki", "http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion"),
        ("Sci-Hub (Mirror)", "Various .onion mirrors available"),
    ],
}


async def show_directory() -> None:
    """Display the categorized .onion link directory."""
    print_panel(
        "[rw.warning]⚠  EDUCATIONAL USE ONLY[/rw.warning]\n\n"
        "[rw.dim]This directory contains publicly documented .onion addresses.\n"
        "Accessing these sites requires the Tor Browser.\n"
        "Always comply with local laws and regulations.\n"
        "The developers of RedWinged V2 assume no liability.[/rw.dim]",
        title="🧅 DARK WEB DIRECTORY",
        border_style="yellow",
    )

    for category, links in DIRECTORY.items():
        table = create_results_table(
            category,
            [("Name", "rw.accent"), ("Address", "rw.dim")],
        )
        for name, address in links:
            table.add_row(name, address)

        console.print(table)
        console.print()

    print_warning(
        "These links may become inactive. .onion addresses change frequently."
    )
