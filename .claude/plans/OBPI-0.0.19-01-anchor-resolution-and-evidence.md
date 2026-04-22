# Plan — OBPI-0.0.19-01-anchor-resolution-and-evidence: Anchor Resolution and Evidence Gathering

**OBPI:** `OBPI-0.0.19-01-anchor-resolution-and-evidence`
**Parent ADR:** `ADR-0.0.19-pre-execution-reasoning-walkthrough`

## Context

`gzkit justify` (ADR-0.0.19) is a pre-execution reasoning walkthrough CLI that turns a raw anchor (GHI, OBPI, or draft text) into a grounded Markdown walkthrough. The CLI, template, and rendering live in downstream OBPIs (02–05); this OBPI (01) delivers the pure library substrate that OBPI-02 consumes: Pydantic data models, anchor resolvers, and a concurrent five-source evidence gatherer — all side-effect-free, no stdout/stderr, no LLM calls, no filesystem mutation.

This is Heavy-lane because `src/gzkit/justify/__init__.py` exposes a new public API (`resolve_anchor`, `gather_evidence`, `AnchorRef`, `EvidenceBundle`, `AnchorKind`, `AnchorResolutionError`) that downstream OBPIs import. Attestation is deferred to ADR-level closeout per lane-inheritance protocol.

## Approach Summary

1. Models module defines 5 frozen Pydantic models + `AnchorKind` literal + `AnchorResolutionError`.
2. Anchors module provides `resolve_anchor(raw, *, draft_text, draft_slug)` dispatching on input shape to three private resolvers (GHI via `run_exec(["gh", ...])`, OBPI via `Path.glob`, draft via literal pass-through).
3. Evidence module provides `gather_evidence(anchor, *, related)` using `concurrent.futures.ThreadPoolExecutor` to run five independent source-fetches in parallel, each wrapped in try/except → append to `warnings` on failure.
4. Package `__init__.py` re-exports only the six public names via explicit `__all__`.
5. Tests: one module per source file, REQ-pinned via `@covers("REQ-0.0.19-01-NN")` decorators, `tempfile.TemporaryDirectory` for filesystem isolation, `@patch("gzkit.justify.anchors.run_exec")` / `@patch("gzkit.justify.evidence.run_exec")` for subprocess mocks, one timing test asserts <3.0s on realistic fixture.

## Files to Create

### Source files (`src/gzkit/justify/`)

**`src/gzkit/justify/__init__.py`** — Public API re-exports with explicit `__all__ = ["AnchorRef", "EvidenceBundle", "AnchorKind", "resolve_anchor", "gather_evidence", "AnchorResolutionError"]`. Internal models (`RuleCitation`, `CommitRef`, `LedgerEvent`) are importable via `from gzkit.justify.models import ...` but excluded from `__all__` so `from gzkit.justify import *` exposes only the six public names (REQ-11).

**`src/gzkit/justify/models.py`** — Five frozen Pydantic models and supporting types.

- `AnchorKind = Literal["ghi", "obpi", "draft"]` — type alias (REQ-02).
- `AnchorResolutionError(Exception)` — raised when anchor cannot be resolved.
- `AnchorRef(BaseModel)` — `kind: AnchorKind`, `identifier: str | None`, `title: str | None`, `body: str | None`, `labels: list[str]`, `author: str | None`, `draft_text: str | None`, `draft_slug: str | None`, `source_path: str | None`. `model_config = ConfigDict(frozen=True, extra="forbid")`. A `@field_validator("kind")` enforces only `"ghi"/"obpi"/"draft"` (ValidationError on `"adr"` — REQ-02 — this is redundant with `Literal` but belt-and-braces with a clearer error message naming `"adr"`).
- `RuleCitation(BaseModel)` — `rule_id: str`, `path: str`, `description: str | None`, `paths_globs: tuple[str, ...]`. Frozen.
- `CommitRef(BaseModel)` — `sha: str`, `subject: str`. Frozen.
- `LedgerEvent(BaseModel)` — `event: str`, `id: str`, `ts: str`, `parent: str | None`, `extra: dict[str, Any]`. Frozen. **Note**: this is a local re-declaration for the justify library's consumption shape; the main `src/gzkit/ledger.py` `LedgerEvent` is the authoritative model. Local model keeps the justify library decoupled from ledger internals and matches only the fields justify consumes.
- `EvidenceBundle(BaseModel)` — `anchor: AnchorRef`, `matching_rules: tuple[RuleCitation, ...]`, `ledger_events: tuple[LedgerEvent, ...]`, `recent_commits: tuple[CommitRef, ...]`, `related_anchors: tuple[AnchorRef, ...]`, `taxonomy_reference: str` (literal path), `warnings: tuple[str, ...]`. Frozen. Uses tuples (not lists) for immutability under `frozen=True`.

Import style: `from pydantic import BaseModel, ConfigDict, Field, field_validator` (matches `src/gzkit/lock_manager.py:18-44` and `src/gzkit/tasks.py:26-55` exemplars).

**`src/gzkit/justify/anchors.py`** — Anchor resolvers.

- Public `resolve_anchor(raw: str | None, *, draft_text: str | None = None, draft_slug: str | None = None, project_root: Path | None = None) -> AnchorRef`.
  - Dispatches on shape: regex `^GHI-\d+$` or `^#\d+$` → `_resolve_ghi`; regex `^OBPI-\d+\.\d+\.\d+-\d+$` → `_resolve_obpi`; `raw is None` and `draft_text` populated → `_resolve_draft`.
  - Malformed input raises `ValueError` with the three accepted shapes listed in the message (REQ-03, REQ-06).
  - `project_root` defaults to `Path.cwd()` but is parameterizable for test isolation (never touches live project root in tests).
- Private `_resolve_ghi(raw: str, project_root: Path) -> AnchorRef` — calls `run_exec(["gh", "issue", "view", num, "--json", "number,title,body,labels,author"], cwd=project_root)` (reuses canonical `run_exec` from `src/gzkit/utils.py:15-31`). Non-zero rc or empty stdout → raise `AnchorResolutionError` with quoted stderr (REQ-04). Parses JSON, populates `AnchorRef(kind="ghi", identifier="GHI-<N>", title, body, labels, author)`.
- Private `_resolve_obpi(raw: str, project_root: Path) -> AnchorRef` — uses `pathlib.Path(project_root).glob(f"docs/design/adr/**/obpis/{raw}-*.md")`. Zero matches → `AnchorResolutionError`. Multiple → `AnchorResolutionError` naming all candidate paths. Single → reads file, returns `AnchorRef(kind="obpi", identifier=raw, source_path=str(path))`. Filename-keyed, not frontmatter-keyed (REQ-05).
- Private `_resolve_draft(draft_text: str, draft_slug: str) -> AnchorRef` — validates `draft_slug` matches `^[a-z][a-z0-9-]*$`, `draft_text` non-empty (`ValueError` if either fails — REQ-06). Returns `AnchorRef(kind="draft", draft_text, draft_slug)`.

**`src/gzkit/justify/evidence.py`** — Concurrent five-source grounding gather.

- Public `gather_evidence(anchor: AnchorRef, *, related: list[str] | None = None, project_root: Path | None = None, timeout: float = 3.0) -> EvidenceBundle`.
- Uses `concurrent.futures.ThreadPoolExecutor(max_workers=5)`. Five tasks submitted:
  1. `_gather_matching_rules(anchor, project_root)` — reads `.gzkit/rules/*.md`, parses `paths:` frontmatter (YAML list). For `kind="obpi"`: reads parent ADR (inferred from filename pattern `docs/design/adr/**/ADR-{X.Y.Z}-*.md` where `X.Y.Z` is extracted from OBPI identifier) to derive anchor surface paths, matches each rule's globs against those paths via `fnmatch`. For `kind="ghi"`: heuristic substring match against the GHI body. For `kind="draft"`: returns rules whose `paths:` includes always-matching globs like `"**"` or `"**/*.py"` (the draft has no surface yet). Graceful degradation: `OSError` / parse failure → empty tuple + warning.
  2. `_gather_ledger_events(anchor, project_root)` — only populated when `anchor.kind == "obpi"`. Calls `run_exec(["uv", "run", "gz", "state", "--json"], cwd=project_root)`, filters to events whose `id == anchor.identifier`. For `kind in {"ghi", "draft"}`: returns empty tuple. Non-zero rc → empty tuple + warning "ledger source unavailable" (REQ-08 for draft says "warning note explaining absence" — we emit an explanatory note in both graceful-degradation and draft/ghi cases).
  3. `_gather_recent_commits(anchor, project_root)` — runs `run_exec(["git", "log", "--since=60.days.ago", "--oneline", f"--grep={grep_pattern}"], cwd=project_root, timeout=10)`. `grep_pattern` is anchor identifier (`GHI-<N>`, `OBPI-X.Y.Z-NN`) or the `draft_slug`. Pattern matches `src/gzkit/commands/obpi_audit_cmd.py:373-380`. Non-zero rc → empty + warning.
  4. `_gather_related_anchors(related, project_root)` — for each ID in `related`, calls `resolve_anchor(rid, project_root=project_root)`. If a single resolution fails, the failed ID goes into `warnings` and the others proceed. (REQ-07d says "stored as AnchorRef entries" — we skip failed ones rather than raising.)
  5. `_gather_taxonomy_reference()` — pure literal: returns `"docs/governance/model-regression-taxonomy.md"`. Always available. This source is a path string, not file contents (REQ-07e).
- Each future wrapped via `concurrent.futures.as_completed` with per-future exception capture; all futures join before `executor.__exit__`.
- All warnings aggregated into `EvidenceBundle.warnings` (tuple for immutability).
- Library never emits to stdout/stderr — caller owns I/O (REQ-10).

### Test files (`tests/justify/`)

**`tests/justify/__init__.py`** — Docstring only: `"""Tests for gzkit.justify — models, anchor resolvers, and evidence gathering."""` (matches `tests/arb/__init__.py` pattern).

**`tests/justify/test_models.py`** — Pydantic model unit tests.

- `test_anchor_ref_is_frozen` — `@covers("REQ-0.0.19-01-01")`. Construct `AnchorRef(kind="ghi", ...)`, assert `ValidationError` on `anchor.kind = "obpi"` (frozen mutation). Pattern from `tests/test_registry.py:33-34`.
- `test_anchor_rejects_adr_kind` — `@covers("REQ-0.0.19-01-02")`. `with self.assertRaises(ValidationError): AnchorRef(kind="adr", ...)`. Asserts error message names `"adr"`.
- `test_evidence_bundle_frozen_and_forbid_extra` — asserts `model_config` invariants for `EvidenceBundle`.
- `test_anchor_kind_literal_values` — asserts `AnchorKind` accepts only the three literal strings.

**`tests/justify/test_anchors.py`** — Resolver tests, all using `tempfile.TemporaryDirectory` for project root isolation.

- `test_resolve_ghi_populates_fields` — `@covers("REQ-0.0.19-01-03")`. `@patch("gzkit.justify.anchors.run_exec")` returns `(0, '{"number": 232, "title": "...", ...}', "")`. Asserts `AnchorRef(kind="ghi", identifier="GHI-232", title=..., body=..., labels=..., author=...)`.
- `test_resolve_ghi_nonzero_raises_anchor_resolution_error` — `@covers("REQ-0.0.19-01-04")`. Mocked `run_exec` returns `(1, "", "gh: auth required")`. Asserts `AnchorResolutionError` with stderr quoted.
- `test_resolve_ghi_never_uses_shell_true` — `@covers("REQ-0.0.19-01-04")`. Inspects the `run_exec` call args: list form, no `shell=True` kwarg (patched `run_exec` records its args).
- `test_resolve_obpi_locates_via_filename_glob` — `@covers("REQ-0.0.19-01-04")`. Creates `tmp/docs/design/adr/foundation/ADR-0.0.19-.../obpis/OBPI-0.0.19-01-foo.md`, calls `resolve_anchor("OBPI-0.0.19-01", project_root=Path(tmp))`. Asserts `AnchorRef(kind="obpi", identifier="OBPI-0.0.19-01", source_path=...)`.
- `test_resolve_obpi_zero_matches_raises` — fixture tmp with no brief → `AnchorResolutionError`.
- `test_resolve_obpi_multiple_matches_raises_with_candidates` — fixture with two matching briefs → `AnchorResolutionError` whose message names both paths.
- `test_resolve_draft_literal_passthrough` — `@covers("REQ-0.0.19-01-05")`. `resolve_anchor(None, draft_text="hello", draft_slug="refactor-parser")` → `AnchorRef(kind="draft", draft_text="hello", draft_slug="refactor-parser")`.
- `test_resolve_draft_missing_slug_raises_value_error` — `@covers("REQ-0.0.19-01-05")`. Missing slug → `ValueError`.
- `test_resolve_draft_bad_slug_raises_value_error` — slug `"Bad Slug"` → `ValueError`.
- `test_resolve_malformed_raises_value_error_listing_shapes` — `@covers("REQ-0.0.19-01-06")`. `resolve_anchor("foo-bar")` → `ValueError` whose message names `GHI-<N>`, `OBPI-X.Y.Z-NN`, and the draft form.

**`tests/justify/test_evidence.py`** — Evidence gather tests.

- `test_gather_evidence_obpi_all_sources_populated` — `@covers("REQ-0.0.19-01-07")`. Tempdir fixture has `.gzkit/rules/cli.md`, a brief, a mocked `run_exec` returning ledger events + git log. Asserts all five bundle fields populated.
- `test_gather_evidence_draft_has_no_ledger_events` — `@covers("REQ-0.0.19-01-08")`. Draft anchor → `bundle.ledger_events == ()` and `"ledger source not applicable for draft"` (or similar) is in `warnings`.
- `test_gather_evidence_missing_gh_graceful_degradation` — `@covers("REQ-0.0.19-01-09")`. Mocked `run_exec` for ledger returns `(1, ...)` → `bundle.ledger_events == ()`, `warnings` names the unavailable source; NO exception propagates.
- `test_gather_evidence_missing_git_log_graceful_degradation` — similar for git log source.
- `test_gather_evidence_missing_rules_file_graceful_degradation` — `.gzkit/rules/` unreadable or empty → `matching_rules == ()` + warning.
- `test_gather_evidence_related_anchors_resolved_each` — `related=["GHI-1", "GHI-2"]` → `related_anchors` tuple contains two entries.
- `test_gather_evidence_related_anchor_failure_warns` — one related ID unresolvable → it appears in `warnings`, other entries still included.
- `test_gather_evidence_taxonomy_reference_literal_path` — bundle always includes `docs/governance/model-regression-taxonomy.md` as the string reference.
- `test_gather_evidence_never_emits_stdout_stderr` — `@covers("REQ-0.0.19-01-10")`. Captures `sys.stdout` / `sys.stderr` around call; asserts both empty after call.
- `test_gather_evidence_under_3_seconds_with_representative_fixture` — `@covers("REQ-0.0.19-01-10")`. Fixture tempdir with ~20 ADRs/~50 OBPIs (scaled-down representative — 200+ is unnecessary for the timing assertion and would push per-test <200ms). Asserts `elapsed < 3.0` via `time.monotonic()`. **This single test is allowed >200ms** per REQ-09; all others <200ms (REQ-12).
- `test_public_api_export_surface` — `@covers("REQ-0.0.19-01-11")`. Imports `from gzkit.justify import *` into a local namespace and asserts the exported names are exactly `{"AnchorRef", "EvidenceBundle", "AnchorKind", "resolve_anchor", "gather_evidence", "AnchorResolutionError"}`.

## Key Reused Utilities

- `run_exec(cmd, cwd, timeout) -> tuple[int, str, str]` from `src/gzkit/utils.py:15-31` — canonical subprocess wrapper. Used by both `_resolve_ghi` and `_gather_ledger_events` / `_gather_recent_commits`.
- `from pydantic import BaseModel, ConfigDict, Field, field_validator` — matches `src/gzkit/lock_manager.py:18-44` exemplar.
- `@covers(req_id)` from `gzkit.traceability` (defined at `src/gzkit/traceability.py:119-163`) — REQ-pinning decorator.
- `_parse_frontmatter` pattern from `src/gzkit/sync.py:278-299` — adapt (but do NOT import; sync.py parser does not expose `paths:` list semantics). The justify library's rule-reader does its own tiny YAML-list parse (`paths:\n  - "glob1"\n  - "glob2"`) — no third-party YAML dependency added.

## Sequencing (per-increment TDD)

TDD Red-Green-Refactor per REQ increment; no test-dump. Each increment:

1. **REQ-01/02 models** — red: write `test_anchor_ref_is_frozen` + `test_anchor_rejects_adr_kind` in `test_models.py`, run, see ImportError. Green: write `models.py` with `AnchorRef` + `AnchorKind` + `AnchorResolutionError` + the `kind` validator. Tests pass. Refactor if needed.
2. **REQ-03 GHI resolver** — red: `test_resolve_ghi_populates_fields`. Green: `anchors.py` skeleton + `_resolve_ghi`. Refactor.
3. **REQ-04 shell-true + error path** — red/green the two error tests.
4. **REQ-05 OBPI resolver** — red/green the three OBPI tests.
5. **REQ-06 draft + malformed** — red/green the three draft/malformed tests.
6. **REQ-07 five-source gather** — red: `test_gather_evidence_obpi_all_sources_populated`. Green: `evidence.py` skeleton + ThreadPoolExecutor + all five source fetchers. Refactor.
7. **REQ-08/09 graceful degradation** — red/green each missing-source test.
8. **REQ-10 no-I/O / <3s** — red/green `test_gather_evidence_never_emits_stdout_stderr` and the timing test.
9. **REQ-11 public API export** — red: `test_public_api_export_surface`. Green: `__init__.py` with explicit `__all__`. Refactor.
10. **REQ-12** is a meta-requirement on the test suite — validated by running `uv run -m unittest tests.justify -v` and confirming per-test wall-clock.

Commit discipline: one commit per green REQ increment (or a small cluster of tightly related REQs). Trailer: `Task: TASK-0.0.19-01-NN-MM-PP` (to be resolved via `gz covers ADR-0.0.19` at task-start time). Never `--amend`.

## Verification Steps (end of implementation)

Per the brief's Verification section:

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest-justify-01 -- uv run -m unittest tests.justify.test_models tests.justify.test_anchors tests.justify.test_evidence

# Package structure
test -d src/gzkit/justify
test -f src/gzkit/justify/__init__.py
test -f src/gzkit/justify/models.py
test -f src/gzkit/justify/anchors.py
test -f src/gzkit/justify/evidence.py

# Public API smoke check
uv run python -c "from gzkit.justify import AnchorRef, EvidenceBundle, resolve_anchor, gather_evidence; print('OK')"

# REQ → @covers parity
uv run gz covers OBPI-0.0.19-01 --json
```

Plus the OBPI-scoped behavioral tests (Heavy lane bypass: no BDD in this OBPI per the brief — BDD lands in OBPI-05):

```bash
uv run gz test --obpi OBPI-0.0.19-01
```

## Out of Scope (denied paths — not touched)

- `src/gzkit/commands/justify_cmd.py` (OBPI-02)
- `src/gzkit/justify/walkthrough.py` + `templates/` (OBPI-02)
- `src/gzkit/justify/parser.py` (OBPI-03)
- `src/gzkit/cli/parser_artifacts.py` (OBPI-02)
- `.gzkit/skills/gz-justify/**` (OBPI-04)
- `docs/user/commands/**`, `docs/user/manpages/**`, `features/**` (OBPI-05)
- New third-party dependencies (stdlib + Pydantic + existing `run_exec` shim only)

## Risks and Mitigations

- **Risk:** `_gather_matching_rules` for `kind="obpi"` needs to read the parent ADR to derive anchor surface paths, which means a filesystem read that might be missing in a test fixture. **Mitigation:** graceful degradation path — if parent ADR cannot be found, fall back to always-matching rules + warning; do not raise.
- **Risk:** `concurrent.futures.ThreadPoolExecutor` with `subprocess.run` on Windows can hit import-deadlock in rare cases. **Mitigation:** timeout=3.0 on the executor + per-future timeout=10 on the subprocess. No precedent in gzkit for either asyncio or executor, but this is the safer choice per research.
- **Risk:** `gz state --json` invocation in a test fixture requires `uv` to be on PATH, which would make the test slow and environment-dependent. **Mitigation:** all ledger fetches in tests mock `run_exec` directly; no real `uv run gz state` subprocess is spawned from tests.
- **Risk:** <3s timing assertion is flaky on loaded CI. **Mitigation:** timing test uses scaled fixture (~20 ADRs); locally the bundle completes in tens of milliseconds with mocked subprocesses; real run is dominated by subprocess startup (~100-500ms per call × 5 concurrent = ~500ms worst case). Generous ceiling.

## Completion Criteria

- All 12 REQs have at least one covering test; `gz covers OBPI-0.0.19-01 --json` reports `uncovered_reqs == 0`.
- `uv run gz lint`, `uv run gz typecheck`, `uv run gz test --obpi OBPI-0.0.19-01` all pass.
- Public API smoke check one-liner succeeds.
- Git tree clean and synced; two-sync pattern executed at Stage 5.
- Stage 4 evidence presented with fully-populated REQ coverage table; Stage 5 completion atomic via `gz obpi complete`.
