---
id: OBPI-0.2.0-03-docs-updates
parent: ADR-0.2.0
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.2.0-03-docs-updates: Update docs for gates and dry-run

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md`
- **Checklist Item:** #3 — "Update user docs for new commands and `--dry-run` usage."

**Status:** Draft

## Objective

Document `gz implement`, `gz gates`, and `--dry-run` options in user-facing docs and command index.

## Lane

**Heavy** — external CLI contract documentation

## Allowed Paths

- `docs/user/commands/` — new/updated command pages
- `docs/user/commands/index.md` — command list
- `docs/user/concepts/gates.md` — gate verification guidance

## Denied Paths

- `docs/design/**` — governance changes out of scope for this OBPI
- `src/**` — code changes handled in other OBPIs

## Requirements (FAIL-CLOSED)

1. Add docs for `gz implement` and `gz gates` with examples.
2. Update existing command docs to include `--dry-run` options where applicable.
3. Update command index to include the new commands.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR — understand scope and checklist

**Context:**

- [ ] Existing docs in `docs/user/commands/`
- [ ] `docs/user/concepts/gates.md`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests pass: `uv run -m unittest discover tests`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uvx mkdocs build --strict
```

## Acceptance Criteria

- [ ] `docs/user/commands/implement.md` added
- [ ] `docs/user/commands/gates.md` added
- [ ] Command index lists new commands
- [ ] Updated commands document `--dry-run`

## Evidence

### Docs Build

```text
# Paste mkdocs output here
```

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
