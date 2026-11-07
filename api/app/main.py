"""Сервис парсинга афиши (FastAPI): источники -> нормализованные события + диагностика сбоев LLM-агентом."""
from __future__ import annotations

import os
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException

from .agent import AgentError, DiagnosticsAgent, build_tools
from .airflow_client import AirflowClient
from .schemas import DiagnoseRequest, DiagnosisOut, EventOut, SourceInfo
from .sources.common import SourceError
from .sources.registry import build_registry

app = FastAPI(title="Event Parser API", version="1.0.0")


@lru_cache
def get_registry() -> dict:
    return build_registry()


def get_agent() -> DiagnosticsAgent:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="LLM не настроен: задайте ANTHROPIC_API_KEY")
    import anthropic  # импорт здесь: сервис парсинга работает и без SDK

    airflow = AirflowClient(
        os.environ.get("AIRFLOW_API_URL", "http://airflow-webserver:8080/api/v1"),
        os.environ.get("AIRFLOW_API_USER", "diagnostics"),
        os.environ.get("AIRFLOW_API_PASSWORD", ""),
    )
    return DiagnosticsAgent(
        client=anthropic.Anthropic(api_key=api_key),
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
        tools=build_tools(get_registry(), airflow),
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/sources", response_model=list[SourceInfo])
def list_sources(registry: dict = Depends(get_registry)):
    return [SourceInfo(name=s.name, kind=s.kind, url=s.url) for s in registry.values()]


def _source_or_404(registry: dict, name: str):
    source = registry.get(name)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Источник '{name}' не найден")
    return source


@app.get("/sources/{name}/events", response_model=list[EventOut])
def source_events(name: str, registry: dict = Depends(get_registry)):
    source = _source_or_404(registry, name)
    try:
        return [event.as_dict() for event in source.fetch()]
    except SourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/sources/{name}/probe")
def source_probe(name: str, registry: dict = Depends(get_registry)):
    return _source_or_404(registry, name).probe()


@app.post("/diagnose", response_model=DiagnosisOut)
def diagnose(request: DiagnoseRequest, agent: DiagnosticsAgent = Depends(get_agent)):
    try:
        return agent.run(request.model_dump()).as_dict()
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
