---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-21T11:10:28Z'
agent: claude-code
session_id: b009536d-2026-4b6a-998e-013f23df7b19
continues_from: .gzkit/handoffs/20260921T085736Z-hook-stage-claim-class-repaired-and-witnessed.md
---

## Current State Summary

Ten commits, six GHIs discharged, gate green at real exit 0 on the final tree. The session resumed a handoff, filed GHI #1077 from a premise correction, then worked five carried items to completion. Closed: #1069 (byte-exact test fixtures), #1076 (OBPI citations resolve from the ledger), #1077 (in-gate step cost instrumentation). Resolved without new issues: #1074's two carried notes and #1075's dedup question. Routed, not built: the ADR-0.35.0 stale-launch finding went to #930 as new evidence, because #930 already owns it. HEAD is 5552696af, six commits ahead of origin at the time of writing, clean tree. The headline measurement: gz check runs 62 steps, 167.63s wall, sum 281.40s, and every expensive step was understated by the standalone record it replaced.

## Important Context

THE PREMISE THREE HANDOFFS CARRIED WAS FALSE, AND CORRECTING IT CHANGED THE WORK. The chain said nothing measured which gz check step costs what. A 62-entry measured_seconds record existed the whole time in data/check_step_concurrency.json. It had zero consumers in src/ or tests/, it was produced by running each step ALONE — a protocol the file's own note calls wrong for cost attribution ('Adding step wall-times treats cores as free, and they are not') — and it had decayed with nothing to notice, which is the exact class GHI #903 closed by hand 23 days earlier. So #1077 is not 'add a timer'; it is 'stop hand-maintaining a record that measures the wrong quantity'. VERIFY BY READING THE DATA SURFACE, NOT THE CLI OUTPUT: the absence of a timing print is not the absence of a measurement.

WHAT THE INSTRUMENTATION FOUND ON ITS FIRST RUN. Validate default scopes measures 65.29s in-gate against a recorded 3.22s — 20x out, second-largest step in the sweep, and never identified as expensive by anyone. Test 100.90s vs 31.99s. Docs build 13.94s vs 3.84s. Every top step understated. That also retires the --fast variance the chain could not explain (169s one session, 64.77s another): it was never Test (changed) at 0.67s.

THE CAUSE-TO-TEST TABLE IS THE MOST VALUABLE THING IN ghi-close, AND IT FIRED FIVE TIMES. Every one was an untested branch in code already written, gated green, and reported by me as verified: the open(...,'w') write shape (#1069); obpi_completion=='completed' and the whole repudiated arm (#1076); a raising step's finally accounting and THE OVERLAP LANE — the branch the real gate takes on every run, mocked away by every timing test (#1077). The lesson is mechanical, not moral: 'the gate is green' and 'the family is covered' are different claims, and only the table checks the second. Build it before writing a close comment, and read it for empty right cells.

THE ts FENCE FOUND A LIVE DEFECT, NOT A HYPOTHETICAL. commands/content/unown.py appended its ledger row with ts=record['ts'] — the crash-recovery JOURNAL's stamp, written before the append. On a delayed replay that lands a past-stamped row after newer ones: the descending pair validate_ledger refuses. GHI #1074's original pass missed it because it is a hand-built LedgerEvent, not the default_factory idiom that pass targeted. Nothing read the value (witness_divergence compares extra payload, never the row's ts).

SCOPE BOUNDARIES HELD DELIBERATELY. The #1077 arm is console output only; a duration on QualityResult feeds gz check --json and is a runtime-contract change, left to the arm the operator routes separately. #1069 ships the GHI's stated literal predicate, not a looser one that would flag 8 more sites. #1075 keeps ledger_merge's no-dedup rule — collapsing rows could destroy a genuine event — and ends the SILENCE instead.

## Decisions Made

- [operator-ruled] File Arm 1 of the gate-cost finding as a GHI rather than repairing it unrouted (verbatim: "file arm 1 as ghi").
- [operator-ruled] Work the recommendations on #1076, #1074's notes, #1069 and the skill ceiling in order (verbatim: "proceed, step by step").
- [operator-ruled] Work all five carried items — #1077, the ledger ts fence, #1075's dedup question, the two uncustodied items, and ADR-0.35.0 (verbatim: "do:").
- [operator-ruled] Sync the session's work and update the handoff (verbatim: "update h/o, git sync").
- [agent-chose] Filed #1077 fresh rather than re-opening #903, which closed 23 days ago on the same root cause: #903's Scope hint says 'No src/ change' and it completed that scope in full, so re-opening it would assert its finished work was unfinished.
- [agent-chose] Annotated data/check_step_concurrency.json's _doc as superseded and left all 63 measured_seconds values untouched, rather than overwriting them with in-gate figures — two protocols in one field is the confusion #903 named.
- [agent-chose] Fixed the unown.py stated-ts site rather than allowlisting it: allowlisting would permanently bless the exact defect the fence exists to prevent, and the owning brief resolves attested-complete so a direct fix was the correct route.
- [agent-chose] Resolved #1075 by keeping the no-dedup merge rule and adding DETECTION, because the rule is deliberate doctrine and the measured harm was the silence, not the duplication.
- [agent-chose] Grandfathered the one historical duplicate by content hash instead of deleting it — the ledger is append-only with no delete path and trust-doctrine T2 forbids rewriting closed-evidence history.
- [agent-chose] Added the mechanical evidence to #930 instead of filing a new GHI for the stale launch marker: /ghi-author Step 0 prior-art found #930 already owns that root cause and already names OBPI-0.35.0-08 as its instance.
- [agent-chose] Diagnosed ADR-0.35.0 and stopped short of touching any OBPI machinery, since only the operator initiates OBPI work.

## Immediate Next Steps

1. Rule the ADR arm of handoff citation resolution — option (A) from #1076 [settled]'s blocker comment, now that (C) has shipped. What SETTLED should assert for an ADR: closeout recorded complete, or every child OBPI attested. The OBPI arm resolves from the ledger today and the ADR arm still reads UNKNOWN by deliberate deferral, documented in reference_checker.py.
2. Route Validate default scopes. It measures 65.29s in-gate, is the second-largest step in the sweep, and nobody has looked at it. #1077 [settled] delivered the measurement and deliberately did not optimise anything. Read the insight recorded under scope gzkit.check first.
3. Rule the Arm 2 contract change for gate instrumentation: a duration field on QualityResult (feeds gz check --json) and duration/timestamp in .gzkit/cache/check-verified.json. It is buildable against real numbers now rather than guesses, and it is OBPI-shaped work only the operator initiates.
4. ADR-0.35.0 remains campaign TOPMOST, 7/13, closeout BLOCKED. OBPI-0.35.0-08 reads in_progress solely from a one-way pipeline_launched latch; the lock was released 29 days ago. #930 carries the finding with this session's mechanical evidence. Only the operator can move it.
5. Decide whether the gz-obpi-pipeline skill's Stage 4 (605 lines of a 1710-line body at its ceiling) extracts to references/. Mechanically available and the pattern already ships; the judgment is that Stage 4 is the human-gate ceremony an agent would then fetch rather than read by default.

## Pending Work / Open Loops

DISCHARGED THIS SESSION. #1069 [settled], #1076 [settled] and #1077 [settled] closed with evidence and cause-to-test tables. #1074 [settled]'s second carried note is answered on the issue (the sibling stores do not claim the ledger's ordering invariant) and its first note is built as tests/governance/test_ledger_ts_is_not_stated.py. #1075 [settled]'s dedup question is resolved and the silence is closed.

OPEN, RULED, NOT BUILT. Arm 2 of the gate instrumentation — the QualityResult/--json/receipt duration fields. A runtime-contract change the operator initiates. It is the one piece of #1077 [settled]'s original option-A framing that did not ship, and it is named in #1077 [settled]'s close comment as such.

OPEN ON ONE OPERATOR RULING. The ADR arm of #1076 [settled] — what SETTLED asserts for an ADR citation. #1076 [settled] is closed because (C) shipped in full; the ADR question is a deferral documented in the code, not a tracked open item, so nothing will surface it but this handoff.

CARRIED, NOT MINE TO MOVE. ADR-0.35.0 at 7/13 with closeout BLOCKED, and OBPI-0.35.0-08 stuck on a one-way latch. GHI #930 owns it and now carries the mechanical evidence: pipeline_launched is set at ledger.py:1154 and cleared by nothing, the lock was released 2026-08-23T13:42:46, and TWO OBPIs are in that state (the other is OBPI-0.47.0-02-owasp-chore-runner).

ACCEPTED AND DISCLOSED, NOT A QUEUE ITEM. Commit 84ea8e435 touches tests/ and carries no Task: or Ceremony: trailer. The only remedy is a history rewrite policy forbids, gz validate --commit-trailers does not scan history so no gate is red, and no roster holds it. An insight under scope gzkit.commit-trailers is now its custodian; it previously lived only in a handoff chain that dropped it after one hop.

MEASURED, UNROUTED. A looser #1069 [settled] predicate (read_bytes() against any non-read_bytes() value) flags 8 further sites, several of which read as deliberate negative controls. Whether non-test code carries the same shape is still unmeasured, as #1069 [settled]'s own Known-uncertainties field said.

STILL OPEN, UNTOUCHED BY THIS SESSION. GHI #1069 [settled]'s siblings in the doctrine-declared-without-mechanism family, and the open queue at 55.

## Verification Checklist

Re-run rather than trusting any figure here; these are dated observations of this tree on 2026-09-21, not thresholds.

uv run gz check -> All checks passed, real exit 0, on a fully staged tree. Observed '62 steps, 167.63s wall (sum 281.40s)'. Run three times across the session; two intermediate failures were genuine (ruff format on new test files; xenon rank D on check() after the render was inlined) and were repaired rather than waived — the xenon one by extracting _render_step_results, which is the fix that removes the cause.

Per-suite, each run to completion and its own exit code read: test_check_step_timing 10 tests; test_ledger_ts_is_not_stated 7; test_ledger_duplicate_rows 8; test_handoff_rulings_count 3; test_reference_checker 15; test_test_fixture_line_endings 8. Regression sweeps: test_content_unown 138, ledger suites 354, handoff suites 307, commands 1579, test_validate 53. All exit 0.

MUTATION CONTROLS RUN, NOT ASSUMED. Removing reference_checker's withdrawn arm fails 2 tests; removing its repudiated arm fails 1; moving _run_one's duration assignment out of finally fails 1; each restores green. Reverting GHI #1068's one-line fix makes the line-endings arm fire at tests/test_report_publication.py:53 on Darwin, where the runtime symptom cannot reproduce.

git rev-list --left-right --count origin/main...HEAD -> 0 6 before sync. git status --short -> empty. Open queue counted by gh issue list --state open --limit 200 -> 55.

NOT VERIFIED, AND SHOULD NOT BE RELAYED AS IF IT WERE. Whether Validate default scopes' 65.29s is one dominant scope or many small ones — the step was measured, never opened. Whether the 8 looser-predicate #1069 sites are defects or deliberate controls. Whether non-test code carries the byte-exact-fixture shape.

## Evidence / Artifacts

Commits, HEAD 5552696af: 8b47789eb, f55624e9c, 48aa5f500, aaf5daa3e, f0a6f9899, 937916d20, 1547f0e96, 979bcc12c, fee5088c3, 5552696af.

New tests: `tests/governance/test_check_step_timing.py`, `tests/governance/test_ledger_ts_is_not_stated.py`, `tests/governance/test_ledger_duplicate_rows.py`, `tests/governance/test_handoff_rulings_count.py`, `tests/governance/test_test_fixture_line_endings.py`.

Source changed: `src/gzkit/commands/quality.py`, `src/gzkit/commands/reference_checker.py`, `src/gzkit/governance/trust_audits/cross_platform.py`, `src/gzkit/validate_pkg/ledger_check.py`, `src/gzkit/handoff_api.py`, `src/gzkit/commands/content/unown.py`, `data/check_step_concurrency.json`, `tests/test_validate.py`.

Issues: #1077 filed and closed; #1069 and #1076 closed; comments added to #1074 (ordering answered) and #930 (stale-latch mechanical evidence).

Insights: four records — scopes gzkit.handoff (premise correction), gzkit.skills.gz-obpi-pipeline (ceiling is extraction, not a wall), gzkit.check (Validate default scopes 19x drift), gzkit.commit-trailers (84ea8e435 accepted and disclosed).

Canon read: `docs/governance/build-to-1.0-campaign-2026-09-20.md` section Workflow fronts; `.gzkit/skills/gz-session-handoff/SKILL.md`; `.claude/rules/gh-cli.md`.

Predecessor: `.gzkit/handoffs/20260921T085736Z-hook-stage-claim-class-repaired-and-witnessed.md`, resumed Fresh, with two handoff_resume_decided records booked carrying the operator's verbatim rulings.

## Settled Rulings

1022 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
