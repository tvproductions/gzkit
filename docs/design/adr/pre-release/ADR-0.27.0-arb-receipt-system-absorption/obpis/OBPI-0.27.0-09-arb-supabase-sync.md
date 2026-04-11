---
id: OBPI-0.27.0-09-arb-telemetry-sync
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 9
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-09: ARB Telemetry Sync (Logfire)

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-09 — "Implement configurable ARB receipt retention via Pydantic Logfire — replaces opsdev Supabase sync"`

## OBJECTIVE

Replace the opsdev Supabase sync approach (`arb/supabase_sync.py`, 157 lines) with a configurable retention backend using Pydantic Logfire as the default provider. The core problem both modules solve is the same: the local ledger (`ledger.jsonl`) is ephemeral to the repository clone — it has no cross-session queryability, no cross-environment visibility, and no long-term retention beyond what git history provides. The opsdev module solved this with Supabase row insertion, coupling gzkit to a specific database backend with schema migration overhead. Logfire solves the same retention problem through OpenTelemetry span export: ARB receipt events are durably retained, queryable via SQL explorer, and visible across sessions and environments — without maintaining tables, migrations, or sync retry logic. The integration must be configurable — Logfire is the default backend, but the design must allow alternative OTel-compatible backends and must degrade gracefully when no backend is configured.

## SOURCE MATERIAL

- **opsdev (superseded):** `../opsdev/src/opsdev/arb/supabase_sync.py` (157 lines) — Supabase receipt row insertion
- **Replacement technology:** [Pydantic Logfire](https://pydantic.dev/docs/logfire/get-started/) — observability platform built on OpenTelemetry with native Pydantic and structlog integration
- **gzkit existing:** structlog with correlation IDs (`src/gzkit/cli/logging.py`), ledger event system (`src/gzkit/events.py`)

## ASSUMPTIONS

- Logfire is an optional dependency — gzkit must function fully without it installed
- The ledger (`ledger.jsonl`) remains the L2 source of truth; Logfire is the L3 retention layer — a durable, queryable copy of receipt events that survives beyond the local clone
- gzkit's existing structlog infrastructure bridges naturally to Logfire's structlog integration
- `LOGFIRE_TOKEN` environment variable provides authentication; no token means retention sync is silently disabled
- The Logfire free tier (10M spans/month) is sufficient for governance receipt volume — a full pipeline run produces ~10-20 spans

## NON-GOALS

- Migrating existing ledger data to Logfire — Logfire captures forward-looking telemetry only
- Building a generic telemetry abstraction framework — use OpenTelemetry directly, configure via Logfire SDK
- Real-time alerting or dashboard design — those are platform-side concerns, not gzkit code
- Replacing structlog — Logfire augments structlog, it does not replace it

## REQUIREMENTS (FAIL-CLOSED)

1. Add `logfire` as an optional dependency (`uv add logfire --optional telemetry`)
1. Implement `src/gzkit/arb/telemetry.py` — configurable telemetry emitter with Logfire as default backend
1. Configuration: enable/disable via `gzkit.toml` or environment variable (`GZKIT_TELEMETRY_ENABLED=true/false`), backend selection, graceful no-op when Logfire is not installed
1. Instrument ARB step execution with Logfire spans (`logfire.span("arb.step", ...)`) so QA steps appear as traced operations
1. Bridge existing structlog loggers to Logfire so `logger.info(...)` calls flow to the platform when enabled
1. Emit receipt events (lint findings, step results, gate outcomes) as structured span attributes
1. All telemetry code must be guarded — `ImportError` for missing `logfire` package produces a no-op emitter, not a crash
1. Unit tests with mocked Logfire SDK — no real network calls in tests
1. Document configuration in command docs and runbook

## DESIGN NOTES

### State Doctrine Alignment

| Layer | Role | Telemetry impact |
|-------|------|-----------------|
| L1 (Canon) | Governance artifacts | No change — Logfire never writes to L1 |
| L2 (Ledger) | Event log — source of truth | No change — ledger remains authoritative |
| L3 (Derived) | Caches, views, indexes | **Logfire is L3** — a queryable view derived from L2 events, fully rebuildable |

### Configuration Model

```toml
# gzkit.toml (optional section)
[telemetry]
enabled = true          # default: false
backend = "logfire"     # default: "logfire" (only supported backend initially)
```

Environment overrides: `GZKIT_TELEMETRY_ENABLED`, `LOGFIRE_TOKEN`.

### Graceful Degradation

```python
try:
    import logfire
except ImportError:
    logfire = None  # telemetry silently disabled
```

## ALLOWED PATHS

- `src/gzkit/arb/telemetry.py` — telemetry emitter module
- `src/gzkit/arb/__init__.py` — exports
- `src/gzkit/cli/` — Logfire configuration at CLI startup
- `tests/` — tests for telemetry module
- `config/` — configuration schema additions
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs
- `pyproject.toml` — optional dependency group

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes; telemetry tests use mocked SDK
- [ ] Gate 3 (Docs): Configuration documented; runbook updated
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
