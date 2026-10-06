## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

Before, the classification field of a corpus entry was schema-required and part of the baseline identity fingerprint, and nothing in `src/` read it; the binding copy of the same concept was a hand-maintained markdown table (`docs/governance/advisory-rules-audit.md`). Now `uv run gz validate --bullet-retention` reads an owned row's class from the corpus entry it cites and an unowned row's from the scorecard, fails closed on a broken owned mapping, refuses to bind an owned section that holds a live Ambiguous entry, and retains a row attributed to a SKILL.md or an ADR file against that file. An enrolled project's audit now also refuses, by name, any rule-table row it cannot read; before the round 2 repair such a row was dropped with no error. On the live repo 178 scorecard rows are audited, 31 answered by the corpus and 147 by the scorecard; six owned rows disagreed between the two surfaces, the operator ruled on 2026-10-05 that the corpus adopts the scorecard class, and the audit prints zero advisories.

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

Executed proof record `proof-1a0b6a5d16d346e1abf5fccc1ffa9d4e` (REQ-0.35.0-10-03): with the disagreement report silenced (control `disagreement-silenced`), two of the three tests failed on their assertions (`test_disagreement_names_the_row_the_entry_and_both_values` and `test_scorecard_change_alone_never_changes_the_verdict`); with the production line that binds the corpus class replaced by one that binds the scorecard class (control `scorecard-class-binds-owned-row`), all three failed on their assertions; the source was restored and the tests were green afterwards.

**3. Evidence**

**Quality checks:**

| Check | Command | Result |
|---|---|---|
| Lint | `uv run gz arb ruff` | exit 0; `arb-ruff-7e9fffa140324cc9a53200c7a34a65a9` |
| Typecheck | `uv run gz arb typecheck` | exit 0; `arb-step-typecheck-6dc81edb9b2548ec99883565620503a6` |
| Tests (full suite) | `arb:unittest` | 11460 tests, OK, 7 skipped; `arb-step-unittest-f9af9a050a58424a8924cb970c2680a2` |
| Docs | `arb:mkdocs` | exit 0; `arb-step-mkdocs-7179dd7b8871480298491651bba80ccd` |
| Behave | `arb:behave` | 1 feature, 5 scenarios, 32 steps passed, 0 failed; `arb-step-behave-d4f94e9d48714883a169827d2300999c` |
| OBPI tests | `arb:obpi-tests` | 57 tests OK; `arb-step-unittest-8774adeeb8984199b189ecd9de1af549` |
| Validation scopes | `validate:scopes` | eight scopes, each exit 0; no receipt |
| REQ coverage | `covers` | 10 REQs; uncovered_reqs 3; behavior_uncovered_reqs 0 |
| Brief drift | `brief-drift` | clean; deltas all 0 |
| Evidence packet | `present-evidence` | exit 3; attestable false; blocked only on the four open findings; three Demo commands exit 0 |
| Precomplete | `precomplete` | exit 3; eight checks pass; adversarial_validation waits on Step 4b |

All six receipts record exit_status 0 and were recorded in this session (2026-10-06 UTC) on commit e59763ff9 with a clean tree; the commit that carries this revision of the packet sits on top of it. The three REQs without a covering test are the two SUPPORT REQs and the STRUCTURAL-FENCE REQ, by proof channel. `present-evidence` exits 3 because four findings await independent closure (see Review history): its `blockers` list holds those four and nothing else, and its `review_blockers` list adds that each of the ten current proofs still lacks an accepted independent review, which is what round 3 supplies. Precomplete passes brief_readiness, reconcile_idempotent, lock_held, arb_receipts, plan_audit_receipt, brief_headings, behave_req_coverage and task_envelope_coherence, and fails adversarial_validation for the same reason.

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

- `features/classification_ownership.feature` (5 Gate 4 scenarios)
- `features/steps/classification_ownership_steps.py` (the steps for those scenarios)

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

- `src/gzkit/governance/trust_audits/bullet_retention.py` (an enrolled project's scorecard is re-read strictly: every line of a `| # | Rule | Score |` table, or of a pipe block with no header row, is a row, and one that cannot be read is a named failure; an escaped pipe is cell text; a Score cell is read by the bold class it leads with; the round 1 guard is subsumed and removed; an unenrolled project keeps the legacy reading; 773 lines)
- `tests/governance/test_bullet_retention.py` (strict-reader tests written first and observed failing on their assertions; the live-population oracle rewritten to read rule tables structurally, independent of the audit's row grammar; 57 tests, up from 53)
- `docs/governance/advisory-rules-audit.md` (five rows requoted to verbatim rule-file wording and attributed: Pythonic #22, Data Models #27, Model Selection #52, Map Doctrine #58, Changelog #65)
- `docs/user/manpages/validate.md` (states that every line of a rule table is a row, that an unreadable one fails closed, that a literal pipe is written escaped, and that a score cell is read by the class it leads with)
- `data/mechanical_witness_grandfather.json` (Model Selection #52 added as frozen witness debt; shrink-only baseline 64 to 65)
- `data/waiver_ratchet_registry.json` (that list's baseline count, 64 to 65)
- `data/waiver_identity_baseline.json` (the authorization record for the new identity, carrying the operator's ruling verbatim)
- the brief, in commit 23bbca489 (the three `data/` files join the allowlist by the same ruling; Change Log entries for round 2 and its three rulings)

Not part of this OBPI: two later commits sit between ca8ab6534 and e59763ff9. Commit 6396fb3cc upgrades Python to 3.13.16, refreshes `uv.lock`, removes wily and edits four workflow files. Commit 6268e2398 retires two duplicate tests elsewhere in `tests/` and regenerates `data/tautological_test_baseline.json`. Neither touches a file on this brief's allowlist. The input digest the proofs are bound to changed after ca8ab6534, which is why all ten proofs were re-run on e59763ff9.

**REQ coverage:**

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|---|---|---|---|---|---|
| REQ-0.35.0-10-01 | BEHAVIOR | 3 tests; 2 controls killed | `TestOwnedBulletResolvesFromCorpus` | `proof-4c2b83db` | behavioral proof valid |
| REQ-0.35.0-10-02 | BEHAVIOR | 12 tests; 6 controls killed | `TestUnownedBulletResolvesFromScorecard` | `proof-e63644fb` | behavioral proof valid |
| REQ-0.35.0-10-03 | BEHAVIOR | 3 tests; 2 controls killed | `TestOwnedDisagreementIsReported` | `proof-1a0b6a5d` | behavioral proof valid |
| REQ-0.35.0-10-04 | BEHAVIOR | 5 tests; 2 controls killed | `TestCaptureDefaultNeverBinds` | `proof-6f71bc53` | behavioral proof valid |
| REQ-0.35.0-10-05 | BEHAVIOR | 1 test; 1 control killed | `TestReconciliationIsAppendOnly` | `proof-b9b05fe6` | behavioral proof valid |
| REQ-0.35.0-10-06 | SUPPORT | `resolve_support_proof` | file on disk + `--documents` | `proof-e6cac2bc` | pass |
| REQ-0.35.0-10-07 | STRUCTURAL-FENCE | `resolve_fence_proof` | ADR-0.35.0 BI-04 | `proof-2d3f902d` | pass |
| REQ-0.35.0-10-08 | BEHAVIOR | 2 tests; 1 control killed | `TestDeclaredSourceRetention` | `proof-bc7ce593` | behavioral proof valid |
| REQ-0.35.0-10-09 | BEHAVIOR | 1 test; 1 control killed | `TestDeclaredSourceRetention` | `proof-41146872` | behavioral proof valid |
| REQ-0.35.0-10-10 | SUPPORT | `resolve_support_proof` | file on disk + `--documents` | `proof-17e05a06` | pass |

```text
Test file for every BEHAVIOR row: tests/governance/test_bullet_retention.py
All ten proof records are valid against input digest 9f528228c9e5…
Every control below: outcome killed, failure_class assertion; source sha256 restored;
restored run green.

REQ-0.35.0-10-01  proof-4c2b83db6a9b498c9fb6f995ccef3aba
  killed controls: scorecard-class-binds-owned-row, wrong-section-entry-binds
REQ-0.35.0-10-02  proof-e63644fb4f4c43e085ba9c50d9078096
  killed controls: duplicate-identity-accepted, unowned-section-demands-corpus-entry,
  unreadable-row-skipped, escaped-pipe-splits-cell, score-qualifier-refused,
  any-table-read-as-rules
  The round 1 control blank-row-number-accepted no longer exists: the guard it mutated
  was subsumed by the strict reader and removed in ca8ab6534. unreadable-row-skipped
  fails test_missing_row_number_fails_closed_naming_the_row and
  test_unreadable_rule_row_fails_closed_and_is_never_skipped.
REQ-0.35.0-10-03  proof-1a0b6a5d16d346e1abf5fccc1ffa9d4e
  killed controls: disagreement-silenced, scorecard-class-binds-owned-row
REQ-0.35.0-10-04  proof-6f71bc532bfd41bf961b8050bf7f1a38
  killed controls: capture-default-binds, unloadable-ownership-falls-back-to-scorecard
REQ-0.35.0-10-05  proof-b9b05fe632a74457b42ea60241f31334
  killed controls: fence-reads-raw-log
REQ-0.35.0-10-06  proof-e6cac2bc017843909ace54611d1520fb
  SUPPORT: the witness clause names artifact_edited citing docs/governance/advisory-rules-audit.md.
  No ledger event cites that path. The resolver passed on its second arm: the cited file
  exists on disk and `uv run gz validate --documents` admits it.
REQ-0.35.0-10-07  proof-2d3f902d4dbb4913b3cf2f6cac1ee465
  STRUCTURAL-FENCE: Boundary Invariants of ADR-0.35.0-canon-entry-corpus-landing, BI-04;
  audited at ADR closeout
REQ-0.35.0-10-08  proof-bc7ce59362484fac9848be0c4807109a
  killed controls: declared-source-checked-against-surface
REQ-0.35.0-10-09  proof-41146872d32f4742b1271f92669cf2e2
  killed controls: absent-text-reads-as-retained
REQ-0.35.0-10-10  proof-17e05a06912a4847a9b4af6db32e2269
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

The reviewer also named the weakest point: the REQ-02 population test derives its expected identities from the same scorecard it audits. The round 1 repair closed the blank-number case it demonstrated; a pinned baseline of identities was not added.

Round 2 — Codex (tier 1), reviewer id `codex-independent-035010-round2`, receipt `arb-step-codexadversary-89c8da29860546c38621432ec67acf05`, reviewed commit 1ef19594e. Verdict refuted. That receipt is a re-emission: the first emission, `arb-step-codexadversary-7ad9ace1ea1e488390fa039a0847de2a`, was refused by the importer because it relisted an existing finding id with new text, and the reviewer was asked for a formatting-only re-emission with no judgment changed. It approved 9 of 10 proofs, with 9 replay records, and closed the two SUPPORT findings. It left `codex-035010-missing-row-number` open and raised `codex-035010-empty-number-cell-dropped-r2` (REQ-02): replacing the prefix `| 7 |` with `||` produced zero errors, 172 audited rows and 30 corpus-resolved rows, because the row grammar dropped a truly empty cell before the identity check ran. It named the same weakest point as round 1: the live population test took its expected identities from the scorecard it audits.

After round 2 (rulings are verbatim in the brief's Change Log entries of 2026-10-05):

- The orchestrator measured five malformed row shapes dropped the same way and took the design to the operator instead of a third patch. Operator ruling, verbatim: "A" — fail closed on any unparseable rule-table row.
- Repair (ca8ab6534): an enrolled project's scorecard is re-read strictly; every line of a `| # | Rule | Score |` table, or of a pipe block with no header row, is a row, and one that cannot be read is a named failure; an escaped pipe is cell text; the round 1 guard is subsumed and removed; an unenrolled project keeps the legacy reading. Tests were written first and observed failing on their assertions.
- The test oracle for the live population was rewritten to read rule tables structurally, independent of the audit's row grammar. No pinned baseline of identities was added; the round 2 reviewer said REQ-02 does not require one.
- The strict reader surfaced five live rows that had never been audited: Pythonic #22, Data Models #27 and Model Selection #52 (escaped pipes in the rule cell), Map Doctrine #58 and Changelog #65 (a Score cell carrying two classes). Operator ruling, verbatim selection: "A: Apply as drafted (Recommended)". Each was requoted to verbatim rule-file wording and attributed. The audited population went from 173 to 178 rows; no identity was removed.
- Model Selection #52 was frozen as witness debt; the shrink-only baseline moved from 64 to 65. Operator ruling, verbatim selection: "A: Freeze as missed debt (Recommended)".

Four findings are open in the acceptance record:

| Finding | REQ | Raised | State |
|---|---|---|---|
| `codex-035010-missing-row-number` | 02 | round 1 | left open by round 2; repair landed in ca8ab6534; closure is the reviewer's |
| `codex-035010-empty-number-cell-dropped-r2` | 02 | round 2 | repair landed in ca8ab6534; closure is the reviewer's |
| `codex-035010-scorecard-edit-witness` | 06 | round 1 | closed by round 2 against `proof-719f97b9`; needs closure again against `proof-e6cac2bc` |
| `codex-035010-manpage-edit-witness` | 10 | round 1 | closed by round 2 against `proof-d17394e4`; needs closure again against `proof-17e05a06` |

The two SUPPORT findings reappear only because the re-run superseded the proofs round 2 closed them against; the acceptance record requires verified closure against the current proof ids. Nothing about those two requirements changed, and this packet's wording for them is what round 2 closed.

Round 3 is the last permitted round (two follow-ups after round 1). It has not run when this revision is written.

**Limits and disclosures**

- Single driver: the implementation and both repairs were done by one session under the operator-ruled 2026-10-03 trial declaration. No implementer, spec-reviewer or quality-reviewer subagent was dispatched. The declaration is on the ledger. Continuing single-driver for the two repairs was the agent's choice and is unreviewed by the operator.
- The RED falsifiability witness (`gz arb red`) was run for all seven BEHAVIOR REQs and returned failure_class=error on a reconstructed base for every one. That is inconclusive, not a RED. The executed proof records with killed controls are the evidence that each test can fail.
- The plan was written after the implementation and is labelled so.
- The proof specifications were rebuilt from the ledger's newest proof record per requirement (selectors, source, mutations). They reuse the trial's controls and the REQ-02 controls added with the round 2 repair. Each mutation's find text was confirmed present exactly once in the source before running. Whether each control expresses its requirement is for the independent reviewer to judge.
- The 31-row mapping was accepted by the operator on a text-match measurement: 25 verbatim-contained, 6 paraphrases, all six paraphrases Judgment in both surfaces. The 25 were not re-derived beyond the text match.
- The resolver module is 773 lines against a 600-line authoring guidance that nothing gates.
- Pythonic #22 and Data Models #27 are scored Mechanical with no property-level witness and remain invisible to the advisory-scorecard scope. This is recorded as an insight, outside this brief.
- The baseline was re-run on a tree that also carries a Python patch upgrade (3.13.16) and a refreshed lockfile, neither part of this OBPI.
- The reviewer's checkout has no git metadata; in rounds 1 and 2 it could not check commit ancestry or historical byte equality.
- The narrator found the brief's atomicity note for REQ-0.35.0-10-05 saying the live corpus needed no change, after twelve rows had been appended. The note was corrected before the first revision of this packet was replayed.

**4. Awaiting attestation.** Step 4b round 3 (independent review, the last permitted round) runs before attestation is solicited.
