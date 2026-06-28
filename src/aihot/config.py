from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from aihot.models import SourceConfig


class SourceCatalogError(ValueError):
    pass


def load_sources(path: str | Path, *, enabled_only: bool = False) -> list[SourceConfig]:
    catalog_path = Path(path)
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise SourceCatalogError("catalog must contain a sources list")

    seen: set[str] = set()
    sources: list[SourceConfig] = []
    for index, raw_source in enumerate(data["sources"], start=1):
        if not isinstance(raw_source, dict):
            raise SourceCatalogError(f"source #{index} must be a mapping")
        source = _build_source(raw_source, index)
        if source.id in seen:
            raise SourceCatalogError(f"duplicate source id: {source.id}")
        seen.add(source.id)
        _validate_source(source)
        if not enabled_only or _is_active_fetch_source(source):
            sources.append(source)
    return sources


def _build_source(raw_source: dict[str, Any], index: int) -> SourceConfig:
    missing = [field for field in ("id", "name", "source_type", "adapter") if not raw_source.get(field)]
    if missing:
        raise SourceCatalogError(f"source #{index} missing required fields: {', '.join(missing)}")
    return SourceConfig(
        id=str(raw_source["id"]),
        name=str(raw_source["name"]),
        source_type=str(raw_source["source_type"]),
        adapter=str(raw_source["adapter"]),
        url=str(raw_source["url"]) if raw_source.get("url") else None,
        tier=str(raw_source.get("tier", "stable")),
        weight=float(raw_source.get("weight", 1.0)),
        enabled=bool(raw_source.get("enabled", True)),
        timeout_seconds=float(raw_source.get("timeout_seconds", 10.0)),
        run_mode=str(raw_source.get("run_mode", "active")),
        auth_env=str(raw_source["auth_env"]) if raw_source.get("auth_env") else None,
        config=dict(raw_source.get("config") or {}),
        quarantined=bool(raw_source.get("quarantined", False)),
    )


def _validate_source(source: SourceConfig) -> None:
    if source.run_mode not in {"active", "shadow"}:
        raise SourceCatalogError(f"source {source.id} run_mode must be active or shadow")
    if source.enabled and source.run_mode == "active" and source.adapter == "disabled":
        raise SourceCatalogError(f"enabled active source {source.id} cannot use disabled adapter")
    if source.enabled and source.adapter != "disabled" and _requires_url(source) and not source.url:
        raise SourceCatalogError(f"enabled source {source.id} requires url")
    if source.config and not isinstance(source.config, dict):
        raise SourceCatalogError(f"source {source.id} config must be a mapping")


def _requires_url(source: SourceConfig) -> bool:
    if source.adapter == "x_api_user_timeline":
        return False
    return True


def _is_active_fetch_source(source: SourceConfig) -> bool:
    return source.enabled and source.run_mode == "active" and not source.quarantined
