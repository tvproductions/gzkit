---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-16T09:00:58Z'
agent: claude-code
session_id: 4fd13b45-724e-4433-ab23-fd6c5df2b932
continues_from: .gzkit/handoffs/20261016T080705Z-safe-mode-plan-in-canon-model-level-reduced.md
---

## Current State Summary

Fourth pilotage handoff of 2026-10-16, superseding 20261016T080705Z-safe-mode-plan-in-canon-model-level-reduced.md. Written so the operator can reduce the model level; the pilot's open acts are listed under Immediate Next Steps. Since the anchor, three acts landed on main and are synced (origin at 8e78efc13): (1) safe mode is the sole term across canon (ead585053: doctrine title and terms, rule mx-mode.md 1.5.2 with scorecard row 62f re-bulleted, skill gz-mx 1.3.2, banner, hook template, enter and exit labels, parser help, event and marker field descriptions, manpages, contract template, glossary, the AGENTS.md corpus entry retired and re-remembered then landed under the operator's words with a retention map; 'martial law' survives only inside operator quotes and dated records; sole-term fence tests over banner, hook body, parser help and the two mode fields; arb red driven after one undriven repair); (2) a sync ordering defect fixed as a direct fix (15361cb33: sync_pkg_surfaces ran before sync_nested_agents_md so the wheel copy of a skill-scoped nested AGENTS.md lagged one sync behind canon; the package copy now runs downstream, red-then-green test in tests/test_sync.py; arb red driven); (3) the control-plane cut booked under the operator's ruling A (8e12e38f4: backup tag control-plane-baseline-2026-10-16 at eff2062c8 pushed; baseline proof .gzkit/chores/instructions-files-diet/proofs/baseline-2026-10-16-control-plane.txt; D4, the drydock exit table, the regime row and the doctrine's standing exit measures widened to every surface an agent loads; executive decision 6; WP-13 #1249, WP-14 #1250, WP-15 #1251, WP-16 #1252 filed with closure contracts; #1246 cross-linked as stage 1). Safe mode has still not been entered through the gz-mx skill (H8) and OBPI-0.35.0-17 and -20 remain Draft (H9).

## Important Context

- The per-turn load measured 2026-10-16 at eff2062c8: AGENTS.md 24,629 B (budget 25,000); rules 149,529 B over 26 files (largest tests.md 11,618 B); skill descriptions 15,816 chars over 73 skills, 11 user-invoked only; skill bodies 639,408 B; agents 10,799 B over 5; nested AGENTS.md 175,877 B over 17 repo-side files; personas 24,879 B; 17 hook scripts, orientation 4,831 B per session. Exit numbers (contract § Drydock exit numbers): rules at or under 60 KB and no rule over 4,000 B; descriptions at or under 6,000 chars; skills at most 40 with bodies under the skill_contract ceiling; agents at or under 6 KB; nested AGENTS.md at or under 60 KB; personas at or under 12 KB; injected hook text at or under 4 KB per turn; every number read by gz validate --instructions-files-budget once WP-13 lands.
- Order of the cut: WP-13 #1249 (the witness) and the WP-16 #1252 protocol first, then stages; no stage is accepted without its WP-16 report (retention maps plus a compression-sweep read, gz readiness evaluate before and after, one work package flown by a fresh session on the cut surfaces). The WP-14 merge plan goes to the operator before the first skill deletion. Any surface restores with git checkout control-plane-baseline-2026-10-16 -- <path>.
- Canon reset against the trimmed state goes through gz content retire and gz content land with --retention-map (every dropped block KEPT with a span or DROPPED with a reason named in the attestation text), never by editing a rendition; a landing then needs gz agent sync control-surfaces. The example map of this session: the scratchpad root.retention.json pattern with extracted_by spec-reviewer and mapped_by main-session.
- A rule heading used as a scorecard bullet must stay a verbatim substring of the rule; mx-mode.md § 'Safe mode: ceremony suspended under a contract' is row 62f's bullet (gz validate --bullet-retention).
- A rebase with --autostash can leave gz-written ledger rows in a stash when both sides appended to .gzkit/ledger.jsonl; this session re-inserted the three displaced rows in timestamp order and validated (gz validate --ledger exit 0). stash@{0} still holds them as a backup and may be dropped. Prefer committing ledger rows before any rebase.
- Records under the contract: one commit per act with its Task: trailer (required whenever src/ is touched, wheel copies included), gz arb red --commit after it, undriven repaired in the same commit, a passage-log row, git add -A then gz check before the commit, gz git-sync --apply after.
- A commit's string-only hunks (banner text, Field descriptions, parser help) come back undriven unless a test asserts the semantics of the wording; the sole-term fence tests are the pattern.

## Decisions Made

- [operator-ruled] Safe mode is the sole term; verbatim "safe mode is the sole term, update the canon". Applied to every authored surface; operator quotes and dated records keep their wording.
- [operator-ruled] The control-plane cut, option A; on the question "where in this safe-mode drydock plan will you aggressively trim all control plane artifacts (agents, rules, skills and any other items that an agent loads and saturates context)?" the ruling verbatim: "A (in safe mode - make backups!!! - help me test how much we can cut and remain effective, I need to better balance context bloat)".
- [operator-ruled] Canon may be re-baselined to the trimmed state; verbatim "we can reset canon against the trimmed state". Carried into executive decision 6 as retire/land with retention maps.
- [agent-chose] The per-surface exit numbers under A (rules 60 KB and 4,000 B per file; descriptions 6,000 chars; skills 40; agents 6 KB; nested AGENTS.md 60 KB; personas 12 KB; hook text 4 KB per turn). **Rationale:** a cut needs a number to read; each is roughly half of today with the largest surfaces cut hardest; the operator may move any by a word, and WP-16 exists to find where effectiveness drops.
- [agent-chose] WP-13 lands before any cut and WP-16's report gates each stage. **Rationale:** the 2026-09-17 compression passed every gate and lost 15 binding conditions; bytes alone do not measure a cut.
- [agent-chose] The sync pass-order defect fixed directly, no GHI. **Rationale:** AGENTS.md § Defect-fix routing: one surface, under ten source lines, surfaced in flight, covered by a red-then-green test.
- [agent-chose] Displaced ledger rows re-inserted rather than left in the stash. **Rationale:** they are gz-written receipt rows the ledger owes; append-only order preserved; validated.

## Immediate Next Steps

1. Operator: H8, invoke /gz-mx and enter safe mode under docs/governance/harbor-pilotage-candidate-2026-10-15.md; then GHI #1244 closes fixed against ac3b0005e.
2. Operator: H9, rule on the four cutover disclosures and attest OBPI-0.35.0-17 and -20.
3. Cheaper sessions, each as its GHI under the contract's § Records, in this order where they depend: WP-13 #1249 (the budget witness) first; then WP-10 #1245, WP-8 #1247, WP-12 #1248 in any order; WP-11 #1246 as stage 1 of the cut once the WP-16 protocol is written, with its report.
4. Pilot, when booked again: write the WP-16 #1252 protocol into docs/evals/ and the acceptance steps of #1250 and #1251; draft the WP-14 #1250 merge plan (73 skills to at most 40) for the operator's ruling; then H5, the catalog's first entries from briefs 16 to 20; H6, one brief cut as a work package.
5. Pilot at the end: the handback amendment (H10) after the drydock release and the sea trial.

## Pending Work / Open Loops

- OBPI-0.35.0-17 and -20 Draft, awaiting attestation (H9).
- GHI #1244 open until H8; #1245, #1246, #1247, #1248, #1249, #1250, #1251, #1252 open as work packages.
- The WP-16 protocol and the WP-14 merge plan are pilot acts not started; H5, H6, H10 not started; drydock D1 to D6 and the sea trial follow.
- stash@{0} holds the three ledger rows already restored to .gzkit/ledger.jsonl; drop it after confirming git stash show -p stash@{0} matches rows present in the ledger.
- Carried from earlier handoffs: the four slice-size findings and the Decomposition Matrix re-cut; GHI #1230 to #1241 routing; the tracker for the 27 helper-or-loop gates; the three pointer-line lifts in the diet chore's recommendation of 2026-10-15 not ruled on.

## Verification Checklist

- git log --oneline -6 shows 8e78efc13, 8e12e38f4, eff2062c8, 15361cb33, ead585053 on main, synced; git ls-remote --tags origin control-plane-baseline-2026-10-16 returns the tag.
- grep -c -i martial AGENTS.md prints 0; grep -rn -i martial .gzkit/rules .gzkit/skills src tests returns only operator quotes and test reasons.
- uv run gz validate --advisory-scorecard --bullet-retention --invariant-coherence --rendition-lineage --rendition-freshness --ledger exits 0.
- uv run python -m unittest tests.test_sync -k nested_agents_md_in_one_sync and tests.hooks.test_mx_awareness tests.commands.test_mx_enter tests.test_hooks pass.
- uv run mkdocs build --strict green; uv run gz check green on 8e12e38f4.
- gh issue view 1249 --json state, 1250, 1251, 1252 are OPEN; gh issue view 1246 --json comments shows the cross-link naming #1249, #1250, #1251, #1252.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (D4, drydock exit table, regime row, executive decision 6, WP-13 to WP-16, passage-log rows of 2026-10-16)
- `docs/governance/safe-mode-doctrine.md` (title, terms, standing exit measures widened)
- `.gzkit/chores/instructions-files-diet/proofs/baseline-2026-10-16-control-plane.txt`
- `.gzkit/rules/mx-mode.md` (1.5.2), `docs/governance/rule-version-history.md`, `docs/governance/advisory-rules-audit.md` (row 62f)
- `.gzkit/skills/gz-mx/SKILL.md` (1.3.2), `.gzkit/templates/safe_mode_contract.md`
- `src/gzkit/mx/awareness.py`, `src/gzkit/hooks/scripts/mx.py`, `src/gzkit/commands/mx_cmd.py`, `src/gzkit/cli/parser_governance.py`, `src/gzkit/events.py`, `src/gzkit/mx/marker.py`
- `src/gzkit/sync_surfaces.py` (package copy downstream of the nested pass), `tests/test_sync.py`
- `tests/hooks/test_mx_awareness.py`, `tests/test_hooks.py`, `tests/commands/test_mx_enter.py`, `tests/commands/test_mx_exit.py`
- `.gzkit/corpus/AGENTS.md.jsonl` (retirement and re-remembered entry), `.gzkit/renditions/AGENTS.md/root.retention.json`
- receipts: arb-red-commit-ead585053def-4d9ae7a260f84156bb192d68088debe7 (driven), arb-red-commit-15361cb33c6d-9e936c03e05744d7b4154531fcbc8434 (driven), arb-red-commit-8e12e38f490d-78ffc26239134724b645a97d744e5eb7 (no-production-hunks)
- GHIs #1249, #1250, #1251, #1252; tag control-plane-baseline-2026-10-16

## Settled Rulings

1555 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
