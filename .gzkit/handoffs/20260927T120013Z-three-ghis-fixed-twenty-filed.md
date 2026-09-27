---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T12:00:13Z'
agent: claude-code
session_id: bb6a018e-e628-483e-b38b-ae838c93c0a2
continues_from: .gzkit/handoffs/20260927T101622Z-seven-ghis-fixed-1017-reopened-and-closed.md
---

## Current State Summary

This session resumed 20260927T101622Z-seven-ghis-fixed-1017-reopened-and-closed.md (ruling booked with gz handoff decide, verbatim "fix 1112"; its steps on the brief-drift insight, ADR-0.35.0 OBPI work and the carried open questions set aside). No OBPI work was initiated and no lock is held.

Closed with evidence: #1112, the eight scaffold-template skills (gz-constitute, gz-prd, gz-plan, gz-adr-promote, gz-init, gz-agent-sync, gz-status, gz-tidy) reviewed two per commit, plus four openai.yaml template lines (cee03d911, 895e961eb, a45297d24, f6d6d7da7, 2de60b196; follow-up runbook row cc2e3dd0d); #1123, gz init --update now writes only what delivery defines and merges chores/registry.json instead of overwriting it (29f195491); #1122, --update and gz upgrade detect operator edits from a shipped hash history, src/gzkit/canonical_history.json (3cad9e3f1).

Filed from the #1112 review findings: GHIs #1119 to #1137 (nineteen, one class each); re-opened #1022 (prd.md and obpi.md templates teach Gate 5 as heavy-only) and #1060 (38 skill doc pages name a .github/skills mirror). New instances were commented onto #837, #978, #1032 and #1110. HEAD 16fb42425 level with origin/main before this handoff.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This session worked the ghi triage front only; the adr/obpi front was not touched. ADR-0.35.0 remains 8/14 with closeout blocked on OBPIs 07, 08, 10, 11, 12 and 13.

New mechanisms other work will meet. src/gzkit/canonical_history.json is appended by gz agent sync control-surfaces (record_canonical_history in sync_pkg_surfaces), and tests/commands/test_init_update.py::TestCanonicalHistory fails when a current canonical file's hash is missing, so run the sync after any canonical edit. Never hand-edit the history; entries are never removed. gzkit.skills.delivered_skill_slugs and delivered_skill_body are the one definition of what skill delivery writes (router rows scoped, GHI #915), shared by scaffold, --update, gz upgrade and the history. gzkit.chores.iter_deliverable_chore_files is the chore delivery definition. surface_write gained effective_bytes and effective_files for sink-aware reads. The shrink-only private-import roster in tests/policy/test_import_boundaries.py lost the init_cmd edge chores._classify_chore_file.

Subagent reports are claims, not evidence: the four #1112 review tracks were spot-checked against the handlers before commit, and one rewrap dropped verbatim REQ-0.0.35-02 phrases that a test caught. The verifier-pipe-gate hook refuses a verifier followed by another statement; capture to a file and echo $? next.

## Decisions Made

- [operator-ruled] Verbatim: "fix 1112" (booked on the predecessor with gz handoff decide; cee03d911, 895e961eb, a45297d24, f6d6d7da7, 2de60b196).
- [operator-ruled] Verbatim: "yes, file the ghis" (#1119 to #1137 filed; #1022 and #1060 re-opened).
- [operator-ruled] Verbatim: "fix 1123" (29f195491).
- [operator-ruled] Verbatim: "fix 1122"; mechanism "Shipped hash history (Recommended)", brief OBPI-0.0.32-05 requirement 4(b) (3cad9e3f1).
- [agent-chose] Filed nineteen GHIs rather than six groups: ghi-author forbids bundling unrelated defects, one class per GHI.
- [agent-chose] Re-opened #1022 and #1060 rather than filing new: each declared a failure class whose fix bounded out a member found 2026-09-27, within 30 days of close.
- [agent-chose] The four already-reviewed openai.yaml fixes moved last_reviewed per skill-surface-sync.md rule 6, correcting the #1112 amendment comment that said it would not.
- [agent-chose] #1123 reads gz upgrade's _SURFACE_CLASSIFIERS at call time (same-package, avoids the upgrade to init_cmd import cycle) instead of adding four cross-package private edges to the shrink-only roster.
- [agent-chose] #1122 backfilled the history from every committed version, not only release tags, matching the forward rule that sync records every shipped state; adopter trees older than 2026-05-11 read EDITED (protected).

## Immediate Next Steps

1. Ask the operator which open GHI to take up next. The #1112 [settled] review findings are #1119 to #1137, and #1022 and #1060 are re-opened; #1119 (gz prd and gz constitute overwrite an existing document) is the nearest data-loss path.
2. Ask the operator about the prior carried items: GHIs #1110 and #1113, and the insight on whether gz obpi brief-drift --dry-run should stop writing a brief_reconciled ledger event.
3. Ask whether OBPI work on ADR-0.35.0 resumes; only the operator initiates it. When OBPI-0.37.0-04 is next initiated, its Denied Paths note on HEAD-only trailer scanning needs an operator amendment (stale since 98bec10c1).
4. Put to the operator that the pool ADR ADR-pool.harness-factoring-minimal-init precedent bullet was reworded in 3cad9e3f1 to name the hash history; it is their design document to confirm.

## Pending Work / Open Loops

Open from this session: #1119 to #1137, plus #1022 and #1060 (re-opened). #1131 is an investigation awaiting an operator ruling on whether gz adr promote should book adr_created. #1136 still carries the skill-surface-sync.md --force and mirror-ahead claims, the runbook --force wipe line, the persona count and the governance_runbook persona file names; its runbook marker item was resolved by 3cad9e3f1 and noted there.

Carried: #1110 (15 remaining redundant no-skill waivers after init was removed), #1113, #1034, #1063, #907. Insights awaiting operator rulings from the predecessor: dry-run brief-drift writes the ledger; OBPI-0.37.0-04's stale denial note; the rm -rf course-correction. The presenter insight that gz complexity advise prints No crossings detected after an all-attested run, the competitor-radar cadence, and whether the scaffolding-settings layer needs its own ADR remain unasked.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- uv run gz check passes on a fully staged tree.
- gh issue view <N> --json state reads CLOSED for #1112, #1122 and #1123, and OPEN for #1119 to #1137, #1022 and #1060.
- uv run gz init --update --dry-run in this repository reads EDITED: 0.
- uv run -m unittest tests.commands.test_init_update passes, including the canonical-history completeness witness.
- uv run gz obpi lock list shows no active locks.

## Evidence / Artifacts

- `src/gzkit/canonical_history.py` and `src/gzkit/canonical_history.json` (#1122)
- `src/gzkit/commands/init_cmd.py` and `src/gzkit/commands/upgrade.py` (#1122, #1123)
- `src/gzkit/chores/__init__.py` (iter_deliverable_chore_files, #1123)
- `src/gzkit/skills/__init__.py` (delivered_skill_slugs, delivered_skill_body, #1122)
- `src/gzkit/surface_write.py` (effective_bytes, effective_files)
- `tests/commands/test_init_update.py` and `features/init.feature`
- `docs/user/manpages/init.md`, `docs/user/manpages/upgrade.md`, `docs/user/runbook.md`
- `.gzkit/skills/gz-init/SKILL.md` and the seven other skills reviewed under #1112

## Settled Rulings

1122 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
