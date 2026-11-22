---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-22T15:08:21Z'
agent: claude-code
session_id: e870dccc-bfdb-48be-baa8-a327a1e81cb8
continues_from:
- 20261122T133155Z-rp12-o4-trial-inspected-mutation-stopped.md
- 20261122T135246Z-session-exit-bookmark.md
---

## Current State Summary

This session worked GHI #1338 to closure and rewrote one pool ADR under the provider rule the operator ruled while working it, then folded the session-exit bookmark of 2026-11-22T13:52Z.
- GHI #1338 (a bare #N beside another repository's name resolved as gzkit's issue) is fixed at authoring, not in the resolver, by operator ruling. gz-session-handoff § Settled-citation annotation states the rule (d4b1bc0a4, reframed in b08739ea4) and the handoff template carries it (c85ec9714). The skill is 7.9.2, its body 495 lines, and the grandfather ceiling ratcheted from 497 to 495. A spec-reviewer subagent confirmed each pass; the issue closed fixed, with a correction comment carrying the operator's reframing.
- ADR-pool.test-integrity-tooling § Target Scope now states the contract required of any mutation provider (isolation, complete outcomes, no score floor) in place of one provider's documents and issues, with a dated amendment line (6e77c2ec3).
- Two improvement insights booked under scope handoff-citation-resolver.
- gz check passed on every commit and every push passed the pre-push hooks; the extractor and reference-checker tests read 130 OK.

## Important Context

- The provider rule is canon now: a handoff says what gzkit expects of a provider, never its issue numbers or other internals. This handoff follows it, so the predecessor's lines about a provider library's backlog are not carried. gzkit stopped managing that backlog (c2369202d), and the hang-bound defect was passed to the library as a message.
- Predecessor 20261122T133155Z's steps: step 2's gzkit half became GHI #1338, now closed, and its other half went to the provider (c2369202d). Step 3 is withdrawn by the operator's ruling to stop managing that backlog. Steps 1, 4 and 5 carry forward below.
- The committed handoff 20261122T051329Z keeps its false [settled] marks on provider citations as the record of the defect; its successor was corrected before c45eb025b.
- Every push this session again printed "gz check (pre-push gate) Passed" with the drydock open, against the skill's statement that no gz check runs at push there. The contradiction is still untraced.
- gz check reports three guards demoted by the MX hangar (Tautological debt, Validate default scopes, tautological test audit). The default validate scopes, run by hand, show only the two OBPI-0.39.0 sensitivity findings that GHI #1189 tracks.
- The advisory rendition-lineage line naming NCSurface.md/root is the QC negative control in src/gzkit/governance/trust_audits/_qc_negative_controls.py firing on purpose, not a defect.
- Shift turnover, hangar open: gz wp tag show --all reads no tag issued; gz wp runs reads no work package in flight; findings awaiting buy-back are read from the contract's § List of discrepancies (unchanged this session) and gz obpi lock list (mx-session ACTIVE, 893 of 1440 minutes elapsed at about 2026-11-22T14:45Z). The buy-back record is not built.

## Decisions Made

- [operator-ruled] Work GHI #1338 (verbatim: "giz ghi 1338").
- [operator-ruled] gzkit learns nothing about other repositories, ruling out a committed list, sibling-clone discovery and a prose heuristic (verbatim: "we don't want to mention another repo's internals").
- [operator-ruled] The fix states the rule at authoring (verbatim: "yes, that's what I meant - we should just say what we expect from a provider.").
- [operator-ruled] The framing of the rule as an unwitnessed hazard is rejected (verbatim: "this is garbage", and "attaching ourselves to the inner dependencies and development schedule of an outside library seems asinine to me.").
- [operator-ruled] Close GHI #1338 once the review confirms (verbatim: "close it when the review confirms").
- [operator-ruled] Rewrite the pool ADR's provider line as a generic contract (verbatim: "yes, rewrite it, but do not reference the dependency by its title, we make it generic and abstracted to the contract desired from any provider").
- [operator-ruled] Fold the session-exit bookmark into a handoff (verbatim: "fold the bookmark into a handoff").
- [agent-chose] Kept the false [settled] marks in the committed handoff 20261122T051329Z as the defect's record rather than editing a committed handoff.
- [agent-chose] Compressed the Settled-citation section and ratcheted the gz-session-handoff body ceiling to 495 rather than raising it.
- [agent-chose] Left the gz-skills#1 examples in handoff_api.py and the tests: they are the glued-form guard's fixtures, not citations of a provider's backlog.

## Immediate Next Steps

1. Put O4's Gate 5 to the operator under ruling 165; its dock trial is recorded and inspected, its residue on the contract's list of discrepancies.
2. Renew the mx-session lease through the gz-mx skill before it lapses near 2026-11-23T00:14Z, if the next session runs past it.
3. Trace whether the pre-push gz check runs in the drydock, and correct whichever of the hook or the gz-session-handoff skill text is stale.
4. Ask the operator whether the false [settled] marks in the committed handoff 20261122T051329Z are corrected or kept as the defect's record.

## Pending Work / Open Loops

- The contract's list of discrepancies carries five O4 lines due by the sea trial: unnamed killers in the record, log.py's stale entry, the flaky test_wp_entry body-alone test, the path-length-fragile test_wp_run test, and a kill that depends on the working directory.
- Four new hexagon test findings (test_mx_renew, test_state, two in test_wp_entry) join ruling 104's line under ruling 125.
- The inspection's notes left untouched: the discrepancy verb's own guards unswept, task 3's schema change taking no mutant.
- OBPI-0.35.0-20 reads PENDING; its completion attestation must name reworded rows S2-062, S2-064, S2-067, S2-074 and S2-080.
- GHI #1337 (gz mx reads a hard-coded ledger path) and GHI #1331 (a timed-out fetch reports stale ahead/behind) stay open.
- 38 chores read overdue in the session orientation; the board announces and never gates.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz obpi lock list reads mx-session ACTIVE.
- gh issue view 1338 --json state reads CLOSED.
- .gzkit/skills/gz-session-handoff/SKILL.md § Settled-citation annotation carries "Cite only this repository's issues" and reads skill-version 7.9.2.
- uv run gz skill audit reports gz-session-handoff within the fixed grandfather ceiling 495.
- docs/design/adr/pool/ADR-pool.test-integrity-tooling.md names no provider library and carries the 2026-11-22 amendment line.

## Evidence / Artifacts

- `.gzkit/skills/gz-session-handoff/SKILL.md` — the provider rule, skill 7.9.2 (d4b1bc0a4, b08739ea4)
- `.gzkit/skills/gz-session-handoff/assets/handoff-template.md` — Pending Work comment carries the rule (c85ec9714)
- `src/gzkit/skill_body_grandfather.json` — gz-session-handoff ceiling 495
- `src/gzkit/handoff_api.py` — the glued repo#N guard's comment
- `docs/design/adr/pool/ADR-pool.test-integrity-tooling.md` — the provider-neutral mutation contract (6e77c2ec3)
- `.gzkit/insights/agent-insights.jsonl` — two improvement records, scope handoff-citation-resolver
- `.gzkit/handoffs/20261122T135246Z-session-exit-bookmark.md` — the bookmark this handoff folds
- GHI #1338 — closure contract amendment, review verdicts, close and correction comments

## Settled Rulings

2453 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
