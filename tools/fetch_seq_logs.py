from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from helpers.plugins import get_plugin_config
from helpers.tool import Response, Tool

from usr.plugins.seq_logs.helpers.seq_client import fetch_seq_events


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _coerce_int(value: Any, default: int = 50, minimum: int = 1, maximum: int = 500) -> int:
    try:
        number = int(value)
    except Exception:
        number = default
    return max(minimum, min(number, maximum))


def fetch_logs(
    agent=None,
    query: str = "*",
    limit: int = 50,
    after: Optional[str] = None,
    before: Optional[str] = None,
    seq_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Fetch logs from Seq using explicit args or saved plugin config."""
    config = get_plugin_config("seq_logs", agent=agent) or {}

    url = (seq_url or config.get("seq_url") or config.get("url") or "").strip()
    key = (api_key or config.get("api_key") or config.get("key") or "").strip()

    if not url:
        return {"ok": False, "error": "Missing Seq URL. Set seq_url in plugin settings or pass seq_url."}
    if not key:
        return {"ok": False, "error": "Missing Seq API key. Set api_key in plugin settings or pass api_key."}

    after_dt = _parse_dt(after)
    before_dt = _parse_dt(before)

    if after_dt is None and config.get("lookback_minutes"):
        try:
            mins = int(config.get("lookback_minutes"))
            after_dt = datetime.now(timezone.utc) - timedelta(minutes=mins)
        except Exception:
            after_dt = None

    try:
        result = fetch_seq_events(
            base_url=url,
            api_key=key,
            query=query or "*",
            limit=_coerce_int(limit),
            after=after_dt,
            before=before_dt,
        )
        return {
            "ok": True,
            "count": len(result.items),
            "events": result.items,
            "raw": result.raw,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Backward-compatible direct entry point for smoke tests.
def run(
    agent=None,
    context=None,
    query: str = "*",
    limit: int = 50,
    after: Optional[str] = None,
    before: Optional[str] = None,
    seq_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    return fetch_logs(
        agent=agent,
        query=query,
        limit=limit,
        after=after,
        before=before,
        seq_url=seq_url,
        api_key=api_key,
    )


class FetchSeqLogs(Tool):
    async def execute(self, **kwargs: Any) -> Response:
        result = fetch_logs(
            agent=self.agent,
            query=str(self.args.get("query") or "*"),
            limit=self.args.get("limit") or 50,
            after=self.args.get("after"),
            before=self.args.get("before"),
            seq_url=self.args.get("seq_url"),
            api_key=self.args.get("api_key"),
        )
        return Response(
            message=json.dumps(result, indent=2, default=str),
            break_loop=False,
        )
