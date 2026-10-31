---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-31T01:30:25Z'
agent: claude-code
session_id: d1bf8fc2-7f0b-4250-9de4-5c166a4c5f1e
continues_from:
- .gzkit/handoffs/20261030T095923Z-ga-redraw-four-records-funded.md
- .gzkit/handoffs/20261030T110751Z-session-exit-bookmark.md
- .gzkit/handoffs/20261030T115550Z-session-exit-bookmark.md
---

## Current State Summary

Drydock safe mode, RO-0, the GA redraw (exit item 11). This session closed advised steps 1 and 2 of the predecessor. The feature package store and value attestation are graded blocking and owned by RO-4 by change order. RO-11 is specified: its row is rewritten once and placed before RO-4, and docs/governance/harbor-ro11-intake.md holds eight rulings and three tranches, accepted by the operator. No code landed: data/catalog/families.json still holds the single letters until RO-11 tranche 1. The last action, 1bf12f5a5, passed gz check and the pre-push gate. The two exit bookmarks of 11:07 and 11:55 are the operator trying a cloud session, whose work (c3a63c36f, the Python floor stated as 3.14+) is already on main; nothing else in them is live.

## Important Context

The work order is now RO-5, RO-12, RO-11, RO-4; RO-12 stays ahead because every order from RO-11 on runs under the contractor kit. Family codes are a fixed three letters, and `RQW` deliberately avoids `REQ` so `REQ1.4` cannot sit beside `REQ-1207`. The general arrangement and the requirements model already use `SES1.4` as the target form while the code still enforces one letter; open list-of-discrepancies lines that say family H, D or M read through the mapping in § Rulings of 2026-10-30, and dated records keep their letters. The mark `Pulled` means bringing a pool entry down has begun, not finished. Planned verbs need a gz-validate-skip command-shape comment on the preceding line, or must avoid the full `gz <verb>` form, or cli-alignment reports them. Pushing can race a cloud session: after a rejected push, reapply onto origin/main and keep the ledger as a union in timestamp order; an interactive git rebase here left a detached state with nothing applied and was aborted. The commit hook appends an mx_contract_amended row after the commit, so stage it and amend once. Operator working style, reinforced this session: ask one question at a time; a choice canon leaves open goes to the operator before it is written; silence is not a ruling.

## Decisions Made

- [operator-ruled] The feature package store and value attestation block return to service, RO-4 owning them by change order (verbatim: "yes, it blocks; RO-4 owns it").
- [operator-ruled] Family codes are a fixed three letters, after observing the one-letter legend "would be constrained to 26 families" (verbatim: "three").
- [operator-ruled] The eleven family codes are AIR, SES, CTL, MNT, PKG, DEC, RQW, GAT, ATT, LED, QUA (verbatim: "yes, those eleven").
- [operator-ruled] RO-11 lands the capability records, the outcome code tightened to three levels and the re-coded legend, by change order (verbatim: "a").
- [operator-ruled] RO-11 lands before RO-4; the order is RO-5, RO-12, RO-11, RO-4 (verbatim: "A").
- [operator-ruled] The entry verb is gz catalog admit (verbatim: "A").
- [operator-ruled] Capability records live in data/catalog/capabilities.json (verbatim: "A").
- [operator-ruled] A capability record is written by its own verb, named gz catalog capability, never as a side effect of admission (verbatim: "A", twice).
- [operator-ruled] The capability store lands empty; each capability is created when its first real outcome needs it (verbatim: "a").
- [operator-ruled] gz validate --catalog refuses an outcome whose capability has no record (verbatim: "a").
- [operator-ruled] The pull stays marked: the first gz catalog admit through the pool door sets the entry status to Pulled (verbatim: "A").
- [operator-ruled] harbor-ro11-intake.md and its three tranches are accepted as the RO-11 specification (verbatim: "yes").
- [agent-chose] Added the entry verb refusing an outcome under a capability with no record, as the consequence of the capability verb ruling; disclosed to the operator, who did not object, and not separately ruled.

## Immediate Next Steps

1. Specify RO-13, the two-way mode contract, with the operator: read its row and docs/rnd/contractor-kit.md first, then put the open questions one at a time, with no draft page unless asked.
2. Ask the operator to look at the Mermaid drawing rendered in the docs site or on GitHub; it was never observed rendering and its example codes changed to SES this session.
3. Ask the operator to renew the mx-session lease, which was past 50% of its TTL at the 2026-10-30T23:32Z restart; `gz mx renew` is operator only.

## Pending Work / Open Loops

- RO-12 and its preconditions remain the next order to land before RO-11; nothing in RO-11 or the feature package change order has begun.
- RO-4 specification carries the feature package change order as ruling 8, with the store place and form, verbs and event names as questions the contractor stops on.
- RO-4 ruling 6 against RO-8 ruling 1, the 0.35.0 Release Package membership flagged for review, remains open.
- The orientation hook output is over its 4000-B budget (`data/instructions_files_budget.json` § injected_hook_text): 4847 B at the last restart.

## Verification Checklist

- `git status -sb` reads main in step with origin/main and clean.
- `uv run gz handoff rulings --search "three"` returns the family-code ruling.
- `grep -n "^| RO-11\|^| RO-4" docs/governance/harbor-pilotage-candidate-2026-10-15.md` shows RO-11 above RO-4.
- `uv run gz validate --cli-alignment` reports no unresolved command.
- `uv run mkdocs build --strict` passes.

## Evidence / Artifacts

- `docs/governance/harbor-ro11-intake.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/harbor-contractor-brief.md`
- `docs/governance/harbor-ro4-release.md`
- `docs/governance/harbor-ro3-requirements-store.md`
- `docs/governance/ieee/requirements-model.md`
- `docs/rnd/four-records.md`
- `.gzkit/insights/agent-insights.jsonl`
- Commits bbce7d1ea through 1bf12f5a5 on main.

## Settled Rulings

1866 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
