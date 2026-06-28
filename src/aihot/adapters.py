from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from time import struct_time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import feedparser

from aihot.models import RawEntry, SourceConfig


@dataclass(frozen=True)
class FetchError(Exception):
    source_id: str
    url: str | None
    reason: str

    def __str__(self) -> str:
        target = self.url or "<missing url>"
        return f"failed to fetch source {self.source_id} from {target}: {self.reason}"


def fetch_source_entries(
    source: SourceConfig,
    *,
    fixture_dir: Path | None = None,
    allow_network: bool = False,
) -> list[RawEntry]:
    if not source.url:
        raise FetchError(source.id, source.url, "source has no url")

    if source.url.startswith("fixture://"):
        data = _read_fixture(source, fixture_dir)
    else:
        if not allow_network:
            raise FetchError(source.id, source.url, "live network fetch disabled for MVP")
        data = _fetch_url(source)
    return parse_feed_bytes(data, source)


def parse_feed_bytes(data: bytes, source: SourceConfig) -> list[RawEntry]:
    parsed = feedparser.parse(data)
    entries: list[RawEntry] = []
    for entry in parsed.entries:
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=_text_or_none(entry.get("title")),
                url=_entry_url(entry),
                published_at=_entry_datetime(entry),
                raw_content=_entry_content(entry),
                author=_text_or_none(entry.get("author")),
                external_id=_text_or_none(entry.get("id") or entry.get("guid")),
                tags=tuple(
                    str(tag.get("term"))
                    for tag in entry.get("tags", [])
                    if isinstance(tag, dict) and tag.get("term")
                ),
            )
        )
    return entries


def _read_fixture(source: SourceConfig, fixture_dir: Path | None) -> bytes:
    if fixture_dir is None:
        raise FetchError(source.id, source.url, "fixture_dir is required for fixture urls")

    name = source.url.removeprefix("fixture://")
    if not name or Path(name).is_absolute() or ".." in Path(name).parts:
        raise FetchError(source.id, source.url, f"invalid fixture path: {name}")

    path = fixture_dir / name
    try:
        return path.read_bytes()
    except OSError as exc:
        raise FetchError(source.id, source.url, str(exc)) from exc


def _fetch_url(source: SourceConfig) -> bytes:
    request = Request(source.url, headers={"User-Agent": "aihot-ingestion/0.1"})
    try:
        with urlopen(request, timeout=source.timeout_seconds) as response:
            return response.read()
    except HTTPError as exc:
        raise FetchError(source.id, source.url, f"HTTP {exc.code}") from exc
    except URLError as exc:
        raise FetchError(source.id, source.url, str(exc.reason)) from exc
    except OSError as exc:
        raise FetchError(source.id, source.url, str(exc)) from exc


def _entry_url(entry: Any) -> str | None:
    link = entry.get("link")
    if link:
        return str(link)

    links = entry.get("links", [])
    if links:
        for candidate in links:
            if isinstance(candidate, dict) and candidate.get("href"):
                return str(candidate["href"])
    return None


def _entry_datetime(entry: Any) -> datetime | None:
    for parsed_key in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed_value = entry.get(parsed_key)
        if parsed_value:
            return _struct_time_to_utc(parsed_value)

    for text_key in ("published", "updated", "created"):
        text_value = entry.get(text_key)
        if text_value:
            parsed = _parse_datetime_text(str(text_value))
            if parsed is not None:
                return parsed
    return None


def _struct_time_to_utc(value: struct_time | tuple[int, ...]) -> datetime:
    return datetime(*value[:6], tzinfo=timezone.utc)


def _parse_datetime_text(value: str) -> datetime | None:
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _entry_content(entry: Any) -> str | None:
    content = entry.get("content")
    if content:
        first = content[0]
        if isinstance(first, dict) and first.get("value"):
            return str(first["value"])

    for key in ("summary", "description"):
        value = entry.get(key)
        if value:
            return str(value)
    return None


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
