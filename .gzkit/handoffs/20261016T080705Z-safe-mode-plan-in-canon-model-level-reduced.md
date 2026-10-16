---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-16T08:07:05Z'
agent: claude-code
session_id: 4fd13b45-724e-4433-ab23-fd6c5df2b932
continues_from: .gzkit/handoffs/20261016T060857Z-pilotage-safe-mode-and-budget-ruling.md
---

## Current State Summary

Third pilotage handoff of 2026-10-16, superseding `20261016T060857Z-pilotage-safe-mode-and-budget-ruling.md`. The safe-mode (martial law) plan exists and is canon: `docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Pilotage chart is the tracking instrument (one exceptional period: harbor, drydock, sea trial, handback; readings move only by a passage-log act), and `docs/governance/safe-mode-doctrine.md` generalizes it with the standard chart, the Release Package type, the sea trial procedure and the contract template. Landed since the last handoff, in order: the pilotage chart (`8984ba022`) and its amendment to one exceptional period on the operator's three confirmations (`cd6099b9c`); safe-mode entry and exit made skill-driven in gz-mx 1.3.0 (`9c157e7f2`); the doctrine, the contract template, the glossary terms and one AGENTS.md corpus entry landed under the operator's words (`47a061243`); the chart's specifics entrenched and the release template added (`d9b222440`); the work order retired, work package everywhere, WP-1 to WP-11 (`3866925b3`); the Release Package named and WP-12 filed as GHI #1248 (`2bd76e81f`). Four packages are filed for cheaper sessions: WP-8 #1247, WP-10 #1245, WP-11 #1246, WP-12 #1248. Main is synced; tree clean. The operator asked for this handoff to reduce the model level: execution now goes to cheaper sessions, the pilot returns for rulings and for H5, H6 and the handback.

## Important Context

- Safe mode is on the record as doctrine, template, rule (mx-mode.md 1.5.1), skill (gz-mx 1.3.1) and verb, but the present pilotage has not been entered through the verb: H8 is the operator invoking `/gz-mx` to enter safe mode under the contract. Until then the banner does not fire and the ledger carries no marker.
- Gate 5 was never suspended: OBPI-0.35.0-17 and -20 are executed but `Draft` until the operator attests them (H9), after ruling on the four disclosures in the passage log (cutover row of 2026-10-15).
- The vocabulary is settled: work package (labor on one contract; keyed to a GHI until the catalog lands), Release Package (one document per version, `status` carries planned/in-flight/released, template `.gzkit/templates/release_package.md`), release (the operator's signature). "Work order" is retired; "release plan" is retired. ADRs are not releases.
- Drydock exit numbers are executive decisions the operator may move: AGENTS.md at or under 25,000 chars; skill descriptions at or under 8,000 chars; rules at or under 90 KB with no rule over 6,000 B; zero controls without a named contract; one attestation per release.
- The AGENTS.md budget is 25,000 by the GHI #1243 ruling; AGENTS.md is 24,643 chars after the corpus entry landed (landing-20261016T073416Z-061bc361).
- Cheaper sessions execute packages under the contract's § Records: one commit per act with its `Task:` trailer, `gz arb red --commit` after it, an undriven verdict repaired in the same commit, a passage-log row with the measurement before and after. The per-change gate runs only the tests a change touches; run `gz test` before claiming a tier green.
- A commit touching `src/` (including the wheel copies under `src/gzkit/skills`, `rules`, `templates`) needs a `Task:` trailer or the pre-push gate refuses.

## Decisions Made

- [operator-ruled] Crisis mode: verbatim "in safemode/martial law, you need to lean in and make executive decisions to achieve outcomes as we are in crisis mode here" and "Don't forget I am in a 'kernel panic' mode here - gzkit has become untenable."
- [operator-ruled] Entry and exit are skill-driven: verbatim "these need to be skill driven: 'gz mx exit'".
- [operator-ruled] One exceptional period, the sea trial substrate, the release document shape: verbatim "confirm all three, amend the chart", on "my expectation is the we leave martial law | safe mode | dry dock with a return to seaworthiness so that I can return to a normal voyage" and "i must have a release management document type too".
- [operator-ruled] The metaphor and the chart's specifics entrenched: verbatim "keep these metaphor entrenched in canon, this won't be the last time we need to reach for this approach" and "i meant these" (the chart's items).
- [operator-ruled] The work order retired: verbatim "retire it, work package everywhere - change now: 'WO-1 to WO-11' to WP".
- [operator-ruled] The release type and the release skill: verbatim "Release Package it is, rename and write WP-12", on the proposal "perhaps the release is 'Release Package.' And we build a skill that has some mechanisms, rubrics, thresholds for when we have enough pipeline pressure to recommend a release it can coordinate with, or subsume, the current patch release skill."
- [agent-chose] Drydock exit numbers set as executive decisions (see context). **Rationale:** the chart needs numbers to read; the operator may move any by a word.
- [agent-chose] The gz-release skill subsumes gz-patch-release rather than coordinating with it. **Rationale:** two skills deciding "ship now" would drift against each other; the patch ceremony is one path of the same act.
- [agent-chose] One AGENTS.md corpus entry pointing at the safe-mode doctrine was landed through `gz content land` with the operator's entrenchment words as the corpus attestation. **Rationale:** the words authorized exactly that addition; the lineage gate is in the default check and would otherwise have blocked every push.

## Immediate Next Steps

1. Operator: H8, invoke `/gz-mx` and enter safe mode under `docs/governance/harbor-pilotage-candidate-2026-10-15.md`; then GHI #1244 closes `fixed` against `ac3b0005e`.
2. Operator: H9, rule on the four cutover disclosures and attest OBPI-0.35.0-17 and -20.
3. Cheaper sessions, any order, each as its GHI under § Records: WP-10 #1245 (the orientation reads the chart), WP-11 #1246 (rules and skill-description cut, H4), WP-8 #1247 (the obligation column, H7), WP-12 #1248 (gz-release, drydock D1).
4. Pilot, when booked again: H5, the catalog's first entries from briefs 16 to 20 under the decided shapes; then the H6 cut of one brief as a work package for a cheaper session to fly.
5. Pilot at the end: the handback amendment (H10) after the drydock release and the sea trial.

## Pending Work / Open Loops

- OBPI-0.35.0-17 and -20 `Draft`, awaiting attestation (H9).
- GHI #1244 open until H8; #1245, #1246, #1247, #1248 open for cheaper sessions.
- H5, H6, H10 are pilot acts not started; drydock D1 to D6 and the sea trial follow.
- Carried from earlier handoffs: the four slice-size findings and the Decomposition Matrix re-cut; GHI #1230 to #1241 routing; the tracker for the 27 helper-or-loop gates.
- The three pointer-line lifts in the diet chore's recommendation of 2026-10-15 were not ruled on.

## Verification Checklist

- `git log --oneline -12` shows `2bd76e81f`, `3866925b3`, `d9b222440`, `47a061243`, `9c157e7f2`, `cd6099b9c`, `8984ba022` on main, synced.
- `uv run gz validate --instructions-files-budget --invariant-coherence --rendition-lineage --distribution` exits 0 with no advisory.
- `uv run gz mx enter --help` lists `--mode {mx,safe}` and `--contract PATH`; `.gzkit/templates/safe_mode_contract.md` and `release_package.md` exist and ship in `src/gzkit/templates/`.
- `uv run mkdocs build --strict` green; `uv run gz check` green on the last commit.
- `gh issue view 1248 --json state` is OPEN; `gh issue view 1243 --json state` is CLOSED.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (contract, chart, packages, passage log)
- `docs/governance/safe-mode-doctrine.md`
- `.gzkit/templates/safe_mode_contract.md`, `.gzkit/templates/release_package.md`
- `.gzkit/rules/mx-mode.md`, `.gzkit/skills/gz-mx/SKILL.md`
- `docs/rnd/renewing-vows/doctrine-merge.md` (glossary terms)
- `.gzkit/renditions/AGENTS.md/root.md`, `AGENTS.md`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1552 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
