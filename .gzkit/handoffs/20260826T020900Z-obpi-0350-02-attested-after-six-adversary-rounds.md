---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-08-26T02:09:00Z'
agent: claude-code-6d83a4ac
obpi_id: OBPI-0.35.0-02-content-withdraw-verb
continues_from: 20260825T084800Z-obpi-0350-02-adversary-refuted-three-rounds.md
---

## Current State Summary

OBPI-0.35.0-02-content-withdraw-verb is ATTESTED COMPLETED (attestor g0, 2026-08-26), verified at Layer 2: gz obpi status reports attested_completed and gz adr status shows it completed under ADR-0.35.0. The session resumed the brief at Stage 4 carrying a standing 3x REFUTED verdict, ran six further ARB-receipted tier-1 cross-vendor adversarial rounds (Codex, rounds 4-9), and closed or routed ~25 findings. The round-9 verdict is REFUTED and is recorded as STANDING on the adversarial_validation event, not overturned: the operator authorized round 9 as the final round and attested on that evidence with the refutation in view. Full uv run gz check passes all 56 checks, exit 0; tests 8850. Work committed as feat(content-retire) plus a gz git-sync chore and pushed to origin/main.

## Important Context

The through-line across all ~25 findings was ONE shape: a check that looks like it binds a requirement and does not. Invisible Hangul fillers passing a letter-category test; tests banning yesterday's literal instead of asserting semantics; a ledger event recording target.tier as a proxy for the liveness delta the gate actually reads; a manpage guard comparing three cherry-picked phrases rather than the real CLI line. Two repairs each replaced one false claim with a different false claim before the four-state delta framing stuck. Eleven implementer subagent dispatches stalled at a ~25 tool-use ceiling, always immediately before returning a result block, so later repairs were authored inline by the orchestrator and Stage-2 dispatch is DECLARED SINGLE-DRIVER with a recorded reason. Two same-day canon rules were found mutually unsatisfiable: the operator directive making the Codex plugin the only tier-1 dispatch surface, and a gate proving tier-1 from the ARB receipt argv[0], which for a plugin dispatch is node. Obeying the directive made a tier-1 claim structurally unclaimable.

## Decisions Made

- [operator-ruled] Widen REQ-0.35.0-02-01's Given clause to the name-plausibility floor rather than mint a ninth REQ; REQ count stays 8.
- [operator-ruled] Amend OBPI-0.35.0-08's allowlist to declare retire.py, the cross-brief drift this OBPI's module-level test import caused and could not repair from inside its own transaction contract.
- [operator-ruled] Widen this brief's allowlist to corpus_entry.json so all three reachable homes of the shrink-only claim are repaired in one commit.
- [operator-ruled] The UCD drift witness WARNS at runtime and asserts HARD only in CI; requires-python stays >=3.13. A witness must fail where someone can act on it.
- [operator-ruled] Rekey REQ-0.35.0-02-03 from the target's tier to the invariant-liveness delta; third of four REQs migrated the same way.
- [operator-ruled] Record the liveness delta on the corpus_entry_retired event (floor_direction, floor_moved_ids) as optional backward-compatible fields.
- [operator-ruled] Land the RECORDING half of the ledger witness and route ENFORCEMENT to a GHI; conditional validator rules are a shared-validator capability, not a defect repair.
- [operator-ruled] Run round 9 as the FINAL adversarial round and route whatever it finds rather than looping further.
- [operator-ruled] Override the security floor with an HONEST reason naming the unfilled canonical scan slot, explicitly NOT claiming the change is non-security-relevant.
- [operator-ruled] Fix the tier-1 argv scan to look one hop past a runtime wrapper, and file the rule conflict as its own GHI.
- [operator-ruled] attest completed - Gate 5 for OBPI-0.35.0-02, given with the standing REFUTED verdict in view.
- [agent-chose] Substituted mutation testing for gz arb red, which returned the weak error class on all seven BEHAVIOR REQs because the test module cannot import at base HEAD.
- [agent-chose] Reopened GHI #863 rather than filing a duplicate, per ghi-author Step 0 same-root-cause rule.
- [agent-chose] Strengthened the manpage transcript guard unprompted after finding it had stayed green through real drift.

## Immediate Next Steps

1. Work OBPI-0.35.0-03-retire-duplicate-invariant-entries, which depends on this brief and is the next unlanded item under ADR-0.35.0.
2. Rule on GHI #884 - the tier-1 argv conflict is repaired in-tree but the doctrine collision between the plugin directive and the argv[0] proof deserves an operator disposition.
3. Rule on GHI #882 - whether the ledger validator should gain conditional rules so a gate's own condition can be asserted, or whether recording-without-enforcement is the accepted posture.
4. Consider routing GHIs #875, #880 and #881 together - three defects in corpus_store.append_entry (ordering, concurrency, atomicity) that one atomic-replace repair would close.
5. Investigate the implementer subagent stall pattern - eleven dispatches stopped at a ~25 tool-use ceiling immediately before returning their result block, which forced single-driver authoring on a heavy-lane security-sensitivity brief.

## Pending Work / Open Loops

OBPI-0.35.0-08-remember-post-append-advisory is in_progress under the same ADR and its allowlist was amended by this session. Five GHIs are open and routed out of this brief: #863 (reopened - a fourth home of the shrink-only claim in corpus.py, a Denied Path), #881 (append_entry truncates before writing), #882 (validator has no conditional rules), #883 (the two canonical ledger readers disagree on null and array item types), #884 (tier-1 proof reads argv[0]). Disclosed residuals recorded in the brief: the CHANGED floor delta is unreachable through the CLI because supersedes has no CLI flag and is tested at the helper boundary; the ledger records the delta but cannot enforce attestation on it; legacy-format corpus rows normalize on append. Stage-2 dispatch is declared SINGLE-DRIVER - the two-stage review ran on the early Task-1/Task-2 work but not on the later adversary-driven repairs.

## Verification Checklist

uv run gz obpi status OBPI-0.35.0-02-content-withdraw-verb -> Runtime State ATTESTED COMPLETED, Proof State recorded, Attestation State recorded. uv run gz check -> all 56 checks passed, exit 0. uv run gz obpi sync OBPI-0.35.0-02-content-withdraw-verb -> PASS, runtime state and proof evidence coherent. uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> OBPI 02 attested_completed, closeout completed. uv run gz obpi lock list -> No active locks. uv run -m unittest tests.commands.test_content_retire -> 56 tests OK. git rev-list --left-right --count origin/main...HEAD to confirm the push landed.

## Evidence / Artifacts

docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md, src/gzkit/commands/content/retire.py, src/gzkit/commands/content/__init__.py, src/gzkit/commands/obpi_complete_adversarial.py, src/gzkit/events.py, src/gzkit/ledger_events.py, src/gzkit/schemas/ledger.json, src/gzkit/schemas/corpus_entry.json, tests/commands/test_content_retire.py, tests/test_adversarial_validation_gate.py, docs/user/manpages/content.md, .gzkit/locks/exchange/20260826T020149Z-OBPI-0.35.0-02-content-withdraw-verb-complete.md

## Settled Rulings

515 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
