# Plan: OBPI-0.0.67-02-wire-orphan-verbs-into-skills

**OBPI:** OBPI-0.0.67-02-wire-orphan-verbs-into-skills
**Brief:** docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-02-wire-orphan-verbs-into-skills.md
**ADR:** ADR-0.0.67-tool-skill-invariant1-enforcement
**Lane:** Heavy

## Context

Wire 10 live orphan verbs into 6 skills (no waivers), remove the 13
multi-word stop-gap waivers from `_NO_SKILL_VERBS` in `cli.py`, and add test
coverage for `obpi_audit_cmd` + `obpi_withdraw_cmd`. Headline: `gz obpi audit`
becomes the deterministic Phase-1 engine of gz-obpi-reconcile.

OBPI-01 recursion is **already implemented** in the working tree — so
`gz validate --skill-alignment` is already enforcing multi-word verbs; these
wirings are immediately effective.

## Files

| Role | Path |
|------|------|
| Edit | `.gzkit/skills/gz-obpi-reconcile/SKILL.md` |
| Edit | `.gzkit/skills/gz-status/SKILL.md` |
| Edit | `.gzkit/skills/gz-adr-promote/SKILL.md` |
| Edit | `.gzkit/skills/gz-adr-sync/SKILL.md` |
| Edit | `.gzkit/skills/gz-arb/SKILL.md` |
| Edit | `.gzkit/skills/gz-chore-runner/SKILL.md` |
| Edit | `.gzkit/skills/gz-skill-router/SKILL.md` |
| Edit | `src/gzkit/governance/trust_audits/cli.py` |
| Create | `tests/commands/test_obpi_audit_cmd.py` |
| Create | `tests/commands/test_obpi_withdraw_cmd.py` |
| Regenerate | mirrors via `uv run gz agent sync control-surfaces` |

## Steps

### 1. Discovery (read-only, no edits)

Read each target skill for current structure and `gz_command:` field placement:
- `.gzkit/skills/gz-obpi-reconcile/SKILL.md` lines 120–153 (Phase 1 body)
- `.gzkit/skills/gz-status/SKILL.md`
- `.gzkit/skills/gz-adr-promote/SKILL.md`
- `.gzkit/skills/gz-adr-sync/SKILL.md`
- `.gzkit/skills/gz-arb/SKILL.md`
- `.gzkit/skills/gz-chore-runner/SKILL.md`
- `.gzkit/skills/gz-skill-router/SKILL.md`
- `src/gzkit/commands/obpi_audit_cmd.py` (understand handler)
- `src/gzkit/commands/obpi_cmd.py:59` (understand withdraw handler)
- `tests/commands/common.py` (mocking harness for new tests)

### 2. Write RED tests (TDD)

Create `tests/commands/test_obpi_audit_cmd.py`:
- `TestObpiAuditCmd.test_obpi_audit_single` — invoke `obpi_audit_cmd(obpi_id)`,
  verify a well-formed `obpi-audit` ledger entry with `criteria_evaluated` is
  produced. Decorate with `@covers("REQ-0.0.67-02-03")`.
- `TestObpiAuditCmd.test_obpi_audit_adr_scope` — invoke with `adr_id=...`,
  verify ledger entry. Decorate with `@covers("REQ-0.0.67-02-03")`.

Create `tests/commands/test_obpi_withdraw_cmd.py`:
- `TestObpiWithdrawCmd.test_withdraw_emits_event` — invoke `obpi_withdraw_cmd`,
  verify `obpi_withdrawn` event emitted. Decorate with `@covers("REQ-0.0.67-02-04")`.
- `TestObpiWithdrawCmd.test_double_withdraw_rejected` — second withdrawal rejected.
  Decorate with `@covers("REQ-0.0.67-02-04")`.

Run `uv run -m unittest tests.commands.test_obpi_audit_cmd tests.commands.test_obpi_withdraw_cmd` — expect RED.

### 3. Wire gz-obpi-reconcile (3 verbs)

Edit `.gzkit/skills/gz-obpi-reconcile/SKILL.md`:
- **Phase 1 (lines 120–153):** Replace ad-hoc `Read/Grep/Bash` audit steps 2–6
  with invocation of `gz obpi audit <OBPI-ID>` (step 1) and
  `gz obpi audit --adr <ADR-ID>` (for ADR-scope run) as the deterministic
  evidence step. Keep the "Parse acceptance criteria" framing as step 0.
- Add `gz obpi emit-receipt` as the receipt-writing step in Phase 2 (where the
  brief update path records proof).
- Add `gz obpi withdraw` as the phantom-remediation step — when Phase 1 finds
  a phantom `obpi_created` event (no brief file), call `gz obpi withdraw` to
  clean the ledger graph.
- Bump `skill-version:` to `3.1.0` and `last_reviewed:` to `2026-06-07`.

### 4. Wire gz-status (1 verb)

Edit `.gzkit/skills/gz-status/SKILL.md`:
- Add `gz obpi status <OBPI-ID>` as a focused single-OBPI runtime view command
  in the skill's procedure (distinct from the ADR-level status command).
- Bump `skill-version:` and `last_reviewed:`.

### 5. Wire gz-adr-promote (1 verb)

Edit `.gzkit/skills/gz-adr-promote/SKILL.md`:
- Add `gz adr demote <ADR-ID>` for bidirectional lifecycle (demotion back to
  pool or pre-release tier). Document it as the inverse of promote.
- Bump `skill-version:` and `last_reviewed:`.

### 6. Wire gz-adr-sync (1 verb)

Edit `.gzkit/skills/gz-adr-sync/SKILL.md`:
- Add `gz adr covers-check <ADR-ID>` as a step where the sync discovers
  `@covers` tags and validates coverage.
- Bump `skill-version:` and `last_reviewed:`.

### 7. Wire gz-arb (1 verb)

Edit `.gzkit/skills/gz-arb/SKILL.md`:
- Add `gz arb ty` as the raw `uvx ty` passthrough entry (note: **NOT** an alias
  of `gz arb typecheck`; runs `uvx ty check .` without the ARB wrapper).
- Bump `skill-version:` and `last_reviewed:`.

### 8. Wire gz-chore-runner (1 verb)

Edit `.gzkit/skills/gz-chore-runner/SKILL.md`:
- Add `gz chores propose-ghi` as the chore→GHI output step at the end of the
  chore runner procedure (when a chore surfaced a finding that warrants a GHI).
- Bump `skill-version:` and `last_reviewed:`.

### 9. Wire gz-skill-router (2 verbs)

Edit `.gzkit/skills/gz-skill-router/SKILL.md`:
- Add `gz skill list` as the catalog discovery command (returns active skill
  catalog).
- Add `gz skill new` as the skill scaffolding command (creates a new skill
  scaffold under `.gzkit/skills/`).
- Bump `skill-version:` and `last_reviewed:`.

### 10. Remove 13 multi-word stop-gap waivers from cli.py

Edit `src/gzkit/governance/trust_audits/cli.py`:
- Remove the entire `# Multi-word subcommand waivers (GHI #588)` block
  (currently lines 71–131): all 13 entries — 3 deprecated aliases +
  10 live orphan verbs.
- For the 3 deprecated aliases (`obpi lock-claim/-release/-status`): only
  the `_NO_SKILL_VERBS` entry is removed here; parser registration /
  doc cascade is OBPI-03 scope (Denied Paths).
- Keep the recursion machinery and all other `_NO_SKILL_VERBS` entries intact.

### 11. Run `gz agent sync control-surfaces`

```bash
uv run gz agent sync control-surfaces
```

Regenerates all mirrors after the 7 canonical skill edits. Must run before
any verify step.

### 12. Implement tests to GREEN

Run the tests; confirm they pass after wiring is done.

```bash
uv run -m unittest tests.commands.test_obpi_audit_cmd tests.commands.test_obpi_withdraw_cmd -v
```

### 13. Verify

```bash
uv run gz validate --skill-alignment
uv run gz validate --surfaces
uv run -m unittest discover -s tests -t .
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
```

## Verification (from brief)

```bash
uv run gz agent sync control-surfaces
uv run gz validate --skill-alignment
uv run gz validate --surfaces
uv run -m unittest discover -s tests -t .
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
```

## Notes

- OBPI-01 recursion is already live — validate --skill-alignment is enforcing
  multi-word verbs now. Wiring is immediately effective.
- 3 deprecated aliases removed from `_NO_SKILL_VERBS` here; parser registrations
  stay until OBPI-03.
- All skill edits must bump `skill-version:` + `last_reviewed:` in the same edit;
  run sync before any verify step.
- No new `_NO_SKILL_VERBS` entries for any of the 10 (NEVER mandate per brief).
- Wiring must be genuine procedural use in the skill body, not a name-drop.
