---
id: OBPI-0.25.0-26-drift-detection-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 26
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-26: Drift Detection Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-26 — "Evaluate and absorb opsdev/lib/drift_detection.py (384 lines) — validation receipt temporal anchoring"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/drift_detection.py` (384 lines) against
gzkit's drift detection surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers validation receipt temporal anchoring. gzkit's
equivalent surface spans `commands/drift.py` (186 lines) and `triangle.py`
(372 lines) — approximately 560+ lines across 2 modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/commands/drift.py`, `src/gzkit/triangle.py` (~560+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's drift detection around airlineops's temporal anchoring model

## Comparison

The two implementations share only the word *drift*. They address orthogonal
concerns and operate over different inputs.

### airlineops `drift_detection.py` (384 lines)

| Function / Type | Lines | Assessment |
|-----------------|-------|------------|
| `DriftStatus = Literal["none", "commits_ahead", "diverged"]` | 32 | Closed three-state classification: no drift, linear progression, history rewrite |
| `DriftResult` (Pydantic, frozen) | 35-54 | ADR-level result: `adr_id`, `status`, `anchor_commit`, `head_commit`, `commits_ahead`, `message` |
| `ObpiDriftResult` (Pydantic, frozen) | 57-78 | OBPI-level result: same fields plus `obpi_id` and `adr_id` |
| `_get_head_commit()` | 86-105 | Thin `git rev-parse HEAD` wrapper; raises `RuntimeError` if git absent or unresolvable |
| `_is_ancestor(ancestor, descendant)` | 108-129 | `git merge-base --is-ancestor`; returns `True`/`False`/`None` (None = commit not in repo, exit 128) |
| `_count_commits_between(ancestor, descendant)` | 132-154 | `git rev-list --count A..B`; returns `int` or `None` on failure |
| `classify_drift(...)` | 162-225 | **Pure** function (no I/O). Five-branch classification: same commit → `none`; ancestor missing from repo → `diverged`; anchor is ancestor of HEAD → `commits_ahead`; anchor not ancestor → `diverged`; each branch produces a human-readable message |
| `detect_drift(adr_id)` | 233-262 | Orchestrator: locates ADR folder via `find_adr_folder`, reads receipts via `read_receipts(VALIDATION_LEDGER_FILENAME)`, picks the most recent, calls git helpers and `classify_drift` |
| `OBPI_AUDIT_FILENAME = "obpi-audit.jsonl"` | 269 | Per-ADR per-OBPI audit ledger filename |
| `_read_anchored_obpi_entries(...)` | 272-325 | JSONL parser with last-entry-wins semantics; filters by `adr_id` and optional `obpi_id`; ignores malformed lines with a warning |
| `detect_obpi_drift(adr_id, *, obpi_id=None)` | 328-374 | Orchestrator: reads `obpi-audit.jsonl` per OBPI, classifies each, returns sorted list |
| `__all__` | 377-384 | Public surface: `DriftStatus`, `DriftResult`, `ObpiDriftResult`, `classify_drift`, `detect_drift`, `detect_obpi_drift` |

The architecture is two-layer-pure-plus-orchestrator:
**git helpers (private)** → **`classify_drift` (pure)** → **detector orchestrators**.
The pure classifier is trivially testable without mocks (all I/O results are
arguments). All Pydantic models use `ConfigDict(extra="forbid", frozen=True)`.

### gzkit drift surface (~558 lines across 2 modules + 1 utility)

| Module / Function | Lines | Capabilities |
|-------------------|-------|--------------|
| `triangle.py:ReqId` / `ReqEntity` / `DiscoveredReq` | 22-87, 167-179 | REQ identifier parser (`REQ-<semver>-<obpi_item>-<criterion>`) and entity/discovery models |
| `triangle.py:VertexType` / `EdgeType` / `VertexRef` / `LinkageRecord` | 95-153 | Spec-test-code triangle vertex and edge types; covers / proves / justifies edges |
| `triangle.py:extract_reqs_from_brief` / `scan_briefs` | 182-281 | Brief scanner: walks `docs/design/adr/`, parses YAML frontmatter, extracts checkbox-state REQ entities from `## Acceptance Criteria` sections |
| `triangle.py:DriftSummary` / `DriftReport` | 298-324 | Counts and lists for unlinked specs, orphan tests, unjustified code changes |
| `triangle.py:detect_drift(reqs, linkages, changed_code, ts)` | 327-372 | **Pure** function (no I/O): computes `unlinked_specs` (REQs with no `@covers` linkage), `orphan_tests` (`@covers` referencing non-existent REQs), and `unjustified_code_changes` (changed `src/` files with no `JUSTIFIES` edge) |
| `commands/drift.py:scan_covers_references(test_dir)` | 32-63 | Regex-driven scan of `tests/**/*.py` for `@covers REQ-…` markers; emits `LinkageRecord` |
| `commands/drift.py:get_changed_files(project_root)` | 66-96 | `git diff --name-only HEAD` plus `--cached` to enumerate staged + unstaged source changes |
| `commands/drift.py:_format_human` / `_format_plain` | 99-147 | Human and plain output formatters |
| `commands/drift.py:drift_cmd(...)` | 150-186 | CLI orchestrator wired to `gz drift`; supports `--json` and `--plain`; exits 1 when total drift > 0 |
| `utils.py:resolve_git_head_commit(project_root)` | 38-49 | **Returns `--short=7` HEAD SHA**, cached per process |
| `utils.py:capture_validation_anchor_with_warnings(project_root, adr_id)` | 64-95 | Captures `{"commit": <short-7>, "tag": <tag>, "semver": <X.Y.Z>}` for receipt evidence |
| `commands/adr_audit.py:adr_emit_receipt_cmd` | 396-403 | Calls `capture_validation_anchor` and stores it in `audit_receipt_emitted` events under `extra["anchor"]` |
| `commands/obpi_complete.py` / `commands/obpi_cmd.py` | 186, 157 | Same anchor capture for `obpi_receipt_emitted` events under `extra["anchor"]` |

The architecture is **single-layer pure** for the structural detector
(`triangle.detect_drift`) and **anchor-write-only** for temporal data: gzkit
captures `anchor.commit` (short SHA-7) into ledger receipt events but never
reads it back to ask "is this validation stale relative to HEAD?".

### Capability Comparison

| Dimension | airlineops `drift_detection.py` (384 lines) | gzkit drift surface (558 lines + anchor capture) | Winner |
|-----------|---------------------------------------------|--------------------------------------------------|--------|
| Problem domain | **Temporal drift** — has the codebase moved since validation? | **Structural drift** — is the spec/test/code triangle consistent? | Different problems |
| Drift inputs | Validation receipt anchor commit + git HEAD | OBPI brief REQs + `@covers` linkages + git change set | Different inputs |
| Drift output model | Three-state literal (`none` / `commits_ahead` / `diverged`) per anchored ADR/OBPI | Three lists (unlinked specs / orphan tests / unjustified code) per scan | Different outputs |
| Pure vs orchestrator separation | `classify_drift` is pure with all I/O passed in as arguments; orchestrators wire I/O | `triangle.detect_drift` is pure (sets in / `DriftReport` out); orchestrator in `commands/drift.py` | Both equivalent — both follow the pure-plus-orchestrator pattern |
| Anchor reader | `detect_drift(adr_id)` reads validation receipts; `detect_obpi_drift(adr_id)` reads `obpi-audit.jsonl` | **None.** `capture_validation_anchor_with_warnings` writes anchors into `audit_receipt_emitted`/`obpi_receipt_emitted` events but no detector reads them back | airlineops only — capability gap in gzkit |
| Anchor commit format | Full SHA from `git rev-parse HEAD` | **Short SHA-7** from `git rev-parse --short=7 HEAD` | Different — adaptation must normalize via `git rev-parse <short>` before comparing against full HEAD |
| Receipt source-of-truth | Per-ADR `validation-ledger.jsonl` and per-ADR `obpi-audit.jsonl` files inside the ADR folder | Single `.gzkit/ledger.jsonl` (event sourcing) with `audit_receipt_emitted` and `obpi_receipt_emitted` events filtered by `id` | Different ledger topology — adaptation must read `.gzkit/ledger.jsonl` and filter, not open per-ADR files |
| Convention compliance (Pydantic) | Frozen `BaseModel` with `ConfigDict(extra="forbid", frozen=True)` | Frozen `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` | Both equivalent — airlineops module already aligns |
| Convention compliance (pathlib + UTF-8) | `pathlib.Path` throughout; explicit `encoding="utf-8"` on all reads | Same | Both equivalent |
| Convention compliance (subprocess) | Direct `subprocess.run([...], capture_output=True, text=True)` per call | Centralized `git_cmd()` helper in `utils.py` (with caching) | gzkit — adaptation should reuse `git_cmd()` to share encoding, error capture, and the HEAD cache |
| Cross-platform robustness | List-form subprocess; UTF-8 by default; raises `RuntimeError` if git absent | List-form subprocess; UTF-8 by default; returns `(rc, stdout, stderr)` tuples — no exception path | Both robust; gzkit's tuple style composes more cleanly with `classify_drift`'s pure-classifier signature |
| Test architecture | Pure classifier is mock-free by construction; orchestrators need temp git + temp ledger fixtures | Pure detector is mock-free; CLI tested via `subprocess`/temp fixtures | Both testable — adaptation can adopt the same pattern |
| CLI surface | None — module is library-only; airlineops has no `airlineops drift` command | `gz drift` (triangle); no `gz drift --temporal` or equivalent | Different — adopting airlineops adds a library, not yet a CLI surface |
| Self-declared status | Production module under active use in airlineops governance flow | Production module under active use; anchor capture present but unused for drift | airlineops |
| Subtraction test | "Is temporal drift detection airline-specific?" — **No.** It operates on git commits and a generic validation-receipt schema that gzkit already maintains | N/A | airlineops capability is portable |

## Decision: Absorb

gzkit captures validation anchor commits into ledger receipt events but has no
detector that reads them back. The airlineops `drift_detection.py` module fills
that gap exactly: it provides a pure three-state classifier plus thin I/O
orchestrators built on the same Pydantic-frozen, pathlib, UTF-8, list-form
subprocess conventions gzkit already follows. The two modules' use of the word
*drift* is semantic overload — temporal drift and structural triangle drift are
orthogonal — so the absorbed module lives at `src/gzkit/temporal_drift.py` and
does not collide with the existing `triangle.py` / `gz drift` surface.

**Rationale:**

1. **Subtraction test passes — temporal drift is not airline-specific.** The
   airlineops module operates on `git rev-parse`, `git merge-base --is-ancestor`,
   and `git rev-list --count`, plus a validation-receipt schema with
   `anchor.commit`. None of those inputs are airline-domain. Removing every
   airline-specific concept from `drift_detection.py` leaves the entire module
   intact. By the subtraction test, it belongs in gzkit.
2. **Concrete capability gap — gzkit writes anchors but never reads them.**
   `src/gzkit/utils.py:64` captures `{"commit": <short-7>, "tag": <tag>,
   "semver": <X.Y.Z>}` and `src/gzkit/commands/adr_audit.py:396` and
   `src/gzkit/commands/obpi_complete.py:186` write that anchor into
   `audit_receipt_emitted` and `obpi_receipt_emitted` ledger events. The data
   has been collected on every receipt for months — confirmed by ledger search
   (`grep '"anchor"' .gzkit/ledger.jsonl` returns real entries, e.g. `{"commit":
   "19f5230", "semver": "0.7.0"}`). Nothing reads it back. Operators have no way
   to ask "this ADR was validated, but is the validation still meaningful at the
   current commit?" — the gap is silent and structural.
3. **Architectural fit — pure classifier separated from I/O.** The airlineops
   module is the textbook shape gzkit already favors: a pure function
   (`classify_drift`) that takes I/O results as arguments, plus thin
   orchestrators that perform the I/O. `triangle.detect_drift` follows the same
   shape. Importing the pattern reinforces it; rewriting from scratch would
   waste the design work airlineops already did.
4. **Convention alignment — minimal adaptation surface.** All `BaseModel` types
   already use `ConfigDict(extra="forbid", frozen=True)`. All file I/O uses
   `pathlib.Path` with explicit `encoding="utf-8"`. All subprocess calls are
   list-form, capture-output. The only structural change required during
   absorption is replacing direct `subprocess.run` with `gzkit.utils.git_cmd()`
   so the absorbed module shares gzkit's HEAD cache and error-capture
   conventions — and that change *removes* duplication rather than adding it.
5. **Anchor format normalization is mechanical.** gzkit stores anchors as short
   SHA-7 (`git rev-parse --short=7 HEAD`), while airlineops compares full SHAs.
   The `classify_drift` function does `if anchor_commit == head_commit:`, which
   would never match short-vs-full. The fix is one line in the orchestrator:
   resolve the short SHA via `git rev-parse <short>` before comparison. This is
   noted as a known integration step in the implementation, not a blocker.
6. **Receipt source-of-truth bridge is mechanical.** airlineops reads
   per-ADR `validation-ledger.jsonl` and per-ADR `obpi-audit.jsonl` files;
   gzkit uses a single event-sourced `.gzkit/ledger.jsonl` filtered by
   `event` and `id`. The orchestrators in `temporal_drift.py` are rewritten to
   read the gzkit ledger; the pure `classify_drift` function and the git
   helpers are unchanged. The split-by-purity in airlineops's design is
   exactly what makes this swap surgical.
7. **Orthogonal to existing `gz drift` (triangle).** The absorbed module lives
   at `src/gzkit/temporal_drift.py`, not inside `commands/drift.py` or
   `triangle.py`. The two `drift` concerns share no state, no functions, and no
   types. CLI surfacing is deliberately deferred to a follow-on OBPI so this
   brief stays focused on absorption — the standalone library is importable and
   tested as soon as it lands.

### Gate 4 (BDD): N/A

No operator-visible behavior change in this OBPI. The absorbed module is a
library surface; no new CLI subcommand, no change to `gz drift`, no change to
any existing command output. CLI surfacing of temporal drift is a follow-on
OBPI. Per the parent ADR's lane definition, a brief may record BDD as `N/A`
when the change does not alter operator-visible behavior; that condition is met
here. When a future OBPI wires this module into a CLI surface, that brief will
own the corresponding behave coverage.

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

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — `src/gzkit/temporal_drift.py` plus `tests/test_temporal_drift.py` (25 tests)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision — **Absorb**
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (library-only addition; no CLI surface change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change — see "Gate 4 (BDD): N/A" subsection above

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-26-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-26-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [x] REQ-0.25.0-26-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [x] REQ-0.25.0-26-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted — N/A (Absorb decision; see
  Decision section for rationale that this is not Confirm/Exclude).
- [x] REQ-0.25.0-26-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/drift_detection.py
# Expected: airlineops source under review exists

test -f src/gzkit/commands/drift.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass — `tests/test_temporal_drift.py` (25 tests, all pass)
- [x] **Gate 3 (Docs):** Decision rationale completed (Absorb, with 7-point rationale)
- [x] **Gate 4 (BDD):** N/A — library-only addition, no operator-visible behavior change
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

gzkit's governance ledger has captured a `{"commit": <short-7>, "tag": <tag>,
"semver": <X.Y.Z>}` anchor inside every `audit_receipt_emitted` and
`obpi_receipt_emitted` event for months, via
`capture_validation_anchor_with_warnings()` in `src/gzkit/utils.py:64-95`. The
data is real — `grep '"anchor"' .gzkit/ledger.jsonl` returns concrete entries
like `{"commit": "19f5230", "semver": "0.7.0"}`. But no detector has ever
read that data back. Operators have had no way to ask "this ADR was validated
weeks ago — is the validation still meaningful at HEAD?" The answer has lived
on disk, unread, since the first anchored receipt was written.

airlineops's `opsdev/lib/drift_detection.py` (384 lines) is the textbook
implementation of exactly that detector. It is a two-layer pure-plus-orchestrator
design: a pure `classify_drift()` function that takes git results as
arguments and returns a frozen Pydantic `DriftResult`, plus thin orchestrators
(`detect_drift`, `detect_obpi_drift`) that perform the I/O and delegate to the
classifier. Every choice in the module — `ConfigDict(extra="forbid", frozen=True)`,
explicit `encoding="utf-8"`, list-form subprocess calls, three-state
`Literal["none", "commits_ahead", "diverged"]` classification with
`commit not found in repo` collapsed into `diverged` — is already a gzkit
convention. The subtraction test passes cleanly: nothing in the module is
airline-domain. Everything operates over git plus a generic validation-receipt
schema gzkit already maintains.

Two integration deltas emerged during absorption and were resolved
mechanically inside the orchestrators while leaving the pure classifier
unchanged. **First**, gzkit stores anchors as **short SHA-7**
(`git rev-parse --short=7 HEAD`), while airlineops compares full SHAs;
`classify_drift`'s `anchor_commit == head_commit` check would never match
short-vs-full. The fix is one helper, `_resolve_full_commit(short)`, that
runs `git rev-parse <short>` and either returns the full SHA or returns
`None` (which the orchestrator threads into `is_ancestor_result=None`,
producing the correct `diverged: anchor commit X not found in repository
history` classification for free). **Second**, airlineops reads per-ADR
`validation-ledger.jsonl` and per-ADR `obpi-audit.jsonl` files inside each
ADR folder; gzkit uses a single event-sourced `.gzkit/ledger.jsonl` filtered
by event type and `id` (or `parent` for OBPI events). The orchestrators in
`temporal_drift.py` use `gzkit.ledger.Ledger.query()` to filter
`audit_receipt_emitted` and `obpi_receipt_emitted` events, walk in reverse
to find the most recent anchored entry per artifact, and pass the result
into the unchanged classifier. The pure classifier is byte-equivalent to
airlineops's; it never had to know about either delta.

Subprocess calls go through `gzkit.utils.git_cmd()` rather than
direct `subprocess.run()`, sharing gzkit's HEAD cache, encoding, and
error-capture conventions. This is the only structural deviation from the
upstream module and it *removes* duplication rather than adding it. The new
module is intentionally library-only — `src/gzkit/temporal_drift.py` is
importable but exposes no CLI surface. Wiring it into a `gz drift --temporal`
or `gz validate --drift` mode is a follow-on OBPI; this brief stays narrow
and the absorbed module ships behind a stable, tested public API
(`DriftStatus`, `DriftResult`, `ObpiDriftResult`, `classify_drift`,
`detect_drift`, `detect_obpi_drift`).

The absorbed module lives at `src/gzkit/temporal_drift.py`, deliberately
separate from `gzkit.triangle` and `gzkit.commands.drift`. The two `drift`
concerns share no state, no functions, and no types. Triangle drift answers
"is the spec/test/code triangle structurally consistent?" Temporal drift
answers "has the codebase moved since validation?" They are orthogonal,
they are now both supported, and they can be wired into the same operator
surface in a future OBPI without coupling. **Decision: Absorb.**

### Implementation Summary


- **Decision:** Absorb — temporal anchor drift detection is the missing
  reader for gzkit's existing anchor-write surface
- **Capability gap closed:** gzkit captured `anchor.commit` in receipt
  events for months without any code path that read it back; the absorbed
  module is the first such reader
- **New module:** `src/gzkit/temporal_drift.py` (~280 lines) — adapted
  from `airlineops/src/opsdev/lib/drift_detection.py` (384 lines), with
  three changes: (1) subprocess calls route through `gzkit.utils.git_cmd`,
  (2) short-SHA-7 anchors are normalized via `_resolve_full_commit` before
  classification, (3) receipts are read from `.gzkit/ledger.jsonl` filtered
  by `audit_receipt_emitted` (ADR) or `obpi_receipt_emitted` (OBPI), not
  per-ADR ledger files
- **Pure classifier:** `classify_drift()` is byte-equivalent in shape to
  the airlineops original — five-branch classification (same commit, ancestor
  missing, ancestor of HEAD, not ancestor, plus commits-ahead count
  None-coercion) with deterministic message formatting
- **Public API (`__all__`):** `DriftStatus`, `DriftResult`,
  `ObpiDriftResult`, `classify_drift`, `detect_drift`, `detect_obpi_drift`
- **Tests:** `tests/test_temporal_drift.py` — 25 unittest cases across 6
  test classes covering pure classifier (5 cases including frozen-model
  enforcement), real-temp-repo git helpers (7 cases including unknown-commit
  paths, no mocks), `detect_drift` orchestrator (6 cases including
  missing-ledger, no-anchor, anchor-at-head, two-commits-behind,
  unresolvable-anchor, latest-wins), `detect_obpi_drift` orchestrator (5
  cases including parent filtering, single-OBPI filter, sort order, prefix
  formatting), and public-surface stability (1 case)
- **Convention compliance:** frozen Pydantic models with
  `ConfigDict(frozen=True, extra="forbid")`; pathlib throughout; UTF-8 by
  default; list-form subprocess via `git_cmd`; cross-platform
  `tempfile.TemporaryDirectory()` context managers in tests (no
  `shutil.rmtree`)
- **Cross-cutting alignment:** mirrors the architecture of
  `gzkit.triangle.detect_drift` (pure detector) and reuses
  `gzkit.utils.git_cmd` (centralized subprocess), so the new module fits
  the existing module-shape conventions exactly
- **No CLI surface change:** the module is library-only; CLI surfacing is a
  follow-on OBPI and Gate 4 BDD is `N/A` accordingly

### Key Proof


```bash
uv run -m unittest tests.test_temporal_drift -v 2>&1 | tail -3
# Expected:
#   Ran 25 tests in <under 5s>
#
#   OK
```

```bash
python -c "from gzkit.temporal_drift import classify_drift, detect_drift, detect_obpi_drift; \
  r = classify_drift('ADR-0.25.0', 'a'*40, 'a'*40, True, 0); \
  print(r.status, r.commits_ahead, r.message)"
# Expected:
#   none 0 ADR-0.25.0: validated at current HEAD (aaaaaaa)
```

```bash
rg -n 'Decision: Absorb' \
  docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md
# Expected: one match — "## Decision: Absorb"
```

## Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-12
- Attestation: Accepted. Absorb decision for airlineops opsdev/lib/drift_detection.py — gzkit had been writing anchor commits into receipt events for months without any reader; the absorbed temporal_drift module fills that gap with a pure classify_drift plus thin orchestrators that share git_cmd and read .gzkit/ledger.jsonl. 25 tests pass; library-only; CLI surfacing deferred to a follow-on OBPI.
