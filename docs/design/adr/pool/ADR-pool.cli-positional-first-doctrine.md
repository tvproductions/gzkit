---
id: ADR-pool.cli-positional-first-doctrine
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.cli-positional-first-doctrine: Positional-First CLI Doctrine and Status Surface Realignment

## Status

Pool

## Date

2026-04-14

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Elevate positional arguments to the default shape for `gz` CLI verbs, and land
the status surface (`gz status`, `gz adr status`, `gz adr report`) as the first
application of that doctrine. Repair the skill-to-CLI routing drift documented
in GHI #141 without collapsing verbs whose distinct consumer roles are real.
Preserve existing flags as aliases so adoption is additive.

The operator-facing concept is "status" — the skill `gz-adr-status` remains the
entry point — and the CLI verbs it wields align to positional invocation
(`gz adr report pool`, `gz adr report ADR-0.25.0`) rather than flag-driven
invocation. A unified JSON status model lets dependent skills consume all three
verbs through a consistent shape.

---

## Target Scope

### Doctrine

- Declare positional-first as standing CLI contract doctrine in
  `.gzkit/rules/cli.md` (and its mirror `.claude/rules/cli.md` after sync).
- Rule: when a CLI verb accepts an identifier or a categorical selector, it
  MUST accept it as a positional argument. Flag-based alternatives (e.g.
  `--type pool`) remain as backward-compatible aliases for one release cycle,
  then deprecate.
- Rule: positional argument shape is discoverable via `--help` with at least
  one positional example.
- Rule: adding a new positional to an existing verb is additive (Lite lane);
  introducing a new subcommand or removing a flag remains Heavy lane.

### Status surface (first application)

- `gz adr report`:
  - `gz adr report` → wide view, all ADRs (current behavior).
  - `gz adr report ADR-X.Y.Z` → single-ADR rich view (current behavior).
  - `gz adr report pool|foundation|feature` → positional type filter (new).
  - `--type {pool,foundation,feature}` → retained as alias.
- `gz adr status`:
  - Remains the programmatic single-ADR JSON consumer used by four dependent
    skills (`gz-adr-audit`, `gz-adr-recon`, `gz-adr-verification`,
    `gz-obpi-pipeline`). Distinct consumer role — not collapsed into `report`.
- `gz status`:
  - Remains the governance-state probe used by ~20 skills as the "did state
    change?" boilerplate check. Distinct consumer role — not collapsed.
- Unified `--json` schema across all three verbs: consistent field names,
  nested shape, versioned schema, documented in
  `data/schemas/status_unified.schema.json`. Dependent skills audited and
  updated in the same patch.

### Skill layer repair

- `gz-adr-status` skill:
  - Name preserved — "status" is the operator concept.
  - Frontmatter `gz_command:` transparently declares `adr report` (the CLI
    verb actually wielded for the rich operator view). Body documents why.
  - Positional translation: skill accepts `ADR-X.Y.Z` or type keyword and
    translates to the canonical CLI invocation.
- Add a thin companion skill (or skill section) documenting
  `gz adr status ADR-X.Y.Z --json` for machine consumers, so the
  programmatic surface is discoverable via skill routing rather than only
  via direct CLI reference in four dependent skills.

### Documentation (Gate-5 runbook-code covenant)

- Manpages for all three status verbs in `docs/user/manpages/`.
- Runbook (`docs/user/runbook.md`) updated to make the three-way verb
  topology explicit with when-to-use-which guidance.
- Command docs (`docs/user/commands/status.md`, `adr-status.md`,
  `adr-report.md`) updated to reflect positional-first shape.
- Release notes entry under "CLI contract changes".

### BDD coverage (closes secondary defect from GHI #141)

- `features/adr_status.feature` — BDD scenarios for `gz adr status`
  including `--json` schema validation.
- `features/adr_report.feature` — BDD scenarios for `gz adr report`
  including wide view, single-ADR view, and positional type filter.
- Extend `features/task_governance.feature` coverage of `gz status` for
  parity.

### Follow-up chore

- Chore: `cli-positional-first-audit` — enumerate all `gz` CLI verbs, flag
  every verb that accepts an identifier or categorical selector via flag
  only, and file a punch list for migration. Not in this ADR's implementation
  scope, but tracked as the natural consequence of the doctrine.

---

## Provenance

This pool ADR emerged from Q&A on 2026-04-14 during triage of GHI #141. The
operator confirmed:

1. Canonical operator concept is "status" — the `gz-adr-status` skill name
   and runbook prescription both preserve it.
2. Current skill routing (skill invokes `gz adr report` under the hood)
   produces the desired output — nothing is behaviorally broken.
3. The three-verb distinction is real: `gz status` is an internal probe,
   `gz adr report` is the operator rich view, `gz adr status --json` is a
   machine-readable consumer used by four dependent skills. Collapsing them
   would regress dependent skills or surrender consumer clarity.
4. Positional-first is the preferred CLI shape across the board (full scope,
   not narrow), acknowledged as Heavy lane.
5. Unified `--json` schema across all three verbs is preferred over
   leaving the current per-verb shapes — architectural purity accepted over
   blast-radius minimization.
6. Work is pooled, not active — captures architectural intent without
   claiming a version slot.

---

## Dependencies

- **Blocks on**: none
- **Blocked by**: none
- **Related**: GHI #141 (status-adjacent CLI/skill routing drift), GHI #144
  (mechanize tool/skill/runbook invariants in `gz validate --surfaces`),
  `ADR-pool.command-aliases` (related CLI affordance theme, independent).

---

## Out of Scope

- Collapsing any of the three status verbs into each other.
- Changing the operator concept from "status" to "report".
- Adding a new CLI subcommand (all changes are additive to existing verbs).
- Implementing the global CLI positional audit — that is the follow-up
  chore's job, tracked separately.
- Migrating flags to positional on verbs outside the status surface in this
  ADR's implementation.

---

## Anti-Patterns (explicit, from the Q&A)

- Do not collapse `gz status`, `gz adr status`, and `gz adr report` into a
  single verb — each serves a distinct consumer (probe / rich view / machine
  JSON). GHI #141 audit confirmed the distinction is real.
- Do not rename `gz-adr-status` skill to match the CLI verb it wields —
  operator concept ("status") is authoritative; the skill's frontmatter is
  where the translation lives.
- Do not break the four dependent skills (`gz-adr-audit`, `gz-adr-recon`,
  `gz-adr-verification`, `gz-obpi-pipeline`) that consume
  `gz adr status ADR-X.Y.Z --json` — audit and update them in the same
  patch when the unified JSON schema lands.
- Do not land the doctrine change without manpages, BDD, and runbook
  updates — Gate 5 runbook-code covenant applies.

---

## Promotion Notes

When promoted to active work, decompose into OBPI briefs along these seams:

1. **Doctrine declaration** — `.gzkit/rules/cli.md` update, sync mirrors.
2. **Unified `--json` schema** — schema file, validation, documentation.
3. **`gz adr report` positional** — add positional type arg, `--type` alias.
4. **`gz adr status` unified JSON output** — align to unified schema.
5. **`gz status` unified JSON output** — align to unified schema.
6. **Dependent skill updates** — four skills consuming `--json`.
7. **Skill frontmatter honesty** — `gz-adr-status` skill metadata repair.
8. **Documentation bundle** — manpages, runbook, command docs, release notes.
9. **BDD coverage** — three feature files or extensions.
10. **Follow-up chore filing** — `cli-positional-first-audit`.

Each seam is an OBPI-sized increment. Full set is Heavy lane (Gates 1-5 with
human attestation).
