"""Парсер афиши Русского театра им. Вахтангова (teatr15.ru)."""
from __future__ import annotations

import logging
import re
from typing import Callable

from bs4 import BeautifulSoup

from .common import Event

log = logging.getLogger(__name__)

URL = "https://teatr15.ru/poster/"
LOCATION = "Академический Русский театр имени Евгения Вахтангова"


def parse_schedule(text: str) -> tuple[str | None, str]:
    """'20 июня 19:00, Большая сцена' -> ('2026-06-20 19:00:00', 'Большая сцена')."""
    import dateparser  # импорт здесь, чтобы тесты остальных функций не зависели от библиотеки

    match = re.search(r",\s*(.+)$", text)
    stage = match.group(1) if match else "Unknown Stage"
    parsed = dateparser.parse(
        text.split(",")[0],
        languages=["ru"],
        settings={"PREFER_DATES_FROM": "future"},  # афиша содержит будущие даты
    )
    return (parsed.strftime("%Y-%m-%d %H:%M:%S") if parsed else None), stage


def parse_poster(
    html: str,
    schedule_parser: Callable[[str], tuple[str | None, str]] = parse_schedule,
) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[Event] = []

    for card in soup.find_all("div", class_="composition__card"):
        rubric = card.find("div", class_="_rubric")
        p_tags = rubric.find_all("p") if rubric else []
        age_restriction = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else "N/A"
        genre = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else "N/A"

        title_div = card.find("div", class_="composition__card_title")
        if title_div is None:
            continue
        schedule_tag = title_div.find("p")
        h3 = title_div.find("h3")
        link = h3.find("a") if h3 else None
        if schedule_tag is None or link is None:
            log.warning("Пропущена карточка: нет названия или расписания")
            continue

        title = link.get_text(strip=True)
        date, stage = schedule_parser(schedule_tag.get_text(strip=True))
        if not date:
            log.warning("Пропущено событие %r: не удалось разобрать дату", title)
            continue

        events.append(
            Event(
                title=title,
                date=date,
                location=LOCATION,
                genre=genre,
                age_restriction=age_restriction,
                scene=stage,
            )
        )
    return events
