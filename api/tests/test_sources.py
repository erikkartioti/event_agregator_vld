import unittest

import requests

from helpers import FakeResponse, FakeSession
from app.sources.adapters import HtmlSource, JsonApiSource, dig
from app.sources.common import SourceError

API_PAYLOAD = {
    "data": {
        "items": [
            {"name": "Ревизор", "start_at": "2026-12-20T18:30:00+03:00", "hall": {"name": "Большая сцена"}, "age": "12+"},
            {"name": "", "start_at": "2026-12-21T18:30:00"},
            {"name": "Без даты"},
        ]
    }
}
FIELD_MAP = {"title": "name", "date": "start_at", "scene": "hall.name", "age_restriction": "age"}


def api_source(session):
    return JsonApiSource("t_api", "https://x.test/events", "Театр", "data.items", FIELD_MAP, session=session)


class DigTests(unittest.TestCase):
    def test_nested_and_list_paths(self):
        self.assertEqual(dig({"a": {"b": [10, 20]}}, "a.b.1"), 20)
        self.assertIsNone(dig({"a": 1}, "a.b"))
        self.assertIsNone(dig({"a": [1]}, "a.5"))
        self.assertIsNone(dig({"a": 1}, None))


class JsonApiSourceTests(unittest.TestCase):
    def test_maps_fields_and_skips_incomplete_items(self):
        events = api_source(FakeSession(FakeResponse(json_data=API_PAYLOAD))).fetch()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "Ревизор")
        self.assertEqual(events[0].date, "2026-12-20 18:30:00")
        self.assertEqual(events[0].scene, "Большая сцена")
        self.assertEqual(events[0].location, "Театр")

    def test_wrong_items_path_raises_source_error(self):
        with self.assertRaises(SourceError):
            api_source(FakeSession(FakeResponse(json_data={"data": {}}))).fetch()

    def test_non_json_raises_source_error(self):
        with self.assertRaises(SourceError):
            api_source(FakeSession(FakeResponse(text="<html>"))).fetch()

    def test_http_error_raises_source_error(self):
        with self.assertRaises(SourceError):
            api_source(FakeSession(FakeResponse(status_code=500, text="boom"))).fetch()

    def test_probe_reports_items(self):
        info = api_source(FakeSession(FakeResponse(json_data=API_PAYLOAD))).probe()
        self.assertTrue(info["reachable"])
        self.assertEqual(info["items_found"], 3)


class HtmlSourceProbeTests(unittest.TestCase):
    def _source(self, session):
        return HtmlSource("h", "https://x.test", lambda html: [], expected_marker="day_row", session=session)

    def test_marker_found(self):
        info = self._source(FakeSession(FakeResponse(text='<div class="day_row"></div>'))).probe()
        self.assertTrue(info["marker_found"])

    def test_marker_missing_means_layout_changed(self):
        info = self._source(FakeSession(FakeResponse(text="<html>new layout</html>"))).probe()
        self.assertEqual(info["status_code"], 200)
        self.assertFalse(info["marker_found"])

    def test_probe_never_raises_on_network_error(self):
        info = self._source(FakeSession(error=requests.ConnectionError("dns"))).probe()
        self.assertFalse(info["reachable"])
        self.assertIn("ConnectionError", info["error"])

    def test_fetch_wraps_network_error(self):
        with self.assertRaises(SourceError):
            self._source(FakeSession(error=requests.Timeout("slow"))).fetch()


if __name__ == "__main__":
    unittest.main()
