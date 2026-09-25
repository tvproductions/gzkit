---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-25T10:46:39Z'
agent: claude-code
session_id: 28544862-05f4-441e-a86e-60582ca93172
continues_from: .gzkit/handoffs/20260925T094609Z-obpi14-completed.md
---

## Current State Summary

OBPI-0.35.0-14-meaning-preserving-landing is attested_completed and synced; Stage 5 finished (gz obpi sync PASS, both git-syncs pushed). The first Stage-5 push was refused by the pre-push gz check on two validators. The completed brief lacked its Step 4b section, which was added. RED parity could not be met for REQ-01/-04/-05 because their production code landed before any working-tree witness ran; the red-parity validator was fixed under GHI #1094 (3f837f2fc) to accept a valid executed acceptance proof as the falsifiability witness. Four GHIs were closed this session: #1094 fixed (3f837f2fc); #1090 fixed (5d6b9d173, canon lane scope restored, with the operator's reversal of ruling B now recorded on the issue); #1095 fixed (7b2427c45, one reply envelope per review with the importer's rules stated); #1096 fixed (7a41f0390, review prompts embed the working set, 1.73 MB down to about 200 KB on OBPI-14's context). origin/main is level with local main. No OBPI lock is held.

## Important Context

Only the operator initiates OBPI pipeline work. The OBPI-14 pipeline was launched by session 37f9383a on 2026-09-24T10:20Z without the operator's explicit initiation; the operator's --from=ceremony run brought it to closure, and this session failed to surface the missing initiation at Stage 1 (recorded as an improvement insight with the operator's words). Stage-2 reviewers now return one gzkit.acceptance.review.v1 envelope; parse_review_result derives the legacy ReviewResult, and verification_gaps is an optional non-governing envelope field. Step 4b renders its reply contract with gzkit.acceptance_context.acceptance_review_frame('adversarial', status_json). Whether live reviewers follow the new single-envelope prompt is unobserved until the next real review round. The gz-obpi-pipeline skill body sits at its 1710-line grandfather ceiling; any growth must compress first. Another concurrent session has uncommitted work under docs/governance/ieee (DISAGREEMENTS.md, OPEN-QUESTIONS.md, README.md, design-candidates.md, design-pivot-session-2026-09-25.md); every commit this session excluded it, and it must stay excluded.

## Decisions Made

- [operator-ruled] Course-correction, verbatim: "i caught you mid pipeline without my explicit execution". An inherited pipeline launch and lock must be confirmed as operator-initiated before building on them.
- [operator-ruled] The pre-push red-parity refusal is repaired, verbatim: "just make this bullshit work. this slop is your fault. do ghi and immediately direct fix this bullshit." (GHI #1094 filed and fixed.)
- [operator-ruled] Verbatim: "close 1090 and file the other two GHIs" (#1090 closed; #1095 and #1096 filed).
- [operator-ruled] Verbatim: "fix 1095 and 1096".
- [agent-chose] #1094 counts a valid executed acceptance proof with at least one killed mutation control as a RED witness, leaving the failure_class none refusal and the void-witness exclusion unchanged.
- [agent-chose] #1095 admits verification_gaps into the acceptance envelope as a non-governing field rather than keeping it forbidden, because reviewers kept placing it there and each placement cost a refused import.
- [agent-chose] #1096 keeps status --json at its documented full history and bounds only what the frame embeds.

## Immediate Next Steps

1. Ask the operator which work to take up next; per ascending ADR order the lowest open work is ADR-0.35.0, and only the operator initiates OBPI work such as OBPI-0.35.0-07.
2. At the next real Stage-2 or Step-4b review round, confirm reviewers return a single importable envelope without a formatting repair, which is the one claim of #1095 [settled] no test can establish.
3. Put Requirement 9's ordinal wording in the OBPI-0.35.0-14 brief (four residuals, mitigations counted first/second/third) to the operator for a ruling.
4. Leave docs/governance/ieee to the session that owns it.

## Pending Work / Open Loops

GHI #1091 (the 23 binding conditions the 2026-09-17 compression dropped) stays open as the family issue. GHI #1092 (commit-locus recorder loses its row under a pre-commit stash) and GHI #1093 (present-evidence runs Demo commands in the live checkout) are open. GHI #1028 (Stage-4 4a/4b loop) is open and cross-linked to #1095 [settled] and #1096 [settled]. The Layer-2 retention digest is deferred (security surface), and the partial-IO sidecar exposure belongs to OBPI-0.35.0-07, whose land must call enforce_retention (BI-10). A stale adversary workspace from an earlier session remains in the macOS temp directory as gz-adversary-OBPI-0.35.0-14-meaning-preserving-landing-4_nj6wjr.

## Verification Checklist

uv run gz obpi status OBPI-0.35.0-14-meaning-preserving-landing
uv run gz obpi lock list
uv run gz validate --red-parity
uv run gz validate --adversarial-validation
uv run -m unittest tests.test_review_reply_contract tests.test_acceptance_context tests.test_red_parity_audit
git rev-list --left-right --count origin/main...HEAD

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/red_parity.py`
- `tests/test_red_parity_audit.py`
- `src/gzkit/acceptance.py`
- `src/gzkit/acceptance_context.py`
- `src/gzkit/pipeline_dispatch.py`
- `tests/test_review_reply_contract.py`
- `tests/test_acceptance_context.py`
- `docs/user/manpages/obpi-acceptance.md`
- `docs/user/manpages/validate.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md`
- Commits: 3f837f2fc (GHI #1094), 7b2427c45 (GHI #1095), 7a41f0390 (GHI #1096)

## Settled Rulings

1064 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
