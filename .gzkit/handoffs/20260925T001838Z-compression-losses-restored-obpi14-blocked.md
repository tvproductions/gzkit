---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-25T00:18:38Z'
agent: claude-code
obpi_id: OBPI-0.35.0-14-meaning-preserving-landing
session_id: 37f9383a-dc69-4071-a582-ea2ee4ba43f3
continues_from: .gzkit/handoffs/20260924T083541Z-three-rulings-landed-integrity-audit-staged.md
---

## Current State Summary

Resumed 20260924T083541Z and worked the test-integrity thread into a control-surface recovery and a new prevention OBPI.

1. The coverage-check GHI was filed as #1090. The audit's "lite warns" finding turned out not to be a runtime defect: the 2026-09-17 diet (GHI #921) dropped the lane scope from the AGENTS.md REQ-coverage line. The line was restored through the corpus at 5d6b9d173.
2. A condition-level sweep of that diet found 33 conditions not carried intact, 23 of them binding. It is recorded at docs/evals/compression-sweep-2026-09-24.md and GHI #1091. Every binding finding is now either restored or was ruled with its drop named:
   - c714b25c6: S02, S03, S10, S11, S13.
   - 90a8b2e9f: S04/S05 full restore of the PRIME DIRECTIVE and the thorough-fix preference; CLAUDE.md tuning now defers to it.
   - 5d892d26a: S06-S08 carried verbatim into gz-adr-create, gz-plan, gz-design, gz-status, gz-airlock, gz-obpi-lock and the token-block rule.
   - 6c6f98dc6 (local, being pushed by this sync): S09, S12, S16, S17.
3. ADR-0.35.0 gained item 14, meaning-preserving landing, sequenced before 07 (9eb84e085). OBPI-0.35.0-14 is in its pipeline, Stage 2, and is BLOCKED (gz obpi block) awaiting an operator ruling.
   - Task 1 (src/gzkit/content/retention.py, the pure retention core) cleared review.
   - Task 2 (the gate inside gz content commit) exhausted its two Stage-2 fix cycles. The quality review accepted all six BEHAVIOR proofs; the closing spec review refuted REQ-02 and REQ-03 for CLI-level proof only.
   - Uncommitted OBPI work (retention.py, commit.py, __init__.py and both test files) is carried by this sync. 80 tests pass in the commit and retention suites.

## Important Context

- The retention gate lives at the promotion seam (gz content commit), not at corpus retirement. The #1090 clause was hand-authored unowned text until 2026-09-17, never a corpus entry. See the ADR-0.35.0 § Intent amendment of 2026-09-24.
- Coverage is meaningful-character, not sentence overlap: every non-whitespace character except markdown markup and the leading list marker must lie inside a condition or non-binding quote. Overlap coverage passed the #1090 loss, and a probe returned [] against it; the brief was corrected to match ADR Decision 10.
- Drop ids must appear in the --attestation-text supplied with THIS commit, never a carried-forward standing attestation. Condition ids are pattern-constrained (^[A-Za-z][A-Za-z0-9_-]{0,15}$) because an empty id matched any text.
- Named residuals (ADR Decision 10, brief Requirement 9):
  - a KEPT span's meaning is not byte-checkable; the commit prints every KEPT pair for the operator, and the Task 4 skill must require the reviewer to verify each pair;
  - a partial IO failure after save_rendition leaves no retention sidecar; this is deferred to OBPI-07's journaled landing;
  - a Layer-2 retention digest would touch ledger_events.py, a registered security surface; this is disclosed, not built.
- Every src/tests edit stales ALL acceptance proofs and reviews for the OBPI (one input digest). Re-prove all six BEHAVIOR REQs with the specs saved in the session scratchpad (prove-01..06.json). Those are session-local, so they must be regenerated from the brief's Change Log and the covering tests.
- Native `claude --print` reviewer runs each leave a session-exit bookmark handoff in .gzkit/handoffs/; 13 were auto-staged this session. Reviewers twice produced envelopes the importer refused (a nested object, then an extra key). The prompt now lists the only admitted keys.
- The haiku and sonnet implementers repeatedly hit the 25-turn subagent limit. Budget resumes, or verify final steps directly.
- The OBPI lock is held (agent claude-code-37f9383a, ttl 1440m, claimed about 2026-09-24T10:20Z), so it expires around 2026-09-25T10:20Z. A resuming session re-claims it or the operator rules.

## Decisions Made

- [operator-ruled] File the coverage-check GHI first (verbatim: "yes, start with the coverage-check GHI").
- [operator-ruled] Reroute #1090 from runtime change to restoring the canon lane scope, after the lane framing (verbatim: "consider the distinction between lite and heavy - we shouldn't be changing behavior with lite"; "external contract/api behavior must be heavy"; "restore: AGENTS.md:134 lost its lane scope in the 2026-09-17 compression. [...]"). This supersedes the earlier "B".
- [operator-ruled] Compression may never lose meaning, and prevention is needed now (verbatim: "the compression process CAN NOT be allowed to lose meaning and intent, a frontier model can, and should, do better."; "This is needed, and NOT for later... NOW!").
- [operator-ruled] Approve the AGENTS.md:134 wording, and add ADR-0.35.0 item 14 ahead of 07 (verbatim: "1 approved, yes to item 14 before 07").
- [operator-ruled] Restore the unruled losses, restore S04/S05, land the sweep with a GHI, and start OBPI-14 (verbatim: "1 restore now, 2 restore, 3 yes, 4 start").
- [operator-ruled] S04/S05 full restore, with DO IT RIGHT #11 and the CLAUDE.md scope line deferring to the PRIME DIRECTIVE (answer: "Full restore (Recommended)").
- [operator-ruled] S06-S08: keep the fa1a52dca placement and carry the rulings into the missing skills (answer: "Add to the missing skills (Recommended)").
- [operator-ruled] Restore the remaining binding findings (verbatim: "restore S09, S12, S16, S17 too").
- [operator-ruled] Continue the OBPI-14 pipeline (verbatim: "keep going with the pipeline").
- [agent-chose] Gate at the rendition delta (gz content commit) over corpus retirement, disclosed in the ADR Intent amendment.
- [agent-chose] Record gz obpi block when Task 2's two-cycle bound was reached, rather than running a third cycle without a ruling.

## Immediate Next Steps

1. Put the OBPI-0.35.0-14 block to the operator: authorize a third Task-2 fix cycle, or rule otherwise. On a ruling, run `uv run gz obpi unblock OBPI-0.35.0-14-meaning-preserving-landing --ruling "<verbatim>" --operator g0`.
2. If authorized, run the Task-2 fix cycle:
   - add two CLI tests, a multi-violation map and an equal/empty extracted_by/mapped_by map, each asserting exit 3, every violation named, and nothing written;
   - add them to the REQ-02/-03 proofs and re-prove all six;
   - run one closing spec+quality round that also re-closes the five open findings (q1-req06-dropped-attested-weak, F-REQ06-success-half-unproven, F-REQ06-covers-misbinding, spec-t2-req02-cli-every-violation-unproven, spec-t2-req03-cli-independence-unproven).
3. Then Task 3 (BDD, features/content_commit_retention.feature) and Task 4 (manpage `### commit` and the gz-content-compose skill with reviewer-verified KEPT pairs; REQ-07). Then Stage 3, Stage 4 with the Codex tier-1 adversary, and Stage 5.
4. Close GHI #1090 through ghi-close, citing 5d6b9d173 (canon restored) and OBPI-0.35.0-14 (prevention).

## Pending Work / Open Loops

- OBPI-0.35.0-14 is BLOCKED at Stage 2. REQ-07 and REQ-08 have no proof yet: REQ-07 is Task 4, and REQ-08 is a STRUCTURAL-FENCE audited at ADR closeout via BI-10.
- GHI #1090 is open (restore landed; closure pending). GHI #1091 is open for prevention only (OBPI-14).
- Advisory, unmapped: split_blocks exceeds the lizard nloc/ccn bands; content_commit_cmd is about 160 lines and enforce_retention takes 6 parameters. xenon C passes.
- Unfiled friction point: native reviewer runs write session-exit bookmark handoffs into this repo (13 this session). This is a GHI candidate if the operator wants one.
- Carried, still unfiled: gz git-sync auto-add stages files another session wrote; scorecard row 37a needs a negative control; whether to author a D-08 finding; the Sonnet tier's frontier scope is unruled; the req-scope-discipline.md:140 citation; the 32768-vs-65536 Codex cap docstring.
- The adopter template src/gzkit/templates/agents.md still carries pre-ADR-0.0.59 REQ-coverage text (sweep limits note).

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0 after the sync, and `git status --short` is clean.
- `uv run gz obpi status OBPI-0.35.0-14-meaning-preserving-landing` shows IN PROGRESS. `uv run gz obpi precomplete OBPI-0.35.0-14-meaning-preserving-landing` reports the block.
- `uv run gz obpi acceptance OBPI-0.35.0-14-meaning-preserving-landing status --stage stage2 --json` lists the REQ-02/-03 spec-review blockers, the five open findings, and REQ-07/-08 missing proof.
- `uv run -m unittest tests.commands.test_content_commit tests.content.test_retention` exits 0 (80 tests).
- `gh issue view 1090` and `gh issue view 1091` both show OPEN.
- `uv run gz validate --advisory-scorecard` exits 0.

## Evidence / Artifacts

- Sweep: `docs/evals/compression-sweep-2026-09-24.md`.
- ADR amendment: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`.
- Brief with Change Log: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md`.
- Plan: `.claude/plans/meaning-preserving-landing-OBPI-0.35.0-14.md`.
- Code: `src/gzkit/content/retention.py`, `src/gzkit/commands/content/commit.py`, `tests/content/test_retention.py`, `tests/commands/test_content_commit.py`.
- Restored canon: `AGENTS.md`, `CLAUDE.md`, `.gzkit/corpus/AGENTS.md.jsonl`, `docs/governance/prime-directive.md`, `.gzkit/rules/token-block-discipline.md`.
- Commits: 5d6b9d173, 9eb84e085, c714b25c6, 90a8b2e9f, 5d892d26a, 6c6f98dc6.
- GHIs: #1090, #1091.
- Predecessor: `.gzkit/handoffs/20260924T083541Z-three-rulings-landed-integrity-audit-staged.md`.

## Settled Rulings

1057 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
