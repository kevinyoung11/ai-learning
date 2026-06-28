from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from time import struct_time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
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
    if source.auth_env and not os.environ.get(source.auth_env):
        raise FetchError(source.id, source.url, f"missing required environment variable {source.auth_env}")

    if not source.url and source.adapter != "x_api_user_timeline":
        raise FetchError(source.id, source.url, "source has no url")

    if source.url and source.url.startswith("fixture://"):
        data = _read_fixture(source, fixture_dir)
        if source.adapter in {"rss", "atom", "github_releases", "rss_proxy", "x_proxy"}:
            return _limit_entries(parse_feed_bytes(data, source))
        if source.adapter == "json_api":
            return _limit_entries(parse_json_api(json.loads(data.decode("utf-8")), source))
        if source.adapter == "html_extract":
            return _limit_entries(parse_html_extract(data, source))
        if source.adapter == "x_api_user_timeline":
            return _limit_entries(parse_x_user_timeline(json.loads(data.decode("utf-8")), source))
        return _limit_entries(parse_feed_bytes(data, source))

    if source.url and source.url.startswith("env://"):
        _resolved_url(source)

    if not allow_network:
        raise FetchError(source.id, source.url, "live network fetch disabled")

    if source.adapter in {"rss", "atom", "github_releases", "rss_proxy", "x_proxy"}:
        return _limit_entries(parse_feed_bytes(_fetch_url(source), source))
    if source.adapter == "github_org_repos":
        return _limit_entries(parse_github_org_repos(_fetch_json(source), source))
    if source.adapter == "huggingface_models":
        return _limit_entries(parse_huggingface_models(_fetch_json(source), source))
    if source.adapter == "hn_algolia":
        return _limit_entries(parse_hn_algolia(_fetch_json(source), source))
    if source.adapter == "html_links":
        return _limit_entries(parse_html_links(_fetch_url(source), source))
    if source.adapter == "html_extract":
        return _limit_entries(parse_html_extract(_fetch_url(source), source))
    if source.adapter == "json_api":
        return _limit_entries(parse_json_api(_fetch_json(source), source))
    if source.adapter == "x_api_user_timeline":
        return _limit_entries(parse_x_user_timeline(_fetch_json(source), source))

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


def parse_json_api(data: Any, source: SourceConfig) -> list[RawEntry]:
    items = _path_value(data, str(source.config.get("items_path", "items")))
    if not isinstance(items, list):
        raise FetchError(source.id, source.url, "JSON API response did not contain an item list")

    entries: list[RawEntry] = []
    for raw_item in items:
        if not isinstance(raw_item, dict):
            continue
        title = _text_or_none(_path_value(raw_item, str(source.config.get("title_path", "title"))))
        url = _text_or_none(_path_value(raw_item, str(source.config.get("url_path", "url"))))
        if not title or not url:
            continue
        tags_value = _path_value(raw_item, str(source.config.get("tags_path", "tags")))
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=title,
                url=url,
                published_at=_parse_iso_datetime(
                    _path_value(raw_item, str(source.config.get("date_path", "published_at")))
                ),
                raw_content=_text_or_none(
                    _path_value(raw_item, str(source.config.get("content_path", "summary")))
                )
                or title,
                author=_text_or_none(_path_value(raw_item, str(source.config.get("author_path", "author")))),
                external_id=_text_or_none(_path_value(raw_item, str(source.config.get("id_path", "id")))),
                tags=_tags_tuple(tags_value),
            )
        )
    return entries


def parse_x_user_timeline(data: Any, source: SourceConfig) -> list[RawEntry]:
    tweets = data.get("data") if isinstance(data, dict) else None
    if not isinstance(tweets, list):
        raise FetchError(source.id, source.url, "X API response must contain data")
    username = str(source.config.get("username") or _included_username(data) or source.id).lstrip("@")

    entries: list[RawEntry] = []
    for tweet in tweets:
        if not isinstance(tweet, dict):
            continue
        tweet_id = _text_or_none(tweet.get("id"))
        text = _text_or_none(tweet.get("text"))
        if not tweet_id or not text:
            continue
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=_trim_title(text),
                url=f"https://x.com/{username}/status/{tweet_id}",
                published_at=_parse_iso_datetime(tweet.get("created_at")),
                raw_content=text,
                author=username,
                external_id=tweet_id,
                tags=("x",),
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


def parse_html_extract(data: bytes, source: SourceConfig) -> list[RawEntry]:
    item_selector = str(source.config.get("item_selector") or "article")
    parser = _SelectorHTMLParser(_base_url(source), item_selector)
    parser.feed(data.decode("utf-8", errors="replace"))
    title_selector = str(source.config.get("title_selector") or "h1")
    link_selector = str(source.config.get("link_selector") or "a")
    date_selector = str(source.config.get("date_selector") or "time")
    content_selector = str(source.config.get("content_selector") or "p")

    entries: list[RawEntry] = []
    for item in parser.items:
        title = item.first_text(title_selector)
        url = item.first_link(link_selector)
        if not title or not url:
            continue
        content = item.first_text(content_selector) or title
        entries.append(
            RawEntry(
                source_id=source.id,
                source_type=source.source_type,
                title=title,
                url=url,
                published_at=_parse_iso_datetime(item.first_datetime(date_selector)),
                raw_content=content,
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
    url = _resolved_url(source)
    headers = {"User-Agent": "Mozilla/5.0 aihot-ingestion/0.1"}
    if source.adapter == "x_api_user_timeline" and source.auth_env:
        headers["Authorization"] = f"Bearer {os.environ[source.auth_env]}"
    request = Request(url, headers=headers)
    last_error: FetchError | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=source.timeout_seconds) as response:
                return response.read()
        except HTTPError as exc:
            last_error = FetchError(source.id, url, f"HTTP {exc.code}")
            if exc.code < 500 or attempt == 2:
                raise last_error from exc
        except URLError as exc:
            last_error = FetchError(source.id, url, str(exc.reason))
            if attempt == 2:
                raise last_error from exc
        except OSError as exc:
            last_error = FetchError(source.id, url, str(exc))
            if attempt == 2:
                raise last_error from exc
    raise last_error or FetchError(source.id, url, "unknown fetch failure")


def _fetch_json(source: SourceConfig) -> Any:
    try:
        return json.loads(_fetch_url(source).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise FetchError(source.id, source.url, f"invalid JSON: {exc}") from exc


def _resolved_url(source: SourceConfig) -> str:
    if source.url:
        if source.url.startswith("env://"):
            return _resolve_env_url(source)
        return source.url
    if source.adapter == "x_api_user_timeline":
        user_id = _text_or_none(source.config.get("user_id"))
        if not user_id:
            raise FetchError(source.id, source.url, "x_api_user_timeline requires url or config.user_id")
        params = {
            "tweet.fields": "created_at",
            "max_results": str(int(source.config.get("max_results", 10))),
        }
        return f"https://api.x.com/2/users/{user_id}/tweets?{urlencode(params)}"
    raise FetchError(source.id, source.url, "source has no url")


def _resolve_env_url(source: SourceConfig) -> str:
    assert source.url is not None
    rest = source.url.removeprefix("env://")
    env_name, separator, suffix = rest.partition("/")
    base_url = os.environ.get(env_name)
    if not separator or not env_name or not base_url:
        raise FetchError(source.id, source.url, f"missing required environment variable {env_name}")
    return "/".join([base_url.rstrip("/"), suffix.lstrip("/")])


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


def _path_value(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        else:
            return None
    return current


def _tags_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(str(item) for item in value if _text_or_none(item))
    if tag := _text_or_none(value):
        return (tag,)
    return ()


def _included_username(data: Any) -> str | None:
    if not isinstance(data, dict):
        return None
    users = data.get("includes", {}).get("users") if isinstance(data.get("includes"), dict) else None
    if not isinstance(users, list) or not users:
        return None
    first = users[0]
    return _text_or_none(first.get("username")) if isinstance(first, dict) else None


def _trim_title(text: str) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= 120 else compact[:117].rstrip() + "..."


def _base_url(source: SourceConfig) -> str:
    if base_url := _text_or_none(source.config.get("base_url")):
        return base_url
    if source.url and not source.url.startswith("fixture://"):
        return source.url
    return "https://example.com"


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


@dataclass
class _HTMLNode:
    tag: str
    attrs: dict[str, str]
    text: list[str]


class _ExtractedItem:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.nodes: list[_HTMLNode] = []

    def first_text(self, selector: str) -> str | None:
        for node in self.nodes:
            if _selector_matches(node.tag, node.attrs, selector):
                text = " ".join("".join(node.text).split())
                if text:
                    return text
        return None

    def first_link(self, selector: str) -> str | None:
        for node in self.nodes:
            if _selector_matches(node.tag, node.attrs, selector):
                href = node.attrs.get("href")
                if href:
                    return urljoin(self.base_url, href)
        return None

    def first_datetime(self, selector: str) -> str | None:
        for node in self.nodes:
            if _selector_matches(node.tag, node.attrs, selector):
                return node.attrs.get("datetime") or " ".join("".join(node.text).split())
        return None


class _SelectorHTMLParser(HTMLParser):
    def __init__(self, base_url: str, item_selector: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.item_selector = item_selector
        self.items: list[_ExtractedItem] = []
        self._current_item: _ExtractedItem | None = None
        self._item_depth = 0
        self._open_nodes: list[_HTMLNode] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if self._current_item is None and _selector_matches(tag, attr_map, self.item_selector):
            self._current_item = _ExtractedItem(self.base_url)
            self._item_depth = 1
            return
        if self._current_item is None:
            return
        self._item_depth += 1
        node = _HTMLNode(tag, attr_map, [])
        self._current_item.nodes.append(node)
        self._open_nodes.append(node)

    def handle_data(self, data: str) -> None:
        if self._open_nodes:
            self._open_nodes[-1].text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current_item is None:
            return
        if self._open_nodes and self._open_nodes[-1].tag == tag:
            self._open_nodes.pop()
        self._item_depth -= 1
        if self._item_depth <= 0:
            self.items.append(self._current_item)
            self._current_item = None
            self._open_nodes = []


def _selector_matches(tag: str, attrs: dict[str, str], selector: str) -> bool:
    selector = selector.strip()
    if not selector:
        return False
    if selector.startswith("."):
        expected_tag = None
        expected_class = selector[1:]
    elif "." in selector:
        expected_tag, expected_class = selector.split(".", 1)
    else:
        expected_tag, expected_class = selector, None
    if expected_tag and tag != expected_tag:
        return False
    if expected_class:
        return expected_class in attrs.get("class", "").split()
    return True
