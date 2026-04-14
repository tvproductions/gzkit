# OBPI-0.25.0-32 — Handoff Validation Pattern (Absorb)

## Context

The brief OBPI-0.25.0-32 asks: does airlineops's `handoff_validation.py` (312 lines) belong in gzkit as Absorb, Confirm, or Exclude?

Evidence gathered in Stage 1:

- **airlineops source** (`../airlineops/src/opsdev/governance/handoff_validation.py`, 312L) is a complete, self-contained handoff-document validator: frontmatter parsing + Pydantic schema (`HandoffFrontmatter`), placeholder scan, secret scan, required-sections check, referenced-file existence check. Exports: `HANDOFF_SCHEMA_VERSION`, `REQUIRED_SECTIONS`, `HandoffFrontmatter`, `HandoffValidationError`, `parse_frontmatter`, `validate_handoff_document`, `validate_no_placeholders`, `validate_no_secrets`, `validate_referenced_files`, `validate_sections_present`.
- **gzkit spec** (`docs/governance/GovZero/handoff-validation.md`) already mandates this exact contract — written ahead of implementation. It references `tests/governance/test_handoff_validation.py` and `from gzkit.validate import parse_frontmatter` — both of which do not currently match reality.
- **gzkit implementation surface** — NO `HandoffFrontmatter` anywhere; NO placeholder/secret/section/file-ref validators; NO `tests/governance/` directory. Only generic helpers exist: `src/gzkit/core/validation_rules.py` has a generic `parse_frontmatter()` (tuple return, not Pydantic) and `extract_headers()`; `src/gzkit/validate_pkg/document.py` does schema-based manifest document validation.
- **The brief's pointer is wrong** — it claims gzkit's equivalent is distributed across `pipeline_dispatch.py` + `lock_manager.py` + `interview_cmd.py` (~970L). Those modules are pipeline dispatch / lock management / interactive Q&A — NOT handoff document validation. The brief's comparison target is incorrect and the plan must correct it in the decision rationale.

**Decision (grounded in evidence):** **ABSORB.** The gzkit spec already promises the capability; the implementation is missing; airlineops already follows gzkit's own conventions (Pydantic with `ConfigDict(extra="forbid", frozen=True)`, pathlib, `from __future__ import annotations`, `re.compile` at module level). The subtraction test passes cleanly: handoff document validation is not airline-specific.

The outcome of this OBPI is a small, targeted absorption: one new module, one new test tree, two doc updates (spec + brief).

## Plan

### Step 1 — Absorb the module

**Create:** `src/gzkit/handoff_validation.py` (new file, ~320 lines)

- Port the airlineops 312L module verbatim into gzkit.
- Minimal adaptations:
  - Keep the original `@covers ADR-0.0.25 (OBPI-0.0.25-06)` docstring line AND add `@covers ADR-0.25.0 (OBPI-0.25.0-32)` so both origin and absorption are traceable.
  - Add cross-platform line-ending normalization at the top of each public validator: `content = content.replace("\r\n", "\n")` before pattern matching. `.claude/rules/cross-platform.md` mandates CRLF safety for any content that flows through `re.MULTILINE` patterns.
  - No structural changes. The module already uses `BaseModel` + `ConfigDict(extra="forbid", frozen=True)`, `pathlib.Path`, `from __future__ import annotations`, and avoids mutable defaults.
- **Do NOT re-export** via `src/gzkit/validate.py`. `core/validation_rules.parse_frontmatter()` already exists with an incompatible signature (tuple return). Re-exporting would create a silent name collision. Consumers must import explicitly from `gzkit.handoff_validation`.

### Step 2 — Add the test tree

**Create:** `tests/governance/__init__.py` (empty, for unittest discovery)

**Create:** `tests/governance/test_handoff_validation.py` (~400 lines)

- `unittest.TestCase` classes; no pytest.
- Follow gzkit test conventions: `tempfile.TemporaryDirectory` as context manager (cross-platform cleanup rule), `@covers("REQ-...")` decorators from `gzkit.traceability`, `subTest` for table-driven cases.
- Test classes and REQ coverage mapping:

  | Test class / method | REQ covered | Purpose |
  |---|---|---|
  | `TestHandoffFrontmatter.test_*` | REQ-0.25.0-32-03 | Pydantic model validators (ADR regex, OBPI regex, ISO timestamp, extra-forbid, mode literal) |
  | `TestParseFrontmatter.test_*` | REQ-0.25.0-32-03 | Structural parse: missing delimiters, invalid YAML, non-mapping body |
  | `TestValidatePlaceholders.test_*` | REQ-0.25.0-32-03 | TBD/TODO/FIXME/PLACEHOLDER/XXX/CHANGEME/ellipsis; HTML comment stripping; frontmatter stripping |
  | `TestValidateSecrets.test_*` | REQ-0.25.0-32-03 | password=, secret=, token=, api_key=, Bearer, PRIVATE KEY, sk-*, ghp_*; negative lookbehind correctness (`task-management` must not match `sk-`) |
  | `TestValidateSectionsPresent.test_*` | REQ-0.25.0-32-03 | All 7 required sections detected; missing section reported |
  | `TestValidateReferencedFiles.test_*` | REQ-0.25.0-32-03 | Existing files pass; missing files reported; command-like backticks (`uv `, `$`, `git `) skipped; non-path backticks (no `/` or `.`) skipped |
  | `TestValidateHandoffDocument.test_*` | REQ-0.25.0-32-03 | Full orchestration: errors accumulate (fail-closed), clean doc returns empty list |
  | `TestHandoffAbsorptionBrief.test_decision_recorded` | REQ-0.25.0-32-01 | Brief file contains the word "Absorb" in decision section |
  | `TestHandoffAbsorptionBrief.test_rationale_cites_concrete_differences` | REQ-0.25.0-32-02 | Brief rationale mentions airlineops capability gap (6 checks vs 0 in gzkit) |
  | `TestHandoffAbsorptionBrief.test_gate4_na_recorded` | REQ-0.25.0-32-05 | Brief records Gate 4 N/A with rationale |

- REQ-0.25.0-32-04 does not apply (outcome is Absorb, not Confirm/Exclude). Record this in the brief's Acceptance Criteria section.

### Step 3 — Update the spec doc

**Modify:** `docs/governance/GovZero/handoff-validation.md`

- Python API section: change `from gzkit.validate import extract_headers, parse_frontmatter` to `from gzkit.handoff_validation import HandoffFrontmatter, parse_frontmatter, validate_handoff_document`.
- Sources line: change `src/gzkit/validate.py, src/gzkit/interview.py` to `src/gzkit/handoff_validation.py`.
- Tests line: `tests/governance/test_handoff_validation.py` already correct.
- Note the absorption lineage in a "History" section: "Absorbed from airlineops/opsdev/governance/handoff_validation.py via OBPI-0.25.0-32."

### Step 4 — Update the brief

**Modify:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-32-handoff-validation-pattern.md`

- Change frontmatter `status: Pending` → `status: Completed`.
- Note in a "Comparison Target Correction" subsection that the brief's original pointer at `pipeline_dispatch.py / lock_manager.py / interview_cmd.py` was incorrect; the actual comparison target was `core/validation_rules.py` generic helpers + the spec doc. Preserve the correction — this is provenance signal for future readers.
- Populate a "Decision" section: **Absorb**, with rationale citing:
  - gzkit spec at `docs/governance/GovZero/handoff-validation.md` already mandated the capability
  - No existing gzkit implementation of any of the 6 checks (HandoffFrontmatter, placeholder scan, secret scan, required sections, file-ref check — all absent)
  - airlineops already follows gzkit conventions (Pydantic ConfigDict, pathlib, UTF-8, frozen models) — absorption is near-zero adaptation cost
  - The subtraction test passes: handoff validation is not airline-specific
- Populate "Gate 4 (BDD)": **N/A** with rationale "Library function; no operator-visible CLI surface change. `gz validate --documents --surfaces` is not wired to the new module in this OBPI."
- Populate Closing Argument (to be authored at completion with fresh test/lint/typecheck evidence).
- Check all 5 gates in the Completion Checklist.
- Add human attestation line (to be populated at Stage 4).

### Step 5 — Verification

Run in order:

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz covers OBPI-0.25.0-32-handoff-validation-pattern --json
```

All must pass. `gz covers` must report `uncovered_reqs == 0` — Invariant 1b (REQ → @covers parity gate) must hold before Stage 4 presents evidence.

## Critical Files

| Path | Action | Why |
|---|---|---|
| `src/gzkit/handoff_validation.py` | **new** | Absorbed 312L module, the primary deliverable |
| `tests/governance/__init__.py` | **new** | unittest discovery |
| `tests/governance/test_handoff_validation.py` | **new** | TDD coverage for all 6 validators + 5 REQs |
| `docs/governance/GovZero/handoff-validation.md` | **modify** | Correct stale import examples and Sources line |
| `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-32-handoff-validation-pattern.md` | **modify** | Record Absorb decision + rationale + Gate 4 N/A + Closing Argument + comparison-target correction |

## Out of Scope

- Wiring `validate_handoff_document()` into `gz validate --documents --surfaces` — that integration is future work (own OBPI). This OBPI is absorption only.
- Changing `core/validation_rules.parse_frontmatter()` — the generic helper stays as-is. The new module gets its own `parse_frontmatter()` with the handoff-specific fail-closed contract.
- Rewriting `pipeline_dispatch.py` / `lock_manager.py` / `interview_cmd.py` — the brief's misidentification of these as the comparison target is noted in the decision rationale but no code changes are made to them.

## Verification Plan

End-to-end test sequence after implementation:

1. `uv run ruff check . --fix && uv run ruff format .` — code quality clean
2. `uv run gz lint` — gzkit lint clean
3. `uv run gz typecheck` — no type errors (`uvx ty check .`)
4. `uv run gz test` — full unit+BDD suite passes (handoff test tree included in discovery)
5. `uv run -m unittest tests.governance.test_handoff_validation -v` — isolated handoff test run, all cases pass
6. `uv run gz covers OBPI-0.25.0-32-handoff-validation-pattern --json` — parity gate passes, `uncovered_reqs == 0`
7. `uv run gz validate --documents --surfaces` — spec doc and brief both validate
8. `uv run mkdocs build --strict` — docs build clean (Heavy lane requirement)
9. `uv run gz adr status ADR-0.25.0` — shows OBPI-32 as Completed, blocker removed, closeout readiness unblocked (pending only OBPI-33)

Expected end state: ADR-0.25.0 at 32/33 OBPIs complete, with only OBPI-0.25.0-33-arb-analysis-pattern remaining before closeout.
