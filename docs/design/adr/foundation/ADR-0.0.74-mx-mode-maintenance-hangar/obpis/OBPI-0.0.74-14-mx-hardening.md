---
id: OBPI-0.0.74-14-mx-hardening
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 14
lane: Heavy
status: Completed
# req_atomic: each REQ is one coherent hardening guard authored in a single TDD
# increment inside the one src/gzkit/mx/hardening.py module — the TTL/max-open
# guard (01), the no-normal-release-while-open guard (02), the ledger debt-aging
# guard (03), the dangling-state detector (04), and the checkpoint-resolution
# boundary fence (05). None decomposes into parallel seq=02+ sub-tasks
# (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-14-01  # TTL / max-open on the hangar
  - REQ-0.0.74-14-02  # no normal release while MX is open
  - REQ-0.0.74-14-03  # ledger debt-aging — accrued advisory debt grows louder over time
  - REQ-0.0.74-14-04  # dangling-state detector — ledger open but marker missing
  - REQ-0.0.74-14-05  # STRUCTURAL-FENCE: each hardening guard resolves severity through the leveled checkpoint
---

# OBPI-0.0.74-14-mx-hardening: Mx Hardening

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #14 - "MX hardening — TTL/max-open on the hangar, no normal release while MX is open, ledger debt-aging (louder over time), dangling-state detector ("ledger open but marker missing"); each resolves through the leveled checkpoint; unit tests"

**Status:** Completed

## Objective

The four MX hardening guards land at `src/gzkit/mx/hardening.py`, each emitting a `GZ_<LEVEL>` resolved through the leveled checkpoint: (1) TTL / max-open — an MX session open past its TTL or beyond the max-open count is flagged; (2) no normal release while MX is open — a patch release / ADR closeout attempted with an open hangar is blocked; (3) ledger debt-aging — accrued advisory debt's effective level grows louder (rises) the longer it sits unaddressed; (4) dangling-state detector — an open session (`mx_session_opened` with no matching `mx_session_closed`) whose marker is missing on disk is detected. "Done" = `hardening.py` exposes the four guards, each resolving severity through the leveled checkpoint (no hand-set bool), and unit tests pin each guard's flagging behavior.

## Lane

**Heavy** - This OBPI ships runtime-contract surfaces — the hardening guards that bound the hangar (TTL, release-lockout, debt-aging, dangling-state) and resolve severity through the leveled checkpoint — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 14)
- `src/gzkit/mx/hardening.py` **CREATE** — the four hardening guards (TTL/max-open, no-normal-release-while-open, ledger debt-aging, dangling-state detector), each resolving severity through the leveled checkpoint
- `src/gzkit/mx/checkpoint.py` — the guards resolve their effective `GZ_<LEVEL>` through the checkpoint (consumer)
- `src/gzkit/mx/marker.py` — the no-release / dangling-state guards read marker presence (`is_active`) (consumer, read-only)
- `src/gzkit/mx/__init__.py` — the `gzkit.mx` package init imported by the guards and tests (consumer, read-only)
- `src/gzkit/commands/patch_release.py` — the patch-release funnel consults `hardening.normal_release_blocked()` and refuses while a marker is present (proof-of-wiring for the no-normal-release guard)
- `src/gzkit/commands/closeout.py` — the ADR-closeout (feature/minor release) funnel consults the same guard — the parallel normal-release path
- `tests/mx/test_hardening.py` **CREATE** — unit tests for each of the four guards, including the block exercised at the real release site
- `docs/user/manpages/patch-release.md` — document the MX-open release lockout (no normal release while a hangar is open; exit 3) — the coupled doc surface for the `gz patch release` behavior change (DO IT RIGHT 1a; allowlist amendment operator-ratified at plan approval 2026-06-27)
- `docs/user/manpages/closeout.md` — document the same lockout for `gz closeout` (the parallel minor-release funnel) — coupled doc surface (allowlist amendment operator-ratified at plan approval 2026-06-27)
- `docs/governance/governance_runbook.md` — one-line note on the release lockout (Gate 3 docs coherence; allowlist amendment operator-ratified at plan approval 2026-06-27)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-14-mx-hardening.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/hardening.py`
- `tests/mx/test_hardening.py`

## Denied Paths

- Paths not listed in Allowed Paths
- A hand-set per-guard staging flag (a `_*_FAIL_CLOSED`-style bool) — each guard resolves severity through the leveled checkpoint, the very pattern OBPI-0.0.74-09 retired
- The `GZ_<LEVEL>` vocabulary (owned by OBPI-0.0.74-11) and the disposition handler (owned by OBPI-0.0.74-12)
- Editing ledger internals (`ledger.py`, `ledger_events.py`, …) — the debt-aging and dangling-state guards READ ledger events, they do not mutate the writer
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A TTL / max-open guard MUST flag an MX session open past its TTL or beyond the max-open count, emitting a `GZ_<LEVEL>` resolved through the leveled checkpoint (REQ-14-01).
1. REQUIREMENT: `hardening.normal_release_blocked()` MUST return a grounding `GZ_<LEVEL>` while a marker is present, AND the normal-release funnels (`gz patch release`, `gz closeout`) MUST consult it and refuse — the guard is wired at the release site, the hangar must be exited first (REQ-14-02).
1. REQUIREMENT: A ledger debt-aging guard MUST raise the effective level of accrued advisory debt the longer it sits unaddressed — debt grows louder over time, it does not stay silent (REQ-14-03).
1. REQUIREMENT: A dangling-state detector MUST flag an open session (`mx_session_opened` with no matching `mx_session_closed`) whose marker is missing on disk (REQ-14-04).
1. REQUIREMENT: Each hardening guard MUST resolve its effective severity through the leveled checkpoint — none hand-sets its own severity with a module-level bool (REQ-14-05).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the leveled checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-02) and the `GZ_<LEVEL>` vocabulary (`src/gzkit/mx/levels.py`, OBPI-11) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 14 — quoted verbatim:** "MX hardening. TTL / max-open on the hangar; no normal release while MX is open; ledger debt-aging (accrued advisory debt grows louder over time); a dangling-state detector ('ledger open but marker missing'). Each is a guard whose severity resolves through the leveled checkpoint."
- [ ] Parent ADR § Consequences/Negative #4 — the shakiest WWHTBT condition (exit is the only path that clears the marker); the dangling-state detector is its backstop.
- [ ] Parent ADR § Decision items 1, 2, 5 — the marker, the leveled checkpoint, and the exit gate these guards harden.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.claude/rules/token-block-discipline.md` § Binding Sub-Invariant 4 — the TTL / warn-then-reap discipline precedent for the hangar TTL guard

**Context:**

- [ ] `src/gzkit/mx/marker.py` (OBPI-01) — marker presence/absence and the `mx_session_opened` binding the dangling-state detector reads
- [ ] `src/gzkit/mx/checkpoint.py` (OBPI-02) + `src/gzkit/mx/levels.py` (OBPI-11) — the leveled checkpoint each guard resolves through
- [ ] The patch-release / closeout path that the no-normal-release guard gates

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/mx/checkpoint.py` exists (OBPI-0.0.74-02 has landed)
- [ ] `src/gzkit/mx/levels.py` exists (OBPI-0.0.74-11 has landed)
- [ ] `src/gzkit/mx/marker.py` exists (OBPI-0.0.74-01 has landed)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/mx/test_checkpoint.py` and `tests/mx/test_marker.py` reviewed for the local test convention before authoring `test_hardening.py`
- [ ] `src/gzkit/mx/checkpoint.py` reviewed for the effective-level resolution each hardening guard consumes

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/mx/hardening.py
test -f tests/mx/test_hardening.py
```

## Demo

```bash
# The four hardening guards (TTL/max-open, release-block, debt-aging, dangling-state)
# resolve severity through the leveled checkpoint. Pinned by tests/mx/test_hardening.py.
uv run gz check
```

## Acceptance Criteria

- [ ] REQ-0.0.74-14-01 [behavior]: Given an MX session open past its TTL (or beyond the max-open count), when the TTL/max-open guard runs, then it flags the session and emits a `GZ_<LEVEL>` resolved through the leveled checkpoint. (@covers test in `tests/mx/test_hardening.py`)
- [ ] REQ-0.0.74-14-02 [behavior]: Given an active marker, when a normal release is attempted via `gz patch release` or `gz closeout`, then the funnel consults `hardening.normal_release_blocked()` and refuses (non-zero exit) — the block is exercised at the real release site, not merely a standalone predicate. (@covers test in `tests/mx/test_hardening.py`)
- [ ] REQ-0.0.74-14-03 [behavior]: Given accrued advisory debt, when the debt-aging guard runs over time, then the effective level of unaddressed debt rises (grows louder) the longer it sits — it does not stay silent. (@covers test in `tests/mx/test_hardening.py`)
- [ ] REQ-0.0.74-14-04 [behavior]: Given an open session (`mx_session_opened` with no matching `mx_session_closed`) whose marker file is missing on disk, when the dangling-state detector runs, then it flags the dangling state. (@covers test in `tests/mx/test_hardening.py`)
- [ ] REQ-0.0.74-14-05 [structural-fence]: Each hardening guard resolves its effective severity through the leveled checkpoint — none hand-sets its own severity with a module-level bool (parent ADR § Boundary Invariants #2 — every fail-closed funnel/guard resolves its effective `GZ_<LEVEL>` through the shared checkpoint).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

Before: the hangar had no bound — a session could stay open indefinitely (guards advisory forever, the pre-mortem's "never leave the hangar"), a release could ship mid-repair, accrued advisory debt sat silent, and a hand-deleted marker left a dangling open session undetected. Now: four hardening guards bound the hangar — TTL/max-open caps how long it stays open, no-normal-release locks the door during repair, debt-aging makes silence louder over time, and the dangling-state detector catches "ledger open but marker missing" — each resolving severity through the one leveled checkpoint, no per-guard hand-set flag.

### Key Proof


$ python -c "from gzkit.mx import hardening; print(hardening.normal_release_blocked())"
# No marker:  blocked=False, emitted_level=10, route=<Route.TRACK>
# Marker up:  blocked=True,  emitted_level=50, route=<Route.AOG>, reason='an MX maintenance hangar is open; exit it (gz mx exit) before releasing'

The block is exercised at the real release sites (patch_release_cmd / closeout_cmd raise SystemExit(3)). Receipt arb-step-unittest-6d42f1f60e304c6da5181ab504cbbe7c (6578/6578); scoped arb-step-unittestscoped-10d7b1a6d36e498ba65843aac285c80c (16/16). Structural-fence negative control: breaking the TTL guard's emitted level fails the test (20 != 40), proving the fence is non-circular.

### Implementation Summary


- Decision item 14 (verbatim): "MX hardening. TTL / max-open on the hangar; no normal release while MX is open; ledger debt-aging (accrued advisory debt grows louder over time); a dangling-state detector ('ledger open but marker missing'). Each is a guard whose severity resolves through the leveled checkpoint."
- Files created: src/gzkit/mx/hardening.py (four guards + frozen Pydantic result models); tests/mx/test_hardening.py (16 tests across 5 classes)
- Files modified: src/gzkit/commands/patch_release.py and src/gzkit/commands/closeout.py (no-release guard wired at real funnels, exit 3); docs/user/manpages/patch-release.md, docs/user/manpages/closeout.md, docs/governance/governance_runbook.md (lockout documented)
- Tests added: 16 (TtlMaxOpen x4, NormalReleaseBlocked x4, DebtAging x3, DanglingState x3, StructuralFence x2)
- Date completed: 2026-06-27
- Attestation status: operator-verbatim "attest completed"
- Defects noted: Adversarial validation surfaced two test gaps (advisory-under-marker coverage; structural-fence circularity) — both fixed in-flight, negative-control verified, before attestation.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-14-mx-hardening: four MX hardening guards (TTL/max-open, no-normal-release wired at gz patch release + gz closeout with exit 3, ledger debt-aging, dangling-state detector) landed at src/gzkit/mx/hardening.py, each resolving severity through the leveled checkpoint (no hand-set bool, parent-ADR BI#2). 16/16 scoped tests (receipt arb-step-unittestscoped-10d7b1a6d36e498ba65843aac285c80c), 6578/6578 full suite (arb-step-unittest-6d42f1f60e304c6da5181ab504cbbe7c), lint/typecheck/mkdocs clean. Adversarial validation surfaced two test gaps (advisory-under-marker coverage; structural-fence circularity) — both fixed in-flight before attestation, structural fence negative-control verified (broken TTL level fails 20 != 40).
- Date: 2026-06-27

---

**Date Completed:** 2026-06-27

**Evidence Hash:** -
