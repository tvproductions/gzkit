## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

Before, the classification field of a corpus entry was schema-required and part of the baseline identity fingerprint, and nothing in `src/` read it; the binding copy of the same concept was a hand-maintained markdown table (`docs/governance/advisory-rules-audit.md`). Now `uv run gz validate --bullet-retention` reads an owned row's class from the corpus entry it cites and an unowned row's from the scorecard, fails closed on a broken owned mapping, refuses to bind an owned section that holds a live Ambiguous entry, and retains a row attributed to a SKILL.md or an ADR file against that file. On the live repo 173 scorecard rows are audited, 31 answered by the corpus and 142 by the scorecard; six owned rows disagreed between the two surfaces, the operator ruled on 2026-10-05 that the corpus adopts the scorecard class, and after the reconciliation the audit prints zero advisories.

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

Executed proof record `proof-8f28374cf329416a8af803c2dee2bbd6` (REQ-0.35.0-10-03): with the production line that binds the corpus class replaced by one that binds the scorecard class (control `scorecard-class-binds-owned-row`), `test_corpus_change_alone_changes_the_verdict` failed on its assertion; with the disagreement report silenced (control `disagreement-silenced`), the other two tests failed; the source was restored and the tests were green afterwards.

**3. Evidence**

**Quality checks:**

| Check | Command | Result |
|---|---|---|
| Lint | `uv run gz arb ruff` | exit 0; `arb-ruff-9a63461499704f3188d3dfc8e3fd0476` |
| Typecheck | `uv run gz arb typecheck` | exit 0; `arb-step-typecheck-633060176b264272a96f8959b70a5558` |
| Tests (full suite) | `arb:unittest` | 11455 tests, OK, 7 skipped; `arb-step-unittest-f5fdef8ed36244e5aba245db3214e7f5` |
| Docs | `arb:mkdocs` | exit 0; `arb-step-mkdocs-f015095c9381479c8d85a9fc1a598e52` |
| Behave | `arb:behave` | 5 scenarios passed, 0 failed; `arb-step-behave-c9665e00a2794e06b82bb82ed461fc95` |
| OBPI tests | `arb:obpi-tests` | 52 tests OK; `arb-step-unittest-0b9faf606a17499184f1f2e58df84c01` |
| Validation scopes | `validate:scopes` | six scopes, each exit 0; no receipt |
| REQ coverage | `covers` | 10 REQs; behavior_uncovered_reqs 0 |
| Precomplete | `uv run gz obpi precomplete` | every check passes except adversarial_validation, which waits on Step 4b |

All six receipts record exit_status 0 and were recorded after the lock claim. `arb:obpi-tests` ran before the corpus reconciliation; `arb:unittest` (the full suite) ran after it. The three REQs without a covering test are the two SUPPORT REQs and the STRUCTURAL-FENCE REQ, by proof channel.

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
# covers
uv run gz covers OBPI-0.35.0-10-classification-reader-and-ownership --json
```

**Files created:**

Commit 4893b7321 (2026-10-03, the single-session trial):

- `features/classification_ownership.feature` (5 Gate 4 scenarios)
- `features/steps/classification_ownership_steps.py` (the steps for those scenarios)

**Files modified:**

Commit 4893b7321:

- `src/gzkit/governance/trust_audits/bullet_retention.py` (the resolver, the mapping fence, the Ambiguous fence, source-aware retention; 674 lines)
- `tests/governance/test_bullet_retention.py` (six new test classes)
- `src/gzkit/content/models/corpus.py` (docstring only)
- `docs/user/manpages/validate.md` (classification source and source-aware retention)
- `docs/governance/advisory-rules-audit.md` (narrowed authority; a source attribution on every row)

2026-10-05 (commits 7c05949ee and 3c53720ab, and the commit that carries this packet):

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` (Decision item 9 amended to carry the retention scope, operator-ruled)
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (REQ-10 witness clause, Allowed Paths bullet split, third Demo command, the REQ-05 atomicity note, Change Log)
- `.gzkit/corpus/AGENTS.md.jsonl` (12 rows appended: 6 retractions, 6 re-captures; the 487 earlier rows byte-identical)
- `.gzkit/renditions/AGENTS.md/root.corpus.json` (provenance refreshed; root rendition and `AGENTS.md` byte-unchanged)
- `docs/governance/advisory-rules-audit.md` (six rows repointed to the new entry ids)
- `.claude/plans/classification-reader-and-ownership-OBPI-0.35.0-10.md` (plan, written after implementation and labelled so)

**REQ coverage:**

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|---|---|---|---|---|---|
| REQ-0.35.0-10-01 | BEHAVIOR | 3 tests; 2 controls killed | `TestOwnedBulletResolvesFromCorpus` | `proof-8ed3d69d` | behavioral proof valid |
| REQ-0.35.0-10-02 | BEHAVIOR | 7 tests; 2 controls killed | `TestUnownedBulletResolvesFromScorecard` | `proof-92d2622c` | behavioral proof valid |
| REQ-0.35.0-10-03 | BEHAVIOR | 3 tests; 2 controls killed | `TestOwnedDisagreementIsReported` | `proof-8f28374c` | behavioral proof valid |
| REQ-0.35.0-10-04 | BEHAVIOR | 5 tests; 2 controls killed | `TestCaptureDefaultNeverBinds` | `proof-53b950ce` | behavioral proof valid |
| REQ-0.35.0-10-05 | BEHAVIOR | 1 test; 1 control killed | `TestReconciliationIsAppendOnly` | `proof-794a8cf9` | behavioral proof valid |
| REQ-0.35.0-10-06 | SUPPORT | `resolve_support_proof` | `artifact_edited` + `--documents` | `proof-6f7cd6b4` | pass |
| REQ-0.35.0-10-07 | STRUCTURAL-FENCE | `resolve_fence_proof` | ADR-0.35.0 BI-04 | `proof-9466151a` | pass |
| REQ-0.35.0-10-08 | BEHAVIOR | 2 tests; 1 control killed | `TestDeclaredSourceRetention` | `proof-450c798d` | behavioral proof valid |
| REQ-0.35.0-10-09 | BEHAVIOR | 1 test; 1 control killed | `TestDeclaredSourceRetention` | `proof-97649539` | behavioral proof valid |
| REQ-0.35.0-10-10 | SUPPORT | `resolve_support_proof` | `artifact_edited` + `--documents` | `proof-fef990d7` | pass |

```text
Test file for every BEHAVIOR row: tests/governance/test_bullet_retention.py
All ten proof records are valid against input digest aed47c90d763…

REQ-0.35.0-10-01  proof-8ed3d69d50ea4417a34a6db3b04926f9
  killed controls: scorecard-class-binds-owned-row, wrong-section-entry-binds
REQ-0.35.0-10-02  proof-92d2622c44e74bdea41f176c48c12a5f
  killed controls: duplicate-identity-accepted, unowned-section-demands-corpus-entry
REQ-0.35.0-10-03  proof-8f28374cf329416a8af803c2dee2bbd6
  killed controls: disagreement-silenced, scorecard-class-binds-owned-row
REQ-0.35.0-10-04  proof-53b950cea3cd4a50a82989386aae9880
  killed controls: capture-default-binds, unloadable-ownership-falls-back-to-scorecard
REQ-0.35.0-10-05  proof-794a8cf9ece24eadb21d401653475573
  killed controls: fence-reads-raw-log
REQ-0.35.0-10-06  proof-6f7cd6b4dac34a7593eb11ae3e41df41
  SUPPORT: ledger event artifact_edited citing docs/governance/advisory-rules-audit.md,
  plus `uv run gz validate --documents`
REQ-0.35.0-10-07  proof-9466151a397e4bc6b8d6cb98a09ab4f8
  STRUCTURAL-FENCE: Boundary Invariants of ADR-0.35.0-canon-entry-corpus-landing, BI-04;
  audited at ADR closeout
REQ-0.35.0-10-08  proof-450c798db98b4b45a793be81b4896f3e
  killed controls: declared-source-checked-against-surface
REQ-0.35.0-10-09  proof-976495390ffe467e9570d4521748ca7b
  killed controls: absent-text-reads-as-retained
REQ-0.35.0-10-10  proof-fef990d7255642319f1c7acecdcb293f
  SUPPORT: ledger event artifact_edited citing docs/user/manpages/validate.md,
  plus `uv run gz validate --documents`

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

**Limits and disclosures**

- The RED falsifiability witness (`gz arb red`) was run for all seven BEHAVIOR REQs and returned failure_class=error on a reconstructed base for every one. That is inconclusive, not a RED. The executed proof records with killed controls are the evidence that each test can fail.
- The implementation was a single-session trial (operator-ruled 2026-10-03). No implementer, spec-reviewer or quality-reviewer subagent was dispatched. The declaration is on the ledger.
- The plan was written after the implementation and is labelled so.
- The ten proof specifications reuse the trial's controls, recovered from the ledger's earlier proof records. Whether each control expresses its requirement is for the independent reviewer to judge.
- The 31-row mapping was accepted by the operator on a text-match measurement: 25 verbatim-contained, 6 paraphrases, all six paraphrases Judgment in both surfaces. The 25 were not re-derived beyond the text match.
- The source module is 674 lines against a 600-line authoring guidance that nothing gates.
- The `arb:obpi-tests` receipt (52 tests) was recorded before the corpus reconciliation. The full-suite receipt was recorded after it.
- The narrator found the brief's atomicity note for REQ-0.35.0-10-05 saying the live corpus needed no change, after twelve rows had been appended. The note was corrected before this packet was replayed.
- Step 4b (independent review by Codex) has not run when this packet is written.

**4. Awaiting attestation.** Step 4b (independent review) runs before attestation is solicited.
