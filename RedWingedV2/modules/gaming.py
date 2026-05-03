"""
RedWinged V2 — Gaming & Social Module
=========================================
Professional-grade async lookups for gaming/social platforms.

Features:
    - Roblox: Username → UserID, RAP, Join Date, Limiteds count
    - Discord: Invite code validation (active / expired / invalid)
    - Glitch-Killer integration for profile verification
    - Jittered delays (0.5–1.2s) for anti-detection
    - 2026 Safari macOS User-Agent mimicry
"""
from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime
from typing import Optional

import aiohttp
from pydantic import BaseModel, Field

from core.engine import AsyncRequestEngine, RequestResult, get_session
from core.validator import ProfileValidator
from core.ui import (
    console,
    print_panel,
    print_info,
    print_success,
    print_error,
    print_warning,
    create_results_table,
    create_progress,
)


# ── Anti-Detection Headers ───────────────────────────────────────────────────
# Mimics a 2026 Safari build on macOS Sequoia to avoid naked-request flagging.

_SAFARI_2026_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/619.2.17.10.7 "
        "(KHTML, like Gecko) Version/19.0 Safari/619.2.17.10.7"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "application/json;q=0.8,*/*;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

_UA_POOL: list[str] = [
    # Safari 19.x — macOS Sequoia (2026)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/619.2.17.10.7 "
    "(KHTML, like Gecko) Version/19.0 Safari/619.2.17.10.7",
    # Safari 18.x — macOS Sonoma
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/618.3.11 "
    "(KHTML, like Gecko) Version/18.4 Safari/618.3.11",
    # Chrome 126 — macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    # Chrome 125 — macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Safari 17.x — macOS Ventura
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


def _random_headers() -> dict[str, str]:
    """Build request headers with a randomized User-Agent from the pool."""
    headers = dict(_SAFARI_2026_HEADERS)
    headers["User-Agent"] = random.choice(_UA_POOL)
    return headers


async def _jittered_delay(low: float = 0.5, high: float = 1.2) -> None:
    """Sleep for a random duration to avoid rate-limiting / fingerprinting."""
    await asyncio.sleep(random.uniform(low, high))


# ── Data Models ──────────────────────────────────────────────────────────────


class RobloxProfile(BaseModel):
    """Structured Roblox user profile data."""
    user_id: int
    username: str
    display_name: str = ""
    description: str = ""
    created: str = ""
    is_banned: bool = False
    avatar_url: str = ""
    rap: int = 0
    limiteds_count: int = 0


class DiscordInviteResult(BaseModel):
    """Structured Discord invite validation result."""
    code: str
    is_valid: bool = False
    guild_name: str = ""
    guild_id: str = ""
    member_count: int = 0
    channel_name: str = ""
    expires_at: Optional[str] = None
    error: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
#  ROBLOX LOOKUP
# ══════════════════════════════════════════════════════════════════════════════


class RobloxLookup:
    """
    Async Roblox account lookup engine.

    Pipeline:
        1. Validate profile via Glitch-Killer (web page check)
        2. Resolve Username → UserID via search API
        3. Fetch detailed profile (join date, ban status, bio)
        4. Fetch avatar headshot URL
        5. Fetch RAP + Limiteds count from inventory API
    """

    _TIMEOUT = aiohttp.ClientTimeout(total=10)

    def __init__(self, username: str) -> None:
        self.username = username
        self._session: Optional[aiohttp.ClientSession] = None
        self._validator = ProfileValidator()

    async def __aenter__(self) -> "RobloxLookup":
        self._session = aiohttp.ClientSession(
            timeout=self._TIMEOUT,
            connector=aiohttp.TCPConnector(limit=5, ssl=False),
            read_bufsize=65_536,
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    # ── Private API helpers ──────────────────────────────────────────────────

    async def _api_get(self, url: str, *, label: str = "API") -> Optional[dict]:
        """Perform a GET request with randomized headers and error handling."""
        assert self._session is not None
        headers = _random_headers()
        headers["Accept"] = "application/json"
        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status == 429:
                    print_warning(f"{label}: Rate-limited (429). Backing off...")
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                    return None
                if resp.status != 200:
                    return None
                return await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError):
            return None

    async def resolve_user_id(self) -> Optional[dict]:
        """Resolve username to user ID via the precise Roblox users POST API."""
        url = "https://users.roblox.com/v1/usernames/users"
        assert self._session is not None
        
        headers = _random_headers()
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        payload = {"usernames": [self.username], "excludeBannedUsers": True}
        
        try:
            async with self._session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 429:
                    print_warning("UserSearch: Rate-limited (429). Backing off...")
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                    return None
                if resp.status != 200:
                    return None
                    
                data = await resp.json(content_type=None)
                users = data.get("data", [])
                if users:
                    return users[0]
        except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError):
            pass
            
        return None

    async def fetch_profile(self, user_id: int) -> Optional[dict]:
        """Fetch detailed profile data for a given user ID."""
        url = f"https://users.roblox.com/v1/users/{user_id}"
        return await self._api_get(url, label="Profile")

    async def fetch_avatar(self, user_id: int) -> str:
        """Fetch the avatar headshot URL for a given user ID."""
        url = (
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
            f"?userIds={user_id}&size=150x150&format=Png&isCircular=false"
        )
        data = await self._api_get(url, label="Avatar")
        if data:
            entries = data.get("data", [])
            if entries:
                return entries[0].get("imageUrl", "")
        return ""

    async def fetch_rap_and_limiteds(self, user_id: int) -> tuple[int, int]:
        """
        Scan the user's collectible inventory for RAP and Limiteds count.

        Paginates through inventory.roblox.com with jittered delays.
        Returns (total_rap, limiteds_count) or (-1, -1) if inventory is private.
        """
        total_rap = 0
        limiteds_count = 0
        cursor: Optional[str] = ""

        base_url = (
            f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles"
            f"?assetType=All&limit=100"
        )

        max_pages = 5
        page = 0

        while cursor is not None and page < max_pages:
            url = base_url
            if cursor:
                url += f"&cursor={cursor}"

            await _jittered_delay(0.5, 1.0)
            
            headers = _random_headers()
            headers["Accept"] = "application/json"
            
            assert self._session is not None
            try:
                async with self._session.get(url, headers=headers) as resp:
                    if resp.status == 403:
                        return -1, -1  # Indicate private inventory
                    if resp.status == 429:
                        print_warning("Inventory: Rate-limited (429). Backing off...")
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        continue
                    if resp.status != 200:
                        break
                    data = await resp.json(content_type=None)
            except Exception:
                break

            items = data.get("data", [])
            for item in items:
                rap_value = item.get("recentAveragePrice", 0) or 0
                total_rap += rap_value
                limiteds_count += 1

            cursor = data.get("nextPageCursor")
            page += 1

        return total_rap, limiteds_count

    async def validate_profile(self) -> bool:
        """
        Use the Glitch-Killer validator to verify the Roblox profile
        actually exists (not a soft-404 / phantom page).
        """
        assert self._session is not None
        profile_url = (
            f"https://www.roblox.com/users/profile?username={self.username}"
        )
        headers = _random_headers()

        try:
            async with self._session.get(
                profile_url, headers=headers, allow_redirects=True,
            ) as resp:
                body = await resp.text(errors="replace")

                result = RequestResult(
                    url=profile_url,
                    status_code=resp.status,
                    content_length=len(body.encode("utf-8")),
                    body_text=body,
                    headers={k: v for k, v in resp.headers.items()},
                    elapsed_ms=0.0,
                    redirected=len(resp.history) > 0,
                    final_url=str(resp.url),
                )

                validation = self._validator.validate(result)

                if not validation.exists:
                    print_warning(
                        f"Glitch-Killer flagged profile as suspicious: "
                        f"{', '.join(validation.flags[:3])}"
                    )
                return validation.exists

        except (aiohttp.ClientError, asyncio.TimeoutError):
            return True  # Don't block if web check fails


# ══════════════════════════════════════════════════════════════════════════════
#  DISCORD INVITE VALIDATOR
# ══════════════════════════════════════════════════════════════════════════════


class DiscordInviteValidator:
    """
    Validates Discord invite codes against the public Discord API.

    Checks if an invite is active, expired, or invalid without joining.
    Uses the public endpoint: discord.com/api/v10/invites/{code}
    """

    _TIMEOUT = aiohttp.ClientTimeout(total=10)
    _API_BASE = "https://discord.com/api/v10/invites"

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "DiscordInviteValidator":
        self._session = aiohttp.ClientSession(
            timeout=self._TIMEOUT,
            connector=aiohttp.TCPConnector(limit=3, ssl=False),
            read_bufsize=65_536,
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def validate(self, invite_code: str) -> DiscordInviteResult:
        """
        Check a single Discord invite code.

        Args:
            invite_code: The invite code (e.g. 'abc123' from discord.gg/abc123).

        Returns:
            DiscordInviteResult with guild info if valid.
        """
        assert self._session is not None

        # Strip full URL if user pasted one
        code = invite_code.strip()
        for prefix in ("https://discord.gg/", "https://discord.com/invite/",
                        "discord.gg/", "discord.com/invite/"):
            if code.lower().startswith(prefix):
                code = code[len(prefix):]
                break

        url = f"{self._API_BASE}/{code}?with_counts=true"
        headers = _random_headers()
        headers["Accept"] = "application/json"

        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status == 404:
                    return DiscordInviteResult(
                        code=code,
                        is_valid=False,
                        error="Invite not found or expired.",
                    )
                if resp.status == 429:
                    return DiscordInviteResult(
                        code=code,
                        is_valid=False,
                        error="Rate-limited by Discord. Try again later.",
                    )
                if resp.status != 200:
                    return DiscordInviteResult(
                        code=code,
                        is_valid=False,
                        error=f"Unexpected HTTP {resp.status}.",
                    )

                data = await resp.json(content_type=None)
                guild = data.get("guild", {})
                channel = data.get("channel", {})

                return DiscordInviteResult(
                    code=code,
                    is_valid=True,
                    guild_name=guild.get("name", "Unknown"),
                    guild_id=str(guild.get("id", "")),
                    member_count=data.get("approximate_member_count", 0),
                    channel_name=channel.get("name", "Unknown"),
                    expires_at=data.get("expires_at"),
                )

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return DiscordInviteResult(
                code=code,
                is_valid=False,
                error=f"Connection error: {type(e).__name__}",
            )


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC ENTRY POINTS (called from main.py dispatchers)
# ══════════════════════════════════════════════════════════════════════════════


async def lookup_roblox(username: str) -> None:
    """
    Full Roblox account lookup: UserID, RAP, Join Date, Limiteds.

    Orchestrates the RobloxLookup class and renders a Rich table.
    """
    print_panel(
        f"Looking up Roblox user: [rw.accent]{username}[/rw.accent]\n"
        f"[rw.dim]Using jittered delays for anti-ban protection...[/rw.dim]",
        title="🎮 ROBLOX LOOKUP",
    )

    async with RobloxLookup(username) as rblx:

        # Step 1: Glitch-Killer web validation
        print_info("Running Glitch-Killer profile validation...")
        profile_valid = await rblx.validate_profile()
        await _jittered_delay()

        if not profile_valid:
            print_error(
                f"Profile for '{username}' failed Glitch-Killer validation.\n"
                f"  The profile may not exist or may be a soft-404."
            )

        # Step 2: Resolve username → user ID
        print_info("Resolving username via Roblox API...")
        user_match = await rblx.resolve_user_id()
        await _jittered_delay()

        if not user_match:
            print_error(f"No Roblox user found matching '{username}'.")
            return

        user_id: int = user_match["id"]
        matched_name: str = user_match.get("name", username)

        if matched_name.lower() != username.lower():
            print_warning(
                f"Exact match not found. Closest: '{matched_name}' (ID: {user_id})"
            )

        # Step 3: Fetch detailed profile
        print_info("Fetching profile details...")
        profile_data = await rblx.fetch_profile(user_id) or {}
        await _jittered_delay()

        # Step 4: Fetch avatar
        print_info("Fetching avatar headshot...")
        avatar_url = await rblx.fetch_avatar(user_id)
        await _jittered_delay()

        # Step 5: Fetch RAP + Limiteds
        print_info("Scanning inventory for RAP & Limiteds...")
        rap, limiteds_count = await rblx.fetch_rap_and_limiteds(user_id)

        # Step 6: Format join date
        created_raw = profile_data.get("created", "")
        join_date = "N/A"
        if created_raw:
            try:
                dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                join_date = dt.strftime("%B %d, %Y")
            except (ValueError, TypeError):
                join_date = created_raw[:10]

        # Step 7: Display results
        table = create_results_table(
            f"Roblox Profile: {matched_name}",
            [("Field", "rw.accent"), ("Value", "white")],
        )

        table.add_row("User ID", str(user_id))
        table.add_row("Username", profile_data.get("name", matched_name))
        table.add_row("Display Name", profile_data.get("displayName", "N/A"))
        table.add_row("Join Date", join_date)
        table.add_row(
            "Description",
            (profile_data.get("description", "") or "—")[:200],
        )
        table.add_row(
            "Banned",
            "⛔ Yes" if profile_data.get("isBanned") else "✅ No",
        )
        
        if rap == -1:
            table.add_row("RAP (Robux)", "[rw.warning]🔒 Inventory Hidden/Private[/]")
            table.add_row("Limiteds Count", "[rw.warning]🔒 Hidden[/]")
        else:
            table.add_row("RAP (Robux)", f"R$ {rap:,}" if rap else "R$ 0")
            table.add_row("Limiteds Count", str(limiteds_count))
            
        table.add_row("Avatar", avatar_url or "N/A")
        table.add_row(
            "Profile URL",
            f"https://www.roblox.com/users/{user_id}/profile",
        )
        table.add_row(
            "Glitch-Killer",
            "[rw.success]✅ Verified[/]" if profile_valid
            else "[rw.warning]⚠ Flagged[/]",
        )

        console.print()
        console.print(table)
        console.print()
        print_success(f"Lookup complete for '{username}'.")


async def validate_discord_invite(invite_code: str) -> None:
    """
    Validate a Discord invite code and display results.

    Orchestrates the DiscordInviteValidator class and renders a Rich table.
    """
    print_panel(
        f"Validating Discord invite: [rw.accent]{invite_code}[/rw.accent]",
        title="💬 DISCORD INVITE CHECK",
    )

    async with DiscordInviteValidator() as validator:
        await _jittered_delay(0.3, 0.8)
        result = await validator.validate(invite_code)

    if result.is_valid:
        table = create_results_table(
            f"Discord Invite: {result.code}",
            [("Field", "rw.accent"), ("Value", "white")],
        )
        table.add_row("Status", "[rw.success]✅ Active[/]")
        table.add_row("Server", result.guild_name)
        table.add_row("Server ID", result.guild_id)
        table.add_row("Channel", f"#{result.channel_name}")
        table.add_row("Members", f"{result.member_count:,}")
        table.add_row(
            "Expires",
            result.expires_at[:19] if result.expires_at else "Never",
        )

        console.print()
        console.print(table)
        console.print()
        print_success(f"Invite '{result.code}' is active.")
        console.print()
        print_error(f"Invite '{result.code}': {result.error}")
        console.print()

async def lookup_minecraft(username: str) -> None:
    """
    Minecraft account lookup via Mojang API.
    """
    import aiohttp
    print_panel(
        f"Looking up Minecraft user: [rw.accent]{username}[/rw.accent]",
        title="⛏️ MINECRAFT LOOKUP",
    )
    
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    headers = _random_headers()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    uuid = data.get("id")
                    actual_name = data.get("name")
                    
                    if uuid:
                        table = create_results_table(
                            f"Minecraft Profile: {actual_name}",
                            [("Field", "rw.accent"), ("Value", "white")],
                        )
                        table.add_row("Username", actual_name)
                        table.add_row("UUID", uuid)
                        table.add_row("Skin / Cape", f"https://crafatar.com/renders/body/{uuid}")
                        table.add_row("NameMC URL", f"https://namemc.com/profile/{actual_name}")
                        
                        console.print()
                        console.print(table)
                        console.print()
                        print_success(f"Lookup complete for '{username}'.")
                        return
                        
        print_error(f"No Minecraft profile found for '{username}'.")
    except Exception as e:
        print_error(f"Failed to lookup Minecraft profile: {e}")

async def dispatch_lookup(username: str, mode: str) -> None:
    """
    Primary Router for Gaming modules (Roblox & Minecraft).
    """
    if mode == "roblox":
        await lookup_roblox(username)
    elif mode == "minecraft":
        await lookup_minecraft(username)
    else:
        print_error(f"Unknown gaming lookup mode: {mode}")
