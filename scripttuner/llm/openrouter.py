"""OpenRouter-aware LLM client — header-driven RPM-cap recovery.

OpenRouter free-tier models often hit per-minute caps. The OpenAI SDK's default
exponential backoff (`min(0.5 * 2^n, 8s)`) caps at 8s, which never spans the
RPM window — every retry within the same minute also fails, wasting quota
(failed requests count toward the daily limit).

This client wraps `OpenAICompatibleClient` and adds RPM-cap-aware retry:

- SDK internal retries are disabled (`max_retries=0`) so the wrapper owns all
  retry behavior — quota is spent exactly once per attempt.
- On `429`, the wrapper inspects `Retry-After` (the only header OpenRouter
  documents):
    * `Retry-After` ≤ 60s → sleep that long, retry exactly once.
    * No header → sleep 60s fallback (assumed RPM cap), retry exactly once.
    * `Retry-After` > 60s → treat as daily-cap / long throttle, raise without
      sleeping so the caller (pairs.py) skips this monologue.
- The response headers from every 429 are dumped to stderr for diagnostic
  purposes; the dump can be removed once the behavior is verified.
"""

from __future__ import annotations

import sys
import time
from typing import Any

from openai import RateLimitError

from scripttuner.llm.openai_compatible import OpenAICompatibleClient

# Hard ceiling on a single sleep. Anything larger almost certainly means a daily
# / hourly cap reset that retrying soon cannot recover from.
_MAX_SLEEP_SECONDS = 60

# Used when the 429 response carries no Retry-After header. OpenRouter's free
# models are observed not to send the standard header; a 60s window is the
# common RPM bucket size and is the safest conservative wait.
_FALLBACK_SLEEP_SECONDS = 60


def _parse_retry_after(headers: Any) -> float | None:
    """Parse the standard ``Retry-After`` header as a delta in seconds.

    Returns ``None`` if the header is absent or unparseable. We intentionally do
    not consult ``X-RateLimit-Reset`` because OpenRouter does not document its
    unit (sec vs ms vs Unix timestamp) and guessing is unsafe.
    """
    if headers is None:
        return None
    raw = headers.get("retry-after")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


class OpenRouterClient:
    """`LLMClient` Protocol impl tailored to OpenRouter free-tier behavior.

    Wraps `OpenAICompatibleClient` via composition; the inner client is created
    with ``max_retries=0`` so all retry policy lives here.
    """

    def __init__(self, *, model: str, sleep: Any = time.sleep) -> None:
        # Inner client owns the actual HTTP call; we disable its retry loop so
        # quota is consumed exactly once per attempt we explicitly make.
        self._inner = OpenAICompatibleClient(model=model, max_retries=0)
        self._sleep = sleep

    def complete(self, system: str, user: str) -> tuple[str, dict[str, Any]]:
        try:
            return self._inner.complete(system, user)
        except RateLimitError as e:
            sleep_for = self._sleep_seconds_for(e)
            if sleep_for is None:
                # Long retry-after → caller should skip; nothing to recover here.
                raise
            print(
                f"[openrouter] 429 — sleeping {sleep_for}s then retrying once",
                file=sys.stderr,
            )
            self._sleep(sleep_for)

        # Single retry. A second 429 raises and pairs.py will skip this monologue.
        return self._inner.complete(system, user)

    @staticmethod
    def _sleep_seconds_for(error: RateLimitError) -> float | None:
        """Decide how long to wait before the single retry.

        Returns ``None`` when the caller should give up immediately (daily-cap
        signature: Retry-After > 60s).
        """
        response = getattr(error, "response", None)
        headers = getattr(response, "headers", None) if response is not None else None
        retry_after = _parse_retry_after(headers)
        if retry_after is None:
            return float(_FALLBACK_SLEEP_SECONDS)
        if retry_after <= 0:
            return float(_FALLBACK_SLEEP_SECONDS)
        if retry_after > _MAX_SLEEP_SECONDS:
            return None
        return retry_after
