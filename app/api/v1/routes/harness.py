from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.harness import STORE, simulate_run, validate_trace_jsonl

router = APIRouter(prefix="/v1", tags=["harness"])


class RunCreate(BaseModel):
    config: Dict[str, Any] = Field(default_factory=dict)
    task: Dict[str, Any] = Field(default_factory=dict)


class RunOut(BaseModel):
    run_id: str
    created_at: float
    config: Dict[str, Any]
    task: Dict[str, Any]


class EventOut(BaseModel):
    ts: float
    type: str
    tool: Optional[str] = None
    call_id: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    run_id: Optional[str] = None


class TraceValidateIn(BaseModel):
    jsonl: str


class TraceValidateOut(BaseModel):
    ok: bool
    errors: List[str]


@router.post("/runs", response_model=RunOut)
def create_run(body: RunCreate) -> RunOut:
    run = STORE.create_run(config=body.config, task=body.task)
    simulate_run(run)
    return RunOut(run_id=run.run_id, created_at=run.created_at, config=run.config, task=run.task)


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: str) -> RunOut:
    if not STORE.has_run(run_id):
        raise HTTPException(status_code=404, detail="run not found")
    run = STORE.get_run(run_id)
    return RunOut(run_id=run.run_id, created_at=run.created_at, config=run.config, task=run.task)


@router.get("/runs/{run_id}/events", response_model=List[EventOut])
def list_events(run_id: str) -> List[EventOut]:
    if not STORE.has_run(run_id):
        raise HTTPException(status_code=404, detail="run not found")
    run = STORE.get_run(run_id)
    return [EventOut(**e) for e in run.events]


@router.post("/runs/{run_id}/replay", response_model=List[EventOut])
def replay(run_id: str) -> List[EventOut]:
    if not STORE.has_run(run_id):
        raise HTTPException(status_code=404, detail="run not found")
    run = STORE.get_run(run_id)
    # Deterministic for our simulated runner.
    simulate_run(run)
    return [EventOut(**e) for e in run.events]


@router.post("/traces/validate", response_model=TraceValidateOut)
def validate_trace(body: TraceValidateIn) -> TraceValidateOut:
    ok, errors = validate_trace_jsonl(body.jsonl)
    return TraceValidateOut(ok=ok, errors=errors)
