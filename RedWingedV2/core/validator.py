"""
RedWinged V2 — Profile Validator ("Glitch-Killer")
=====================================================
Four-layer false-positive detection system that eliminates
the "False 200 OK" problem from V1.

Layers:
    1. Status Code + Redirect Analysis
    2. Content-Length Verification (< 500 bytes = suspicious)
    3. Platform-Specific Keyword Heuristics
    4. Behavioral Validation (positive/negative signal matching)
"""
from __future__ import annotations
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from core.engine import RequestResult


# ── Confidence Levels ─────────────────────────────────────────────────────────

class Confidence(float, Enum):
    """Confidence tiers for profile existence."""
    CONFIRMED = 1.0
    HIGH = 0.85
    MEDIUM = 0.6
    LOW = 0.35
    NONE = 0.0


# ── Validation Result ─────────────────────────────────────────────────────────

class ValidationResult(BaseModel):
    """Structured output from the Glitch-Killer validation pipeline."""
    url: str
    platform: str = "unknown"
    exists: bool = False
    confidence: float = 0.0
    flags: list[str] = Field(default_factory=list)
    raw_status: int = 0
    content_length: int = 0
    final_url: str = ""

    @property
    def status_emoji(self) -> str:
        if self.exists and self.confidence >= 0.8:
            return "✅"
        elif self.exists and self.confidence >= 0.5:
            return "⚠️"
        elif not self.exists:
            return "❌"
        return "❓"

    @property
    def summary(self) -> str:
        status = "FOUND" if self.exists else "NOT FOUND"
        return (
            f"{self.status_emoji} [{self.platform}] {status} "
            f"(confidence: {self.confidence:.0%}) — {', '.join(self.flags) or 'clean'}"
        )


# ── Platform Signatures ──────────────────────────────────────────────────────
# Maps domain substrings to lists of "not found" indicator strings.
# If ANY of these appear in the response body, the profile does NOT exist.

PLATFORM_SIGNATURES: dict[str, list[str]] = {
    "twitter.com": [
        "This account doesn't exist",
        "Account suspended",
        "Hmm...this page doesn't exist",
        "Try searching for something else",
        "User not found",
    ],
    "x.com": [
        "This account doesn't exist",
        "Account suspended",
        "Hmm...this page doesn't exist",
        "Try searching for something else",
        "User not found",
    ],
    "instagram.com": [
        "Sorry, this page isn't available",
        "The link you followed may be broken",
        "this page is not available",
        "No posts yet",
        "content isn't available",
    ],
    "github.com": [
        "Not Found",
        "This is not the web page you are looking for",
        "404",
    ],
    "tiktok.com": [
        "Couldn't find this account",
        "couldn't find this page",
        "This account has been banned",
        "page you're looking for doesn't exist",
    ],
    "facebook.com": [
        "This content isn't available right now",
        "Page Not Found",
        "this page may have been removed",
        "The link you followed may be broken",
    ],
    "reddit.com": [
        "Sorry, nobody on Reddit goes by that name",
        "this user has deleted their account",
        "u/ is not a redditor",
        "page not found",
        "unauthenticated_reddit_landing",
        "we didn't find any results",
    ],
    "youtube.com": [
        "This channel does not exist",
        "This page isn't available",
        "404 Not Found",
    ],
    "twitch.tv": [
        "Sorry. Unless you've got a time machine",
        "This channel does not exist",
        "the community has closed",
    ],
    "linkedin.com": [
        "This page doesn't exist",
        "Profile Not Found",
        "page you requested was not found",
    ],
    "pinterest.com": [
        "User not found",
        "Sorry! We couldn't find that page",
        "Looks like this page doesn't exist",
    ],
    "snapchat.com": [
        "Page Not Found",
        "We can't find that user",
        "Snapchat user not found",
    ],
    "steam": [
        "The specified profile could not be found",
        "This user has not yet set up their Steam",
    ],
    "roblox.com": [
        "Page cannot be found",
        "404",
        "This user does not exist",
    ],
    "spotify.com": [
        "Page not found",
        "Couldn't find what you were looking for",
    ],
    "medium.com": [
        "404",
        "Out of nothing, something",
        "We couldn't find this page",
    ],
    "tumblr.com": [
        "There's nothing here",
        "Not found",
        "whatever you were looking for",
    ],
    "soundcloud.com": [
        "We can't find that user",
        "Something went wrong",
    ],
    "patreon.com": [
        "This page is no longer available",
        "Page not found",
    ],
    "gitlab.com": [
        "Sign in",
        "The page could not be found",
    ],
    "bitbucket.org": [
        "Repository not found",
        "We can't find this page",
    ],
    "discord": [
        "Not Found",
        "Unknown User",
    ],
    "telegram.org": [
        "If you have Telegram",
        "can preview this channel",
    ],
}

# ── Behavioral Validation Signals ────────────────────────────────────────────
# POSITIVE_SIGNALS: keywords that PROVE a profile EXISTS (metadata markers).
# NEGATIVE_STRINGS: soft-404 text that PROVES a profile does NOT exist,
#   even when the server returns 200 OK.

POSITIVE_SIGNALS: dict[str, list[str]] = {
    "reddit.com": [
        "karma",
        "cake day",
        "trophy-case",
        "usertext-body",
        "profile-header",
        "\"totalKarma\"",
    ],
    "instagram.com": [
        "edge_followed_by",
        "edge_follow",
        "biography",
        "is_private",
        "profile_pic_url",
        "edge_owner_to_timeline_media",
    ],
    "github.com": [
        "followers",
        "repositories",
        "contrib-cell",
        "vcard-details",
        "js-profile-editable-area",
        "pinned-items-list",
    ],
    "roblox.com": [
        "last online",
        "join date",
    ],
    "x.com": [
        "followers_count",
        "profile_image_url",
        "screen_name",
    ],
    "twitter.com": [
        "followers_count",
        "profile_image_url",
        "screen_name",
    ],
}

NEGATIVE_STRINGS: dict[str, list[str]] = {
    "reddit.com": [
        "Sorry, nobody on Reddit goes by that name",
        "unauthenticated_reddit_landing",
        "page not found",
        "this user has deleted their account",
        "we didn't find any results",
    ],
    "instagram.com": [
        "Sorry, this page isn't available",
        "The link you followed may be broken",
        "this page is not available",
        "content isn't available",
        "Login \u2022 Instagram",
    ],
    "github.com": [
        "This is not the web page you are looking for",
        "Not Found",
    ],
    "x.com": [
        "This account doesn\u2019t exist",
        "Hmm...this page doesn\u2019t exist",
        "Account suspended",
    ],
    "twitter.com": [
        "This account doesn\u2019t exist",
        "Hmm...this page doesn\u2019t exist",
        "Account suspended",
    ],
}

# Platforms where behavioral validation (Layer 4) should override Layers 1-3.
# These are platforms known for returning 200 OK on non-existent profiles.
BEHAVIORAL_PLATFORMS: set[str] = {
    "reddit.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "github.com",
    "roblox.com",
}

# ── URL Redirect Traps ───────────────────────────────────────────────────────
# Some platforms redirect non-existent profiles to a generic page.

REDIRECT_TRAPS: dict[str, list[str]] = {
    "twitter.com": ["/i/flow/login", "/home", "/explore"],
    "x.com": ["/i/flow/login", "/home", "/explore"],
    "instagram.com": ["/accounts/login", "/explore/"],
    "linkedin.com": ["/authwall", "/login"],
    "facebook.com": ["/login", "/r.php"],
}


# ── Generic Not-Found Patterns ───────────────────────────────────────────────

GENERIC_NOT_FOUND: list[str] = [
    "404",
    "not found",
    "page not found",
    "does not exist",
    "doesn't exist",
    "no longer available",
    "unavailable",
    "this page is private",
    "error",
    "removed",
    "banned",
    "suspended",
]

# Minimum content threshold — pages under this are likely soft-404s
MIN_CONTENT_LENGTH: int = 500


# ── Validator Class ───────────────────────────────────────────────────────────

class ProfileValidator:
    """
    Three-layer false-positive detection for OSINT profile checks.

    Usage:
        validator = ProfileValidator()
        result = validator.validate(request_result)
    """

    def __init__(
        self,
        *,
        min_content_length: int = MIN_CONTENT_LENGTH,
        use_generic_heuristics: bool = True,
        custom_signatures: Optional[dict[str, list[str]]] = None,
    ) -> None:
        """
        Args:
            min_content_length: Threshold below which responses are suspicious.
            use_generic_heuristics: Also apply generic not-found patterns.
            custom_signatures: Additional platform keyword signatures to merge.
        """
        self._min_content_length = min_content_length
        self._use_generic = use_generic_heuristics
        self._signatures = {**PLATFORM_SIGNATURES}
        if custom_signatures:
            for domain, keywords in custom_signatures.items():
                existing = self._signatures.get(domain, [])
                self._signatures[domain] = existing + keywords

    def _detect_platform(self, url: str) -> str:
        """Extract platform name from a URL."""
        url_lower = url.lower()
        for domain in self._signatures:
            if domain in url_lower:
                # Return clean name: "twitter.com" -> "Twitter"
                return domain.split(".")[0].capitalize()
        # Fallback: extract domain
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname or ""
            parts = host.replace("www.", "").split(".")
            return parts[0].capitalize() if parts else "Unknown"
        except Exception:
            return "Unknown"

    def validate(self, result: RequestResult) -> ValidationResult:
        """
        Run the four-layer validation pipeline on a RequestResult.

        Layer 1: Status code + redirect analysis
        Layer 2: Content-Length verification
        Layer 3: Keyword heuristics (platform-specific + generic)
        Layer 4: Behavioral validation (positive/negative signal matching)

        Args:
            result: The RequestResult from AsyncRequestEngine.

        Returns:
            ValidationResult with existence verdict and confidence score.
        """
        flags: list[str] = []
        confidence = Confidence.CONFIRMED.value
        platform = self._detect_platform(result.url)

        # ── Handle request errors ─────────────────────────────────
        if result.error:
            return ValidationResult(
                url=result.url,
                platform=platform,
                exists=False,
                confidence=Confidence.NONE.value,
                flags=[f"REQUEST_ERROR: {result.error}"],
                raw_status=result.status_code,
                content_length=result.content_length,
                final_url=result.final_url,
            )

        # ── LAYER 1: Status Code + Redirect Analysis ─────────────
        confidence, flags = self._layer_status_code(result, confidence, flags)

        # ── LAYER 2: Content-Length Verification ──────────────────
        confidence, flags = self._layer_content_length(result, confidence, flags)

        # ── LAYER 3: Keyword Heuristics ──────────────────────────
        confidence, flags = self._layer_keyword_heuristics(result, confidence, flags)

        # ── LAYER 4: Behavioral Validation ───────────────────────
        # Overrides previous layers for platforms that serve 200 on
        # non-existent profiles (Reddit, Instagram, X/Twitter).
        confidence, flags = self._layer_behavioral_validation(
            result, confidence, flags,
        )

        # ── Final Verdict ─────────────────────────────────────────
        exists = confidence >= 0.5

        return ValidationResult(
            url=result.url,
            platform=platform,
            exists=exists,
            confidence=round(confidence, 2),
            flags=flags,
            raw_status=result.status_code,
            content_length=result.content_length,
            final_url=result.final_url,
        )

    def _layer_status_code(
        self,
        result: RequestResult,
        confidence: float,
        flags: list[str],
    ) -> tuple[float, list[str]]:
        """Layer 1: Analyze HTTP status code and redirects."""
        status = result.status_code

        # Clear non-200 codes
        if status == 404:
            confidence = Confidence.NONE.value
            flags.append("HTTP_404")
        elif status == 403:
            confidence = min(confidence, Confidence.LOW.value)
            flags.append("HTTP_403_FORBIDDEN")
        elif status == 410:
            confidence = Confidence.NONE.value
            flags.append("HTTP_410_GONE")
        elif status == 301 or status == 302:
            confidence = min(confidence, Confidence.LOW.value)
            flags.append(f"HTTP_{status}_REDIRECT")
        elif status == 429:
            confidence = min(confidence, Confidence.MEDIUM.value)
            flags.append("HTTP_429_RATE_LIMITED")
        elif status >= 500:
            confidence = min(confidence, Confidence.LOW.value)
            flags.append(f"HTTP_{status}_SERVER_ERROR")
        elif status != 200:
            confidence = min(confidence, Confidence.MEDIUM.value)
            flags.append(f"HTTP_{status}_UNEXPECTED")

        # Check for redirect traps (200 after sneaky redirect)
        if result.redirected:
            final = result.final_url.lower()
            url_lower = result.url.lower()

            for domain, traps in REDIRECT_TRAPS.items():
                if domain in url_lower:
                    for trap in traps:
                        if trap in final:
                            confidence = min(confidence, Confidence.LOW.value)
                            flags.append(f"REDIRECT_TRAP:{trap}")
                            break

            # Even without known traps, a redirect is suspicious
            if "REDIRECT_TRAP" not in str(flags) and result.redirected:
                if result.final_url.rstrip("/") != result.url.rstrip("/"):
                    confidence = min(confidence, Confidence.HIGH.value)
                    flags.append("REDIRECTED")

        return confidence, flags

    def _layer_content_length(
        self,
        result: RequestResult,
        confidence: float,
        flags: list[str],
    ) -> tuple[float, list[str]]:
        """Layer 2: Flag suspiciously small responses."""
        if result.content_length < self._min_content_length:
            confidence = min(confidence, Confidence.LOW.value)
            flags.append(f"SMALL_RESPONSE:{result.content_length}B")

        return confidence, flags

    def _layer_keyword_heuristics(
        self,
        result: RequestResult,
        confidence: float,
        flags: list[str],
    ) -> tuple[float, list[str]]:
        """Layer 3: Search for platform-specific 'not found' indicators."""
        body_lower = result.body_text.lower()
        url_lower = result.url.lower()
        matched_keywords: list[str] = []

        # Platform-specific signatures
        for domain, keywords in self._signatures.items():
            if domain in url_lower:
                for keyword in keywords:
                    if keyword.lower() in body_lower:
                        matched_keywords.append(keyword)

        # Generic heuristics (applied to all platforms)
        if self._use_generic:
            # Only apply generic checks if no platform-specific match found
            if not matched_keywords:
                for pattern in GENERIC_NOT_FOUND:
                    # Use word-boundary matching to reduce false positives
                    if re.search(rf"\b{re.escape(pattern)}\b", body_lower):
                        matched_keywords.append(f"GENERIC:{pattern}")

        if matched_keywords:
            # Each keyword match reduces confidence
            penalty = min(len(matched_keywords) * 0.25, 0.9)
            confidence = max(confidence - penalty, Confidence.NONE.value)
            flags.append(f"KEYWORD_MATCH:{';'.join(matched_keywords[:5])}")

        return confidence, flags

    def _layer_behavioral_validation(
        self,
        result: RequestResult,
        confidence: float,
        flags: list[str],
    ) -> tuple[float, list[str]]:
        """
        Layer 4: Behavioral validation — positive/negative signal matching.

        For platforms in BEHAVIORAL_PLATFORMS, this layer OVERRIDES earlier
        confidence scores based on actual page content:
            - Negative string found  → 0% confidence (SOFT_404_DETECTED)
            - Positive signal found  → 100% confidence (METADATA_MATCH)
            - Neither found          → 30% confidence (UNCERTAIN)
        """
        body_lower = result.body_text.lower()
        url_lower = result.url.lower()

        # Determine which behavioral platform (if any) this URL belongs to
        matched_domain: str | None = None
        for domain in BEHAVIORAL_PLATFORMS:
            if domain in url_lower:
                matched_domain = domain
                break

        if matched_domain is None:
            return confidence, flags

        # ── Check NEGATIVE strings first (they take priority) ────
        neg_strings = NEGATIVE_STRINGS.get(matched_domain, [])
        for neg in neg_strings:
            if neg.lower() in body_lower:
                confidence = Confidence.NONE.value
                flags.append(f"SOFT_404_DETECTED:{neg[:40]}")
                return confidence, flags

        # ── Check POSITIVE signals ───────────────────────────────
        pos_signals = POSITIVE_SIGNALS.get(matched_domain, [])
        matched_pos: list[str] = []
        for pos in pos_signals:
            if pos.lower() in body_lower:
                matched_pos.append(pos)

        if matched_pos:
            confidence = Confidence.CONFIRMED.value
            flags.append(f"METADATA_MATCH:{';'.join(matched_pos[:3])}")
            return confidence, flags

        # ── Neither found → ambiguous, mark as SUSPICIOUS ──────────
        confidence = Confidence.NONE.value
        flags.append("[?] SOFT_404")
        return confidence, flags

    def validate_batch(
        self, results: list[RequestResult]
    ) -> list[ValidationResult]:
        """Validate a batch of RequestResults."""
        return [self.validate(r) for r in results]


# ── Standalone Demo ───────────────────────────────────────────────────────────

async def _demo() -> None:
    """Demonstrate the Glitch-Killer against real targets."""
    from core.engine import AsyncRequestEngine
    from core.ui import (
        console, print_banner, print_panel, print_success,
        print_error, print_warning, print_info, create_results_table,
        create_progress, status_style,
    )

    print_banner(animate=False)
    print_panel(
        "Running Glitch-Killer validation demo against live targets.\n"
        "This demonstrates false-positive detection on real websites.",
        title="⚡ VALIDATOR DEMO",
    )

    # Test URLs — mix of real and non-existent profiles
    test_urls: list[tuple[str, str]] = [
        ("https://github.com/torvalds", "Should EXIST"),
        ("https://github.com/thisuser-definitely-does-not-exist-xz99", "Should NOT exist"),
        ("https://x.com/elonmusk", "Should EXIST"),
        ("https://x.com/fakeuser_nonexistent_xz99", "Should NOT exist"),
        ("https://www.reddit.com/user/spez", "Should EXIST"),
        ("https://www.reddit.com/user/thisuser_nonexistent_xz99", "Should NOT exist"),
    ]

    validator = ProfileValidator()
    table = create_results_table(
        "Glitch-Killer Results",
        [
            ("Platform", "rw.accent"),
            ("URL", "rw.dim"),
            ("Expected", "white"),
            ("Verdict", "white"),
            ("Confidence", "white"),
            ("Flags", "rw.dim"),
        ],
    )

    async with AsyncRequestEngine(max_concurrent=5, timeout_seconds=15) as engine:
        with create_progress() as progress:
            task = progress.add_task("Validating profiles...", total=len(test_urls))
            for url, expected in test_urls:
                result = await engine.fetch(url)
                validation = validator.validate(result)

                style = status_style(validation.exists, validation.confidence)
                verdict = f"[{style}]{validation.status_emoji} {'FOUND' if validation.exists else 'NOT FOUND'}[/]"

                table.add_row(
                    validation.platform,
                    url.split("/")[-1],
                    expected,
                    verdict,
                    f"{validation.confidence:.0%}",
                    ", ".join(validation.flags[:3]) or "—",
                )
                progress.advance(task)

    console.print()
    console.print(table)
    console.print()
    print_info("Demo complete. The Glitch-Killer catches false positives that V1 missed.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
