---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T10:00:23Z'
agent: claude-code
session_id: 66ff7d9b-39d7-42b2-bafa-fab50266d15d
continues_from: .gzkit/handoffs/20260919T085029Z-diet-pass-two-complete-skills-and-rules.md
---

## Current State Summary

Diet pass two is closed by operator ruling; GHI #921 stays open because its subject (.gzkit/rules is uncorpused and fans out to the generated AGENTS.md files) is not repaired by wording fixes, and a progress comment on #921 records what landed and what remains. After the predecessor handoff: three more skills were read end to end and fixed (gz-pythonic-pattern-apply 1.1.0 with its chore CHORE.md, a8170a2cc; airlineops-parity-scan 1.2.0, a214128fb; gz-complexity-distill 0.3.2, 222dede4b). Three of the six GHIs the pass filed were then fixed and closed through ghi-close, each on the operator's 'fix #N': #1035 (4b576497d, runtime citations name AGENTS.md sections, not retired rule numbers), #1031 (e4f9e4dc5, attestor fill-in tokens read <attestor-handle>), #1033 (c1201c766, the chat-silence hook follows a backslash-newline; test-first, RED then GREEN). GHI #1036 was filed, authoring only: a configured attestor handle in .gzkit.json. Every commit had a full gz check on a fully staged tree, exit 0. No pipeline, OBPI, lock or TASK is active; ADR-0.35.0 is TOPMOST and Draft.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-08-16.md#workflow-fronts. This session touched only the ghi-triage front (direct GHI repair) and the instruction-surface chore under #921; the handoff, adr/obpi and R&D fronts were not inspected beyond the orientation output. Mapping used for #1035, recovered from the July numbered AGENTS.md at fb4079e84: Never #2 is the ledger-only-through-gz rule, Never #6 the blocking-hook rule, Never #7 completion-evidence-is-the-ledger, Never #8 and #1 Gate 5, Never #10 no --no-verify. The stop-turn lint refusal had cited Never #5, which never governed ending a turn on a red tier; no AGENTS.md sentence does, and the refusal now cites ADR-0.0.70 only. src/gzkit/templates/agents.md still numbers its own rules and cites them consistently, so it is not a member of the #1035 class. For #1031, literal g0 in worked examples is the established form at 20+ shipped sites since #899 and was left; about 38 neutral name tokens were left because they do not name the forbidden value. Hook-script templates under src/gzkit/hooks/scripts are Python inside an outer string: every backslash is doubled and an apostrophe inside a single-quoted rendered string breaks the rendered hook. git stash --staged with a pathspec reverted the whole working tree while leaving the index staged; a gz check run in that state validated HEAD, not the change. Recover with git restore --worktree and rerun. The verifier-pipe-gate hook refuses any shell call where ruff, unittest or gz check is not the last statement; run each verifier alone with its output sent to a log and the exit code echoed. The full gz check takes several minutes and dominated session time.

## Decisions Made

- [operator-ruled] Slate for the predecessor's advised steps, offered by the agent and answered verbatim: "ratified". It set: read the three largest swept skills then close pass two with #921 left open; pull #1035 first, then #1031; #1029 goes to R&D through gz-rnd, operator-invoked; the pipeline trim stays parked until the next operator-initiated OBPI is measured against #1028; the AGENTS.md size destination is OBPI-0.35.0-10 (brief to be re-read before relying on it), not an ADR-0.0.33 Invariant 1 ruling.
- [operator-ruled] Three-skill slate, verbatim: "ratified". gz-pythonic-pattern-apply A with D1-A (the semantics-pinning test must pass before the rewrite and, unchanged, after it); airlineops-parity-scan A; gz-complexity-distill A with D1-B (the 'attests at Gate 5' wording is left, because it agrees with the manpage and is tied to REQ-0.0.27-04-10).
- [operator-ruled] "fix #1035", then on the wording proposal: "ratified" — D1-A drop the AGENTS.md citation from the stop-turn lint refusal and cite ADR-0.0.70; D2-A reword only the now-false phrase in handoff_api; fix the test comments too.
- [operator-ruled] On how rulings are requested, verbatim: "why are not suggesting these for autocomplete here?" Bounded rulings are now presented as clickable options through the harness question tool, recommendation first. Recorded with gz insights remember (improvement, scope operator-dialogue).
- [operator-ruled] #1031 scope, chosen by click: land the name-prompting tokens as <attestor-handle>; leave literal g0 examples and neutral name tokens.
- [operator-ruled] On attestor identity, verbatim: "handle is preferred, but adopters should just configure this. i feel like gzkit is weak on config." Routed by click to a narrow enhancement GHI (#1036); the broad question is named there as an R&D candidate.
- [operator-ruled] On pace, verbatim: "you seem to be getting bogged". Then, by click: write this handoff and stop.
- [agent-chose] In gz-pythonic-pattern-apply, folded a duplicated tests-rule pointer into one after the ruled pointer fix made it repeat.
- [agent-chose] Added docs/governance/governance_runbook.md:701 to the #1031 fix; it carried the same Human Name example outside docs/user. Recorded as a contract amendment in the close comment.
- [agent-chose] In the claim-citation refusal, quoted only the first sentence of the current rule, because the second contains an apostrophe that would break the rendered hook string.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Ask whether to pull #1032 (gz agent sync exits 0 while printing 'Recovery required'). It changes an exit code, so show the intended behavior as a clickable choice before editing; it needs the operator's 'fix #1032'.
3. Offer the design rulings for #1030 (how gz issue file runs a prior-art lookup against a foreign repository) and #1034 (ship gz-flighttest's program files in the wheel, or stop the skill reading them) as clickable options; no code until ruled.
4. Before relying on OBPI-0.35.0-10 as the home for the AGENTS.md size reduction, re-read that brief and report whether it still owns the reduction.
5. When the operator next initiates an OBPI, record its launch, proof and review counts on #1028 against the ADR-0.35.0 figures quoted in #1029, then rebuild the parked pipeline trim from the then-current gz-obpi-pipeline version.

## Pending Work / Open Loops

Open from this pass: #1030, #1032, #1034, #1036. Carried: #1028 awaits measurement; #1029 awaits an operator-invoked gz-rnd run whose first job is to measure how wide a per-obligation dependency set really is; #921 stays open. Seen and not fixed, all recorded on #921: docs/proposals/REPORT-TEMPLATE-airlineops-parity.md line 47 and the mining template line 17 list .github paths gzkit does not have; gz-pythonic-pattern-detect § Reference cites the generated src copies of its chore files; gz-complexity-distill and its manpage say the operator attests at Gate 5 for a distillation re-run while AGENTS.md § Attestation scopes Gate 5 to completed OBPI/ADR work (left by ruling; a correction is one edit across skill, manpage and rule after reading the REQ); 50 swept skills were never read in full. Unruled from earlier handoffs: whether patch-release.md should carry the Foundation-skip rule; whether gz-adr-audit's manual Step 8 survives a fix to #1015; whether a rule's version should live in frontmatter. No standing validator resolves AGENTS.md section citations, so the #1035 [settled] class can recur after a future re-rendering; the advisory-audit promotion freeze applies. The rendition-lineage advisory printed by gz check predates this session and was present in every run.

## Verification Checklist

git status --short prints nothing and git rev-list --left-right --count origin/main...HEAD prints 0 0. gh issue view 1035, 1031 and 1033 each report CLOSED; 1036 reports OPEN. The grep in #1035's close comment returns only the two handoff_api.py comment lines. grep -rniE '<your name>|<human name>|human name/handle' over src/gzkit, docs/user, .gzkit/skills and .gzkit/templates returns nothing. uv run python -m unittest tests.hooks.test_ghi_triage_chat_silence runs 13 tests, OK. uv run gz skill list shows gz-pythonic-pattern-apply 1.1.0, airlineops-parity-scan 1.2.0, gz-complexity-distill 0.3.2, gz-obpi-specify 1.9.1.

## Evidence / Artifacts

`.gzkit/skills/gz-pythonic-pattern-apply/SKILL.md`, `.gzkit/chores/pythonic-design-pattern-application/CHORE.md`, `.gzkit/skills/airlineops-parity-scan/SKILL.md`, `.gzkit/skills/gz-complexity-distill/SKILL.md`, `src/gzkit/hooks/scripts/quality.py`, `src/gzkit/hooks/scripts/ghi.py`, `src/gzkit/commands/content/retire.py`, `.gzkit/rules/guardrail-feedback-prose.md`, `docs/governance/rule-version-history.md`, `tests/hooks/test_ghi_triage_chat_silence.py`, `tests/hooks/test_stop_turn_feedback.py`. Commits a8170a2cc, a214128fb, 222dede4b, 4b576497d, e4f9e4dc5, c1201c766. Issues: tvproductions/gzkit #921 comment 5740718435; #1035, #1031, #1033 close comments; #1036.

## Settled Rulings

944 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
