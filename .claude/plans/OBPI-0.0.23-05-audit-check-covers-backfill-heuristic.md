# Plan — OBPI-0.0.23-05 `@covers` backfill heuristic for `gz adr audit-check`

**OBPI:** OBPI-0.0.23-05-audit-check-covers-backfill-heuristic
**Parent ADR:** ADR-0.0.23-agent-failure-mode-taxonomy
**Lane:** Heavy (brief frontmatter `lane: Heavy`; ADR §4 already lifted parent to heavy via OBPI-04)
**Kind:** foundation (parent ADR-0.0.23 is foundation-kind ⇒ brief-level Gate 5 attestation required)
**Sensitivity:** security (third-axis attestation; brief frontmatter `sensitivity: security`)

## Context

GHI #309 surfaced the `Skipped cheap verification` failure shape at the
`gz adr audit-check` validator surface: an agent can silence the audit by
adding a cosmetic `@covers(REQ-X.Y.Z-NN-MM)` decorator to an existing test
in the same commit as the closing receipt for that REQ — the audit accepts
it at face value because it cannot tell a freshly-derived assertion from a
backfilled tag. GHI #272 is the originating anti-pattern; ADR-0.0.23 §5
operationalizes the failure shape into a temporal heuristic.

This OBPI lands the heuristic, the threshold-config file + Pydantic schema,
the new `--strict` flag, the same-commit-fixture pair, the BDD scenario,
the manpage update, and the runbook entry — in one Heavy-lane patch
attested under the (foundation × heavy × security) three-way OR.

### Design decisions (proposed; flagged for operator review at plan-audit)

- **Module placement (REQ-1, REQ-3).** The heuristic logic, the Pydantic
  model, and the loader live in a **new** module
  `src/gzkit/commands/adr_audit_covers_backfill.py` rather than being
  bolted into the already-758-line `adr_audit.py`. This requires
  **widening the brief's Allowed Paths** to cover the new module; the
  alternative (inline in `adr_audit.py`) violates `.claude/rules/pythonic.md`
  § Size Limits (≤600 lines/module). Surface for operator decision in §
  Open questions below.
- **Pydantic model parity with `security_surfaces`.** The threshold model
  follows the ADR-0.0.22 precedent: `src/gzkit/schemas/audit_thresholds.json`
  is the JSON-Schema artifact (consumed by `gz validate` and external
  tooling); a Pydantic `BaseModel` (`frozen=True, extra="forbid"`,
  `TypeAdapter`-loaded) lives alongside the heuristic logic. Same shape as
  `src/gzkit/models/security_surfaces.py`, kept in the new
  `adr_audit_covers_backfill.py` module unless the operator prefers the
  `models/audit_thresholds.py` location (also widens Allowed Paths).
- **Threshold semantics (REQ-2).** "Fire on either condition" is the
  brief's literal text — a decorator whose introducing-commit gap is `≤
  max_covers_backfill_commits` **OR** whose introducing-date gap is `≤
  max_covers_backfill_days` is flagged. Both predicates compute on the
  same decorator; either tripping the smaller threshold flags it.
- **Manpage location (REQ-12).** No current `docs/user/manpages/gz-adr.md`
  exists; existing per-verb manpages (`gz-issue.md`, `gz-justify.md`,
  `arb.md`) suggest the right surface is a new
  `docs/user/manpages/gz-adr-audit-check.md` covering `gz adr audit-check`
  (including `--strict`, the heuristic, threshold file, exit codes,
  examples). The brief's REQ-12 explicitly allows "or sibling manpage."
  Authoring a comprehensive `gz-adr.md` covering all `gz adr` subcommands
  is out of scope.
- **Git history wrapper (REQ-1, REQ-8).** Reuse the existing
  `subprocess.run(["git", "log", ...])` pattern from
  `src/gzkit/commands/patch_release.py` and `src/gzkit/justify/evidence.py`
  rather than introducing a new helper module. The unit-test mock
  boundary is `subprocess.run` (or a thin module-level helper that wraps
  it) — tests never reach the live repo's git history per REQ-9.
- **Closing-receipt resolution.** The brief uses "closing receipt" for the
  REQ; gzkit's ledger surfaces this as the `obpi_completed` /
  `obpi_completion_recorded` event for the parent OBPI of each REQ. Map
  `REQ-0.0.23-05-NN` → parent `OBPI-0.0.23-05` → completion event commit
  via the ledger's existing artifact graph. Fallback (REQ-6): when no
  formal receipt exists yet (open OBPI), compare against the most recent
  commit touching the OBPI's allowed paths.
- **`--json` parity.** Existing `gz adr audit-check` already supports
  `--json`; backfill findings extend the `result` dict with a
  `covers_backfill_findings` key (same shape as `coverage_findings`)
  rather than introducing a new top-level surface. Default human output
  appends a Backfill section under the existing `Advisory` section.

### Out-of-scope notes

- 249 advisory scope-collisions reported by `gz plan audit` (parity with
  OBPI-04's PASS receipt) — none are active locks; this OBPI claims the
  paths first.
- Operator email never enters any default output, diagnostic, manpage
  example, or test fixture (REQ-15 / `AGENTS.md` § Local Agent Rules).
- The `_compute_adr_coverage` engine in `src/gzkit/commands/adr_coverage.py`
  is **read-only** to this OBPI — the heuristic consumes its
  `_collect_covers_annotations` output but does not modify the engine.

## Files

### Created

- `src/gzkit/commands/adr_audit_covers_backfill.py` — module hosting:
  - `AuditThresholds(BaseModel)` — `model_config=ConfigDict(frozen=True,
    extra="forbid")`; fields `max_covers_backfill_commits: int = Field(3,
    ge=0)` and `max_covers_backfill_days: int = Field(7, ge=0)` per REQ-3.
  - `load_audit_thresholds(path: Path) -> AuditThresholds` — reads
    `data/audit_thresholds.json`, validates via Pydantic; on
    `FileNotFoundError`, `json.JSONDecodeError`, or `ValidationError`
    raises `GzCliError` with diagnostic naming the file and the
    validation failure (REQ-3, REQ-5; never silently falls back to
    compiled-in defaults).
  - `find_covers_decorator_introductions(project_root, covers: dict[str,
    list[str]]) -> dict[tuple[str, str, int], CoverIntroduction]` —
    for each `(target, file_path, line_no)` triple, runs
    `git log --diff-filter=A --reverse -L<line>,<line>:<file> --format=%H|%cI`
    (or equivalent) to find the introducing commit/date. Returns frozen
    `CoverIntroduction(commit_sha: str, commit_date: date, file:
    Path, line: int)` per triple. Mock boundary: a module-level
    `_run_git(args, cwd) -> tuple[int, str, str]` wrapper that
    `subprocess.run`s with `encoding="utf-8"`, `text=True`,
    `capture_output=True`. Tests mock `_run_git`.
  - `resolve_req_closing_receipt(ledger, adr_id, obpi_id) ->
    ReqClosingReceipt | None` — looks up the OBPI's
    `obpi_completed`/`obpi_completion_recorded` event, returns
    `ReqClosingReceipt(receipt_id: str, commit_sha: str | None, date:
    date)`. When no formal receipt exists, returns the most-recent
    commit touching the OBPI's allowed paths (REQ-6 fallback).
  - `compute_backfill_findings(introductions, receipts, thresholds) ->
    list[BackfillFinding]` — for each `@covers` introduction, computes
    `gap_commits` (commits between introduction commit and receipt
    commit on the same branch) and `gap_days` (datetime delta). Flags
    when `gap_commits <= thresholds.max_covers_backfill_commits` OR
    `gap_days <= thresholds.max_covers_backfill_days` (REQ-2). REQ-7
    inverse: when both gaps exceed thresholds, the decorator passes.
  - `BackfillFinding(BaseModel)` (`frozen=True, extra="forbid"`) — fields
    `req_id`, `file`, `line`, `introducing_commit_sha`, `closing_receipt_id`,
    `gap_commits`, `gap_days`, `severity` (`warning` | `blocking`).
    `severity` is `blocking` for heavy/foundation/`--strict` per REQ-5.
  - `format_backfill_finding(finding) -> str` — `{file}:{line} REQ {req_id}
    introduced @ {short_sha} ({gap_commits}c / {gap_days}d before
    receipt {receipt_id}); see .claude/rules/tests.md § Invariant 6f for
    remediation` (REQ-5 remediation hint).
  - `evaluate_backfill_for_audit(adr_id, lane, kind, strict, ...) ->
    BackfillResult` — orchestrator: loads thresholds, walks `@covers`,
    resolves receipts, computes findings, classifies severity. Returns
    `BackfillResult(findings, exit_code, unresolvable)` where
    `unresolvable` lists decorators whose git history could not be
    resolved (REQ-8). Module size target ≤500 lines.

- `src/gzkit/schemas/audit_thresholds.json` — JSON Schema (draft 2020-12,
  `$id: gzkit.audit_thresholds.v1`, `additionalProperties: false`,
  `required: [max_covers_backfill_commits, max_covers_backfill_days]`,
  both `integer` `minimum: 0`). Mirrors `security_surfaces.json` shape.

- `data/audit_thresholds.json` — `{"max_covers_backfill_commits": 3,
  "max_covers_backfill_days": 7}` per REQ-3 defaults.

- `tests/governance/test_audit_check_covers_backfill.py` —
  `unittest.TestCase` suites with `@covers("REQ-0.0.23-05-NN")`
  decorators (parity-gate gate per Stage 3 Phase 1b):
  - `TestAuditThresholds` — schema rejects unknown keys
    (`extra="forbid"`); rejects negative ints; loads default file.
  - `TestLoadAuditThresholds` — missing file raises `GzCliError` with
    file name; malformed JSON raises with diagnostic; valid file
    returns frozen instance (REQ-5).
  - `TestFindCoversDecoratorIntroductions` — mocks `_run_git`; validates
    that file:line resolution maps to the right commit SHA / date.
  - `TestComputeBackfillFindings` — fires when gap_commits ≤ 3; fires
    when gap_days ≤ 7; passes when BOTH gaps exceed thresholds (REQ-7);
    fires when EITHER trips (REQ-2 "fire on either").
  - `TestSeverityClassification` — `warning` on lite-without-strict;
    `blocking` on heavy / foundation / `--strict` (REQ-4, REQ-5).
  - `TestFormatBackfillFinding` — output contains file:line, REQ id,
    short SHA, gap shape `Nc / Dd`, receipt id, remediation hint
    (REQ-6).
  - `TestUnresolvableGitHistory` — mocked shallow-clone error continues
    in default mode (skipping decorator), exits 2 under `--strict`
    (REQ-8).
  - All tests mock `_run_git` at the module boundary; never reach the
    live repo's git history (REQ-9).

- `tests/fixtures/adr_audit_covers_backfill/` — fixture pair (REQ-10):
  - `legitimate_evolution/` — fixture ADR + OBPI brief + test file
    where the `@covers` decorator was introduced 30 commits before the
    closing receipt (test mocks `_run_git` to return that history).
  - `same_commit_backfill/` — fixture ADR + OBPI brief + test file where
    the `@covers` decorator and the closing receipt land in the same
    commit (test mocks `_run_git` to return identical SHAs).

- `features/adr_audit_covers_backfill.feature` — BDD scenario with
  `@REQ-0.0.23-05-03` tag (heavy-lane fail-closed end-to-end per REQ-11).
  Scenario: `gz adr audit-check ADR-<heavy-fixture>` against the
  same-commit-backfill fixture exits 3 with the expected diagnostic.

- `features/steps/adr_audit_covers_backfill_steps.py` — step definitions
  consuming the fixtures and the mocked `_run_git`.

- `docs/user/manpages/gz-adr-audit-check.md` — verb-specific manpage
  (mirrors `gz-issue.md` shape):
  - DESCRIPTION, USAGE, OPTIONS (`adr` positional, `--json`, `--strict`),
    EXIT CODES (0/1/2/3 per `.claude/rules/cli.md`), THRESHOLDS section
    documenting `data/audit_thresholds.json` + key semantics, EXAMPLES
    showing default-mode warning output and `--strict` exit-3 output.
  - REQ-12 satisfied. `gz cli audit` parity verified post-author.

- `docs/user/commands/adr-audit-check.md` already exists — modify
  (see § Modified) to add `--strict` documentation rather than
  authoring fresh.

### Modified

- `src/gzkit/commands/adr_audit.py` — extend `adr_audit_check()` to call
  `evaluate_backfill_for_audit(adr_id, lane, kind, strict, ...)` after
  the existing `_partition_coverage_findings` step. Append findings to
  the result dict; merge `unresolvable` into the rendered output;
  thread `strict` and `lane`/`kind` through from the parser. Plumb
  `passed = passed and not blocking_backfill_findings`. Existing
  `--json` shape gains `covers_backfill_findings` and
  `covers_backfill_unresolvable` keys.

- `src/gzkit/cli/parser_artifacts.py` — extend `p_adr_audit_check`
  registration (~line 385):
  - `p_adr_audit_check.add_argument("--strict", action="store_true",
    help="Fail-close on any covers-backfill finding (lite ADRs);
    no-op on heavy/foundation ADRs which already fail-close.")`
  - `p_adr_audit_check.set_defaults` lambda updates to pass
    `strict=a.strict`.

- `docs/user/commands/adr-audit-check.md` — add `--strict` flag entry
  (per `.claude/rules/cli.md` § Consistency); add example showing the
  heuristic output; mention `data/audit_thresholds.json`.

- `docs/user/manpages/index.md` (or canonical manpage index file —
  `gz cli audit` will name the right path) — add
  `gz-adr-audit-check.md` entry per `.claude/rules/cli.md` § Consistency.

- `docs/user/runbook.md` — add runbook entry: when audit-check fails
  on backfill, route operator to `.claude/rules/tests.md` § Invariant
  6f for assertion re-derivation; reference `--strict` for explicit
  fail-close; reference `data/audit_thresholds.json` for tuning.

- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
  — Evidence section: tick the `Validator scope` and `Thresholds`
  bullets; Checklist: tick item 5; Attestation Block: 0.0.23 row
  populated post-attestation.

- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/obpis/OBPI-0.0.23-05-audit-check-covers-backfill-heuristic.md`
  — populate `### Implementation Summary`, `### Key Proof`, evidence
  sections, frontmatter `status: Completed` post-Stage-5.

### Generated mirrors (touched only by `gz agent sync control-surfaces`)

- None — this OBPI does not edit `.gzkit/rules/**` or
  `.gzkit/skills/**`, so no rule/skill mirror sync is required.

## Steps

1. **Brief widening (operator decision).** Surface the proposed
   widening of Allowed Paths to include
   `src/gzkit/commands/adr_audit_covers_backfill.py`. If accepted,
   append to brief's `## Allowed Paths`. If rejected, refactor plan
   to inline the heuristic in `adr_audit.py` (raises pythonic-rule
   defect; flag for follow-up GHI).

2. **TDD red.** Author
   `tests/governance/test_audit_check_covers_backfill.py` covering
   REQs 01–09. Run `uv run -m unittest tests.governance.test_audit_check_covers_backfill -v`
   — confirm tests fail with "module not found" (red).

3. **Author schema + data.** Write
   `src/gzkit/schemas/audit_thresholds.json` (JSON Schema mirror of
   `security_surfaces.json`). Write `data/audit_thresholds.json` with
   defaults per REQ-3. Run `uv run gz validate --documents` — confirm
   schema is registered.

4. **Implement heuristic module.** Author
   `src/gzkit/commands/adr_audit_covers_backfill.py`:
   `AuditThresholds`, `load_audit_thresholds`, `_run_git`,
   `find_covers_decorator_introductions`, `resolve_req_closing_receipt`,
   `compute_backfill_findings`, `BackfillFinding`,
   `format_backfill_finding`, `evaluate_backfill_for_audit`. Keep
   module ≤500 lines, function size ≤50 lines per
   `.claude/rules/pythonic.md`.

5. **Wire into `adr_audit_check`.** Edit `src/gzkit/commands/adr_audit.py`
   to call `evaluate_backfill_for_audit` after coverage partitioning;
   thread `strict`, `lane`, `kind` through from parser; merge findings
   into result dict; update human-output renderer.

6. **Register `--strict` flag.** Edit `src/gzkit/cli/parser_artifacts.py`
   to add `--strict` to `p_adr_audit_check`; update `set_defaults` to
   thread the new arg into `adr_audit_check(adr=..., as_json=...,
   strict=...)`. Run `uv run gz adr audit-check --help` — confirm
   `--strict` is listed.

7. **Author fixtures.** Build
   `tests/fixtures/adr_audit_covers_backfill/legitimate_evolution/`
   and `tests/fixtures/adr_audit_covers_backfill/same_commit_backfill/`
   — minimal ADR/OBPI/test triples per REQ-10.

8. **TDD green.** Re-run unit tests; confirm all REQs pass.
   Run `uv run gz arb step --name unittest -- uv run -m unittest
   tests.governance.test_audit_check_covers_backfill -v` to mint
   receipts.

9. **Author manpage and command-doc updates.** Write
   `docs/user/manpages/gz-adr-audit-check.md`. Update
   `docs/user/commands/adr-audit-check.md` with `--strict` and
   threshold semantics. Add manpage-index entry. Run
   `uv run gz cli audit` — confirm exit 0 with `--strict` covered
   (REQ-13).

10. **Author BDD feature + steps.** Write
    `features/adr_audit_covers_backfill.feature` (`@REQ-0.0.23-05-03`)
    and `features/steps/adr_audit_covers_backfill_steps.py`. Run
    `uv run -m behave features/adr_audit_covers_backfill.feature` —
    green. Run `uv run gz validate --behave-req-tags` — exit 0
    (REQ-11).

11. **Update runbook.** Add cross-reference flow entry to
    `docs/user/runbook.md` per REQ-12 / Gate 5 runbook covenant.

12. **Verify all gates.** Run baseline ARB-wrapped sweep (lint,
    typecheck, unittest, mkdocs, behave, security-scan if available
    per `security-sensitivity.md`). Run
    `uv run gz validate --documents --surfaces --brief-headings
    --behave-req-tags --sensitivity`. Run
    `uv run gz covers OBPI-0.0.23-05-audit-check-covers-backfill-heuristic
    --json` and confirm `uncovered_reqs == 0`.

## Verification

Per the brief's Verification section:

```bash
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz validate --brief-headings
uv run gz validate --behave-req-tags
uv run gz validate --sensitivity
uv run gz cli audit
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
test -f data/audit_thresholds.json
test -f src/gzkit/schemas/audit_thresholds.json
test -d tests/fixtures/adr_audit_covers_backfill
test -f features/adr_audit_covers_backfill.feature
```

Heuristic-specific smoke checks (post-implementation):

```bash
uv run gz adr audit-check --help                      # --strict listed
uv run gz adr audit-check ADR-<lite-fixture>          # exit 0 (warning)
uv run gz adr audit-check ADR-<lite-fixture> --strict # exit 3
uv run gz adr audit-check ADR-<heavy-fixture>         # exit 3 (inheritance)
uv run -m behave features/adr_audit_covers_backfill.feature
```

REQ-level dispatch (Stage 3 Phase 2): each REQ maps to one or more tests
in `tests/governance/test_audit_check_covers_backfill.py` and the BDD
scenario; test paths are non-overlapping → parallel verification subagent
dispatch is safe per OBPI-pipeline Phase 2 rules.

## Open questions for operator review

1. **Allowed-Paths widening (REQ-1, blocker).** The brief lists
   `src/gzkit/commands/adr_audit.py` as the in-scope module, but the
   pythonic-rule size cap (`≤600 lines/module`) is already breached at
   758 lines. Two options:
   - **(A) Widen** Allowed Paths to add
     `src/gzkit/commands/adr_audit_covers_backfill.py`. Keeps the
     existing module from growing further; aligns with the
     `security_surfaces.py` precedent (a separate module per
     concern). **Recommended.**
   - **(B) Inline** in `adr_audit.py` — keeps Allowed Paths as
     authored, but pushes the file deeper into pythonic-rule
     violation. Triggers a follow-up GHI for size-cap remediation.

2. **Pydantic model location.** Inline in
   `adr_audit_covers_backfill.py` (recommended, scoped to the heuristic)
   vs. break out to `src/gzkit/models/audit_thresholds.py`
   (matches `security_surfaces.py` precedent — a separate `models/`
   module). Operator preference; either way the brief's Allowed Paths
   need widening.

3. **Manpage location (REQ-12).** New
   `docs/user/manpages/gz-adr-audit-check.md` (recommended; verb-
   specific; matches `gz-issue.md` shape) vs. comprehensive new
   `docs/user/manpages/gz-adr.md` (covers all `gz adr <verb>`; large
   scope expansion; arguably out of scope for this OBPI). REQ-12
   permits "or sibling manpage."

4. **Closing-receipt fallback when REQ has no formal receipt yet
   (REQ-6).** Plan resolves to "most-recent commit touching OBPI's
   allowed paths." Alternative: skip such REQs entirely (no flag
   possible) and emit an advisory line. **Recommended option:**
   fallback path as written; advisory for unresolvable REQs
   per REQ-8.

## Notes

### Destination-in-mind (Step 6a disclosure)

I had a clear approach before authoring this plan: (1) heuristic in a
new sibling module to respect the size cap, (2) Pydantic schema parity
with `security_surfaces`, (3) `--strict` as a heavy-lane-additive flag
threaded through the parser, (4) git-history wrapper as a single
mockable function, (5) verb-specific manpage at `gz-adr-audit-check.md`
to satisfy REQ-12 without authoring a comprehensive `gz-adr.md`.
Op-questions §1 and §3 surface the two ambiguities the brief leaves
genuinely open; the rest is direct mechanical instantiation of the
brief's REQs against the security-sensitivity / models / cli rules.

### Rejected alternatives considered during exploration

- **Compiled-in defaults with override.** Rejected by REQ-3 — the
  threshold file MUST exist; missing or malformed exits 1.
- **Hash-comparison instead of git-history scan.** Rejected — the brief
  prescribes commit-window and date-window, both of which require
  git-history not file-content comparison.
- **Reuse `_compute_adr_coverage` as a backfill engine.** Rejected — that
  engine answers "is this REQ covered at all?" not "when was the
  decorator added relative to the receipt?" The two are
  orthogonal scopes.
- **Promote findings into ADR-level closeout blockers regardless of
  lane.** Rejected — REQ-4 explicitly carves lite-without-strict as
  warning-level; respecting the carve-out matches the brief.
- **Skip the BDD scenario; rely on unit + smoke tests.** Rejected —
  REQ-11 is explicit; `gz validate --behave-req-tags` enforces the
  scenario tag.

### Files outside the brief allowlist

- `src/gzkit/commands/adr_audit_covers_backfill.py` — proposed widening
  per Open Question §1.
- `docs/user/manpages/gz-adr-audit-check.md` — proposed widening per
  Open Question §3 (the brief allows this via "or sibling manpage").

Both are flagged for operator decision before implementation.
