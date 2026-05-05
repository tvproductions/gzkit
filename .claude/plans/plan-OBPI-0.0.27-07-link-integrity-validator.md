# Plan: OBPI-0.0.27-07 — `gz validate --complexity-doctrine-links` link-integrity validator

**OBPI:** OBPI-0.0.27-07-link-integrity-validator
**Parent ADR:** ADR-0.0.27-exemplar-corpus-doctrine
**Lane:** Heavy (Foundation-kind brief-level Gate 5 attestation)
**Date:** 2026-05-05
**Active persona:** `pipeline-orchestrator` (post-plan execution)

## Context

OBPI-07 is the closing OBPI of the ADR-0.0.27 exemplar-corpus-doctrine cluster. OBPIs 01–06 landed:

- **OBPI-01:** `.gzkit/rules/complexity-doctrine.md` — selection methodology, criteria, anti-patterns, refresh cadence, project-doctrine fitness, citation contract
- **OBPI-02:** `data/exemplar_corpus.json` — pinned corpus + Pydantic schema
- **OBPI-03:** `src/gzkit/complexity/measurement.py` — measurement pipeline
- **OBPI-04:** `docs/governance/complexity/distilled-characteristics-2026-05-04.md` — first distilled-characteristics document
- **OBPI-05:** `src/gzkit/complexity/citation.py` — `parse_citation` and `is_portable` (the parser surface OBPI-07 consumes)
- **OBPI-06:** `.gzkit/skills/gz-complexity-distill/` — skill driving distillation cadence

OBPI-07 closes the cluster by wiring a fail-closed link-integrity validator that scans every citation in the four cluster ADRs (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) and the rule body, parses each via OBPI-05's `parse_citation`, and verifies the cited document, anchor, and corpus revision all resolve. Closes the 2am-Scenario-2 failure mode (operator follows an advisor diagnosis to a missing artifact).

### Anchor evidence (already validated)

- **Brief allowed paths corrected** — original brief named `src/gzkit/governance/trust_audits.py`, `src/gzkit/commands/validate.py`, `src/gzkit/cli/parser_artifacts.py`, `docs/user/manpages/gz-validate.md`. Repo has refactored: `trust_audits` is now a subpackage (GHI #360); `commands/validate_cmd.py` holds the dispatcher; `cli/parser_maintenance.py` registers `--<scope>` flags; flag-level docs land at `docs/user/commands/validate.md`. Brief amended in this same patch before plan authoring.
- **Canonical pattern source:** `audit_advisory_scorecard` at `src/gzkit/governance/trust_audits/release.py:83-113` (file scan, fail-closed exit 3 via `ValidationError` list return, re-export through `trust_audits/__init__.py:64,83`).
- **Dispatch wiring source:** `src/gzkit/commands/validate_cmd.py:488` (`"advisory_scorecard": lambda: trust_audits.audit_advisory_scorecard(project_root)`), parallel for `_resolve_scopes` at lines 911-947, `--all` umbrella at line 935.
- **Flag registration source:** `src/gzkit/cli/parser_maintenance.py:433-438` (`--advisory-scorecard` declaration; `dest="check_advisory_scorecard"`).
- **`gz check` integration source:** `run_*_audit` runner pattern in `src/gzkit/quality.py:513-579`; `steps` list in `src/gzkit/commands/quality.py:298-314`.
- **Confidence:** ≥ 90% — every code surface this plan touches has a canonical peer pattern in the same package. Skip the `gz justify` walkthrough; proceed to Stage 2.

## Allowed paths (canonical)

Per the corrected brief allowed-paths section:

1. `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` (NEW)
2. `src/gzkit/governance/trust_audits/__init__.py` (re-export only)
3. `src/gzkit/cli/parser_maintenance.py` (flag registration + dest threading)
4. `src/gzkit/commands/validate_cmd.py` (dispatch + `_resolve_scopes` + `validate(...)` signature)
5. `src/gzkit/quality.py` (new `run_complexity_doctrine_links_audit` runner)
6. `src/gzkit/commands/quality.py` (add to `gz check` `steps` list)
7. `tests/governance/test_complexity_doctrine_links.py` (NEW)
8. `features/complexity_doctrine_links.feature` (NEW)
9. `docs/user/commands/validate.md` (canonical command doc — flag section)
10. `docs/user/runbook.md` (governance-doctrine-surfaces entry)
11. `docs/governance/advisory-rules-audit.md` (promote OBPI-01 row to `promoted/Mechanical`)
12. `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` (brief evidence updates only)

## Files to be authored / edited

| File | Action | Lines (est.) |
|---|---|---|
| `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` | CREATE | ~250 (5 helpers + main, all ≤ 50 lines/function per `.claude/rules/pythonic.md`) |
| `src/gzkit/governance/trust_audits/__init__.py` | EDIT | +2 lines (import + `__all__`) |
| `src/gzkit/cli/parser_maintenance.py` | EDIT | +6 lines (flag declaration + `dest` threading in `check_kwargs`) |
| `src/gzkit/commands/validate_cmd.py` | EDIT | +6 lines (dispatch dict entry, `_resolve_scopes` `run_all_scopes` entry, `validate(...)` signature flag, `_collect_errors` checks dict) |
| `src/gzkit/quality.py` | EDIT | +12 lines (`run_complexity_doctrine_links_audit` runner mirroring `run_advisory_scorecard_audit`) |
| `src/gzkit/commands/quality.py` | EDIT | +2 lines (steps tuple entry + import) |
| `tests/governance/test_complexity_doctrine_links.py` | CREATE | ~300 (8 REQ-decorated test methods + 1 integration test class) |
| `features/complexity_doctrine_links.feature` | CREATE | ~80 (4 scenarios tagged `@REQ-0.0.27-07-{01..04}`) |
| `docs/user/commands/validate.md` | EDIT | +30 (flag section with example) |
| `docs/user/runbook.md` | EDIT | +5 (entry under "Governance doctrine surfaces") |
| `docs/governance/advisory-rules-audit.md` | EDIT | promote OBPI-01 entry score `Promotable → promoted/Mechanical`; add validator citation |
| OBPI brief evidence sections | EDIT | populate Implementation Summary / Key Proof / Closing Argument at Stage 4 |

## Steps (TDD discipline; helpers before main)

### Step 1: RED — author REQ-derived unit tests

Create `tests/governance/test_complexity_doctrine_links.py` with 8 test methods, each `@covers("REQ-0.0.27-07-NN")`. Use `tempfile.TemporaryDirectory` to simulate cluster-ADR layout: a fake project root with `docs/design/adr/foundation/ADR-0.0.27/` ADR file, `docs/governance/complexity/distilled-characteristics-2026-05-04.md` with anchored sections, and `.gzkit/rules/complexity-doctrine.md`.

Test methods:

- `test_well_formed_citation_resolves_clean` (REQ-01): Given a cluster ADR with a well-formed citation to an existing file + anchor + portable revision, validator returns `[]`.
- `test_missing_distilled_file_fails_closed` (REQ-02): Given a citation pointing at `distilled-characteristics-1999-01-01.md` (does not exist), validator returns one `ValidationError` with type `complexity_doctrine_links` and a message naming the file + line number.
- `test_unresolved_anchor_fails_closed` (REQ-03): Given a citation with an anchor that does not match any heading in the cited file, validator returns one error naming the anchor.
- `test_non_portable_revision_fails_closed` (REQ-04): Given a citation with `corpus_revision = N - 2` (outside the supported window), validator returns one error directing to `ADR-pool.doctrine-amendment-protocol`.
- `test_speculative_marker_skips_citation` (REQ-05): Given a citation preceded by `<!-- gz-validate-skip: complexity-doctrine-links -->`, validator returns `[]`.
- `test_validate_all_includes_complexity_doctrine_links` (REQ-06a): Confirm `_resolve_scopes` returns `complexity_doctrine_links` when `run_all=True`.
- `test_gz_check_steps_includes_runner` (REQ-06b): Confirm `gz check` `steps` list includes `("Complexity-doctrine links", run_complexity_doctrine_links_audit)`.
- `test_parse_failure_fails_closed` (REQ-02 corollary): Given a citation that does not match the canonical pattern, validator returns one error with `parse-failure` shape (file + line).

All tests fail (RED).

### Step 2: GREEN — author validator helpers

Create `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` with 5 named helpers (all ≤ 50 lines per `.claude/rules/pythonic.md`):

```python
# Module shape (skeletal):
_CITATION_PATTERN = re.compile(...)  # mirrors _CANONICAL_PATTERN from citation.py
_SPECULATIVE_MARKER = "<!-- gz-validate-skip: complexity-doctrine-links -->"

def _enumerate_in_scope_artifacts(project_root: Path) -> list[Path]:
    """ADR-0.0.27..30 ADR bodies + their OBPI briefs + .gzkit/rules/complexity-doctrine.md +
    docs/governance/complexity/**/*.md (excluding the distilled-characteristics
    documents themselves, which are the targets, not the sources)."""

def _extract_citations(file: Path) -> list[tuple[int, str]]:
    """Return [(lineno, citation_text), ...] for every line matching _CITATION_PATTERN
    that is not preceded by the speculative-skip marker."""

def _resolve_distilled_file(citation: Citation, project_root: Path) -> Path | None:
    """Return absolute path if the cited file exists, else None."""

def _resolve_section_anchor(file: Path, anchor: str) -> bool:
    """Slugify each H1/H2/H3 heading in `file`; return True if `anchor` matches."""

def _check_portability(citation: Citation, current_revision: int) -> bool:
    """Thin wrapper over citation.is_portable for symmetry / test seam."""

def validate_complexity_doctrine_links(project_root: Path) -> list[ValidationError]:
    """Main entry. Enumerates artifacts, walks each citation, applies the four
    checks (parse, file, anchor, portability), returns ValidationError list."""
```

Anchor slugification: lower-case heading text, strip leading `#` and surrounding whitespace, replace runs of non-alphanumeric with `-`, strip leading/trailing `-`. Mirrors GitHub-style anchor generation.

Current corpus revision: parse `corpus_revision: <N>` from frontmatter of the most recent `docs/governance/complexity/distilled-characteristics-*.md`. Cache once per call.

Re-export `validate_complexity_doctrine_links` from `src/gzkit/governance/trust_audits/__init__.py` (mirrors `audit_advisory_scorecard` at lines 64, 83).

Run tests; iterate until green.

### Step 3: CLI flag registration

Add to `src/gzkit/cli/parser_maintenance.py` (peer to `--advisory-scorecard` at lines 433-438):

```python
p_validate.add_argument(
    "--complexity-doctrine-links",
    dest="check_complexity_doctrine_links",
    action="store_true",
    help="Audit ADR-0.0.27 complexity-doctrine citations resolve (link integrity)",
)
```

Thread `check_complexity_doctrine_links=a.check_complexity_doctrine_links` into the `validate(...)` call kwargs (around line 568-590).

### Step 4: Validate command dispatch wiring

Edit `src/gzkit/commands/validate_cmd.py`:

- Add parameter `check_complexity_doctrine_links: bool = False` to `validate(...)` (line ~1085) and to `_collect_errors(...)` (line ~337) signatures.
- Add `"complexity_doctrine_links": check_complexity_doctrine_links` to the `checks` dict (line ~411 and line ~1309).
- Add dispatch entry to `_explicit_scope_runners` (line ~480): `"complexity_doctrine_links": lambda: trust_audits.validate_complexity_doctrine_links(project_root),`
- Add `"complexity_doctrine_links"` to `run_all_scopes` list in `_resolve_scopes` (line ~911-947) so `gz validate --all` fires it.

### Step 5: `gz check` aggregate integration

Add to `src/gzkit/quality.py` (peer to `run_advisory_scorecard_audit`):

```python
def run_complexity_doctrine_links_audit(project_root: Path) -> QualityResult:
    """Run the ADR-0.0.27 complexity-doctrine link-integrity audit."""
    errors = trust_audits.validate_complexity_doctrine_links(project_root)
    return _qualityresult_from_errors("Complexity-doctrine links", errors)
```

Add the runner to `src/gzkit/commands/quality.py` `steps` list (between "Instructions files budget" and "Preflight" — lines 312-314):

```python
("Complexity-doctrine links", run_complexity_doctrine_links_audit),
```

Update import at the top of `gz_check_cmd` to include the new runner.

### Step 6: BDD scenarios

Create `features/complexity_doctrine_links.feature` with 4 scenarios:

```gherkin
Feature: Complexity-doctrine link integrity
  As a governance maintainer
  I want gz validate --complexity-doctrine-links to fail-close on broken citations
  So that operators never land on missing artifacts at 2am

  @REQ-0.0.27-07-01
  Scenario: Well-formed citation resolves clean
    Given a cluster ADR with a well-formed citation
    When I run "gz validate --complexity-doctrine-links"
    Then the exit code is 0

  @REQ-0.0.27-07-02
  Scenario: Missing distilled-characteristics file fails closed
    ...

  @REQ-0.0.27-07-03
  Scenario: Unresolved section anchor fails closed
    ...

  @REQ-0.0.27-07-04
  Scenario: Non-portable corpus revision fails closed
    ...
```

Step definitions live in `features/steps/`; reuse existing `gz_command_runs` step where possible.

### Step 7: Documentation updates

**`docs/user/commands/validate.md`** — add a flag section (peer to `--advisory-scorecard`):

```markdown
### `--complexity-doctrine-links`

Audit ADR-0.0.27 complexity-doctrine citations for link integrity. Scans every
citation in cluster ADRs (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) and the rule body,
parses each via the canonical `parse_citation` surface, and fails closed when
the cited file, anchor, or corpus revision does not resolve.

Closes the 2am-Scenario-2 failure mode (operator follows advisor diagnosis to a
missing artifact).

Speculative-citation marker: `<!-- gz-validate-skip: complexity-doctrine-links -->`
on the line preceding a citation skips that citation. Use only for
planned-but-unlanded distillation references.

Example:

    uv run gz validate --complexity-doctrine-links
```

**`docs/user/runbook.md`** — add entry under "Governance doctrine surfaces":

> `uv run gz validate --complexity-doctrine-links` — fail-closed audit of
> ADR-0.0.27 complexity-doctrine citations. Recovery on flag: re-author the
> citation against the current `corpus_revision` and `distilled-characteristics-*.md`
> file, or amend the citing ADR through its own ceremony per
> `ADR-pool.doctrine-amendment-protocol`.

**`docs/governance/advisory-rules-audit.md`** — locate the OBPI-01 entry for
`complexity-doctrine.md`; update its score column from `Promotable` to
`promoted/Mechanical`; add the validator citation `gz validate
--complexity-doctrine-links` (OBPI-0.0.27-07).

### Step 8: Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_complexity_doctrine_links -v
uv run gz validate --complexity-doctrine-links
uv run gz validate --all
uv run gz arb step --name behave -- uv run -m behave features/complexity_doctrine_links.feature
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz check
```

Each command emits an ARB receipt; receipt IDs flow into the Stage 4 evidence table.

## Notes

- **Function-size discipline (REQ-11):** Every helper ≤ 50 lines per `.claude/rules/pythonic.md`. The validator decomposes into 5 helpers + main.
- **Speculative marker convention:** `<!-- gz-validate-skip: complexity-doctrine-links -->`. Convention chosen to mirror existing HTML-comment marker idiom in the doc tree; not lifted from `audit_cli_alignment` (which uses a global `_DOC_PROSE_VERBS` allowlist instead).
- **Operator PII:** Tests, fixtures, manpage, runbook, commit messages MUST NOT include the operator's personal email (REQ-13, AGENTS.md § Local Agent Rules).
- **ADR-0.0.27 Decision text drift (advisory):** Line 95 of the ADR still names `src/gzkit/governance/trust_audits.py` (single file). This is foundation-kind doctrine surface; fixing requires its own ceremony. File a `fix(adr-0.0.27)` follow-up commit per the defect-fix routing thresholds (≤10 lines, single-surface, in-flight trigger). Out of scope for this OBPI.
- **271 sibling-overlap advisories:** Pending sibling ADRs (0.31.0, 0.34.0, 0.39.0, etc.) share forward-looking files. Advisory only; not a blocker since this OBPI lands first.

### Destination-in-mind disclosure (per skill Step 6a)

Before authoring this plan I had already formed the following conclusion:
build the validator as a new submodule under `trust_audits/`, mirroring
`audit_advisory_scorecard`'s scan-and-return-`ValidationError`-list shape,
register the flag through `parser_maintenance.py`, dispatch through
`validate_cmd.py`, and integrate into `gz check` via a `quality.py` runner.

### Rejected alternatives

1. **Single-file validator at the brief's original `trust_audits.py` path.** Rejected because the package was split under GHI #360; honoring the package structure beats reverting it.
2. **Manpage at `docs/user/manpages/gz-validate.md`.** Rejected because peer flags (`--advisory-scorecard`, `--brief-headings`, `--sensitivity`) all document at `docs/user/commands/validate.md`; authoring a new manpage at the brief's original path creates a doc surface no rule names.
3. **Inline citation handling without the speculative marker.** Rejected because REQ-07 explicitly mandates the marker, and the cluster's foundation-amendment forcing function (`ADR-pool.doctrine-amendment-protocol`) needs a way for ADRs to forward-reference unlanded distillations.
4. **Defer `gz check` integration to a follow-up OBPI.** Rejected because REQ-06 binds it to this OBPI; deferring would orphan the runner and miss the 2am-scenario gate.

## Verification (final acceptance gates)

| Gate | Command | Pass condition |
|---|---|---|
| 2 (TDD) | `uv run -m unittest tests.governance.test_complexity_doctrine_links -v` | 8/8 pass; `@covers` decorations satisfy parity |
| Code Quality | `uv run gz lint && uv run gz typecheck` | clean |
| 3 (Docs) | `uv run mkdocs build --strict` | clean |
| 4 (BDD) | `uv run -m behave features/complexity_doctrine_links.feature` | 4/4 scenarios pass with `@REQ-` tags |
| Integration | `uv run gz validate --all` and `uv run gz check` | both fire the new validator |
| 5 (Human) | TTY + `ATTEST` confirmation gate | foundation-kind brief-level Gate 5 attestation |

## Stage 4 evidence outline (for Stage 4 ceremony)

To be populated post-implementation:

- Receipt IDs: `arb-step-unittest-*`, `arb-ruff-*`, `arb-step-typecheck-*`, `arb-step-mkdocs-*`, `arb-step-behave-*`
- Files created: 3 new (validator module, test module, feature file)
- Files modified: 9 (init re-export, parser_maintenance, validate_cmd, quality.py, commands/quality.py, validate.md, runbook.md, advisory-rules-audit.md, brief evidence)
- REQ coverage table: REQ-01..08 mapped to test methods + line numbers; REQ-09 to behave scenarios; REQ-10..13 to mechanical constraints (size limits, TDD discipline, no PII)
