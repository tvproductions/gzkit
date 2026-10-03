## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

OBPI: `OBPI-0.35.0-08-remember-post-append-advisory` (parent `ADR-0.35.0-canon-entry-corpus-landing`, checklist item 8, lane Heavy). Tree: `main` at `90f6f6aff`, uncommitted. Step 4b has run twice: round 1 refuted, the work was repaired, and round 2 accepted on the repaired tree. Every proof, quality receipt and current review below is post-repair.

**1. Value Narrative**

Before: an append with `gz content remember` leaves every committed, routed rendition of the surface stale, and the advisory that reported it cited only the failing gates and pointed at a per-consumer `compose` + `commit` recovery (brief, pre-landed table, REQ-0.35.0-08-04 row; GHI #654 names the original defect as the silence). Now: after such an append the operator is told which consumers drifted, why (the corpus->rendition seam, ADR-0.0.37 § Decision Re-Alignment), and the one attested `gz content land <surface>` command that recovers. The append is never refused and the exit code stays 0, including when the advisory itself cannot be written.

**2. Key Proof**

The brief's `## Demo`, both commands, in order. The replay tool runs them in its own disposable copy; do not run the first line in the working repository (it appends to the real corpus). Pasted lines are the stable ones from the evidence generator's Demo run on the current tree (generated 2026-10-03T08:32:43Z, both commands `ran: true`, `exit_status: 0`). The entry id, landing id and fingerprints are left out because they change per run.

```bash
$ uv run gz content remember AGENTS.md --section behavior-rules --text "Advisory demonstration entry." --tier compressible
Warning: this append drifted 1 committed rendition(s) of 'AGENTS.md'
  (root). They no longer derive from the current corpus,
  Why: the corpus->rendition seam (ADR-0.0.37 § Decision Re-Alignment). The
    uv run gz content land AGENTS.md \
        --attestor <handle> --attestation-text "<the operator's verbatim words>"
$ uv run gz content land AGENTS.md --attestor g0 --attestation-text "demo corpus delta attested" --dry-run
Surface: AGENTS.md
Attestation: g0 -- supplied on this invocation
Consumers: root
```

Executed proof record for the advisory's three parts: `proof-9547d290ab01499f969af47e274b81e3` (REQ-0.35.0-08-04), two covering tests, baseline green, five substitutions each killed on an assertion, restored green.

**3. Evidence**

**Quality checks:**

All six receipts are under `artifacts/receipts/`, record `commit 90f6f6aff`, `dirty: true`, and `exit_status: 0`. Counts are taken from the receipts.

| Check | Command | Result |
|---|---|---|
| Lint | `uv run gz arb ruff` | exit 0, `findings_total: 0` — `arb-ruff-beeb7f3446134fdd8d54c639fa57a6bc` |
| Typecheck | `uv run gz arb typecheck` | exit 0, `All checks passed!` — `arb-step-typecheck-99ecd388c77c46e2a1aa13afb68eec9b` |
| Unit suite (Gate 2) | ARB unittest | exit 0, 11407 tests, `OK (skipped=7)` — `arb-step-unittest-c4592cebdbf84d95902c8fb71f253af5` |
| Docs (Gate 3) | ARB mkdocs | exit 0, strict build completed — `arb-step-mkdocs-d2c1b207d90044a59557adfbb618846d` |
| BDD, this OBPI's tags (Gate 4) | ARB behave (tags) | exit 0, 3 scenarios passed, 0 failed, 453 skipped; 27 steps passed — `arb-step-behave-178ac5a438fb4d8db9f00195520f34cf` |
| BDD, both content features (Gate 4) | ARB behave (features) | exit 0, 20 scenarios passed, 0 failed, 0 skipped; 140 steps passed — `arb-step-behave-b9ae23437ab347ccb163176bb3bde746` |

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.35.0-08-04,@REQ-0.35.0-08-05 features/
uv run gz arb step --name behave -- uv run -m behave features/content_remember.feature features/content_land.feature
```

The typecheck receipt records its step command as `uv run ty check . --exclude features`. The two modules holding this OBPI's covering tests, run now:

```bash
$ uv run -m unittest tests.commands.test_content_remember tests.commands.test_content_retire
OK
```

**Files created:**

None under `src/`, `tests/`, `features/` or `docs/user/` (`git status` shows no untracked file there).

**Files modified:**

| File | Change |
|---|---|
| `src/gzkit/commands/content/_drift.py` | Advisory prose: seam named and cited, next step is `uv run gz content land <surface>` with `--attestor` and `--attestation-text`; compose + commit lines removed; prose assembly moved to `_advisory_lines`. Step 4b repairs: emission is guarded for `OSError` and `ValueError`; the surface in the printed command is shell-quoted with `shlex.quote`; the docstring no longer says a retirement can only shrink the floor |
| `tests/commands/test_content_remember.py` | Covering tests added for REQ-04, REQ-02 (OSError arm) and REQ-06; premise guards on REQ-01 and REQ-02; REQ-05 and REQ-03 assertions repointed from `compose` to `land`; `unittest.main()` block moved to the end of the module. Step 4b repairs: `test_advisory_output_fault_never_costs_the_exit_code` (REQ-01) and `test_printed_command_quotes_a_surface_name_containing_a_space` (REQ-04) added; the rendition-seeding helper takes a `surface=` parameter |
| `tests/commands/test_content_retire.py` | Imports `gzkit.ledger` first so the module loads when run alone. Step 4b repair: the REQ-08 test routes a consumer named `alpha` through a vendor manifest |
| `features/content_remember.feature` | Three scenarios added: two tagged `@REQ-0.35.0-08-04`, one tagged `@REQ-0.35.0-08-05` |
| `features/steps/content_remember_steps.py` | Five local steps for those scenarios |
| `docs/user/manpages/content.md` | `remember` gains a "Post-append advisory" section with captured output. It states the two Step 4b behaviours and that the quoting is POSIX-shell quoting |
| `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md` | Brief: Change Log, pre-landed table updates, `## Demo` corrections |

`git diff --stat -- src tests features docs/user/manpages/content.md`: 6 files, 525 insertions, 51 deletions.

Also modified in the working tree and not part of the diff above: `.gzkit/ledger.jsonl`, `.gzkit/insights/agent-insights.jsonl`, `docs/governance/GovZero/adr-status.md`, two files under `.claude/plans/`, and the parent ADR file, whose frontmatter `status` reads `Accepted` against `Draft` at HEAD. The parent ADR file is not in this brief's allowlist and no agent edited it: `gz obpi pipeline` wrote that change when this OBPI was launched ("ADR ... accepted: OBPI work started (Draft -> Proposed -> Accepted)"), which is the operator-ruled behaviour of GHI #1014 (commit `bf346ea73`, rulings 2026-09-28). The launch does not regenerate the derived status index, so `tests.governance.test_standing_taxonomy_gate` failed in the first full-suite run of this pipeline (`arb-step-unittest-a16cd6a27b54488ab01daccd50bf30c9`, exit 1, that one test); `uv run gz register-adrs` regenerated `docs/governance/GovZero/adr-status.md` and the suite has passed since. That gap in the launch is recorded with `gz insights remember`, as is the campaign plan's now-stale 2026-08-12 "Draft holds" paragraph.

**REQ coverage:**

Every proof below is the current proof for its REQ, is recorded `valid`, and carries the same input digest as the acceptance status snapshot (`c419563ac956...`). For the seven behavior proofs the record shows baseline green, each substitution killed with failure class `assertion`, and the restored source green with sha256 `60c07586...`, which is the sha256 of `src/gzkit/commands/content/_drift.py` on disk now. "remember tests" is `tests/commands/test_content_remember.py::TestContentRememberDriftWarning`; "retire tests" is `tests/commands/test_content_retire.py::TestContentRetireDriftWarning`.

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|---|---|---|---|---|---|
| REQ-0.35.0-08-01 | behavior | `@covers` tests (2) | remember tests, `test_append_survives_and_exit_stays_0_when_the_advisory_fires` and `test_advisory_output_fault_never_costs_the_exit_code` | `proof-1f116ca277574ed2bbdf906307bc7496`. Killed: `advisory-becomes-a-refusal` and `emission-fault-not-guarded`, each by its own test. Establishes that with the advisory firing the entry is in the corpus and the exit is 0, and that an `OSError` while writing the advisory does not change the exit. Limit: the emission handler's `ValueError` arm has no covering assertion, and the output-fault test does not itself assert the failing sink was reached (disclosures 13 and 16). | Pass |
| REQ-0.35.0-08-02 | behavior | `@covers` tests (2) | remember tests, `test_malformed_sidecar_never_costs_the_append_or_the_exit_code` and `test_drift_detection_raising_oserror_never_costs_the_append_or_the_exit_code` | `proof-a5f25a0926d441328bd7f4280b854a45`. Killed: `handler-drops-oserror` and `handler-drops-valueerror`, each by its own test. Establishes that either exception from drift detection leaves the append and exit 0 intact. Limit: the OSError arm was observed on macOS only. | Pass |
| REQ-0.35.0-08-03 | behavior | `@covers` tests (2) | remember tests and retire tests, `test_warns_naming_the_routed_consumer_not_the_retained_record` | `proof-1c979ee611ef496195fc90a5fc69d65a`. Killed: `enumerate-by-private-glob-copy`, failing both tests. Establishes that the routed consumer is counted and named and the off-route record is not. | Pass |
| REQ-0.35.0-08-04 | behavior | `@covers` tests (2) | remember tests, `test_advisory_names_drift_cites_the_seam_and_gives_a_runnable_land` and `test_printed_command_quotes_a_surface_name_containing_a_space` | `proof-9547d290ab01499f969af47e274b81e3`. Killed: `seam-paraphrased-not-cited`, `next-step-verb-is-not-a-registered-verb`, `next-step-flag-is-not-a-registered-flag`, `attestation-flags-dropped-from-the-printed-command`, `surface-not-shell-quoted`. Establishes the named consumer, the cited seam, that the printed command passes the real parser as `content land` with both attestation flags, and that a surface name containing a space arrives as one argument. Limit: the unit fixtures stop before the attestation check, so no unit test shows a landing complete; recovery by the printed command is shown by the Gate 4 scenario "the attested landing command the advisory prints recovers the drift it announced" in `features/content_remember.feature`, for a name without a space. | Pass |
| REQ-0.35.0-08-05 | behavior | `@covers` test | remember tests, `test_silent_when_no_rendition_has_been_committed` | `proof-7ade2e4d390b409fb0116ef02d1ab3a8`. Killed: `advisory-fires-with-nothing-drifted`. Establishes that a surface with no committed rendition gets no advisory markers in the combined output. Limit: says nothing about which stream. | Pass |
| REQ-0.35.0-08-06 | behavior | `@covers` test | remember tests, `test_corpus_row_is_byte_identical_with_and_without_drift` | `proof-94904e70c9da46ffb451b1384265dfed`. Killed: `advisory-alters-the-corpus-row`. Establishes byte-identical corpus rows and equal exit codes across paired fixtures on one frozen clock. Limit: RED witness is `none`; sensitivity rests on this killed substitution only. | Pass |
| REQ-0.35.0-08-07 | structural-fence | Parent ADR `## Boundary Invariants` entry | `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`, `## Boundary Invariants`, BI-06 ("*Proves REQ-0.35.0-08-07.*") | `proof-b6f42fc4faa7450896927d62d2bf49c5`. Resolver `gzkit.req_kind_fence.resolve_fence_proof`, result `pass`. Establishes that the anchor exists and names this REQ. Limit: the fence itself is audited at ADR closeout, not here; sibling OBPIs were not audited. | Anchor present; audit deferred to ADR closeout |
| REQ-0.35.0-08-08 | behavior | `@covers` test | retire tests, `test_advisory_names_exactly_what_the_gates_grade` | `proof-cf544cc39eb24d418596b74d0fd55788`. Killed: `enumerate-by-private-glob-copy` and `enumerate-by-hard-coded-consumer-name`. The second is the substitution the Step 4b reviewer showed surviving before the fixture routed a consumer named `alpha`. Establishes that the advisory names exactly the set `is_graded_rendition` grades. | Pass |

RED witnesses (latest per REQ, under `artifacts/receipts/`):

| REQ | Receipt | Failure class | Base |
|---|---|---|---|
| 01 | `arb-red-REQ-0.35.0-08-01-825948abf3d340f69e50f43c571d0701` | error | reconstructed |
| 02 | `arb-red-REQ-0.35.0-08-02-5e9ce1ec30bd4f1cb0472e868df233de` | error | reconstructed |
| 03 | `arb-red-REQ-0.35.0-08-03-2ae61e3621b44b10b59f1cbf7bf68da2` | error | reconstructed |
| 04 | `arb-red-REQ-0.35.0-08-04-0d662fbdf42a46778b8081cacd771647` | assertion (both covering tests) | working-tree |
| 05 | `arb-red-REQ-0.35.0-08-05-977a5b7c71ef4d219b81efe98c92716c` | error | reconstructed |
| 06 | `arb-red-REQ-0.35.0-08-06-5816a21034f749cfb44dc0875732aed7` | none | working-tree |
| 08 | `arb-red-REQ-0.35.0-08-08-91f40ebb4e5745d79f7d2532cf955934` | error | reconstructed |

In each `error` receipt the output is `ModuleNotFoundError: No module named 'gzkit.git_spawn_boundary'` raised from `tests/__init__.py` in the reconstructed base, so the covering tests did not run there.

**Reviews.** Twelve are imported: ten Stage-2 (five rounds, spec and quality, all tier 2) and two Step 4b rounds (tier 1).

- Stage-2 round 1: quality `arb-step-qualityreview-76c995ef5bdf4968934b19c8c19aa1ab` was `refuted` on REQ-0.35.0-08-04 (finding `QR-0.35.0-08-04-printed-land-invocation-refused-in-firing-state`: the advisory printed bare `gz content land <surface>`, which landing refuses in the state the advisory fires). Repair: the printed command carries `--attestor` and `--attestation-text` (brief Change Log).
- Step 4b round 1: Codex, tier 1, receipt `arb-step-codexadversary-c811f6d7391a45ca9b339d772f89b0db`, verdict `refuted`, 7 of the 8 then-current proofs approved (the REQ-0.35.0-08-01 proof was withheld). It executed: it replayed all eleven then-recorded substitutions and ran the Demo, both test modules and both features in a disposable checkout. Two mapped findings:
  - `AR-0.35.0-08-01-advisory-write-error-changes-exit` (REQ-0.35.0-08-01): with a stderr sink raising `OSError` while the advisory was written, `remember` exited 1 after the row was durable, and the same sink without drift exited 0. Repair: emission is guarded for `OSError` and `ValueError`; covering test `test_advisory_output_fault_never_costs_the_exit_code`.
  - `AR-0.35.0-08-04-unquoted-surface-breaks-printed-command` (REQ-0.35.0-08-04): for a surface named `Land Surface.md` the printed command split into two arguments and exited 2 (`unrecognized arguments: Surface.md`), while the same surface passed as one argument exited 0. Repair: the printed command uses `shlex.quote(surface)`; covering test `test_printed_command_quotes_a_surface_name_containing_a_space`.
- Stage-2 round 5 (current pair): spec `arb-step-specreview-dacab557598a422d9233afd45ad0a2df` and quality `arb-step-qualityreview-18e3f5de23da4a8a9a8201508d4c601a`, both `accepted`, both on the current input digest, each accepting all 8 current proofs and each recording three closures: the two Step 4b findings and the round-1 REQ-04 finding. They closed them by reading; neither re-ran the Step 4b counterexamples against the repaired tree.
- Step 4b round 2: a focused follow-up by the same cross-vendor reviewer (Codex, tier 1), on the current input digest. Verdict `accepted`; its verdict lines are `CORROBORATED-WITH-CAVEATS` / `not-refuted`. All 8 current proofs approved. It executed on the repaired tree in a disposable checkout:
  - all 14 recorded substitutions replayed, each killed by its nominated assertion and restored byte-identically; REQ-07 has no substitution, and its fence resolver was run and returned `pass`;
  - both test modules (79 tests, OK), both features (20 scenarios passed, 0 failed), and both Demo commands (exit 0);
  - its own two round-1 counterexamples re-run, both now passing: the advisory output fault exits 0 with one durable row, and the printed command for `Land Surface.md` exits 0 with the name as one argument and all three sidecars fresh;
  - three closures against the current proofs: `AR-0.35.0-08-01-advisory-write-error-changes-exit` (`proof-1f116ca277574ed2bbdf906307bc7496`), `AR-0.35.0-08-04-unquoted-surface-breaks-printed-command` and `QR-0.35.0-08-04-printed-land-invocation-refused-in-firing-state` (both `proof-9547d290ab01499f969af47e274b81e3`);
  - three unmapped observations it keeps open as non-blocking: its execution limits and weakest point (disclosures 7 and 16), the out-of-scope drift (disclosure 8), and the success-line and ledger output faults (disclosure 15).
- Two receipts carry round 2 (brief Change Log, "Step 4b round 2"). `arb-step-codexadversary-532836277d0e409db476f5300dd499ab` is the executed review; the importer refused it because three unmapped observations reused finding ids from earlier rounds with different text. The reviewer's own thread was resumed and re-issued the same object with new ids for those three and the statement "No judgment changed": `arb-step-codexadversary-786f351877904100a29553682a505316`, which is the imported record. The Change Log says every other field was compared and is identical; this packet did not repeat that comparison.

The acceptance status reports `ready: true`, no blockers and no open findings.

**Limits and disclosures**

1. No test proves the advisory goes to stderr only. Both runners merge stdout and stderr, and the clause was struck from REQ-05 and REQ-06 by operator ruling on 2026-08-24. The Step 4b reviewer observed the split once, in round 1 on the pre-repair tree, by redirecting the Demo's stdout and stderr to separate files: the `Appended corpus entry` line on stdout, the advisory on stderr. The emission code was changed after that observation, and no record shows the split on the repaired tree: round 2 pasted the Demo output without stream labels. The manpage states "It goes to **stderr**".
2. REQ-06's RED witness is `none`: no production change was needed because the property already held. Its sensitivity rests on the one killed substitution in its executed proof.
3. The RED witnesses for REQ-01, 02, 03, 05 and 08 are inconclusive (import error on a reconstructed base), not REDs. Their sensitivity rests on their executed proofs. Only REQ-04 has an assertion-class RED.
4. No REQ-04 unit test carries a landing: both stop at the parser and the handler's first refusal. Recovery by the printed command is shown by the Gate 4 scenario, on a three-consumer fixture project, not on `AGENTS.md`. For a surface name containing a space, a completed landing was observed only by the Step 4b round-2 reviewer's probe on a three-consumer fixture (`PRINTED COMMAND exit= 0`, `Land Surface.md` as one argument, all three sidecars fresh); no test in the repository carries that landing. The Demo's second command is a dry run: it shows the attested landing accepted, not written.
5. The Demo's exit codes do not witness the advisory: `remember` exits 0 with or without it. The advisory is visible in the Demo's captured output and proven by the REQ-04 and REQ-05 tests (round-4 spec review, finding `SR-0.35.0-08-demo-exit-status-does-not-witness-the-advisory`, non-blocking).
6. REQ-07 (structural fence) is audited at ADR closeout, not here.
7. Step 4b has run twice. Round 1 refuted with two mapped findings; both were repaired. Round 2 accepted and closed them by execution. The acceptance status now reports `ready: true` with no blockers, and the evidence generator (2026-10-03T09:10:09Z) reports `attestable: true` with no blockers. The round-2 reviewer states what it could NOT confirm:
    - no execution on Windows/cmd.exe or Linux, and none on an actual full disk; it ran on macOS and injected the exception types;
    - it did not re-run whole-project lint, typecheck or docs, and did not confirm the whole-project quality receipts;
    - no completed landing of `AGENTS.md` (the Demo's second command is a dry run); completed landings were verified only on the three-consumer fixtures, including `Land Surface.md`;
    - the cross-decomposition no-refusal audit is ADR closeout's; no sibling-OBPI audit is claimed;
    - it retained the supplied input digest and did not recompute it.
8. Five items outside this brief's Allowed Paths were found and recorded for an operator routing ruling, not repaired: the `gz-content-remember` skill still shows the compose, advise, commit chain; `docs/user/runbook.md` still says a retirement implies no recomposition; the `gzkit.ledger_events` import cycle (worked around in one test module, not fixed); the rendition-freshness gate's recovery message and `retire`'s floor-direction prose still say recompose and re-attest; the brief's frontmatter `allowlist` omits `src/gzkit/core/attestor_names.py`. The brief says four were recorded with `gz insights remember` and the fifth is noted in the brief only. The Step 4b reviewer confirmed all five in both rounds; they remain.
9. Two corrections were made to the brief's own `## Demo` during this run (dated note, 2026-10-03): the landing line gained `--attestor` and `--attestation-text`, and the `gz validate --rendition-freshness` line was removed because it exits 3 by design after the append.
10. No Stage-2 review executed anything (tool grant Read, Glob, Grep); their approvals rest on reading the files, the recorded proof evidence and the receipts. The only reviewer that executed is the Step 4b reviewer: round 1 against the pre-repair tree, round 2 against the repaired tree. The round-5 reviewers were not supplied the post-repair full-suite, typecheck, docs or BDD records.
11. The six quality receipts are timestamped 08:25Z to 08:32Z and carry no tree digest that ties them to the current input digest. By file modification time, each postdates the last change to the files it checks: source, test and feature files were last modified by 08:24Z, and the manpage at 08:32:06Z, before the docs receipt at 08:32:36Z.
12. The scoped BDD receipt's stdout tail is truncated ahead of the `content_remember` scenarios: it shows the count (3 passed) and the tag selector, not the scenario names.
13. Round-5 review notes are carried unrepaired; none is mapped to a REQ (brief Change Log, round-5 entry):
    - the emission handler's `ValueError` arm has no covering assertion, and `test_advisory_output_fault_never_costs_the_exit_code` does not assert the failing sink was reached; its reach is shown by the killed `emission-fault-not-guarded` substitution and by the Step 4b round-2 probe (disclosure 16), not by the test itself;
    - `sys.stdout.flush()` shares the emission `try`, so a stdout fault also drops an advisory that stderr could have delivered (confirmed by execution in Step 4b round 2: exit 0, advisory not delivered);
    - `tests/commands/test_content_retire.py` keeps a docstring saying retirement only ever shrinks the floor;
    - `TestContentRememberDriftWarning` is past the class-size guidance.
14. The printed command's quoting and its trailing-backslash continuation are POSIX-shell forms. The manpage now says so. Behaviour in a Windows shell was reasoned by the round-5 reviewers from reading, not observed; the Step 4b reviewer did not run cmd.exe either.
15. QUESTION FOR THE OPERATOR. An output fault on the success line or on the ledger append in `src/gzkit/commands/content/remember.py`, after the row is durable, also exits 1. It is not repaired here. Brief Requirement 1 reads "On EVERY path". Whether that sentence reaches this path is the operator's ruling.
    - Round-5 spec review raised it by reading (finding `SR5-aux-success-line-output-fault-is-the-same-class-and-unguarded`).
    - The Step 4b round-2 reviewer executed both faults, with and without drift: each exits 1 with one durable row, and the advisory is not called.
    - That reviewer judged them outside REQ-01, reading "On EVERY path" as the enumerated advisory paths. That is the reviewer's opinion. The ruling remains the operator's.
16. The Step 4b reviewer's stated weakest point, in its terms: the permanent REQ-01 output-fault test neither asserts that the failing sink was reached nor covers the emission handler's `ValueError` arm. The recorded substitution proves `OSError` reach today. Its instrumented paired probe observed the sink reached and exit 0 for both `OSError` and `ValueError`. It calls this a regression-test limitation, not a demonstrated requirement violation. The probe is the reviewer's, in its disposable checkout; it is not a test in the repository.

**4. Awaiting attestation.**

Step 4b is complete: round 2 accepted, and the acceptance status is `ready: true`. What remains is the operator's Gate 5 attestation. Disclosure 15 carries one question for the operator's ruling.
