---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-31T07:20:21Z'
agent: claude-code
session_id: 7ca90eda-af71-482e-995a-9699cbac14ca
continues_from: .gzkit/handoffs/20261031T013025Z-ro11-specified-three-letter-families.md
---

## Current State Summary

Drydock safe mode, RO-0. This session specified the last two unspecified pieces: RO-13, the two-way mode contract, and RO-5's change order of 2026-10-30, the catalog verbs after entry. Every repair order and change order now has a specification. docs/governance/harbor-ro13-mode-contract.md is new and accepted; RO-5's page gains § Amended 2026-10-31 with tranche 6, accepted. No code landed. The operator renewed the mx-session lease with gz mx renew --attestor g0. The last action, a73c70974, passed the pre-push gz check.

## Important Context

The order of work is now RO-12, RO-11, RO-5 tranche 6, RO-13 foundation F1 to F5, RO-4, RO-6, RO-7, RO-8, RO-13 retrofit R1 to R3. RO-5 stays open across RO-12 and RO-11; tranches 1 to 5 landed and RO-12 keys only on the work-package id. RO-13's foundation is landed by the operator and a working session, not the contractor; the retrofit waits on T0, the default level and interval tables the agent drafts and the operator rules. Reading the code found two gaps in what RO-5 reported landed: gz wp close moves no outcome and the freeze lock does not exist; both are worked in tranche 6. The census's 421 is a dated measure, not the population. Planned verbs need a gz-validate-skip comment or must avoid the full gz-verb form; a comment only covers the next line, so the contract's multi-line bullets were reworded to bare names under the catalog parent. A command recommended to the operator must be run or read in its help first: gz mx renew was given without its required --attestor flag and failed in the operator's hands. Shift turnover: gz obpi lock list shows only mx-session, no tags are hung because the tag-out log does not exist until RO-12, and no work package is commenced, WP-01 having closed 2026-10-29. Workflow fronts: this session worked the adr/obpi campaign front through the drydock; handoff system, ghi triage and new R&D were not worked.

## Decisions Made

- [operator-ruled] RO-13 splits: a foundation tranche after RO-11, the retrofit tranches after RO-8 (verbatim: "c").
- [operator-ruled] One control per distinct check, wherever reached; the entry sits at the implementation and dispatchers inherit it (verbatim: "A").
- [operator-ruled] A control's CLI refusal goes through one named call carrying its control identity; a plain GzCliError stays a usage error (verbatim: "a").
- [operator-ruled] The MX checkpoint is declared as one temporary group entry; the baseline counts its members as having no entry (verbatim: "a").
- [operator-ruled] The operator rules a default level per role; an entry below default comes to the operator, and the QAI inspects the rest (verbatim: "a").
- [operator-ruled] A modification is profound when any fact in the entry stops being true; the control drops to not yet accepted (verbatim: "a").
- [operator-ruled] The retrofit runs code by role, then skills, then rules and the other surfaces (verbatim: "a").
- [operator-ruled] Self-test intervals are defaults per role and kind in JSON; lengthening past a default is on the operator's word (verbatim: "a").
- [operator-ruled] The self-test chore is admitted in the foundation, and gz check re-runs the self-tests of controls a change touches (verbatim: "a").
- [operator-ruled] Lockout is dropped as a mode signal; the tag-out log carries isolation of a surface (verbatim: "A").
- [operator-ruled] The operator and a working session land RO-13's foundation; the drydock contractor lands the retrofit under the kit (verbatim: "A").
- [operator-ruled] harbor-ro13-mode-contract.md and its tranches are accepted as RO-13's specification (verbatim: "i accept").
- [operator-ruled] RO-5's change order lands directly after RO-11, before RO-13's foundation (verbatim: "A").
- [operator-ruled] Outcome moves means lifecycle moves; a REQ's membership change is an edit and a misplaced outcome is withdrawn and re-admitted under a new code (verbatim: "A").
- [operator-ruled] One event records every catalog edit, replayed by the validator against data/catalog (verbatim: "A").
- [operator-ruled] A REQ's revision rises on any change to its statement, criteria or kind, and on nothing else (verbatim: "A").
- [operator-ruled] The freeze lock covers every field of a baselined REQ and the outcome's statement, modules and user_facing, with no expiry (verbatim: "A").
- [operator-ruled] A reopening returns the outcome to designing and unlocks only the named REQs until the new package's freeze (verbatim: "A").
- [operator-ruled] A withdrawal is the terminal state withdrawn, setting retired, allowed only before released (verbatim: "A").
- [operator-ruled] The lifecycle verb is named transition, beside edit, reopen, withdraw and the event catalog_edited (verbatim: "A").
- [operator-ruled] RO-5's § Amended 2026-10-31 and tranche 6 are accepted as the change order's specification (verbatim: "accept").
- [agent-chose] Added to RO-13's F5 the disagreeing --self-test exit codes and the assert-based arm, both disclosed and not separately ruled.
- [agent-chose] Graded the new RO-13 and RO-5 discrepancy lines as blocking return to service, because exit requires every order closed; disclosed, not separately ruled.
- [agent-chose] Removed RO-9 from the contractor brief's order, as it closed 2026-10-29.

## Immediate Next Steps

1. Start RO-12's preconditions as direct fixes, #1273 first, because RO-12 and RO-13's F2 both read the signal it settles; put the MX-signal shape to the operator one question at a time.
2. Ask the operator to look at the Mermaid drawing in the contract, rendered in the docs site or on GitHub; it was never observed rendering.

## Pending Work / Open Loops

- #1200, #1206, #1208, #1028 and #1273 stay open as RO-12 preconditions, with the other reused-part defects its row lists.
- RO-13's T0 tables are undrafted; they are owed before the retrofit, not before the foundation.
- RO-4 ruling 6 against RO-8 ruling 1, the 0.35.0 Release Package membership flagged for review, remains open.
- The orientation hook output is over its 4000-B budget (data/instructions_files_budget.json § injected_hook_text): 4366 B at this session's start.
- The contractor-kit record's disposition row 3 still reads the self-test chore as advise-only; the contract's ruling of 2026-10-31 admits it, and the record is dated so it was left unchanged.

## Verification Checklist

- git status -sb reads main in step with origin/main.
- uv run gz handoff rulings --search withdrawn returns the withdrawal ruling.
- grep -n '^6\. \*\*The catalog verbs' docs/governance/harbor-ro5-work-packages.md shows tranche 6.
- uv run gz validate --cli-alignment reports no unresolved command.
- uv run mkdocs build --strict passes.
- uv run gz obpi lock list shows the mx-session lease live.

## Evidence / Artifacts

- `docs/governance/harbor-ro13-mode-contract.md`
- `docs/governance/harbor-ro5-work-packages.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/harbor-contractor-brief.md`
- `docs/governance/ieee/requirements-model.md`
- Commits bf90fd6a2's successor 0b2d6ff3a through a73c70974 on main.

## Settled Rulings

1887 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
