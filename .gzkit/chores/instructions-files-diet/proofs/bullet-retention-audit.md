# Bullet-Retention Audit — instructions-files-diet — 2026-08-02

**Acceptance criterion 8:** every Mechanical / Promotable scorecard entry
resolves to a bullet still present in the per-turn contract.

## Method

Retention is **structurally guaranteed** for this pass, not merely sampled.
The lift script replaced only contiguous lines matching `^> ` (the
`> **Rule version:**` block quote) plus the `<!-- rule-version: X.Y.Z -->`
marker line. No bullet, heading, table row, code fence, or prose line was in
the replaced range in any of the nine files.

Mechanical proof:

```bash
git diff -- .gzkit/rules/ | grep '^-' | grep -v '^---' \
  | grep -vE '^-> ' | grep -vE '^-<!-- rule-version'
```

Result: 4 matches, all bare blank lines (end-of-file normalization). Zero
content lines removed.

## Scope

Nine canonical rules had their multi-version chains lifted; each retains its
current-version rationale plus a pointer to
`docs/governance/rule-version-history.md`:

| Rule | Chain lines before | After | Version |
|---|---:|---:|---|
| `governance-core.md` | 29 | 1 | 0.8.0 -> 0.8.1 |
| `cli.md` | 19 | 1 | 0.3.0 -> 0.3.1 |
| `gate5-runbook-code-covenant.md` | 11 | 1 | 0.2.0 -> 0.2.1 |
| `chores.md` | 9 | 1 | 0.3.0 -> 0.3.1 |
| `adr-audit.md` | 9 | 1 | 0.2.0 -> 0.2.1 |
| `gh-cli.md` | 9 | 1 | 0.3.0 -> 0.3.1 |
| `task-discovery.md` | 7 | 1 | 0.5.0 -> 0.5.1 |
| `pythonic.md` | 7 | 1 | 0.2.0 -> 0.2.1 |
| `hexagonal-architecture.md` | 6 | 1 | 0.2.0 -> 0.2.1 |

## Validator corroboration

`uv run gz validate --advisory-scorecard` exit 0; `uv run gz check` all
checks passed, including Surface fidelity and the bullet-retention audit
wired into it.

## Note on the shape

This pass trimmed toward the contract rather than away from it.
`.gzkit/rules/skill-surface-sync.md` specifies the marker as a block quote
"with a one-sentence rationale"; the accumulated chains (6-29 lines) exceeded
that. Post-trim, every one of the nine conforms.
