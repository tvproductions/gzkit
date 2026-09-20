---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-20T16:07:21Z'
agent: claude-code
session_id: ef443016-1abc-410c-8338-4b64521fd9d3
continues_from: .gzkit/handoffs/20260920T133039Z-f1-measurement-campaign-pointer-and-row3-chore.md
---

## Current State Summary

Thirteen commits, 72dfc1a81..5d8219c9a, tree clean, 0/0 with origin. Drew R&D row 4, then the session turned on one operator question -- 'how many other arbitrary and random rules do we have lingering?' -- and became config work.

Landed: row 4 (ghi-triage family/staleness pass, ghi-author Step 0 class test, sibling-state subtraction); the compress-before-grow discipline in two homes; a NEW Magna Carta edition dated 2026-09-20 with the reckoning re-measured and converted to a pointer; the 1.0 target moved to ~2027-08 by declaration; a config-derivation census; three shrink-only fences (GHI #1066, #1067); the single read seam gzkit.registries; and a config surface design record.

ADR-0.35.0 unchanged at 7/13, pre_closeout, closeout BLOCKED. No OBPI initiated, no lock claimed. Open GHI queue 56. Four GHIs closed (#1064, #1065, #1066, #1067); two of them were filed and closed the same session.

ADR-0.39.0 is AUTHORED-PENDING: the operator excepted ADR order for authoring only, and the gz-adr-create Step 0 interview has 12 of 19 fields banked with 7 outstanding. The ADR file does not exist yet.

## Important Context

Persona: main-session -- craftsperson, governance-aware, whole-file reasoning, direct.

THE SINGLE MOST USEFUL THING A SUCCESSOR INHERITS: the operator caught the agent dodging, and that correction is why config work exists at all. The agent treated 'ADR ORDER IS ABSOLUTE' as blocking the config system, built only the additive ratchet, and handed the ordering contradiction back as 'your call'. Operator verbatim: 'what of this ask about config? are you dodging it?' The dodge was specific -- most of a config system needs no ADR, and the shape was already decided when the operator named airlineops. Surface a doctrine contradiction as a named ruling request; do not route around it.

THE DOCTRINE CONTRADICTION, NAMED AND STILL LIVE. AGENTS.md Defect-fix routing sends runtime-contract work to OBPI; OBPI needs a parent ADR; ADR order put the config ADR fifth. Followed exactly, the doctrine makes the most urgent item wait longest. The operator resolved it twice: the loader and fences are DIRECT REPAIR (landed under GHIs #1066/#1067), and ADR order is excepted for AUTHORING 0.39.0 but NOT for completion. That second half arrived as a mid-turn correction, verbatim: 'wait, I will not complete adrs out of order.' Do not read the exception wider than authoring.

THE DEBT-CLASS BOUNDARY IS THE ADR'S LOAD-BEARING SEAM. The operator ranked the pre-mortem: '2 is the likeliest -- the debt class leaking back in.' That is a design instruction, not a comment. 'Separate class' is prose, and prose without a mechanism is the family the campaign exists to close, so the ADR must ship a MECHANICAL fence on the settings/debt boundary. Precedent in the tree: 'no parallel systems' has been declared in the hardcoded-root-eradication chore since 2026-04 and had 50 live violations on 2026-09-20.

TWO DETECTORS WERE WRONG AND BOTH WERE CAUGHT BEFORE LANDING. The direct-reach regex missed Path("data") and rostered 30 of 50 real, a 40% false-negative rate. A draft census script grew its own advisory-scorecard counter returning 70/34/71/1 against the validated 71/33/72/0 and was removed rather than reconciled. Against that, the family-signal heuristic WAS calibrated against a 38-member ground truth first, measured 26% wrong, and correctly shipped as candidate evidence rather than a count. Same skill, same session, applied inconsistently -- calibrate before landing any detector.

THE GATE REFUSED ITS AUTHOR, which is the first evidence it is not theatre. Mid-migration the agent wrote a fresh root / "data" / NAME while repairing a consumer, and --config-registry exited 3 on it by name.

MIGRATION IS NOT A SWEEP. population_controls.py took a real migration: read once, referenced seven times, four inside error strings calling .as_posix(), imported by two other modules. The gotcha a script would miss is that load_registry raises RegistryError where the old code caught OSError and JSONDecodeError -- leaving the except clause is how a check silently stops catching.

THE 1.0 SLOPE MATTERS MORE THAN THE DATE. OBPI completions by month: 306 (Mar), 109, 134, 75, 28, 3 (Aug), 4 (Sep, 20 days). About 2027-08 is defensible IF the rate returns to ~0.15/day; at August's rate alone it is 2027-11. Today: thirteen commits, zero OBPIs.

## Decisions Made

- [operator-ruled] Draw R&D row 4 (verbatim: 'row 4 it is'), after the resumed handoff was presented and its claims verified.
- [operator-ruled] Leave .github/workflows/queue-hygiene.yml standing as-is, ratifying the prior session's unilateral addition.
- [operator-ruled] Repair the campaign by cutting a NEW EDITION with full re-evaluation, over amending with pointers, amending Movement B alone, or holding to measure first.
- [operator-ruled] Seat the compress-before-grow discipline in BOTH homes -- the AGENTS.md corpus and skill-authoring.md clause 6 (verbatim: 'if we hit a limit then the agent htting the limit needs to stop and look for opportunities for compression and merging. We can't just have these grow, we need a discipline.').
- [operator-ruled] File a GHI for the SKILL_BODY_MAX_LINES thresholds and propose re-sourcing to the external 500; later folded into Movement F and closed superseded.
- [operator-ruled] Census the config surface first and route after ('census first, route after').
- [operator-ruled] One config system becomes a 1.0 prerequisite (verbatim: 'gzkit lacks a comprehensive and all-encompassing config system like airlineops had, we need to adopt this as a pre-requisite for 1.0. this is inexcusable. there are so many janky and undocumented rules, thresholds and pseudo-settings handing around gzkit. it is a travesty').
- [operator-ruled] Move the 1.0 target to ~2027-08 and record the declaration.
- [operator-ruled] Build the ratchet AND bring the 56 module constants into scope, rather than either alone.
- [operator-ruled] The loader seam and coherence gate are DIRECT REPAIR under GHIs, not OBPI work, resolving the routing and ADR-order contradiction rather than waiting on it.
- [operator-ruled] Config surface scope is the data/ registries and module constants PLUS .gzkit.json; shape is entry point plus categorical subdirectories; the waiver and grandfather rosters are a SEPARATE CLASS (debt state, not settings); readers migrate ONCE, after the surface lands.
- [operator-ruled] Addressing is LOGICAL KEYS, not filenames.
- [operator-ruled] Author ADR-0.39.0 now under a named exception to ADR order, AUTHORING ONLY (verbatim: 'wait, I will not complete adrs out of order').
- [operator-ruled] The likeliest pre-mortem failure is the debt class leaking back into settings.
- [agent-chose] Reproduced ghi-author Step 0's failure before hardening it, which REFUTED the remembered diagnosis: #1017 sat at rank 12 of the 20 titles shown, so the query reached the sibling and the reading did not.
- [agent-chose] Shipped family_signal as candidate evidence with a measured 26% disagreement rate rather than as a family count, because a keyword classifier presented as a measurement would author a fresh instance of the family it measures.
- [agent-chose] Removed the census script's own scorecard counter rather than reconciling it with the validator.
- [agent-chose] Merged the GHI #1064 coupling test into the existing registry suite rather than a new file, and retired a junk TEST corpus row through gz content retire rather than hand-editing the append-only store.
- [agent-chose] Compressed the corpus entry from 490B to 105B rather than raising the AGENTS.md budget, applying the discipline to its own statement.

## Immediate Next Steps

1. Present this state and await the operator's ruling. Nothing here authorizes execution.
2. FINISH THE ADR-0.39.0 INTERVIEW. docs/design/adr/ADR-0.39.0-config-surface-interview.json has 12 of 19 fields authored; 7 remain: wwhtbt, constraint_archaeology, assumption_surfacing, reversibility, operator_2am, scope_minimization, downstream_adrs. gz-adr-create Step 0 requires draft-first, one question at a time. The pre-mortem is DONE and operator-ranked -- do not re-ask it.
3. Then scaffold: uv run gz interview adr --from docs/design/adr/ADR-0.39.0-config-surface-interview.json, populate every template section, co-create one OBPI brief per checklist item, and register. The checklist field still reads 'TO BE DECOMPOSED' and must be authored before scaffolding.
4. The ADR's load-bearing requirement is a MECHANICAL fence on the settings and debt boundary, per the operator's pre-mortem ranking. A stated separation is not acceptable as the deliverable.
5. Do NOT migrate more readers. The operator ruled migrate-once-after-the-surface; 49 remain rostered and the ratchet refuses new bypasses meanwhile.

## Pending Work / Open Loops

- ADR-0.39.0 does not exist on disk; only the interview answers file does, and nothing is registered in the ledger for it.
- 49 of 50 readers remain on data/direct_data_reach_grandfather.json. Of those, 43 genuinely read a top-level registry, 2 read data/schemas/ (a class the seam does not cover -- arb/validator.py and governance/frontmatter_coherence.py), and 4 only name data/ in display strings without reading.
- The 56 module constants are rostered shrink-only and entirely untriaged.
- 19 of 48 registries still record no derivation. The fence freezes them; it repairs nothing.
- One cross-surface duplicate is unreconciled: eval_feedback_thresholds.json cluster_min_recurrence = 3 and eval_feedback_cluster_lib.py _DEFAULT_CLUSTER_MIN_RECURRENCE = 3, agreeing by coincidence. Two module-constant pairs DISAGREE with nothing reconciling them: DEFAULT_MAX_OUTPUT_CHARS 4000 against 8000, and DEFAULT_TIMEOUT_SECONDS 30.0 against 3.0.
- Five project-root resolvers exist in src/gzkit. Real, unrepaired, and the reason the seam takes project_root as a parameter. Belongs to Movement F's single-entry-point box.
- Campaign section 5's escape clause is untouched and was named in canon without being closed: 'the standard is not negotiable, the calendar is' reads as licence to move the date forever. The date has now absorbed two enlargements.
- R&D disposition rows 1 and 2 remain funded and unstarted. Row 1 is propose-only; row 2 is GHI #1039 plus the open half of GHI #943.
- Row 17h of the advisory scorecard remains Promotable with four named instances.
- GHI #969 argues its remedy is compromised BECAUSE #889 [settled] reports a defect in it; #889 [settled] closed 2026-09-14. Re-reading #969 against what #889 [settled] landed is still unresolved judgment work.
- Previously tracked and still unselected: the airlock surface under ADR-0.37.0's three Draft briefs, GHI #1063's blocker, scripts/check_proof_freshness.py stdout capture, and skill-support-delivery packaging omitting references/ assets -- which now costs ghi-author's four worked examples on the adopter path.

## Verification Checklist

VERIFIED this session with the command that produced each figure. Dated observations, not a claim that all checks were rerun for this handoff.

- uv run gz check -- exit 0, run eight times across the session on a fully staged tree; last before 5d8219c9a.
- uv run gz validate --config-registry -- exit 0 with all three arms wired (derivation, module constants, direct reach).
- uv run gz validate --waiver-ratchet -- exit 0; 29 registered surfaces.
- Negative controls, each run and observed at exit 3: stripped authority citation; new module constant; a 20th entry in a 19-entry baseline; a new module reaching into data/; a stale roster entry; and the pre-existing undeclared-registry arm.
- 47 tests across tests/test_registries.py, tests/governance/test_config_derivation.py and tests/governance/test_config_registry.py.
- tests/governance/test_active_campaign_registry.py -- 9 pass; the negative control on the REAL supersession fails 2 of 9 at exit 1.
- uv run mkdocs build --strict -- exit 0.
- scripts/session_orientation.py -- resolves the 2026-09-20 edition, checklist 7/30.
- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -- Pending, pre_closeout, closeout BLOCKED, landed count UNCHANGED from session start. Run the verb for the count rather than trusting a figure transcribed here.
- uv run gz obpi lock list -- no active locks. gh issue list --state open -- 56.
- git rev-list --left-right --count origin/main...HEAD -- 0 0, tree clean at 5d8219c9a.
- Detector correction measured: the old direct-reach pattern found 30 modules, the corrected pattern 50 -- a 40% false-negative rate caught before landing.

## Evidence / Artifacts

- docs/governance/build-to-1.0-campaign-2026-09-20.md -- the new Magna Carta edition; full carry-forward, reckoning re-measured, target ~2027-08, Movement F created, ADR-order exception recorded.
- docs/governance/build-to-1.0-campaign-2026-08-16.md -- banner corrected to SUPERSEDED.
- data/active_campaign.json -- the list move that IS the supersession.
- docs/governance/reckoning-2026-09-20-evidence/reckon.py -- re-runnable, carries no literals from its authoring date.
- docs/governance/reckoning-2026-09-20-evidence/README.md -- counting methods, and why scorecard tallies are deliberately not computed there.
- docs/governance/config-derivation-census-2026-09-20.md -- the census record.
- docs/governance/config-derivation-2026-09-20-evidence/census.py -- read-only, three fail-closed asserts.
- docs/governance/config-derivation-2026-09-20-evidence/README.md -- stated bounds.
- docs/governance/config-surface-design-2026-09-20.md -- the design record; all 48 files placed, addressing ruled.
- docs/design/adr/ADR-0.39.0-config-surface-interview.json -- 12 of 19 fields authored.
- src/gzkit/registries.py -- the single read seam.
- src/gzkit/governance/trust_audits/config_derivation.py -- the three fence arms.
- data/config_derivation_grandfather.json -- 19 unsourced registries, shrink-only.
- data/module_constant_grandfather.json -- 56 constants, shrink-only.
- data/direct_data_reach_grandfather.json -- 49 parallel readers, shrink-only.
- data/waiver_ratchet_registry.json -- all three registered.
- tests/test_registries.py -- the seam tests.
- tests/governance/test_config_derivation.py -- the fence tests.
- .gzkit/skills/ghi-author/SKILL.md -- row 4 landed; Step 0 class test and family branch row.
- .gzkit/skills/ghi-triage/SKILL.md -- the family and staleness pass.
- .gzkit/skills/ghi-author/references/examples.md -- extracted at the body ceiling.
- .gzkit/rules/skill-authoring.md -- 0.2.0, clause 6 carries compress-before-lift.
- docs/governance/advisory-rules-audit.md -- row 94c scored Judgment; ledger row moved 0.1.1 to 0.2.0.
- .gzkit/insights/agent-insights.jsonl -- two records: the Step 0 reproduction, and the dodging course-correction.
- Commits: 72dfc1a81, 1e7dc892a, f3c1e446c, 602dfa801, 13a08bd0f, efcf661a2, 55eae6fa1, 2bdf83b25, 52f70db64, 371c524f4, 41604da6d, eb085d076, 5d8219c9a.

## Settled Rulings

986 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
