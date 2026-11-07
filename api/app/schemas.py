from __future__ import annotations

from pydantic import BaseModel, Field


class EventOut(BaseModel):
    title: str
    date: str = Field(description="YYYY-MM-DD HH:MM:SS, локальное время")
    location: str
    genre: str | None = None
    age_restriction: str | None = None
    scene: str | None = None
    details: str | None = None


class SourceInfo(BaseModel):
    name: str
    kind: str
    url: str


class DiagnoseRequest(BaseModel):
    dag_id: str = Field(pattern=r"^[A-Za-z0-9_.\-]{1,250}$")
    task_id: str = Field(pattern=r"^[A-Za-z0-9_.\-]{1,250}$")
    run_id: str = Field(pattern=r"^[A-Za-z0-9_.:+\-]{1,250}$")
    error: str | None = Field(default=None, max_length=2000)


class DiagnosisOut(BaseModel):
    category: str
    summary: str
    probable_cause: str
    suggested_action: str
    confidence: str
