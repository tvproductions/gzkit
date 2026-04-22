---
id: OBPI-0.0.19-01-anchor-resolution-and-evidence
parent: ADR-0.0.19
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.19-01-anchor-resolution-and-evidence: Anchor resolution and evidence gathering

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
- **Checklist Item:** #1 — Anchor resolution + evidence gathering. Pydantic models (`AnchorRef`, `EvidenceBundle`, `RuleCitation`, `CommitRef`, `LedgerEvent`); GHI/OBPI/draft resolvers; five-source concurrent grounding gather with graceful degradation for missing sources.

**Status:** Draft

## Objective

Build the evidence-gathering substrate of `gzkit justify` as a pure, side-effect-free library layer under `src/gzkit/justify/`. This OBPI delivers the Pydantic data models (`AnchorRef`, `EvidenceBundle`, `RuleCitation`, `CommitRef`, `LedgerEvent`) and the resolver/gather functions that turn a raw anchor (GHI identifier, OBPI identifier, or draft text) into a fully-populated `EvidenceBundle` suitable for handing to the scaffold renderer in OBPI-02. The CLI surface, Jinja2 template, and Walkthrough rendering live in OBPI-02 and are out of scope here. This OBPI produces no operator-visible command and no markdown output — it delivers the internal API the next OBPI consumes.

## Lane

**Heavy** — This OBPI introduces a new Python package (`src/gzkit/justify/`) and a set of governance-adjacent data models (ledger event shapes, rule citations) that downstream OBPIs depend on. The contract is load-bearing even though no CLI surface ships in this brief.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/justify/__init__.py` — new package, re-exports the public API consumed by OBPI-02
- `src/gzkit/justify/models.py` — Pydantic models (`AnchorRef`, `EvidenceBundle`, `RuleCitation`, `CommitRef`, `LedgerEvent`, `AnchorKind` enum)
- `src/gzkit/justify/anchors.py` — anchor resolvers (GHI via `gh` subprocess, OBPI via filesystem glob, draft via literal pass-through)
- `src/gzkit/justify/evidence.py` — concurrent five-source grounding gather with graceful degradation
- `tests/justify/__init__.py` — new test package
- `tests/justify/test_models.py` — Pydantic model unit tests (frozen/extra=forbid behavior, validator edge cases)
- `tests/justify/test_anchors.py` — anchor resolver tests (mocked `gh` subprocess, fixture OBPI briefs, draft pass-through)
- `tests/justify/test_evidence.py` — grounding gather tests (table-driven source availability, missing-source annotation, concurrency correctness)
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md` — parent ADR for intent (read-only; not modified by this OBPI)

## Denied Paths

- `src/gzkit/commands/justify_cmd.py` — CLI handler lives in OBPI-02
- `src/gzkit/justify/walkthrough.py` — Walkthrough model + Jinja2 rendering lives in OBPI-02
- `src/gzkit/justify/templates/**` — Jinja2 templates live in OBPI-02
- `src/gzkit/justify/parser.py` — reverse parser lives in OBPI-03
- `src/gzkit/cli/parser_artifacts.py` — CLI registration lives in OBPI-02
- `.gzkit/skills/gz-justify/**` — skill authoring lives in OBPI-04
- `docs/user/commands/**`, `docs/user/manpages/**`, `features/**` — docs + BDD live in OBPI-05
- New third-party dependencies (the substrate uses stdlib + existing Pydantic + existing `gh` subprocess shim only)
- Any file mutation outside `Allowed Paths`

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: All five data models (`AnchorRef`, `EvidenceBundle`, `RuleCitation`, `CommitRef`, `LedgerEvent`) are defined as Pydantic `BaseModel` subclasses with `model_config = ConfigDict(frozen=True, extra="forbid")`. Stdlib `dataclass` is NEVER used for these shapes.
2. REQUIREMENT: `AnchorKind` is a `typing.Literal["ghi", "obpi", "draft"]` alias (or an equivalent `StrEnum`). The library NEVER accepts `"adr"` as an anchor kind; attempting to construct an `AnchorRef` with `kind="adr"` raises `ValidationError`.
3. REQUIREMENT: `resolve_anchor(raw: str, *, draft_text: str | None = None, draft_slug: str | None = None) -> AnchorRef` accepts three input shapes: `"GHI-<N>"` / `"#<N>"` (GHI kind), `"OBPI-<X.Y.Z>-<NN>"` (OBPI kind), or `raw=None` with `draft_text` populated (draft kind). Malformed inputs raise `ValueError` with a message naming the accepted shapes.
4. REQUIREMENT: GHI resolution calls `gh issue view <N> --json number,title,body,labels,author` via `subprocess.run` with `text=True, encoding="utf-8", check=False`. `shell=True` is NEVER used. Non-zero exit or empty output raises `AnchorResolutionError` with the underlying stderr quoted. Network calls outside of `gh` are NEVER made.
5. REQUIREMENT: OBPI resolution uses `pathlib.Path` globbing against `docs/design/adr/**/obpis/<OBPI-id>.md` (case-sensitive). If zero matches, raises `AnchorResolutionError`. If multiple matches, raises `AnchorResolutionError` naming all candidates. The resolver NEVER keys on frontmatter `id:` — it keys on filename match (consistent with `.gzkit/rules/state-doctrine` invariants).
6. REQUIREMENT: Draft resolution with `raw=None` requires both `draft_text` (non-empty) and `draft_slug` (kebab-case, matches `^[a-z][a-z0-9-]*$`). Missing or malformed inputs raise `ValueError`.
7. REQUIREMENT: `gather_evidence(anchor: AnchorRef, *, related: list[str] | None = None) -> EvidenceBundle` gathers from exactly five sources, executed concurrently via `asyncio.gather` or `concurrent.futures.ThreadPoolExecutor`:
   (a) `.gzkit/rules/*.md` files whose `paths:` frontmatter globs match the anchor's inferred surface (for OBPI: parent ADR's allowed paths; for GHI: heuristic on anchor body text; for draft: always-matching rules only);
   (b) Ledger events via `gz state --json` filtered to the anchor identifier — only populated when anchor kind is `"obpi"`;
   (c) Git log: `git log --since='60 days ago' --oneline --grep='<anchor-id or scope>'` scoped to the anchor identifier;
   (d) Related anchors: each ID in `related` resolved via `resolve_anchor` and stored as `AnchorRef` entries in `EvidenceBundle.related_anchors`;
   (e) A literal reference to `docs/governance/model-regression-taxonomy.md` (path string; the file is cited, not inlined).
8. REQUIREMENT: Missing-source graceful degradation is NON-FATAL. If `gh` is unavailable (GHI), if `gz state --json` fails (OBPI), if `git log` fails, or if `.gzkit/rules/*.md` cannot be read, the source is recorded as an empty list on `EvidenceBundle` and a warning note is appended to `EvidenceBundle.warnings: list[str]` naming the unavailable source. The library NEVER raises on missing sources except for the anchor resolution itself (REQ-04/05/06).
9. REQUIREMENT: Concurrent gather completes in under 3.0 seconds wall-clock on a clean repo with all five sources reachable. Measured via a test that populates a temp repo with representative fixtures and asserts the elapsed time.
10. REQUIREMENT: The library NEVER calls an LLM, NEVER mutates filesystem state outside of temp test fixtures, NEVER reads user credentials beyond what `gh` CLI already has cached, and NEVER emits to stdout/stderr directly (callers own I/O).
11. REQUIREMENT: Public API re-exported from `src/gzkit/justify/__init__.py` is limited to: `AnchorRef`, `EvidenceBundle`, `AnchorKind`, `resolve_anchor`, `gather_evidence`, `AnchorResolutionError`. Internal models (`RuleCitation`, `CommitRef`, `LedgerEvent`) are importable but are NOT in the top-level `__all__`.
12. REQUIREMENT: Unit tests cover every REQ. Test naming pins REQ identifiers (e.g. `test_anchor_rejects_adr_kind_REQ_0_0_19_01_02`). Tests use `tempfile.TemporaryDirectory` for filesystem fixtures; NEVER touch the live project root or the live ledger.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` — agent operating contract
- [ ] `.gzkit/rules/models.md` — Pydantic model policy (`ConfigDict(frozen=True, extra="forbid")`)
- [ ] `.gzkit/rules/tests.md` — unittest discipline, REQ-pinning naming, tempfile isolation
- [ ] `.gzkit/rules/cross-platform.md` — UTF-8 encoding, pathlib, subprocess list form
- [ ] Parent ADR — full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
- [ ] Sibling OBPIs in same ADR (01-05)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/` package structure exists (confirmed)
- [ ] `src/gzkit/ledger.py` and related ledger-event modules exist (source for `gz state --json` consumer API)
- [ ] `.gzkit/rules/` has `paths:` frontmatter on rule files (source for rule-matching grounding)
- [ ] `gh` CLI available in test environment (mocked in unit tests via subprocess patch)

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/validate_frontmatter.py` — exemplar for ledger graph access patterns
- [ ] `src/gzkit/ledger.py` — canonical ledger reader
- [ ] `src/gzkit/governance/` — existing Pydantic models for shape precedent
- [ ] `tests/commands/common.py` — canonical subprocess patcher helpers (`_git_subprocess_patcher`)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] No docs changes in this OBPI — docs land in OBPI-05. Gate 3 passes trivially for this brief; the ADR-level Gate 3 fires at ADR closeout.

### Gate 4: BDD (Heavy only)

- [ ] No BDD scenarios in this OBPI — scenarios land in OBPI-05. Gate 4 passes trivially for this brief.

### Gate 5: Human (Heavy only)

- [ ] Human attestation deferred to ADR-level closeout per lane inheritance protocol.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest-justify-01 -- uv run -m unittest tests.justify.test_models tests.justify.test_anchors tests.justify.test_evidence

# Package structure check
test -d src/gzkit/justify
test -f src/gzkit/justify/__init__.py
test -f src/gzkit/justify/models.py
test -f src/gzkit/justify/anchors.py
test -f src/gzkit/justify/evidence.py

# Public API smoke check (no LLM, no CLI — just library importability)
uv run python -c "from gzkit.justify import AnchorRef, EvidenceBundle, resolve_anchor, gather_evidence; print('OK')"
```

## Acceptance Criteria

- [ ] REQ-0.0.19-01-01: Given a call to construct `AnchorRef(kind="ghi", identifier="GHI-232", ...)`, when the model is instantiated with valid fields, then the instance is returned with `frozen=True` preventing subsequent mutation.
- [ ] REQ-0.0.19-01-02: Given a call to construct `AnchorRef(kind="adr", ...)`, when the model is instantiated, then a `ValidationError` is raised naming `"adr"` as an unsupported anchor kind.
- [ ] REQ-0.0.19-01-03: Given `resolve_anchor("GHI-232")` with a mocked `gh` subprocess returning valid JSON, when the resolver runs, then the returned `AnchorRef` has `kind="ghi"`, `identifier="GHI-232"`, and populated `title`/`body` fields.
- [ ] REQ-0.0.19-01-04: Given `resolve_anchor("OBPI-0.0.19-01")` against a temp repo containing the brief file, when the resolver runs, then it locates the brief via `pathlib.Path` glob against `docs/design/adr/**/obpis/OBPI-0.0.19-01-*.md` and returns an `AnchorRef` populated from filename match.
- [ ] REQ-0.0.19-01-05: Given `resolve_anchor(None, draft_text="...", draft_slug="refactor-parser")`, when the resolver runs, then a draft `AnchorRef` is returned with the literal text preserved; missing `draft_slug` raises `ValueError`.
- [ ] REQ-0.0.19-01-06: Given a malformed anchor string `"foo-bar"`, when `resolve_anchor` is called, then a `ValueError` is raised with a message listing the three accepted anchor shapes.
- [ ] REQ-0.0.19-01-07: Given an `AnchorRef` of kind `"obpi"` and a temp repo with all five grounding sources available, when `gather_evidence` runs, then the returned `EvidenceBundle` contains non-empty `matching_rules`, `ledger_events`, `recent_commits`, and `related_anchors` (when `related=` was passed), plus the taxonomy reference path.
- [ ] REQ-0.0.19-01-08: Given an `AnchorRef` of kind `"draft"`, when `gather_evidence` runs, then `ledger_events` is an empty list (no ledger entries for drafts) and the `warnings` field contains a note explaining the absence.
- [ ] REQ-0.0.19-01-09: Given an `AnchorRef` and a mocked `subprocess.run` that simulates `gh` returning non-zero exit, when `gather_evidence` runs, then the returned `EvidenceBundle` has empty `matching_rules` (or appropriate missing source) and `warnings` lists the unavailable source; NO exception propagates.
- [ ] REQ-0.0.19-01-10: Given a temp repo of representative size (~80 ADRs, ~200 OBPIs fixtures), when `gather_evidence` runs, then wall-clock is under 3.0 seconds (measured in a dedicated timing test).
- [ ] REQ-0.0.19-01-11: Given `from gzkit.justify import *`, when the public API is imported, then exactly `AnchorRef`, `EvidenceBundle`, `AnchorKind`, `resolve_anchor`, `gather_evidence`, `AnchorResolutionError` are exposed (verified via `__all__`).
- [ ] REQ-0.0.19-01-12: Given any test in this OBPI's suite, when it runs, then it completes in under 200ms on a typical workstation (per `.gzkit/rules/tests.md` unit-tier contract) and uses only `tempfile.TemporaryDirectory` for filesystem fixtures — no live project root access.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQ-IDs, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Library layer exists; downstream OBPI-02 can consume it
- [ ] **Key Proof:** `uv run python -c "from gzkit.justify import AnchorRef, gather_evidence"` succeeds
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

Not applicable at this OBPI; deferred to OBPI-05.

### Gate 4 (BDD)

Not applicable at this OBPI; deferred to OBPI-05.

### Gate 5 (Human)

Deferred to ADR-level closeout.

### Value Narrative

**Before:** `gzkit justify` does not exist; there is no evidence-gathering substrate to ground pre-execution reasoning walkthroughs.

**After:** `src/gzkit/justify/` exposes `resolve_anchor` and `gather_evidence` as a pure library that any caller (CLI, test, future skill) can use to turn a GHI/OBPI/draft anchor into an evidence-populated `EvidenceBundle` without network, LLM, or file mutation.

### Key Proof


```
$ uv run python -c "from gzkit.justify import AnchorRef, EvidenceBundle, resolve_anchor, gather_evidence, AnchorKind, AnchorResolutionError; print('OK')"
OK

$ uv run gz covers OBPI-0.0.19-01 --json | tail -7
  "summary": {
    "identifier": "OBPI-0.0.19-01",
    "total_reqs": 12,
    "covered_reqs": 12,
    "uncovered_reqs": 0,
    "coverage_percent": 100.0
  }

ARB receipts:
  lint:    arb-ruff-5f6f745bf683466d84a908c0f67e3b49
  types:   arb-step-typecheck-8589d2b09f0046e184f98369157279f6
  tests:   arb-step-unittest-justify-01-0b8b75460d9c48bd8897d860405bda82 (31/31 passed, 23ms)
```

### Implementation Summary


- Files created: src/gzkit/justify/__init__.py, src/gzkit/justify/models.py, src/gzkit/justify/anchors.py, src/gzkit/justify/evidence.py, tests/justify/__init__.py, tests/justify/test_models.py, tests/justify/test_anchors.py, tests/justify/test_evidence.py
- Tests added: 31 (REQ-01..-12 each covered; 12/12 @covers parity at 100%)
- Public API: AnchorRef, EvidenceBundle, AnchorKind, resolve_anchor, gather_evidence, AnchorResolutionError
- Concurrency: concurrent.futures.ThreadPoolExecutor(max_workers=5); per-source graceful degradation with warnings tuple
- Reused utilities: run_exec (src/gzkit/utils.py:15-31); @covers (src/gzkit/traceability.py:119-163); Pydantic ConfigDict(frozen=True, extra='forbid') matching lock_manager.py:18-44 exemplar
- Date completed: 2026-04-21
- Attestation status: human-attested (normal mode)
- Defects noted: GHI #288 filed for plan-mode harness vs plan-audit-gate deadlock (unrelated to this OBPI's scope; surfaced during Stage 1 entry)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Library substrate for `gz justify` landed as the pure side-effect-free foundation OBPI-02 consumes. Five-source concurrent ThreadPoolExecutor gather with per-source graceful degradation; Pydantic frozen models matching the lock_manager exemplar; explicit __all__ exposes exactly the six public names required by REQ-11. 31/31 unit tests green; 12/12 REQs @covers parity at 100% (receipt arb-step-unittest-justify-01-0b8b75460d9c48bd8897d860405bda82). Lint clean (arb-ruff-5f6f745bf683466d84a908c0f67e3b49); typecheck clean (arb-step-typecheck-8589d2b09f0046e184f98369157279f6). No stdout/stderr from library; <3s wall-clock on scaled fixture. Filed GHI #288 for the plan-mode harness / plan-audit-gate deadlock surfaced at Stage 1 entry — unrelated to this OBPI's scope.
- Date: 2026-04-22

---

**Brief Status:** Completed

**Date Completed:** 2026-04-22

**Evidence Hash:** -
