# gz validate

Validate governance artifacts against schema rules.

## Usage

```bash
gz validate [--manifest] [--documents] [--surfaces] [--ledger]
            [--instructions] [--briefs] [--personas]
            [--interviews] [--decomposition]
            [--requirements] [--commit-trailers]
            [--frontmatter [--adr <ID>] [--explain <ADR-ID>]]
```

## Description

Verifies governance artifacts against their schema definitions and enforces
canonical/mirror sync parity for generated control surfaces. When no flag is
supplied, the manifest, documents, surfaces, ledger, instructions, briefs, and
personas scopes all run. The `--interviews`, `--decomposition`,
`--requirements`, and `--commit-trailers` scopes are opt-in and only run when
explicitly requested.

### `--requirements`

Flags OBPI briefs whose `## REQUIREMENTS` sections contain no
`REQ-X.Y.Z-NN-MM` identifiers. Such briefs are invisible to `gz covers` and
break the REQ → test traceability chain. Added under GHI-160 Phase 6 to
prevent the governance-graph rot that surfaced in ADR-0.23.0 and the 18
ADRs using the legacy fail-closed requirements template.

### `--commit-trailers`

Flags HEAD commits that touch `src/` or `tests/` without a `Task:` trailer.
The trailer format is `Task: TASK-X.Y.Z-NN-MM-PP` and provides the
execution-level link from a code change back to the governing REQ. Added
under GHI-160 Phase 6 as an advisory guard against the TASK-registry
bypass pattern observed across GHI-141 through GHI-156.

Non-code commits (docs-only, config-only) and commits with a valid
trailer pass the check. The scope scans HEAD only.

### `--surfaces`

The surfaces scope enforces three contracts:

1. **Existence and shape** — required control surface files exist and their
   YAML frontmatter + required headers validate against the schema.
2. **Frontmatter models** — SKILL.md and `.github/instructions/*` frontmatter
   validate against the canonical Pydantic models.
3. **Canonical sync parity** — every generated surface file (`AGENTS.md`,
   `CLAUDE.md`, `.claude/rules/**`, `.claude/hooks/**`, `.claude/skills/**`,
   `.agents/skills/**`, `.github/skills/**`, `.github/instructions/**`,
   `.github/copilot-instructions.md`, `.github/discovery-index.json`,
   `.claude/settings.json`, `.copilotignore`, and nested `AGENTS.md` under
   `src/`, `tests/`) must match what `sync_all()` would write for the current
   canonical state. Hand edits to generated surfaces surface as drift findings
   pointing at `uv run gz agent sync control-surfaces` for repair.

Sync parity is checked via a snapshot-sync-compare-restore protocol: the
validator reads each tracked surface, runs `sync_all()` in place, compares the
regenerated content to the snapshot, and restores the pre-check state. From
the caller's perspective the check is non-mutating. The operational
`- **Updated**: YYYY-MM-DD` line in `AGENTS.md` is normalized before
comparison so stale sync timestamps never trigger false drift.

### `--frontmatter`

Validates the four governed frontmatter fields (`id`, `parent`, `lane`,
`status`) on every ADR and OBPI file against the ledger's artifact graph.
Keys lookups on filesystem path only — never on frontmatter `id:` (that
pattern reproduces GHI #166). The check uses the same canonical ledger
semantics API that `gz adr report` uses, so drift reported by this scope
is the same drift the operator sees in the report surface.

Ungoverned frontmatter keys (`tags:`, `related:`, any key outside the
four governed fields) are ignored. The validator never mutates files —
reconciliation belongs to `gz chore run frontmatter-ledger-coherence`
(ADR-0.0.16 / OBPI-03). Exits 3 on drift per CLI doctrine 4-code map.

#### `--adr <ID>`

Scopes `--frontmatter` validation to one ADR (and its child OBPIs).
Useful for iterating on a single artifact without reprinting repo-wide
drift.

#### `--explain <ADR-ID>`

Prints step-by-step remediation per drifted field for the named ADR.
Every drifted field gets a one-line recovery command naming an executable
`gz` verb (`gz register-adrs`, `gz adr promote`,
`gz chore run frontmatter-ledger-coherence`). Never suggests hand-editing
frontmatter — frontmatter is L3 derived state, not a source of truth.

#### Examples

```bash
# Repo-wide frontmatter coherence check
gz validate --frontmatter

# Machine-readable drift report (emits drift[] array in payload)
gz validate --frontmatter --json

# One ADR at a time
gz validate --frontmatter --adr ADR-0.1.0

# Remediation guidance for a drifted ADR
gz validate --frontmatter --explain ADR-0.1.0
```

## Exit Codes

Follows the CLI doctrine 4-code map:

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All artifacts valid | — |
| 1 | User/config error or non-frontmatter validation error | Fix invocation or address reported errors |
| 2 | System/IO error | Check filesystem and retry |
| 3 | Frontmatter-ledger policy breach (drift) | Run `gz validate --frontmatter --explain <ADR>` then the suggested recovery command |
