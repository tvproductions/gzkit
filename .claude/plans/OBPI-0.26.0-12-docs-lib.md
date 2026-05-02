# Plan — OBPI-0.26.0-12: Documentation Library (Confirm by Inheritance)

**OBPI:** OBPI-0.26.0-12-docs-lib
**Parent ADR:** ADR-0.26.0-governance-library-module-absorption (Heavy, feature)
**Paired (attested):** OBPI-0.25.0-25-docs-validation-pattern — `attested_completed` 2026-04-12 (Jeffry)
**Lane:** Heavy
**Operator routing:** Path B (re-frame as Confirm, inherit paired decision)

## Context

OBPI-0.26.0-12 evaluates `../airlineops/src/opsdev/lib/docs.py` (218 lines).
The `paired_with` sibling OBPI-0.25.0-25 has already evaluated the identical
upstream source file, producing a fully-rationalized **Confirm** decision
backed by attestation. The current brief's premise — "gzkit equivalent: None"
and "no Confirm path" — is structurally false against the paired evidence.

Operator directed Path B: keep ADR-0.26.0's 12-row WBS intact and re-frame
this brief as Confirm by inheritance, with cross-citation to the paired
brief as the canonical evaluation.

## Files (allowlist contract)

Only these paths may be edited:

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md`
  — the brief itself (re-frame to Confirm, inherit decision)

No `src/gzkit/` or `tests/` edits — Confirm decision means no code change.

## Steps

### Step 1 — Correct the brief premise (ASSUMPTIONS + SOURCE MATERIAL)

Replace the false premises that force Absorb-or-Exclude:

- `SOURCE MATERIAL` → change `gzkit equivalent: None` to name the canonical
  equivalent surface: `src/gzkit/doc_coverage/` package (~802 lines across
  `scanner.py`, `models.py`, `manifest.py`, `runner.py`) + `mkdocs build --strict`
  integration. Cite OBPI-0.25.0-25 as the discovery brief.
- `ASSUMPTIONS` → strike the line *"No existing gzkit equivalent means either
  Absorb or Exclude — there is no Confirm path"*. The Confirm path exists
  and was attested in the paired brief.
- `OBJECTIVE` → broaden the determination set to `Absorb / Confirm / Exclude`
  to match OBPI-0.25.0-25's outcome surface.

### Step 2 — Add Comparison section

Mirror the structure of OBPI-0.25.0-25's `## Comparison` section. Author by
inheritance: cite the paired brief's tables (opsdev `docs.py` function
inventory, gzkit `doc_coverage/` capabilities, capability comparison matrix)
by reference rather than duplicating them verbatim. The cross-citation IS
the audit trail; copying defeats the subtraction-test discipline.

Sections to add at the same H2 level as the paired brief:

- `## Comparison` — H2 with `### Inheritance Statement` (H3) naming the
  paired brief and attestation date, plus a brief paraphrase of the
  capability-comparison conclusion (different problem scopes; link
  validation is mkdocs-redundant; manifest-driven obligations vs hardcoded
  checks; type-safe models vs untyped primitives; 87 tests vs none;
  self-declared temporary status of opsdev source).

### Step 3 — Add Decision section

`## Decision: Confirm` — H2 matching the paired brief's heading. Body:

- Restate the Confirm outcome.
- Inheritance rationale: identical upstream source file, paired brief
  produced a fully-evidenced decision, re-litigation under the
  ADR-0.26.0 "governance library" lens reaches the same conclusion
  because the source has not changed.
- Subtraction-test affirmation: nothing in opsdev `docs.py` is both unique
  and non-redundant against gzkit's `doc_coverage/` surface and
  `mkdocs build --strict`.
- `### Gate 4 (BDD): N/A` — no operator-visible behavior change (Confirm
  decision; no code added/removed/modified).

### Step 4 — Update REQUIREMENTS, Acceptance Criteria, Quality Gates

- `REQUIREMENTS (FAIL-CLOSED)` → add the Confirm row that OBPI-0.25.0-25
  carries: *"If Confirm: document why gzkit's implementation is
  sufficient."* Keep the existing five lines; add Confirm as a sixth.
- `Acceptance Criteria` → REQ-0.26.0-12-01 broadens to
  `Absorb / Confirm / Exclude`. Add REQ-0.26.0-12-06 for the Confirm
  outcome obligation (mirrors REQ-0.25.0-25-04).
- `Quality Gates` → check Gate 1 (intent), Gate 2 (no code → tests
  unchanged), Gate 3 (decision rationale completed), Gate 4 (N/A with
  rationale per Confirm). Gate 5 left unchecked — operator attestation
  fires in Stage 4.
- `Completion Checklist` → mirror the same gate state.

### Step 5 — Author Implementation Summary, Key Proof, Closing Argument

H3 evidence sections per `.claude/rules/brief-heading-conventions.md`:

- `### Implementation Summary` — bulleted "- Key: value" form so the
  `_has_substantive_implementation_summary` check accepts it. Naming:
  decision (Confirm by inheritance), paired brief, attestation date,
  upstream source SHA-equivalent (line count match), gzkit equivalent
  surface, code changes (None — Confirm decision).
- `### Key Proof` — at least one concrete command + observed output. Use
  `rg -n 'Decision: Confirm' <brief-path>` showing the H2 heading match,
  plus `rg -n 'attested_completed' <paired-brief-path>` showing the
  paired attestation status.
- `### Closing Argument` — paragraph form, naming the inheritance basis,
  the subtraction-test affirmation, and why re-litigating under a
  different ADR lens still produces Confirm.

### Step 6 — Fix the brief-internal path drift

The existing `Verification Commands` section references
`docs/design/adr/.../briefs/OBPI-0.26.0-12-docs-lib.md` (in `briefs/`),
but the actual file lives in `obpis/`. Update all three `rg -n` commands
to point at the actual `obpis/` path so the verification commands
execute against the brief that exists.

### Step 7 — Stage 3 verification

Baseline ARB-wrapped checks (per `.claude/rules/gate5-runbook-code-covenant.md`):

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz validate --briefs
uv run gz validate --brief-headings
uv run gz validate --absorption-duplicates
uv run gz validate --requirements
```

Brief-specific verification (from the corrected Verification Commands section):

```bash
test -f ../airlineops/src/opsdev/lib/docs.py
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
```

### Step 8 — REQ → @covers parity

This brief's REQs are documentation requirements (`[doc]`-class), not
test-asserted code requirements — same shape as OBPI-0.25.0-25. The
`@covers` parity gate (Stage 3 Phase 1b) will be satisfied by the
existing brief-doc REQ pattern; if `gz covers OBPI-0.26.0-12-docs-lib --json`
flags uncovered REQs, the fix is to mark them `[doc]`-class in the
acceptance criteria (matching paired-brief convention) rather than
authoring synthetic tests.

## Verification

- Brief records `## Decision: Confirm` (H2) — matches paired-brief shape.
- Cross-citation to `OBPI-0.25.0-25-docs-validation-pattern` present in
  Comparison and Decision sections.
- All evidence H3 sections (`Implementation Summary`, `Key Proof`,
  `Closing Argument`) populated and non-placeholder.
- All `gz validate --*` scopes above exit 0.
- `gz covers OBPI-0.26.0-12-docs-lib --json` reports
  `summary.uncovered_reqs == 0`.

## Notes

- **Lane and attestation:** Heavy lane, feature kind, sensitivity absent →
  brief-level human attestation required (per AGENTS.md attestation
  matrix). Stage 4 fires the Normal-mode HUMAN GATE.
- **No code change:** ALLOWED PATHS includes `src/gzkit/` and `tests/`
  but the Confirm decision means neither is touched. The allowlist is a
  ceiling, not a floor.
- **Plan-before-exploration disclosure (gz-plan-audit Step 6a):**
  - *Destination-in-mind:* Confirm by inheritance from OBPI-0.25.0-25.
    Operator surfaced the conflict, weighed Path A (withdraw) vs Path B
    (re-frame as Confirm) vs Path C (independent re-evaluation), and
    explicitly chose Path B. Plan was authored against that decision.
  - *Rejected alternatives:* Path A (withdraw) was the agent's initial
    recommendation on subtraction-test grounds; operator overrode on the
    basis that withdrawal would unbalance ADR-0.26.0's WBS and the
    inherited-Confirm path produces a complete audit trail without code
    change. Path C (independent re-evaluation) was rejected as
    re-litigation that would consume a cycle to produce the same
    conclusion against an unchanged source file.
