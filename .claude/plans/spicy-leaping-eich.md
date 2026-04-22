# OBPI-0.0.19-05-docs-bdd-closeout Implementation Plan

**Canonical OBPI:** `OBPI-0.0.19-05-docs-bdd-closeout`
**Parent ADR:** `ADR-0.0.19-pre-execution-reasoning-walkthrough`
**Brief:** `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/obpis/OBPI-0.0.19-05-docs-bdd-closeout.md`

## Context

ADR-0.0.19 introduced `gz justify` — a deterministic CLI that scaffolds an
8-section pre-execution reasoning walkthrough for GHIs, OBPIs, or draft
anchors, plus a `validate` subverb that reverse-parses filled walkthroughs.
OBPI-01 through OBPI-04 landed the resolver, scaffold renderer, validate
subverb, and skill/upstream integrations (justify-walkthrough skill plus
`gz-adr-evaluate` low-score and `gz-obpi-pipeline` Stage 1→2 confidence
gate suggestions). All four prior OBPIs are `attested_completed`.

This OBPI is the Heavy-lane closeout: it ships the documentation covenant
(Gate 3), BDD acceptance coverage (Gate 4), and the human-attestation
package (Gate 5) so ADR-0.0.19 can move from `Pending` to `Completed`.
Currently `gz adr status ADR-0.0.19` reports `BLOCKED — OBPI-05 ledger
proof of completion is missing`; this OBPI removes that block.

**Existing state surfaced during exploration:**

- `docs/user/commands/justify.md` exists as a Gate-3 stub (47 lines) that
  explicitly defers full operator guidance to "a later OBPI under this ADR"
  — that later OBPI is this one. The stub will be expanded in place.
- `docs/user/commands/index.md` already lists `gz justify` (line 25).
- `docs/user/manpages/gz-justify.md` does NOT exist — must be created.
- `config/doc-coverage.json` flags `justify` as `governance_relevant: false`
  with only `manpage + index_entry + docstring` required. The brief's
  REQ-03 and REQ-04 mandate runbook entries — the manifest must flip
  `operator_runbook` and `governance_runbook` to `true` so the audit
  enforces what the brief promises (this is the canonical "fix the class
  of failure" move per `.claude/rules/agent-contract.md` § 6a).
- `gz cli audit` does NOT discover subverbs as separate commands; the
  validate subverb's coverage is inherited through the parent `justify`
  verb's manpage/command-doc sections. Both surfaces will document the
  subverb explicitly per REQ-01 and REQ-02.
- BDD step infrastructure (`features/steps/gz_steps.py`) exposes the
  canonical `When I run the gz command "..."` / `Then the command exits
  with code N` step pair plus a shared `_invoke()` helper — the new
  `justify_steps.py` will reuse those steps and only add justify-specific
  Given/Then steps (file fixtures, `gh` mocking).

## Approach

The work decomposes into 8 sequential tasks, each producing testable
artifacts. Tasks 2-7 are TDD increments (Red→Green per artifact). Task 8
is the Stage 4/5 ceremony per `gz-obpi-pipeline`.

### Task 1 — Update doc-coverage manifest for `justify` Heavy coverage

**File:** `config/doc-coverage.json`

Flip `commands.justify.surfaces.operator_runbook` and `governance_runbook`
to `true`. Set `governance_relevant: true` (justify suggestions feed
governance skills). Add `justify validate` entry only if the audit's
manifest schema accepts subverb keys (verify schema first; if not, document
that subverb coverage is inherited via parent and rely on REQ-01/02 to
mandate explicit subverb sections in manpage + command doc).

### Task 2 — Author `tests/cli/test_justify_manpage.py` (Red→Green)

**File:** `tests/cli/test_justify_manpage.py` (new)

Mirrors the heading-and-section pattern from
`tests/test_skill_manpage_coverage.py`. Asserts:

- File exists at `docs/user/manpages/gz-justify.md`
- Heading `# gz justify` (or `# gz-justify` matching the personas
  exemplar's `# gz-personas` form — pick the existing convention)
- Required sections present: NAME, SYNOPSIS, DESCRIPTION, OPTIONS,
  EXIT STATUS, EXAMPLES, SEE ALSO
- At least three EXAMPLES blocks (GHI, OBPI with `--save`, `validate`)
- EXIT STATUS documents codes 0, 1, 2 with meanings
- OPTIONS section names every flag from `gz justify --help`
- All lines ≤80 chars (CLI doctrine)
- Decorated with `@covers("REQ-0.0.19-05-01")`

Run `uv run -m unittest tests.cli.test_justify_manpage -v` to confirm Red
(file does not exist), then proceed to Task 3 to make it Green.

### Task 3 — Create `docs/user/manpages/gz-justify.md`

**File:** `docs/user/manpages/gz-justify.md` (new)

Mirror `docs/user/manpages/gz-personas.md` layout. Sections:

- `# gz-justify` (matches existing manpage convention)
- NAME — one-line summary
- SYNOPSIS — usage forms for parent verb and `validate` subverb
- DESCRIPTION — anchor-resolution + scaffold rendering + validate flow,
  citing parent ADR-0.0.19 and the deterministic-no-LLM contract
- OPTIONS — every flag (`--save`, `--output`, `--related`, `--draft`,
  `--draft-slug`, `--json` for validate, `--quiet`, `--verbose`, `--debug`)
  with applies-to column distinguishing parent verb from validate subverb
- EXIT STATUS — table of 0/1/2 with the validate-specific semantics
  (0 parseable+complete, 1 parseable+incomplete, 2 unparseable)
- EXAMPLES — at minimum three: `gz justify GHI-232`,
  `gz justify OBPI-0.0.19-05 --save`,
  `gz justify validate path/to/walkthrough.md`
- SEE ALSO — `gz-adr-evaluate`, `gz-obpi-pipeline`,
  `commands/justify.md`

Re-run the manpage test → Green.

### Task 4 — Expand `docs/user/commands/justify.md`

**File:** `docs/user/commands/justify.md` (existing stub — expand in place)

Identify exemplar via Glob (likely `docs/user/commands/adr-evaluate.md`
or another well-formed command doc). Mirror its heading layout. Add:

- Overview paragraph (anchor types, validate subverb)
- Usage block (both invocation forms)
- Anchor types table (GHI, OBPI, draft) with examples
- Flag table (mirroring the manpage OPTIONS)
- Exit-code table (0/1/2 with validate semantics)
- Operator-flow example (resolve GHI → review scaffold → fill →
  validate → cite in OBPI Key Proof)
- Troubleshooting note: `--draft + --save` requires `--draft-slug`
  (matches CLI's own error message)

REQ-02 satisfied.

### Task 5 — Extend `docs/user/runbook.md`

**File:** `docs/user/runbook.md`

Insert subsection inside Loop A (after the Step 2 pipeline content,
before the Verification Checklist). Title: "Step 2b: Pre-execution
Reasoning Walkthrough (`gz justify`)". Content:

- When to invoke (low confidence, ambiguous scope, complex anchor)
- Three anchor types (GHI / OBPI / draft) with one-line example each
- Validate flow (`gz justify validate <file>` to confirm completeness
  before citing in attestation)
- Cross-link to manpage and command doc

Integrated into Loop A narrative — NOT a standalone appendix
(brief explicitly requires this).

### Task 6 — Extend `docs/governance/governance_runbook.md`

**File:** `docs/governance/governance_runbook.md`

Insert subsection under "Workflow: Create or Promote ADR" (after the
quality-evaluation step). Title: "5b: Pre-execution reasoning when
quality signals are weak". Content:

- `gz-adr-evaluate` low-score output suggests `gz justify` (cite
  Prime Directive invariant 11 — "if <90% sure, ask")
- `gz-obpi-pipeline` Stage 1→2 confidence gate routes operators to
  `gz justify` when self-reported confidence < 90%
- Brief mention of the validate subverb as the closure check

REQ-04 satisfied (cites both upstream skills + invariant 11).

### Task 7 — BDD coverage at `features/justify.feature` + steps

**Files:**
- `features/justify.feature` (new)
- `features/steps/justify_steps.py` (new)

Eight scenarios per REQ-05, each tagged `@REQ-0.0.19-05-NN`:

| Tag | Scenario |
|-----|----------|
| `@REQ-0.0.19-05-S1` | invoke on GHI with mocked `gh` |
| `@REQ-0.0.19-05-S2` | invoke on OBPI against fixture brief |
| `@REQ-0.0.19-05-S3` | invoke `--draft` + `--draft-slug` + `--save` |
| `@REQ-0.0.19-05-S4` | reject ADR anchor with exit 1 |
| `@REQ-0.0.19-05-S5` | reject `--draft` + `--save` without `--draft-slug` |
| `@REQ-0.0.19-05-S6` | `validate` on complete fixture exits 0 |
| `@REQ-0.0.19-05-S7` | `validate` on incomplete fixture exits 1 with unfilled list |
| `@REQ-0.0.19-05-S8` | `validate` on malformed fixture exits 2 |

`features/steps/justify_steps.py`:
- Reuse `_invoke()` from `gz_steps.py` via the existing
  `When I run the gz command "..."` step (no duplication)
- Add Given steps: `a fixture OBPI brief at "<path>"`, `a fixture
  walkthrough file at "<path>" with content`, `gh issue view returns
  fixture body for "GHI-{N}"` (the last one patches the resolver's
  subprocess call)
- Add Then steps: `the output names unfilled section "<name>"`,
  `a scaffold artifact is written under "<dir>"`
- Decorated with `@covers("REQ-0.0.19-05-05")` and per-step
  `@covers("REQ-0.0.19-05-06")` for the behave-passing requirement

Verify: `uv run -m behave features/justify.feature` exits 0.

### Task 8 — Heavy-lane closeout ceremony

This task IS Stage 4/5 of the pipeline — execute it through the
pipeline orchestrator, not as a freeform script:

1. Run baseline checks: `uv run gz lint`, `uv run gz typecheck`,
   `uv run gz test --obpi OBPI-0.0.19-05 --bdd`,
   `uv run mkdocs build --strict`, `uv run gz cli audit`
2. Run REQ → @covers parity gate:
   `uv run gz covers OBPI-0.0.19-05 --json`; close any gaps before
   advancing
3. Capture ARB receipts (canonical invocations from
   `.claude/rules/attestation-enrichment.md`):
   - `uv run gz arb ruff` → `arb-ruff-*`
   - `uv run gz arb typecheck` → `arb-step-typecheck-*`
   - `uv run gz arb step --name unittest -- uv run -m unittest -q`
     → `arb-step-unittest-*`
   - `uv run gz arb coverage run -m unittest discover -s tests -t .`
     → `arb-step-coverage-*`
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
     → `arb-step-mkdocs-*`
4. Update `docs/design/adr/.../ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
   Evidence section with the five receipt IDs quoted inline
5. Update `docs/design/adr/.../ADR-CLOSEOUT-FORM.md` to reflect all
   gates green
6. Stage 4 ceremony presentation (Normal mode — operator attests)
7. `uv run gz obpi precomplete OBPI-0.0.19-05` → must exit 0
8. `uv run gz obpi complete OBPI-0.0.19-05 --attestor "Jeffry Babb"
   --attestation-text "<verbatim + em-dash enrichment>"
   --implementation-summary "..." --key-proof "..."`
9. `uv run gz obpi lock release OBPI-0.0.19-05`
10. Cleanup pipeline markers
11. Git-sync #1 (`uv run gz git-sync --apply`)
12. `uv run gz obpi reconcile OBPI-0.0.19-05`
13. `uv run gz adr status ADR-0.0.19 --json`
14. Git-sync #2
15. ADR-level closeout: `uv run gz adr audit-check ADR-0.0.19` (REQ-11),
    `uv run gz closeout ADR-0.0.19`, `uv run gz attest ADR-0.0.19
    --status completed` with the same attestation-enrichment shape
    (REQ-12), update Attestation Block table (REQ-13)

## Files Modified

**New files:**
- `docs/user/manpages/gz-justify.md`
- `tests/cli/test_justify_manpage.py`
- `features/justify.feature`
- `features/steps/justify_steps.py`

**Modified files:**
- `docs/user/commands/justify.md` (expand from stub)
- `docs/user/runbook.md` (Step 2b subsection)
- `docs/governance/governance_runbook.md` (5b subsection)
- `config/doc-coverage.json` (flip surface flags for justify)
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md` (Evidence + Attestation Block)
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-CLOSEOUT-FORM.md` (gate states)
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/EVALUATION_SCORECARD.md` (refresh if warranted)
- The OBPI brief itself (Evidence sections, Implementation Summary,
  Key Proof — written by `gz obpi complete`)

All paths within the brief's Allowed Paths (verified against the brief).

## Reused Existing Patterns

- `tests/test_skill_manpage_coverage.py` — heading + section presence
  pattern for the manpage test
- `features/steps/gz_steps.py` — `_invoke()` helper, `When I run the
  gz command "..."` / `Then the command exits with code N` step pair
- `docs/user/manpages/gz-personas.md` — manpage layout exemplar
- `docs/user/commands/adr-evaluate.md` — full command-doc layout
  exemplar (verify via Glob during Task 4)
- `.claude/rules/attestation-enrichment.md` § Canonical invocations —
  the five ARB-wrapped commands (locked by `CANONICAL_STEP_COMMANDS`)
- `gz-obpi-pipeline` Stage 5 two-sync pattern

## Verification (end-to-end)

```bash
# Gate 2 — TDD
uv run -m unittest tests.cli.test_justify_manpage -v

# Gate 3 — Docs
uv run mkdocs build --strict
uv run gz cli audit

# Gate 4 — BDD
uv run -m behave features/justify.feature

# REQ → @covers parity
uv run gz covers OBPI-0.0.19-05 --json

# OBPI completion preconditions
uv run gz obpi precomplete OBPI-0.0.19-05

# ADR-level audit
uv run gz adr audit-check ADR-0.0.19

# Final state check
uv run gz adr status ADR-0.0.19
```

Expected end state: ADR-0.0.19 lifecycle = `Completed`, OBPI 5/5 done,
no closeout blockers, all five ARB receipts referenced in the ADR
Evidence section.
