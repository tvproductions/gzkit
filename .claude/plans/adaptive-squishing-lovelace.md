# OBPI-0.0.20-01-validator-and-allowlist — Validator and Allow-list Foundation

**OBPI slug:** `OBPI-0.0.20-01-validator-and-allowlist`
**Parent ADR:** `ADR-0.0.20-agent-rule-placement-invariant`
**Brief:** `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/obpis/OBPI-0.0.20-01-validator-and-allowlist.md`

## Context

ADR-0.0.20 codifies an **Agent Rule Placement Invariant**: `.gzkit/rules/*.md`
files with `paths: "**"` (or missing `paths:`) may not live under any vendor
rule directory; non-path-scoped agent rules belong in `AGENTS.md` or the
per-directory hierarchical equivalent, with allow-list exceptions recorded
in `.gzkit/manifest.json` under `rules.unscoped_allowlist`.

OBPI-0.0.20-01 delivers the **mechanical substrate** that makes the
invariant enforceable. It does NOT migrate any rule content — that is
OBPI-02/03/04. After this brief lands:

- `uv run gz validate --unscoped-rules` exits 0 against today's repo (the
  three doomed files — `agent-contract.md`, `attestation-enrichment.md`,
  `defect-fix-routing.md` — are ALLOWLISTED pending consolidation)
- Any future author adding `paths: "**"` to a rule without an allow-list
  entry fails `gz check` at Gate 2
- `gz validate --audits` picks up the new scope; bare `gz validate` runs
  it as part of the default-scope pass

## Brief drift to flag (scope expansion)

Two Allowed-Paths drafting defects in the brief must be corrected for
REQ-3 and REQ-19 to be satisfiable. Flagging as scope expansion tied to
existing REQs (per Prime Directive #5 — flag defects, never excuse them):

| Brief says | Reality | REQ anchor |
|---|---|---|
| `src/gzkit/cli/parser_validate.py` | `src/gzkit/cli/parser_maintenance.py` (file rename pre-dates the brief) | REQ-3 (flag registration) |
| *(missing)* | `src/gzkit/commands/validate_cmd.py` (must register runner in `_explicit_scope_runners`) | REQ-7 / REQ-19 (dispatch) |
| *(missing)* | `src/gzkit/commands/quality.py` (REQ-19 requires `gz check` to invoke) | REQ-19 explicitly |

The corrected effective Allowed Paths are listed under "Files to modify"
below. The brief body itself will be left alone (denied by its own
Allowed Paths) — OBPI-05's closeout sweep can refresh the brief.

## Architecture

### Module placement

- **`src/gzkit/validators/unscoped_rules.py`** (new package, new module):
  Pydantic models + classification logic + orchestration. The brief
  explicitly prescribes a fresh `validators/` package rather than
  absorbing into `governance/trust_audits.py` (which is already 1,520
  lines, past the 600-line ceiling — fixing that is a separate concern).
- **`src/gzkit/validators/__init__.py`** (new, empty package init).
- **`tests/validators/__init__.py`** + **`tests/validators/test_unscoped_rules.py`** (new).

### Reused existing seams (no new deps)

- `ValidationError` Pydantic model — `src/gzkit/core/validation_rules.py:13-24`
  (fields: `type`, `artifact`, `message`, `field`, `ledger_value`,
  `frontmatter_value`; frozen; `extra="forbid"`). Runner returns
  `list[ValidationError]` for `validate_cmd.py` consumption.
- Frontmatter parsing pattern — mirror the stdlib-only approach of
  `_parse_adr_frontmatter()` at `src/gzkit/governance/trust_audits.py:1414-1444`
  (manual `---` delimiter scan + line-by-line `key: value` parse). Our
  parser is `_parse_paths_field()` — a focused helper that distinguishes
  `paths` absent / null / `"**"` string / `["**"]` single-item list /
  concrete glob. No new `yaml` library import.
- Runner dispatch — mirrors `_taxonomy_runner` at
  `src/gzkit/commands/validate_cmd.py:362-366` (lazy import, returns
  `list[ValidationError]`).

### Classification contract (REQ-6)

| `paths:` value | Result | `Violation.reason` |
|---|---|---|
| Key absent | VIOLATION | `missing-paths` |
| `paths:` (null / empty) | VIOLATION | `missing-paths` |
| `paths: "**"` (string) | VIOLATION | `universal-glob` |
| `paths: ["**"]` (single list) | VIOLATION | `universal-glob` |
| `paths: "src/**"` or similar concrete | PASS | — |
| `paths: ["tests/**"]` concrete list | PASS | — |
| In `rules.unscoped_allowlist` | `allowlisted=True` (does not gate-fail) | (carried unchanged) |

### Exit codes (REQ-7)

- 0 — all PASS or ALLOWLISTED
- 2 — I/O error (missing manifest, malformed YAML, unreadable file)
- 3 — one or more non-allowlisted VIOLATIONs

### CLI wiring

1. **Flag registration** — `src/gzkit/cli/parser_maintenance.py` adds
   `--unscoped-rules` (dest `check_unscoped_rules`), immediately after
   `--taxonomy` (line 443-448) to keep the block alphabetic/adjacent.
   Also adds OR-composition into the `--audits` aggregate and threads
   through `set_defaults` lambda.
2. **Flag plumbing** — `src/gzkit/commands/validate_cmd.py`:
   - Add `check_unscoped_rules: bool = False` to `validate()` and
     `_collect_validation_errors()`.
   - Register in `explicit_scopes` dict (the `--audits` OR-pattern
     composes via `check_unscoped_rules=a.check_unscoped_rules or a.check_audits`
     at the parser layer — keeping it explicit-only matches the other
     audit scopes).
   - Add runner to `_explicit_scope_runners()`: `"unscoped_rules":
     lambda: _unscoped_rules_runner(project_root)`. The runner imports
     `gzkit.validators.unscoped_rules` lazily.
3. **`gz check` inclusion (REQ-19)** — `src/gzkit/commands/quality.py`
   adds a step invoking the validator (similar to the existing advisory
   drift check; non-blocking on ALLOWLISTED, fail-closed on true
   VIOLATIONs).
4. **`--json` / `--allowlist-only`** — both are scope-local sub-flags.
   `--json` piggybacks on the existing `add_json_flag(p_validate)`
   (line 455); `--allowlist-only` is a new flag added alongside
   `--unscoped-rules` and honored inside the runner.

### Pydantic models (REQ-1, REQ-2)

```python
class UnscopedAllowlistEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file: str
    rationale: str = Field(..., min_length=20)
    tracking_ref: str = Field(..., pattern=r"^(GHI-\d+|ADR-[\d.]+[-\w]*)$")
    added_date: date

class Violation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file: str
    reason: Literal["missing-paths", "universal-glob"]
    allowlisted: bool
    detected_value: str | None = None

class UnscopedRulesResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    scope: str = "unscoped-rules"
    result: Literal["pass", "fail"]
    violations: list[Violation]
    allowlist_entries: list[UnscopedAllowlistEntry]
    canonical_root: str
    files_checked: int
    exit_code: int
```

### Manifest schema fragment (REQ-11)

Extend `src/gzkit/schemas/manifest.schema.json` under
`properties.rules.properties.unscoped_allowlist` as a typed array
mirroring the Pydantic contract (required: file / rationale /
tracking_ref / added_date; additionalProperties: false; rationale
minLength 20; tracking_ref regex pattern).

### Initial allow-list entries (REQ-12)

Three entries added to `.gzkit/manifest.json` under
`rules.unscoped_allowlist`:

```json
{"file": ".gzkit/rules/agent-contract.md",
 "rationale": "Pending consolidation per OBPI-02",
 "tracking_ref": "ADR-0.0.20",
 "added_date": "2026-04-21"}
{"file": ".gzkit/rules/attestation-enrichment.md",
 "rationale": "Pending consolidation per OBPI-03",
 "tracking_ref": "ADR-0.0.20",
 "added_date": "2026-04-21"}
{"file": ".gzkit/rules/defect-fix-routing.md",
 "rationale": "Pending consolidation per OBPI-04",
 "tracking_ref": "ADR-0.0.20",
 "added_date": "2026-04-21"}
```

## TDD order (Red-Green-Refactor per REQ; per-increment rhythm)

Each REQ gets its own Red → Green cycle with `@covers(REQ-...)`
decoration. No batch-then-run. Increments flow without per-step
approval pauses per `.claude/rules/tests.md` § Per-increment rhythm.

1. **T1 — Pydantic models (REQ-1, REQ-2).** Tests: model construction
   with valid + invalid fields (rationale too short, tracking_ref bad
   regex, extra field rejection). RED → GREEN → next.
2. **T2 — `_parse_paths_field()` classification (REQ-6).** Table-driven
   test with 6 scalar cases (absent, null, `"**"`, `["**"]`,
   `"src/**"`, `["tests/**"]`). RED → GREEN.
3. **T3 — Allowlist resolution (REQ-6).** Test that a file in
   `rules.unscoped_allowlist` is marked `allowlisted=True` and does not
   flip `result` to `"fail"`. RED → GREEN.
4. **T4 — Exit codes (REQ-7).** Three fixture cases: all PASS → 0;
   malformed YAML → 2; non-allowlisted VIOLATION → 3. RED → GREEN.
5. **T5 — `--json` roundtrip (REQ-8).** Assert JSON output parses via
   `json.loads` and rehydrates through `UnscopedRulesResult.model_validate`.
   RED → GREEN.
6. **T6 — `--allowlist-only` (REQ-9).** Assert human-readable listing
   prints entries with rationale + tracking_ref and exits 0. RED → GREEN.
7. **T7 — Mirror-not-enumerated (REQ-4).** Fixture has a violating
   mirror under `.claude/rules/`; assert the validator does NOT flag it
   (only canonical is enumerated). RED → GREEN.
8. **T8 — Missing manifest (REQ-7, exit 2).** Fixture has no manifest
   file; assert exit code 2 and a specific error message.
9. **T9 — Read-only enforcement (REQ-20).** Static check via `inspect`
   or `grep`-equivalent assertion that the module contains no `write_*`,
   `shell=True`, LLM call, or file write. Also verify no files in the
   fixture directory are mutated across a run.

All tests use `tempfile.TemporaryDirectory` fixture dirs — never the
live repo or live manifest (REQ-14). `@covers(REQ-0.0.20-01-NN)` on
each test per GHI #160 Phase 6.

## Files to modify (corrected effective Allowed Paths)

| Path | Action | REQ |
|---|---|---|
| `src/gzkit/validators/__init__.py` | NEW (empty) | REQ-1 |
| `src/gzkit/validators/unscoped_rules.py` | NEW — models + runner | REQ-1/2/4/5/6/7/8/9/20 |
| `src/gzkit/cli/parser_maintenance.py` | ADD flag block | REQ-3, REQ-19 |
| `src/gzkit/commands/validate_cmd.py` | ADD runner dispatch | REQ-7, REQ-8, REQ-19 |
| `src/gzkit/commands/quality.py` | ADD `gz check` step | REQ-19 |
| `src/gzkit/schemas/manifest.schema.json` | EXTEND with fragment | REQ-11 |
| `.gzkit/manifest.json` | ADD 3 allowlist entries | REQ-12 |
| `tests/validators/__init__.py` | NEW (empty) | REQ-13 |
| `tests/validators/test_unscoped_rules.py` | NEW — table-driven | REQ-13/14/15 |
| `docs/governance/advisory-rules-audit.md` | ADD scorecard row | REQ-16 |
| `docs/user/commands/validate.md` | ADD `--unscoped-rules` section | REQ-17 |

`.gzkit/rules/agent-contract.md`, `attestation-enrichment.md`,
`defect-fix-routing.md` — NOT touched (denied; deletion is OBPI-02/03/04).
Mirror files under `.claude/rules/` etc. — NOT hand-edited (auto-regenerated
by `gz agent sync control-surfaces` if needed; no sync run expected since
we don't touch canonical rule content here).

## Verification

```bash
# TDD per increment (running test after each Red→Green step)
uv run -m unittest tests.validators.test_unscoped_rules -v

# Scope-level verification (REQ-18: exits 0 with 3 allowlisted)
uv run gz validate --unscoped-rules
uv run gz validate --unscoped-rules --json
uv run gz validate --unscoped-rules --allowlist-only

# Aggregate integration (REQ-19)
uv run gz validate --audits
uv run gz check

# Code quality
uv run gz lint
uv run gz typecheck
uv run gz arb coverage run -m unittest discover -s tests/validators -t .

# ARB receipts for attestation (canonical invocations per attestation-enrichment.md)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Not in scope (denied / deferred)

- Rule-content migration (OBPI-02/03/04)
- Allow-list expiry enforcement (deferred to follow-up GHI per ADR § Negative #5)
- `--fix` autofix (deliberately excluded per REQ-10 — judgment call)
- Mirror-file direct checks (sync contract handles per REQ-4)
- Refactoring `governance/trust_audits.py` size ceiling overrun (pre-existing,
  out of scope — would be flagged as a separate GHI if needed)

## Acceptance

All 20 REQs in the brief's Acceptance Criteria are satisfied. `gz validate
--unscoped-rules` exits 0 against the final repo state (3 allowlisted, 0
violations). `gz validate --audits` and `gz check` both invoke the new
scope. Coverage for `src/gzkit/validators/unscoped_rules.py` ≥ 40%.
