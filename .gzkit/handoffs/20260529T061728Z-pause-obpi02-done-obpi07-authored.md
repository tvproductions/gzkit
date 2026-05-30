---
mode: CREATE
adr_id: ADR-0.0.63
branch: main
timestamp: "2026-05-29T06:17:28Z"
agent: claude-code
obpi_id: OBPI-0.0.63-07
session_id: salvation-phase-i-adr-0.0.63
continues_from:
---

<!-- Full identifiers: parent ADR package ADR-0.0.63-closeout-ceremony-runtime-engine-parity ;
     OBPI OBPI-0.0.63-07-verify-stage-command-shape-gate. Frontmatter uses the short canonical
     forms the HandoffFrontmatter model requires (ADR-X.Y.Z / OBPI-X.Y.Z-NN). -->

## Current State Summary

Executing the June 2026 Road-to-Salvation Phase I by implementing **all of ADR-0.0.63** (closeout-ceremony-runtime-engine-parity — the promoted-but-stalled #517 5-alarm ADR), operator-directed "full ADR now". Paused for context-window budget after **1 of 7 OBPIs landed**.

Progress:
- **ADR-0.0.63 made implementation-ready** (committed + pushed): persona filled; OBPI-0.0.63-07 added (Checklist + Target Scope + brief); Non-Goal #5 amended to carve out the #550 gate; Decomposition Scorecard 6→7; new `## Boundary Invariants` section (BI-1 shell-less executability, BI-2 single-runtime ledger parity, BI-3 Gate-5 no-self-advance).
- **OBPI-0.0.63-02 (demo-and-arb-receipt-discipline): COMPLETE — attested_completed, committed, pushed.** Closes GHI #539 + #540 at the function layer. Shipped `src/gzkit/brief_commands.py` (the BI-1 shared spine) + refactored `ceremony_data._commands_from_demo_sections` to delegate. 14 tests GREEN, lint/ty/mkdocs clean, no regression. Attested by g0 (agent-relayed under active pipeline marker, GHI #292); REQ-05 accepted-uncovered as STRUCTURAL-FENCE.
- **OBPI-0.0.63-07 (verify-stage-command-shape-gate): brief authored + `gz obpi validate --authored` PASS.** NOT implemented. Two empty RED-first test stubs created. **These changes are UNCOMMITTED on the working tree** (the authored brief is a modification over the committed scaffold; the two stubs are untracked).

Last action succeeded: `gz obpi validate --authored` on OBPI-07 returned PASS.

## Important Context

- **Use the skills, do not improvise the pipeline.** Operator corrected an earlier improvisation: author briefs via the `gz-obpi-specify` skill, run implementation via the `gz-obpi-pipeline` skill, close the ADR via `gz-adr-closeout-ceremony`. Reading a SKILL.md ≠ invoking the skill.
- **BI-1 classifier already exists** in `src/gzkit/brief_commands.py`: `extract_fenced_commands`, `is_shell_less_executable`, `reexecute_demo`/`DemoReceipt`, `command_argv`. OBPI-07 and any future demo/verification work MUST consume it, never fork it.
- **`gz validate --commit-trailers` is HEAD-only + advisory** (documented drift in the `control-surface-rule-vs-check-drift` chore). `gz git-sync` emits `Ceremony:` commits with no `Task:` trailer, which the GHI #552 strict prose flags for src/tests scope. OBPI-02's src/tests landed in git-sync Ceremony commit `3467cbd` without a Task trailer (pushed; not fixable without force-push, which is forbidden).
- **`gz obpi complete` on heavy/foundation needs `--attestor-present`** (agent-relayed, gated on an active pipeline marker, GHI #292) when run headless and when using `--accept-uncovered`. STRUCTURAL-FENCE REQs are `covered=False` in `gz covers` by design → use `--accept-uncovered <REQ> --accept-uncovered-reason "..."`.
- **OBPI-06 is BLOCKED**: it consumes a `req_evidence:` field that does NOT exist in `src/gzkit/schemas/obpi_brief_structure.json`; the owning `ADR-pool.obpi-authoring-mechanical-floor` is still `Pool`. Operator-approved resolution: land a minimal `req_evidence` schema field within OBPI-06 itself and consume it; flag the pool-ADR relationship for later narrowing.
- **ADR's absorbed-findings line numbers are stale** (cited 2026-05-26): re-anchor every brief's line citations against current code (e.g. F2's `ceremony_data.py:288` is now `discover_demo_commands`, not the ARB path).
- **`_extract_gz_verb_chain` (ceremony_data.py) has a distinct demo-loss bug** (captures positional args into the verb chain → drops `gz <verb> <ID>` demos). Tracked in `.gzkit/insights/agent-insights.jsonl`; kept OUT of OBPI-02 scope; route separately at closeout.

## Decisions Made

- **Decision:** Implement the entire ADR-0.0.63 (7 OBPIs) rather than a tight Phase-I cut.
  **Rationale:** Operator chose "Full ADR-0.0.63 now" after being shown the magnitude (briefs are scaffolds; multi-session).
  **Alternatives rejected:** tight cut (OBPI-02+07 only); fresh narrow ADR (would duplicate the stalled 0.0.63).
- **Decision:** New shared module `src/gzkit/brief_commands.py` (BI-1 spine) rather than adding to `ceremony_data.py`.
  **Rationale:** `ceremony_data.py` was at 544/600 lines (pythonic cap) and BI-1 mandates one shared classifier consumed by OBPI-02 (demo) and OBPI-07 (verify).
  **Alternatives rejected:** inline in `ceremony_data.py` (breaches module cap, not shareable).
- **Decision:** demos ≠ receipts — OBPI-02 re-executes `## Demo` commands (ADR Decision #2) while presenter posture is preserved for already-attested quality receipts (ADR Non-Goal #1).
  **Rationale:** reconciles the ADR's internal Decision#2-vs-Non-Goal#1 tension; recorded in the OBPI-02 brief.
- **Decision:** Pre-commit src/tests with a proper `Task:` trailer BEFORE Stage 5 git-sync for the remaining 6 OBPIs.
  **Rationale:** operator chose this so HEAD stays strict-compliant; git-sync then ceremony-commits only non-src/tests artifacts.
  **Alternatives rejected:** follow skill git-sync as-is (accepts advisory drift); file GHI + pre-commit.
- **Decision:** OBPI-02 closeout-walkthrough WIRING deferred to OBPI-01 (which owns `closeout_ceremony.py`).
  **Rationale:** avoids churning a file OBPI-01 rewrites; end-to-end audited at closeout via BI-1.

## Immediate Next Steps

1. **Commit the uncommitted OBPI-07 brief + stubs** (operator was asked to hold; confirm first). The authored brief `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-07-verify-stage-command-shape-gate.md` and stubs `tests/governance/test_brief_command_shape.py`, `tests/commands/test_obpi_stages.py` are on the working tree.
2. **Run `/gz-plan-audit OBPI-0.0.63-07`** to author the plan file + PASS receipt (Plan-Mode Gate prerequisite).
3. **Invoke the `gz-obpi-pipeline` skill for OBPI-0.0.63-07** (`--no-subagents` optional). Implement RED→GREEN: new `audit_brief_command_shape` in `src/gzkit/governance/trust_audits/briefs.py`; register `--brief-command-shape` flag in `src/gzkit/cli/parser_maintenance.py`; dispatch in `src/gzkit/commands/validate_cmd.py`; verify-stage classification in `src/gzkit/commands/obpi_stages.py`; `## Verification` authoring guidance in `.gzkit/templates/obpi.md` (then `gz agent sync control-surfaces`). All consume `brief_commands.is_shell_less_executable` (BI-1).
4. **At Stage 5:** pre-commit src/tests with `Task: TASK-0.0.63-07-NN-MM-PP` trailer, then `gz git-sync --apply`; complete with `--attestor-present` (heavy lane → Gate 5 human attestation required).
5. **Then proceed in order:** OBPI-01 (state machine, owns `closeout_ceremony.py`; wire OBPI-02's demo-receipt binding here) → 03 (proof-binding validator) → 05 (dual-runtime collapse) → 06 (req-evidence schema — resolve blocker) → 04 (wording fix). Finally `gz-adr-closeout-ceremony` for ADR-0.0.63.

## Pending Work / Open Loops

- **6 OBPIs remain:** 07 (brief done, code pending), 01, 03, 05, 06 (blocked on req_evidence schema), 04.
- **OBPI-06 schema blocker** — see Important Context; resolve by landing minimal `req_evidence` field in OBPI-06.
- **Pre-existing repo-wide `gz check` failure (NOT this ADR):** `ADR-0.0.64`'s `OBPI-0.0.64-05` SUPPORT REQ `REQ-0.0.64-05-06` lacks a `gz validate --<scope>` citation → `gz validate --req-kind-discipline` fails. Will block ADR-0.0.63 closeout's quality pipeline. Logged in `agent-insights.jsonl`. Needs the 0.0.64 owner or a GHI; do NOT blind-fix.
- **`_extract_gz_verb_chain` positional-capture demo-loss bug** — tracked; route at closeout (follow-on REQ or GHI).
- **Stale plan-audit receipt** for `OBPI-0.0.64-05` was the active marker before this work; superseded.
- **GHIs to close at ADR-0.0.63 closeout:** #539, #540 (OBPI-02), #550 (OBPI-07), and #516 (relabel/close per OBPI-01/03).

## Verification Checklist

- [ ] Branch matches: `git branch --show-current` returns `main`
- [ ] `uv run gz adr status ADR-0.0.63-closeout-ceremony-runtime-engine-parity` shows OBPI-02 `attested_completed`/`completed`, others `pending`/`draft`
- [ ] `uv run -m unittest tests.test_brief_commands tests.test_ceremony_demo_discovery` → 14 pass (OBPI-02 landed code)
- [ ] `uv run gz obpi validate --authored docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-07-verify-stage-command-shape-gate.md` → PASS
- [ ] `git status --short` shows uncommitted OBPI-07 brief + the two test stubs (resolve per Immediate Next Step 1)
- [ ] `python -c "from gzkit.brief_commands import is_shell_less_executable"` imports cleanly (BI-1 spine present)

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md` — amended ADR (persona, OBPI-07, Non-Goal #5, Boundary Invariants)
- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-02-demo-and-arb-receipt-discipline.md` — completed brief (status: Completed)
- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-07-verify-stage-command-shape-gate.md` — authored brief (uncommitted)
- `src/gzkit/brief_commands.py` — BI-1 shared classifier spine (OBPI-02)
- `src/gzkit/commands/ceremony_data.py` — `_commands_from_demo_sections` delegates to the spine
- `tests/test_brief_commands.py`, `tests/test_ceremony_demo_discovery.py` — OBPI-02 tests (14 pass)
- `tests/fixtures/ceremony_demos/multiline_demo.md` — OBPI-02 fixture
- `tests/governance/test_brief_command_shape.py`, `tests/commands/test_obpi_stages.py` — empty RED stubs for OBPI-07 (uncommitted)
- `.claude/plans/demo-and-arb-receipt-discipline-OBPI-0.0.63-02.md` — OBPI-02 heavy-lane plan
- `.gzkit/insights/agent-insights.jsonl` — tracked defects + course-corrections this session

## Environment State

Python 3.13 / uv. Model for this work: Opus 4.8 (NOT the Haiku that the `/git-sync` skill pins — Phase-I engineering needs Opus per the Road-to-Salvation plan). The `gz-obpi-specify` skill frontmatter is `model: opus`. No feature branch — work lands on `main` via `gz git-sync`.
