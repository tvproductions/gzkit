---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T07:37:19Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260919T004306Z-pipeline-stage4-convergence-and-digest-finding.md
---

## Current State Summary

Diet pass two of the instructions-files-diet chore (GHI #921) continued through ten skills after the pipeline. Every change was proposed with a generated full before/after, ruled by the operator, then landed on main with a full `uv run gz check` (fully staged tree) and `uv run gz git-sync --apply`. HEAD is `73d4269c2`, level with origin/main, tree clean. No pipeline, OBPI, lock or TASK is active; ADR-0.35.0 is still TOPMOST and Draft.

The finding of the pass: in every skill after the pipeline, the headline was a contradiction or a stale pointer, not bytes. Byte savings were small except where narration or a reference block could be lifted. Landed, in order: ghi-close 2.9.0 (`3868c1698`), ghi-author 1.8.0 (`f614801fb`), gz-session-handoff 7.6.0 (`fc3179d15`), gz-adr-closeout-ceremony 7.19.0 (`d91afdc25`), gz-tech-debt-review 1.4.0 (`1184eee97`), gz-adr-audit 6.15.0 with both templates (`b9231acdb`), gz-patch-release 1.11.0 (`44be434fa`), gz-adr-create 6.8.0 then 6.8.1 with the legacy template asset deleted and its user doc rewritten (`d1c520a67`, `a969459d1`), the Self-Escalation block narrowed in seven skills (`2bf05e1b2`), gz-health-audit 1.4.0 with the constellations lifted byte-identical to a reference file (`73d4269c2`). Skill bodies total 675,633 B across 72 skills.

Three GHIs were filed through ghi-author, authoring only, none started: #1030 (gz issue file declares a Step 0 pre-flight that no code or skill carries), #1031 (attestor fill-in tokens in docs, a brief template and gz content remedy strings prompt for a real name), #1032 (agent sync exits 0 while printing Recovery required for stale mirror paths).

## Important Context

Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts). Handoff system: observed this session, gz-session-handoff skill corrected so CREATE drives `gz handoff create`; GHI #870 not inspected. GHI triage: three issues added (#1030, #1031, #1032), queue not otherwise read. ADR/OBPI campaign: untouched; ADR-0.35.0 TOPMOST and Draft, no OBPI initiated. New R&D: untouched; #1029 still awaits the operator's choice of R&D or OBPI.

Method that earned every ruling, and should be kept: read the whole skill; grep tests, features and src for strings that bind it and read each @covers REQ literally; verify every pointer, verb, flag, chore slug, path and quoted sentence against the live tree BEFORE counting bytes; build the candidate in scratch from exact 1-indexed line ranges with an anchor assertion per edit, so untouched lines are byte-identical and moved text is provably identical; send a generated PROPOSAL file (per-edit BEFORE/AFTER, then the unified diff); present A/B/C with a recommendation plus separate D-questions for anything doctrinal; land nothing until ruled. The scratch build harness is not in the repo; it is a 40-line script and is quicker to rewrite than to recover.

Classes of defect found repeatedly, worth checking first in every remaining skill: sentences presented as AGENTS.md quotes that AGENTS.md no longer contains (numbered Prime Directive, Always #13, Never #7, § Local Agent Rules for PII, § Lane behavior); `.claude/rules/` cited where `.gzkit/rules/` is canonical; steps that hand-build what a gz verb scaffolds; a bare `gh issue close` where ghi-close is required; retired commands (`uv run -m unittest -q` for the whole suite, `mkdocs build -q`); foundation offered as a live kind; a state or field table that disagrees with the Pydantic model; mirror-pair MUST and MUST NOT lists.

Gotchas. The verifier-pipe-gate hook refuses any verifier that is piped or not the last statement, including `gz validate --help`; run it alone with `> log 2>&1; echo "REAL EXIT: $?"`. In zsh an unquoted `--include=*.py` fails the glob; quote it. Some skills quote `last_reviewed` and a test pins the string type (gz-justify); preserve the existing quoting when bumping. `gz agent sync control-surfaces` exits 0 even when it prints Recovery required for stale mirror-only paths, so read its output after deleting any canonical asset and `git rm` the mirror copies by hand (GHI #1032). Skill-version rule: minor for a procedure change, patch for wording; `last_reviewed` moves in the same edit.

## Decisions Made

- [operator-ruled] ghi-close candidate landed whole; routing consequence 2 (an OBPI brief authored in-session as a destination) does not conflict with the IRON LAW; dead-letter rule 1 reads feature or pool ADR (verbatim: "A, D1 no conflict, D2 feature or pool ADR").
- [operator-ruled] ghi-author candidate landed whole and the gz issue file pre-flight gap was filed as a GHI, #1030 (verbatim: "A, D1 A").
- [operator-ruled] gz-session-handoff, gz-adr-closeout-ceremony, gz-tech-debt-review and gz-adr-audit candidates each landed whole (verbatim, four separate rulings: "A").
- [operator-ruled] The attestor fill-in-token class was filed as a GHI, #1031 (verbatim: "file the GHI, then continue with gz-patch-release, full before/after").
- [operator-ruled] gz-patch-release landed whole; the Foundation GitHub-release skip keys on the release's own version being 0.0.x, and a foundation-closeout qualifier does not trigger it (verbatim: "A, D1 A").
- [operator-ruled] gz-adr-create landed whole; the Self-Escalation block is narrowed, not removed; the superseded template asset is deleted and the user doc rewritten (verbatim: "A, D1 B, D2 A").
- [operator-ruled] The drafted Self-Escalation wording landed across seven skills, and a GHI was ordered for the sync gap (verbatim: "A, file the GHI, then continue with gz-health-audit").
- [operator-ruled] gz-health-audit took the two quote fixes plus the byte-identical lift of the four constellations to references/constellations.md (verbatim: "B, then write the successor handoff").
- [agent-chose] Filed #1032 narrower than ordered. The premise given to the operator (sync does not prune a deleted asset) was partly wrong: the sync reports the stale paths and prescribes manual removal by design. The defect actually observed is the exit 0 over a Recovery required message. Said so plainly to the operator; withdrawable if the operator disagrees.
- [agent-chose] Left the manual Step 8 receipt procedure in gz-adr-audit unchanged although `gz audit` already emits a validated receipt and attempts the transition; it is a design question tied to open GHI #1015, raised to the operator and not answered.
- [agent-chose] In ghi-close, kept the six examples and the #677 and #771 regression narratives; concrete cases do work that emphasis does not. Cut only restatements of the two doctrines.
- [agent-chose] Used minor bumps for the seven-skill Self-Escalation change after telling the operator to expect patch bumps; the skill-sync rule calls for minor on a procedure change. Reported.
- [agent-chose] In #1031, left the adopter-facing fill-in wording to the fixer: docs/user and the brief template ship to adopters, where g0 is not their identity.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Offer to continue diet pass two with the next skills by size: gz-adr-evaluate (18,028 B), gz-obpi-specify (17,089 B), gz-obpi-sync (14,940 B), gz-justify (14,444 B), gz-plan-audit (14,003 B), ghi-triage (13,618 B). Use the method in Important Context; check the listed defect classes first.
3. Ask whether `docs/governance/GovZero/releases/patch-release.md` should gain the Foundation-skip rule the gz-patch-release skill now carries; the skill names that doc as its authority and the doc is silent on it.
4. Ask for the rulings still carried from the prior handoff: how GHI #1029 proceeds (R&D or toward an OBPI), the parked 17-passage pipeline trim plus the receipt-filename question, and the AGENTS.md destination ruling (OBPI-0.35.0-10 or ADR-0.0.33 Invariant 1).
5. When the operator next initiates an OBPI, record its launch, proof and review counts on GHI #1028 against the ADR-0.35.0 figures and close or amend #1028 on that evidence.

## Pending Work / Open Loops

- Diet pass two: 11 of 72 skill bodies audited (the pipeline's Stage 4 plus ten). 61 remain, all at or under 18,028 B. Rules at or under about 8 KB remain unaudited, `pythonic.md` first.
- GHI #1030, #1031, #1032 are open and unselected: eligible work, not blockers.
- GHI #1028 stays open until an operator-initiated OBPI is measured. GHI #1029 awaits a route. GHI #921, #943, #1019, #1023 remain open.
- Whether gz-adr-audit's manual Step 8 survives a fix to GHI #1015 is unanswered.
- The same real-name class may exist in neutral `<name>` fill-in tokens (about ten sites listed in #1031); whether they are in the class is a judgment left to the fixer.
- `docs/governance/attested-req-subject-retirement.md` still says no known instance, though REQ-0.0.19-04-06 and -05-04 were one this session's predecessor handled.
- AGENTS.md is 19,872 B against a 15,000 B budget; closing that needs the operator's destination ruling.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads `0 0` and `git status --short` is empty.
- `git log --oneline -12` shows `73d4269c2` at the head and the eleven fix(skills) commits named in the summary.
- `uv run gz check > check.log 2>&1; echo "REAL EXIT: $?"` on a fully staged tree exits 0 (last observed at `73d4269c2`).
- `uv run gz obpi lock list` reports no active locks.
- `gh issue view 1030 --json state`, and the same for 1031 and 1032, each report OPEN.
- `wc -c .gzkit/skills/gz-health-audit/SKILL.md` reads 12672, and `.gzkit/skills/gz-health-audit/references/constellations.md` exists.
- `ls .gzkit/skills/gz-adr-create/assets` fails or is empty in canonical and both mirrors.

## Evidence / Artifacts

- `.gzkit/skills/ghi-close/SKILL.md`
- `.gzkit/skills/ghi-author/SKILL.md`
- `.gzkit/skills/gz-session-handoff/SKILL.md`
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
- `.gzkit/skills/gz-tech-debt-review/SKILL.md`
- `.gzkit/skills/gz-adr-audit/SKILL.md`
- `.gzkit/skills/gz-adr-audit/assets/AUDIT.template.md`
- `.gzkit/skills/gz-adr-audit/assets/AUDIT_PLAN.template.md`
- `.gzkit/skills/gz-patch-release/SKILL.md`
- `.gzkit/skills/gz-adr-create/SKILL.md`
- `docs/user/skills/gz-adr-create.md`
- `.gzkit/skills/gz-health-audit/SKILL.md`
- `.gzkit/skills/gz-health-audit/references/constellations.md`
- `.gzkit/chores/instructions-files-diet/proofs/pipeline-skill-trim-proposal-2026-09-18.md`

## Settled Rulings

928 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
