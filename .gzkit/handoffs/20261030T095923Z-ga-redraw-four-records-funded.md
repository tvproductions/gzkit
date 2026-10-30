---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-30T09:59:23Z'
agent: claude-code
session_id: d1bf8fc2-7f0b-4250-9de4-5c166a4c5f1e
continues_from:
- .gzkit/handoffs/20261030T054212Z-ga-redraw-eleven-rulings.md
- .gzkit/handoffs/20261030T054557Z-session-exit-bookmark.md
---

## Current State Summary

The GA redraw's step 2 to step 5 work ran under RO-0 and ended in a funded R&D run. Step 2 landed: the contract the rails read is the outcome, which gains a `modules` field (229ba2f05); repair orders are repair work packages naming issues, a drift repair under RO-5 rulings 1 and 2 (498328438); the catalog is empty at the handback and RO-8's carry, withdraw and Release Package acts run at civil rule (5d2554113). Step 3 landed: the nine processes and their edges (124582b4d), the general arrangement rewritten as one description with the 2026-10-17 text superseded (bbd11b61d), the drawing as Mermaid source rendered in the browser with no Node (97c803ed2). Step 4 landed: the three-level-brief finding graded due by a named event, holder family H (05c9453eb, corrected in 7f9721e9a), and the five unwitnessed edges graded by owner (7f9721e9a). Step 5 began with RO-11: the catalog-authoring verbs split, RO-11 owning entry and RO-5 the rest (546d46578); intake fixed as admitting a requirement into the catalog, nothing more, its witness the entry verb's unit tests (963f480ea). RO-11's review then opened the packaging question; the operator locked four records (345119ec0), mapped them to the ADR/OBPI system (afa0cc07a) and the R&D run docs/rnd/four-records.md was opened, researched (ten verbatim source files), settled its six open points and was signed off funded (53b0c32b2, names corrected in 46feb727e). Its row 4 landed: the general arrangement and requirements model gain the feature package (6f98736cc). Every commit passed gz check and is pushed. No code changed in this session; mkdocs.yml gained a Mermaid fence.

## Important Context

The four records are the requirements catalog (family.capability.outcome), the feature package (the one new record: catalog outcomes plus the story of why, each outcome in at most one; the mADR's successor), the work package (the OBPI's successor, matching TASKs to REQs) and the release package (the cart for one order, carrying the version). "REQ catalog", "feature pack", "work pack" and "release pack" are the operator's shortenings, never renames; the agent misread them once and the operator had to correct it. The whole is a loosening and renaming of the ADR/OBPI system, not a greenfield. How the operator wants to work, reinforced three times this session: do not frame bounded A/B/C questions while the problem is still undecomposed; spell actions out plainly, never as "row 4"; when the operator's direction already makes a step obvious, do it and report instead of asking. The mx-session lock is listed as held by claude-code-1250b9d4 (the prior session's agent), lease renewed 2026-10-30T05:45Z for 1440 minutes. Shift turnover: no tag is hung, no finding awaits buy-back and no work package is commenced (WP-01 closed 2026-10-29); the tag-out log does not exist yet, so the contract's § List of discrepancies and the lock list were read in its place. The Mermaid drawing in § The general arrangement builds under mkdocs --strict but its rendering was never seen; nothing in a Python-only toolchain parses Mermaid. The remaining ledger.jsonl change is the commit hook's mx_contract_amended rows.

## Decisions Made

- [operator-ruled] The contract the rails read is the outcome, which gains a modules field naming the code paths it owns (verbatim: "A").
- [operator-ruled] The catalog is empty at the handback; the 0.35.0 outcomes enter at civil rule (verbatim: "A").
- [operator-ruled] RO-8 acts 1 to 3 move to civil rule in order; the drydock books the plan and runs act 4 (verbatim: "A").
- [operator-ruled] The brief-bearing processes are nine, transit drawn as a gate (verbatim: "a").
- [operator-ruled] The general arrangement is rewritten in place as one description, the 2026-10-17 text superseded verbatim (verbatim: "A").
- [operator-ruled] The drawing is Mermaid source rendered in the browser, Python only, no Node (verbatim: "no node, python only. option B. again no node,").
- [operator-ruled] The three-level-brief finding is due by a named event, held by a family-H outcome from the handback (verbatim: "A").
- [operator-ruled] Intake's unwitnessed edge blocks under RO-11; session exit, R&D, design acceptance and chore edges are due by a named event (verbatim: "A").
- [operator-ruled] RO-11 owns the entry verb; RO-5 owns the catalog verbs after entry (verbatim: "A").
- [operator-ruled] Intake is admitting a requirement into the catalog, nothing more (verbatim: "yes, it is just admitting/registering a new requirement into the requirements catalog, nothing more.").
- [operator-ruled] Admission is on the operator's word, separate from work selection (verbatim: "yes, admission is on my word.").
- [operator-ruled] The four records are locked as the broader model (verbatim: "yes, those are the four").
- [operator-ruled] The four are named requirements catalog, feature package, work package, release package (verbatim: "no, those were shortenings (surprised I need to be this pedantic): requirements catalog (family.capability.outcome), feature package, work package, release package.").
- [operator-ruled] A feature package lists catalog outcomes plus the story; an outcome sits in at most one, for now; prerequisites are outcome depends_on edges; a human attests its value delivered at the release or work package attestation; the pool stays as intentions (verbatim: "it lists outcomes from the catalog, plus the story", "yes, at most one for now", "yes, it matches", "yes, a human moment to attest the value delivered", "yes, the pool stays as intentions until brought down").
- [operator-ruled] The four-records R&D is funded (verbatim: "read it, fund (req catalog, feature pack, work pack, release pack)").
- [agent-chose] Repaired the repair-order-as-GitHub-issue wording as drift under RO-5 rulings 1 and 2 without a fresh question, since canon already ruled it.

## Immediate Next Steps

1. Put to the operator the open grading question: does the feature package's store and value attestation block return to service, and does RO-4 own it by change order? The agent's reading is yes and RO-4, because RO-8's first civil-rule act turns ADR-0.35.0, an mADR, into the 0.35.0 release package.
2. Finish RO-11's review and rewrite its row once: admission on the operator's word with work selection out of it; drop the stale "the session specifies with the operator after RO-4" and the contractor brief's "not worked … once RO-4 has landed"; correct its bands ("catalog, version"); then name the entry verb.
3. Specify RO-13 with the operator (the 2026-10-29 ruling: every unspecified order is specified now).
4. Ask the operator to look at the Mermaid drawing rendered in the docs site or on GitHub, since its rendering was never observed.

## Pending Work / Open Loops

- The feature-package finding is ungraded (next step 1).
- RO-11's row still carries its 2026-10-25 text about selection and parsing, its stale sequencing and bands; `docs/governance/harbor-contractor-brief.md` still says RO-11 is not worked until RO-4 lands.
- The first-principles list put mid-run was never ratified; it is marked unratified in the R&D review.
- RO-4 and RO-5 code carry the work-package and Release Package names unchanged, which is correct; nothing is to be renamed.
- The three-level-brief line and the four unwitnessed-edge line sit on § List of discrepancies under RO-0, due by a named event.

## Verification Checklist

- `uv run gz obpi lock list` shows the mx-session lock and its holder.
- `git rev-list --left-right --count origin/main...HEAD` reads 0 0 after the sync.
- `uv run gz check` passes on the synced tree.
- `uv run mkdocs build --strict` exits 0, and the built page `site/governance/harbor-pilotage-candidate-2026-10-15/index.html` carries a `pre class="mermaid"` block.
- `uv run gz handoff rulings --search "feature package"` returns this session's rulings.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` — § The general arrangement, § Rulings of 2026-10-30, § List of discrepancies, RO-5, RO-8 and RO-11 rows
- `docs/governance/ieee/requirements-model.md` — records table, § 6, § 8 pointer
- `docs/governance/safe-mode-doctrine.md` — § Records, § The instruments item 3, RO-3 row
- `docs/governance/harbor-ro8-in-flight-work.md` — § Acts amendment
- `docs/governance/harbor-ro5-work-packages.md` and `docs/governance/harbor-ro3-requirements-store.md` — verb ownership amendments
- `data/catalog/outcomes.json` — _doc corrected
- `.gzkit/templates/safe_mode_contract.md` and `src/gzkit/templates/safe_mode_contract.md`
- `mkdocs.yml` — Mermaid custom fence
- `docs/rnd/four-records.md`, `docs/rnd/four-records/review.md` and `docs/rnd/four-records/sources/`
- `.gzkit/handoffs/20261030T054557Z-session-exit-bookmark.md` — folded into this handoff

## Settled Rulings

1854 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
