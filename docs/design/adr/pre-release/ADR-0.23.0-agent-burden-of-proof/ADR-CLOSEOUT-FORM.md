# ADR Closeout Form: ADR-0.23.0-agent-burden-of-proof

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.23.0-agent-burden-of-proof` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.23.0-01-closing-argument](OBPI-0.23.0-01-closing-argument.md) | OBPI-0.23.0-01 — Value Narrative Becomes Closing Argument | Completed |
| [OBPI-0.23.0-02-product-proof-gate](OBPI-0.23.0-02-product-proof-gate.md) | OBPI-0.23.0-02 — Product Proof Gate | Completed |
| [OBPI-0.23.0-03-reviewer-agent](OBPI-0.23.0-03-reviewer-agent.md) | OBPI-0.23.0-03 — Reviewer Agent Role | Completed |
| [OBPI-0.23.0-04-ceremony-enforcement](OBPI-0.23.0-04-ceremony-enforcement.md) | OBPI-0.23.0-04 — Ceremony Skill Enforcement | Completed |

## Defense Brief

### Closing Arguments

#### OBPI-0.23.0-01-closing-argument

1. **What was built** — Added `### Closing Argument (Lite)` and `### Closing Argument (Heavy)` sections to `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md`, with migration comments for briefs started under the old template. Created `tests/test_obpi_template.py` with 6 validation tests.

2. **What it enables** — Agents completing OBPI briefs now have structured guidance requiring them to substantiate their closing argument from delivered artifacts: what was built (paths), what it enables (operator capability), and why it matters (proof command). This replaces the mechanical "Value Narrative" fill-in with an earned-evidence standard.

3. **Why it matters** — `uv run -m unittest tests.test_obpi_template -v` proves the template enforces the new structure: Closing Argument sections exist in both lanes, Value Narrative headings are absent, completion-time authoring guidance is present, and planning-phase placeholders are rejected.

#### OBPI-0.23.0-02-product-proof-gate

We added `check_product_proof()` to `src/gzkit/quality.py` with three detection mechanisms (runbook keyword match, command doc existence, AST-parsed public docstrings) and integrated it into `closeout_cmd()` as a blocking gate. Operators running `uv run gz closeout ADR-X.Y.Z` now see a per-OBPI product proof table and cannot proceed when any OBPI lacks documentation proof. This matters because previously agents could declare completion without proving their work was documented — the gate makes rubber-stamp closeout impossible.

#### OBPI-0.23.0-03-reviewer-agent

The pipeline previously had no independent verification of whether delivered work matched OBPI promises. The implementing agent self-certified its own output. This OBPI adds a reviewer agent dispatch (Stage 3.5) that receives the brief, closing argument, changed files, and doc files — then independently assesses promises-met, docs-quality, and closing-argument-quality. The assessment is stored as a `REVIEW-*.md` artifact and presented in the Stage 4 ceremony before human attestation. Evidence: 42 unit tests, 8 BDD scenarios (46 steps), lint/typecheck/docs all clean.

#### OBPI-0.23.0-04-ceremony-enforcement

The closeout ceremony was a checklist — agents ticked boxes and declared completion without presenting the substance of what was delivered. The human attestor saw file lists and pass/fail statuses but never the agent's case for why the work matters. This OBPI transforms the ceremony into a defense presentation where the agent must present closing arguments (authored from delivered evidence per OBPI-01), product proof status (validated by the gate from OBPI-02), and an independent reviewer's assessment (dispatched by the pipeline from OBPI-03). If any evidence is missing, the ceremony blocks — the agent cannot proceed to attestation without making its case.

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.23.0-01-closing-argument | runbook | FOUND |
| OBPI-0.23.0-02-product-proof-gate | command_doc | FOUND |
| OBPI-0.23.0-03-reviewer-agent | docstring | FOUND |
| OBPI-0.23.0-04-ceremony-enforcement | command_doc | FOUND |

### Reviewer Assessment

| OBPI | Verdict | Promises Met | Docs Quality | Closing Arg | Artifact |
|------|---------|-------------|-------------|-------------|----------|
| OBPI-0.23.0-01-closing-argument | PASS | n/a | substantive | earned | `REVIEW-OBPI-0.23.0-01-closing-argument.md` |
| OBPI-0.23.0-02-product-proof-gate | PASS | n/a | substantive | earned | `REVIEW-OBPI-0.23.0-02-product-proof-gate.md` |
| OBPI-0.23.0-03-reviewer-agent | PASS | n/a | substantive | earned | `REVIEW-OBPI-0.23.0-03-reviewer-agent.md` |
| OBPI-0.23.0-04-ceremony-enforcement | PASS | n/a | substantive | earned | `REVIEW-OBPI-0.23.0-04-ceremony-enforcement.md` |


## Human Attestation

### Verbatim Attestation

- `completed`

**Attested by**: Jeff
**Timestamp (UTC)**: 2026-03-28T21:55:07Z
