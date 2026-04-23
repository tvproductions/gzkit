# Plan: OBPI-0.0.20-05 — Closeout Sweep + Downstream GHIs + Foundation Walkthrough

## Context

ADR-0.0.20 (`agent-rule-placement-invariant`) consolidated three rule files
(`agent-contract.md`, `attestation-enrichment.md`, `defect-fix-routing.md`)
out of `.gzkit/rules/` and into `AGENTS.md` plus `docs/governance/`. OBPIs
01–04 are `attested_completed`. OBPI-05 is the closeout: a final sweep, three
downstream-impact GHIs, and the foundation-kind closeout walkthrough.

This OBPI is Lite-lane but foundation-kind, so per ADR-0.0.18 the human
walkthrough discipline still fires. No new code, no schema changes — only
verification, GHI filing, ceremony, and attestation.

## Pre-conditions verified (read-only sweep)

- Three target rule files absent from `.gzkit/rules/` and all three vendor mirrors
- `.gzkit/manifest.json` → `rules.unscoped_allowlist` has zero entries
- `EVALUATION_SCORECARD.md` exists; ADR scores 4.00/4.0; all five OBPIs ≥3.6/4.0; no score-1 dimensions
- `ADR-CLOSEOUT-FORM.md` exists in Phase 0 (Draft), needs population
- ADR Attestation Block row is empty (`| 0.0.20 | Draft | | | |`)
- Live-surface grep returns only legitimate references to the **new** governance homes (`docs/governance/agent-contract-rationale.md`, `docs/governance/arb-middleware.md`, `docs/governance/defect-fix-routing.md`) and skill files. No stale `.gzkit/rules/` references.

## Critical files to modify (Allowed Paths only)

| Path | Mutation |
|------|----------|
| `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-CLOSEOUT-FORM.md` | Populate Pre-Attestation Checklist, OBPI Status table, Defense Brief Closing Arguments + Reviewer Assessment, Product Proof table |
| `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md` | Update Attestation Block to `Validated` with attestor + date + reason; populate Evidence section with real outputs from OBPI-01/02/03/04 evidence sections |
| `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/obpis/OBPI-0.0.20-05-closeout-and-downstream.md` | Populate evidence sections, Implementation Summary, Key Proof, Value Narrative, Human Attestation block — Stage 4/5 of the pipeline |
| `EVALUATION_SCORECARD.md` | Already populated — no edits expected |

## Steps

### Step 1 — Mechanical verification (CLI evidence)

Run and capture output of:

```bash
uv run gz agent sync control-surfaces            # confirm no stale mirrors
uv run gz validate --unscoped-rules              # zero allow-list entries
uv run gz validate --all                         # exits 0
uv run gz check                                  # lint + format + typecheck + tests
uv run gz test                                   # explicit test run
uv run mkdocs build --strict                     # docs build clean
```

Plus the brief's grep sweep + `test ! -f` mirror absence checks (per Verification block in the brief).

If any check fails, STOP. Defects file as separate GHIs per OBPI-05 REQ-14.

### Step 2 — File three downstream GHIs

Per the brief's REQ-7/8/9. The exploration discovered:

- **GHI #1 (ADR-0.36.0 WBS):** GHI #289/#291 already exist and OBPI-0.36.0-08 has been retargeted (commit `f262b08a` — same OBPI ID, no typo intended). Action: file a confirmation/closeout-side GHI **only** if no umbrella issue links from ADR-0.0.20's perspective. Otherwise, link the existing GHIs in the ADR Attestation Block. **Default:** file the GHI per the brief's literal wording, citing GHI #289/#291 as already-resolved upstream.
- **GHI #2 (ADR-0.38.0-07 baseline):** New GHI noting that gzkit AGENTS.md absorbed ~440 lines from three rule files; OBPI-0.38.0-07's airlineops-vs-gzkit comparison runs against this normalized baseline.
- **GHI #3 (ADR-0.0.19 reference refresh):** New GHI calling out citation strings at lines 17 and 19 of `ADR-0.0.19-pre-execution-reasoning-walkthrough.md` (cite `behavioral-invariants.md` / `agent-contract.md` — both gone). Proposed text: pin to `AGENTS.md § Prime Directive § Invariant 11`.

All three filed via `gh issue create --label defect --title "..." --body "..."` per `.gzkit/rules/gh-cli.md`. Body structure follows the GHI #289/#294 conventions (Observed → Expected → Proposed resolution → Provenance).

### Step 3 — Populate ADR-CLOSEOUT-FORM.md

- Check all 9 Pre-Attestation Checklist boxes with evidence paths
- Update the OBPI Status table: 01–04 → `Completed`; 05 → `Completed` (after this step)
- Populate Defense Brief Closing Arguments + Reviewer Assessment (cite the consolidation result, scorecard, and grep-sweep evidence)
- Populate Product Proof table

### Step 4 — Update parent ADR Attestation Block + Evidence

- Attestation Block: `| 0.0.20 | Validated | Jeffry Babb | 2026-04-23 | <reason — concrete, grounded> |`
- Evidence section: paste real command outputs from Step 1 verification + OBPI-01/02/03/04 evidence

### Step 5 — Populate OBPI-0.0.20-05 brief evidence

The closure-narrative gate (Stage 5 Step 1 of `gz-obpi-pipeline`) requires substantive `### Implementation Summary` and `### Key Proof` text in the brief before `gz obpi complete` will accept it. Populate:

- Value Narrative
- Key Proof (concrete: final `gz validate --unscoped-rules` output)
- Implementation Summary (bulleted, files-modified list)
- Downstream GHIs table (with real GHI numbers)
- Human Attestation block

### Step 6 — Foundation walkthrough + ceremony + sync (Stage 4 + Stage 5 of pipeline)

Use `gz-obpi-pipeline` Stage 4 (Normal mode — present evidence to operator and wait for `attest completed`) and Stage 5:

1. Pre-flight: `uv run gz obpi precomplete OBPI-0.0.20-05-closeout-and-downstream`
2. Closure-narrative gate (skill-prescribed inline preview)
3. `uv run gz obpi complete OBPI-0.0.20-05-closeout-and-downstream --attestor "Jeffry Babb" --attestation-text "<operator phrase + enrichment>" --implementation-summary "..." --key-proof "..." --attestor-present`
4. `uv run gz obpi lock release OBPI-0.0.20-05-closeout-and-downstream`
5. Remove pipeline markers
6. Git-sync #1: `uv run gz git-sync --apply`
7. `uv run gz obpi reconcile OBPI-0.0.20-05-closeout-and-downstream`
8. `uv run gz adr status ADR-0.0.20 --json`
9. Git-sync #2: `uv run gz git-sync --apply`

Then the ADR-level closeout (separate from OBPI completion):

10. `uv run gz attest ADR-0.0.20 --status completed`
11. `uv run gz adr emit-receipt ADR-0.0.20 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"ADR-0.0.20","date":"2026-04-23"}'`
12. Final `uv run gz git-sync --apply` to commit any remaining ADR-level edits.

### Step 7 — Foundation closeout ceremony surface (optional, depends on operator preference)

`uv run gz closeout ADR-0.0.20 --ceremony` is the deterministic step-by-step ceremony surface (per `gz-adr-closeout-ceremony` skill). It bundles attestation + repo sync into a guided flow. The brief's verification block lists `gz attest` + `gz adr emit-receipt` as the explicit minimum surface, so Step 6 above suffices; the ceremony is operator-preference for the walkthrough framing.

## Verification (end-to-end)

After completion, the following should all be true:

- `uv run gz adr status ADR-0.0.20` shows: Lifecycle `Completed`, Closeout Phase `closed`, OBPI 5/5, Closeout `READY` or equivalent, QC `READY`
- `uv run gz adr audit-check ADR-0.0.20` exits 0
- `uv run gz validate --unscoped-rules` exits 0 with zero allow-list entries
- `gh issue list --label defect --search "ADR-0.36.0"` / `--search "ADR-0.38.0"` / `--search "ADR-0.0.19"` returns the three filed GHIs
- ADR-0.0.20 Attestation Block reads `Validated` with attestor + date
- Tree is clean after final git-sync

## Open decisions for operator

1. **GHI #1 routing:** GHI #289/#291 already exist and have retargeted OBPI-0.36.0-08. Should I (a) file a fresh GHI per the brief's literal wording, or (b) cite the existing #289/#291 as satisfying the requirement and note that in the closeout form? Default: (a) — file per literal brief wording, citing #289/#291 as already-resolved upstream.
2. **Attestor name in receipt:** Brief specifies `Jeffry Babb` (operator name only). Confirmed.
3. **Ceremony surface:** Use `gz closeout --ceremony` walkthrough (Step 7) or just minimum `gz attest` + `gz adr emit-receipt` (Step 6)? Default: Step 6 only; ceremony is optional UX framing.
