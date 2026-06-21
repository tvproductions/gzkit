---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-21T20:58:05Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260621T150858Z-obpi-0-0-74-02-completed.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-21T20:58:05Z -->

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

ADR-0.0.74 (MX Mode — Maintenance Hangar; Draft, foundation, heavy) was amended
this session to realize the **leveled `GZ_<LEVEL>` severity substrate** — Build-to-1.0
Magna Carta Movement I item 1 ("ADR-0.0.74 BI#2 built for real"). **Phase A (the
ADR design edits) is COMPLETE, operator-approved ("looks good"), and UNCOMMITTED.**
Working tree is dirty: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
is modified, and `.gzkit/ledger.jsonl` carries the read-only validation events
emitted this session. Branch `main`, HEAD `20a2f9ff`, ahead=0 behind=0.

What landed in the ADR (Phase A): Decision items 2/3/9 reshaped (binary checkpoint
to leveled severity authority; gate5_invariants gains grader-gaming; staging flags
resolve via the leveled checkpoint) and **four new Decision items 11–14** (the
`GZ_<LEVEL>` Python-logging vocabulary, gates-as-T/F-sensors plus the disposition
matrix table, the proxy-reality distance detector, MX hardening); Boundary
Invariants BI#2 leveled, BI#3 gains grader-gaming, new BI#5 (floor membership bound
to a live §5 negative control); Checklist 9 to 13 active items; Decomposition
Scorecard Baseline 5 to 9 and Final Target 9 to 13; Alternatives gained 4 recorded
rejections. Validation green: `uv run gz validate --documents` PASS and
`uv run gz adr fidelity ADR-0.0.74-mx-mode-maintenance-hangar --check` PASS (2
assertions parse).

Phases B (OBPI briefs), C (Magna Carta amendment), and D (evaluate plus full
validate) are NOT started.

## Important Context

The amendment is the product of a multi-turn operator-led design dialogue this
session. The load-bearing frame a resuming agent needs:

- **V.I.B.E.S.** ("Velocity Increased, Bugs Expected Software") is the named
  failure class the whole substrate hunts — not a severity dimension, not a
  demotable facet. The **four airlocks** (Design | Build | MX | Chores) are the
  seams; V.I.B.E.S. is what leaks through them. Source: `docs/governance/work-phases-and-airlock.md`.
- **Tracer-bullet plus lateral-seams diagnosis:** the vertical stack
  (Constitution to PRD to ADR to OBPI to REQ to TASK) is the tracer bullet gzkit
  governs well; the lateral seams (the two-graph edges — couplings between
  artifacts) are where vibe coding reigns, because AIRLOCK-IN (the seam-map before
  work) is unbuilt while AIRLOCK-OUT catches drift only on the way out (the literal
  "caught post-hoc"). The `GZ_<LEVEL>` sensors must read lateral edges.
- **The substrate lands IN ADR-0.0.74, not a sibling ADR.** The campaign places it
  at "ADR-0.0.74 BI#2 built for real"; the 2026-06-20 taxonomy reset abolished the
  `foundation` kind, so the design-dialogue handoff's "sibling foundation ADR"
  (Option B) is doubly invalid. The campaign governs; the operator confirmed
  in-ADR placement.
- **The ladder choice owes a paired Magna Carta amendment** (Phase C): D1 picks
  Python `logging` over the campaign §3b kernel-0-7 ladder, on STDLIB-FIRST
  grounds. Until Phase C lands, the ADR (Python levels) and the campaign (kernel
  0-7) disagree on the ladder — a KNOWN, intended divergence to be reconciled by
  the amendment, NOT silent drift.
- **`gz specify` precondition:** the Checklist now lists 13 active items but only 9
  OBPI brief files exist; `gz specify` reads checklist count and requires it to
  match the Scorecard Final Target. The 4 new briefs (items 11–14) MUST be authored
  in Phase B to restore the Checklist-to-brief 1:1; until then any 1:1/count
  validation flags the gap (expected, not a defect).
- **OBPI-01 (marker) and OBPI-02 (checkpoint) are DONE and attested (g0).** The
  binary checkpoint is the honest base; the leveled layer is NEW work (OBPI-11/12).
  Do NOT reshape 01/02 — their attestations stand.
- The **Q&A Transcript** section of the ADR is the preserved 2026-06-20 interview
  (still reads 10 binary items); the living Decision/Checklist/BI are current.
  Historical-vs-current divergence, flagged, not drift.

## Decisions Made

- **Decision (D1):** `GZ_<LEVEL>` is backed by the Python `logging` ladder
  (CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10), grounding
  threshold effective severity `>= ERROR`, NOTICE 25 the agent-fidelity / V.I.B.E.S.
  drift rung.
  **Rationale:** STDLIB-FIRST (binding) — Python `logging` constants are stdlib and
  reused; the kernel 0-7 ladder is a re-invented convention with unused top rungs
  (YAGNI).
  **Alternatives rejected:** kernel/syslog 0-7 ladder (campaign §3b as originally
  ratified).

- **Decision (D2):** `grader-gaming` joins the `gate5_invariants` never-relax floor
  AND its live §5 negative control — the proxy-reality distance record ("a gate
  went green AND reality was later found wrong, here is the gate") — is scoped into
  this ADR.
  **Rationale:** the observability system is itself a grader; Opus 4.8 names
  grader-gaming the most concerning training trend; a grader-gaming that could go
  advisory in the hangar makes MX the safe place to vibe undetected. A floor member
  with no live detector is a facade member, which §5 forbids.
  **Alternatives rejected:** name grader-gaming on the floor with its detector
  deferred.

- **Decision (D3):** The "one disposition handler" IS the matrix —
  (design × build × vibes) diagnosis to `GZ_<LEVEL>` to route. Forward airlocks
  (Design, Build) are the diagnosis axes; maintenance airlocks (MX, Chores) are the
  routes; vibes is the fidelity axis. Level-keyed (the airlock is the route, not a
  second input).
  **Rationale:** the campaign mandates "one disposition handler (the level to
  AOG/advisory wire)"; the matrix is the diagnosis-to-level computation, the levels
  its output — not a competing structure (that conflation was caught and corrected
  mid-dialogue).
  **Alternatives rejected:** a (level × owning-airlock) 2-D matrix (re-expands the
  diagnosis the level compresses).

- **Decision:** The substrate lands in ADR-0.0.74 (BI#2 reshaped), not a sibling
  ADR.
  **Rationale:** the campaign places it there ("built for real"); the foundation
  kind is abolished, so a sibling foundation ADR is invalid.
  **Alternatives rejected:** sibling foundation ADR (design-dialogue Option B).

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before acting. -->

1. **Decide commit timing for Phase A.** The ADR edits are uncommitted on `main`.
   Committing Phase A alone leaves a transient Checklist-to-brief 1:1 gap (13 listed
   / 9 briefs); committing Phase A and B together is cleaner. Operator's call; work
   on `main` (no feature branch).
2. **Phase B — author the OBPI briefs.** Reshape DRAFT briefs OBPI-03
   (gate5_invariants plus grader-gaming, leveled), OBPI-05 (exit re-emits levels
   plus live exit negative-control), OBPI-09 (flags resolve via the leveled
   checkpoint). Then `uv run gz specify <slug> --parent ADR-0.0.74 --item 11|12|13|14
   --lane heavy` for the four new briefs and author each semantically (REQ kinds per
   ADR-0.0.59; ground every Allowed Path per the gz-obpi-specify Pre-Save
   Ground-Truth Check). Then `uv run gz obpi validate --adr ADR-0.0.74 --authored`
   and `uv run gz register-adrs ADR-0.0.74 --all` to restore the 1:1.
3. **Phase C — paired Magna Carta amendment.** Append to
   `docs/governance/build-to-1.0-campaign-2026-06-20.md` § Archive: campaign §3b
   kernel-0-7 to Python `logging` plus NOTICE (D1), recorded with the operator's
   verbatim ratification words.
4. **Phase D — quality gate.** Run `/gz-adr-evaluate ADR-0.0.74` (any dimension
   scoring 1 is revised) and full `uv run gz validate` plus `uv run gz check`.
5. **Then sync.** `uv run gz git-sync --apply --lint --test` once the unit is
   coherent (commit to `main`, no feature branch).

## Pending Work / Open Loops

- **ADR-0.0.74 is 2/13 complete** after the amendment (OBPI-01/02 done; 03–14
  remain, with 03/05/09 reshaped-but-still-DRAFT and 11–14 unauthored).
- **Phase B/C/D unstarted** (see Immediate Next Steps).
- **Checklist-to-brief 1:1 is intentionally broken** until Phase B authors briefs
  11–14 (13 listed / 9 on disk).
- **ADR-0.29.0-precise-auth still sits in the feature list**, not yet dropped to
  pool per the campaign's "free the 0.29.0 number for MX" plan — separate release
  bookkeeping, downstream of building the substrate.
- **Tracked defect (Magna Carta Movement II item 3):** `gz obpi precomplete`'s
  behave-coverage check in `src/gzkit/commands/obpi_precomplete.py` (around lines
  324–396) is not REQ-kind-aware, unlike `obpi_complete.py`. Clean GHI-tracked
  direct fix, awaiting operator go (moratorium on reflexive GHI-filing).
- **The enforcement-claim meta-validator** (Magna Carta Movement I item 3 — the
  general §5 mechanism) is its own work, not in this ADR; the proxy-reality detector
  (item 13) is grader-gaming's specific live negative control and must comply with §5.

## Verification Checklist

- [ ] `git status` shows `ADR-0.0.74-mx-mode-maintenance-hangar.md` modified (Phase A uncommitted)
- [ ] `git branch --show-current` is `main`
- [ ] `uv run gz validate --documents` passes
- [ ] `uv run gz adr fidelity ADR-0.0.74-mx-mode-maintenance-hangar --check` passes (2 assertions)
- [ ] `uv run gz adr status ADR-0.0.74 --json` shows OBPI-01/02 completed, 03–09 draft (11–14 not yet on disk)
- [ ] ADR Checklist lists 13 active items and Decomposition Scorecard Final Target is 13

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — the amended ADR (Phase A, uncommitted)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-03-mx-gate5-invariants.md` — a DRAFT brief to reshape in Phase B (the gate5_invariants plus grader-gaming model)
- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — the Magna Carta; § Archive receives the Phase C ladder amendment; §7 Movement I item 1 is this work
- `docs/governance/work-phases-and-airlock.md` — the airlock design (tracer-bullet plus lateral-seams; V.I.B.E.S. as the forbidden fifth cell)
- `.gzkit/handoffs/20260621T143820Z-vibes-observability-design.md` — predecessor: the V.I.B.E.S. design dialogue, Opus 4.8 findings, and the matrix's original capture
- `.gzkit/handoffs/20260620T180109Z-levels-mx-gzkit-lobotomy.md` — predecessor: the kernel-severity/MX decision and the control-review facade findings
- `src/gzkit/commands/obpi_precomplete.py` — site of the tracked stale-behave-check defect (around lines 324–396)

## Environment State

Platform win32; Python 3.13; `uv run` throughout. Branch `main` (operator
directive: no feature branches). HEAD `20a2f9ff`, ahead=0 behind=0. Working tree
dirty: the ADR-0.0.74 main doc (Phase A edits) plus `.gzkit/ledger.jsonl`
(read-only validation events appended this session). No OBPI lock was claimed this
session — the work was design ceremony via gz-design; this is a context-continuity
handoff, not a lock-release register entry.
