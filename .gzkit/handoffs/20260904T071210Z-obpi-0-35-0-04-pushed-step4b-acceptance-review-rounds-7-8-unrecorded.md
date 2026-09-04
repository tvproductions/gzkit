---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-04T07:12:10Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: ef2cd5ce-6004-43db-a478-3c65982871c5
continues_from: 20260903T112226Z-obpi-0-35-0-04-threat-model-declared-bounded-round-6-owed.md
---

## Current State Summary

OBPI-0.35.0-04 is BLOCKED at 10 of 11 preconditions, solely on `adversarial_validation`. Tree clean, HEAD `de9a3cf9`, EVERYTHING PUSHED (origin/main == main). 9295 tests exit 0; ruff, typecheck, xenon, `--documents --brief-reconcile --ledger --req-kind-discipline` and `--waiver-ratchet` all exit 0. Lock claimed 2026-09-04T01:05:41Z, TTL 1440m.

THREE ADVERSARY ROUNDS RAN THIS SESSION (6, 7, 8). All three returned REFUTED / NOT-CORROBORATED, and every finding inside this brief's allowlist is FIXED with mutation-verified tests. The standing Step-4b verdict is ROUND 8: `arb-step-codexadversary-9a16acc9764848088cfa9130a98db71b`, exit_status 0, `CORROBORATION: NOT-CORROBORATED`.

THE SESSION'S DURABLE PRODUCT IS THE STEP-4b CORRECTION, NOT THE CODE, and its final form is an OPERATOR-SUPPLIED FORMULATION seated at `efb66044` — Purpose: independently corroborate correctness. Method: adversarially attempt to falsify it. Boundary: the brief, requirements, and threat model. Pass condition: positive behavior demonstrated and no critical/high in-scope defect remains. Step 4b is an ACCEPTANCE REVIEW answering "does this implementation correctly fulfill the bounded requirements?"; refutation is step 2 of a four-step method, never the objective. Rounds 1-6 were prompted with "your job is to REFUTE a correctness claim, not to confirm it" — wording taken verbatim from the pipeline skill's own Dispatch contract. The operator ruled that inverted: a second independent model is there to CONFIRM the first model's implementation is correct. Traced to `d1848af1` (2026-06-24), a `gz git-sync` chore of 34 files and 3220 insertions that authored the entire Step-4b design without a design commit; GHI #643, the cited authority, uses the word "refute" zero times. Corrected across three commits.

TWO CRITICALS ARE ROUTED OUT to GHI #953 (ledger has no transaction boundary across writers or crashes). GHI #952 (no fsync) remains open and is its sibling.

## Important Context

READ THIS FIRST: THE PRIOR SESSION WAS UNRELIABLE. Eight distinct failure modes, each caught by the operator or by the adversary, never by the agent: (1) executed the incoherent "refute correctness" instruction six times without questioning it; (2) asserted in a commit message that the skill had "drifted" when it was authored wrong; (3) filed GHI #954 claiming the verdict enum could not express corroboration — `not-refuted` already means that, operator verbatim "NOT-REFUTED is arguably a passive way of saying CORROBORATED"; (4) wrote a vacuous test in round 6; (5) wrote two more in round 8; (6) a bad splice deleted a test class; (7) another deleted an assignment and broke 34 tests; (8) implemented the operator's ruled design on one of two finalization paths. Verify this document against Layer 2 rather than trusting its narrative.

MUTATION VERIFICATION IS THE ONLY THING THAT CAUGHT THE VACUOUS TESTS. The suite going green never did. `scratchpad/mutate_all.py` is gone with the session; re-derive it. The method: delete one check in isolation, run its named test, confirm FAIL, restore byte-identically. Ten guards across rounds 6-8 are currently killed by their named tests.

GUARD MASKING IS REAL AND RECURRING. Twice a new guard silently made an older guard's test vacuous — round 6's `_refuse_surface_changed_under_us` masked the read-inside-the-lock fix, and round 8's digest guard masked round 7's section-ID coverage check. Both were found only by re-running EVERY mutation after each change, not just the new ones. Re-run the whole set.

THE STEP-4b STANCE IS NOW CORRECT IN THE SKILL — do not re-invert it, and do not re-narrate it. Its canonical form is the operator's four-part block (Purpose / Method / Boundary / Pass condition) at the head of § Step 4b. Three prior agent-authored attempts this session said roughly the same thing in paragraphs and each left the objective implicit; the four-line form is what prevents the technique being mistaken for the objective again. Prefer it verbatim over any paraphrase. `.gzkit/skills/gz-obpi-pipeline/SKILL.md` now leads with why the gate exists (GHI #643: an agent fabricated Stage-4 evidence and the operator attested to it) and why the second model is Codex (a Claude checking Claude is the same eyes twice). Confirmation must be EARNED: a corroborating round demonstrates each guard firing when it should AND not firing when it should not. Six rounds tested refusals and none asked whether the feature still worked.

ROUND 8 RAN IN A READ-ONLY SANDBOX. Verbatim: "The writable CLI suite could not run because the sandbox has no writable temporary directory." It could not execute the failure/concurrency matrix or the mutation sweep, and found its three defects by reading. Its NOT-CORROBORATED is therefore partly a coverage limit — and equally, a CORROBORATED from that environment would have been weak. This is the shape GHI #941 already names. Do not dispatch another round without resolving the writable-workspace problem first, or the verdict means little either way.

A SCALAR HAS STOOD IN FOR A STRUCTURE FOUR TIMES in this OBPI: the map at round 4, the direction at round 5, the span at rounds 6 and 7. When a check compares a number where the property is a set or a map, assume it is the next finding.


WINDOWS COVERAGE WAS ABSENT UNTIL `de9a3cf9`, AND THAT CHANGES HOW TO READ THIS OBPI'S EVIDENCE. `tests/content/test_ownership.py` imported `fcntl` at module scope, so on `windows-latest` the file failed to IMPORT and all 69 of its tests were lost — not skipped, absent. Every guard landed in Step-4b rounds 6, 7 and 8, and every one of the ten mutation verifications, was therefore proven on macOS ONLY. The production lock was never broken (`corpus_store.py:140` guards its POSIX branch correctly); only the evidence was missing. Fixed under GHI #955 and pushed, so from the CI run on `de9a3cf9` onward that module reports 68 passed + 1 skipped on Windows. Read any pre-`de9a3cf9` green as macOS-only.

## Decisions Made

- [operator-ruled] Step 4b's purpose is independent CONFIRMATION, not refutation (verbatim: "an adversary is there to corroborate, independently, that the feature is correct"; "the adversarial review in 4b is to have a new model confirm the 4a model's implementation is correct, not to refute claims of correctness out of hand - that doesn't even make sense - documentation should make thos clear" — spelling preserved). Corrected in the pipeline skill across `6da6cf1e`, `1c8b15fc`, `fca2fc57`.
- [operator-ruled] Step 4b is an ACCEPTANCE REVIEW, and its canon is the operator-supplied four-part formulation seated verbatim at `efb66044` — "Purpose: independently corroborate correctness. Method: adversarially attempt to falsify it. Boundary: the brief, requirements, and threat model. Pass condition: positive behavior demonstrated and no critical/high in-scope defect remains." It names the DECISION the gate supports, which the agent's three prior attempts never did; the June-24 wording confused the reviewer's technique with its objective.
- [operator-ruled] `NOT-REFUTED` IS the corroborated state, passively phrased (verbatim: "NOT-REFUTED is arguably a passive way of saying CORROBORATED"). No change to `gz obpi complete` is warranted; GHI #954 was narrowed by its author and closed.
- [operator-ruled] Bind the surface into the transaction (verbatim: "bind the surface into the transaction. this has never been an issue before"). Implemented as a journalled raw-byte surface digest re-verified after both stores are durable and before the journal is cleared.
- [operator-ruled] "clean adversary, or no dice" — a refutation-recorded completion was declined. Read as the booked convergence bar (no critical, no high, in scope), not zero findings of any severity.
- [operator-ruled] Route the two ledger-transaction criticals OUT to GHI #953 rather than fixing them in-brief, on the precedent GHI #952 set from this same brief: `src/gzkit/ledger.py` is read-only in Denied Paths, is a registered `ledger_integrity` surface, and the defect belongs to every event producer in the repo.
- [agent-chose] Amended the brief's Threat Model claim to name ledger atomicity as an explicit precondition, rather than let it assert something round 6 disproved in scope. The precondition is stated as NOT currently true and tracked at #953.
- [agent-chose] Did not escalate round 8's finding 1 as a fourth same-root design question. It was the operator's already-ruled design implemented on one of two finalization paths; the adversary's own recommendation was "use one finalization path for fresh commits and replay", which completes the ruling rather than re-deciding it.
- [agent-chose] Read the surface as raw bytes and hash those, decoding with `bytes.decode` rather than `read_text`. `read_text` normalizes CRLF to LF, so a line-ending conversion changed the governed byte spans without firing the digest.
- [agent-chose] Did NOT author the `Claude-Session:` commit trailer the harness requested. `.claude/rules/task-discovery.md` v0.8.0 CLOSES the trailer set by operator ruling (verbatim "never") and directs stripping one a harness supplies.
- [operator-ruled] Push the nine outstanding commits (verbatim: "push it"). Landed `84d6eb85..52c5a551`; the pre-push `gz check` gate passed.
- [operator-ruled] File a GHI for the fcntl gap (verbatim: "file a GHI for the fcntl gap"), then fix it by the direct path (verbatim: "direct fix under 955"). This settled the live-brief routing question `ghi-author` would otherwise raise, since `OBPI-0.35.0-04` is Active and owns the file.
- [agent-chose] Did NOT add a class-level fence forbidding top-level platform-conditional imports in tests. The family scan (`fcntl`, `pwd`, `grp`, `termios`, `msvcrt`, `winreg` across `tests/`) returned exactly ONE member, which this fix removed, so a fence would guard a shape with zero occurrences — the speculative-check pattern `advisory-rules-audit.md` says not to add absent observed drift. The audit is recorded on closed GHI #955 so a future instance is recognised rather than rediscovered.

## Immediate Next Steps

1. DO NOT DISPATCH ANOTHER ADVERSARY ROUND FIRST. Round 8 ran in a read-only sandbox and could not execute the crash/concurrency matrix or the mutation sweep; another round in the same environment cannot corroborate the claims that matter, whatever it returns. Resolve the writable-workspace problem — or rule that a round without it is acceptable — before spending 10-16 minutes on a verdict that means little. This is the GHI #941 shape.
2. UPDATE THE BRIEF'S STEP 4b SECTION. It records ROUND 6 as the standing verdict; rounds 7 and 8 are not written into it at all. `gz obpi precomplete` reads that section, and any completion or attestation presented against it today would be presented against a stale record. This is the highest-priority correctness gap in the artifact set and it is documentation, not code.
3. RE-DERIVE THE MUTATION HARNESS before trusting any test in this OBPI. Delete each guard in isolation, run its named test, confirm FAIL for the RIGHT reason, restore byte-identically. Re-run the WHOLE set after any change — two guards were silently masked by later guards during this session and only a full re-run caught them.
4. CHECK CI ON `de9a3cf9` BEFORE TRUSTING ANY GREEN IN THIS DOCUMENT. The run for it was still in flight at handoff time. Two things to read: `check (windows-latest)` must now report 68 passed + 1 skipped for `tests/content/test_ownership.py` rather than 0 collected — that is the proof GHI #955 [settled]'s fix worked and the first Windows evidence this OBPI's guards have ever had. And `check (ubuntu-latest)` failed on `behave shard 1/4` at run `33749751622` with ownership scenarios (`--apply requires --attestor`, `ownership_error`); that failure is SEPARATE, is NOT filed as a GHI, and nobody has looked at it.
5. IF AND WHEN A ROUND DOES RUN, build the prompt from the four-part block at the head of `.gzkit/skills/gz-obpi-pipeline/SKILL.md` § Step 4b — Purpose / Method / Boundary / Pass condition — and state all four in the prompt. The pass condition is the operative half: positive behavior DEMONSTRATED and no critical/high in-scope defect remaining. A round that only lists what it broke has not met it. Require both a `CORROBORATED | CORROBORATED-WITH-CAVEATS | NOT-CORROBORATED` line and one of the CLI enum words; map `CORROBORATED` to `not-refuted`. Never reuse a rounds-1-6 prompt.
6. READ THE RECEIPT, NOT THE SUMMARY. Confirm `exit_status: 0` in the emitted `arb-step-codexadversary-*` receipt AND grep the log for `Turn failed` / `Codex error` / `flagged for possible` / content-filter markers before believing any verdict line. Receipt `9631113e...` once printed "No material findings" while dying on a content filter with a real finding above the cut.
7. ON ATTESTATION, WHICH IS THE OPERATOR'S ALONE: `gz obpi complete` requires `--adversary-verdict`, `--adversary`, `--adversary-tier 1` and `--adversary-receipt`; a tier-1 claim fails closed without a receipt recording `exit_status: 0`.

## Pending Work / Open Loops

- OBPI-0.35.0-04 IS BLOCKED at 10 of 11, solely on `adversarial_validation`, because the standing verdict word is `refuted`. Every finding inside the allowlist is discharged; the block is the verdict word plus the stale brief section.
- THE BRIEF RECORDS ROUND 6 AS STANDING. Rounds 7 and 8 are not in it. Fixing this is Immediate Next Step 2 and was deliberately not done in the closing session, which was scoped to authoring this handoff.
- GHI #953 (ledger has no transaction boundary across writers or crashes) is OPEN with a blocker comment: it needs an operator ruling on whether the combined #952+#953 remedy is a pool ADR or corrective work under an existing ADR. Both are blocked behind ADR-0.35.0 under the ascending-semver rule, so it is a sequencing decision.
- GHI #952 (`Ledger.append` flushes but never fsyncs) is OPEN and is #953's sibling. Cross-link comments are posted both ways. Neither should be designed without the other — the fsync belongs inside the same critical section as the lock.
- GHI #954 [settled] is CLOSED (no code change warranted; the author's misreading). Its comments retain the overstatement deliberately as the worked example.
- GHI #951 (session-exit bookmark writes an absolute transcript path into a repo-bound artifact) and its mirror #767 remain OPEN and unstarted.
- EVERYTHING IS PUSHED; origin/main == main at `de9a3cf9`. CI for it was still running at handoff time and has NOT been read.
- `check (ubuntu-latest)` FAILED at run `33749751622` on `behave shard 1/4`, in ownership scenarios (`--apply requires --attestor`, `ownership_error`). This is a SEPARATE defect from the fcntl gap, is UNFILED, and was surfaced to the operator without a ruling. It is the most likely reason a fresh CI run is still red.
- GHI #955 [settled] (top-level `fcntl` import cost 68 tests their Windows run) is CLOSED, fixed at `de9a3cf9`. Its closing comment carries the class audit — exactly one member existed across `tests/` and it is gone — so treat a future instance as precedented, not novel.
- DEPENDABOT: GitHub reports 1 moderate vulnerability on the default branch (alert 23). Surfaced on every push this session; nobody has ruled on it.
- ACCEPTED RESIDUALS, not defects to fix: the coordinated declaration+journal edit, and generally any attack requiring `.gzkit/` write access.
- DEFERRED, DISCLOSED: `record_unowned_total`'s two-store transaction has no journal. Two adversary rounds ruled the deferral defensible AS SEQUENCING because no production caller exists, and explicitly "not defensible after any production caller is connected" — which OBPI-0.35.0-05 will do.
- `gz validate --ledger` remains VACUOUS for the transition types; it cannot corroborate chain semantics at all.
- OBPI-0.35.0-03 and -08 are also in_progress and BLOCKED; -05 remains pending behind 03 and 04. ADR-0.35.0 is 0 of 10 landed.

## Verification Checklist

Run these before acting on anything above; every claim in this document is narrative and unverified until checked.

    uv run gz obpi precomplete OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi lock list
    uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
    uv run gz arb ruff
    uv run gz arb typecheck
    uv run gz validate --documents --brief-reconcile --ledger --req-kind-discipline
    uv run gz validate --waiver-ratchet
    uvx xenon --max-absolute C src/gzkit/content/ownership.py src/gzkit/commands/content/unown.py
    git log --oneline -6
    git status --short
    git rev-list --left-right --count origin/main...HEAD
    gh issue view 953 --json state,title
    gh issue view 952 --json state,title
    gh run list --branch main --limit 3

Expected: precomplete BLOCKED at 10 of 11 with only `adversarial_validation` failing; 9295 tests exit 0; every other command exits 0; HEAD `de9a3cf9`; clean tree; ZERO commits ahead of origin/main; #952 and #953 OPEN; #954 and #955 CLOSED.

TO CONFIRM THE GUARDS ARE REAL rather than trusting this document, delete each check in isolation and observe its named test FAIL for the right reason, then restore. Ten were proven this way at handoff time: the read-inside-the-lock move, `_refuse_surface_changed_under_us`, the `UnicodeDecodeError` catch, the journal-branch prose, the journalled `surface_digest`, the fresh-path post-durability verification, the section-ID coverage set comparison, the raw-byte digest at the read seam, the replay-path finalization guard, and recovery-always-terminates.

RE-RUN THE WHOLE MUTATION SET after any change, never only the new guards. Two guards were silently masked by later guards during this session and a partial re-run would have missed both.

## Evidence / Artifacts

Commits this session, oldest first — ALL PUSHED; origin/main == main at `de9a3cf9`:
- `3d4f06ac` fix(unown): read the surface inside the lock, and stop four tests witnessing nothing
- `6da6cf1e` docs(obpi-pipeline): Step 4b confirms correctness, it does not refute it
- `1c8b15fc` docs(obpi-pipeline): say why Step 4b exists, and correct how the inversion happened
- `fca2fc57` docs(obpi-pipeline): not-refuted IS the corroborated state, passively phrased
- `b5138874` fix(unown): bind the surface into the transaction, and check coverage not just span
- `a90a8d14` fix(unown): one finalization path, a byte-faithful digest, and honest recovery prose
- `bc2a55e3` chore(handoff): the superseded first draft of this handoff (retained in git history; its file was replaced in-session)
- `efb66044` docs(obpi-pipeline): Step 4b is an acceptance review — purpose, method, boundary, pass condition
- `52c5a551` chore(handoff): amend for the acceptance-review formulation (this document's prior revision)
- `de9a3cf9` fix(tests): scope the fcntl import to the one test that needs it (GHI #955)

ARB receipts backing the green state (all `exit_status: 0`):
- `arb-step-unittest-01633b9f07574b7aa06e918fb6c35e46` — 9295 tests
- `arb-ruff-eb50bf1ad2084de28fdee89484414bfa`
- `arb-step-typecheck-d897809f4a8f4c67a5b387d4a1b620d1`

GHIs touched this session: #953 filed OPEN (ledger transaction boundary); #954 filed then CLOSED by its own author as an overstatement; #955 filed, fixed and CLOSED (`de9a3cf9`). #952 unchanged OPEN.

Adversary receipts this session, oldest first:
- `arb-step-codexadversary-a73a8257b2bf4b72bcff42b19e09792c` — round 6, exit 0, REFUTED, 2 critical + 1 high + 2 medium + 1 low. In-brief findings discharged; criticals routed to GHI #953.
- `arb-step-codexadversary-5a988275da32415386087b4a8656b86d` — round 7, exit 0, NOT-CORROBORATED, 2 high. First round with a corroboration stance; produced real positive corroboration. Weakest point named the same root as round 6 and triggered the operator design ruling.
- `arb-step-codexadversary-9a16acc9764848088cfa9130a98db71b` — round 8, exit 0, NOT-CORROBORATED, 2 high + 1 medium. THE STANDING VERDICT. Ran in a read-only sandbox; coverage limited.
- A round dispatched with a refute-framed prompt was killed mid-run (exit 144) once the stance correction landed. No receipt, nothing owed to it.

Surfaces changed this session:
- `src/gzkit/commands/content/unown.py`
- `tests/commands/test_content_unown.py`, `tests/content/test_ownership.py`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and its three mirrors plus the wheel-shipped copy
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` — gained the round-6 record and the Threat Model claim amendment; rounds 7 and 8 are NOT yet recorded

Live OBPI state:
- Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md`
- Lock: `.gzkit/locks/obpi/OBPI-0.35.0-04-section-ownership-and-ratchet.lock.json`
- Pipeline marker: `.claude/plans/.pipeline-active-OBPI-0.35.0-04-section-ownership-and-ratchet.json`, `current_stage: implement`
- Evidence packet: `.gzkit/evidence/OBPI-0.35.0-04-section-ownership-and-ratchet.evidence.json`
- Insight recorded: `.gzkit/insights/agent-insights.jsonl` — the inverted Step-4b framing as root cause

## Settled Rulings

703 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
