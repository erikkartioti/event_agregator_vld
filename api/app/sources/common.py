"""Общая модель события и вспомогательные функции источников."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime

USER_AGENT = "Mozilla/5.0 (compatible; EventAggregatorBot/1.0)"


class SourceError(Exception):
    """Источник недоступен или вернул данные неожиданного формата."""


@dataclass(frozen=True)
class Event:
    title: str
    date: str  # 'YYYY-MM-DD HH:MM:SS' (локальное время, как в БД)
    location: str
    genre: str | None = None
    age_restriction: str | None = None
    scene: str | None = None
    details: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def normalize_date(value: object) -> str | None:
    """ISO-строка (с часовым поясом или без) -> 'YYYY-MM-DD HH:MM:SS' или None."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    return parsed.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
