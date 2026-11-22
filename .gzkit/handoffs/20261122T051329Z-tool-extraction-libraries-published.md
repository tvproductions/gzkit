---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-22T05:13:29Z'
agent: claude-code
session_id: 415a938c-6382-453a-bd6e-da609c47dd86
continues_from: .gzkit/handoffs/20261121T235919Z-rp12-mutation-tool-and-drift.md
---

## Current State Summary

This session continued past handoff 20261121T235919Z and worked its step 2 (the mutation-tool investigation) to an outcome the operator redirected: gzkit's mutation engine and cognitive scorer were extracted as-is into two public libraries and gzkit now depends on them.
- Dependency pass first: uv 0.13.9 and Python 3.14.10 already current; mkdocs-material 9.8.1 to 9.8.2 and eight lock moves (3d03cb4c8).
- tvproductions/gz-mutation-witness (was gzkit.mutation_witness) and tvproductions/gz-mindload (was gzkit.complexity.cognitive): public, set up from gz-starter v0.12.0 (7303deff) for Claude Code, release workflow testing Linux, Windows and macOS then publishing by PyPI trusted publishing. Both published 0.1.0; gz-mutation-witness 0.2.0 followed, judging each nominated test on its own (issue #1, fixed by b6d5090).
- gzkit depends on gz-mindload>=0.1.0 and gz-mutation-witness>=0.2.0 (6225cee5b, f15e21ea0); its two modules and their 54 tests are deleted (carried into the libraries); the instructions name the libraries (0d5c544ec).
- 0d5c544ec broke 44 pipeline tests on main by hand-editing the rendered stage-2 procedure and the attested control inventory; 2f3061dc6 restored them. Full suite 14209 OK on 0.2.0 (receipt arb-step-unittest-83ca960068404a8eac4afc17a63447f9).
- gz-mutation-witness carries a draft PRD-1.0.0 and backlog issues #1 to #13; TI-01 was withdrawn from ADR-pool.test-integrity-tooling and its sections moved verbatim to that project (87725614d).

## Important Context

- CI on f15e21ea0 (run 44987474841) was in progress at authoring. It is the first full CI run carrying both the 2f3061dc6 restore and the 0.2.0 floor; the run on bf8c7c916 failed on the same 41 failures and 3 errors the restore fixed, on Linux and Windows. The local tree passed the full suite and the per-change gate.
- The per-change gz check selects tests by a changed module's stem, so it never reached the pipeline tests the stage-2 edit broke; only a full unit run caught it. Run the full suite after any edit to a skill, rule or data file another surface pins.
- The served stage-2 procedure (.gzkit/skills/gz-obpi-pipeline/references/stage-2-implement.md) is rendered from data/obpi_pipeline_control_inventory.json against a pinned baseline body and pinned digests (OBPI-0.35.0-17, -20); never edit either by hand. It still names gzkit.mutation_witness.run_mutation_sweep, which gzkit no longer ships (insight scope gz-obpi-pipeline).
- The operator's global git identity carries the personal email; both new repositories set user.name g0 and the noreply email locally before their first commit. Any new repository needs the same before committing.
- PyPI's JSON and simple-index pages are CDN-cached: a 404 or a missing version right after an upload can be stale. Query the simple index uncached and install with uv --no-cache before concluding a publish failed.
- commit_witness imports the library's private _run under noqa PLC2701 until gz-mutation-witness exports it (issue #10). The guard canaries stay in gzkit: they bind gzkit's registered claims, ledger and registries.
- The session ran in safe mode under docs/governance/harbor-pilotage-candidate-2026-10-15.md; the mx-session lease was renewed at 2026-11-22T00:13Z for 24h.

## Decisions Made

- [operator-ruled] Commit and push the dependency upgrade without the pending ledger change (verbatim: "commit and push, leave the ledger out").
- [operator-ruled] Renew the lease and take up the handoff (verbatim: "renew the mx-session lease ands let's examine handoff work.").
- [operator-ruled] The internal tool's mistake is the route (verbatim: "that it bypassed the pool ADR's decision").
- [operator-ruled] O2's and O3's Gate 5 stand, booked as RP-12 ruling 200 (verbatim: "they stand; the evidence was valid, the route was wrong.").
- [operator-ruled] The break-outs go as drydock acts, not ADRs (verbatim: "not together and not an ADR - we will NOT perpetuate the old ADR system here. I just need some GSD approaches here.").
- [operator-ruled] The libraries' names (verbatim: "gz-mutation-witness and gz-mindload").
- [operator-ruled] No Co-Authored-By trailer on commits (verbatim: "will you please stop stamping \"co-authored by\" here? it gets old.").
- [operator-ruled] gzkit and other projects consume both as PyPI libraries (verbatim: "they need to migrate as libraries").
- [operator-ruled] Both repositories are public (verbatim: "yes, start step 1 and these are public").
- [operator-ruled] The interim rename to gzkit.mutation.witness was withdrawn before any edit (verbatim: "wait until it is ported").
- [operator-ruled] Withdraw TI-01 and move its sections to the new project (verbatim: "withdraw TI-01 from the pool ADR, keep the rest", "move to new project", "it can use those").
- [operator-ruled] Mutant generation belongs in gz-mutation-witness, by contract with adopters (verbatim: "yes, mutant gen, but in collaboration with adopters (design-by-contract)").
- [operator-ruled] What counts as a kill (verbatim: "judge each nominated test on its own, errors elsewhere don't disqualify").
- [operator-ruled] Implement the kill rule and release it (verbatim: "yes, implement #1 and release 0.2.0").
- [agent-chose] Left the every-branch generator out of the as-is extraction, since gzkit shipped only the engine; issue #11 carries it.
- [agent-chose] Restored the stage-2 procedure, the gz-obpi-pipeline skill version and the control inventory to their prior bytes rather than re-pinning them by hand.

## Immediate Next Steps

1. Read CI run 44987474841 on f15e21ea0 (gh run view 44987474841 --repo tvproductions/gzkit); if any job failed, read its failed log before anything else.
2. Rename the stage-2 procedure's gzkit.mutation_witness.run_mutation_sweep through the control inventory's governed re-baseline and re-render (OBPI-0.35.0-20's path), with the operator's go.
3. Put the gz-mutation-witness backlog to the operator for ordering; #10 [settled] (public runner and copy helper) lets gzkit drop its noqa PLC2701 and its copy code once released.
4. Return to the predecessor handoff's open steps 3 and 4: RP-12 ruling 27 against the drydock doctrine's item 5, and gz check per act, each put to the operator with both texts quoted.

## Pending Work / Open Loops

- gzkit's served stage-2 procedure names a module gzkit no longer ships (insight scope gz-obpi-pipeline).
- gz-mutation-witness issues #2 [settled] to #13 [settled] are open; #1 [settled] is fixed in 0.2.0 and #11 [settled] is decided (generation by contract with adopters, its shape still to design). The PRD-1.0.0 is a draft awaiting the operator's approval.
- gz-starter issue #1 [settled] can now qualify gz-mindload 0.1.0 through the starter's own process.
- O4's survivor triage, dock-trial section, inspection and Gate 5 stay held from the predecessor handoff.
- ADR-pool.test-integrity-tooling keeps TI-02 to TI-05.
- GHI #1337 (gz mx reads a hard-coded ledger path) and GHI #1331 (a timed-out fetch reports stale ahead/behind) remain open from the predecessor.

## Verification Checklist

- gh run view 44987474841 --repo tvproductions/gzkit reads success.
- uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer reads 14209 tests OK.
- uv pip show gz-mutation-witness reads 0.2.0 and uv pip show gz-mindload reads 0.1.0.
- git log -1 --format=%h -- src/gzkit/mutation_witness.py names the commit that deleted it, 6225cee5b.
- gh issue list --repo tvproductions/gz-mutation-witness --state all --limit 20 lists #1 closed and #2 to #13 open.
- uv run gz obpi lock list reads mx-session ACTIVE until the lease lapses near 2026-11-23T00:14Z.

## Evidence / Artifacts

- `pyproject.toml`
- `uv.lock`
- `data/astral_exceptions.json`
- `docs/design/adr/pool/ADR-pool.test-integrity-tooling.md`
- `docs/governance/harbor-ro12-contractor-kit.md`
- `src/gzkit/commit_witness.py`
- `src/gzkit/governance/trust_audits/complexity_ceiling.py`
- `.gzkit/insights/agent-insights.jsonl`
- `artifacts/receipts/arb-step-unittest-83ca960068404a8eac4afc17a63447f9.json`
- `artifacts/receipts/arb-step-unittest-46e66079b7584b84a4112eb3fde86149.json`

## Settled Rulings

2434 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
