# Conflict matrix — 2026-10-10

Scope: 29 canonical files, 406 unordered pairs (27 files under `.gzkit/rules/`, root `AGENTS.md`, `CLAUDE.md`). Baseline `7757851b603a7d3129eabe224aae366364f2444c` (2026-09-19). Eleven files changed since the baseline, one of them new (`weaponeering.md`), so 253 pairs were re-reviewed and 153 carry the September judgment unchanged. Per-pair judgments are in [current-pair-review.json](current-pair-review.json); hashes in [rule-inventory.md](rule-inventory.md). Counts describe review coverage, not a proof that every possible contradiction has been found.

Method this run: one reviewer (the main session) read every file in scope whole, then read each hunk changed since the baseline against every other file. The September run used three independent partitions; this one did not, and says so.

## Rows closed in this period

No concrete conflict remains open. The two rows below are the ones this period closed; they are listed so the matrix names what changed rather than presenting an empty table.

| Rule A | Rule B | Worked example | Evidence | Mechanical winner | Suggested resolution | Severity |
|---|---|---|---|---|---|---|
| R01 `.gzkit/rules/chores.md`, Authoring a New Chore (September text: canonical chore packages live in the package directory) | `.gzkit/rules/skill-surface-sync.md`, Surface layout: `.gzkit/chores/<slug>/` is canonical, edit here | Edit a canonical chore's CHORE.md in the project, damage its acceptance file, run the doctor: the package copy overwrites the surviving edit, while the other rule called the project copy the source | GHI #1044 | `sync_pkg_surfaces` writes project to package; the doctor restores package to project only for a damaged slug | Closed 2026-09-28 by operator ruling: `chores.md` 0.6.0 names `.gzkit/chores/` the authoring source and describes doctor recovery as repair | theoretical (closed) |
| F1 `.gzkit/rules/tests.md`, Two runners: cites `AGENTS.md` Gate Covenant for "behave is heavy-lane OBPI and CI scope, never a per-change gate" | Root `AGENTS.md`, Gate Covenant | The diet landing of 2026-10-10 lifted that sentence to `docs/governance/agent-contract-rationale.md`. An agent following the citation found a pointer where the rule had been; `data/check_step_scopes.json`, the `gz-check` skill and a test docstring cite the same place | 64f35c53e | `AGENTS.md` Execution Rules (plain `gz check` drops the acceptance tier) and `data/check_step_scopes.json` | Closed the same day: the two binding sentences restored verbatim to Gate Covenant as one bullet; the rationale stays lifted | episodic (closed) |

F1 was introduced by this session's own diet landing and found by this audit. The landing treated two paragraphs as argument when each carried one binding sentence.

## Findings inside one file (not pair conflicts)

- `model-selection.md` § Do Not kept *"Hardcoding model IDs in subagent prompts (`claude-opus-4-7`) instead of using effort levels"* after 0.7.0 declared prompt-level effort inert. Repaired at 0.7.1 in this run: it was this session's own incomplete edit.
- `model-selection.md` line 55 maps `haiku` to `claude-haiku-4-5` and `sonnet` to `claude-sonnet-5`. Anthropic's system-card hub lists Sonnet 5.5 and Haiku 5.5 (read 2026-10-10, maintenance visit A). The line says to verify against the current catalog, so it is a currency item for `frontier-model-card-currency`, not a contradiction. Not edited.
- `gh-cli.md` § Census prescribes `gh api` forms that its own § Allowed commands block does not list. Whether the block is exhaustive is unstated in the rule; its 0.6.0 and 0.7.0 notes treat it as an allowlist. Carried to the reachability audit, where three skills meet the same block.

## Candidates, unproven (seven)

Recorded in `current-pair-review.json` as `unproven`. None has a worked example of two files prescribing opposite acts.

- `chores.md` and root `AGENTS.md`: chore scope against PRIME DIRECTIVE's fix-what-you-find. GHI #943 carries it. Observed this period as separate direct-fix commits outside chore runs, which both rules permit.
- `mx-mode.md` and root `AGENTS.md`: narrowed, because root now reads as MX does. Residue: MX forbids leaving the hangar with a detectable defect open; root lets an out-of-scope defect be tracked.
- `chores.md` and `mx-mode.md`; `mx-mode.md` and `skill-authoring.md`; `adr-audit.md` and root `AGENTS.md`: September judgments, re-read and kept.
- `weaponeering.md` and `hexagonal-architecture.md`: "interfaces" in the constraints sortie against the single-adapter port rule.
- `weaponeering.md` and `task-discovery.md`: the sortie-to-TASK mapping is unstated in both.

## Prior rows

The [2026-09-19 matrix](archive/2026-09-19/conflict-matrix.md) and its supporting proofs are preserved unchanged under `archive/2026-09-19/`; the 2026-09-12 set remains under `archive/2026-09-12/`.
