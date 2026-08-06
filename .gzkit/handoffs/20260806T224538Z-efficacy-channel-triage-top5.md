---
mode: CREATE
adr_id: ADR-0.25.0
branch: main
timestamp: '2026-08-06T22:45:38Z'
agent: claude-code
---

## Current State Summary

The operator ruled 'commit, then traige' at session open, then directed the top 5 of the resulting rank. Four landed and one reversed. GHI #533's dead-pointer sweep finished (6298531a7); GHI #594 gained move-not-delete receipt retention (1c947aa5c) and then the efficacy channel (bfa0fe5be); GHI #719's forcing-function alignment landed end to end (8b0a2f32e). GHI #581 was NOT fixed — the proposed deletion would have falsified sealed Gate-5 evidence, and the corrected premise was posted instead. GHI #579 is drafted and posted, not built; the operator has parked all instructions-file budget work until the product stabilizes. gz check exits 0 at 8042 tests. Four commits on main, unpushed at authoring time.

## Important Context

The session's through-line is one defect class the operator named directly: 'these are all defects of design.' gzkit had presence checks (validators) and correctness checks (unit tests) and nothing that asked whether a capability reaches its input. That gap produced three separate findings this session. (1) GHI #581's dead schema is runtime-dead but evidence-live: zero consumers in src/tests/features, yet REQ-0.0.37-03-04 and REQ-0.0.37-08-07 name it as their literal subject on a Validated ADR, so the cure the GHI proposes would have flagged a citation that must stay. (2) ARB's own OBPI-0.25.0-33 reached attested_completed on five criteria — three about the brief's own prose, one asserting the package is PRESENT, one asserting six scenarios exist — with 'Receipts scanned: 0' cited as passing Key Proof. All five still hold while the harvest reads 130 of 3286 receipts. (3) 11 of 32 chores are gated solely on 'uv run -m unittest -q', including memory-hygiene and evidence-integrity-audit, the two the operator is counting on for insight retention. The efficacy channel's reach is deliberately covered/PRESENT rather than covered/eligible: measured against eligible, ARB reports 100 percent, because a consumer that declares most of its store ineligible has narrowed its own denominator rather than succeeded.

## Decisions Made

- [operator-ruled] Work the session as 'commit, then traige' (verbatim), booked via gz handoff decide; advised steps 1, 3 and 4 were recorded set-aside, step 1 because origin/main was already 0/0 and the sync it advised had run before the predecessor handoff's ink dried.
- [operator-ruled] Do the top 5 of the triage list (verbatim: 'let's do the top 5 on the triage list').
- [operator-ruled] Direct fix beats riding the pool ADR where the fix removes or reuses rather than adding a parallel reader (operator: 'pool won't be promoted soon, is direct fix better?'). Applied per-item, which is what caught #581.
- [operator-ruled] Park all instructions-file budget work until the product stabilizes (verbatim: 'don't worry about any instructions file budgets right now, we want the product to stabilize').
- [operator-ruled] No ARB purge until insight retention is solid (verbatim: 'i don't want purges until guaranteed summaries for action-taking remedies are in place'), on the stated ground that 'there is no point in 1/2 measures now unless we are going to solve now'.
- [operator-ruled] Align the forcing-function surfaces as a direct fix (verbatim: 'ALIGN THESE!!!'), characterized by the operator as 'a direct fix for what is a clear defect of misalignment/incomplete implementation'.
- [operator-ruled] Build the efficacy channel (verbatim: 'efficacy channel is right — build it - these are all defects of design').
- [operator-ruled] Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (verbatim: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). This restates canon the operator had already booked; the genuine residual is that a correction never traces BACK to its ADR.
- [agent-chose] Do NOT delete .gzkit/schemas/ledger_events.json. Reversed my own recommendation on reading the surface: two sealed REQs name it, so deletion would falsify attested Gate-5 evidence.
- [agent-chose] Correct data/instructions_files_budget.json by APPENDING a dated entry rather than editing its four historical mentions of the terminal ADR — the file states its own reading convention and each dated entry was true on its date.
- [agent-chose] Forcing-function questions are required=False. check_interview_complete routes missing required fields through _confirm, which has no answer in an agent or CI context and exits 130; it broke 21 tests exactly that way, and gating authoring on a TTY is forbidden by canon.
- [agent-chose] Scope gz arb archive to relocation only, no purge verb, per GHI #594's own routing note that purge needs an operator design conversation.

## Immediate Next Steps

1. Push the four commits: uv run gz git-sync --apply. Unpushed at authoring time; the revision count against origin/main is 4.
2. Build gz validate --chore-criteria-witness — a chore whose acceptance criteria never invoke its own subject fails closed. 11 unambiguous cases measured today, needing a shrink-only ratchet in data/ plus registration in data/waiver_ratchet_registry.json (an unregistered grandfather file fails closed as silent-bypass). This is the general half of the efficacy channel; only the ARB instance landed.
3. Rule on GHI #579's posted recommendation (count binding bullets, additive scope, advisory until ADR-0.35.0 lands) — or leave it parked with the rest of the budget work.
4. Decide whether the correction-to-ADR back-reference gap deserves a durable answer. Canon routes defect repair to GHI direct fix but nothing lets a Validated ADR report what has been corrected under it.

## Pending Work / Open Loops

- The ARB harvest reads 130 of 3286 receipts. The efficacy channel now REPORTS this; nothing yet fixes it. 2265 step receipts and 125 red receipts have no harvester in the codebase at all.
- gz arb purge is unbuilt by operator ruling, pending a solid insight-retention story. The harvest-receipt proposal was drafted and judged thin — correctly, because it designed a ledger for a loop that was never closed.
- 11 of 32 chores are gated solely on the full test suite, so a chore can be declared PASS while never running. arb-pattern-extraction's single logged run is 2026-05-10 and its declared evidence artifact arb-patterns.txt is absent from proofs/.
- GHI #581 and #719 both remain scope of ADR-pool.governance-document-structural-validation. #719's code half landed; its residual question — is forcing_functions legitimate pool-interview content — was answered by aligning the channel, so the pool ADR's claim on it has narrowed.
- The correction-to-ADR back-reference has no mechanism. Carried unruled.
- AGENTS.md renders 33153 B against the codex 32768 B delivery cap. Advisory only, and explicitly parked by the operator this session.
- ARB receipts continue to accumulate (3286 at session end).

## Verification Checklist

- uv run gz check exits 0; the All-checks-passed line is at line 115 of the captured log. Every exit code this session was read from an explicit echo after redirecting to a file — the verifier-pipe-gate hook refused one piped gz arb invocation mid-session and was correct to.
- uv run -m unittest -q reports Ran 8042 tests / OK (26 added across four commits).
- Receipts: arb-ruff-102734f42392479995ea1a99e44ab35a, arb-step-unittest-895738341f34491fb1a6dd93b706b2c9, arb-step-typecheck-b51a39762ee848d28cb23c926ef7d9a8.
- uv run gz cli audit passes 134/134 commands after gz arb archive was added.
- uv run gz arb advise --limit 50 prints the coverage line: read 14 of 3286 items (0%) — TRUNCATED by limit.
- git rev-list --left-right --count origin/main...HEAD returns 4 0 before the sync and must return 0 0 after.

## Evidence / Artifacts

- src/gzkit/efficacy.py — StoreCoverage; reach is covered/present by construction.
- src/gzkit/arb/coverage.py — the store census, deliberately a separate pass from the harvest loop.
- src/gzkit/arb/archive.py — move-not-delete retention; the citation guard protects 951 of 3286 receipts on the live store.
- src/gzkit/cli/helpers/durations.py — the --older-than grammar both retention verbs now derive from.
- src/gzkit/interview.py — the eight forcing-function questions.
- .gzkit/templates/adr.md — the Forcing Functions section (canonical; src/gzkit/templates/adr.md is the derived copy).
- src/gzkit/commands/adr_promote_utils.py — promotion now merges AUTHOR_PROMPTS instead of enumerating template variables by hand.
- docs/user/manpages/arb-archive.md — observed output, not invented.
- data/instructions_files_budget.json — the dated 2026-08-06 entry repointing the EXIT CONDITION.
- tests/test_efficacy.py, tests/arb/test_arb_archive.py, tests/test_forcing_functions_alignment.py — 26 tests added.
- .gzkit/handoffs/20260806T181915Z-exchange-record-deconfliction-763-764.md — the predecessor this supersedes.

## Settled Rulings

- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (operator verbatim 2026-08-06: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). The residual the canon does not cover: a correction never traces back to the ADR it repaired.
