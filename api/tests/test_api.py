import os
import unittest
from unittest import mock

from helpers import *  # noqa: F401,F403
from app.sources.common import Event, SourceError

try:
    from fastapi.testclient import TestClient
except ImportError:  # fastapi/httpx есть в контейнере сервиса
    TestClient = None


class FakeSource:
    kind, url = "html", "https://x.test"

    def __init__(self, name, events=None, error=None):
        self.name, self._events, self._error = name, events or [], error

    def fetch(self):
        if self._error:
            raise self._error
        return self._events

    def probe(self):
        return {"source": self.name, "reachable": True}


@unittest.skipIf(TestClient is None, "fastapi не установлен")
class ApiTests(unittest.TestCase):
    def setUp(self):
        from app.main import app, get_registry

        registry = {
            "ok": FakeSource("ok", [Event("Ревизор", "2026-12-20 18:30:00", "Театр", genre="Комедия")]),
            "down": FakeSource("down", error=SourceError("down: timeout")),
        }
        app.dependency_overrides[get_registry] = lambda: registry
        self.client = TestClient(app)
        self.app = app

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def test_health(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})

    def test_events(self):
        response = self.client.get("/sources/ok/events")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["title"], "Ревизор")

    def test_unknown_source_404(self):
        self.assertEqual(self.client.get("/sources/nope/events").status_code, 404)

    def test_source_failure_is_502(self):
        self.assertEqual(self.client.get("/sources/down/events").status_code, 502)

    def test_diagnose_without_key_is_503(self):
        body = {"dag_id": "d", "task_id": "t", "run_id": "manual__1"}
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            self.assertEqual(self.client.post("/diagnose", json=body).status_code, 503)

    def test_diagnose_rejects_bad_ids(self):
        body = {"dag_id": "../x", "task_id": "t", "run_id": "r"}
        self.assertEqual(self.client.post("/diagnose", json=body).status_code, 422)


if __name__ == "__main__":
    unittest.main()
