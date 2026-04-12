# Plan: OBPI-0.25.0-25 — Documentation Validation Pattern

## Context

OBPI-0.25.0-25 evaluates `airlineops/src/opsdev/lib/docs.py` (218 lines) against gzkit's `src/gzkit/doc_coverage/` package (~800 lines, 4 modules) and records an Absorb/Confirm/Exclude decision. This is part of ADR-0.25.0 (Core Infrastructure Pattern Absorption) — Phase 2 opsdev evaluation.

**Preliminary finding:** The two implementations address fundamentally different concerns. airlineops validates documentation structure (file existence, link resolution, orphan pages), while gzkit validates CLI-to-documentation coverage (AST-based command discovery, 5-surface checks, manifest-driven gap reporting). The expected decision is **Confirm** — gzkit's surface is already far more sophisticated in every comparable dimension.

## Plan

### Task 1: Complete the comparison analysis

Document the side-by-side comparison in the OBPI brief using the established ADR-0.25.0 pattern. The comparison will cover these dimensions:

| Dimension | airlineops docs.py | gzkit doc_coverage/ |
|---|---|---|
| Architecture | Single 218-line module, procedural | 4-module package (scanner, models, manifest, runner), Pydantic models |
| Documentation validation | Index existence check only | AST-driven 5-surface coverage per CLI command |
| Link validation | Regex-based markdown link parser, graph-based orphan detection (2-click reachability) | N/A — handled externally by `mkdocs build --strict` |
| MkDocs integration | Subprocess wrapper for strict build | External invocation via `gz validate --documents` |
| Manifest/config | None | Full manifest-driven obligation system with per-command exemptions |
| Gap reporting | None | Structured gap report with JSON output, undeclared command detection |
| Orphan detection | Page-level: markdown pages unreachable from index | Command-level: manpage files with no matching CLI command |
| Error handling | `sys.exit(1)` with stderr message | Pydantic validation, structured error models |
| Cross-platform | UTF-8 encoding on read; hardcoded `_REPO_ROOT` via `__file__` | pathlib throughout, `get_project_root()` helper |
| Test coverage | Unknown (not evaluated here) | 87 test cases across 3 files |

**Key finding:** The link validation in airlineops (lines 100-218) is the only capability gzkit doesn't have — but `mkdocs build --strict` already catches broken links and unreachable pages during documentation builds, making it redundant.

**File to modify:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-25-docs-validation-pattern.md`

### Task 2: Record the decision — Confirm

Add the DECISION section to the brief with rationale citing:
- gzkit's 4x larger, more architecturally mature surface
- Different problem domains (structure validation vs. CLI coverage validation)
- Link validation redundancy with `mkdocs build --strict`
- airlineops's temporary/suspended policy (its own TODO says "restore strict docs checks post-remodel")

### Task 3: Record Gate 4 BDD N/A rationale

Confirm decisions produce no code changes and no operator-visible behavior changes. Record N/A with rationale in the brief.

### Task 4: Write the closing argument

Synthesize the comparison into the brief's Closing Argument section following the established ADR-0.25.0 pattern.

### Task 5: Update acceptance criteria checkboxes

Mark all acceptance criteria as met:
- REQ-0.25.0-25-01: Decision recorded (Confirm)
- REQ-0.25.0-25-02: Rationale cites concrete capability differences
- REQ-0.25.0-25-03: N/A (not Absorb)
- REQ-0.25.0-25-04: Explains why no absorption warranted (Confirm)
- REQ-0.25.0-25-05: Gate 4 N/A recorded with rationale

### Task 6: Present OBPI Acceptance Ceremony

Present evidence for human attestation (Stage 4, Normal mode Heavy lane).

## Verification

```bash
# Brief records one final decision
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-25-docs-validation-pattern.md

# Existing tests remain green
uv run gz test

# Lint passes
uv run gz lint

# Typecheck passes
uv run gz typecheck

# Docs build (Heavy lane)
uv run mkdocs build --strict
```

## Critical Files

- **Brief:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-25-docs-validation-pattern.md`
- **airlineops source:** `../airlineops/src/opsdev/lib/docs.py`
- **gzkit target:** `src/gzkit/doc_coverage/` (scanner.py, models.py, manifest.py, runner.py)

## Notes

- No code changes expected — this is a Confirm decision
- No new tests needed — existing 87 test cases cover doc_coverage thoroughly
- Heavy lane requires human attestation at Stage 4
