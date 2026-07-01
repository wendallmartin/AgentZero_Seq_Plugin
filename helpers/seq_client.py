from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import requests


@dataclass
class SeqQueryResult:
    items: list[dict[str, Any]]
    raw: dict[str, Any]


def _to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_seq_events(
    base_url: str,
    api_key: str,
    query: str,
    limit: int = 50,
    after: Optional[datetime] = None,
    before: Optional[datetime] = None,
    timeout: int = 30,
) -> SeqQueryResult:
    base_url = base_url.rstrip("/")

    params: dict[str, Any] = {
        "count": max(1, min(int(limit), 500)),
        "filter": query,
    }
    if after:
        params["after"] = _to_iso(after)
    if before:
        params["before"] = _to_iso(before)

    headers = {
        "X-Seq-ApiKey": api_key,
        "Accept": "application/json",
    }

    resp = requests.get(
        f"{base_url}/api/events",
        params=params,
        headers=headers,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("events") or data.get("Events") or []
    else:
        items = []
    return SeqQueryResult(items=items, raw=data)
