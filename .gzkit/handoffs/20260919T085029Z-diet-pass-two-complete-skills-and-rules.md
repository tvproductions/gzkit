---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T08:50:29Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260919T073719Z-diet-pass-two-ten-skills-contradictions-over-bytes.md
---

## Current State Summary

Diet pass two of the instructions-files-diet chore (GHI #921) has now covered every skill and every rule. Every change was proposed with a full before/after, ruled by the operator, and landed on main with a full `uv run gz check` on a fully staged tree, then `uv run gz git-sync --apply`. HEAD is `636409447`, level with origin/main, tree clean. No pipeline, OBPI, lock or TASK is active; ADR-0.35.0 is still TOPMOST and Draft.

Landed since the prior handoff: gz-adr-evaluate 6.8.2 (`61f18743b`), gz-obpi-specify 1.9.0 (`cc985aea5`), gz-obpi-sync 3.4.0 as a partial rewrite with its README deleted (`c84ae495d`), gz-plan-audit 6.5.0 (`f1cc8d42b`), ghi-triage 5.2.1 (`ffd920626`), gz-obpi-pipeline 6.59.1, the three-site receipt and handoff-location fix (`574a22133`), gz-design 1.6.0 (`436238239`), an eight-skill stale-pointer batch (`270cc2ab3`), and four rules with their version notes lifted and Coverage Ledger versions set (`7422e33ab`). gz-justify and gz-flighttest were read in full and needed no text change.

Coverage: 19 skills read end to end (18 changed); the other 53 skills and all 24 rules were covered by two mechanical sweeps (known defect classes, and existence of every cited repo path) with each hit read in context, which changed 8 skills and 4 rules. Skill bodies total 672,343 B; rules 144,415 B. The pass's finding stands: the defects were contradictions and stale pointers, and bytes were secondary.

Six GHIs were filed through ghi-author across the pass, authoring only, all OPEN and unselected: #1030, #1031, #1032, #1033, #1034, #1035.

## Important Context

Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts). Handoff system: not inspected this segment beyond the pipeline's Stage 1 now pointing at `.gzkit/handoffs/`; GHI #870 not read. GHI triage: three issues added this segment (#1033, #1034, #1035); the queue was not otherwise read. ADR/OBPI campaign: untouched; ADR-0.35.0 TOPMOST and Draft, no OBPI initiated. New R&D: untouched; #1029 still awaits the operator's route.

What the mechanical sweeps cannot see: an internal contradiction. Every one of the 19 skills read end to end had at least one defect a regex would not find (a step ordering the opposite of a doctrine paragraph, a Trust Model denying a write the verb performs, a procedure hand-building what a verb scaffolds). The 53 swept skills are small, mostly under 5 KB, but they were not read end to end; if one of them misbehaves in use, read it whole before trusting the sweep.

Settled this segment, so the next session does not re-derive it. The plan-audit receipt is `.claude/plans/.plan-audit-receipt-<OBPI-ID>.json`, written by `uv run gz plan audit`; the bare `.plan-audit-receipt.json` is the gate's legacy fallback and nothing writes it. That closes the parked D3 question in both gz-plan-audit and gz-obpi-pipeline. `gz obpi sync` reconciles brief frontmatter FROM ledger-derived state; no skill may mark a brief Completed from test evidence. Gate 5 is every lane; Lite omits Gates 3 and 4 only (three skills had this wrong). Rules DO have frontmatter (`id`, `paths`, `description`, `RuleFrontmatter`, extra forbidden), which is why a rule's version lives in a body comment plus a block quote; bumping a rule means marker, one-sentence note, prior note lifted to `docs/governance/rule-version-history.md`, and the scored-at version set in the Coverage Ledger table of `docs/governance/advisory-rules-audit.md`, or `gz validate --advisory-scorecard` fails closed.

Gotchas met. Removing a skill's only mention of a verb fails the skill-alignment check (Invariant 1): `gz obpi emit-receipt` is wielded only by gz-obpi-sync, so a correct mention had to stay. A post-commit hook (`ledger-commit-locus`) may print Failed with files modified after a rules commit; the commit still lands and the ledger row it writes is picked up by the following git-sync. `gz agent sync` exits 0 while printing Recovery required (GHI #1032): grep its log after deleting any canonical file and `git rm` the mirror copies. The verifier-pipe-gate refuses `gz validate --help` unless it is the last statement. The handoff validator rejects the literal word for a fill-in token as if it were an unfilled marker.

## Decisions Made

- [operator-ruled] gz-adr-evaluate and gz-obpi-specify candidates each landed whole (verbatim, two separate rulings: "A").
- [operator-ruled] gz-obpi-sync rewrite landed; an OBPI whose audit passes but which the ledger does not show completed is reported to the operator and nothing is changed; the skill's README is deleted everywhere (verbatim: "A, D1 A, D2 A, then continue with gz-justify").
- [operator-ruled] gz-plan-audit landed whole and the three pipeline sites were to be proposed at once (verbatim: "A, pipeline D3, then continue with ghi-triage").
- [operator-ruled] ghi-triage and the pipeline D3 fix both landed, and the hook-regex finding was filed as GHI #1033 (verbatim: "A, A, file the GHI, then continue with gz-design").
- [operator-ruled] gz-design landed whole (verbatim: "A, then continue with gz-flighttest, full before/after").
- [operator-ruled] The gz-flighttest delivery finding was filed as GHI #1034, and the remaining skills were to be batched with only changes reported (verbatim: "A, then batch the remaining skills, report only changes").
- [operator-ruled] The eight-skill batch landed, and the small rules were audited next (verbatim: "A, then audit the small rules, full before/after").
- [operator-ruled] The four-rule candidate landed; the adr-audit rule's attestor reads "<attestor-handle>" because rules ship to adopters; the 25 stale numbered citations in runtime messages were filed as GHI #1035 (verbatim: "A, D1 A, D2 yes, then write the successor handoff").
- [agent-chose] Added an eight-line "Receipts are the operator's" paragraph to gz-obpi-sync after the ruling, because removing the wrong emit-receipt instruction orphaned the verb and failed the full check. Told the operator it was text they had not seen.
- [agent-chose] Proposed no change to gz-justify or to gz-flighttest's text; both resolve every pointer and read consistently.
- [agent-chose] Dropped guardrail-feedback-prose.md from the rules candidate: its worked example mirrors a live hook message in src, so fixing the rule alone would move the mismatch. It rides with GHI #1035.
- [agent-chose] Left `uvx xenon` and `uvx radon` in the two pythonic skills and `uvx ty` in gz-arb: the complexity chore and arb.py really run those spellings.
- [agent-chose] Landed literal g0 as the attestor in the gz-adr-audit and gz-obpi-sync skills earlier, then "<attestor-handle>" in the adr-audit rule on the operator's D1-A. The two forms now coexist; GHI #1031 is the place to settle one wording for shipped surfaces.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Ask whether diet pass two is closed for GHI #921, or whether any of the 53 swept skills should be read end to end; name gz-pythonic-pattern-apply (8,988 B), airlineops-parity-scan (8,158 B) and gz-complexity-distill (7,988 B) as the largest unread.
3. Ask which of the six filed GHIs to pull first; #1035 (25 runtime messages citing rule numbers that no longer exist) and #1031 (attestor fill-in wording) both finish work this pass started.
4. Ask for the rulings carried from earlier handoffs: how GHI #1029 proceeds, the parked 17-passage pipeline trim (rebuild it from gz-obpi-pipeline 6.59.1; the receipt-filename question inside it is now settled), and the AGENTS.md destination (OBPI-0.35.0-10 or an ADR-0.0.33 Invariant 1 ruling).
5. When the operator next initiates an OBPI, record its launch, proof and review counts on GHI #1028 against the ADR-0.35.0 figures and close or amend #1028 on that evidence.

## Pending Work / Open Loops

- GHI #1030, #1031, #1032, #1033, #1034, #1035 are open and unselected: eligible work, not blockers.
- GHI #1028 stays open until an operator-initiated OBPI is measured. GHI #1029 awaits a route. GHI #921, #943, #1019, #1023 remain open.
- Whether `docs/governance/GovZero/releases/patch-release.md` should carry the Foundation-skip rule the gz-patch-release skill now states was raised and not ruled.
- Whether gz-adr-audit's manual Step 8 survives a fix to GHI #1015 was raised and not ruled.
- The operator asked whether rules have frontmatter by design; answered yes. If the intent was that a rule's version belongs in frontmatter, that is a `RuleFrontmatter` model change in src and would be a GHI; not filed.
- `docs/governance/attested-req-subject-retirement.md` still says no known instance.
- AGENTS.md is 19,872 B against a 15,000 B budget; closing that needs the operator's destination ruling.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads `0 0` and `git status --short` is empty.
- `git log --oneline -12` shows `636409447` at the head and the nine fix commits named in the summary.
- `uv run gz check > check.log 2>&1; echo "REAL EXIT: $?"` on a fully staged tree exits 0 (last observed before `7422e33ab`).
- `uv run gz obpi lock list` reports no active locks.
- `gh issue view <N> --json state` reports OPEN for 1030 through 1035.
- `grep -c "plan-audit-receipt-<OBPI-ID>" .gzkit/skills/gz-obpi-pipeline/SKILL.md` is at least 2.
- `uv run gz validate --advisory-scorecard > sc.log 2>&1; echo "REAL EXIT: $?"` exits 0 (the four bumped rules match their Coverage Ledger versions).

## Evidence / Artifacts

- `.gzkit/skills/gz-adr-evaluate/SKILL.md`
- `.gzkit/skills/gz-obpi-specify/SKILL.md`
- `.gzkit/skills/gz-obpi-sync/SKILL.md`
- `.gzkit/skills/gz-plan-audit/SKILL.md`
- `.gzkit/skills/ghi-triage/SKILL.md`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- `.gzkit/skills/gz-obpi-pipeline/references/plan-audit-receipt-contract.md`
- `.gzkit/skills/gz-design/SKILL.md`
- `.gzkit/rules/adr-audit.md`
- `.gzkit/rules/gh-cli.md`
- `.gzkit/rules/chores.md`
- `.gzkit/rules/pythonic.md`
- `docs/governance/rule-version-history.md`
- `docs/governance/advisory-rules-audit.md`

## Settled Rulings

936 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
