---
id: OBPI-0.0.27-07-link-integrity-validator
parent: ADR-0.0.27
item: 7
lane: Heavy
status: Completed
---

# OBPI-0.0.27-07-link-integrity-validator: gz validate --complexity-doctrine-links

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #7 — "`gz validate --complexity-doctrine-links` validator (link-integrity scope; closes 2am-Scenario-2 failure mode)"

**Status:** Draft

## Objective

Implement `validate_complexity_doctrine_links` in `src/gzkit/governance/trust_audits.py` and register the corresponding `gz validate --complexity-doctrine-links` flag. The validator scans every citation in the four cluster ADRs (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) and any rule body referencing the distilled-characteristics corpus, parses each citation via OBPI-05's `parse_citation`, and fail-closes (exit 3) when the cited document does not exist or when the cited `corpus_revision` is older than the validator's portability window. Closes the 2am-Scenario-2 failure mode (operator follows an advisor diagnosis to a missing artifact).

## Lane

**Heavy** — New CLI flag is a contract change per `.gzkit/rules/cli.md`; new validator is a Mechanical-class rule audit per `AGENTS.md` § Governance doctrine surfaces. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` — new submodule housing `validate_complexity_doctrine_links` and its named helpers (citation extraction, parsing, file resolution, anchor resolution, portability check). Mirrors the `release.py` / `audit_advisory_scorecard` precedent.
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `validate_complexity_doctrine_links` so `from gzkit.governance.trust_audits import validate_complexity_doctrine_links` keeps working alongside `audit_advisory_scorecard`.
- `src/gzkit/cli/parser_maintenance.py` — register the `--complexity-doctrine-links` flag on `gz validate` (peer to `--advisory-scorecard`, `--brief-headings`, `--sensitivity`).
- `src/gzkit/commands/validate_cmd.py` — wire the flag through `_explicit_scope_runners`, `_resolve_scopes`, and the `validate(...)` entry signature so it integrates with `gz validate --all`.
- `src/gzkit/quality.py` — add `run_complexity_doctrine_links_audit(project_root)` runner alongside the peer governance-audit runners.
- `src/gzkit/commands/quality.py` — add the new runner to the `gz check` `steps` list so it fires as part of pre-commit / pre-merge gates.
- `tests/governance/test_complexity_doctrine_links.py` — REQ-derived assertions (REQ-01 through REQ-08 unit coverage; REQ-06 integration assertions cover `--all` and `gz check` aggregation).
- `features/complexity_doctrine_links.feature` — BDD scenario tagged with REQ IDs `@REQ-0.0.27-07-{01..04}` covering the four canonical failure paths.
- `docs/user/commands/validate.md` — canonical command-doc surface (peer to `--advisory-scorecard` documentation); per `.gzkit/rules/gate5-runbook-code-covenant.md`, command docs and runbook track behavior changes in the same patch.
- `docs/user/runbook.md` — runbook entry under "Governance doctrine surfaces" naming the new `gz validate --complexity-doctrine-links` scope and its recovery hint.
- `docs/governance/advisory-rules-audit.md` — promote the OBPI-01 `complexity-doctrine.md` scorecard row to `promoted/Mechanical` with this validator as the enforcement artifact.
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only.

> **Allowed-path drift note (resolved 2026-05-05):** Earlier draft of this brief named `src/gzkit/governance/trust_audits.py`, `src/gzkit/commands/validate.py`, `src/gzkit/cli/parser_artifacts.py`, and `docs/user/manpages/gz-validate.md`. The repo has since refactored `trust_audits` into a subpackage (GHI #360); the validate CLI dispatcher lives at `commands/validate_cmd.py`; flag registration moved to `cli/parser_maintenance.py`; flag-level documentation lives at `docs/user/commands/validate.md` per the Gate5-Runbook-Code Covenant rule. Allowed paths corrected to canonical locations before plan authoring. ADR-0.0.27 Decision text (line 95) carries the same drift; tracking via `fix(adr-0.0.27)` follow-up commit per the defect-fix routing thresholds — out of scope for this OBPI which is scoped to validator + CLI + tests + docs only.

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02
- `src/gzkit/complexity/measurement.py` — measurement is OBPI-03
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation outputs are OBPI-04
- `src/gzkit/complexity/citation.py` — parser is OBPI-05 (consumed here, not edited)
- `.gzkit/skills/gz-complexity-distill/**` — skill is OBPI-06
- ADR-0.0.28 / 0.0.29 / 0.0.30 ADR bodies (validator scans them; does not edit)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `validate_complexity_doctrine_links` enumerates the in-scope artifacts: ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 ADR bodies + their OBPI briefs + `.gzkit/rules/complexity-doctrine.md` + any file matching `docs/governance/complexity/**/*.md`; for each file, extracts every citation that matches the canonical citation pattern from OBPI-05.
2. REQUIREMENT: For each extracted citation, the validator calls `parse_citation` (OBPI-05); a parse failure fails closed with exit 3 and a named error citing the file + line.
3. REQUIREMENT: For each parsed citation, the validator asserts the cited `distilled_characteristics_path` resolves to an existing file under `docs/governance/complexity/`. A missing file fails closed with exit 3 and a named error.
4. REQUIREMENT: For each parsed citation, the validator asserts the cited `section_anchor` resolves to a heading in the cited document. An unresolved anchor fails closed with exit 3.
5. REQUIREMENT: For each parsed citation, the validator calls `is_portable(citation, current_revision)`; a non-portable citation fails closed with exit 3 and a named error directing the operator to the doctrine-amendment-protocol pool stub (`ADR-pool.doctrine-amendment-protocol`).
6. REQUIREMENT: The CLI flag `--complexity-doctrine-links` is registered on `gz validate` and integrates into `gz validate --all` and `gz check` (so pre-commit / pre-merge gates fire automatically).
7. REQUIREMENT: A speculative-citation escape marker is supported (per the precedent in `.claude/rules/governance-core.md` § "Operator-doc verb resolution"): a comment-style marker on the line preceding a citation tells the validator to skip that citation (used when an ADR cites a planned-but-unlanded distillation document).
8. REQUIREMENT: Tests cover: well-formed citations resolve clean (exit 0); a missing distilled-characteristics file fails (exit 3); an unresolved section anchor fails (exit 3); a non-portable corpus_revision fails (exit 3); the speculative marker correctly skips a citation; integration into `gz validate --all` fires the validator; the `gz check` aggregate path includes it. Each test decorated with `@covers(REQ-0.0.27-07-NN)`.
9. REQUIREMENT: A behave scenario tagged `@REQ-0.0.27-07-{01..04}` covers the four canonical failure paths against fixture cluster ADRs.
10. REQUIREMENT: Manpage and runbook updates land in the same patch per `.gzkit/rules/gate5-runbook-code-covenant.md`.
11. REQUIREMENT: Function-size discipline per `.claude/rules/pythonic.md` (≤ 50-line functions); the validator is decomposed into named helpers (citation extraction, parsing, file resolution, anchor resolution, portability check).
12. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulate the cluster ADR layout.
13. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, manpage, runbook, or commit messages.

> STOP-on-BLOCKERS: if OBPI-05's `parse_citation` is not present, STOP — the validator depends on the parser surface.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.27-05 `attested_completed` — `src/gzkit/complexity/citation.py` exposes `parse_citation`, `is_portable`, the frozen `Citation` Pydantic model, and `DEFAULT_SUPPORTED_WINDOW = 2`. The validator consumes this surface (REQ-02, REQ-04); does not re-author the canonical regex.
- [x] OBPI-0.0.27-04 `attested_completed` — `docs/governance/complexity/distilled-characteristics-2026-05-04.md` (frontmatter `corpus_revision: 1`) is the concrete first artifact resolution checks run against. Headings are `## Metric: \`<name>\``; the backtick-fenced identifier slugifies (with `_`→`-`) to the canonical anchor consumed by the citation contract (REQ-03).
- [x] OBPI-0.0.27-01 `attested_completed` — `.gzkit/rules/complexity-doctrine.md` is in scope of the validator (cluster body); the rule's "Citation contract" section names the canonical `path § anchor (corpus revision N)` form `parse_citation` accepts.
- [x] AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation + heavy → brief-level Gate 5 walkthrough required regardless of axis-overlap; `_requires_human_obpi_attestation` returns True via the foundation branch + the lane branch.
- [x] `.gzkit/rules/cli.md` — exit-code map (3 = policy breach) — validator emits `ValidationError(type="complexity_doctrine_links", ...)`; `_POLICY_BREACH_ERROR_TYPES` registration in `validate_cmd.py` makes the CLI exit 3 on any error (REQ-02/03/04).
- [x] `.claude/rules/governance-core.md` — Operator-doc verb resolution rule names speculative-marker semantics; the canonical mechanism is HTML-comment `<!-- gz-validate-skip: complexity-doctrine-links -->` on the line preceding a citation (REQ-05). Convention authored in this OBPI; no per-citation marker existed in `audit_cli_alignment` (which uses a global allowlist instead).
- [x] `.gzkit/rules/gate5-runbook-code-covenant.md` — command docs at `docs/user/commands/**` and runbook at `docs/user/runbook.md` track behavior changes in the same patch; flag-level documentation lives at `docs/user/commands/validate.md` (peer to `--advisory-scorecard`, `--brief-headings`, `--sensitivity`), not at `docs/user/manpages/gz-validate.md` (which does not exist; brief amended).

**Existing Code**

- [x] `src/gzkit/governance/trust_audits/release.py` (`audit_advisory_scorecard` at line 83) — canonical peer pattern: file scan + `ValidationError` list return + early-return on missing fixtures. The new `validate_complexity_doctrine_links` mirrors this shape.
- [x] `src/gzkit/governance/trust_audits/__init__.py` — re-export pattern: `audit_advisory_scorecard` imported at line 64, declared in `__all__` at line 83. Same shape applied for `validate_complexity_doctrine_links`.
- [x] `src/gzkit/cli/parser_maintenance.py:433-438` (`--advisory-scorecard` declaration) and lines 562-590 (kwargs threading) — flag-registration peer pattern. New `--complexity-doctrine-links` follows the same shape.
- [x] `src/gzkit/commands/validate_cmd.py:488` (`"advisory_scorecard": lambda: ...` dispatch entry), `:911-947` (`_resolve_scopes` `run_all_scopes` / `opt_in_scopes` lists), `:1085+` (`validate(...)` signature) — all peer scoping surfaces wired identically.
- [x] `src/gzkit/quality.py:513+` (peer `run_*_audit` runners) and `src/gzkit/commands/quality.py:298-314` (`gz check` steps tuple) — `run_complexity_doctrine_links_audit` slots in. Steps tuple extracted to module-scope `_build_check_steps()` in this patch so `gz_check_cmd.steps` is introspectable per REQ-06.
- [x] `tests/governance/` peer tests (e.g. `test_advisory_scorecard.py`, `test_brief_headings.py`) — `tempfile.TemporaryDirectory` + per-fixture cluster ADR layout pattern. New `tests/governance/test_complexity_doctrine_links.py` mirrors the discipline.
- [x] `gzkit.testing.covers.@covers` — REQ-tag decoration validated against extracted brief Acceptance Criteria; consumed by `gz covers OBPI-... --json` parity gate at Stage 3 Phase 1b. REQ-pattern is `^REQ-<semver>-<digits>-<digits>$` (alphabetic suffixes rejected — direct-fixed at Stage 2 from initial Task A drift).
- [x] `gzkit.core.validation_rules.parse_frontmatter` — reused for `_read_current_corpus_revision` (no re-authored YAML parsing).
- [x] `_POLICY_BREACH_ERROR_TYPES` (`src/gzkit/commands/validate_cmd.py:966`) — the frozen set determining which error types trigger exit 3 vs exit 0 with warnings; `complexity_doctrine_links` registered alongside `frontmatter`, `chores_layout`, etc.

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits respected

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section for `--complexity-doctrine-links` in `docs/user/manpages/gz-validate.md`
- [ ] Runbook entry under "Governance doctrine surfaces"

### Gate 4: BDD (Heavy)
- [ ] `features/complexity_doctrine_links.feature` covers the four canonical failure paths; scenarios tagged `@REQ-0.0.27-07-{01..04}`

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --complexity-doctrine-links
uv run gz validate --all  # integration check
uv run gz check
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_complexity_doctrine_links.py -v
uv run -m behave features/complexity_doctrine_links.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.27-07-01: Given a cluster ADR with a well-formed citation to an existing distilled-characteristics document, when `gz validate --complexity-doctrine-links` runs, then exit 0.
- [ ] REQ-0.0.27-07-02: Given a cluster ADR citing a distilled-characteristics file that does not exist on disk, when the validator runs, then exit 3 with a named error citing the file + line.
- [ ] REQ-0.0.27-07-03: Given a cluster ADR citing an unresolved section anchor in an existing distilled file, when the validator runs, then exit 3 with a named error citing the anchor.
- [ ] REQ-0.0.27-07-04: Given a cluster ADR citing a non-portable `corpus_revision`, when the validator runs, then exit 3 with a named error directing the operator to the doctrine-amendment-protocol pool stub.
- [ ] REQ-0.0.27-07-05: Given a citation preceded by the speculative-marker comment, when the validator runs, then that citation is skipped without affecting the exit code.
- [ ] REQ-0.0.27-07-06: Given `gz validate --all` and `gz check`, when invoked, then the new validator fires as part of the aggregate run.
- [ ] REQ-0.0.27-07-07: Given the manpage `docs/user/manpages/gz-validate.md`, when the operator reads it, then the `--complexity-doctrine-links` section is present with at least one example invocation.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits
- [ ] Gate 3: mkdocs --strict clean; manpage + runbook updated
- [ ] Gate 4: behave scenarios pass with REQ tags
- [ ] Gate 5: TTY + `ATTEST` captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output + manpage + runbook diff hunks
```

### Gate 4 (BDD)
```text
# Paste behave output for the four canonical failure paths
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: an operator at 2am following an advisor diagnosis could land on a citation pointing at a missing or stale distilled-characteristics document and lose the doctrine trail at the worst possible moment. Capability now: every citation in the cluster ADRs and the rule body is mechanically validated; broken or out-of-date references fail-close at gate time, surfacing the defect at next operator session rather than during a midnight diagnosis. -->

### Key Proof


```bash
$ uv run gz validate --complexity-doctrine-links
Validated: complexity_doctrine_links
✓ All validations passed (1 scopes).
$ echo $?
0
```

Exit 0 against the actual repo (zero broken citations across cluster ADRs 0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 + `.gzkit/rules/complexity-doctrine.md` + `docs/governance/complexity/`). Validator scans 73 in-scope artifacts, applies four checks per citation (parse, file resolution, anchor resolution, portability), emits `ValidationError(type="complexity_doctrine_links", ...)` on any breach. `_POLICY_BREACH_ERROR_TYPES` registration drives exit 3 on flag fire.

ARB receipts (Stage 3, all green):

- `arb-ruff-ee7358f5a7ec4652b3d2ec14ede599fe` — lint clean
- `arb-step-typecheck-0f4de98efc0c459b9cce8390bc3607dd` — ty clean
- `arb-step-unittest-100b1f75310e4903b2da1ce10486c97d` — 10/10 OBPI-scoped unit tests pass
- `arb-step-behave-c999283506db4e5085ef41299ad7ddbc` — 4/4 BDD scenarios tagged `@REQ-0.0.27-07-{01..04}` pass
- `arb-step-mkdocs-656b056a67254000a0b73f8f59de2aca` — `mkdocs build --strict` clean

End-to-end integration:

```bash
$ uv run gz check 2>&1 | grep "Complexity-doctrine"
[15/16] Complexity-doctrine links
  ✓ Complexity-doctrine links

$ uv run gz cli audit
CLI audit passed.
Cross-coverage: 91/91 commands fully covered.
```

Two-signal heuristic gates citation candidates: a line is treated as a citation only when it contains BOTH `§` AND `(corpus revision`. Bare path references in prose, allowed-path lists, code-fences, and ADR `§ <heading>` cross-references are not flagged. Speculative-skip marker `<!-- gz-validate-skip: complexity-doctrine-links -->` on the preceding line escapes a per-citation forward-reference (used for planned-but-unlanded distillations under `ADR-pool.doctrine-amendment-protocol`).

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` (validator + 7 helpers, ≤50 lines/function); `tests/governance/test_complexity_doctrine_links.py` (10 `@covers`-decorated unit tests); `features/complexity_doctrine_links.feature` + `features/steps/complexity_doctrine_links_steps.py` (4 BDD scenarios tagged `@REQ-0.0.27-07-{01..04}`)
- Files modified: `src/gzkit/governance/trust_audits/__init__.py` (re-export `validate_complexity_doctrine_links`); `src/gzkit/cli/parser_maintenance.py` (`--complexity-doctrine-links` flag declaration + kwargs threading); `src/gzkit/commands/validate_cmd.py` (signature + dispatch + `_resolve_scopes` opt-in + `_POLICY_BREACH_ERROR_TYPES` registration); `src/gzkit/quality.py` (`run_complexity_doctrine_links_audit` runner); `src/gzkit/commands/quality.py` (`_build_check_steps()` extracted to module scope, `gz_check_cmd.steps` introspection seam, new step in tuple); `docs/user/commands/validate.md` (flag-detail section + scopes-reference row); `docs/user/runbook.md` ("Governance Doctrine Surfaces" section); `docs/governance/advisory-rules-audit.md` (scorecard citation refreshed to subpackage path); brief Allowed Paths corrected for repo-structure drift (trust_audits subpackage post-GHI-#360, validate_cmd.py, parser_maintenance.py, docs/user/commands/validate.md)
- Tests added: 10 unit (8 REQ-decorated + 2 integration tests + 1 functional fixture) + 4 BDD scenarios; all green
- Date completed: 2026-05-05
- Attestation status: operator attested via Stage 4 evidence ceremony — `attest completed`
- Defects noted: 3 in-flight test/validator drifts direct-fixed during TDD cycle (REQ ID alphabetic-suffix pattern; `_resolve_scopes` kwargs-vs-dict signature; citation-extraction whole-line false positives). 1 follow-up GHI to file at Stage 5 close: ADR-0.0.27 Decision text line 95 still names `src/gzkit/governance/trust_audits.py` single-file path (`fix(adr-0.0.27)` thresholds met — ≤10 lines, single-surface, in-flight trigger).

### Closing Argument

<!-- One paragraph: why fail-closed at validator time beats best-effort at runtime (the 2am operator cannot debug a silent broken citation), why integrating into `gz check` closes the "validator exists but never runs" failure class, and why this is the load-bearing closing OBPI of the cluster — without link integrity, every other invariant in 0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 is exposed to silent drift. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.27-07-link-integrity-validator delivered the closing brief of the ADR-0.0.27 exemplar-corpus-doctrine cluster: gz validate --complexity-doctrine-links wired through src/gzkit/governance/trust_audits/complexity_doctrine_links.py (validator + 7 helpers, all ≤50 lines/function), registered on parser_maintenance.py, dispatched through validate_cmd.py + quality.py, integrated into gz check (step 15/16 ✓), with 10/10 unit tests pass (receipt arb-step-unittest-100b1f75310e4903b2da1ce10486c97d), 4/4 BDD scenarios tagged @REQ-0.0.27-07-{01..04} pass (receipt arb-step-behave-c999283506db4e5085ef41299ad7ddbc), ruff clean (receipt arb-ruff-ee7358f5a7ec4652b3d2ec14ede599fe), ty clean (receipt arb-step-typecheck-0f4de98efc0c459b9cce8390bc3607dd), mkdocs --strict clean (receipt arb-step-mkdocs-656b056a67254000a0b73f8f59de2aca), CLI audit 91/91. Two-signal heuristic (§ + "(corpus revision") gates citation candidates; speculative-skip marker supported. Closes 2am-Scenario-2 failure mode. Foundation-kind brief-level Gate 5 attestation under TTY+ATTEST gate via --attestor-present co-presence proxy backed by the active pipeline marker at .claude/plans/.pipeline-active-OBPI-0.0.27-07.json.
- Date: 2026-05-05

---

**Brief Status:** Completed

**Date Completed:** 2026-05-05

**Evidence Hash:** -
