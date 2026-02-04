from __future__ import annotations

import os

import httpx
import streamlit as st

API_URL = os.getenv("UI_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Agent Harness Skeleton", layout="centered")

st.title("Agent Harness Skeleton (JSON-RPC-ish)")
st.caption("Local-first demo: create a run → view events → validate/replay a trace.")

with st.expander("Ping /health", expanded=False):
    if st.button("Ping /api/health"):
        with httpx.Client(base_url=API_URL, timeout=5.0) as client:
            r = client.get("/api/health")
            st.write(r.status_code)
            st.json(r.json())

st.subheader("Create run")
input_text = st.text_input("Task input", value="hello")

if st.button("Create run", type="primary"):
    with httpx.Client(base_url=API_URL, timeout=10.0) as client:
        r = client.post("/api/v1/runs", json={"config": {"seed": 1}, "task": {"input": input_text}})
        r.raise_for_status()
        st.session_state["run_id"] = r.json()["run_id"]

run_id = st.session_state.get("run_id")
if run_id:
    st.success(f"Run: {run_id}")
    with httpx.Client(base_url=API_URL, timeout=10.0) as client:
        ev = client.get(f"/api/v1/runs/{run_id}/events").json()
    st.write("Events")
    st.json(ev)

    if st.button("Replay"):
        with httpx.Client(base_url=API_URL, timeout=10.0) as client:
            ev = client.post(f"/api/v1/runs/{run_id}/replay").json()
        st.json(ev)

st.subheader("Validate trace JSONL")
default_jsonl = """{\"ts\": 0, \"type\": \"tool_call\", \"tool\": \"x\", \"call_id\": \"c1\", \"args\": {}}\n{\"ts\": 0, \"type\": \"tool_result\", \"tool\": \"x\", \"call_id\": \"c1\", \"result\": {}}\n"""
jsonl = st.text_area("Trace JSONL", value=default_jsonl, height=160)
if st.button("Validate"):
    with httpx.Client(base_url=API_URL, timeout=10.0) as client:
        r = client.post("/api/v1/traces/validate", json={"jsonl": jsonl})
        st.json(r.json())

st.caption(f"API: {API_URL}")
