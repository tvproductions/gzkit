---
id: OBPI-0.0.8-08-operator-docs
parent: ADR-0.0.8-feature-toggle-system
item: 8
lane: Heavy
status: in_progress
---

# OBPI-0.0.8-08: Operator Documentation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #11 — "Operator docs (runbook, manpage, system docs)"

**Status:** Completed

## Objective

Deliver operator-facing documentation for the feature flag system: a runbook
section in `docs/user/runbook.md`, a command manpage for `gz flags` and
`gz flag explain`, and a system documentation page explaining the flag
lifecycle, categories, and configuration.

Also document the `config.gates` → `flags` migration for operators who may
have existing `.gzkit.json` configuration.

## Lane

**Heavy** — Operator-facing documentation is a Gate 3 deliverable. The
runbook and manpages are external contracts per the Gate 5 Runbook-Code
Covenant.

## Dependencies

- **Upstream:** All prior OBPIs (01-07). Docs describe the implemented system.
- **Downstream:** None. This is the final OBPI.
- **Parallel:** None — must follow all implementation OBPIs.

## Allowed Paths

- `docs/user/runbook.md` — Add feature flags section
- `docs/user/commands/flags.md` — New command manpage
- `docs/user/commands/flag-explain.md` — New command manpage
- `docs/user/commands/index.md` — Add flags commands to index
- `docs/governance/feature-flags.md` — System documentation (flag lifecycle, categories, configuration)

## Denied Paths

- `src/gzkit/` — No code changes in docs OBPI
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Runbook MUST include a "Feature Flags" section with: how to list flags, how to check stale flags, how to override a flag via `.gzkit.json`, how to override via env var.
1. REQUIREMENT: Command manpage for `gz flags` MUST include: description, usage, options (--stale, --json, --help), examples, exit codes.
1. REQUIREMENT: Command manpage for `gz flag explain` MUST include: description, usage, arguments, examples, exit codes.
1. REQUIREMENT: System docs MUST explain: flag categories (release, ops, migration, development), lifecycle rules (remove_by, review_by), precedence chain, ON/OFF convention, where toggle points are allowed/forbidden.
1. REQUIREMENT: Migration note MUST explain the `config.gates` → `flags` transition for operators with existing configs.
1. REQUIREMENT: `mkdocs build --strict` MUST pass with new docs.
1. NEVER: Leave placeholder output examples — all examples must show real command output.
1. ALWAYS: Keep lines <=80 chars in manpage examples.

> STOP-on-BLOCKERS: OBPIs 01-07 must be complete. Docs describe the implemented, tested system.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item #11 referenced

### Gate 2: TDD

- [x] N/A — documentation OBPI; no code changes

### Code Quality

- [x] Docs lint: docs build cleanly

### Gate 3: Docs (Heavy)

- [x] `mkdocs build --strict` passes
- [x] Runbook feature flags section present
- [x] Command manpages present for `gz flags` and `gz flag explain`
- [x] System docs page present
- [x] Migration note present

### Gate 5: Human (Heavy)

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.0.8-08-01: Given `mkdocs build --strict`, when run, then exits 0 with no warnings about missing pages.
- [x] REQ-0.0.8-08-02: Given `docs/user/runbook.md`, when searched for "Feature Flags", then a section exists with list/stale/override instructions.
- [x] REQ-0.0.8-08-03: Given `docs/user/commands/flags.md`, when read, then contains description, usage, options, examples, exit codes per CLI Doctrine.
- [x] REQ-0.0.8-08-04: Given `docs/user/commands/flag-explain.md`, when read, then contains description, usage, arguments, examples, exit codes.
- [x] REQ-0.0.8-08-05: Given `docs/governance/feature-flags.md`, when read, then explains categories, lifecycle rules, precedence, convention, and forbidden locations.
- [x] REQ-0.0.8-08-06: Given a grep for "config.gates" in docs, when found, then it appears only in the migration note context.

## Verification Commands

```bash
# Docs build
uv run mkdocs build --strict
# Expected: exit 0, no warnings

# Runbook section exists
grep -n "Feature Flags" docs/user/runbook.md
# Expected: at least one match

# Command manpages exist
test -f docs/user/commands/flags.md && echo "flags.md OK"
test -f docs/user/commands/flag-explain.md && echo "flag-explain.md OK"

# System docs exist
test -f docs/governance/feature-flags.md && echo "feature-flags.md OK"

# Docs validation
uv run gz validate --documents
```

## Evidence

### Implementation Summary

- Files created: docs/user/commands/flags.md, docs/user/commands/flag-explain.md, docs/governance/feature-flags.md
- Files modified: docs/user/runbook.md, docs/user/commands/index.md, mkdocs.yml
- Validation commands run: gz lint, gz typecheck, gz test (2163 pass), mkdocs build --strict, gz validate --documents
- Date completed: 2026-03-30

### Key Proof

```bash
uv run mkdocs build --strict
# exit 0 — all three new pages build without errors

grep -n "Feature Flags" docs/user/runbook.md
# 473:## Feature Flags
```

## Human Attestation

- **Attestor:** Jeff
- **Attestation:** attest completed
- **Date:** 2026-03-30

---

**Brief Status:** Completed
**Date Completed:** 2026-03-30
