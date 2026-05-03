"""
RedWinged V2 — Async Request Engine
=====================================
High-performance HTTP client built on aiohttp with retry logic,
rate limiting, and User-Agent rotation.
"""
from __future__ import annotations
import asyncio
import random
import time
from typing import Optional
import aiohttp
from pydantic import BaseModel, Field


class RequestResult(BaseModel):
    """Structured result from an async HTTP request."""
    url: str
    status_code: int
    content_length: int = 0
    body_text: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    elapsed_ms: float = 0.0
    redirected: bool = False
    final_url: str = ""
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status_code == 200 and self.error is None


_USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


# ── Session Factory ───────────────────────────────────────────────────────────

def get_session(
    *,
    max_connections: int = 50,
    timeout_seconds: int = 10,
) -> aiohttp.ClientSession:
    """
    Create a pre-configured aiohttp.ClientSession with large read buffer.

    Use this when you need a raw session outside of AsyncRequestEngine,
    for example in module-specific API calls.

    Args:
        max_connections: TCP connection pool limit.
        timeout_seconds: Total request timeout.

    Returns:
        Configured ClientSession (caller must close or use as async context).
    """
    return aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=timeout_seconds),
        connector=aiohttp.TCPConnector(
            limit=max_connections,
            ssl=False,
        ),
        read_bufsize=65_536,  # 64 KB — handles oversized CSP headers
    )


# ── Async Request Engine ──────────────────────────────────────────────────────


class AsyncRequestEngine:
    """
    High-performance async HTTP client with built-in resilience.

    Features:
        - Semaphore-based concurrency control
        - Exponential backoff retry logic
        - User-Agent rotation per request
        - Configurable timeouts
        - Redirect tracking
    """

    def __init__(
        self,
        *,
        max_concurrent: int = 50,
        timeout_seconds: int = 10,
        max_retries: int = 3,
        backoff_base: float = 0.5,
    ) -> None:
        self._max_concurrent = max_concurrent
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncRequestEngine":
        self._session = aiohttp.ClientSession(
            timeout=self._timeout,
            connector=aiohttp.TCPConnector(
                limit=self._max_concurrent,
                ssl=False,
            ),
            read_bufsize=65_536,  # 64 KB — handles oversized CSP headers
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    def _random_ua(self) -> str:
        return random.choice(_USER_AGENTS)

    async def fetch(
        self,
        url: str,
        *,
        method: str = "GET",
        headers: Optional[dict[str, str]] = None,
        allow_redirects: bool = True,
    ) -> RequestResult:
        """Fetch a single URL with retry logic and rate limiting."""
        if not self._session:
            raise RuntimeError("Engine not initialized. Use async context manager.")

        req_headers = {"User-Agent": self._random_ua()}
        if headers:
            req_headers.update(headers)

        last_error: Optional[str] = None

        for attempt in range(1, self._max_retries + 1):
            async with self._semaphore:
                start = time.monotonic()
                try:
                    async with self._session.request(
                        method, url, headers=req_headers, allow_redirects=allow_redirects,
                    ) as resp:
                        body = await resp.text(errors="replace")
                        elapsed = (time.monotonic() - start) * 1000
                        return RequestResult(
                            url=url,
                            status_code=resp.status,
                            content_length=len(body.encode("utf-8")),
                            body_text=body,
                            headers={k: v for k, v in resp.headers.items()},
                            elapsed_ms=round(elapsed, 2),
                            redirected=len(resp.history) > 0,
                            final_url=str(resp.url),
                        )
                except asyncio.TimeoutError:
                    last_error = f"Timeout after {self._timeout.total}s"
                except aiohttp.ClientResponseError as e:
                    # Handle 400/403 gracefully — return result, don't crash
                    if e.status in (400, 403):
                        return RequestResult(
                            url=url,
                            status_code=e.status,
                            error=f"HTTP {e.status}: {e.message}",
                        )
                    last_error = f"{type(e).__name__}: {e}"
                except aiohttp.ClientError as e:
                    last_error = f"{type(e).__name__}: {e}"
                except Exception as e:
                    last_error = f"Unexpected: {type(e).__name__}: {e}"

            if attempt < self._max_retries:
                backoff = self._backoff_base * (2 ** (attempt - 1))
                await asyncio.sleep(backoff + random.uniform(0, backoff * 0.5))

        return RequestResult(url=url, status_code=0, error=last_error or "Unknown error")

    async def fetch_many(
        self, urls: list[str], *, method: str = "GET", headers: Optional[dict[str, str]] = None,
    ) -> list[RequestResult]:
        """Fetch multiple URLs concurrently with rate limiting."""
        tasks = [self.fetch(url, method=method, headers=headers) for url in urls]
        return await asyncio.gather(*tasks)
