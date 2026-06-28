from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from aihot.models import NormalizedItem, RawEntry


def normalize_entry(entry: RawEntry, *, fetched_at: datetime) -> NormalizedItem | None:
    title = _clean_text(entry.title)
    url = _clean_text(entry.url)
    if not title or not url:
        return None

    canonical_url = canonicalize_url(url)
    title_key = normalize_title_key(title)
    raw_content = entry.raw_content or ""
    published_at = _to_utc(entry.published_at or fetched_at)
    fetched_at_utc = _to_utc(fetched_at)
    content_hash = _content_hash(title_key, raw_content)

    return NormalizedItem(
        source_id=entry.source_id,
        source_type=entry.source_type,
        title=title,
        url=url,
        canonical_url=canonical_url,
        raw_content=raw_content,
        published_at=published_at,
        fetched_at=fetched_at_utc,
        content_hash=content_hash,
        title_key=title_key,
    )


def canonicalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    port = parsed.port

    netloc = hostname
    if port is not None and not _is_default_port(scheme, port):
        netloc = f"{netloc}:{port}"

    path = parsed.path or ""
    if path != "/":
        path = path.rstrip("/")
    else:
        path = ""

    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not _is_tracking_param(key)
    ]
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def normalize_title_key(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).casefold()
    chars: list[str] = []
    for char in normalized:
        category = unicodedata.category(char)
        if category[0] in {"P", "S"}:
            chars.append(" ")
        elif char.isalnum() or char.isspace():
            chars.append(char)
        else:
            chars.append(" ")
    return re.sub(r"\s+", " ", "".join(chars)).strip()


def _is_default_port(scheme: str, port: int) -> bool:
    return (scheme == "http" and port == 80) or (scheme == "https" and port == 443)


def _is_tracking_param(key: str) -> bool:
    lowered = key.lower()
    return lowered == "ref" or lowered.startswith("utm_")


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _content_hash(title_key: str, raw_content: str) -> str:
    content_key = normalize_title_key(raw_content)
    payload = "\n".join((title_key, content_key))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
