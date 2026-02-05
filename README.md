# Agent Harness Skeleton (JSON-RPC-ish)

Small FastAPI + Streamlit service project.

## Overview
This repository contains a minimal but structured implementation focused on the core domain logic described below.

## Why
Codex-style harnesses are the *real* product surface: streaming progress, approvals, diffs, and replayable traces. This project gives a minimal harness + trace validator you can extend.

## What it does
- FastAPI backend (`/api/*`)
- Streamlit UI (`app/web/streamlit_app.py`)
- Minimal unit tests (pytest)

## Run locally
```bash
python -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e .

# API
uvicorn app.main:build_app --factory --host 0.0.0.0 --port 8000

# UI (in another shell)
streamlit run app/web/streamlit_app.py
```

## Sources
- https://openai.com/index/unlocking-the-codex-harness\n- https://news.smol.ai/issues/26-02-03-not-much/

## Roadmap
- Add SSE event streaming for live runs\n- Add pluggable tool sandbox + file diff artifact store\n- Add real JSON-RPC stdio protocol between harness and subprocess agent
