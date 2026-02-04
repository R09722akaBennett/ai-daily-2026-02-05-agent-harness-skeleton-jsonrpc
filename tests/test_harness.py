from fastapi.testclient import TestClient

from app.main import build_app


def test_create_run_and_events() -> None:
    client = TestClient(build_app())
    r = client.post("/api/v1/runs", json={"config": {"seed": 1}, "task": {"input": "hi"}})
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    ev = client.get(f"/api/v1/runs/{run_id}/events")
    assert ev.status_code == 200
    events = ev.json()
    assert events[0]["type"] == "run_started"
    assert any(e["type"] == "tool_call" for e in events)
    assert any(e["type"] == "tool_result" for e in events)


def test_trace_validate_missing_result() -> None:
    client = TestClient(build_app())
    bad = '{"ts":0,"type":"tool_call","tool":"x","call_id":"c1","args":{}}\n'
    r = client.post("/api/v1/traces/validate", json={"jsonl": bad})
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert "missing tool_result" in "\n".join(r.json()["errors"])
