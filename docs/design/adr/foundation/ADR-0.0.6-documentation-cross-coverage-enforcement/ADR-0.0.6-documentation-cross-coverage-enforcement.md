---
id: ADR-0.0.6-documentation-cross-coverage-enforcement
status: Pending
semver: 0.0.6
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-23
---

# ADR-0.0.6: Documentation Cross-Coverage Enforcement

## Status

Pending

## Date

2026-03-23 (authored), 2026-03-26 (revised)

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Problem Statement

gzkit's documentation obligation is enforced piecemeal. `gz cli audit` checks
manpage existence and index entries. The `COMMAND_DOCS` dict in `common.py` maps
commands to doc paths. Four chores (`validate-manpages`, `sync-manpage-docstrings`,
`test-manpage-examples`, `skill-command-doc-parity`) each cover a narrow surface.
But no single tool enforces the *full* documentation contract across all required
surfaces for every command.

**Before:** On 2026-03-23, four QC capabilities (#29-#32) were merged without
runbook references or manpage coverage. The gap was caught by manual audit (#33),
not by tooling. Commands like `gz lint`, `gz format`, `gz test`, `gz typecheck`,
and `gz check` have no `/docs/user/commands/*.md` files at all.

**After:** An AST-driven scanner discovers every CLI command from argparse
registrations and verifies six documentation surfaces per command. A manifest
declares which surfaces are required. A chore produces an actionable gap report
that fails closed on missing coverage.

**So what:** Without cross-coverage enforcement, every new command is a
documentation debt time bomb. The Gate 5 Runbook-Code Covenant
(`.claude/rules/gate5-runbook-code-covenant.md`) requires docs to track behavior
changes in the same patch set, but nothing enforces this at the command level.

---

## Decisions

### Decision 1: AST-driven discovery over static lists

Scan `cli/main.py` for `add_parser()` calls to discover commands automatically,
rather than maintaining a manual command list.

**Why:** The `COMMAND_DOCS` dict (37 entries in `common.py:36-75`) already drifts
from reality. Manual lists are always stale. AST scanning is authoritative.

**Alternatives considered:**
- *Extend `COMMAND_DOCS` with more fields* -- rejected: same drift problem, just
  wider. A dict that must be manually updated is not enforcement.
- *Introspect argparse at runtime* -- viable alternative, but AST scanning
  produces results without executing code, making it safer for CI and chore use.

**Precedent:** OBPI-0.0.3-09 established AST-based policy tests for the codebase.

### Decision 2: Declarative manifest over implicit rules

Create `config/doc-coverage.json` declaring per-command documentation obligations
explicitly.

**Why:** Not every command needs every surface. `gz init` needs a manpage and
runbook reference. Internal plumbing commands may only need a docstring. The
manifest makes these choices auditable and reviewable rather than buried in
scanner logic.

**Alternatives considered:**
- *Convention-only (all commands get all surfaces)* -- rejected: creates false
  positives for internal commands. Operators would suppress findings, defeating
  the purpose.
- *Inline annotations in CLI code* -- rejected: mixes documentation policy with
  implementation. Policy belongs in config.

### Decision 3: Three-layer architecture (Scanner + Manifest + Chore)

Separate the scanner (discovers what exists), the manifest (declares what should
exist), and the chore runner (enforces the contract).

**Why:** Each layer is independently testable and replaceable. The scanner can be
used standalone for ad-hoc audits. The manifest can be reviewed without reading
code. The chore integrates into the existing `gz chores` maintenance workflow.

```
Layer A: AST Scanner (discovers what exists, verifies surfaces)
  +-- Scans cli/main.py for add_parser() calls
  +-- Verifies: manpage, index entry, runbook ref, docstring, mapping
  +-- Detects: orphaned docs referencing removed commands

Layer B: Documentation Manifest (declares what should exist)
  +-- config/doc-coverage.json
  +-- Maps command -> required surfaces
  +-- Governance-relevant flag per command

Layer A+B: Chore Runner (enforcement surface)
  +-- gz chores run doc-coverage
  +-- Produces pass/fail report
  +-- Actionable gap list
```

### Decision 4: Bidirectional coverage detection

Check both directions: undocumented commands AND stale documentation for removed
commands.

**Why:** `gz cli audit` only checks forward (command -> doc). It cannot detect
orphaned manpages that reference commands that no longer exist. Bidirectional
detection prevents documentation rot.

---

## Required Surfaces Per Command

| Surface | Verification method | Current tooling |
|---------|-------------------|-----------------|
| Manpage | `docs/user/commands/<slug>.md` exists | `gz cli audit` (exists) |
| Command index | Listed in `docs/user/commands/index.md` | `gz cli audit` (exists) |
| Operator runbook | Referenced in `docs/user/runbook.md` | None (gap) |
| Governance runbook | Referenced in `docs/governance/governance_runbook.md` | None (gap) |
| Docstring | CLI handler function has non-empty docstring | None (gap) |
| Manpage mapping | Registered in `COMMAND_DOCS` dict | Exists but not enforced |

---

## Feature Checklist

1. **AST Scanner** -- Discover CLI commands and verify documentation surfaces.
   Extends `gz cli audit` output with a new "Cross-Coverage" section listing
   per-command surface status (manpage, index, runbook, docstring, mapping) as
   a table with pass/fail per cell.
2. **Documentation Manifest** -- Declare per-command documentation obligations
3. **Chore Registration and Enforcement** -- Register as chore, produce actionable
   gap report. `--json` output conforms to a schema in `data/schemas/` for
   consumer stability.

---

## Non-Goals

- **Generating documentation automatically** -- this ADR detects gaps, it does
  not auto-generate manpages or runbook entries. Generation is a separate concern.
- **Skill documentation coverage** -- the `skill-command-doc-parity` chore
  handles skill documentation. This ADR focuses on CLI commands.
- **Content quality assessment** -- this ADR checks existence and structural
  completeness, not whether documentation is well-written or accurate.
- **Replacing `gz cli audit`** -- the scanner extends `gz cli audit` coverage,
  it does not replace it. Existing checks remain.

---

## OBPI Decomposition

| # | OBPI | Lane | Dependencies |
|---|------|------|-------------|
| 01 | AST Scanner | Heavy | None |
| 02 | Documentation Manifest | Lite | None |
| 03 | Chore Registration and Enforcement | Heavy | 01, 02 |

**Critical path:** 2 stages. OBPIs 01 and 02 run in parallel. OBPI 03
integrates both and registers the chore.

**Lane rationale:** OBPI-01 is Heavy because it adds a new verification surface
to `gz cli audit` (changes operator-visible command output). OBPI-02 is Lite
(config file only). OBPI-03 is Heavy because it adds a new chore to the `gz
chores` interface.

---

## Dependencies

None. All required infrastructure exists:

- `gz cli audit` (`src/gzkit/commands/cli_audit.py`) -- extend, don't replace
- `COMMAND_DOCS` dict (`src/gzkit/commands/common.py:36-75`) -- existing mapping
- `gz chores` framework (`config/gzkit.chores.json`) -- registration target
- `docs/user/runbook.md` and `docs/governance/governance_runbook.md` -- audit targets

---

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 3-4
- Baseline Selected: 3
- Final Target OBPI Count: 3

---

## Q&A Transcript

Discovered 2026-03-23 when four QC capabilities (#29-#32) were merged without
runbook or manpage coverage. Manual audit caught the gap (#33). Prior art:
`gz cli audit` (manpage/index parity), `interrogate` (docstring coverage),
OBPI-0.0.3-09 (AST policy tests).

---

## Consequences

### Positive

Automated detection of documentation gaps at the point of change, not after
manual audit. Operators get a single command (`gz chores run doc-coverage`) that
reports all documentation obligations.

### Negative

New maintenance surface (manifest). Mitigated by the scanner catching drift
automatically -- if a command is added without a manifest entry, the scanner
reports it as undeclared.

---

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.6 | Completed | Jeff | 2026-03-26 | completed |
