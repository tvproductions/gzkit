---
id: OBPI-0.25.0-32-handoff-validation-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 32
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-32: Handoff Validation Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-32 — "Evaluate and absorb opsdev/governance/handoff_validation.py (312 lines) — session handoff governance"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/governance/handoff_validation.py` (312 lines)
against gzkit's handoff governance surface and determine: Absorb, Confirm, or
Exclude. The airlineops module covers session handoff governance validation.
gzkit's equivalent surface spans `pipeline_dispatch.py` (556 lines),
`lock_manager.py` (175 lines), and `commands/interview_cmd.py` (243 lines) —
approximately 970+ lines across 3 modules providing handoff result parsing,
work lock management, and session interview logic.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/governance/handoff_validation.py` (312 lines)
- **gzkit equivalent (as authored in this brief):** Distributed across `src/gzkit/pipeline_dispatch.py`, `src/gzkit/lock_manager.py`, `src/gzkit/commands/interview_cmd.py` (~970+ lines total)

### Comparison Target Correction (2026-04-14)

The brief's original pointer at `pipeline_dispatch.py / lock_manager.py /
interview_cmd.py` is **factually incorrect** and has been preserved above for
provenance. Those three modules implement pipeline dispatch, work-lock
management, and interactive interview flows — none of them validate handoff
*documents*. The actual pre-absorption comparison target was:

- `docs/governance/GovZero/handoff-validation.md` — a specification document
  that describes the exact airlineops validator contract (6 fail-closed checks)
  but was written ahead of any implementation.
- `src/gzkit/core/validation_rules.py` — contained only a generic
  `parse_frontmatter()` (tuple return, not Pydantic) and `extract_headers()`
  helper. None of the 6 handoff-specific checks (HandoffFrontmatter schema,
  placeholder scan, secret scan, required-sections check, referenced-file
  existence) existed anywhere under `src/gzkit/`.
- `tests/governance/` — did not exist before this OBPI.

The corrected comparison target is therefore "gzkit had the specification
without the implementation." The decision rationale below is grounded in this
corrected target, not the mis-identified one.

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 3x larger surface suggests more mature handoff handling — comparison will verify

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's pipeline dispatch around airlineops's handoff validation model

## Decision

**Absorb** — the airlineops `handoff_validation.py` module has been ported into
gzkit at `src/gzkit/handoff_validation.py` with minimal adaptation (dual
`@covers` lineage docstring and cross-platform CRLF normalization on every
public validator).

### Rationale

- **Capability gap.** gzkit had zero of the six handoff-document validation
  checks implemented before this OBPI. Specifically missing: `HandoffFrontmatter`
  Pydantic schema, placeholder scan
  (TBD/TODO/FIXME/PLACEHOLDER/XXX/CHANGEME/standalone-ellipsis), secret scan
  (password/secret/token/api_key/Bearer/PRIVATE KEY/sk-*/ghp_*), required
  sections check (the 7 canonical `REQUIRED_SECTIONS`), referenced-file existence
  check, and the orchestrator `validate_handoff_document` that accumulates
  violations fail-closed instead of short-circuiting. The only handoff-adjacent
  code in gzkit before absorption was a generic `parse_frontmatter()` in
  `src/gzkit/core/validation_rules.py` that returns a raw `tuple[dict, str]`
  with no schema validation.
- **Spec-mandated capability.** The governance document
  `docs/governance/GovZero/handoff-validation.md` describes the exact airlineops
  contract as the authoritative gzkit specification. It even references
  `tests/governance/test_handoff_validation.py` as the test file, but that
  directory did not exist. The spec was written ahead of implementation; this
  OBPI closes the gap.
- **Near-zero adaptation cost.** The airlineops source already follows every
  gzkit convention that matters: `BaseModel` with
  `ConfigDict(extra="forbid", frozen=True)`, `from __future__ import
  annotations`, `pathlib.Path`, module-level `re.compile`, no mutable defaults,
  no bare excepts, type hints in modern pythonic form (`str | None`, `list[str]`).
  The only adaptations this OBPI applied are the dual `@covers` lineage and
  CRLF-normalization defensive first-statements.
- **Subtraction test passes.** Handoff document validation is not
  airline-specific governance — it is a generic GovZero capability. The module
  has no knowledge of airline operations, crew scheduling, or any domain-specific
  concept. Every check (placeholder, secret, section, file-ref) is generic
  markdown hygiene that any governed repository needs.
- **Confirm was rejected** because gzkit had none of the 6 checks implemented
  and no test coverage, so the "gzkit is already sufficient" claim is empty.
  **Exclude was rejected** because the spec doc explicitly lives under GovZero
  as a generic governance requirement, not an airline concern.

### Gate 4 (BDD): **N/A**

No operator-visible behavior change. The absorbed module is a **library function
only** — it is not wired into any CLI surface in this OBPI. `gz validate
--documents --surfaces` continues to route through `validate_pkg/document.py`;
integrating `validate_handoff_document()` into that command path is deliberately
out of scope for this absorption. Because there is **no operator-visible CLI
surface change**, no behavioral proof is required. The brief therefore records
`N/A` per the Gate 4 alternative clause.

### Evidence

- **Module:** `src/gzkit/handoff_validation.py` (320 lines, lint-clean, all 10
  public symbols importable).
- **Tests:** `tests/governance/test_handoff_validation.py` (54 tests across 8
  test classes — `TestHandoffFrontmatter`, `TestParseFrontmatter`,
  `TestValidatePlaceholders`, `TestValidateSecrets`, `TestValidateSectionsPresent`,
  `TestValidateReferencedFiles`, `TestValidateHandoffDocument`,
  `TestHandoffAbsorptionBrief`) with `@covers` decorators tying every test to
  REQ-0.25.0-32-01/02/03/05. REQ-0.25.0-32-04 is N/A because the decision is
  Absorb, not Confirm/Exclude.
- **Spec doc update:** `docs/governance/GovZero/handoff-validation.md` Python
  API section and Sources line corrected to reference the new module path.
- **Provenance docstring:** the ported module carries both `@covers ADR-0.0.25
  (OBPI-0.0.25-06)` (airlineops origin) and `@covers ADR-0.25.0 (OBPI-0.25.0-32)`
  (gzkit absorption) so lineage is recoverable.

### Comparison Matrix

| Dimension | airlineops (pre-absorption) | gzkit (pre-absorption) | gzkit (post-absorption) |
|---|---|---|---|
| HandoffFrontmatter Pydantic model | Present | Absent | Present (verbatim) |
| Placeholder scan (6 tokens + ellipsis) | Present | Absent | Present (verbatim) |
| Secret scan (8 patterns) | Present | Absent | Present (verbatim) |
| REQUIRED_SECTIONS check (7 sections) | Present | Absent | Present (verbatim) |
| Referenced-file existence check | Present | Absent | Present (verbatim) |
| Fail-closed orchestrator | Present | Absent | Present (verbatim) |
| CRLF cross-platform normalization | Absent | N/A | **Added** (gzkit adaptation) |
| Test coverage | Implied (upstream) | None | 54 tests, @covers parity |
| Spec doc alignment | N/A | Specced but not implemented | Specced and implemented |

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.25.0-32-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-32-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-32-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-32-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-32-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/governance/handoff_validation.py
# Expected: airlineops source under review exists

test -f src/gzkit/pipeline_dispatch.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-32-handoff-validation-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

### Value Narrative

Before this OBPI, gzkit had a complete specification at
`docs/governance/GovZero/handoff-validation.md` mandating six fail-closed
handoff-document validation checks, but zero of them were implemented. After
this OBPI, `gzkit.handoff_validation` ships the full six-check module absorbed
from airlineops with dual `@covers` lineage and CRLF normalization added for
Windows cross-platform safety, and `tests/governance/test_handoff_validation.py`
anchors all 5 REQs via `@covers` parity with 55 tests across 8 classes.

### Key Proof


```text
$ uv run gz covers OBPI-0.25.0-32 --json | jq '.summary'
{
  "identifier": "OBPI-0.25.0-32",
  "total_reqs": 5,
  "covered_reqs": 5,
  "uncovered_reqs": 0,
  "coverage_percent": 100.0
}

$ uv run -m unittest tests.governance.test_handoff_validation -q
Ran 55 tests in 0.007s
OK
```

Paired with `uv run gz test` → 2893 unit tests OK, 17/17 behave features passed,
110/110 scenarios passed (10.5s total).

### Implementation Summary


- Files created/modified:
  - `src/gzkit/handoff_validation.py` (new, 320 lines, absorbed from airlineops
    with dual `@covers` lineage and CRLF normalization on all 7 public
    validators)
  - `tests/governance/__init__.py` (new, package marker)
  - `tests/governance/test_handoff_validation.py` (new, 55 tests across 8
    classes with `@covers` parity for REQ-01/02/03/04/05)
  - `docs/governance/GovZero/handoff-validation.md` (modified, Python API
    section corrected, Sources updated, History section added)
  - `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-32-handoff-validation-pattern.md`
    (modified, Decision section + Comparison Target Correction + Gate 4 N/A +
    Closing Argument)
- Tests added: 55 across `TestHandoffFrontmatter`, `TestParseFrontmatter`,
  `TestValidatePlaceholders`, `TestValidateSecrets`, `TestValidateSectionsPresent`,
  `TestValidateReferencedFiles`, `TestValidateHandoffDocument`,
  `TestHandoffAbsorptionBrief`
- Date completed: 2026-04-14
- Attestation status: Attested by Jeffry (ahuimanu@gmail.com) at Stage 4 gate
- Defects noted: Brief's original `gzkit equivalent` pointer at
  `pipeline_dispatch.py / lock_manager.py / interview_cmd.py` was factually
  incorrect; corrected in `### Comparison Target Correction` section above.
  No new defects tracked.

## Human Attestation

- Attestor: `Jeffry (ahuimanu@gmail.com)`
- Attestation: attest completed — Absorb decision for airlineops/opsdev/governance/handoff_validation.py (312L). Ported to src/gzkit/handoff_validation.py (320L) with dual @covers lineage and CRLF normalization on all 7 validators. 55 tests green, 5/5 REQs covered, 2893 unit tests OK, 17/17 behave features. Gate 4 N/A (library function, no operator-visible CLI change). ARB receipts unavailable — OBPI-0.25.0-33 is arb-analysis.
  `airlineops/opsdev/governance/handoff_validation.py` (312L). Ported to
  `src/gzkit/handoff_validation.py` (320L) with dual `@covers` lineage
  (ADR-0.0.25 provenance + ADR-0.25.0 absorption) and CRLF normalization on
  all 7 public validators per `.gzkit/rules/cross-platform.md`. Tests at
  `tests/governance/test_handoff_validation.py` (55 tests across 8 classes).
  Direct evidence captured this session: `gz lint`/`typecheck` clean;
  `gz test` green (2893 unit tests OK, 17/17 behave features, 110/110
  scenarios); `gz covers OBPI-0.25.0-32` → 5/5 REQs covered at 100%;
  `gz validate --documents --surfaces` → 2 scopes passed; `mkdocs build
  --strict` → clean in 2.10s. Gate 4 N/A (library function; no
  operator-visible CLI surface change — wiring into `gz validate` is a
  future OBPI). Decision rejected: Confirm (gzkit had 0/6 checks); Exclude
  (handoff validation is generic GovZero, not airline-specific). ARB
  receipts unavailable — ARB infrastructure is itself the target of
  OBPI-0.25.0-33, not yet absorbed into gzkit; concrete command output
  substituted per attestation-enrichment rule spirit.
- Date: 2026-04-14

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass — `tests/governance/test_handoff_validation.py` with 54 tests across 8 classes, all `@covers`-anchored to REQ-0.25.0-32-01/02/03/05
- [x] **Gate 3 (Docs):** Decision rationale completed (see `## Decision` section above)
- [x] **Gate 4 (BDD):** **N/A** — library function only; no operator-visible CLI surface change (no external-surface change). Rationale in `## Decision` Gate 4 subsection.
- [ ] **Gate 5 (Human):** Attestation recorded (pending Stage 4 ceremony)

## Closing Argument

OBPI-0.25.0-32 absorbs `airlineops/opsdev/governance/handoff_validation.py`
(312 lines) into `src/gzkit/handoff_validation.py` (320 lines after two
adaptations) and adds the missing `tests/governance/test_handoff_validation.py`
tree (54 tests, 8 classes, `@covers`-parity with REQ-01/02/03/05).

The decision is **Absorb** rather than Confirm or Exclude because gzkit had
already written the specification at `docs/governance/GovZero/handoff-validation.md`
describing this exact validator contract, while implementing **zero** of its
six fail-closed checks: `HandoffFrontmatter` Pydantic schema, placeholder scan,
secret scan, required-sections check, referenced-file existence, and the
fail-closed orchestrator. The generic `parse_frontmatter()` helper in
`core/validation_rules.py` returns a raw tuple and performs no schema
validation; it is not a handoff validator.

The absorbed module ships with near-zero adaptation cost. airlineops already
used Pydantic `BaseModel` with `ConfigDict(extra="forbid", frozen=True)`,
`pathlib.Path`, `from __future__ import annotations`, and module-level
`re.compile`. The only gzkit adaptations are: (a) dual `@covers` lineage in the
module docstring, preserving the original `@covers ADR-0.0.25 (OBPI-0.0.25-06)`
provenance and adding `@covers ADR-0.25.0 (OBPI-0.25.0-32)` absorption; and
(b) CRLF normalization (`content = content.replace("\r\n", "\n")`) as the
first executable statement in every public validator function, as required by
`.gzkit/rules/cross-platform.md` for any content flowing through `re.MULTILINE`
patterns on Windows hosts.

Gate 4 (BDD) is **N/A** with explicit rationale: the absorbed module is a
**library function only** — it is not wired into any CLI surface in this OBPI.
`gz validate --documents --surfaces` continues to route through
`validate_pkg/document.py`; wiring `validate_handoff_document()` into that
command path is a future integration task with its own OBPI. Because there is
**no operator-visible CLI surface change** and **no external-surface change**,
no behavioral proof is required.

A notable provenance artifact of this OBPI is the **Comparison Target
Correction** section above. The brief's original "gzkit equivalent" pointer
at `pipeline_dispatch.py / lock_manager.py / interview_cmd.py` was factually
incorrect — those modules handle pipeline dispatch, work-lock management, and
interactive interview flows, not handoff-document validation. The Stage 1
subagent sweep surfaced the discrepancy; the corrected comparison target (spec
doc present, implementation absent) is what the decision rationale is grounded
in. The incorrect pointer is preserved in the brief so future readers can
trace the provenance of the correction.

Post-absorption state: ADR-0.25.0 moves from 31/33 to 32/33 OBPIs complete.
Only `OBPI-0.25.0-33-arb-analysis-pattern` remains before closeout.
