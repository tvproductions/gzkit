# Plan: OBPI-0.0.23-03-sync-mirrors

## OBPI

`OBPI-0.0.23-03-sync-mirrors` — Sync vendor mirrors and verify the failure-mode rule loads correctly under each agent harness.

## Parent

`ADR-0.0.23-agent-failure-mode-taxonomy` (foundation kind, lite lane)

## Context

OBPI-0.0.23-01 authored `.gzkit/rules/agent-failure-modes.md` (canonical) and OBPI-0.0.23-02 cross-linked it from `AGENTS.md` § DO IT RIGHT and added a scorecard entry to `docs/governance/advisory-rules-audit.md`. Both are `Completed`. The OBPI-0.0.23-01 evidence already records that the project's `control-surface-sync` PostToolUse hook auto-generated the vendor mirrors during that brief's authoring pass:

- `.claude/rules/agent-failure-modes.md` (mtime 2026-04-30 03:02)
- `.github/instructions/agent_failure_modes.instructions.md` (mtime 2026-04-30 03:57)

OBPI-03 closes the loop by (a) running `gz agent sync control-surfaces` explicitly so a canonical sync run lands in this OBPI's evidence chain rather than as an authoring-time side effect, (b) confirming each mirror is byte-equivalent to the canonical modulo vendor-specific frontmatter rendering per `.claude/rules/skill-surface-sync.md` § Conflict resolution, and (c) gating completion on `gz validate --surfaces` exit 0.

### Current `gz validate --surfaces` baseline (pre-sync, 17 errors)

A clean-tree run reports drift across three classes:

1. **AGENTS.md generated-surface drift** (1) — `.gzkit/rules/AGENTS.md` is a sync-regenerated nested-AGENTS file. Currently shows 223 inserts vs HEAD because it was last touched in OBPI-01's PostToolUse hook run; running `gz agent sync control-surfaces` here will re-emit it deterministically and either no-op against HEAD or reproduce the same content (we will diff to confirm).
2. **Pre-existing `applyTo` field-required errors** (14) — every `.github/instructions/*.instructions.md` mirror is failing instruction-frontmatter schema validation (`Field required: applyTo`). This includes the new `agent_failure_modes.instructions.md` mirror but also 13 sibling mirrors (`adr_audit`, `brief_heading_conventions`, `chores`, `cli`, `cross_platform`, `gate5_runbook_code_covenant`, `gh_cli`, `governance_core`, `models`, `pythonic`, `skill_surface_sync`, `tests`, `tool_skill_runbook_alignment`). These are pre-existing and outside this brief's allowed paths.
3. **Rule-placement subtree warnings** (2) — `agent_failure_modes.instructions.md` and `skill_surface_sync.instructions.md` are flagged as "shared subtree rule for X has no nested AGENTS.md" for `docs/governance` and `.github/instructions` respectively. Investigate during execution; if root cause is an `applyTo` glob from the canonical rule's frontmatter expecting a nested AGENTS.md, that lands in scope; if it's a generator-side artifact, it lands outside scope.

The brief's REQ-3 (`gz validate --surfaces` exits 0) and STOP-on-BLOCKERS clause ("STOP if `gz validate --surfaces` reports drift after sync — escalate to operator before declaring completion") together mean: sync first, classify residual errors, escalate the out-of-scope class to the operator for routing before declaring the brief complete.

## Goal

1. Land a canonical, ledger-witnessed `gz agent sync control-surfaces` run inside this OBPI's evidence chain.
2. Confirm `.claude/rules/agent-failure-modes.md` and `.github/instructions/agent_failure_modes.instructions.md` are byte-equivalent to the canonical (modulo frontmatter rendering).
3. Drive `gz validate --surfaces` to exit 0 — or, if the residual drift is the pre-existing `applyTo` field-required class outside this brief's allowed paths, STOP per the brief clause, file a GHI for the out-of-scope class, surface to operator with explicit routing options before declaring completion.

## Files

### Sync command writes (in scope per brief allowed paths)

- `.claude/rules/agent-failure-modes.md` — Claude rule mirror (regenerated)
- `.github/instructions/agent_failure_modes.instructions.md` — GitHub instructions mirror (regenerated; note `agent_failure_modes` underscore form is the generator's vendor-rendered slug)
- `.gzkit/manifest.json` — surface registration may update (verify no-op vs HEAD if schema unchanged)
- `.gzkit/ledger.jsonl` — append-only `agent_sync_completed` event for this run
- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/obpis/OBPI-0.0.23-03-sync-mirrors.md` — evidence sections + status flip at completion (parent ADR package scope)

### Sync command writes (sync byproducts; require allowlist clarification)

- `.gzkit/rules/AGENTS.md` — nested subtree-rules generated file. Already modified (223 inserts) on the working tree. Sync may re-emit. The brief's allowed paths do not list `.gzkit/rules/AGENTS.md`, but its modification is a deterministic byproduct of running the sync verb the brief itself prescribes.
- Other generated nested AGENTS.md files under `.gzkit/skills/`, `.agents/`, etc. if present — same class of byproduct.

### Out of scope per brief allowed paths

- `.github/instructions/*.instructions.md` other than `agent_failure_modes.instructions.md` — pre-existing `applyTo` defects covered by the GHI we will file under the STOP-on-BLOCKERS path.
- `.gzkit/rules/agent-failure-modes.md` — canonical, edited only in OBPI-01 (denied path)
- `AGENTS.md`, `docs/governance/advisory-rules-audit.md` — edited in OBPI-02 (denied paths)

## Steps

1. **Pre-conditions check.**
   - Confirm OBPI-0.0.23-01 and OBPI-0.0.23-02 are `Completed` (already verified via ledger + frontmatter).
   - Confirm `.gzkit/rules/agent-failure-modes.md` exists (already verified; 11471 bytes, mtime 2026-04-30 03:02).
   - Capture pre-sync `gz validate --surfaces` output as baseline evidence.
   - Capture pre-sync state of working tree (`.gzkit/rules/AGENTS.md` is modified; this is a deterministic sync byproduct that pre-dates this OBPI's execution).

2. **Run `gz agent sync control-surfaces` under ARB.**
   - Invocation: `uv run gz arb step --name agent-sync -- uv run gz agent sync control-surfaces`
   - Capture full stdout/stderr in evidence.
   - Confirm exit 0.
   - Confirm receipt ID emitted (`arb-step-agent-sync-*`).

3. **Verify mirror byte-equivalence.**
   - `diff .gzkit/rules/agent-failure-modes.md .claude/rules/agent-failure-modes.md` — Claude mirror should match canonical modulo frontmatter rendering. Any non-frontmatter divergence is fail-closed.
   - `diff .gzkit/rules/agent-failure-modes.md .github/instructions/agent_failure_modes.instructions.md` — GitHub mirror should match canonical modulo frontmatter rendering. Apply same rule.
   - Per `.claude/rules/skill-surface-sync.md` § Anti-patterns: NEVER hand-edit a vendor mirror to make sync pass. If non-frontmatter divergence is found, the failure is in the canonical or generator, not the mirror.

4. **Run `gz validate --surfaces` under ARB.**
   - Invocation: `uv run gz arb step --name validate-surfaces -- uv run gz validate --surfaces`
   - Capture exit code and full output.
   - Capture receipt ID (`arb-step-validate-surfaces-*`).

5. **Classify residual errors (decision branch):**
   - **Branch A (clean)** — exit 0. Proceed to Step 6.
   - **Branch B (only the rule-placement warnings remain, both for `agent_failure_modes`)** — investigate root cause. If they trace to the canonical `agent-failure-modes.md` `paths:` frontmatter expecting nested AGENTS.md files that don't exist, fix the canonical's `paths` declaration in scope (denied path; would force scope expansion → STOP and surface). If they trace to the generator, file GHI and STOP. Do not hand-edit mirrors.
   - **Branch C (the 14 pre-existing `applyTo` field-required errors remain)** — STOP per brief STOP-on-BLOCKERS clause. File a GHI titled "applyTo field-required errors across .github/instructions/*.instructions.md vendor mirrors (validator vs generator gap)" with a reproduction (the `gz validate --surfaces` output), label `defect`, link the ADR-0.0.23 package, and surface to operator with three routing options:
     1. Accept OBPI-03 closeout with REQ-3 marked partial pass (sync ran clean, mirror parity verified, residual errors are pre-existing in the GHI'd scope) — operator attestation acknowledges the carve-out.
     2. Expand OBPI-03 brief allowlist to include `.github/instructions/*.instructions.md` and fix the schema-validator gap inline (foundation-kind brief amendment).
     3. Land the fix in a separate brief / direct fix routed off the new GHI; OBPI-03 stays open until that brief is `Completed`.
     Do not pick the route — the operator picks.

6. **Confirm canonical agent-sync ledger event.**
   - `grep '"agent_sync\|agent-sync\|sync_completed"' .gzkit/ledger.jsonl | tail -3`
   - Confirm a new event with this run's timestamp is present. The exact event name is determined by the sync command's emission contract; capture verbatim in evidence.

7. **Re-run `gz validate --documents` for cross-validation.**
   - Invocation: `uv run gz arb step --name validate-documents -- uv run gz validate --documents`
   - Confirms the brief's verification block (line 84) and ensures OBPI-02's documents stay clean post-sync.
   - Capture receipt (`arb-step-validate-documents-*`).

8. **Author brief evidence sections.**
   - Fill `### Implementation Summary` with bulleted "Files modified / Sync invocation / Mirror parity confirmed / Ledger event" prose so `_has_substantive_implementation_summary` accepts.
   - Fill `### Key Proof` with the diff-equivalence command + observed output, plus the four ARB receipt IDs (agent-sync, validate-surfaces, validate-documents, lint).
   - Fill `### Value Narrative` (one short paragraph: rule was authored and cross-linked in OBPIs 01/02; this brief closes the surface-sync loop with a ledger-witnessed canonical run).
   - Tick the Completion Checklist boxes the evidence supports.

9. **Two-stage review.** Per Stage 2 of the pipeline. Implementer (sync work is mechanical, complexity simple → haiku) → spec-reviewer + quality-reviewer. Sync work that touches generated files is the simplest implementer flavor; review focus is mirror byte-equivalence and ledger event presence.

## Verification

Brief-mandated commands (verbatim from the brief's `## Verification` block, lines 81–88):

```bash
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
uv run gz validate --documents
test -f .claude/rules/agent-failure-modes.md
test -f .github/instructions/agent-failure-modes.md   # NOTE: brief lists dash form; actual generator emits underscore form
diff .gzkit/rules/agent-failure-modes.md .claude/rules/agent-failure-modes.md
```

**Brief defect noted (in-scope to surface, out-of-scope to fix in OBPI-03):** the brief's `test -f .github/instructions/agent-failure-modes.md` references the dash-named form, but the generator emits `agent_failure_modes.instructions.md` (underscored, `.instructions.md` suffix). The brief's verification block is technically wrong; the actual mirror exists and OBPI-01 evidence already cited the correct underscored form. Capture this discrepancy in evidence and either (a) flag in the closing summary for operator routing, or (b) treat as cosmetic — the actual file existence is verifiable, the brief's wrong path string is the defect. Recommend (a): file a follow-up GHI to fix the brief's verification block in a future foundation-kind amendment OR resolve at ADR closeout.

Augmented with the brief's REQ table:

| REQ | Verification |
|-----|--------------|
| REQ-0.0.23-03-01 | `test -f .claude/rules/agent-failure-modes.md && test -f .github/instructions/agent_failure_modes.instructions.md` |
| REQ-0.0.23-03-02 | `uv run gz validate --surfaces` exits 0 (or STOP-on-BLOCKERS branch above) |
| REQ-0.0.23-03-03 | Canonical `agent_sync_completed` (or equivalent) ledger event present with this run's timestamp |

## Notes

### Destination-in-mind disclosure (Step 6a per skill)

**Conclusion already formed before authoring:** before writing this plan I had already decided the work splits into "run sync; run validate; if drift remains, escalate." This is the obvious shape for any sync-and-verify brief, and the brief itself prescribes it. The non-obvious decisions, which the plan walks through deliberately rather than reconstructing post-hoc, are: (a) how to handle the 14 pre-existing `applyTo` errors I observed during context-loading (chose: STOP-on-BLOCKERS branch + GHI + operator routing, not silent absorption or scope-expansion), (b) how to handle the `.gzkit/rules/AGENTS.md` working-tree modification I observed (chose: name it as a deterministic sync byproduct, treat it as a path-allowlist clarification question for the operator if sync re-emits new content, not as foreign work).

**Rejected alternatives:**
1. **Hand-edit the 14 mirrors to add `applyTo:` frontmatter** — rejected. Direct violation of `.claude/rules/skill-surface-sync.md` § Anti-patterns ("Do not edit `.github/instructions/` directly"). Mirrors are generated outputs; the fix lives in the generator or the validator.
2. **Expand brief allowlist inline ("scope is small, just fix it")** — rejected. The brief is foundation-kind under a foundation-kind ADR. Allowlist amendments require operator-attested brief amendment, not agent judgment. The STOP-on-BLOCKERS clause exists exactly for this case.
3. **Skip `gz validate --surfaces` and call REQ-3 satisfied because the new mirrors look right** — rejected. REQ-3 is the gate; satisfying its mechanical command is the contract. Narrative substitution is the failure mode the brief's verification block exists to prevent.
4. **Run sync inside a worktree subagent for review-isolation** — rejected for this brief. Sync work is whole-tree by design; running inside a worktree would not isolate the mirror generation against the canonical state and would force the validator to run against a partially-detached working set. The simple inline-implementer + parallel reviewer pattern is correct here.

### Lane and attestation

- Lane: Lite. Foundation-kind triggers brief-level Gate 5 attestation per AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix. TTY + `ATTEST` confirmation gate fires at `gz obpi complete`.
- No security sensitivity (sync is mechanical, no security surfaces in registry overlap with allowed paths).

### ARB receipt budget

Expected receipts emitted:
- `arb-step-agent-sync-*` — Step 2
- `arb-step-validate-surfaces-*` — Step 4
- `arb-step-validate-documents-*` — Step 7
- `arb-ruff-*` — baseline lint at Stage 3 entry
- `arb-step-typecheck-*` — baseline typecheck at Stage 3 entry
- `arb-step-unittest-*` — baseline unittest at Stage 3 entry (scoped to OBPI per `gz covers` parity gate; sync work has no `@covers` REQs to test directly per brief Acceptance Criteria — note this in evidence, ledger event presence is the mechanical witness)

### REQ → @covers parity gate caveat

The brief's `## Acceptance Criteria` are filesystem-and-ledger assertions, not test assertions. There are no unit tests covering `REQ-0.0.23-03-01/02/03` because the verification is mechanical (file existence, validator exit code, ledger event presence) — exactly the brief's design as sync-work. Stage 3 Phase 1b (`gz covers` parity gate) will likely report `uncovered_reqs > 0` for all three REQs. Resolution per OBPI-02's precedent (operator-decided route B): consolidate the parity skip into a follow-up GHI rather than authoring synthetic tests that pin filesystem state at a moment. The mechanical witnesses are: ARB receipt for the validator command + ARB receipt for the agent-sync command + ledger grep proof. Capture the GHI link in evidence; do not block on it.

### Lock and pipeline markers

- Stage 1 of the pipeline claims `OBPI-0.0.23-03-sync-mirrors` lock and writes `.claude/plans/.pipeline-active-OBPI-0.0.23-03-sync-mirrors.json` + `.claude/plans/.pipeline-active.json`.
- Stage 5 releases the lock and clears markers post-completion.

### Scope-collision findings (advisory; from `gz plan audit` collision scanner)

The CLI scope-collision scanner reported 7 sibling-ADR overlaps:

- `ADR-0.16.0 / OBPI-0.16.0-04-template-engine` contests `.claude/rules/agent-failure-modes.md`, `.github/instructions/agent-failure-modes.md`
- `ADR-0.36.0 / OBPI-0.36.0-{11,12,13}-*-instructions` each contest `.claude/rules/agent-failure-modes.md`
- `ADR-0.0.9 / OBPI-0.0.9-06-marker-migration-path`, `ADR-0.0.10 / OBPI-0.0.10-{01,04}-*` each contest `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/**`

Classification: all advisory, none active. The contesting OBPIs are either (a) sibling brief allowlists naming the same generator-emitted mirror path (template-engine briefs that scaffold rule mirrors) or (b) scoped to the ADR-0.0.23 package directory because they touch any foundation ADR package. None of these briefs are claimed (`.gzkit/locks/` empty per session orientation). Proceed without conflict; note the scanner output in evidence for downstream review.
