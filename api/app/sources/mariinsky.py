"""Парсер афиши филиала Мариинского театра в РСО-Алания."""
from __future__ import annotations

import logging
import re

from bs4 import BeautifulSoup

from .common import Event, normalize_date

log = logging.getLogger(__name__)

URL = "https://alania.mariinsky.ru/playbill/playbill/"
LOCATION = "Филиал Мариинского театра в РСО-Алания"
_GENRE_RE = re.compile(r"^(балетный спектакль|опера|оперетта|балет)\b", re.IGNORECASE)


def fix_details_format(details: str) -> tuple[str | None, str]:
    """Приводит описание к читаемому виду и достаёт жанр из его начала."""
    text = re.sub(r"([а-яa-z])([А-ЯA-Z])", r"\1. \2", details)
    text = re.sub(r"([A-Za-zА-Яа-я])–", r"\1 –", text)
    text = re.sub(r"–([A-Za-zА-Яа-я])", r"– \1", text)
    text = re.sub(r",([^\s])", r", \1", text)
    text = re.sub(r"([^\s])\(", r"\1 (", text)
    text = re.sub(r"\)([A-ZА-Я])", r"). \1", text)

    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
        if not text.endswith("."):
            text += "."

    genre = None
    match = _GENRE_RE.search(text)
    if match:
        genre = match.group(1).lower()
        if genre == "балетный спектакль":
            genre = "балет"
        genre = genre.capitalize()
    return genre, text


def parse_playbill(html: str) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[Event] = []

    for row in soup.find_all("div", class_="day_row"):
        time_tag = row.find("time", itemprop="startDate")
        date = normalize_date(time_tag.get("datetime") if time_tag else None)

        name_div = row.find("div", class_="spec_name")
        link = name_div.find("a") if name_div else None
        title = link.get_text(strip=True) if link else None

        if not title or not date:
            log.warning("Пропущена карточка без названия или даты: title=%r date=%r", title, date)
            continue

        descr = row.find("div", class_="descr")
        genre, details = fix_details_format(descr.get_text(strip=True)) if descr else (None, "")

        events.append(
            Event(
                title=title,
                date=date,
                location=LOCATION,
                genre=genre or "N/A",
                age_restriction=None,
                scene="N/A",
                details=details or None,
            )
        )
    return events
