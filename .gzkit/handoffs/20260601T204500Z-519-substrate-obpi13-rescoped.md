---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-01T20:45:00Z"
agent: claude-code
obpi_id: OBPI-0.0.37-13
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.37 — created by claude-code at 2026-06-01T20:45:00Z -->

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

Session was return-to-health Tier-0 (restore green) followed by #519 / ADR-0.0.37
substrate diagnosis and re-scope. Outcomes:

- **Harness GREEN.** `uv run gz check` exits 0, 26/26 gates (Snapshot D), recorded
  in `docs/governance/return-to-health-plan-2026-05-30.md`. Captured with a
  file-redirect to read the true exit code (not a `| tail` pipe, which masked the
  earlier Snapshot-C failure as a false "exit 0").
- **Tree clean, synced to `origin/main` at `a2131975`.** Four commits this session:
  `eef2558c` (restore green: preflight cleanup + task-envelope ceremony-exclusion
  fix), `8867abc1` (plan register: re-home #563/#564 to Phase 3, register #578),
  `09eaccd7` (re-scope OBPI-0.0.37-13), `a2131975` (gz-sync chore of residual
  pipeline markers).
- **#519 is NOT fixed.** The CMS substrate was diagnosed hollow and the blocking
  OBPI-0.0.37-13 brief was re-scoped to a buildable spec. **Zero substrate code is
  written.** Codex surface is still ~32 KB.
- Last action: authoring this handoff. **No active OBPI lock** — the pipeline
  aborted at the Stage-1 plan-audit gate (verdict FAIL) before the lock-claim step,
  so there is nothing to release.

## Important Context

- **The substrate is hollow, proven.** `uv run gz content import AGENTS.md --as
  AgentContract` parses the 32,121-byte contract into a 161-byte model that
  re-renders to 52 bytes — a 99.84% loss. `_parse_agent_contract` in
  `src/gzkit/content/parse/markdown_parser.py` only reads `## Tech Stack` and
  `## Rules` sections and never populates `pillars`. This is the regression floor
  the re-scoped OBPI-13 must beat.
- **ADR-0.0.34 (Validated, 8/8) already shipped the base** reverse-parse, `gz
  content import`, and the migration registry. OBPI-0.0.37-13 was named identically
  to the shipped `OBPI-0.0.34-03-reverse-parse-migration`; the re-scope makes
  OBPI-13 *extend* (populate pillars + classification), not rebuild.
- **The diet (Phase 1) is already spent.** ADR-0.0.54 lifted AGENTS.md narrative,
  measured the binding-corpus floor at ~31k, and honestly retargeted the budget
  15k→32k — see the `_doc` field in `data/instructions_files_budget.json`. It
  deferred the <15k goal to ADR-0.0.37 registry-projection. No quick-win headroom
  remains in a second diet pass.
- **AGENTS.md is generated, not hand-authored.** `sync_agents_md` renders it from
  `src/gzkit/templates/AGENTS.md` (the 23 KB monolith) plus the `.gzkit/agents.local.md`
  splice. Editing AGENTS.md directly breaks the `invariant-coherence` /
  map-conformance gates — edit the template/source, run sync.
- **Classification source is the advisory scorecard** (`docs/governance/advisory-rules-audit.md`),
  which already scores each bullet Mechanical/Promotable/Judgment/Ambiguous. The
  import joins from it; it does not reverse-engineer classification from prose.
- **The render template emits no metadata by design.** `src/gzkit/content/templates/agentcontract/claude.md.j2`
  is a terse stub; classification/density/witness live model-side and drive
  temperature projection, not the human-readable prose.
- Predecessor thread: `.gzkit/handoffs/20260531T105641Z-canon-foundation-design-captured.md`
  (broader CMS/canon design capture). This session was a sibling: return-to-health
  plus #519 substrate diagnosis, not a direct resume of that handoff.
- `uv run gz git-sync --apply` auto-commits residual state (pipeline markers,
  plan-audit receipts) with a `(gz git-sync)` subject suffix — that is why
  `a2131975` exists after the brief commit.

## Decisions Made

- **Decision:** Restore green via a narrow validator ceremony-exclusion plus a
  `req_atomic:` brief exemption.
  **Rationale:** the flagged ledger event `:8460` is a `meta-receipt-bind` Gate-5
  ceremony event, not TASK labor; excluding it is honest classification, not gate
  weakening, and avoids a ledger hand-edit (Never #2).
  **Alternatives rejected:** moving `_TASK_ENVELOPE_ENFORCEMENT_EPOCH` forward
  (would hide genuine post-epoch defects); hand-editing the ledger (Never #2).
- **Decision:** Model is the source; AGENTS.md is a forward-rendered lossy human
  view; the lossless round-trip is model↔JSON.
  **Rationale:** clean prose cannot carry per-bullet classification, so a lossless
  prose round-trip is unsatisfiable; #519 needs forward render only.
  **Alternatives rejected:** lossless `parse(render(model))` on clean prose
  (impossible); annotated-markdown render (bloats and uglifies AGENTS.md).
- **Decision:** Fold template-growth into OBPI-13; treat model + template + parser
  as one irreducible unit (relax OBPI-13 Denied-Paths on those surfaces).
  **Rationale:** non-lossy population spans all three; the mutual Denied-Paths
  across OBPI-11/12/13 were the decomposition bug behind the hollowness.
  **Alternatives rejected:** a separate OBPI to re-open OBPI-12's template (adds
  ceremony without changing the work).
- **Decision:** Close Phase 1 (diet) as spent; commit to the Phase-2 substrate build.
  **Rationale:** ADR-0.0.54 already harvested the diet to the measured floor.
  **Alternatives rejected:** a second marginal diet pass dressed up as #519 relief.

## Immediate Next Steps

Advisory only — present to the operator and obtain authorization before executing.

1. **Re-plan-audit the re-scoped OBPI-13.** Author a concise implementation plan
   under `.claude/plans/`, then run `uv run gz plan audit OBPI-0.0.37-13`. Confirm
   the contradiction-FAIL is cleared. The path-overlap warnings on
   `src/gzkit/commands/content/` are expected shared-directory noise, not a blocker.
2. **Run the OBPI-13 build via the pipeline** (`/gz-obpi-pipeline OBPI-0.0.37-13`):
   extend `_parse_agent_contract` to populate `pillars` from every `##` section;
   join per-bullet `classification` from the advisory scorecard; grow
   `agentcontract/claude.md.j2` so a populated model renders the full clean contract;
   add the model↔JSON round-trip test in `tests/content/test_round_trip_agent_contract.py`;
   dissolve `.gzkit/agents.local.md` into model rows.
3. **TDD per REQ** (RED then GREEN), committing each GREEN increment. Foundation +
   heavy lane means Gate-5 human attestation is required at pipeline Stage 4 — the
   pipeline cannot self-close it.
4. **After OBPI-13, sequence the rest:** OBPI-0.0.37-14 (wire `sync_agents_md` to
   render from the model, retire the monolith, re-point `--invariant-coherence`),
   then OBPI-0.0.37-15 (per-vendor temperature so Codex renders `lite` — the #519
   byte payload), then OBPI-0.0.37-09 (registry-project the binding corpus toward
   <15k).

## Pending Work / Open Loops

- **#519 stays unrelieved until OBPI-0.0.37-15 lands** (Codex `lite`). OBPI-13 and
  14 are necessary but not the byte payload.
- **GHI #578** (preflight reaps expired locks without the token-block register
  entry) open, routed to Phase 3.
- **GHI #563 broader class fix** still open — this session only excluded ceremony
  events; the closeout pipeline should itself populate `task_id` on worklog events.
- **Model expressiveness risk:** `Pillar` carries only `bullets`; AGENTS.md has
  tables, numbered lists, and prose blocks. OBPI-13 may need a minimal block/table
  representation. Keep it bounded — grow the model to fit the corpus, not speculation.
- **ADR-0.0.37 vs ADR-0.0.34 overlap** — the re-scope clarifies OBPI-13 extends
  0.0.34-03, but the ADR-level decomposition (two competing migration philosophies:
  AgentContract substrate vs invariant registry) could use a reconciliation pass.

## Verification Checklist

- [ ] `uv run gz check` exits 0, 26/26 (Snapshot D holds) — capture the true exit
      code via file redirect, never `| tail`
- [ ] Branch is `main`: `git branch --show-current`
- [ ] Tree clean and synced: `git status --short --branch` shows no ahead/behind
- [ ] Re-scoped brief is coherent: read `OBPI-0.0.37-13-reverse-parse-migration.md`,
      confirm Requirements 1-6 and Acceptance Criteria REQ-01 through REQ-06 agree
- [ ] Reproduce the hollow-importer floor: `uv run gz content import AGENTS.md --as
      AgentContract` yields a name+purpose-only model (the 99.84% loss OBPI-13 beats)

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-13-reverse-parse-migration.md` — the re-scoped brief (commit `09eaccd7`)
- `docs/governance/return-to-health-plan-2026-05-30.md` — Snapshot D and the GHI register
- `src/gzkit/commands/validate_task_envelope.py` — the meta-receipt-bind ceremony-exclusion fix
- `tests/governance/test_task_envelope_coherence.py` — the two TDD tests pinning the carve-out
- `src/gzkit/content/parse/markdown_parser.py` — the parser to extend (populates no pillars today)
- `src/gzkit/content/models/agent_contract.py` — the AgentContract / Pillar / Bullet model
- `src/gzkit/content/templates/agentcontract/claude.md.j2` — the stub template to grow
- `src/gzkit/commands/content/import_.py` — the `gz content import` surface
- `data/instructions_files_budget.json` — the `_doc` documenting the diet compromise (15k→32k)
- `.gzkit/insights/agent-insights.jsonl` — the drive-don't-ask course-correction insight

## Environment State

Python 3.13 with uv on Windows. `uv run gz check` is multi-minute (the Test gate
dominates). The advisory spec-test-code drift (~1,739 findings) is non-blocking and
does not affect the exit code.
