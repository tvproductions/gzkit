---
paths:
  - "src/airlineops/warehouse/**"
---

# Warehouse — Guardrails
Status: Active
Last reviewed: 2026-02-04

## Subsystem Covenant (ADR-0.0.3)

**Warehouse executes active manifests and owns artifact lifecycle; it is contract-naive.**

### Responsibilities

- Execute active manifests (acquired from registrar via `warehouse manifest create`)
- Acquire artifacts (download ZIPs, cache HTTP, check local sources)
- Ingest staged data from artifacts into SQLite
- Promote staged rows to production tables
- Manage ledgers (append-only audit trail per period)
- Enforce sliding window purge when periods become stale (via `warehouse maintain tidy`)
- Update manifest fulfillment records

### Prohibited (Import Covenant)

- **MUST NOT** import from `src/airlineops/librarian/` (no contract generation or discovery)
- **MUST NOT** generate, validate, or register contracts
- **MUST NOT** read external catalogs or perform discovery operations
- **MUST NOT** call discovery or contract composition functions

**Enforcement:** `tests/policy/test_subsystem_import_boundaries.py::test_warehouse_does_not_import_librarian`

## Artifact Lifecycle Ownership (Warehouse Custody)

| Artifact               | Location                                                | Lifecycle                                | Retention                                                                                                                          |
| ---------------------- | ------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Manifests**          | `artifacts/manifests/<dataset>.manifest.json`           | Active = registered with registrar       | Keep indefinitely while active; delete when superseded                                                                             |
| **Ledgers**            | `artifacts/ledgers/ingest/ingest_events.<period>.jsonl` | Append-only audit trail per period       | Keep while period in-window; prune when stale via `warehouse maintain tidy`                                                        |
| **Downloaded ZIPs**    | `artifacts/downloads/<dataset>/<filename>.zip`          | Source archives for periods in manifest  | Retained for now; manifest is keep-list but auto-prune deferred until attic/freezer ADR; safe to re-download                       |
| **Validation Reports** | `artifacts/validation/*.json`                           | Generated during orchestrate/validate    | Prune monthly or per-cycle; no operational impact                                                                                  |
| **HTTP Cache**         | `artifacts/cache/`                                      | Playwright browser cache                 | Always safe to delete; will re-fetch on-demand                                                                                     |
| **Database**           | `artifacts/db/airlineops_public.sqlite`                 | **🔴 CRITICAL: WAREHOUSE MUST PRESERVE** | **Config-driven path. NEVER allow programmatic deletion. Only tidy staging/quarantine rows. Manifest-driven data retention only.** |
| **Ingest scratch**     | `artifacts/ingest/`                                     | Intermediate CSV/JSONL/Parquet outputs   | Retained for now; manifest-scoped cleanup deferred to attic/freezer ADR                                                            |

**Key principle:** The manifest is the explicit keep-list. Any artifact not listed in the active manifest is out-of-scope for retention. When the manifest changes and old periods fall out, warehouse removes corresponding ledgers. ZIP and ingest scratch pruning are deferred until the attic/freezer ADR formalizes their retention.

## General Guardrails

- **Flag defects, never excuse them.** If an adapter, config entry, boundary violation, or manifest is wrong — flag it as a defect. Never rationalize it as "pre-existing" or "not in scope". Fix it or file a GHI.
- **Python-only automation**; no shell scripts in pipelines/helpers.
- Determinism: stable schemas, fixed seeds, reproducible transforms.
- Respect frozen interfaces; refactors are **behavior-preserving** unless explicitly required.
- Write only to sanctioned paths (e.g., `artifacts/`, `data/`); avoid ad-hoc temp files.
- Evidence/proofs only when the brief calls for it.
- Keep changes small; prefer helpers over sweeping edits.


## Run

- `uv run ruff check . --fix && uv run ruff format .`
- `uv run -m unittest -v`
- Optional smoke (≤60s): `uv run -m opsdev lite`

## Verify

- Smoke ≤60s; no unsanctioned writes; deterministic outputs.
