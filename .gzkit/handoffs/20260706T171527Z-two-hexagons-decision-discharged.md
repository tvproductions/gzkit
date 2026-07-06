---
mode: CREATE
adr_id: ADR-0.0.3
branch: main
timestamp: "2026-07-06T17:15:27Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: ba01f1e9
session_id:
continues_from: .gzkit/handoffs/20260706T161520Z-hexagonal-enshrinement-and-two-hexagons-finding.md
---

<!-- Handoff: the two-hexagons decision is discharged; campaign amendment appended. -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

The prior handoff's single **owed decision — the two-hexagons conformance gap —
is discharged.** The operator ruled decision **(b)**: bless gzkit's
parameter-injection seam as its canonical hexagon and retire the dormant
`ports/`+`adapters/`+`tests/fakes/` facade. That landed as a direct-fix
correction under **ADR-0.0.3**, commit `ba01f1e9`
(`fix(hexagonal): retire dormant ports/adapters facade; bless injection seam`),
already on `main` and level with `origin/main`.

The correction deleted ~1,064 lines: `src/gzkit/ports/` (4 Protocols),
`src/gzkit/adapters/` (`FileConfigStore`), `tests/fakes/` (4 fakes),
`tests/test_ports.py`, `tests/test_fakes.py`. It reframed
`tests/policy/test_import_boundaries.py` to the real **core-purity** wall (core
imports no `cli`/`adapters`/`rich`/`argparse`) and dropped the
configurator-contradicting commands-adapter guard, and trimmed
`tests/test_load_config.py` to the real `load_config(path=)` seam. Supersession
callouts were stamped on OBPI-0.0.3-01/-04/-05/-09 and an ADR-0.0.3 banner; the
resolution is recorded in `docs/governance/hexagonal-architecture.md` canon.
Verification at commit time: `unittest` 6747 OK; ruff/ty clean; `gz validate` 6
scopes pass; `mkdocs --strict` clean.

This session then **updated the two requested artifacts**: (1) this handoff, and
(2) the Build-to-1.0 campaign — a dated 2026-07-06 § Amendments entry recording
the hexagonal-as-primary-directive ruling and the facade retirement (operator
chose "Append § Amendments entry"; no Movement checkbox changed state, so the
Queue body and the `> Topmost` note were deliberately left untouched).

Working tree is clean.

## Important Context

- **The retirement is a *correction*, not a retreat from hexagonal.** Per the
  operator's correction-vs-enhancement doctrine, the shipped ports facade did not
  fulfil its declared intent (zero production wiring, zero domain-test injection
  after ADR-0.0.3 closed at Gate 5), so closing the gap is corrective work homed
  under the owning ADR-0.0.3 — never a fresh ADR. A port ABC over a single/zero
  impl beside a working self-contained seam is exactly the speculative generality
  the newly-enshrined `.gzkit/rules/hexagonal-architecture.md` forbids
  (*"encapsulate first; formalize the port only when the second adapter is
  real"*).
- **What was NOT done, on purpose.** The correction removed the *wrong-shaped,
  dormant* facade (`src/gzkit/adapters/` happened to sit *inside* the app
  package); it neither relocates nor builds any adapter and enshrines **no folder
  mandate.** Cockburn's "adapters live outside the core" folder discipline
  (`domain`/`application`/`adapters`/`api` zoning enforced by import direction) is
  the intended direction but is **dedicated ADR work** — deferred to the new pool
  ADR because "gzkit + adopters not yet ready" and it is "too big to rewire in a
  correction" (operator, 2026-07-06).
- **Campaign amendment protocol was honored.** The Build-to-1.0 file is Magna
  Carta; its own discipline warns inline accretion "killed the predecessor."
  Amendments append to § Amendments only, dated and operator-ratified — which is
  where the new entry went. No Queue checkbox moved because no Movement item
  changed state (this was foundation-rule + direct-fix correction, not a Queue
  item).
- **Forward spine is unchanged.** The campaign's topmost sequenced item remains
  **Movement III Phase 2 — HULL: graph substrate** (single feature ADR, "the
  gzkit ontology"), whose work-start is **operator-gated and not yet
  authorized.** The `provenance: INTENT | OBSERVED` keystone (landed last session
  under ADR-0.32.0) still awaits the push-domain OBSERVED edges before the
  seam-diff can compute.

## Decisions Made

- **Decision:** Bless parameter-injection as gzkit's canonical hexagon and retire
  the dormant ports/adapters/fakes facade — the two-hexagons decision (b).
  **Rationale:** the working hexagon is the injection seam (`project_root: Path`,
  738 sites; `Ledger(path)`; `load_config(path=)`, wired by the command-layer
  configurator, Cockburn Fig 2.1); the advertised ports layer was never
  load-bearing. **Alternatives rejected:** (a) wire the four dormant ports into
  production + domain tests — rejected as building out speculative generality the
  enshrined rule forbids.
- **Decision:** Defer the "adapters live outside the core" folder-structure
  realization to a new pool ADR (`ADR-pool.hexagonal-folder-structure-realization`).
  **Rationale:** operator ruled it too large to fold into a correction, and
  neither gzkit nor adopter projects are ready. **Alternatives rejected:**
  attempting the `domain`/`application`/`adapters`/`api` folder rewire inside this
  correction.
- **Decision:** Record the ruling in the campaign as a dated § Amendments entry,
  touching no checkboxes. **Rationale:** operator-selected ("Append § Amendments
  entry"); the work changed no Movement item's state, and the campaign's
  anti-accretion discipline confines operator-ratified rulings to § Amendments.
  **Alternatives rejected:** "no campaign change" and "amendment + refresh Topmost
  note" — the operator picked the amendment-only option.

## Immediate Next Steps

1. **Confirm nothing else is owed on the hexagonal correction.** The decision is
   discharged and committed; if the operator considers the two-hexagons thread
   closed, no further action is needed here.
2. **When forward work resumes, the topmost gated item is Movement III Phase 2 —
   HULL: graph substrate** (single feature ADR). Work-start is operator-gated;
   present it and await explicit authorization before authoring the ADR (per the
   campaign's operator-gated-work-start rule and the resume contract).
3. **The deferred folder-structure realization lives at
   `docs/design/adr/pool/ADR-pool.hexagonal-folder-structure-realization.md`** — a
   pool (backlog) item, not runtime-track; do not promote it into active work
   absent an operator pull (Architectural Boundary #1/#2).

## Pending Work / Open Loops

- **Movement III Phase 2 (HULL), Phase 3 (HATCH), deferred Phase 4 (RECALL)** —
  the campaign's remaining forward-airlock constellation; Phase 2 work-start not
  yet authorized.
- **ADR-0.32.0 deferred-breadth OBPIs 05/06/07** (OKF absorption, work-domain L2
  schema, source tree-sitter) — pending, operator-gated work-start; the seam-diff
  on the `provenance` field needs the push-domain OBSERVED edges from 06/07.
- **`ADR-pool.hexagonal-folder-structure-realization`** — pool backlog; the
  eventual adapters-outside-the-core folder discipline. Not scheduled.
- **AGENTS.md > 32768 B still truncates under Codex at runtime** (GHI #533) — the
  budget-guard rename last session decoupled gzkit's guard, not Codex's behavior;
  durable fix remains corpus-split.

## Verification Checklist

- [ ] `git rev-parse --short HEAD` resolves to `ba01f1e9` (or the operator
  explains drift); branch `main`, `origin/main` level.
- [ ] `git status --short` is clean.
- [ ] `test -d src/gzkit/ports` returns non-zero (the facade is gone); same for
  `src/gzkit/adapters` and `tests/fakes`.
- [ ] `uv run -m unittest -q` passes (6747 at correction commit).
- [ ] `docs/governance/build-to-1.0-campaign-2026-06-30.md` § Amendments carries
  the dated 2026-07-06 hexagonal entry, and no Movement checkbox in § 7 changed.

## Evidence / Artifacts

- `docs/design/adr/pool/ADR-pool.hexagonal-folder-structure-realization.md` — the
  deferred folder-structure realization (new pool ADR from the correction).
- `docs/governance/hexagonal-architecture.md` — canon updated with the resolved
  conformance ruling ("the injection seam IS the canonical hexagon") + retired-facade note.
- `.gzkit/rules/hexagonal-architecture.md` — the binding per-turn primary
  code-architecture directive (enshrined prior session).
- `docs/governance/build-to-1.0-campaign-2026-06-30.md` — campaign with the new
  § Amendments entry appended this session.
- `tests/policy/test_import_boundaries.py` — reframed to the real core-purity AST wall.
- `tests/test_load_config.py` — trimmed to the real `load_config(path=)` seam.
- `src/gzkit/ontology/model.py` — the `provenance` field keystone (prior session; unchanged here).
- `.gzkit/handoffs/20260706T161520Z-hexagonal-enshrinement-and-two-hexagons-finding.md` — predecessor handoff (`continues_from`).
