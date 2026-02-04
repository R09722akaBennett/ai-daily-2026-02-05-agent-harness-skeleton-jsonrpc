from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Run:
    run_id: str
    created_at: float
    config: Dict[str, Any]
    task: Dict[str, Any]
    events: List[Dict[str, Any]] = field(default_factory=list)


class InMemoryHarnessStore:
    def __init__(self) -> None:
        self._runs: Dict[str, Run] = {}

    def create_run(self, config: Dict[str, Any], task: Dict[str, Any]) -> Run:
        run_id = str(uuid.uuid4())
        run = Run(run_id=run_id, created_at=time.time(), config=config, task=task)
        self._runs[run_id] = run
        return run

    def get_run(self, run_id: str) -> Run:
        return self._runs[run_id]

    def has_run(self, run_id: str) -> bool:
        return run_id in self._runs


STORE = InMemoryHarnessStore()


def _ts() -> float:
    return time.time()


def simulate_run(run: Run) -> None:
    """A deterministic mini-run to demonstrate harness-like traces."""
    run.events.clear()
    run.events.append({"ts": _ts(), "type": "run_started", "run_id": run.run_id})

    # A fake tool call derived from task payload.
    tool_name = "echo"
    payload = run.task.get("input", "hello")
    call_id = "call_" + run.run_id.replace("-", "")[:12]

    run.events.append(
        {
            "ts": _ts(),
            "type": "tool_call",
            "tool": tool_name,
            "args": {"text": payload},
            "call_id": call_id,
        }
    )
    run.events.append(
        {
            "ts": _ts(),
            "type": "tool_result",
            "tool": tool_name,
            "result": {"text": payload, "length": len(str(payload))},
            "call_id": call_id,
        }
    )

    run.events.append({"ts": _ts(), "type": "run_finished", "run_id": run.run_id, "status": "ok"})


def validate_trace_jsonl(text: str) -> Tuple[bool, List[str]]:
    """Validates a minimal constraint: every tool_call has a matching tool_result by call_id."""
    errors: List[str] = []
    calls: Dict[str, Dict[str, Any]] = {}
    results: Dict[str, Dict[str, Any]] = {}

    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:  # noqa: BLE001
            errors.append(f"line {i}: invalid json: {e}")
            continue

        if not isinstance(obj, dict):
            errors.append(f"line {i}: event must be an object")
            continue

        et = obj.get("type")
        if et == "tool_call":
            cid = obj.get("call_id")
            if not cid:
                errors.append(f"line {i}: tool_call missing call_id")
            else:
                calls[str(cid)] = obj
        if et == "tool_result":
            cid = obj.get("call_id")
            if not cid:
                errors.append(f"line {i}: tool_result missing call_id")
            else:
                results[str(cid)] = obj

    for cid in calls:
        if cid not in results:
            errors.append(f"missing tool_result for call_id={cid}")

    return (len(errors) == 0), errors
