# OBPI-0.35.0-10 trial evaluation

Dated evaluation measured 2026-10-04 UTC, of implementation `4893b7321` at HEAD
`3c207fcac`, requested by the operator. **Independent review verdict: FAIL for
the unchanged implementation.** The direct session was substantially cheaper in
the recorded comparison, but passing checks did not establish complete requirement
satisfaction. Independent review found reproducible gaps.

The evidence supports retaining independent examination of behavior in a reduced
workflow. It does not establish the marginal value of the full pipeline,
equivalent quality from an unreviewed direct session, or that gzkit has no useful
capabilities. This evaluation changes no doctrine and supplies no attestation.

## Method and evidence

One fresh-context reviewer read the brief, parent ADR Decision 9, all changed
source/tests/BDD/docs and immediate dependencies. A separate reader traced the
acceptance controls and completion blockers. The main session reproduced the
population, source-path, enrollment, malformed-input and proof-freshness findings
in temporary fixtures. All 31 live corpus mappings received a semantic read.

No implementation, tests, brief, classification, ownership or completion state was
repaired. The existing ledger modification was preserved. Findings are assigned
to existing owners below and recorded as defect insights.

- [Protocol and baseline](README.md).
- [Behavioral probes](trial_eval_probes.py) and [observations](trial-evaluation-probes.json).
- [Cost and verification measurements](trial-evaluation-measurements.json).
- [Owning brief](../../design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md).
- [Implementation](https://github.com/tvproductions/gzkit/blob/4893b73214ea47dcd39b4b7fc26283e54b2bb77a/src/gzkit/governance/trust_audits/bullet_retention.py)
  and [tests](https://github.com/tvproductions/gzkit/blob/4893b73214ea47dcd39b4b7fc26283e54b2bb77a/tests/governance/test_bullet_retention.py).

Reproduce the isolated behavioral measurements from the repository root:

```bash
uv run python docs/governance/obpi-run-cost-2026-10-03-evidence/trial_eval_probes.py
```

## Recorded cost

The existing transcript script was rerun for both sessions, deduplicating API
usage by message ID. Trial figures cover its entire recorded session, including
later discussion and handoff. Baseline includes the orchestrator, three in-process
subagents and twelve sibling reviewer transcripts selected by the script's
documented time-window rule.

| Measure | OBPI-08 baseline | OBPI-10 trial |
|---|---:|---:|
| API calls | 557 | 98 |
| Cache-read input tokens | 153,928,733 | 25,639,640 |
| Cache-creation input tokens | 6,256,193 | 721,805 |
| Output tokens | 668,037 | 170,922 |
| Orchestrator peak context | 743,855 | 410,992 |
| In-process subagent transcripts | 3 | 0 |
| Sibling transcripts in window | 12 | 0 |

The trial used **82.4% fewer calls and 83.3% fewer cache-read tokens**. This is
indicative, not controlled: the OBPIs differ. OBPI-08 changed 63 added/34 removed
source lines in one file; OBPI-10 changed 427 added/27 removed source lines in two.
Line counts do not establish equal difficulty or quality.

Baseline window: `2026-10-03T06:55:00+00:00`–`2026-10-03T11:35:00+00:00`.
Trial sibling window: `2026-10-03T12:00:00+00:00`–`2026-10-04T00:00:00+00:00`.
Session IDs: `553e5afb-48e8-4cae-be4a-db046a3690ba` and
`a0f543a5-5dc2-41ff-949b-f036f79ce0a1`, respectively.

Cache reads are repeated context consumption, not unique tokens or monetary
prices. Operator attention was not measured. These totals exclude this subsequent
Codex evaluation; they are not an end-to-end reviewed-workflow comparison.

## Verification

All ten commands represented by the brief's verification list passed against
the evaluated implementation; the four validator scopes were exercised together.

| Check | Observed result |
|---|---|
| Focused unit module | 52 tests, OK |
| Classification ownership BDD | 5 scenarios and 32 steps passed |
| Full unit tier | 11,430 tests, OK, 7 skipped |
| Lint and typecheck | Both exit 0 |
| Bullet retention | Exit 0, six disagreement advisories |
| Advisory scorecard, documents, REQ kind discipline | All exit 0 |
| Strict documentation build | Exit 0 |

The first full unit run inside the filesystem sandbox returned five failures,
including refusal to create a detached worktree. A rerun with the needed
filesystem access passed without changing source:

```text
Ran 11430 tests in 103.571s

OK (skipped=7)

Unit tests passed.
```

These are evaluation observations, not newly emitted attestation receipts.

## Material findings

### E1 Five scored rows remain outside the audit

An escaped-pipe-aware read found **178 actual identities before and after the
commit**, with none added or removed. The validator and its new population test
see only **173**. All five omitted rows lack source attribution: Pythonic
Standards 22, Data Models 27, Model Selection 52, Map-not-Encyclopedia Doctrine 58,
and Changelog/Release Notes 65. Full identities are in the observation JSON.

Three rule cells contain escaped pipes; two Score cells have both Mechanical and
Judgment components. The production regex at `bullet_retention.py:94` skips
these forms; the new oracle at `test_bullet_retention.py:858` repeats the
restriction. The existing reader at `release.py:415` handles both forms.

The omission predates the trial; its attribution migration and population proof
preserved it. The test at line 985 also derives expected identities from the
current file, so it cannot prove preservation against an earlier population.
Physical preservation was independently verified here. **Correction under
OBPI-10 REQ-02.**

### E2 Equivalent source paths change enforcement

Raw string comparisons at `bullet_retention.py:295,352` choose authority and
retention target. Reproduced:

- A canonical owned source without its required entry ID is rejected. Spelling
  it `./AGENTS.md#owned` instead gives zero errors and scorecard authority,
  despite enrollment of the same physical file.
- A canonical skill path lacking its Mechanical rule is rejected. Prefixing
  that path with `./` passes when a per-turn mirror contains the rule.

These are new source-routing defects. Normalize identity or explicitly reject
unsupported spellings. **Correction under REQ-01, REQ-08 and REQ-09.**

### E3 Enrollment checks can disappear with their inputs

Two reproduced states pass despite a live owned Ambiguous entry: deleting the
declaration while retaining its ledger genesis and an unowned-attributed row; or
keeping the declaration but emptying the scorecard's parsed population.

Enrollment discovery at line 212 reads only existing declaration files. The
early return at lines 150–155 runs before ownership checks. The existing
missing-declaration test retains an entry-citing row and catches only that route.
**Correction under REQ-04 and the Identity and Reconciliation Contract.**

### E4 Recovery can change more than classification

The Ambiguous recovery at `bullet_retention.py:261`, repeated in the manpage,
omits the attestor required to retire an invariant entry. The independent
reviewer's isolated invocation was refused for that omission. The printed
remember command also omits tier and witness; its parsed defaults are
`tier=compressible` and an empty witness. Supplying the missing authorization
and following that command can demote an invariant entry and lose its witness
during classification reconciliation.

The test checks command-name substrings, not executed recovery with preserved
metadata. **Correction under REQ-04 and reconciliation, including the manpage.**

### E5 Malformed ownership produces raw exceptions

JSON `[]` raises `AttributeError`; a null `unowned_byte_floor` raises
`TypeError`. The existing loader reaches unvalidated shapes, and the new
consumer at line 226 does not translate these exceptions. These do not silently
pass, but lack the promised named ownership diagnostic and recovery.
**Correction at the existing ownership loader and its OBPI-10 consumer.**

### E6 Proof freshness excludes the validator's live data

At `acceptance_execution.py:210`, the file roster hashes code, tests, fixtures,
rules and selected configuration. A temporary-root comparison found the roster
unchanged after adding/changing the scorecard, manpage, corpus, ownership
declaration and AGENTS.md; none is included. With the brief and parent contract
unchanged, these changes cannot change the input digest.

A current digest therefore does not establish review of the current live
classification/mappings. SUPPORT has its own live resolver, which does not fix
behavioral proof freshness. **Inherited acceptance-execution limitation, routed
to its existing owner (GHI #985), not new OBPI-10 functionality.**

## Requirement assessment

This grades implementation/content, not completion or operator acceptance.

| REQ suffix | Result | Basis |
|---|---|---|
| 01 | Fail | Normal binding works; path aliases bypass it |
| 02 | Fail | 178 physical identities preserved; five remain unaudited |
| 03 | Pass for canonical mappings | Corpus precedence and disagreement independently exercised |
| 04 | Fail | E3, E4 and E5 violate the refusal/recovery contract |
| 05 | Pass for this increment | Corpus, rendition, AGENTS.md and identity serialization unchanged; append-only fixture passes |
| 06 | Pass | Scorecard describes its narrowed authority |
| 07 | Not yet decidable | Explicitly depends on all parent ADR OBPIs landing |
| 08 | Fail | Normal skill/ADR retention works; aliases bypass it |
| 09 | Fail | Missing source/text rejected normally; alias bypass remains |
| 10 | Content present; formal proof invalid | Both docs explain scope; witness parser reads artifact `both` |

All 31 corpus mappings were read against effective entries. No concrete
wrong-entry assignment was found: they match clauses or recognizable paraphrases.
The six disclosed classification disagreements remain. Two other rows attribute
themselves to the scorecard, preserving catalog identity without establishing
original-source provenance. This review invents no operator ruling on those rows.

## Existing controls and completion blockers

The eleven recorded source mutations were genuinely killed across seven behavior
proofs. They exercise particular assertions about precedence, section/duplicate
identity, unowned routing, disagreement, Ambiguous entries, ownership, effective
corpus and source retention. They do not exercise the omitted population, source
aliases or the other failure shapes above. Mutation sensitivity is useful
evidence, but not proof of adequacy of an entire requirement's oracle.

The full unit suite, lint, typecheck, scoped BDD and four validator scopes pass
while these defects exist. Independent review and targeted probes found them.
No paired run of the same change through both complete workflows was performed;
the trial cannot establish which additional pipeline stages would catch them.

Read-only acceptance evaluation found ten proofs, nine valid, zero reviews and
twelve blockers. Code tracing establishes:

- On this single-driver route, human-review would clear all ten missing-review
  blockers by accepting the latest proofs through its required adversarial
  channel. It is explicitly degraded human-only provenance; REQ-10's two
  invalid-evidence/support blockers would remain.
- `citing both paths` is parsed as one artifact named `both`. The documents
  are present. Replacing it with one path would mechanically witness only one
  document. This defect already has an insight dated 2026-09-25.
- Precomplete requires a PASS plan-audit receipt. The stored failure is the
  missing plan file; its 50 scope-collision entries are advisory. Completion's
  acceptance path does not consult that receipt.

None of those current blockers detected E1–E6. Review was pending, support failed
on citation grammar, and the plan check concerned a missing workflow artifact.
No human-review or completion operation was executed.

## Decision implication

The direct session produced useful implementation at much lower recorded cost,
but its unchanged result does not satisfy the brief. The remaining independent
evaluation has now exposed specific corrective work. A reduced workflow must
retain genuinely independent requirements and behavior review. This trial
supplies no evidence that restoring the entire apparatus is necessary, and no
evidence that tests plus a goal/loop alone are enough.
