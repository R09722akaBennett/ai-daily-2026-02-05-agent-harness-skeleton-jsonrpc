# Agent Harness Skeleton (JSON-RPC)
Slug: agent-harness-skeleton-jsonrpc

## Problem
Teams keep rebuilding the same agent “harness glue”: consistent run configs, tool calling, event streaming, trace capture, and replay. Without a minimal skeleton, agent experiments are hard to reproduce and debug.

## Users
- AI engineers building agentic workflows and needing a consistent local/CI harness
- DevTools teams plugging different models/providers into one runtime
- Researchers wanting replayable structured traces

## MVP
- Local-first harness that runs a simple agent loop with JSON-RPC 2.0 over stdio (simulated in-process for MVP)
- Trace event stream (JSONL) + artifacts folder
- Replay mode that rehydrates from trace (mock tool results)
- CLI-like endpoints: run, validate, replay

## Non-goals
- Not a full agent framework (planning/memory/etc)
- Not hosted

## API
- `POST /v1/runs` create a run (task + config)
- `GET /v1/runs/{id}` run metadata
- `GET /v1/runs/{id}/events` list events
- `POST /v1/runs/{id}/replay` replay from stored trace
- `POST /v1/traces/validate` validate a trace JSONL

## UI
- Streamlit: upload a trace, view timeline, run summary, and validate

## Acceptance criteria
- Can create a run and receive a streamed/collected event list
- Trace validator catches missing tool_result for tool_call
- Replay produces same action sequence when tool results are mocked

## Risks
- Determinism with model outputs; mitigate by focusing on tool replay + config capture

## Sources
- https://openai.com/index/unlocking-the-codex-harness
- https://news.smol.ai/issues/26-02-03-not-much/
