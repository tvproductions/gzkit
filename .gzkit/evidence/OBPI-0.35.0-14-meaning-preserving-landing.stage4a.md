## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

Before: `gz content commit` promoted a candidate after three checks (candidate present, corpus present, attestation present when the corpus moved). Nothing compared the candidate with the prior committed rendition, and that is how the 2026-09-17 compression of root AGENTS.md landed 23 binding losses while every check passed (GHI #1090, #1091). Now: a candidate that removes any block of the prior committed rendition is promoted only with a `--retention-map` that accounts for every meaningful character of every removed block — each condition KEPT at a verbatim candidate span or DROPPED with a reason, every DROPPED id named in this invocation's `--attestation-text`, every non-binding exemption carrying a reason, the map bound to this invocation's surface and consumer, extractor and mapper identities required to differ, and any violation exits 3 and writes nothing. The validated map persists as `<consumer>.retention.json`; the gz-content-compose skill requires an independent reviewer and the operator's own words for every drop. The tool proves bytes, never meaning; Requirement 9's four residuals are disclosed below.

**2. Key Proof**

```
$ uv run -m behave features/content_commit_retention.feature
1 feature passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
32 steps passed, 0 failed, 0 skipped
...
```

```
$ uv run -m unittest tests.content.test_retention tests.commands.test_content_commit
...
OK
```

`gz obpi present-evidence` ran the brief's self-contained Demo with exit 0. The Demo prints `exit codes: [3, 3, 0] | sidecar written: True`. It builds a mktemp project, so its paths are not reproducible. The ledger line count and `git status` were identical before and after the run.

**3. Evidence**

Quality checks (Stage 3 re-run on the repaired tree, acceptance input digest 220bb858…):

| Check | Result | Receipt |
|---|---|---|
| Tests (arb:unittest) | 10822 tests OK (4 skipped) | arb-step-unittest-2324c61641434b0aa43a1d6eeca95683 |
| Lint (arb:ruff) | clean | arb-ruff-4e5dc659d853417aada46f818691b33c |
| Typecheck (arb:typecheck) | clean | arb-step-typecheck-a6c57f0798d64074931db71901b13eb7 |
| Docs (arb:mkdocs) | strict build clean | arb-step-mkdocs-7135a077f08c4511adbbc85bbc4cded5 |
| BDD, scoped to @REQ-0.35.0-14-01/-04/-05/-06 (arb:behave) | 4 scenarios / 32 steps | arb-step-behave-fa64e2019e4b46cfb2a65695eea0bc28 |
| `gz validate --documents --req-kind-discipline --cli-alignment` | exit 0 | — |
| `gz cli audit` | exit 0 | — |
| RED witness (arb-red-REQ-0.35.0-14-01..06) | failure_class `error` against reconstructed base 6c6f98dc6 — INCONCLUSIVE and non-blocking; not a finding against the tests. The executed acceptance proofs below carry the behavioral evidence. | — |

The arb incantations (citations; receipts carry the result):

```
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.35.0-14-01,@REQ-0.35.0-14-04,@REQ-0.35.0-14-05,@REQ-0.35.0-14-06 features/
```

Files created (by this OBPI):
- `src/gzkit/content/retention.py` (pure core: block splitter, removed-block delta, meaningful-character coverage, total validator, map-target check, RetentionMap model, sidecar path)
- `tests/content/test_retention.py`
- `features/content_commit_retention.feature`, `features/steps/content_commit_retention_steps.py`

Files modified:
- `src/gzkit/commands/content/commit.py` (retention gate between the existing checks and the first write; enforce_retention; exit 2 for any unreadable prior including non-UTF-8; sidecar write and stale-sidecar removal; KEPT/DROPPED/NB report)
- `src/gzkit/commands/content/__init__.py` (--retention-map flag, help, exit 3)
- `tests/commands/test_content_commit.py`
- `docs/user/manpages/content.md` (retention gate section, schema including the two amended rules, exit codes, a worked example of real output)
- `.gzkit/skills/gz-content-compose/SKILL.md` (v1.1.0 "Before commit: the retention map"; its mirrors are generated)
- the brief (REQ-07 witness-clause amendment, Demo amendment, and the Requirement 3 / REQ-02 amendment, all operator-ruled; Change Log)

REQ coverage (all accepted by the follow-up Stage-2 spec review `arb-step-specreview-cabd2da0ec7b4f899d2d19e245bcb589` and quality review `arb-step-qualityreview-6da8f48d0fdd457aab3ff086f8aa440f`, a verdict-word formatting repair of `arb-step-qualityreview-3204ccdba3884efe9ddb23d225660388`):

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|---|---|---|---|---|---|
| REQ-0.35.0-14-01 | BEHAVIOR | mutation testing | tests/commands/test_content_commit.py | [P1] | 2 @covers tests |
| REQ-0.35.0-14-02 | BEHAVIOR | mutation testing | tests/content/test_retention.py, tests/commands/test_content_commit.py | [P2] | 32 @covers tests |
| REQ-0.35.0-14-03 | BEHAVIOR | mutation testing | tests/content/test_retention.py, tests/commands/test_content_commit.py | [P3] | 4 @covers tests |
| REQ-0.35.0-14-04 | BEHAVIOR | mutation testing | tests/commands/test_content_commit.py | [P4] | 4 @covers tests |
| REQ-0.35.0-14-05 | BEHAVIOR | mutation testing | tests/commands/test_content_commit.py | [P5] | 5 @covers tests |
| REQ-0.35.0-14-06 | BEHAVIOR | mutation testing (verbatim GHI #1090 replay) | tests/content/test_retention.py, tests/commands/test_content_commit.py | [P6] | 6 @covers tests |
| REQ-0.35.0-14-07 | SUPPORT | artifact_edited + cli-alignment resolver | .gzkit/skills/gz-content-compose/SKILL.md | [P7] | n/a |
| REQ-0.35.0-14-08 | STRUCTURAL-FENCE | parent-ADR audit | parent ADR BI-10 | [P8] | n/a |

Proof labels expanded:

```
[P1] proof-df929d5d8b574ae8aa4f68665a016708 (commit.py; 2 selectors, 1 control)
[P2] proof-c1dd2ecc6a6b4080b6e40bd403dd6944 (retention.py; 13 selectors, 10 controls incl. non-binding-reason-unchecked, map-surface-unchecked, map-consumer-unchecked)
[P3] proof-9d0e75efd51045e8a26cee4a644dec5e (retention.py; 4 selectors, 3 controls)
[P4] proof-8415eb94bf2d4dcc93cbbafe89c39a60 (commit.py; 3 selectors, 2 controls)
[P5] proof-c77149c068ba493b91c104562f8f6521 (commit.py; 5 selectors, 2 controls)
[P6] proof-a627857e682a4b7bb8016916cb45b937 (retention.py; 6 selectors, 3 controls; verbatim GHI #1090 replay)
[P7] proof-3de8e21e7c964979be113b284ad58339: artifact_edited citing .gzkit/skills/gz-content-compose/SKILL.md + gz validate --cli-alignment (resolver: pass)
[P8] proof-a3971f6fde324fc0b3fe0b8873037b96: parent-ADR BI-10, audited at ADR closeout
```

`gz covers`: 6/8 covered, 0 BEHAVIOR uncovered; SUPPORT and STRUCTURAL-FENCE use their own proof channels.

**Step 4b history**

- Round 1 (tier-1 Codex, `arb-step-codexadversary-19743ce8aff64c9a998251308ba6ec9b`, imported through formatting repair `arb-step-codexadversary-91370c4450284f6da7afbb02cbb7e22d`): CORROBORATED-WITH-CAVEATS, accepted. REQ-01..07 approved after 18 replayed controls. REQ-08 was not adjudicated because of an orchestrator prompt defect. Three auxiliary counterexamples were found: a non-UTF-8 prior rendition exited 1 instead of 2; an empty non-binding reason was accepted; the map's surface and consumer were never checked. All three were repaired as Task 5. The second and third were added to Requirement 3 and REQ-02 by operator ruling ("Amend + fix now (Recommended)", each).
- Round 2 (tier-1 Codex, `arb-step-codexadversary-0db64ea60fbb4e8dbef0e952323057aa`, workspace digest 1656e806…): CORROBORATED-WITH-CAVEATS, accepted. All eight current proofs were approved, REQ-08 included on its declared BI-10 channel. There were no findings. 21 controls were replayed; each killed on an assertion and restored byte-identically. The Demo returned [3, 3, 0] with the sidecar written. All three round-1 repairs were confirmed both ways. Weakest point, as the adversary stated it: the target binding sits outside the unchanged `validate_retention` API, so a future promotion caller must use the complete gate (`enforce_retention`). That is BI-10's fence for OBPI-0.35.0-07, audited at ADR closeout. It is not a finding. The adversary could not confirm the revision SHA, because the disposable copy carries no Git metadata.

**Disclosures**

1. Stage 4a incident: `gz obpi present-evidence` ran the OLD Demo in the live checkout and wrote a real commit with attestation "demo". The sidecar was restored from HEAD. A tool-generated `rendition_committed` ledger row (2026-09-25T01:28:45Z, attestor g0) remains; it is disclosed in GHI #1093, per the operator ruling.
2. Requirement 9's text lists four residuals but maps its mitigations "first/second/third". The manpage states all four correctly. The brief's own wording is left for operator ruling.
3. The first Task-5 spec and quality reviews (`arb-step-specreview-ca58765b74cc411985d944fb03ff7530`, `arb-step-qualityreview-d9b4e4dea21d43a7bff72d0b34614446`) could not be imported: their envelopes were malformed, and the spec review closed a REQ-07 finding against a proof it had withheld. Their one substantive finding was that the manpage lacked the amended rules. It was fixed, and the follow-up reviews verified the fix.
4. The test for Requirement 1's exit 2 on a non-UTF-8 prior (`test_invalid_utf8_prior_rendition_exits_2_and_writes_nothing`) carries no `@covers`, because no acceptance criterion states that clause.
5. Unmapped, non-blocking reviewer observations: retention.py is about 859 lines, above the advisory 600-line module guidance; the manpage usage line's `C2 drop accepted` is not paired with the one-condition minimal example; a looser OR filter remains in `test_validator_rejects_identical_extracted_and_mapped`.
6. GHIs filed this session: #1092 (the commit-locus recorder loses its row under a pre-commit stash) and #1093 (present-evidence runs Demo commands in the live checkout).
7. Named residual (Requirement 9): the Layer-2 retention digest is deferred (the ledger event module is a security surface), and the partial-IO sidecar exposure belongs to OBPI-0.35.0-07.

**4. Awaiting attestation.**

`gz obpi acceptance OBPI-0.35.0-14-meaning-preserving-landing status --stage stage4` reports ready, with no blockers and no open findings.
