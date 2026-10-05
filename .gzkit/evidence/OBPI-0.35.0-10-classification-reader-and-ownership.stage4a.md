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

Executed proof record `proof-3828d9e64a4b4910a6079338508de753` (REQ-0.35.0-10-03): with the production line that binds the corpus class replaced by one that binds the scorecard class (control `scorecard-class-binds-owned-row`), `test_corpus_change_alone_changes_the_verdict` failed on its assertion; with the disagreement report silenced (control `disagreement-silenced`), the other two tests failed; the source was restored and the tests were green afterwards.

**3. Evidence**

**Quality checks:**

| Check | Command | Result |
|---|---|---|
| Lint | `uv run gz arb ruff` | exit 0; `arb-ruff-186b806c47494166ae2fa5d105a428c0` |
| Typecheck | `uv run gz arb typecheck` | exit 0; `arb-step-typecheck-7cc73ee1581b49df92c24f605784c503` |
| Tests (full suite) | `arb:unittest` | 11456 tests, OK, 7 skipped; `arb-step-unittest-db420c449325416cb9f99d8440e8d24c` |
| Docs | `arb:mkdocs` | exit 0; `arb-step-mkdocs-0f63553f385246608ab5507ebcc210fe` |
| Behave | `arb:behave` | 5 scenarios passed, 0 failed; `arb-step-behave-169dcb2d18bc4dbdbd35b85df70c3541` |
| OBPI tests | `arb:obpi-tests` | 53 tests OK; `arb-step-unittest-c6a5ea9a82d141c49c15dbf742b588cd` |
| Validation scopes | `validate:scopes` | six scopes, each exit 0; no receipt |
| REQ coverage | `covers` | 10 REQs; behavior_uncovered_reqs 0 |
| Precomplete | `uv run gz obpi precomplete` | every check passes except adversarial_validation, which waits on Step 4b |

All six receipts record exit_status 0 and were recorded after the lock claim, on the tree that carries the round 1 repair. The three REQs without a covering test are the two SUPPORT REQs and the STRUCTURAL-FENCE REQ, by proof channel.

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

- `src/gzkit/governance/trust_audits/bullet_retention.py` (the resolver, the mapping fence, the Ambiguous fence, source-aware retention)
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

Round 1 repair (2026-10-05, commit 60e622dee):

- `src/gzkit/governance/trust_audits/bullet_retention.py` (a row with no row number is refused by name; 679 lines)
- `tests/governance/test_bullet_retention.py` (`test_missing_row_number_fails_closed_naming_the_row`)
- `docs/user/manpages/validate.md`, `docs/governance/advisory-rules-audit.md` (the fail-closed list names the missing row number)

**REQ coverage:**

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|---|---|---|---|---|---|
| REQ-0.35.0-10-01 | BEHAVIOR | 3 tests; 2 controls killed | `TestOwnedBulletResolvesFromCorpus` | `proof-42ff88a9` | behavioral proof valid |
| REQ-0.35.0-10-02 | BEHAVIOR | 8 tests; 3 controls killed | `TestUnownedBulletResolvesFromScorecard` | `proof-4a087137` | behavioral proof valid |
| REQ-0.35.0-10-03 | BEHAVIOR | 3 tests; 2 controls killed | `TestOwnedDisagreementIsReported` | `proof-3828d9e6` | behavioral proof valid |
| REQ-0.35.0-10-04 | BEHAVIOR | 5 tests; 2 controls killed | `TestCaptureDefaultNeverBinds` | `proof-422d8cde` | behavioral proof valid |
| REQ-0.35.0-10-05 | BEHAVIOR | 1 test; 1 control killed | `TestReconciliationIsAppendOnly` | `proof-e5f93b0d` | behavioral proof valid |
| REQ-0.35.0-10-06 | SUPPORT | `resolve_support_proof` | file on disk + `--documents` | `proof-719f97b9` | pass |
| REQ-0.35.0-10-07 | STRUCTURAL-FENCE | `resolve_fence_proof` | ADR-0.35.0 BI-04 | `proof-ee97a10d` | pass |
| REQ-0.35.0-10-08 | BEHAVIOR | 2 tests; 1 control killed | `TestDeclaredSourceRetention` | `proof-4af3a36d` | behavioral proof valid |
| REQ-0.35.0-10-09 | BEHAVIOR | 1 test; 1 control killed | `TestDeclaredSourceRetention` | `proof-e06037c1` | behavioral proof valid |
| REQ-0.35.0-10-10 | SUPPORT | `resolve_support_proof` | file on disk + `--documents` | `proof-d17394e4` | pass |

```text
Test file for every BEHAVIOR row: tests/governance/test_bullet_retention.py
All ten proof records are valid against input digest 883b5c8a8095…

REQ-0.35.0-10-01  proof-42ff88a901194284b303a053eb9890b0
  killed controls: scorecard-class-binds-owned-row, wrong-section-entry-binds
REQ-0.35.0-10-02  proof-4a087137f9294193976b40fd548223b0
  killed controls: duplicate-identity-accepted, unowned-section-demands-corpus-entry,
  blank-row-number-accepted (added in the round 1 repair)
REQ-0.35.0-10-03  proof-3828d9e64a4b4910a6079338508de753
  killed controls: disagreement-silenced, scorecard-class-binds-owned-row
REQ-0.35.0-10-04  proof-422d8cde5a8742e79fba93ca6ea2c224
  killed controls: capture-default-binds, unloadable-ownership-falls-back-to-scorecard
REQ-0.35.0-10-05  proof-e5f93b0d3f8d4f1f9855cb79d3c08efb
  killed controls: fence-reads-raw-log
REQ-0.35.0-10-06  proof-719f97b96cc54e5ba2708b1135a21598
  SUPPORT: the witness clause names artifact_edited citing docs/governance/advisory-rules-audit.md.
  No ledger event cites that path. The resolver passed on its second arm: the cited file
  exists on disk and `uv run gz validate --documents` admits it.
REQ-0.35.0-10-07  proof-ee97a10dd84e420dbdff2a8bca1a2bd8
  STRUCTURAL-FENCE: Boundary Invariants of ADR-0.35.0-canon-entry-corpus-landing, BI-04;
  audited at ADR closeout
REQ-0.35.0-10-08  proof-4af3a36d721342359bbce91d40459e90
  killed controls: declared-source-checked-against-surface
REQ-0.35.0-10-09  proof-e06037c14936463fb96cf653f5a2e7d9
  killed controls: absent-text-reads-as-retained
REQ-0.35.0-10-10  proof-d17394e48a0d446d8aa8be8f45c51527
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
| `codex-035010-missing-row-number` | 02 | a row with a blank number cell was audited with an empty identity and no error | the identity check refuses it by name; new test written first and observed failing on its assertion; new control `blank-row-number-accepted` killed |
| `codex-035010-scorecard-edit-witness` | 06 | this packet said a ledger event cites the scorecard; none does | packet now states the resolver arm that passed |
| `codex-035010-manpage-edit-witness` | 10 | this packet said a ledger event cites the manpage; none does | packet now states the resolver arm that passed |

The reviewer also named the weakest point: the REQ-02 population test derives its expected identities from the same scorecard it audits. The repair closes the blank-number case it demonstrated; a pinned baseline of identities was not added.

**Limits and disclosures**

- The RED falsifiability witness (`gz arb red`) was run for all seven BEHAVIOR REQs and returned failure_class=error on a reconstructed base for every one. That is inconclusive, not a RED. The executed proof records with killed controls are the evidence that each test can fail.
- The implementation was a single-session trial (operator-ruled 2026-10-03). No implementer, spec-reviewer or quality-reviewer subagent was dispatched. The declaration is on the ledger.
- The plan was written after the implementation and is labelled so.
- The ten proof specifications reuse the trial's controls, recovered from the ledger's earlier proof records. Whether each control expresses its requirement is for the independent reviewer to judge.
- The 31-row mapping was accepted by the operator on a text-match measurement: 25 verbatim-contained, 6 paraphrases, all six paraphrases Judgment in both surfaces. The 25 were not re-derived beyond the text match.
- The source module is 679 lines against a 600-line authoring guidance that nothing gates.
- The narrator found the brief's atomicity note for REQ-0.35.0-10-05 saying the live corpus needed no change, after twelve rows had been appended. The note was corrected before this packet was replayed.
- Step 4b round 1 ran on commit e8617ba90 and refuted (see Review history). Round 2, the focused follow-up on the repaired tree, has not run when this revision is written.

**4. Awaiting attestation.** Step 4b (independent review) runs before attestation is solicited.
