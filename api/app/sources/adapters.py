"""Адаптеры источников: единый интерфейс fetch() / probe() поверх HTML-страниц и JSON API."""
from __future__ import annotations

import logging
import os
from typing import Any, Callable

import requests

from .common import USER_AGENT, Event, SourceError, normalize_date

log = logging.getLogger(__name__)


def dig(data: Any, path: str | None) -> Any:
    """Достаёт значение по пути вида 'data.items.0.title'. Нет значения -> None."""
    if not path:
        return None
    current = data
    for part in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


class _HttpSource:
    kind = "http"

    def __init__(self, name, url, *, session=None, timeout=30, headers=None, params=None):
        self.name = name
        self.url = url
        self.session = session or requests.Session()
        self.timeout = timeout
        self.headers = {"User-Agent": USER_AGENT, **(headers or {})}
        self.params = params

    def _request(self):
        return self.session.get(self.url, headers=self.headers, params=self.params, timeout=self.timeout)

    def _get(self):
        try:
            response = self._request()
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SourceError(f"{self.name}: запрос не удался: {exc}") from exc
        return response

    def _inspect(self, response) -> dict:
        return {}

    def probe(self) -> dict:
        """Диагностическая проверка источника: никогда не бросает исключений."""
        try:
            response = self._request()
        except requests.RequestException as exc:
            return {"source": self.name, "reachable": False, "error": f"{type(exc).__name__}: {exc}"[:300]}
        info = {
            "source": self.name,
            "reachable": True,
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "bytes": len(response.content),
        }
        info.update(self._inspect(response))
        return info


class HtmlSource(_HttpSource):
    """Страница афиши, разбираемая функцией parser(html) -> list[Event]."""

    kind = "html"

    def __init__(self, name, url, parser: Callable[[str], list[Event]], expected_marker: str, **kwargs):
        super().__init__(name, url, **kwargs)
        self.parser = parser
        self.expected_marker = expected_marker  # фрагмент вёрстки, без которого парсер ничего не найдёт

    def fetch(self) -> list[Event]:
        return self.parser(self._get().text)

    def _inspect(self, response) -> dict:
        return {"expected_marker": self.expected_marker, "marker_found": self.expected_marker in response.text}


class JsonApiSource(_HttpSource):
    """Настоящий JSON API театра/билетной системы. Соответствие полей задаётся конфигом."""

    kind = "api"

    def __init__(self, name, url, location, items_path, field_map, **kwargs):
        kwargs["headers"] = {k: os.path.expandvars(v) for k, v in (kwargs.get("headers") or {}).items()}
        super().__init__(name, url, **kwargs)
        self.location = location
        self.items_path = items_path
        self.field_map = field_map

    def _field(self, item, key):
        value = dig(item, self.field_map.get(key))
        return str(value).strip() if value not in (None, "") else None

    def fetch(self) -> list[Event]:
        response = self._get()
        try:
            data = response.json()
        except ValueError as exc:
            raise SourceError(f"{self.name}: ответ не является JSON") from exc
        items = dig(data, self.items_path) if self.items_path else data
        if not isinstance(items, list):
            raise SourceError(f"{self.name}: по пути '{self.items_path}' нет списка событий")

        events: list[Event] = []
        for item in items:
            title = self._field(item, "title")
            date = normalize_date(self._field(item, "date"))
            if not title or not date:
                log.warning("%s: пропущена запись без названия или даты", self.name)
                continue
            events.append(
                Event(
                    title=title,
                    date=date,
                    location=self.location,
                    genre=self._field(item, "genre"),
                    age_restriction=self._field(item, "age_restriction"),
                    scene=self._field(item, "scene"),
                    details=self._field(item, "details"),
                )
            )
        return events

    def _inspect(self, response) -> dict:
        try:
            items = dig(response.json(), self.items_path) if self.items_path else response.json()
        except ValueError:
            return {"is_json": False}
        return {"is_json": True, "items_found": len(items) if isinstance(items, list) else None}
