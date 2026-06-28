from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from hashlib import sha1

from aihot.models import NormalizedItem, Story


_STORY_SOURCE_IDS: dict[str, tuple[str, ...]] = {}
_TITLE_STOPWORDS = {
    "a",
    "ai",
    "an",
    "and",
    "for",
    "hn",
    "in",
    "latest",
    "news",
    "of",
    "on",
    "show",
    "the",
    "to",
    "under",
    "using",
    "with",
}


def dedupe_items(items: Iterable[NormalizedItem]) -> list[NormalizedItem]:
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    deduped: list[NormalizedItem] = []

    for item in items:
        if item.canonical_url in seen_urls or item.content_hash in seen_hashes:
            continue
        seen_urls.add(item.canonical_url)
        seen_hashes.add(item.content_hash)
        deduped.append(item)

    return deduped


def cluster_items(items: Iterable[NormalizedItem]) -> list[Story]:
    clusters: list[list[NormalizedItem]] = []

    for item in sorted(_dedupe_for_clustering(items), key=_item_sort_key):
        for cluster in clusters:
            if _belongs_to_cluster(item, cluster):
                cluster.append(item)
                break
        else:
            clusters.append([item])

    stories = [_story_from_cluster(cluster) for cluster in clusters]
    return sorted(
        stories,
        key=lambda story: (-story.source_count, story.day, story.canonical_title, story.id),
    )


def get_story_source_ids(story: Story) -> tuple[str, ...]:
    return _STORY_SOURCE_IDS.get(story.id, ())


def _belongs_to_cluster(item: NormalizedItem, cluster: list[NormalizedItem]) -> bool:
    if not any(
        abs(item.published_at - existing.published_at) <= timedelta(hours=24)
        for existing in cluster
    ):
        return False

    item_tokens = _tokens(item.title_key or item.title)
    return any(
        item.source_id != existing.source_id
        and _token_similarity(item_tokens, _tokens(existing.title_key or existing.title))
        for existing in cluster
    )


def _story_from_cluster(cluster: list[NormalizedItem]) -> Story:
    ordered = sorted(cluster, key=_item_sort_key)
    representative = ordered[0]
    source_ids = tuple(sorted({item.source_id for item in ordered}))
    item_urls = tuple(dict.fromkeys(item.canonical_url for item in ordered))
    day = representative.published_at.date().isoformat()
    story_id = _story_id(day, representative.title_key, item_urls[0] if len(item_urls) == 1 else "")
    _STORY_SOURCE_IDS[story_id] = source_ids

    return Story(
        id=story_id,
        canonical_title=representative.title,
        day=day,
        summary=representative.raw_content,
        hotness=float(len(ordered)),
        source_count=len(source_ids),
        item_urls=item_urls,
    )


def _tokens(text: str) -> set[str]:
    return {token for token in text.lower().split() if token and token not in _TITLE_STOPWORDS}


def _token_similarity(left: set[str], right: set[str]) -> bool:
    if not left or not right:
        return False
    overlap = len(left & right)
    smaller = min(len(left), len(right))
    if smaller <= 3:
        return left == right
    return overlap >= 3 and overlap / smaller >= 0.60


def _dedupe_for_clustering(items: Iterable[NormalizedItem]) -> list[NormalizedItem]:
    seen_source_urls: set[tuple[str, str]] = set()
    deduped: list[NormalizedItem] = []

    for item in items:
        key = (item.source_id, item.canonical_url)
        if key in seen_source_urls:
            continue

        seen_source_urls.add(key)
        deduped.append(item)

    return deduped


def _story_id(day: str, title_key: str, disambiguator: str = "") -> str:
    digest = sha1(f"{day}\n{title_key}\n{disambiguator}".encode("utf-8")).hexdigest()
    return digest[:12]


def _item_sort_key(item: NormalizedItem) -> tuple[object, ...]:
    return (item.published_at, item.title_key, item.canonical_url, item.source_id)
