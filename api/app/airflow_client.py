"""Клиент Airflow REST API только для чтения (логи и история запусков)."""
from __future__ import annotations

from urllib.parse import quote

import requests


class AirflowClient:
    def __init__(self, base_url: str, user: str, password: str, session=None, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.auth = (user, password)
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, path: str, **kwargs):
        response = self.session.get(f"{self.base_url}{path}", auth=self.auth, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

    def get_log(self, dag_id: str, run_id: str, task_id: str, tail_chars: int = 4000) -> str:
        run = quote(run_id, safe="")
        base = f"/dags/{dag_id}/dagRuns/{run}/taskInstances/{task_id}"
        try_number = self._get(base).json().get("try_number") or 1  # последняя попытка
        text = self._get(f"{base}/logs/{try_number}", headers={"Accept": "text/plain"}).text
        return text[-tail_chars:]

    def recent_runs(self, dag_id: str, limit: int = 5) -> list[dict]:
        data = self._get(f"/dags/{dag_id}/dagRuns", params={"order_by": "-execution_date", "limit": limit}).json()
        return [
            {k: run.get(k) for k in ("dag_run_id", "state", "start_date", "end_date")}
            for run in data.get("dag_runs", [])
        ]
