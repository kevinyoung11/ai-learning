from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from time import struct_time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

import feedparser

from aihot.models import RawEntry, SourceConfig

MAX_ENTRIES_PER_FETCH = 50


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
        return _limit_entries(parse_feed_bytes(data, source))

    if not allow_network:
        raise FetchError(source.id, source.url, "live network fetch disabled")

    if source.adapter in {"rss", "atom", "github_releases"}:
        return _limit_entries(parse_feed_bytes(_fetch_url(source), source))
    if source.adapter == "github_org_repos":
        return _limit_entries(parse_github_org_repos(_fetch_json(source), source))
    if source.adapter == "huggingface_models":
        return _limit_entries(parse_huggingface_models(_fetch_json(source), source))
    if source.adapter == "hn_algolia":
        return _limit_entries(parse_hn_algolia(_fetch_json(source), source))
    if source.adapter == "html_links":
        return _limit_entries(parse_html_links(_fetch_url(source), source))

    raise FetchError(source.id, source.url, f"unsupported adapter: {source.adapter}")


def parse_feed_bytes(data: bytes, source: SourceConfig) -> list[RawEntry]:
    parsed = feedparser.parse(data)
    if not parsed.entries:
        reason = parsed.get("bozo_exception") or "feed contained no entries"
        raise FetchError(source.id, source.url, f"malformed feed: {reason}")
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


def parse_github_org_repos(data: Any, source: SourceConfig) -> list[RawEntry]:
    if not isinstance(data, list):
        raise FetchError(source.id, source.url, "GitHub repos response must be a list")

    entries: list[RawEntry] = []
    for repo in data:
        if not isinstance(repo, dict):
            continue
        name = _text_or_none(repo.get("full_name") or repo.get("name"))
        url = _text_or_none(repo.get("html_url"))
        if not name or not url:
            continue
        language = _text_or_none(repo.get("language"))
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=name,
                url=url,
                published_at=_parse_iso_datetime(repo.get("created_at"))
                or _parse_iso_datetime(repo.get("pushed_at")),
                raw_content=_text_or_none(repo.get("description")) or f"GitHub repository: {name}",
                author=_repo_owner(name),
                external_id=_text_or_none(repo.get("id") or repo.get("node_id")),
                tags=(language,) if language else (),
            )
        )
    return entries


def parse_huggingface_models(data: Any, source: SourceConfig) -> list[RawEntry]:
    if not isinstance(data, list):
        raise FetchError(source.id, source.url, "HuggingFace models response must be a list")

    entries: list[RawEntry] = []
    for model in data:
        if not isinstance(model, dict):
            continue
        model_id = _text_or_none(model.get("modelId") or model.get("id"))
        if not model_id:
            continue
        tag = _text_or_none(model.get("pipeline_tag"))
        stats = [
            f"downloads: {model.get('downloads')}" if model.get("downloads") is not None else "",
            f"likes: {model.get('likes')}" if model.get("likes") is not None else "",
        ]
        content = ", ".join(part for part in stats if part) or f"HuggingFace model: {model_id}"
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=model_id,
                url=f"https://huggingface.co/{model_id}",
                published_at=_parse_iso_datetime(model.get("createdAt"))
                or _parse_iso_datetime(model.get("lastModified")),
                raw_content=content,
                author=_repo_owner(model_id),
                external_id=model_id,
                tags=(tag,) if tag else (),
            )
        )
    return entries


def parse_hn_algolia(data: Any, source: SourceConfig) -> list[RawEntry]:
    if not isinstance(data, dict) or not isinstance(data.get("hits"), list):
        raise FetchError(source.id, source.url, "HN Algolia response must contain hits")

    entries: list[RawEntry] = []
    for hit in data["hits"]:
        if not isinstance(hit, dict):
            continue
        title = _text_or_none(hit.get("title") or hit.get("story_title"))
        url = _text_or_none(hit.get("url") or hit.get("story_url"))
        object_id = _text_or_none(hit.get("objectID"))
        if not url and object_id:
            url = f"https://news.ycombinator.com/item?id={object_id}"
        if not title or not url:
            continue
        points = hit.get("points")
        comments = hit.get("num_comments")
        content_parts = [
            f"points: {points}" if points is not None else "",
            f"comments: {comments}" if comments is not None else "",
        ]
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=title,
                url=url,
                published_at=_parse_iso_datetime(hit.get("created_at")),
                raw_content=", ".join(part for part in content_parts if part) or title,
                author=_text_or_none(hit.get("author")),
                external_id=object_id,
                tags=("hacker-news",),
            )
        )
    return entries


def parse_html_links(data: bytes, source: SourceConfig) -> list[RawEntry]:
    if not source.url:
        raise FetchError(source.id, source.url, "source has no url")

    parser = _ArticleLinkParser(source.url)
    try:
        parser.feed(data.decode("utf-8", errors="replace"))
    except ValueError as exc:
        raise FetchError(source.id, source.url, str(exc)) from exc

    entries: list[RawEntry] = []
    seen: set[str] = set()
    for title, url in parser.links:
        if url in seen:
            continue
        seen.add(url)
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=title,
                url=url,
                published_at=None,
                raw_content=title,
                tags=("html",),
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
    request = Request(source.url, headers={"User-Agent": "Mozilla/5.0 aihot-ingestion/0.1"})
    last_error: FetchError | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=source.timeout_seconds) as response:
                return response.read()
        except HTTPError as exc:
            last_error = FetchError(source.id, source.url, f"HTTP {exc.code}")
            if exc.code < 500 or attempt == 2:
                raise last_error from exc
        except URLError as exc:
            last_error = FetchError(source.id, source.url, str(exc.reason))
            if attempt == 2:
                raise last_error from exc
        except OSError as exc:
            last_error = FetchError(source.id, source.url, str(exc))
            if attempt == 2:
                raise last_error from exc
    raise last_error or FetchError(source.id, source.url, "unknown fetch failure")


def _fetch_json(source: SourceConfig) -> Any:
    try:
        return json.loads(_fetch_url(source).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise FetchError(source.id, source.url, f"invalid JSON: {exc}") from exc


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


def _parse_iso_datetime(value: Any) -> datetime | None:
    text = _text_or_none(value)
    if text is None:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return _parse_datetime_text(text)
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


def _repo_owner(name: str) -> str | None:
    if "/" not in name:
        return None
    owner, _ = name.split("/", 1)
    return owner or None


def _limit_entries(entries: list[RawEntry]) -> list[RawEntry]:
    return entries[:MAX_ENTRIES_PER_FETCH]


class _ArticleLinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.base = urlsplit(base_url)
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        absolute = urljoin(self.base_url, href)
        if self._is_candidate_url(absolute):
            self._current_href = absolute
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return
        title = " ".join("".join(self._current_text).split())
        if len(title) >= 12:
            self.links.append((title, self._current_href))
        self._current_href = None
        self._current_text = []

    def _is_candidate_url(self, url: str) -> bool:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc != self.base.netloc:
            return False
        base_path = self.base.path.rstrip("/")
        if not base_path:
            return parsed.path not in {"", "/"}
        return parsed.path.startswith(f"{base_path}/")
