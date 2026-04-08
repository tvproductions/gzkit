<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.15 — GHI-Driven Patch Release Ceremony

## Tidy First Plan

Behavior-preserving tidyings required before any behavior change:

1. Audit `sync_project_version` in `src/gzkit/commands/closeout.py` to understand
   the shared version-sync code path that `gz patch release` will reuse
1. Catalog existing release-related artifacts (RELEASE_NOTES.md format, GitHub
   release note conventions, tag naming) to establish the contract
1. Review `gh issue list` label taxonomy to confirm whether a `runtime` label
   exists or needs creation

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If `sync_project_version` is tightly coupled to ADR closeout logic in ways
  that prevent reuse, refactor it into a shared utility first.

**Date Added:** 2026-03-31
**Date Closed:**
**Status:** Draft
**SemVer:** 0.0.15
**Area:** Governance Foundation — Patch Release Lifecycle
**Lane:** Heavy

## Agent Context Frame — MANDATORY

**Role:** CLI infrastructure developer creating the patch-level release ceremony
that complements the existing ADR-driven minor release path (`gz closeout`).

**Purpose:** When this ADR is complete, gzkit has a deterministic, auditable
ceremony for patch releases driven by GHI completion. The operator runs
`gz patch release`, the agent proposes qualifying GHIs, cross-validates intent
(label) against evidence (diff), drafts narrative release notes, and the
operator approves. Version sync, manifests, tags, and GitHub releases follow
the same mechanical patterns as `gz closeout`.

**Goals:**

- `gz patch release` discovers GHIs closed since last tag and proposes a
  release with cross-validated qualification (label + diff)
- Dual-format manifest (markdown + JSONL) provides an audit trail for every
  patch release
- Version sync reuses `sync_project_version` from `gz closeout` — single
  code path for all version bumps
- Agent drafts narrative release notes; operator approves before publish

**Critical Constraint:** Implementations MUST NOT create a second version-sync
code path. `sync_project_version` is the single source of truth for bumping
pyproject.toml, `__init__.py`, and README badge. `gz patch release` calls it,
never reimplements it.

**Anti-Pattern Warning:** A failed implementation adds the CLI command but
leaves version sync as a manual edit to pyproject.toml — exactly the drift
pattern (0.24.1 in pyproject.toml, 0.24.0 in `__init__.py`) that motivated
this ADR. If an operator can bump the version without the command, the command
has failed its purpose.

**Integration Points:**

- `src/gzkit/commands/closeout.py` — `sync_project_version` to reuse
- `src/gzkit/cli/parser_governance.py` — CLI parser for new subcommand
- `src/gzkit/ledger.py` — ledger append for manifest JSONL entries
- `src/gzkit/ledger_events.py` — event factory for patch release events
- `RELEASE_NOTES.md` — release notes append target
- `.gzkit/ledger.jsonl` — machine-readable manifest entries
- `docs/releases/` — markdown manifest location (new directory)

---

## Feature Checklist — Appraisal of Completeness

### Checklist

- [ ] `gz patch release` CLI command scaffold with `--dry-run` and `--json`
- [ ] GHI discovery: find issues closed since last tag via `gh issue list`
- [ ] Cross-validation engine: runtime label AND `src/gzkit/` diff for each GHI
- [ ] Version sync integration: call `sync_project_version` for patch increment
- [ ] Dual-format manifest: markdown (`docs/releases/PATCH-vX.Y.Z.md`) and
      JSONL ledger entry with GHI list, cross-validation results, operator approval
- [ ] Ceremony skill (`gz-patch-release`): agent drafts narrative, operator
      approves, handles RELEASE_NOTES + git-sync + GitHub release

## Non-Goals

- **Major/minor version bumps** — those are `gz closeout`, tied to ADR completion.
  This ADR covers patch (Z) increments only.
- **Automatic release without operator approval** — the agent proposes, the
  operator decides. No unattended publishes.
- **Backport or hotfix workflows** — patch releases apply to the current HEAD
  only. Cherry-pick backports to maintenance branches are out of scope.
- **GHI triage or labeling policy** — this ADR consumes the `runtime` label
  but does not define the triage workflow that applies it.

## Alternatives Considered

### 1. Fully automatic release on GHI close

Rejected. The agent cannot distinguish between a single critical fix that
warrants an immediate patch and a batch of minor fixes that should accumulate.
Operator judgment is required for release timing.

### 2. Label-only qualification (no diff validation)

Rejected. Labels are intent signals applied by humans at triage time.
They can be wrong — a GHI labeled `runtime` may only change docs, or a
GHI labeled `chore` may touch `src/gzkit/`. Diff evidence catches both
false positives and false negatives. The Q&A design dialogue concluded
that label and diff cross-validate each other; disagreement is a warning.

### 3. Diff-only qualification (no label requirement)

Rejected. Diff evidence is proof but not intent. A commit that touches
`src/gzkit/__init__.py` (import reorder) shouldn't qualify as a runtime
change. The label carries the human's intent about whether the change
matters to operators.

### 4. Separate version-sync implementation

Rejected. `sync_project_version` already exists in `closeout.py` and
handles pyproject.toml, `__init__.py`, and README badge atomically.
A second code path is the exact drift pattern this ADR exists to prevent.

## Intent

Establish a deterministic patch release ceremony driven by GHI completion,
closing the governance gap where minor releases have a full ceremony
(`gz closeout`) but patch releases have no formal path — leading to manual
version edits, version drift, and missing release artifacts.

**Before (quantified):** Of the last 5 patch-level version changes in gzkit,
at least 2 were manual edits to pyproject.toml without corresponding updates
to `__init__.py` or git tags (0.24.0 -> 0.24.1 being the most recent). Zero
patch releases have a RELEASE_NOTES entry or GitHub release artifact.

## Decision

- `gz patch release` is the CLI entry point. It discovers qualifying GHIs,
  cross-validates them, bumps the patch version, and writes the release manifest.
- A GHI qualifies for a patch release when it has both a `runtime` label AND
  commits that modified files under `src/gzkit/`. Disagreement between label
  and diff is surfaced as a warning, not silently resolved.
- Version sync uses the existing `sync_project_version` function — no second
  code path. Patch increments the `z` in `X.Y.Z`.
- The release manifest is dual-format: a human-readable markdown file in
  `docs/releases/PATCH-vX.Y.Z.md` and a structured JSONL entry in the
  governance ledger.
- The agent drafts narrative release notes from GHI titles and descriptions.
  The operator reviews, edits, and approves before the release is published.
- RELEASE_NOTES.md, git-sync, and GitHub release creation follow the same
  patterns as `gz closeout` ceremony Steps 9-10.
- When no GHIs qualify (no closed issues since last tag, or none pass
  cross-validation), `gz patch release` exits 0 with a message explaining
  why no release was produced. This is not an error — it is the expected
  outcome when no runtime changes have landed.

## Interfaces

- **CLI (external contract):** `uv run gz patch release [--dry-run] [--json]`
  - `--dry-run`: show qualifying GHIs and proposed version, don't execute
  - `--json`: machine-readable output to stdout
- **Config keys consumed (read-only):** none — GHI discovery uses `gh` CLI
- **Exchange/Schemas:** patch release manifest schema (new, in
  `data/schemas/patch_release_manifest.schema.json`)

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.15-01 | CLI command scaffold with `--dry-run` and `--json` | Heavy | Pending |
| 2 | OBPI-0.0.15-02 | GHI discovery and cross-validation engine | Lite | Pending |
| 3 | OBPI-0.0.15-03 | Version sync integration (reuse `sync_project_version`) | Lite | Pending |
| 4 | OBPI-0.0.15-04 | Dual-format release manifest (markdown + JSONL) | Lite | Pending |
| 5 | OBPI-0.0.15-05 | Ceremony skill: narrative drafting, RELEASE_NOTES, GitHub release | Heavy | Pending |
| 6 | OBPI-0.0.15-06 | Dogfood: fix 0.24.1 version drift as first invocation | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.0.15-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-5 required (ADR + TDD + Docs + BDD + Human)

---

## Rationale

gzkit has a mature ceremony for ADR-driven minor releases (`gz closeout`), but
no formal path for patch releases driven by bug fixes and small improvements
tracked as GHIs. This gap produces predictable failure modes:

1. **Manual version edits** — operators edit pyproject.toml directly, creating
   drift between pyproject.toml, `__init__.py`, and git tags
2. **Missing release artifacts** — no RELEASE_NOTES entry, no GitHub release,
   no audit trail for what went into the patch
3. **No qualification criteria** — no distinction between GHIs that warrant a
   release (runtime behavior changes) and those that don't (docs, governance)

The cross-validation pattern (label as intent signal, diff as proof) provides
a principled qualification mechanism that catches both mislabeled GHIs and
unlabeled runtime changes.

## Consequences

- `gz patch release` becomes the single path for patch-level version bumps
- `docs/releases/` directory is created as the manifest archive
- `runtime` label is added to the GitHub label taxonomy
- `sync_project_version` may need minor refactoring to accept arbitrary
  version strings (currently may assume ADR-derived versions)
- The closeout ceremony skill and patch release skill share the same
  post-attestation patterns (RELEASE_NOTES, git-sync, GitHub release)

## Evidence (Five Gates)

- **ADR:** this document
- **TDD (required):** `tests/adr/test_patch_release.py`
  - Must include a contract test that validates the GHI qualification path
    pattern (`src/gzkit/`) matches the actual source directory structure.
    If the project restructures source directories, the qualification regex
    must fail loudly rather than silently stop qualifying GHIs.
- **Docs (Heavy):** `docs/user/commands/patch-release.md`, `docs/user/manpages/patch-release.md`
- **BDD (Heavy):** `features/patch_release.feature`
- **Human (Heavy):** Gate 5 attestation at closeout

---

## OBPI Acceptance Note (Human Acknowledgment)

Each checklist item maps to one OBPI brief. Record a one-line acceptance note
in the brief once gates are green.

`uv run gz patch release --dry-run`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.0.15`
- **Related issues:** #65 (closeout ceremony improvements)

### Source & Contracts

- CLI: `src/gzkit/commands/patch_release.py`
- Shared: `src/gzkit/commands/closeout.py` (`sync_project_version`)
- Parser: `src/gzkit/cli/parser_governance.py`

### Tests

- Unit: `tests/adr/test_patch_release.py`
- BDD: `features/patch_release.feature`

### Docs

- Command docs: `docs/user/commands/patch-release.md`
- Manpage: `docs/user/manpages/patch-release.md`
- Manifest archive: `docs/releases/PATCH-vX.Y.Z.md`
- Skill: `.gzkit/skills/gz-patch-release/SKILL.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD
- Notes: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|---------------------|----------|-------|
| pyproject.toml | M | Version set to 0.0.15 | Diff link | |
| src/gzkit/__init__.py | M | `__version__` matches | Diff link | |
| RELEASE_NOTES.md | M | 0.0.15 entry recorded | Commit link | Foundation — no GitHub release |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. ...

1. ...

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.15 | Completed | Jeffry | 2026-04-08 | completed |
