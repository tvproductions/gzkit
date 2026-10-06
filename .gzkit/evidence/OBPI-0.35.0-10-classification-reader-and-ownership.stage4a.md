## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

Before, the classification field of a corpus entry was schema-required and part of the baseline identity fingerprint, and nothing in `src/` read it; the binding copy of the same concept was a hand-maintained markdown table (`docs/governance/advisory-rules-audit.md`). Now `uv run gz validate --bullet-retention` reads an owned row's class from the corpus entry it cites and an unowned row's from the scorecard, fails closed on a broken owned mapping, refuses to bind an owned section that holds a live Ambiguous entry, and retains a row attributed to a SKILL.md or an ADR file against that file. An enrolled project's audit also refuses, by name, a rule-table row it cannot read, where before the round 2 repair such a row was dropped with no error; the row shape round 3 found, a table line with no leading pipe, is now refused, and an enrolled project's rows are held against a committed list of identities, so a row the reader stops recognising is named. Round 4 confirmed that repair independently and then found one route it did not cover: with the scorecard file itself removed, the audit returned no errors and no rows while the identities stayed pinned. The round 4 repair (4839e2cf1) refuses that route: with the scorecard absent and identities pinned, the audit returns one error naming the scorecard path, the count of pinned identities and the pinned file. Round 5 confirmed that repair independently and then found one more route: a project enrolled only by an attributed scorecard row, with no ownership declaration, whose scorecard stops yielding an attributed row is read as not enrolled, and its pinned identities are not checked. The round 5 repair (92c12bdd5) makes the pinned file alone decide whether the pinned check runs, so a project that pins any identity is held to the list whatever its scorecard, ownership declarations or attributions say, and a file the audit cannot decode as UTF-8 is a finding where it raised. Round 6 confirmed that repair independently, closed all seven findings and raised none (see Review history). A change made to the scorecard and the pinned file in one edit can pass clean; the operator ruled that boundary out of scope on 2026-10-06, and it is written into the brief's Threat Model. The live repository carries an ownership declaration; the round 5 reviewer observed its emptied, prose-only, directory and unreadable scorecards each failing closed through the pinned check. On the live repo 178 scorecard rows are audited, 31 answered by the corpus and 147 by the scorecard; six owned rows disagreed between the two surfaces, the operator ruled on 2026-10-05 that the corpus adopts the scorecard class, and the audit prints zero advisories.

**2. Key Proof**

With the scorecard held fixed, the corpus classification of an owned row decides the verdict (REQ-0.35.0-10-03), and the live audit and the retirement-witness scope both pass.

```
$ uv run -m unittest tests.governance.test_bullet_retention.TestOwnedDisagreementIsReported -v
test_corpus_change_alone_changes_the_verdict (tests.governance.test_bullet_retention.TestOwnedDisagreementIsReported.test_corpus_change_alone_changes_the_verdict)
Holding the scorecard fixed, the corpus classification decides the verdict. ... ok
test_disagreement_names_the_row_the_entry_and_both_values (tests.governance.test_bullet_retention.TestOwnedDisagreementIsReported.test_disagreement_names_the_row_the_entry_and_both_values)
The operator sees which row and entry disagree, and what each says. ... ok
test_scorecard_change_alone_never_changes_the_verdict (tests.governance.test_bullet_retention.TestOwnedDisagreementIsReported.test_scorecard_change_alone_never_changes_the_verdict)
Holding the corpus fixed, the scorecard cell decides only whether a report appears. ... ok
...
OK
```

```
$ uv run gz validate --bullet-retention
Validated: bullet_retention
✓ All validations passed (1 scopes).
```

```
$ uv run gz validate --corpus-retirement-witness
Validated: corpus_retirement_witness
✓ All validations passed (1 scopes).
```

Executed proof record `proof-d2546eb8de9e481c9545c5f1bd4569e8` (REQ-0.35.0-10-03), re-run after the round 5 repair and the brief amendment: with the disagreement report silenced (control `disagreement-silenced`), two of the three tests failed on their assertions (`test_disagreement_names_the_row_the_entry_and_both_values` and `test_scorecard_change_alone_never_changes_the_verdict`); with the production line that binds the corpus class replaced by one that binds the scorecard class (control `scorecard-class-binds-owned-row`), all three failed on their assertions; the source was restored and the tests were green afterwards.

**3. Evidence**

**Quality checks:**

| Check | Command | Result |
|---|---|---|
| Lint | `uv run gz arb ruff` | exit 0; `arb-ruff-890637c24ed94fa590f5e9e5ef6c5f2c` |
| Typecheck | `uv run gz arb typecheck` | exit 0; `arb-step-typecheck-1f68cbe2743f47f289d58add74c71e7a` |
| Tests (full suite) | `arb:unittest` | 11476 tests, OK, 7 skipped; `arb-step-unittest-ff410e92a866415ca8c76d3746c019af` |
| Docs | `arb:mkdocs` | exit 0; `arb-step-mkdocs-0b67da2c160042f0a21e77fc1a256065` |
| Behave | `arb:behave` | 8 scenarios, 53 steps passed, 0 failed; `arb-step-behave-672c45b33af5432fb42e2a703d275e20` |
| OBPI tests | `arb:obpi-tests` | 71 tests OK; `arb-step-unittest-cad416370b9045f4a0e5c5d81a7efd84` |
| Validation scopes | `validate:scopes` | nine scopes, each run alone after each proof run, each exit 0; no receipt |
| REQ coverage | `covers` | 10 REQs; covered 7; uncovered_reqs 3; behavior_uncovered_reqs 0 |
| Brief drift | `brief-drift` | clean; deltas all 0; re-run after the Threat Model section was added |
| Evidence packet | `present-evidence` | after round 6: exit 0; attestable true; no blocker; three Demo commands each exit 0 |
| Precomplete | `precomplete` | after round 6: exit 0; all eleven checks pass |

All six receipts were recorded in this session (2026-10-06 UTC) on commit 33f36a47e, the sync commit that follows the repair commit 92c12bdd5, with a clean tree; each receipt's git field reads dirty false. The brief's Threat Model section and its Change Log entry were written after the receipts; they change the brief only, no source, test, feature, data or doc file the receipts exercise. The full-suite count of 11476 is 11469 plus the 7 tests of this repair. The nine validation scopes were each run alone after each proof run, and `--bullet-retention` printed no advisory lines. The three REQs without a covering test are the two SUPPORT REQs and the STRUCTURAL-FENCE REQ, by proof channel. Before round 6, `present-evidence` exited 3 because seven findings awaited independent closure (see Review history): its `blockers` list held those seven and nothing else, and its `review_blockers` list held 17, those seven plus one for each current proof lacking an accepted adversarial review; precomplete passed ten checks and failed adversarial_validation. After round 6 was imported, both commands were run again: `present-evidence` exits 0 with attestable true and both lists empty, the acceptance status reads ready with no open finding, and precomplete passes all eleven checks (brief_readiness, reconcile_idempotent, lock_held, arb_receipts, plan_audit_receipt, brief_headings, behave_req_coverage, task_envelope_coherence, adversarial_validation, operator_block and stage2_dispatch). The per-change check (`uv run gz check`) produces no receipt and is not cited as evidence here; it was run on the staged packet before the sync that preceded round 6.

```bash
# arb:unittest
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
# arb:mkdocs
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# arb:behave
uv run gz arb step --name behave -- uv run -m behave features/classification_ownership.feature
# arb:obpi-tests
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_bullet_retention -v
# validate:scopes
uv run gz validate --bullet-retention
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --brief-reconcile
uv run gz validate --cli-alignment
uv run gz validate --corpus-retirement-witness
uv run gz validate --waiver-ratchet
uv run gz validate --config-registry
# covers
uv run gz covers OBPI-0.35.0-10-classification-reader-and-ownership --json
# brief-drift
uv run gz obpi brief-drift OBPI-0.35.0-10-classification-reader-and-ownership
# present-evidence
uv run gz obpi present-evidence OBPI-0.35.0-10-classification-reader-and-ownership --json
# precomplete
uv run gz obpi precomplete OBPI-0.35.0-10-classification-reader-and-ownership
```

**Files created:**

Commit 4893b7321 (2026-10-03, the single-session trial):

- `features/classification_ownership.feature` (5 Gate 4 scenarios at that commit; 6 after 2346d91c5; 7 after 4839e2cf1; 8 after 92c12bdd5)
- `features/steps/classification_ownership_steps.py` (the steps for those scenarios)

Commit 2346d91c5 (2026-10-06, the round 3 repair):

- `data/advisory_scorecard_identities.json` (the pinned row identities an enrolled project's audit is held against; 178 identities, seeded from the rows the audit read)

**Files modified:**

Commit 4893b7321:

- `src/gzkit/governance/trust_audits/bullet_retention.py` (the resolver, the mapping fence, the Ambiguous fence, source-aware retention)
- `tests/governance/test_bullet_retention.py` (six new test classes)
- `src/gzkit/content/models/corpus.py` (docstring only)
- `docs/user/manpages/validate.md` (classification source and source-aware retention)
- `docs/governance/advisory-rules-audit.md` (narrowed authority; a source attribution on every row)

2026-10-05 (commits 7c05949ee and 3c53720ab, and e8617ba90, which first carried this packet):

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` (Decision item 9 amended to carry the retention scope, operator-ruled)
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (REQ-10 witness clause, Allowed Paths bullet split, third Demo command, the REQ-05 atomicity note, Change Log)
- `.gzkit/corpus/AGENTS.md.jsonl` (12 rows appended: 6 retractions, 6 re-captures; the 487 earlier rows byte-identical)
- `.gzkit/renditions/AGENTS.md/root.corpus.json` (provenance refreshed; root rendition and `AGENTS.md` byte-unchanged)
- `docs/governance/advisory-rules-audit.md` (six rows repointed to the new entry ids)
- `.claude/plans/classification-reader-and-ownership-OBPI-0.35.0-10.md` (plan, written after implementation and labelled so)

Round 1 repair (2026-10-05, commit 60e622dee):

- `src/gzkit/governance/trust_audits/bullet_retention.py` (a row with no row number is refused by name; this guard was later subsumed by the strict reader in ca8ab6534)
- `tests/governance/test_bullet_retention.py` (`test_missing_row_number_fails_closed_naming_the_row`)
- `docs/user/manpages/validate.md`, `docs/governance/advisory-rules-audit.md` (the fail-closed list names the missing row number)

Round 2 repair, operator-ruled (2026-10-05, commit ca8ab6534):

- `src/gzkit/governance/trust_audits/bullet_retention.py` (an enrolled project's scorecard is re-read strictly: every line of a `| # | Rule | Score |` table, or of a pipe block with no header row, is a row, and one that cannot be read is a named failure; an escaped pipe is cell text; a Score cell is read by the bold class it leads with; the round 1 guard is subsumed and removed; an unenrolled project keeps the legacy reading; 773 lines at that commit)
- `tests/governance/test_bullet_retention.py` (strict-reader tests written first and observed failing on their assertions; the live-population oracle rewritten to read rule tables structurally, independent of the audit's row grammar; 57 tests at that commit, up from 53)
- `docs/governance/advisory-rules-audit.md` (five rows requoted to verbatim rule-file wording and attributed: Pythonic #22, Data Models #27, Model Selection #52, Map Doctrine #58, Changelog #65)
- `docs/user/manpages/validate.md` (states that every line of a rule table is a row, that an unreadable one fails closed, that a literal pipe is written escaped, and that a score cell is read by the class it leads with)
- `data/mechanical_witness_grandfather.json` (Model Selection #52 added as frozen witness debt; shrink-only baseline 64 to 65)
- `data/waiver_ratchet_registry.json` (that list's baseline count, 64 to 65)
- `data/waiver_identity_baseline.json` (the authorization record for the new identity, carrying the operator's ruling verbatim)
- the brief, in commit 23bbca489 (the three `data/` files join the allowlist by the same ruling; Change Log entries for round 2 and its three rulings)

Round 3 repair, operator-ruled (2026-10-06, commit 2346d91c5):

- `src/gzkit/governance/trust_audits/bullet_retention.py` (a rule table runs to its first blank line or heading, and a line inside it that does not begin with a pipe is a row the audit refuses by name; an enrolled project's rows are held against the pinned identities in `data/advisory_scorecard_identities.json`, and the audit fails closed on a pinned identity it no longer reads, on a row that is not pinned, and on a pinned file that is missing or unreadable; 854 lines at that commit)
- `tests/governance/test_bullet_retention.py` (four tests written first; the live-population test is now `test_live_scorecard_population_is_the_committed_pinned_set` and compares against the pinned file; the structural oracle `_table_identities`, which shared the reader's leading-pipe assumption, is removed; every enrolled fixture now writes a pinned file; 61 tests at that commit, up from 57)
- `data/config_registry.json` (one declaration for the new file, which `gz validate --config-registry` requires of any new file under `data/`)
- `features/classification_ownership.feature` (one new scenario tagged @REQ-0.35.0-10-02, "A pinned row the scorecard no longer carries fails closed"; 6 scenarios at that commit)
- `features/steps/classification_ownership_steps.py` (the fixture pins its identities)
- `docs/user/manpages/validate.md` (states the table boundary and the pinned-identities contract)
- `docs/governance/advisory-rules-audit.md` (states the table boundary and the pinned-identities contract)
- the brief (the allowlist gains the pinned file by the ruling, and `data/config_registry.json` on the orchestrator's reading of the ruling; Change Log entry of 2026-10-06)

Round 4 repair, operator-ruled (2026-10-06, commit 4839e2cf1):

- `src/gzkit/governance/trust_audits/bullet_retention.py` (when the scorecard is absent, `validate_bullet_retention` no longer returns an empty result unconditionally; it calls a new function, `_absent_scorecard_errors`, which returns nothing when the project has no pinned file, returns the existing "could not be read" error when the pinned file cannot be read, returns nothing when the pinned file lists no identities, and otherwise returns one error naming the scorecard path, the count of pinned identities, the pinned file, ADR-0.35.0 § Decision item 9 and the re-run command; `audited_population` is unchanged at that commit; 885 lines at that commit, 854 before; the two exits that return nothing moved into `_pins_identities` in 92c12bdd5)
- `tests/governance/test_bullet_retention.py` (three tests written first, all tagged `@covers("REQ-0.35.0-10-02")`: `test_absent_scorecard_fails_closed_while_identities_stay_pinned`, `test_absent_scorecard_with_an_unreadable_pinned_set_fails_closed` and `test_project_with_no_scorecard_and_nothing_pinned_has_nothing_to_audit`; 64 tests at that commit, up from 61)
- `features/classification_ownership.feature` (one new scenario tagged @REQ-0.35.0-10-02, "An absent scorecard fails closed while its rows stay pinned"; 7 scenarios at that commit)
- `features/steps/classification_ownership_steps.py` (one new step that removes the scorecard file)
- `docs/user/manpages/validate.md` (lists the absent scorecard among the fail-closed cases; says a project with no scorecard and nothing pinned has nothing to audit)
- `docs/governance/advisory-rules-audit.md` (lists the absent scorecard among the fail-closed cases)
- the brief (Change Log entry of 2026-10-06 recording the ruling and the repair; no requirement and no allowlist entry changed)

Round 5 repair, operator-ruled (2026-10-06, commit 92c12bdd5):

- `src/gzkit/governance/trust_audits/bullet_retention.py` (a new function, `_pins_identities`, is true when the pinned file exists and either lists at least one identity or cannot be read, and false when the file is absent or lists nothing; `_resolve_population` takes only the project root and makes the whole entry decision: an absent scorecard returns `_absent_scorecard_errors` when identities are pinned and nothing otherwise, a scorecard that is not UTF-8 returns one finding naming the scorecard, the legacy return requires nothing pinned, no ownership declaration and no attributed row together, and every other project takes the strict read with the pinned check, unchanged; `validate_bullet_retention` and `audited_population` both call it and no longer test for the scorecard themselves; `_absent_scorecard_errors` keeps its two error outcomes and loses its two early exits; a new function, `_undecodable_scorecard_error`, returns the finding for a scorecard that is not UTF-8; `_parse_scorecard` and `_read_rule_rows` keep their signatures; four more reads treat a file that is not UTF-8 as unreadable where they raised: the pinned file, the per-turn surface files, an attributed skill or ADR file, and an advisor-QC receipt; the module docstring states the rule; 922 lines, 885 before)
- `tests/governance/test_bullet_retention.py` (seven tests, each written before the code it drives: four tagged `@covers("REQ-0.35.0-10-02")`, one tagged `@covers("REQ-0.35.0-10-09")`, and two under other briefs' requirements, REQ-0.0.33-01-02 and REQ-0.0.37-25-03; 71 tests, up from 64)
- `features/classification_ownership.feature` (one new scenario tagged @REQ-0.35.0-10-02, "A pinned row is held when nothing but the pinned file enrolls the project"; 8 scenarios)
- `features/steps/classification_ownership_steps.py` (three new steps)
- `docs/user/manpages/validate.md` (says the pinned file alone decides whether the check runs and that a scorecard that is not UTF-8 fails closed by name; lists the other four undecodable reads; says the legacy audit requires no pinned identity)
- `docs/governance/advisory-rules-audit.md` (says the pinned file alone decides whether the check runs and that a scorecard that is not UTF-8 fails closed by name)
- the brief (Change Log entry of 2026-10-06 recording the ruling and the repair; no requirement and no allowlist entry changed)

Scope ruling (2026-10-06; written after the receipts, not part of 92c12bdd5):

- the brief (a `## Threat Model` section holding the text the operator selected, placed after the Identity and Reconciliation Contract, and a Change Log entry for the ruling; no requirement, allowlist entry, source or test changed)

Not part of this OBPI: two later commits sit between ca8ab6534 and e59763ff9. Commit 6396fb3cc upgrades Python to 3.13.16, refreshes `uv.lock`, removes wily and edits four workflow files. Commit 6268e2398 retires two duplicate tests elsewhere in `tests/` and regenerates `data/tautological_test_baseline.json`. Neither touches a file on this brief's allowlist. The input digest the proofs are bound to changed after ca8ab6534, which is why all ten proofs were re-run on e59763ff9. The round 3 repair changed the digest again, and all ten proofs were re-run on 2346d91c5. Commit eeb4f2758 (2026-10-06), a direct fix for GHI #1178 in `src/gzkit/file_lock.py` with two tests in `tests/test_file_lock.py`, landed between round 4 and the round 4 repair. It touches no file on this brief's allowlist. It changed the input digest on its own, before the repair did. All ten proofs were re-executed on the tree repaired by 4839e2cf1. The round 5 repair (92c12bdd5) changed the digest again, and all ten were re-executed on the repaired tree (digest cd893928…); that run is superseded. The Threat Model section is part of the proof contract: adding it made all ten proofs read "stale contract" and "stale inputs", and all ten were re-executed against the amended brief. The proof ids below are from that second run.

**REQ coverage:**

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|---|---|---|---|---|---|
| REQ-0.35.0-10-01 | BEHAVIOR | 3 selectors; 2 controls killed | `TestOwnedBulletResolvesFromCorpus` | `proof-abc9288e` | behavioral proof valid |
| REQ-0.35.0-10-02 | BEHAVIOR | 23 selectors; 18 controls killed | `TestUnownedBulletResolvesFromScorecard` | `proof-9595e0fa` | behavioral proof valid |
| REQ-0.35.0-10-03 | BEHAVIOR | 3 selectors; 2 controls killed | `TestOwnedDisagreementIsReported` | `proof-d2546eb8` | behavioral proof valid |
| REQ-0.35.0-10-04 | BEHAVIOR | 5 selectors; 2 controls killed | `TestCaptureDefaultNeverBinds` | `proof-7aeae83b` | behavioral proof valid |
| REQ-0.35.0-10-05 | BEHAVIOR | 1 selector; 1 control killed | `TestReconciliationIsAppendOnly` | `proof-d89849e2` | behavioral proof valid |
| REQ-0.35.0-10-06 | SUPPORT | `resolve_support_proof` | file on disk + `--documents` | `proof-b1bdb3e5` | pass |
| REQ-0.35.0-10-07 | STRUCTURAL-FENCE | `resolve_fence_proof` | ADR-0.35.0 BI-04 | `proof-4ffce7c5` | pass |
| REQ-0.35.0-10-08 | BEHAVIOR | 2 selectors; 1 control killed | `TestDeclaredSourceRetention` | `proof-89465c15` | behavioral proof valid |
| REQ-0.35.0-10-09 | BEHAVIOR | 2 selectors; 2 controls killed | `TestDeclaredSourceRetention` | `proof-1bd5d1e6` | behavioral proof valid |
| REQ-0.35.0-10-10 | SUPPORT | `resolve_support_proof` | file on disk + `--documents` | `proof-173b4199` | pass |

```text
Test file for every BEHAVIOR row: tests/governance/test_bullet_retention.py
All ten proof records are valid against input digest
829bd985fc73025175023c08cdb94fead25dd030dc6a9e8d111a5989e7049f8b
Twenty-eight controls in all. Every control below: outcome killed, failure_class assertion;
source sha256 restored (501bba87ca73… before and after the whole run); restored run green.

REQ-0.35.0-10-01  proof-abc9288eea174fb1b21f4c78ae09091a
  killed controls: scorecard-class-binds-owned-row, wrong-section-entry-binds
REQ-0.35.0-10-02  proof-9595e0fac63842d897616049780a2db7
  killed controls: duplicate-identity-accepted, unowned-section-demands-corpus-entry,
  unreadable-row-skipped, escaped-pipe-splits-cell, score-qualifier-refused,
  any-table-read-as-rules, pipeless-table-line-skipped, lost-pinned-identity-ignored,
  unpinned-row-accepted, unreadable-pinned-set-ignored,
  absent-scorecard-unreadable-pinned-set-ignored, absent-scorecard-returns-clean,
  unpinned-project-demands-a-pinned-file, empty-pinned-list-enrolls-the-project,
  unreadable-pinned-file-pins-nothing, pinned-file-no-longer-decides-the-check,
  undecodable-scorecard-not-reported, undecodable-pinned-file-raises
  The round 1 control blank-row-number-accepted no longer exists: the guard it mutated
  was subsumed by the strict reader and removed in ca8ab6534. unreadable-row-skipped
  fails test_missing_row_number_fails_closed_naming_the_row and
  test_unreadable_rule_row_fails_closed_and_is_never_skipped.
  The four controls added with the round 3 repair (2346d91c5) and the test each fails:
    pipeless-table-line-skipped
      -> test_table_line_without_a_leading_pipe_is_refused_not_dropped
    lost-pinned-identity-ignored
      -> test_pinned_identity_the_audit_no_longer_reads_fails_closed
    unpinned-row-accepted
      -> test_row_the_pinned_set_does_not_list_fails_closed
    unreadable-pinned-set-ignored
      -> test_missing_or_unreadable_pinned_set_fails_closed_with_recovery
  Of the four controls added with the round 4 repair (4839e2cf1), one is unchanged, two
  are rewritten against the code of 92c12bdd5 because the lines they named were removed,
  and one is replaced. Each, and the test it fails:
    absent-scorecard-unreadable-pinned-set-ignored
    (unchanged)
      -> test_absent_scorecard_with_an_unreadable_pinned_set_fails_closed
    absent-scorecard-returns-clean
    (rewritten: the absent-scorecard return replaced by return [], [])
      -> test_absent_scorecard_fails_closed_while_identities_stay_pinned
      -> test_absent_scorecard_with_an_unreadable_pinned_set_fails_closed
    unpinned-project-demands-a-pinned-file
    (rewritten: the "no pinned file" exit of _pins_identities disabled)
      -> test_project_with_no_scorecard_and_nothing_pinned_has_nothing_to_audit
      -> test_unenrolled_project_keeps_the_legacy_audit
    empty-pinned-list-enrolls-the-project
    (replaces empty-pinned-set-refused: _pins_identities made to return True always)
      -> test_project_with_no_scorecard_and_nothing_pinned_has_nothing_to_audit
      -> test_pinned_file_listing_no_identity_enrolls_nothing
  The four controls added with the round 5 repair (92c12bdd5) and the test each fails:
    unreadable-pinned-file-pins-nothing
    (an unreadable pinned file no longer counts as pinning)
      -> test_absent_scorecard_with_an_unreadable_pinned_set_fails_closed
    pinned-file-no-longer-decides-the-check
    ("not pins" removed from the legacy return, which restores the pre-repair entry decision)
      -> test_pinned_identity_is_held_when_nothing_else_enrolls_the_project
    undecodable-scorecard-not-reported
    (the undecodable return disabled)
      -> test_scorecard_that_is_not_utf8_is_a_finding_of_the_audit_not_a_crash
    undecodable-pinned-file-raises
    (the decode error no longer caught for the pinned file)
      -> test_pinned_set_that_is_not_utf8_fails_closed_with_recovery
  pinned-file-no-longer-decides-the-check is the control that operates at the entry
  decision round 5 named as the weakest point.
  absent-scorecard-returns-clean mutates the absent-scorecard return, which now sits in
  _resolve_population; round 4 named that return, then in validate_bullet_retention, as
  the weakest point.
  escaped-pipe-splits-cell also nominates the renamed live test
  test_live_scorecard_population_is_the_committed_pinned_set.
REQ-0.35.0-10-03  proof-d2546eb8de9e481c9545c5f1bd4569e8
  killed controls: disagreement-silenced, scorecard-class-binds-owned-row
REQ-0.35.0-10-04  proof-7aeae83b0f754902b4ab6bc9d592d265
  killed controls: capture-default-binds, unloadable-ownership-falls-back-to-scorecard
REQ-0.35.0-10-05  proof-d89849e2bc994b9b8aaed51d82a944ac
  killed controls: fence-reads-raw-log
REQ-0.35.0-10-06  proof-b1bdb3e5ca704af082ac2cb6acb7efbb
  SUPPORT: the witness clause names artifact_edited citing docs/governance/advisory-rules-audit.md.
  No ledger event cites that path. The resolver passed on its second arm: the cited file
  exists on disk and `uv run gz validate --documents` admits it.
REQ-0.35.0-10-07  proof-4ffce7c587ce4414b3f51e810db00653
  STRUCTURAL-FENCE: Boundary Invariants of ADR-0.35.0-canon-entry-corpus-landing, BI-04;
  audited at ADR closeout
REQ-0.35.0-10-08  proof-89465c15b65c42ba91ff2db57d6145dc
  killed controls: declared-source-checked-against-surface
REQ-0.35.0-10-09  proof-1bd5d1e672bf4be5972202549ab6c524
  killed controls: absent-text-reads-as-retained, undecodable-source-raises
  undecodable-source-raises, added with the round 5 repair
  (the decode error no longer caught for an attributed source)
      -> test_source_that_is_not_utf8_fails_closed_naming_the_row
REQ-0.35.0-10-10  proof-173b41995d74462a9693485d04b98fa8
  SUPPORT: the witness clause names artifact_edited citing docs/user/manpages/validate.md.
  No ledger event cites that path. The resolver passed on its second arm: the cited file
  exists on disk and `uv run gz validate --documents` admits it.

Corpus reconciliation of 2026-10-05 (six owned rows; corpus adopts the scorecard class).
Each row: scorecard identity | class change | old entry id -> new entry id | tombstone id

local-agent-rules-claude-md-local-agent-rules#7 | Judgment -> Mechanical
  old:       corpus-execution-rules-2026-09-17T11:39:35.178468+00:00
  new:       corpus-execution-rules-2026-10-05T21:33:07.026263+00:00
  tombstone: corpus-retraction-corpus-execution-rules-2026-09-17T11:39:35.178468+00:00-2026-10-05T21:33:06.862515+00:00
local-agent-rules-claude-md-local-agent-rules#8 | Mechanical -> Judgment
  old:       corpus-execution-rules-2026-09-17T11:39:35.331784+00:00
  new:       corpus-execution-rules-2026-10-05T21:33:07.346566+00:00
  tombstone: corpus-retraction-corpus-execution-rules-2026-09-17T11:39:35.331784+00:00-2026-10-05T21:33:07.185828+00:00
local-agent-rules-claude-md-local-agent-rules#10 | Judgment -> Mechanical
  old:       corpus-attestation-2026-09-17T11:39:35.990401+00:00
  new:       corpus-attestation-2026-10-05T21:33:07.666420+00:00
  tombstone: corpus-retraction-corpus-attestation-2026-09-17T11:39:35.990401+00:00-2026-10-05T21:33:07.505922+00:00
governance-core-gzkit-rules-governance-core-md#14 | Judgment -> Mechanical
  old:       corpus-project-identity-2026-09-17T11:40:15.738676+00:00
  new:       corpus-project-identity-2026-10-05T21:33:07.986003+00:00
  tombstone: corpus-retraction-corpus-project-identity-2026-09-17T11:40:15.738676+00:00-2026-10-05T21:33:07.826719+00:00
governance-core-gzkit-rules-governance-core-md#16 | Judgment -> Mechanical
  old:       corpus-behavior-rules-2026-09-17T11:39:31.740284+00:00
  new:       corpus-behavior-rules-2026-10-05T21:33:08.305718+00:00
  tombstone: corpus-retraction-corpus-behavior-rules-2026-09-17T11:39:31.740284+00:00-2026-10-05T21:33:08.144665+00:00
governance-core-gzkit-rules-governance-core-md#17a | Judgment -> Mechanical
  old:       corpus-behavior-rules-2026-09-17T11:39:31.433847+00:00
  new:       corpus-behavior-rules-2026-10-05T21:33:08.624072+00:00
  tombstone: corpus-retraction-corpus-behavior-rules-2026-09-17T11:39:31.433847+00:00-2026-10-05T21:33:08.464416+00:00
```

**Review history**

Round 1 — Codex (tier 1), receipt `arb-step-codexadversary-c47b21f19ded456989a48f7dbb25e5e6`, reviewed commit e8617ba90. Verdict NOT-CORROBORATED, token refuted. It replayed all 11 recorded controls (each killed on its own assertion, source restored), ran the live audit (0 errors, 173 rows, 31 answered by the corpus), ran six probes of its own, and approved seven of ten proofs. Three findings:

| Finding | REQ | What it found | Repair |
|---|---|---|---|
| `codex-035010-missing-row-number` | 02 | a row with a blank number cell was audited with an empty identity and no error | the identity check refused it by name; new test written first and observed failing on its assertion. That guard and its control `blank-row-number-accepted` were later subsumed by the strict reader (ca8ab6534); the test remains and control `unreadable-row-skipped` now fails it |
| `codex-035010-scorecard-edit-witness` | 06 | this packet said a ledger event cites the scorecard; none does | packet now states the resolver arm that passed |
| `codex-035010-manpage-edit-witness` | 10 | this packet said a ledger event cites the manpage; none does | packet now states the resolver arm that passed |

The reviewer also named the weakest point: the REQ-02 population test derived its expected identities from the same scorecard it audits. The round 1 repair closed the blank-number case it demonstrated; a pinned baseline of identities was not added then, and one was added in the round 3 repair (2346d91c5).

Round 2 — Codex (tier 1), reviewer id `codex-independent-035010-round2`, receipt `arb-step-codexadversary-89c8da29860546c38621432ec67acf05`, reviewed commit 1ef19594e. Verdict refuted. That receipt is a re-emission: the first emission, `arb-step-codexadversary-7ad9ace1ea1e488390fa039a0847de2a`, was refused by the importer because it relisted an existing finding id with new text, and the reviewer was asked for a formatting-only re-emission with no judgment changed. It approved 9 of 10 proofs, with 9 replay records, and closed the two SUPPORT findings. It left `codex-035010-missing-row-number` open and raised `codex-035010-empty-number-cell-dropped-r2` (REQ-02): replacing the prefix `| 7 |` with `||` produced zero errors, 172 audited rows and 30 corpus-resolved rows, because the row grammar dropped a truly empty cell before the identity check ran. It named the same weakest point as round 1: the live population test took its expected identities from the scorecard it audits.

After round 2 (rulings are verbatim in the brief's Change Log entries of 2026-10-05):

- The orchestrator measured five malformed row shapes dropped the same way and took the design to the operator instead of a third patch. Operator ruling, verbatim: "A" — fail closed on any unparseable rule-table row.
- Repair (ca8ab6534): an enrolled project's scorecard is re-read strictly; every line of a `| # | Rule | Score |` table, or of a pipe block with no header row, is a row, and one that cannot be read is a named failure; an escaped pipe is cell text; the round 1 guard is subsumed and removed; an unenrolled project keeps the legacy reading. Tests were written first and observed failing on their assertions.
- The test oracle for the live population was rewritten to read rule tables structurally, independent of the audit's row grammar. No pinned baseline of identities was added at that point; the round 2 reviewer said REQ-02 does not require one. That oracle was removed, and a pinned baseline added, in the round 3 repair.
- The strict reader surfaced five live rows that had never been audited: Pythonic #22, Data Models #27 and Model Selection #52 (escaped pipes in the rule cell), Map Doctrine #58 and Changelog #65 (a Score cell carrying two classes). Operator ruling, verbatim selection: "A: Apply as drafted (Recommended)". Each was requoted to verbatim rule-file wording and attributed. The audited population went from 173 to 178 rows; no identity was removed.
- Model Selection #52 was frozen as witness debt; the shrink-only baseline moved from 64 to 65. Operator ruling, verbatim selection: "A: Freeze as missed debt (Recommended)".

Four findings were open in the acceptance record when round 3 was dispatched:

| Finding | REQ | Raised | State before round 3 |
|---|---|---|---|
| `codex-035010-missing-row-number` | 02 | round 1 | left open by round 2; repair landed in ca8ab6534 |
| `codex-035010-empty-number-cell-dropped-r2` | 02 | round 2 | repair landed in ca8ab6534 |
| `codex-035010-scorecard-edit-witness` | 06 | round 1 | closed by round 2 against `proof-719f97b9`; needed closure again against `proof-e6cac2bc` |
| `codex-035010-manpage-edit-witness` | 10 | round 1 | closed by round 2 against `proof-d17394e4`; needed closure again against `proof-17e05a06` |

The two SUPPORT findings reappeared only because the re-run superseded the proofs round 2 closed them against; the acceptance record requires verified closure against the current proof ids. Nothing about those two requirements changed.

Round 3 — Codex (tier 1), reviewer id `codex-independent-035010-round3`, receipt `arb-step-codexadversary-32d287557baa4a10b11ac9e4b9683a41`, reviewed commit 23eced80f in a disposable checkout (source digest e04f6e17044a…). Verdict refuted. It approved all ten proofs then current, recorded 15 replays (every recorded control failed its nominated tests on their own assertions; source restored), and closed all four findings above against the proof ids then current: both earlier missing-number counterexamples produced one named error at scorecard line 107. Its own probes with an empty rule cell, an unbold score, too few cells and an unescaped pipe in the rule text were each refused by name; escaped-pipe text and a qualified score were audited; a table of another shape was ignored. It raised one new finding:

| Finding | REQ | What it found |
|---|---|---|
| `codex-035010-leading-pipe-row-dropped-r3` | 02 | removing only the leading pipe from Local Agent Rules row 7's line dropped the row with no error: the audit reported 0 errors, 177 rows and 30 corpus-resolved rows, against 0, 178 and 31 on the restored file. The reader skipped any line without a leading pipe before validating it, and the live-population test made the same exclusion, so it still passed under the edit |

The orchestrator reproduced the counterexample in the same checkout: 0 errors, 177 rows, row 7 absent; 178 rows after restoring the file. The reviewer named the weakest point as the leading-pipe assumption shared by production and the population oracle, the same family as the weakest point of rounds 1 and 2.

Round 3 was the last round the bound permits (two follow-ups after round 1). With one mapped finding open, the OBPI was recorded as blocked on the operator (`gz obpi block`, 2026-10-06 UTC) and no fourth round was dispatched at that point.

After round 3:

- The decision was put to the operator with four options: (A) a committed baseline of row identities together with the narrow reader fix and one more review round past the bound; (B) the narrow reader and oracle fix alone; (C) a contract boundary stating that a rule-table row begins with a pipe; (D) hold item 10. Operator ruling, verbatim: "A". The block was cleared with `gz obpi unblock` carrying that ruling.
- Repair (2346d91c5): a rule table runs to its first blank line or heading, and a line inside it that does not begin with a pipe is a row the audit refuses by name. An enrolled project's rows are held against the pinned identities in `data/advisory_scorecard_identities.json`, and the audit fails closed on a pinned identity it no longer reads, on a row that is not pinned, and on a pinned file that is missing or unreadable.
- Four tests were written first. `test_table_line_without_a_leading_pipe_is_refused_not_dropped`, `test_pinned_identity_the_audit_no_longer_reads_fails_closed` and `test_row_the_pinned_set_does_not_list_fails_closed` were each observed failing on their assertion (`0 != 1`) before their code existed. `test_missing_or_unreadable_pinned_set_fails_closed_with_recovery` was observed failing on an unhandled exception before the handler existed; its control `unreadable-pinned-set-ignored` is the assertion-level evidence.
- The live-population test is now `test_live_scorecard_population_is_the_committed_pinned_set` and compares against the pinned file. The structural oracle `_table_identities`, which shared the reader's leading-pipe assumption, is removed. Every enrolled fixture now writes a pinned file.
- The pinned file holds 178 identities, seeded from the rows the audit read. Cross-check: an independent crude reading of the scorecard (any line whose third cell leads with a bold class) found 181 lines; the three extra are rows of a `| Class | Count | Membership |` table, not rule rows; every one of the 178 is in the crude set.
- The brief's allowlist gained the pinned file by the ruling, and `data/config_registry.json` on the orchestrator's reading of the ruling, not the operator's words; the option as presented said it "needs an allowlist amendment for one data file".
- Live audit after the repair: 0 errors, 178 rows, 31 answered by the corpus, 147 by the scorecard; zero advisories.
- The orchestrator did not re-run the round 3 counterexample on the repaired tree. The covering test `test_table_line_without_a_leading_pipe_is_refused_not_dropped` and control `pipeless-table-line-skipped` are the evidence; the independent re-run is round 4's.

Five findings were open in the acceptance record when round 4 was dispatched:

| Finding | REQ | Raised | State before round 4 |
|---|---|---|---|
| `codex-035010-leading-pipe-row-dropped-r3` | 02 | round 3 | repair in 2346d91c5; closure was round 4's to give |
| `codex-035010-missing-row-number` | 02 | round 1 | closed by round 3 against `proof-e63644fb`; needs closure again against `proof-c1cb02b8` |
| `codex-035010-empty-number-cell-dropped-r2` | 02 | round 2 | closed by round 3 against `proof-e63644fb`; needs closure again against `proof-c1cb02b8` |
| `codex-035010-scorecard-edit-witness` | 06 | round 1 | closed by round 3 against `proof-e6cac2bc`; needs closure again against `proof-fe39538d` |
| `codex-035010-manpage-edit-witness` | 10 | round 1 | closed by round 3 against `proof-17e05a06`; needs closure again against `proof-1986839f` |

The block was cleared by the operator's ruling. Round 3 closed four of these five against the proofs current then; the re-run after the repair superseded those proofs, so the record lists the four as requiring verified closure again against the current ids. For REQ-06 and REQ-10 nothing changed. For REQ-02 the repair changed the reader, so round 4 re-verifies those two closures as well. Round 4 was authorized by the operator's ruling "A" past the two-follow-up bound.

Round 4 — Codex (tier 1), reviewer id `codex-independent-035010-round4`, receipt `arb-step-codexadversary-25f144e1dcdd4461984e783878b6eb4e`, reviewed commit 0171dd746 in a disposable checkout (source digest 63c5cdc1654c…). Verdict NOT-CORROBORATED, token refuted. It approved all ten current proofs, recorded 19 replays (every control failed its nominated tests on their own assertions; source restored), ran the 61 module tests, and closed all five findings above against the current proof ids. Removing only row 7's leading pipe now yields 2 errors, 177 rows and 30 corpus-resolved rows: one error names scorecard line 107 and one names the lost pinned identity. The blank-number and empty-number counterexamples each yield the same two kinds of named refusal. It asserted no contradiction between any requirement's text and the stated boundary on coordinated edits of the scorecard and the pinned file. It raised one new finding:

| Finding | REQ | What it found |
|---|---|---|
| `codex-035010-missing-scorecard-bypasses-pins-r4` | 02 | removing only `docs/governance/advisory-rules-audit.md`, with the 178 pinned identities, the ownership declaration, the corpus and the ledger untouched, makes the audit report 0 errors and 0 rows. `validate_bullet_retention` returns an empty result when the scorecard is absent, before the enrolled path and the pinned check are reached; `audited_population` has the same early return |

The orchestrator reproduced the counterexample in the same checkout: 0 errors and 0 rows with the file removed; 0 errors, 178 rows and 31 corpus-resolved after restoring it. The reviewer named the weakest point as that entry-point early return: every recorded control operates below it, so their replay cannot rule the route out. This is a different root from the one rounds 1 to 3 named (a row shape the reader excluded before validating it).

Round 4 was the one round the ruling authorized. With one mapped finding open, the OBPI was recorded as blocked on the operator again (`gz obpi block`, 2026-10-06 UTC). No repair was attempted and no fifth round was dispatched at that point.

After round 4:

- In a new session the decision was put to the operator with four options: (A) repair the early return and run a fifth focused Codex round; (B) repair it and close it by the operator's own review, recorded as the human-adversary tier; (C) rule the absent-scorecard case out of scope in the brief; (D) hold item 10 and move to the tune-up items. Operator ruling, verbatim: "A". The ruling was booked on the handoff with `gz handoff decide` and the block was cleared with `gz obpi unblock` carrying it.
- Repair (4839e2cf1): when the scorecard is absent, `validate_bullet_retention` no longer returns an empty result unconditionally. It calls a new function, `_absent_scorecard_errors`, which returns nothing when the project has no pinned file, returns the existing "could not be read" error when the pinned file cannot be read, returns nothing when the pinned file lists no identities, and otherwise returns one error naming the scorecard path, the count of pinned identities, the pinned file, ADR-0.35.0 § Decision item 9 and the re-run command.
- `audited_population` is unchanged: for an absent scorecard it still returns no rows, because none were read. The error channel is `validate_bullet_retention`.
- Three tests were written first, all tagged `@covers("REQ-0.35.0-10-02")`. `test_absent_scorecard_fails_closed_while_identities_stay_pinned` and `test_absent_scorecard_with_an_unreadable_pinned_set_fails_closed` were each observed failing on their assertion (`0 != 1`) before the code existed. `test_project_with_no_scorecard_and_nothing_pinned_has_nothing_to_audit` (two sub-cases: no pinned file; a pinned file listing no rows) is the control for the boundary and passed before and after. The module holds 64 tests, up from 61.
- The feature gained one scenario tagged @REQ-0.35.0-10-02, "An absent scorecard fails closed while its rows stay pinned", for 7 scenarios, and the steps file gained one step that removes the scorecard file.
- `docs/user/manpages/validate.md` and `docs/governance/advisory-rules-audit.md` each now list the absent scorecard among the fail-closed cases. The manpage also says a project with no scorecard and nothing pinned has nothing to audit.
- The brief gained a Change Log entry of 2026-10-06 recording the ruling and the repair. No requirement and no allowlist entry changed.
- Four controls were added to the REQ-02 proof with this repair. `absent-scorecard-returns-clean` is the control that operates at the entry point round 4 named as the weakest point.
- Live audit after the repair: 0 errors, 178 rows, 31 answered by the corpus, 147 by the scorecard; the pinned file holds 178 identities; `uv run gz validate --bullet-retention` printed no advisory lines.
- The orchestrator re-ran the round 4 counterexample on a copy holding the live pinned file, ownership declaration, corpus and per-turn surfaces and no scorecard. Observed: 1 error, 0 rows. The error text follows. The independent re-run is round 5's.

```text
Bullet-retention identity violation: the scorecard docs/governance/advisory-rules-audit.md is absent while 178 scorecard row identities are pinned in data/advisory_scorecard_identities.json.
  Why: ADR-0.35.0 § Decision item 9 — the audited population never shrinks; removing the scorecard removes every pinned row from the audit at once.
  Fix: restore the file with `git checkout -- docs/governance/advisory-rules-audit.md`, then re-run `uv run gz validate --bullet-retention`.
```

Six findings were open in the acceptance record when round 5 was dispatched:

| Finding | REQ | Raised | State before round 5 |
|---|---|---|---|
| `codex-035010-missing-scorecard-bypasses-pins-r4` | 02 | round 4 | repair in 4839e2cf1; closure was round 5's to give |
| `codex-035010-leading-pipe-row-dropped-r3` | 02 | round 3 | closed by round 4 against `proof-c1cb02b8`; needs closure again against `proof-f723da05` |
| `codex-035010-missing-row-number` | 02 | round 1 | closed by round 4 against `proof-c1cb02b8`; needs closure again against `proof-f723da05` |
| `codex-035010-empty-number-cell-dropped-r2` | 02 | round 2 | closed by round 4 against `proof-c1cb02b8`; needs closure again against `proof-f723da05` |
| `codex-035010-scorecard-edit-witness` | 06 | round 1 | closed by round 4 against `proof-fe39538d`; needs closure again against `proof-6811368d` |
| `codex-035010-manpage-edit-witness` | 10 | round 1 | closed by round 4 against `proof-1986839f`; needs closure again against `proof-030611d7` |

Round 4 closed five of these against the proofs current then. The re-run superseded those proofs, so the record lists the five as requiring verified closure again. For REQ-06 and REQ-10 the two documents each gained a sentence about the absent scorecard; the witness clause and the resolver arm that passes are unchanged. Round 5 was authorized by the operator's ruling "A" and was the fourth round past the first, two more than the standing bound of two follow-ups; the third was authorized by the earlier "A".

Round 5 — Codex (tier 1), reviewer id `codex-independent-035010-round5`, receipt `arb-step-codexadversary-b1e97958254b472193064ffcee97e1bf`, reviewed commit b1c510a7a in a disposable checkout (source digest 133a894a6331…). Verdict NOT-CORROBORATED, token refuted. It approved all ten current proofs, recorded 23 replays (every control failed its nominated tests on their own assertions; source restored), ran the 64 module tests, and closed all six findings above against the current proof ids. With the live scorecard removed the audit now prints 1 error and 0 rows, naming the scorecard, the 178 pinned identities, the pinned file, Decision item 9 and the recovery. The three earlier row counterexamples on row 7 each yield 2 errors, 177 rows and 30 corpus-resolved rows. A live scorecard that is empty, prose only, a directory or unreadable fails closed through the pinned check. An enrolled project with no scorecard and no pinned file, or with an empty pinned list, returns no error. It judged that `audited_population` returning no rows for an absent scorecard reports what was read, and that the count-bearing message satisfies the repair. It raised one new finding:

| Finding | REQ | What it found |
|---|---|---|
| `codex-035010-attribution-enrollment-bypasses-pins-r5` | 02 | in a fixture with no ownership declaration, one Mechanical row attributed to a skill file, that file's matching text and one pinned identity, the audit prints 0 errors and 1 row. Changing only the scorecard to an empty file, to prose with no table, or removing the row's leading pipe each prints 0 errors and 0 rows, with the pinned file byte-identical. `_resolve_population` returns on its not-enrolled path, before the pinned check, whenever no ownership declaration exists and the legacy reader sees no attributed row. Removing the scorecard entirely prints 1 error there, so the round 4 repair holds and this is a separate entry condition |

The orchestrator reproduced the counterexample on a copy of the reviewer's fixture against the live source: 0 errors and 1 row at baseline; 0 errors and 0 rows with the scorecard emptied and the pinned file untouched; 1 error with the scorecard removed; 0 errors and 1 row restored. The reviewer named the weakest point: `_resolve_population` decides whether to enforce the pinned population by asking whether the legacy reader still sees an attributed row, so the loss of the last readable attribution disables the witness meant to detect that loss. It shares its root with round 4's weakest point: the pinned check is reached only after an entry decision that depends on what the reader read.

The reviewer also observed, as an observation and not a finding, that a scorecard holding invalid UTF-8 raises `UnicodeDecodeError` and exits 1: not a clean result, and not the audit's normal actionable error.

Round 5 was the one round the ruling authorized. With one mapped finding open, the OBPI was recorded as blocked on the operator a third time (`gz obpi block`, 2026-10-06 UTC). No repair was attempted and no sixth round was dispatched at that point.

After round 5 (rulings are verbatim in the brief's Change Log entries of 2026-10-06):

- The decision was put to the operator with four options: (A) redesign the entry decision so that a pinned identities file alone puts a project on the strict path, and run a sixth focused Codex round; (B) the same redesign closed by the operator's own review, recorded as the human-adversary tier; (C) rule a project enrolled by attribution alone out of scope in the brief; (D) hold item 10 and move to the tune-up items. Operator ruling, verbatim: "A, but we need a h/o and git sync". The ruling was booked on the handoff with `gz handoff decide` and the block was cleared with `gz obpi unblock` carrying it. A handoff was written and synced; no repair was started in that session.
- In the next session the handoff was presented with its claims checked against live state, and the operator ruled, verbatim: "proceed". That ruling is booked on the handoff.
- Repair (92c12bdd5), all in files on the brief's allowlist: the pinned file alone decides whether the pinned check runs. A new function, `_pins_identities`, is true when `data/advisory_scorecard_identities.json` exists and either lists at least one identity or cannot be read, and false when the file is absent or lists nothing. `_resolve_population` takes only the project root and makes the whole entry decision, in this order: read `_pins_identities`; scorecard absent, return `_absent_scorecard_errors` when identities are pinned and nothing otherwise; scorecard not UTF-8, return one finding naming the scorecard; the legacy return, which requires nothing pinned, no ownership declaration and no attributed row together; otherwise the strict read with the pinned check, unchanged.
- `validate_bullet_retention` and `audited_population` no longer test for the scorecard's existence themselves; both call `_resolve_population`. `_absent_scorecard_errors` lost its two early exits (no pinned file; pinned list empty), which `_pins_identities` decides before it is called; its two error outcomes are unchanged.
- Folded in, as the ruled option said it would be: the decode error the round 5 reviewer observed. A new function, `_undecodable_scorecard_error`, returns the finding for a scorecard that is not UTF-8. Four more reads treat a file that is not UTF-8 as unreadable where they raised: the pinned file, the per-turn surface files (AGENTS.md, CLAUDE.md and each rule file), an attributed skill or ADR file, and an advisor-QC receipt.
- Seven tests were written, each before the code it drives. The module holds 71 tests, up from 64.
  - `test_pinned_identity_is_held_when_nothing_else_enrolls_the_project` (REQ-02) is the reviewer's counterexample: clean with 1 row at baseline, then the scorecard emptied, replaced with prose, and the row's leading pipe removed. It was observed failing on its assertion (`0 != 1`) in all three sub-cases before the code existed.
  - `test_pinned_file_listing_no_identity_enrolls_nothing` (REQ-02) is the control for the boundary. It passed before the code existed and after.
  - `test_scorecard_that_is_not_utf8_is_a_finding_of_the_audit_not_a_crash` (REQ-02; two sub-cases, a project that pins its rows and a project on the legacy audit), `test_pinned_set_that_is_not_utf8_fails_closed_with_recovery` (REQ-02) and `test_source_that_is_not_utf8_fails_closed_naming_the_row` (REQ-09; skill file and ADR file) were each observed failing because the audit raised.
  - `test_bullet_only_in_a_surface_file_that_is_not_utf8_emits_error` (covers REQ-0.0.33-01-02; AGENTS.md and a rule file) and `test_compressible_with_a_receipt_that_is_not_utf8_fails_closed` (covers REQ-0.0.37-25-03) cover the two decode repairs under other briefs' requirements. Each was observed failing because the audit raised. They have no control in these ten proofs, which are scoped to this brief's requirements.
- The feature gained one scenario tagged @REQ-0.35.0-10-02, "A pinned row is held when nothing but the pinned file enrolls the project", for 8 scenarios, and the steps file gained three steps. The scenario was run against the pre-repair source and observed failing (7 passed, 1 failed), then passing with the repair; the source was restored byte-identical between the two runs.
- `docs/user/manpages/validate.md` and `docs/governance/advisory-rules-audit.md` each now say the pinned file alone decides whether the check runs, and that a scorecard that is not UTF-8 fails closed by name. The manpage also lists the other four undecodable reads and says the legacy audit requires no pinned identity.
- The brief gained a Change Log entry of 2026-10-06 recording the ruling and the repair. No requirement and no allowlist entry changed.
- A first attempt at the commit was refused by the typecheck hook. The repair had changed `_parse_scorecard` to take text, and a dated evidence script outside this brief, `docs/governance/obpi-run-cost-2026-10-03-evidence/trial_eval_probes.py`, imports that private function with a path. The orchestrator's search for callers had covered `src`, `tests`, `features` and `scripts` and missed `docs`. The two readers' signatures were restored and the decode check moved in front of them; the evidence script is untouched.
- Controls: the REQ-02 proof carries 18. Eleven earlier controls are unchanged; of the four added with the round 4 repair, two are rewritten against the new code and one is replaced, because the lines they named were removed; four are new. `pinned-file-no-longer-decides-the-check` is the control that operates at the entry decision round 5 named as the weakest point. The REQ-09 proof gained `undecodable-source-raises`. The fenced block under REQ coverage lists each control and the test it fails.
- The orchestrator ran the round 5 counterexample on a scratch fixture against the repaired source: no ownership declaration, one Mechanical row attributed to `.gzkit/skills/demo/SKILL.md` with matching text, one pinned identity. Observed output follows. The emptied and prose cases each name the lost identity from the pinned file; the leading-pipe case gives two errors, the row refused by name and the lost identity. The independent re-run is round 6's.

```text
baseline: 0 errors, 1 rows
scorecard emptied: 1 errors, 0 rows
scorecard prose: 1 errors, 0 rows
leading pipe removed: 2 errors, 0 rows
scorecard removed: 1 errors, 0 rows
scorecard not utf-8: 1 errors, 0 rows
scorecard a directory: 1 errors, 0 rows
pinned file not utf-8: 1 errors, 1 rows
pinned not utf-8 + scorecard emptied: 1 errors, 0 rows
pinned file a directory: 1 errors, 1 rows
pinned not json + scorecard emptied: 1 errors, 0 rows
pinned removed alone: 1 errors, 1 rows
pinned emptied alone: 1 errors, 1 rows
pinned removed + scorecard emptied: 0 errors, 0 rows
pinned emptied + scorecard emptied: 0 errors, 0 rows
pinned removed + scorecard removed: 0 errors, 0 rows
```

- Scope ruling. After the repair, the baseline and the first proof run, the orchestrator ran single and coordinated edits on a throwaway copy of the live audit inputs at commit 33f36a47e (a `git archive` of the per-turn surfaces, `.gzkit`, the scorecard, the ADR tree and `data`). Observed output follows. Each of the five edits confined to one file returned an error. Four of the five coordinated edits of the scorecard and the pinned file returned none.

```text
live copy, untouched: 0 errors, 178 rows
scorecard emptied alone: 1 errors, 0 rows
scorecard removed alone: 1 errors, 0 rows
pinned file removed alone: 1 errors, 178 rows
pinned list emptied alone: 1 errors, 178 rows
COORDINATED: scorecard removed + pinned file removed: 0 errors, 0 rows
COORDINATED: scorecard emptied + pinned file removed: 1 errors, 0 rows
COORDINATED: scorecard emptied + pinned list emptied: 0 errors, 0 rows
COORDINATED: scorecard removed + pinned list emptied: 0 errors, 0 rows
one row removed alone (local-agent-rules-claude-md-local-agent-rules #7): 1 errors, 177 rows
COORDINATED: one row removed + its identity removed (local-agent-rules-claude-md-local-agent-rules #7): 0 errors, 177 rows
live copy, restored: 0 errors, 178 rows
```

- The boundary was put to the operator with those measurements and four options: out of scope and written into the brief; in scope, with a shrink-only guard on the pinned file before round 6; leave it unruled; or hold. Operator ruling, verbatim selection: "Out of scope, in the brief (Recommended)". The brief now carries a `## Threat Model` section holding the text the operator selected, after the Identity and Reconciliation Contract, and a Change Log entry for the ruling. The section reads:

> The audit holds the scorecard against the pinned row identities and reports any difference between them. An edit confined to the scorecard, or to the pinned file, fails closed.
>
> Out of scope: a change made to both in one edit (a row removed together with its identity; the scorecard emptied or removed together with the pinned list or file). Both are committed files of record, the change is visible as a diff of `data/advisory_scorecard_identities.json`, and deleting an identity follows an operator ruling.
>
> Also out of scope: anyone who can write the project's files of record directly (ledger, corpus, ownership declarations, the pinned file).

- One measured case is narrower than the section's words: with an ownership declaration present, the scorecard emptied together with the pinned file removed still fails closed (1 error), because the declaration sends the project to the strict path. The section rules the class out of scope; the audit catches that member of it.
- Refresh. The Threat Model section is part of the proof contract: adding it made all ten proofs read "stale contract" and "stale inputs". All ten were re-executed against the amended brief. The first run (digest cd893928…, before the section) is superseded; the proof ids in this packet are from the second run, and all ten are valid against digest 829bd985….
- A defect outside this brief was found and recorded as an insight, not repaired: `load_registry` in `src/gzkit/registries.py` raises a raw `UnicodeDecodeError` for a registry that is not UTF-8, where its own docstring promises one exception type. That file is named by Draft brief OBPI-0.39.0-02-tolerance-contract (ADR-0.39.0), so its route is the operator's. This brief's audit catches the error locally for the pinned file.
- Live audit, re-observed this session: 178 rows, 31 answered by the corpus, 147 by the scorecard; zero advisories.

Seven findings were open in the acceptance record when round 6 was dispatched:

| Finding | REQ | Raised | State before round 6 |
|---|---|---|---|
| `codex-035010-attribution-enrollment-bypasses-pins-r5` | 02 | round 5 | repair in 92c12bdd5; closure was round 6's to give |
| `codex-035010-missing-scorecard-bypasses-pins-r4` | 02 | round 4 | closed by round 5 against `proof-f723da05`; needs closure again against `proof-9595e0fa` |
| `codex-035010-leading-pipe-row-dropped-r3` | 02 | round 3 | closed by round 5 against `proof-f723da05`; needs closure again against `proof-9595e0fa` |
| `codex-035010-missing-row-number` | 02 | round 1 | closed by round 5 against `proof-f723da05`; needs closure again against `proof-9595e0fa` |
| `codex-035010-empty-number-cell-dropped-r2` | 02 | round 2 | closed by round 5 against `proof-f723da05`; needs closure again against `proof-9595e0fa` |
| `codex-035010-scorecard-edit-witness` | 06 | round 1 | closed by round 5 against `proof-6811368d`; needs closure again against `proof-b1bdb3e5` |
| `codex-035010-manpage-edit-witness` | 10 | round 1 | closed by round 5 against `proof-030611d7`; needs closure again against `proof-173b4199` |

Round 5 closed six of these against the proofs current then. The re-runs superseded those proofs, so the record lists the six as requiring verified closure again. For REQ-06 and REQ-10 the two documents each gained text about the pinned file deciding the check and about undecodable files; the witness clause and the resolver arm that passes are unchanged. Round 6 was authorized by the operator's ruling "A, but we need a h/o and git sync" and was the fifth round past the first, three more than the standing bound of two follow-ups.

Round 6 — Codex (tier 1), reviewer id `codex-independent-035010-round6`, receipt `arb-step-codexadversary-60bd7975823d4d7182d839b10f419579`, reviewed commit d14696086 in a disposable checkout (source digest 3701abf97a84…), dispatched 09:13Z and returned 09:26Z on 2026-10-06. Verdict CORROBORATED-WITH-CAVEATS, token not-refuted; the review object's verdict is accepted. It approved all ten current proofs, recorded 28 replays (every control failed its nominated tests on their own assertions; source restored), ran the 71 module tests, raised no finding, and closed all seven findings above against the current proof ids. The review is imported.

What the reviewer reported observing, in its own figures (errors / rows / corpus-resolved):

- The round 5 counterexample, on a fixture it built itself with no ownership declaration: 0/1/0 at baseline; the scorecard emptied and the scorecard replaced with prose each 1/0/0 naming `fixture-contract #1`; the leading pipe removed 2/0/0 naming the unreadable row and the missing pinned identity; the pinned file's hash unchanged throughout. Control `pinned-file-no-longer-decides-the-check` failed all three sub-cases on its own assertion.
- The four earlier REQ-02 counterexamples on the live scorecard: the scorecard moved aside 1/0/0 naming the scorecard, 178 pinned identities and the pinned path; Local Agent Rules row 7 with its leading pipe removed, with its prefix replaced by `|   |`, and by `||`, each 2/177/30 naming the unreadable line and the lost row 7 identity. The scorecard was restored to its hash after each.
- No clean result reachable with identities pinned and a pinned identity lost, on the paths it read and probed: a missing scorecard returns an error, an undecodable scorecard returns an error, and every remaining path reaches the identity check.
- Positive direction: both no-scorecard variants with nothing pinned returned 0/0/0, and both legacy variants returned 0/3/0 with their text retained and the expected two retention findings with it removed.
- Decode: a scorecard that is not UTF-8 returned exactly one named finding on live and on legacy data; skill text that is not UTF-8 named its row and source. It judged the `self.fail` form of the three proof-bound decode tests an honest assertion of the required behavior, and an unreadable pinned file forcing the strict read appropriate fail-closed behavior.
- It treated no coordinated edit of the scorecard and the pinned file as a finding, and identified no requirement that contradicts the operator-selected Threat Model.
- Packet cross-check: it found no independently checked packet claim false.

What it could not confirm: the reviewed commit, its ancestry and clean-tree state, and historical byte equality of the corpus prefix, because the checkout has no git metadata; the six quality receipts and the results they record (the full suite, lint, typecheck, the docs build, behave), because the receipt files are not in the checkout; behave, which it read and did not run; the written-first chronology and the recorded `present-evidence`, precomplete and brief-drift outcomes. It did not recompute the input digest or the workspace digest.

The reviewer named the weakest point: historical byte preservation for REQ-0.35.0-10-05, which the current prefix fingerprints and append events corroborate but which a checkout with no git history cannot compare against earlier bytes. It called that a verification gap, not a counterexample. It is a different root from rounds 4 and 5, which both named an entry decision made before the pinned check.

After round 6 the acceptance status reads ready, with no blocker and no open finding; `present-evidence` exits 0 with attestable true and both blocker lists empty; precomplete exits 0 with all eleven checks passing. The reviewer's disposable checkout was deleted; its report and logs were copied out first and are not in the repository.

**Limits and disclosures**

- Single driver: the implementation and the first three repairs were done by one session under the operator-ruled 2026-10-03 trial declaration. No implementer, spec-reviewer or quality-reviewer subagent was dispatched, for the round 3 repair as for the two before it. The declaration is on the ledger. Continuing single-driver for those three repairs was the agent's choice and is unreviewed by the operator. The round 4 repair was also done by one session under the 2026-10-03 declaration, the fourth repair so; that is also unreviewed by the operator. The round 5 repair was also done by one session under the 2026-10-03 declaration, the fifth repair so. The orchestrator asked the operator, when presenting the handoff, whether this repair should run single-driver or with dispatch; the operator answered "proceed" and did not choose. Continuing single-driver is the orchestrator's reading of the recorded declaration.
- The RED falsifiability witness (`gz arb red`) was run for all seven BEHAVIOR REQs and returned failure_class=error on a reconstructed base for every one. That is inconclusive, not a RED. The executed proof records with killed controls are the evidence that each test can fail. For REQ-0.35.0-10-02 the witness was run once more in this session, before the repair commit (`uv run gz arb red --req REQ-0.35.0-10-02`): it used a reconstructed base (2136c07888be) and returned failure_class=error, which is inconclusive; receipt `arb-red-REQ-0.35.0-10-02-5e63772bebc34ff9a2abff163591b6ba`. It was not run for the other REQs this session.
- The plan was written after the implementation and is labelled so.
- The proof specifications were rebuilt from the ledger's newest proof record per requirement (selectors, source, mutations). For the run on 2346d91c5 the REQ-02 specification was then extended by the orchestrator with the four new tests, the renamed live test and four new controls; the other nine were reused unchanged. For the run on the tree repaired by 4839e2cf1 the REQ-02 specification was extended by the orchestrator with the three new tests and four new controls; the other nine specifications were rebuilt from the ledger's newest record per requirement and reused unchanged. For the runs on the tree repaired by 92c12bdd5 the REQ-02 and REQ-09 proof specifications were extended by the orchestrator (REQ-02: four new tests, three rewritten controls, four new controls; REQ-09: one new test, one new control); the other eight were rebuilt from the round 5 specifications and reused unchanged. Each mutation's find text was confirmed present exactly once in the source before running. The current run carries the trial's controls, the REQ-02 controls added with the round 2 repair, the four added with the round 3 repair, the four added with the round 4 repair (one unchanged, two rewritten, one replaced) and the five added with the round 5 repair (four for REQ-02, one for REQ-09). Whether each control expresses its requirement is for the independent reviewer to judge.
- The fourth test written first for the round 3 repair, `test_missing_or_unreadable_pinned_set_fails_closed_with_recovery`, first failed on an unhandled exception, not an assertion.
- Of the three tests written first for the round 4 repair, `test_project_with_no_scorecard_and_nothing_pinned_has_nothing_to_audit` passed before the code existed and after; it was not observed failing first. In the current run controls `unpinned-project-demands-a-pinned-file` and `empty-pinned-list-enrolls-the-project`, which replaces `empty-pinned-set-refused`, each fail it.
- Of the seven tests written first for the round 5 repair, `test_pinned_file_listing_no_identity_enrolls_nothing` passed before the code existed and after; it was not observed failing first. Control `empty-pinned-list-enrolls-the-project` fails it.
- The five decode tests were observed failing because the audit raised, not on a value assertion. Each wraps the call so that a raise becomes an assertion failure; that is what lets a control count as killed on an assertion.
- An unreadable pinned file counts as pinning. That keeps the round 4 behaviour (an absent scorecard with an unreadable pinned file fails closed) and means a project with no declaration, no attribution and a corrupt pinned file is read strictly, not by the legacy audit.
- The scorecard is now read up to three times in one audit (the decode check, the legacy reader, the strict reader). The readers' signatures were kept so the dated evidence script outside this brief still imports.
- The pinned-file decode error is caught in this module, not at its source in `src/gzkit/registries.py`, which is outside this brief. Recorded as an insight.
- The two decode repairs under other briefs' requirements (the per-turn surface files and the advisor-QC receipt) have tests in the module and the full suite and no control in these ten proofs.
- The orchestrator did not re-run the round 3 counterexample on the repaired tree outside the test suite.
- The orchestrator's re-run of the round 4 counterexample used a copy assembled from the live files, not the reviewer's checkout.
- The orchestrator's counterexample runs after the round 5 repair used scratch fixtures and a `git archive` copy of the live inputs, not the round 5 reviewer's checkout.
- `audited_population` still returns no rows for an absent scorecard. That is a statement of what was read, and the failure is reported by `validate_bullet_retention`; the round 5 reviewer judged that it reports what was read (see Review history).
- A change made to the scorecard and the pinned file in one edit can pass clean. On a copy of the live inputs at 33f36a47e, one row removed together with its identity, the scorecard emptied or removed together with the pinned list emptied, and the scorecard removed together with the pinned file removed each returned 0 errors. This boundary is now ruled by the operator (verbatim selection: "Out of scope, in the brief (Recommended)") and written into the brief's Threat Model. One measured member of the class still fails closed: with an ownership declaration present, the scorecard emptied together with the pinned file removed returns 1 error.
- The error for an absent scorecard gives the count of pinned identities and does not list them.
- The pinned set is an equality check: it names a row that leaves or arrives, and it cannot say whether deleting an identity from the file was ruled. That deletion is visible only as a diff of a committed file.
- The pinned file was seeded by the audit's own reader; its independence rests on being committed, on round 3's independent confirmation of the 178-row population, and on the crude cross-check described under "After round 3".
- `data/config_registry.json` joined the allowlist on the orchestrator's reading of the ruling.
- Round 4 ran past the two-follow-up round bound, on the operator's ruling.
- Round 5 ran past the two-follow-up bound, on the operator's ruling.
- Round 6 ran past the two-follow-up bound, on the operator's ruling.
- The round 6 paragraphs of the Review history, the sentence on round 6 in the Value Narrative, the two after-round-6 rows of the Quality checks table and section 4 were written by the orchestrator from the reviewer's report and the commands it re-ran, not by the narrator.
- The round 6 reviewer could not authenticate the six quality receipts, did not rerun the full suite, lint, typecheck, the docs build or behave, and could not check commit ancestry or historical byte equality; it lists each under what it could not confirm. Its weakest point, historical byte preservation for REQ-0.35.0-10-05, is such a gap.
- The round 6 reviewer's full report (its checks with pasted output) lived in its disposable checkout. The orchestrator copied the report and logs to its session scratch directory before deleting the checkout; they are not committed. The review object and its 28 replay records are in the ledger through the receipt.
- The round 5 paragraphs of the Review history and the sentence describing the round 5 finding in the Value Narrative were written by the orchestrator from the reviewer's report and its own reproduction, not by the narrator. The narrator revised the packet after the round 5 repair from the orchestrator's record of observed facts, checked against the brief, the source, the tests and the acceptance status; the narrator ran no test, validator or `gz` command.
- Rounds 4 and 5 were given that boundary as the orchestrator's statement, before the ruling existed: each was told that a coordinated edit of the scorecard and the pinned file is out of scope, and round 5 also that a coordinated removal of both is. The round 5 reviewer's finding uses neither statement.
- The Threat Model section and its Change Log entry were written after the six receipts. They change the brief only; all ten proofs were re-executed against the amended brief.
- The round 5 reviewer could not authenticate the six quality receipts, which are not in its checkout, and did not rerun the full suite, lint, typecheck, the docs build or behave.
- The docs changed in 2346d91c5 say a pinned identity the audit no longer reads fails closed; round 4 showed that was not true when the scorecard file itself is absent. The round 4 repair makes it true for an absent scorecard, and both documents now state that case. After the round 5 repair both documents also say the pinned file alone decides whether the check runs.
- The six receipts of this run read clean: each was recorded on commit 33f36a47e with a clean tree and its git field reads dirty false. The receipts of the run before round 5 (a6fe3e0d6) also read clean; this packet recorded then that the receipts of the run before that read dirty.
- The 31-row mapping was accepted by the operator on a text-match measurement: 25 verbatim-contained, 6 paraphrases, all six paraphrases Judgment in both surfaces. The 25 were not re-derived beyond the text match.
- The resolver module is now 922 lines against a 600-line authoring guidance that nothing gates (885 before this repair).
- Pythonic #22 and Data Models #27 are scored Mechanical with no property-level witness and remain invisible to the advisory-scorecard scope. This is recorded as an insight, outside this brief.
- The baseline was re-run on a tree that also carries a Python patch upgrade (3.13.16) and a refreshed lockfile, neither part of this OBPI. The tree of this run also carries the file-lock fix eeb4f2758, not part of this OBPI; two of the 11476 tests are its.
- The reviewer's checkout has no git metadata; in rounds 1 and 2 it could not check commit ancestry or historical byte equality.
- The narrator found the brief's atomicity note for REQ-0.35.0-10-05 saying the live corpus needed no change, after twelve rows had been appended. The note was corrected before the first revision of this packet was replayed.

**4. Awaiting attestation.** Step 4b round 6 accepted the current state and the acceptance status reads ready. Stage 5 does not start until the operator responds.
