---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-09-12T19:07:29Z'
agent: codex
continues_from: .gzkit/handoffs/20260912T181335Z-four-workflow-fronts.md
---

## Current State Summary

Applied interim Codex parity locally: three native hooks, canonical agent-role delivery, orientation/drift validation, and truthful skill previews. Codex recognizes all three hooks; native trust remains pending. No commit; existing dirty work preserved.

## Important Context

Four-front authority: docs/governance/build-to-1.0-campaign-2026-08-16.md, Workflow fronts. Handoff: carry this evidence. GHI triage: queue not re-triaged by this mission. Campaign: full parity remains ADR-pool.vendor-alignment-codex, formerly ADR-0.44.0; no parked OBPI initiated. R&D: lifecycle and transcript mappings require native evidence.

## Decisions Made

- [operator-ruled] special mission: get me codex parity. is there an adr for it? can you do best effort parity until we can get to that adr?
- [agent-chose] Repair retained delivery through canonical sync sources, preserve metadata and root contract, and distinguish hook registration from trusted dispatch.

## Immediate Next Steps

1. Review and trust the three project hook definitions using Codex /hooks.
2. Observe lifecycle context and shell-guard dispatch after native trust.
3. Review the local repair with the existing dirty work before the next operator-directed guarded git sync.

## Pending Work / Open Loops

Automatic lifecycle dispatch remains unobserved while native hooks are untrusted. Comprehensive hook/file-edit coverage, ExitPlanMode substitutes, and harness-neutral pipeline authority remain owned by the pool ADR. This handoff does not authorize that work.

## Verification Checklist

343 relevant unit tests, seven scoped validators, Ruff, type checks, and strict MkDocs passed. Native Codex delivered 48511 of 48511 root-contract bytes. Generated commands executed from src/: all exit 0; workflow fronts present; handoff context supplied; masked verifier returned native deny JSON.

## Evidence / Artifacts

- `docs/governance/codex-interim-parity-2026-09-12.md`
- `.codex/hooks.json`
- `.gzkit/agents/roles.json`
- `src/gzkit/hooks/codex.py`
- `src/gzkit/codex_roles.py`
- `tests/test_codex_hooks.py`
- `tests/test_codex_roles.py`
- `tests/test_sync_skill_capture.py`

## Settled Rulings

802 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
