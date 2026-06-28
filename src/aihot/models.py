from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class SourceConfig:
    id: str
    name: str
    source_type: str
    adapter: str
    url: str | None = None
    tier: str = "stable"
    weight: float = 1.0
    enabled: bool = True
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class RawEntry:
    source_id: str
    source_type: str
    title: str | None
    url: str | None
    published_at: datetime | None
    raw_content: str | None = None
    author: str | None = None
    external_id: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NormalizedItem:
    source_id: str
    source_type: str
    title: str
    url: str
    canonical_url: str
    raw_content: str
    published_at: datetime
    fetched_at: datetime
    content_hash: str
    title_key: str


@dataclass(frozen=True)
class SourceRun:
    source_id: str
    status: str
    fetched_at: datetime
    item_count: int
    error: str | None = None


@dataclass(frozen=True)
class Story:
    id: str
    canonical_title: str
    day: str
    summary: str
    hotness: float
    source_count: int
    item_urls: tuple[str, ...]
    selected: bool = True


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
