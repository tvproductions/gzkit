---
id: OBPI-0.25.0-14-os-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 14
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-14: OS Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-14 — "Evaluate and absorb common/os.py (241 lines) — cross-platform file operations"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/common/os.py` (241 lines) and determine:
Absorb (airlineops is better) or Exclude (domain-specific). The airlineops
module provides cross-platform file operations, path normalization, and OS
abstraction. gzkit currently has no dedicated OS abstraction module, only a
cross-platform development policy rule. The comparison must determine whether
airlineops's battle-tested OS utilities should become a gzkit module that
enforces the cross-platform policy in code.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/common/os.py` (241 lines)
- **gzkit equivalent:** Cross-platform rule only (`.claude/rules/cross-platform.md`)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit code equivalent means either Absorb or Exclude — there is no Confirm path
- Cross-platform OS utilities are definitively generic infrastructure

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Replacing Python's pathlib — the module should augment it with project-specific utilities

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why the module is domain-specific

## DECISION

**Decision: Exclude** — the module is deployment-environment-specific. No upstream absorption warranted.

**Rationale:** airlineops's `common/os.py` (241 lines) provides UNC/SMB network share handling: macOS `/Volumes/` mount enumeration (`iter_mounts()`), UNC path parsing (`parse_unc_share()`, `UncShare` NamedTuple), UNC-to-mount resolution (`resolve_unc_mount()`, `resolve_unc_path()`, `normalize_unc_path()`), and macOS SMB guest mount refresh via subprocess (`refresh_macos_guest_smb_mount()` calling `diskutil`, `umount`, `mount_smbfs`). Every significant function serves a deployment scenario where airline servers are accessed via SMB shares on macOS workstations. gzkit is a governance toolkit that works with local files — it has no UNC path use case, no SMB mount use case, and no network share resolution need. The only generic primitives (`is_macos()` — `sys.platform == "darwin"`, `is_windows()` — `sys.platform.startswith("win")`) are trivial one-liners (~2 lines each) that don't warrant a standalone module. gzkit's cross-platform needs (path separators, encoding, temp files, subprocess) are handled by `pathlib.Path`, UTF-8 encoding policy, and the cross-platform development rule.

## COMPARISON ANALYSIS

| Dimension | airlineops (241 lines, 1 file) | gzkit (no equivalent) | Assessment |
|-----------|-------------------------------|----------------------|------------|
| Purpose | UNC/SMB network share handling for macOS workstations | No network share use case; local file operations only | Domain-specific |
| Mount enumeration | `iter_mounts()` — yields `/Volumes/` subdirectories on macOS | N/A | macOS-specific, airline deployment assumption |
| UNC parsing | `parse_unc_share()`, `UncShare` NamedTuple — parses `//server/share[/subdir]` and `\\server\\share\\subdir` into (server, share, remainder) | N/A | Windows network share concept; gzkit has no UNC paths |
| UNC resolution | `resolve_unc_mount()`, `resolve_unc_path()`, `normalize_unc_path()` — resolves UNC paths to mounted local paths on macOS | N/A | Deployment-specific: maps Windows UNC to macOS mount |
| SMB refresh | `refresh_macos_guest_smb_mount()` — subprocess calls to `diskutil unmount`, `umount`, `mount_smbfs -N` | N/A | macOS-only, shell subprocess, guest-mode authentication |
| Platform detection | `is_macos()` (~1 line), `is_windows()` (~1 line) | No explicit platform checks needed; `pathlib.Path` handles cross-platform paths | Generic but trivial — not worth a module |
| Cross-platform policy | N/A (module provides OS-level utilities, not a coding policy) | `.claude/rules/cross-platform.md` + `pathlib.Path` usage throughout + UTF-8 encoding + `_ensure_utf8_console()` in CLI entrypoint | gzkit has a comprehensive cross-platform policy enforced through rules and stdlib patterns |
| Error handling | No explicit error handling; subprocess calls use `check=False` | N/A | No errors to absorb |

### Subtraction Test

Removing gzkit from airlineops leaves: UNC/SMB share path parsing, macOS mount enumeration, and SMB guest mount refresh for airline server access. This is pure deployment-environment infrastructure — it fails the subtraction test entirely. No construct in this module belongs in a governance toolkit.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, new gzkit module/tests are added or updated — N/A (Exclude decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Exclude` decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the absorbed pattern changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Exclude decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-14-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-14-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Eight-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-14-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-14-04: [doc] Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-14-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/common/os.py
# Expected: airlineops source under review exists

test -f .claude/rules/cross-platform.md
# Expected: current gzkit comparison doctrine exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-14-os-pattern.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-14-os-pattern.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Exclude)
- [x] **Gate 3 (Docs):** Decision rationale completed with comparison table
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Exclude, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for an Exclude decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Exclude decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented evaluation of whether airlineops's `common/os.py` contained reusable patterns for gzkit. After reading the full 241-line module, every significant function serves UNC/SMB network share handling: macOS mount enumeration under `/Volumes/`, UNC path parsing into server/share/remainder triples, UNC-to-mount resolution, UNC path normalization, and macOS SMB guest mount refresh via subprocess calls to `diskutil`/`umount`/`mount_smbfs`. This is deployment-environment infrastructure for accessing airline servers via SMB shares on macOS workstations. gzkit is a governance toolkit working with local files — it has no UNC path use case and no network share requirement. The two generic primitives (`is_macos()`, `is_windows()`) are trivial one-liners that don't justify a module. gzkit's cross-platform needs are fully covered by `pathlib.Path`, UTF-8 encoding policy, and the existing cross-platform development rule.

### Key Proof


- Decision: Exclude
- Comparison: eight-dimension analysis in Comparison Analysis section
- airlineops os.py: 241 lines, single module, UNC/SMB share handling
- gzkit: no equivalent module, no UNC/SMB use case — local file operations only
- Subtraction test: entire module is deployment-environment-specific — fails completely
- Generic primitives (`is_macos()`, `is_windows()`): too trivial for a standalone module (~2 lines each)
- gzkit cross-platform coverage: pathlib.Path, UTF-8 encoding, cross-platform rule, `_ensure_utf8_console()` in CLI entrypoint

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-10

## Closing Argument

airlineops's `common/os.py` (241 lines) provides UNC/SMB network share handling: `iter_mounts()` enumerates macOS `/Volumes/` mount points, `parse_unc_share()` and `UncShare` parse Windows UNC paths into server/share/remainder triples, `resolve_unc_mount()`/`resolve_unc_path()`/`normalize_unc_path()` resolve and normalize UNC paths to mounted local paths, and `refresh_macos_guest_smb_mount()` refreshes macOS SMB mounts via subprocess calls to `diskutil`, `umount`, and `mount_smbfs`. Every function beyond two trivial platform detection helpers (`is_macos()`, `is_windows()`) serves a deployment scenario where airline servers are accessed via SMB shares on macOS workstations. gzkit works with local files, has no UNC/SMB use case, and its cross-platform needs are comprehensively addressed by `pathlib.Path`, UTF-8 encoding policy, and the existing cross-platform development rule. The subtraction test is unambiguous: this module is pure deployment-environment infrastructure. **Decision: Exclude.**
