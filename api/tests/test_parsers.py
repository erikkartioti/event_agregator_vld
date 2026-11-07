import unittest

from helpers import *  # noqa: F401,F403  (настраивает sys.path)
from app.sources import mariinsky, russian_theater

MARIINSKY_HTML = """
<div class="day_row">
  <time itemprop="startDate" datetime="2026-12-20T19:00:00+03:00"></time>
  <div class="spec_name"><a href="#">Лебединое озеро</a></div>
  <div class="descr">балетный спектакль в двух действиях,музыка П. Чайковского</div>
</div>
<div class="day_row"><div class="spec_name"><a href="#">Без даты</a></div></div>
"""

THEATER_HTML = """
<div class="composition__card">
  <div class="_rubric"><p>12+</p><p>Комедия</p></div>
  <div class="composition__card_title"><p>20 декабря 18:30, Малая сцена</p><h3><a href="#">Ревизор</a></h3></div>
</div>
<div class="composition__card"><div class="composition__card_title"><h3><a href="#">Нет даты</a></h3></div></div>
"""


class MariinskyTests(unittest.TestCase):
    def test_parses_event_and_skips_incomplete_cards(self):
        events = mariinsky.parse_playbill(MARIINSKY_HTML)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "Лебединое озеро")
        self.assertEqual(events[0].date, "2026-12-20 19:00:00")
        self.assertEqual(events[0].genre, "Балет")

    def test_fix_details_format(self):
        genre, text = mariinsky.fix_details_format("опера в трёх действиях,музыка Верди")
        self.assertEqual(genre, "Опера")
        self.assertTrue(text.endswith("."))
        self.assertIn(", музыка", text)

    def test_empty_html(self):
        self.assertEqual(mariinsky.parse_playbill("<html></html>"), [])


class RussianTheaterTests(unittest.TestCase):
    @staticmethod
    def _fake_schedule(text):
        return "2026-12-20 18:30:00", text.split(",")[1].strip()

    def test_parses_card(self):
        events = russian_theater.parse_poster(THEATER_HTML, schedule_parser=self._fake_schedule)
        self.assertEqual([e.title for e in events], ["Ревизор"])
        self.assertEqual(events[0].age_restriction, "12+")
        self.assertEqual(events[0].scene, "Малая сцена")

    def test_unparseable_date_is_skipped(self):
        self.assertEqual(russian_theater.parse_poster(THEATER_HTML, schedule_parser=lambda t: (None, "x")), [])

    def test_parse_schedule_with_dateparser(self):
        try:
            import dateparser  # noqa: F401
        except ImportError:
            self.skipTest("dateparser не установлен")
        date, stage = russian_theater.parse_schedule("20 декабря 18:30, Малая сцена")
        self.assertEqual(stage, "Малая сцена")
        self.assertTrue(date.endswith("-12-20 18:30:00"))


if __name__ == "__main__":
    unittest.main()
