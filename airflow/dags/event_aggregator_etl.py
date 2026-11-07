"""ETL афиши городских мероприятий: источники (через parser-api) -> PostgreSQL -> очистка устаревших.

Парсинг вынесен в сервис parser-api (FastAPI): DAG обращается к нему по REST.
При окончательном падении любой задачи вызывается агент диагностики (POST /diagnose).
Подключение к БД: Airflow Connection `events_db` (в compose задаётся через AIRFLOW_CONN_EVENTS_DB).
"""
from __future__ import annotations

import logging
import os
from datetime import timedelta

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.providers.postgres.hooks.postgres import PostgresHook

log = logging.getLogger(__name__)

CONN_ID = "events_db"
SOURCES = ("russian_theater", "mariinsky")
INSERT_SQL = """
    INSERT INTO events (title, date, genre, age_restriction, location, scene, details)
    VALUES %s
    ON CONFLICT (title, date) DO NOTHING
    RETURNING id
"""
CLEANUP_SQL = """
    WITH deleted AS (
        DELETE FROM events
        WHERE date < (now() AT TIME ZONE 'Europe/Moscow')
        RETURNING 1
    )
    SELECT count(*) FROM deleted
"""


def _parser_api_url() -> str:
    return os.environ.get("PARSER_API_URL", "http://parser-api:8000")


def diagnose_failure(context) -> None:
    """on_failure_callback: просит LLM-агента разобрать сбой. Сам никогда не падает."""
    ti = context["task_instance"]
    payload = {
        "dag_id": ti.dag_id,
        "task_id": ti.task_id,
        "run_id": context["run_id"],
        "error": str(context.get("exception") or "")[:1000],
    }
    try:
        response = requests.post(f"{_parser_api_url()}/diagnose", json=payload, timeout=90)
        if response.ok:
            d = response.json()
            log.error("ДИАГНОЗ [%s, уверенность %s]: %s Причина: %s Действие: %s",
                      d["category"], d["confidence"], d["summary"], d["probable_cause"], d["suggested_action"])
        else:
            log.warning("Диагностика недоступна: HTTP %s", response.status_code)
    except Exception:  # диагностика вторична и не должна ломать обработку сбоя
        log.exception("Не удалось получить диагноз")


@dag(
    dag_id="event_aggregator_etl",
    description="Сбор афиши театров, загрузка в БД и очистка прошедших событий",
    schedule="0 16 * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "event-aggregator",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": diagnose_failure,
    },
    tags=["etl", "events"],
)
def event_aggregator_etl():
    @task
    def extract(source: str) -> list[dict]:
        response = requests.get(f"{_parser_api_url()}/sources/{source}/events", timeout=90)
        response.raise_for_status()
        events = response.json()
        log.info("%s: получено событий: %d", source, len(events))
        if not events:
            # пустой результат обычно означает смену вёрстки или формата API, повторять бессмысленно
            raise AirflowFailException(f"{source}: источник не вернул ни одного события")
        return events

    # all_done: падение одного источника не мешает загрузить данные другого
    @task(trigger_rule="all_done")
    def load_events(batches: list[list[dict] | None]) -> int:
        from psycopg2.extras import execute_values

        rows = [
            (e["title"], e["date"], e["genre"], e["age_restriction"], e["location"], e["scene"], e["details"])
            for batch in batches
            if batch
            for e in batch
        ]
        if not rows:
            raise AirflowFailException("Нет данных для загрузки: все источники вернули ошибку")

        conn = PostgresHook(postgres_conn_id=CONN_ID).get_conn()
        try:
            with conn, conn.cursor() as cur:
                inserted = execute_values(cur, INSERT_SQL, rows, fetch=True)
        finally:
            conn.close()
        log.info("Получено: %d, добавлено новых: %d", len(rows), len(inserted))
        return len(inserted)

    @task
    def cleanup_outdated_events() -> int:
        deleted = PostgresHook(postgres_conn_id=CONN_ID).get_first(CLEANUP_SQL)[0]
        log.info("Удалено устаревших событий: %d", deleted)
        return deleted

    # DAG-run считается по последней задаче, поэтому этот шаг делает падение источника видимым в статусе запуска
    @task(trigger_rule="all_done")
    def assert_sources_healthy(**context) -> None:
        failed = [
            ti.task_id
            for ti in context["dag_run"].get_task_instances(state=["failed", "upstream_failed"])
        ]
        if failed:
            raise AirflowFailException(f"Часть задач завершилась с ошибкой: {failed}")

    extracts = [extract.override(task_id=f"extract_{source}")(source) for source in SOURCES]
    loaded = load_events(extracts)
    cleaned = cleanup_outdated_events()
    loaded >> cleaned >> assert_sources_healthy()


event_aggregator_etl()
