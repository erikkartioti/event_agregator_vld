"""Реестр источников: HTML-парсеры по умолчанию + JSON API из конфига (SOURCES_CONFIG)."""
from __future__ import annotations

import json
import os

from . import mariinsky, russian_theater
from .adapters import HtmlSource, JsonApiSource


def build_registry(session=None, config_path: str | None = None) -> dict:
    sources = [
        HtmlSource("russian_theater", russian_theater.URL, russian_theater.parse_poster,
                   expected_marker="composition__card", session=session),
        HtmlSource("mariinsky", mariinsky.URL, mariinsky.parse_playbill,
                   expected_marker="day_row", session=session),
    ]
    path = config_path or os.environ.get("SOURCES_CONFIG")
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for cfg in json.load(fh):
                sources.append(JsonApiSource(session=session, **cfg))
    return {source.name: source for source in sources}
