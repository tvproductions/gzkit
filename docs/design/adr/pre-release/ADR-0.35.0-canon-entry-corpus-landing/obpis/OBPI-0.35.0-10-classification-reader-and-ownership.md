---
id: OBPI-0.35.0-10-classification-reader-and-ownership
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 10
lane: Heavy
status: Active
allowlist:
  - src/gzkit/governance/trust_audits/bullet_retention.py
  - tests/governance/test_bullet_retention.py
  - src/gzkit/content/models/corpus.py
  - .gzkit/corpus/AGENTS.md.jsonl
  - .gzkit/renditions/AGENTS.md/
  - AGENTS.md
  - docs/user/manpages/validate.md
  - docs/governance/advisory-rules-audit.md
  - features/classification_ownership.feature
  - features/steps/classification_ownership_steps.py
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md
reqs:
  - REQ-0.35.0-10-01
  - REQ-0.35.0-10-02
  - REQ-0.35.0-10-03
  - REQ-0.35.0-10-04
  - REQ-0.35.0-10-05
  - REQ-0.35.0-10-06
  - REQ-0.35.0-10-07
  - REQ-0.35.0-10-08
  - REQ-0.35.0-10-09
  - REQ-0.35.0-10-10
req_atomic:
  - REQ-0.35.0-10-01  # One resolver arm: an owned row binds its cited corpus entry; landed with its covering tests as one unit.
  - REQ-0.35.0-10-02  # One population contract: identity and source parsing with the scorecard fallback; one unit.
  - REQ-0.35.0-10-03  # One advisory emitted at the single point where the corpus class binds; one unit.
  - REQ-0.35.0-10-04  # One fence over the owned sections of the effective corpus; one unit.
  - REQ-0.35.0-10-05  # One append-only reconciliation walk proven on a fixture; the live reconciliation of 2026-10-05 was twelve governed appends, no code labor.
  - REQ-0.35.0-10-06  # One doctrine paragraph in the scorecard; one SUPPORT authoring unit.
  - REQ-0.35.0-10-07  # Fenced by parent-ADR BI-04; no labor of its own in this OBPI.
  - REQ-0.35.0-10-08  # One retention arm for skill- and ADR-sourced rows; one unit.
  - REQ-0.35.0-10-09  # The fail-closed half of that same arm; one unit.
  - REQ-0.35.0-10-10  # Manpage section plus scorecard paragraph; one SUPPORT authoring unit.
verification:
  - uv run -m unittest tests.governance.test_bullet_retention
  - uv run -m behave features/classification_ownership.feature
  - uv run gz lint
  - uv run gz typecheck
  - uv run gz test
  - uv run gz validate --bullet-retention
  - uv run gz validate --advisory-scorecard
  - uv run gz validate --documents
  - uv run gz validate --req-kind-discipline
  - uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-10-01-01
  - TASK-0.35.0-10-02-01
  - TASK-0.35.0-10-03-01
  - TASK-0.35.0-10-04-01
  - TASK-0.35.0-10-05-01
  - TASK-0.35.0-10-06-01
  - TASK-0.35.0-10-07-01
  - TASK-0.35.0-10-08-01
  - TASK-0.35.0-10-09-01
  - TASK-0.35.0-10-10-01
---

# OBPI-0.35.0-10-classification-reader-and-ownership: Classification Reader And Ownership

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #10 - "`classification` reader -- corpus-owned sections resolve from `CorpusEntry.classification`, scorecard elsewhere; the 36 `Ambiguous` capture-defaults reconciled before ownership binds (GHI #737)"

**Status:** Draft

## Objective

Give `CorpusEntry.classification` its first reader: `bullet_retention` resolves a
bullet's classification from the corpus when that bullet's section is
corpus-owned, and from `docs/governance/advisory-rules-audit.md` otherwise. The
field is schema-required and identity-fingerprinted today with **zero** read
sites anywhere in `src/` — every hit is a declaration or a writer — while the
binding copy of the same concept lives in a hand-maintained markdown table. Done
means exactly one surface classifies any given bullet, every identity in the measured pre-change scorecard
population is preserved, and no corpus section binds while its entries still
carry the capture-default.

The same audit also learns **where** a row is retained. A scorecard section
attributed to a skill or ADR source is retention-checked against that source's
own text. It is not exempted: an exempt `Mechanical` row would be a declared
discipline with no witness, the "third state" GHI #939 measured. Rows attributed
to the per-turn surface keep today's check unchanged.

**Dependency order:** 10 consumes landed 01/02 (effective fold and governed retirement),
04 (ownership), and 07 for the post-reconciliation landing. 09 supplies the root-only
AgentContract route. Development may use isolated fixtures; completion includes governed
retirement/capture and re-landing so the repository is coherent.

> **Amendment provenance.** This item was folded into ADR-0.35.0 on 2026-08-02
> by operator ruling, from GHI #737, while the ADR stood at 0/9 landed. It is a
> **correction, not an enhancement** (operator doctrine, verbatim: *"discovering
> that more is needed to fulfill the intent of a feature is not an enhancement,
> it is a correction"*): ADR-0.0.37 § Decision Re-Alignment part 1 declared
> `classification` one of the ten canonical `CorpusEntry` fields, and a field
> that nothing reads does not fulfill that declared intent. The Decomposition
> Scorecard's `Baseline Selected` moved 6 -> 7 in the same amendment; the
> dimension scores are unchanged, because this opens no new dimension.

> **Amendment 2026-09-29 — retention scope (GHI #939).** Operator ruling
> 2026-09-28 (ruling docket), verbatim: *"Fold into OBPI-10 (Recommended)"* —
> the source-aware `bullet_retention` scope goes to this OBPI. Amendment directed
> 2026-09-29, verbatim: *"do all four"*, then *"take care of these"*. Same file,
> same seam: today `_SURFACE_FILES` / `_RULES_GLOB` (`bullet_retention.py:49-50`)
> fix retention to the per-turn surface, so a discipline declared in a `SKILL.md`
> or an ADR can never be scored `Mechanical` or `Promotable` without first being
> mirrored into `AGENTS.md`, and scoring it `Judgment` to dodge that is the
> laundering the scorecard names. This adds REQ-08..10. REQ-01..07 are unchanged.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because `gz validate --bullet-retention` changes which input decides a
fail-closed verdict. A gate that silently changes its authority is the drift
this ADR exists to kill.

## Allowed Paths

- `src/gzkit/governance/trust_audits/bullet_retention.py` — the resolver; today `_SCORECARD_PATH` (line 48) is its only classification input
- `tests/governance/test_bullet_retention.py` — covering tests for the resolution order
- `src/gzkit/content/models/corpus.py` — docstring only, to name the reader the field now has; the field, its `BASELINE_IDENTITY_FIELDS` membership, and its ordering are all untouched
- `.gzkit/corpus/AGENTS.md.jsonl` — governed retire/capture reconciliation; no manual JSONL edits
- `.gzkit/renditions/AGENTS.md/` — governed candidate, lineage, rendition and provenance publication only
- `AGENTS.md` — generated playback only; never manually edited to satisfy the audit
- `docs/user/manpages/validate.md` — observed classification-source and recovery examples
- `docs/governance/advisory-rules-audit.md` — the scorecard states its own now-narrowed authority
- `features/classification_ownership.feature` — **CREATE**, Gate 4 scenarios
- `features/steps/classification_ownership_steps.py` — **CREATE**, the steps for those scenarios
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/schemas/corpus_entry.json` — `classification` stays schema-required; the operator ruling kept the corpus, so there is no demotion to make here
- `src/gzkit/content/models/bullet.py` — `Bullet.classification` is the *rendering* join (`markdown_parser.py:290`), a separate consumer; re-pointing it is not this OBPI's scope
- `src/gzkit/content/parse/markdown_parser.py` — same reason
- `src/gzkit/commands/content/**` — the writers (`remember.py:112,158`, `retire.py:66`, `__init__.py:296`) keep their current behavior; this OBPI adds a reader, never changes capture
- `src/gzkit/content/rendition_store.py` — the fingerprint algorithm and pre-existing-row identity remain unchanged
- `CLAUDE.md`, `.claude/rules/**` — read-only audit inputs; root AGENTS.md may change only through the governed publication allowance
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS resolve a corpus-owned bullet's classification from `CorpusEntry.classification`, and a non-owned bullet's from the scorecard. Exactly one surface answers for any given bullet; there is no merge, no union, and no "most severe wins."
2. NEVER shrink the audited population. The scorecard carries 144 rows against the corpus's 52 over 8 sections; a wholesale swap to the corpus is a ~64% coverage regression and is the shape the parent ADR § Decision 9 explicitly REJECTS. The post-change population MUST retain every pre-change `(scorecard section id, row number)` identity and its source attribution. Equal counts are insufficient: substitution of one identity for another must fail. Historical 144/52/36 counts are context, never constants.
3. NEVER let a corpus-owned section bind while any of its live entries carries the capture-default `Ambiguous`. 36 of 52 rows carry it today, every one with `origin: cli:content-remember` — the default was never revisited. Binding on an unreviewed default would let the capture path silently author gate verdicts. Fail closed with three-part recovery prose per `.claude/rules/guardrail-feedback-prose.md`.
4. NEVER mutate a corpus row to reconcile a classification. Reconciliation is an APPEND — the corpus is an append-only log and OBPI-0.35.0-01's tombstone algebra is the only retirement channel. An in-place edit destroys provenance and re-fingerprints the corpus.
5. NEVER change `corpus_fingerprint()` output over the already-committed prefix. Governed appends intentionally change the full-corpus fingerprint and require rendition refresh. `classification` stays in `BASELINE_IDENTITY_FIELDS` (`corpus.py:53-64`) in its current position; that tuple's own comment says reordering or removing "re-fingerprints every committed rendition."
6. ALWAYS surface a corpus/scorecard disagreement on an owned bullet rather than silently resolving it. Precedence decides which value BINDS; it never decides whether the operator gets to see that the two surfaces disagreed.
7. NEVER add a second classification model. `.claude/rules/hexagonal-architecture.md` § Operative rules 8 forbids "a second, differently-typed representation of the same objects" — this OBPI's whole purpose is to collapse one such pair, not to add a third resolver.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
9. ALWAYS retention-check a skill- or ADR-sourced scorecard row against its attributed source, and NEVER exempt it from retention. The source comes from the same Notes-column attribution the Identity contract below requires, never inferred from the rule text. A missing source file or an absent row text fails closed.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Identity and Reconciliation Contract

Retain scorecard identity as (scorecard section id, row number); bare row numbers are
not unique. Record explicit source attribution in the existing scorecard Notes column:
source path, canonical section id and, for an owned AgentContract row, its unique effective
corpus entry id. This mapping is reviewed during implementation planning. It is evidence
of intended correspondence, not fuzzy text matching: do not infer it from the first
substring hit, manufacture ids, or silently choose among ambiguous candidates. Multiple
rows may reference one entry where the reviewed mapping explicitly says so.

Validate the mapping against the source section and effective corpus. Missing/duplicate
row identities, missing attribution, wrong-section or retired entry ids, and unknown
owned sections are named failures; never fall back to scorecard authority for a broken
owned mapping. Non-AgentContract rows retain their current authority. Missing/corrupt
enrolled ownership cannot silently convert owned rows to scorecard-only rows. A project
without ownership enrollment retains the legacy audit path.

For classification reconciliation, prepare a before/after mapping for operator review;
do not auto-reclassify from prose. Use shipped retire followed by remember for unchanged
text with new classification: the existing writer rejects identical live text and has
no supersedes option. Reuse the approved source witness and record retirement/replacement
ids. Interrupted migration is explicitly incomplete and cannot produce a successful
owned audit until capture and mapping refresh finish. All old raw rows and the old-prefix
fingerprint remain byte-identical; the new full fingerprint changes. Use 07 to re-land,
with corpus-delta attestation; never edit rendered output as an audit workaround.

REQ-01 covers exact entry-id authority and missing/wrong-section/retired ids.
REQ-02 compares identity sets and source attribution, including same text in two sections.
REQ-03 changes the corpus classification while holding the scorecard fixed, and vice versa.
REQ-04 covers invalid ownership and every live Ambiguous entry, not just mapped rows.
REQ-05 covers interrupted retire/capture, old-prefix bytes, new fingerprint and re-landing.
The scorecard's existing NC/grandfather requirements continue to bind any reclassified row;
reader work does not waive them.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 9 — quote it** verbatim into this brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Decision item 3 — section ownership, the seam this item applies to the classification axis.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` — agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against
- [ ] `.claude/rules/hexagonal-architecture.md` § Operative rules 8 — the parallel-model prohibition this OBPI discharges
- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part shape REQ-04's fail-closed message owes

**Context:**

- [ ] `OBPI-0.35.0-04-section-ownership-and-ratchet.md` — the hard prerequisite; read its ownership declaration shape before writing the resolver
- [ ] `OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md` — `effective_corpus()`; the resolver reads the effective view, never the raw log (BI-01)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/governance/trust_audits/bullet_retention.py` exists and `_SCORECARD_PATH` is still its sole classification input
- [ ] Section ownership from OBPI-0.35.0-04 has landed — a bullet's section can be answered `corpus-owned` or not. **If it has not, STOP: this brief cannot land first.**
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` is readable and its `classification` distribution has been measured (36 Ambiguous / 7 Judgment / 4 Mechanical / 5 Promotable as of 2026-08-02 — re-measure, do not inherit)

**Existing Code (understand current state):**

- [ ] `bullet_retention.py:141-163` — `_parse_scorecard` and `_collect_surface_corpus`, the two inputs the verdict is built from today
- [ ] `bullet_retention.py:82-95` — the enforcement loop `_is_enforced` gates
- [ ] `corpus.py:53-64` — `BASELINE_IDENTITY_FIELDS` and the never-reorder warning
- [ ] `tests/governance/test_bullet_retention.py` — the assertions that must keep holding

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/governance/advisory-rules-audit.md` states its narrowed authority

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run -m unittest tests.governance.test_bullet_retention
uv run -m behave features/classification_ownership.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --bullet-retention
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

## Demo

```bash
# The field finally answers a question: a corpus-owned bullet's verdict now
# traces to its corpus entry rather than to a hand-maintained markdown row.
uv run gz validate --bullet-retention --json

# The capture-default fence: an owned section holding an unreviewed
# `Ambiguous` entry refuses to bind, and names the entries to reconcile.
uv run gz validate --bullet-retention

# Provenance of the reconciliation — appended rows, never edited ones:
# every retraction row in the corpus, the six reconciliations included,
# has its ledger witness.
uv run gz validate --corpus-retirement-witness
```

## Acceptance Criteria

- [ ] REQ-0.35.0-10-01 [behavior]: Given a bullet whose section is corpus-owned, when `validate_bullet_retention` runs, then the bullet's classification is read from that section's `CorpusEntry.classification` and NOT from `docs/governance/advisory-rules-audit.md`
- [ ] REQ-0.35.0-10-02 [behavior]: Given a bullet whose section is not corpus-owned, when `validate_bullet_retention` runs, then the bullet's classification is read from the scorecard, and every measured pre-change row identity/source remains represented, with unchanged retention/tier behavior for unowned and non-AgentContract rows
- [ ] REQ-0.35.0-10-03 [behavior]: Given a bullet classified by BOTH surfaces with disagreeing values on an owned section, when the audit runs, then the corpus value binds AND the disagreement is reported to the operator rather than silently discarded
- [ ] REQ-0.35.0-10-04 [behavior]: Given a corpus-owned section with at least one live entry whose classification is the capture-default `Ambiguous`, when the audit runs, then it fails closed naming each unreconciled entry id, the rule that binds, and the runnable next step
- [ ] REQ-0.35.0-10-05 [behavior]: Given the committed corpus, when this OBPI's reconciliation has landed, then `corpus_fingerprint()` over the pre-existing rows is unchanged and every reconciliation is an appended row rather than an edited one
- [ ] REQ-0.35.0-10-06 [support]: `docs/governance/advisory-rules-audit.md` records that its authority is now narrowed to non-corpus-owned sections, so the scorecard cannot be read as the sole classification authority. Witnessed by `artifact_edited` citing `docs/governance/advisory-rules-audit.md` + `gz validate --documents`.
- [ ] REQ-0.35.0-10-07 [structural-fence]: no classification surface exists without a reader, and no bullet resolves from two surfaces at once, after every ADR-0.35.0 OBPI has landed
- [ ] REQ-0.35.0-10-08 [behavior]: Given a scorecard section whose attributed source is a `.gzkit/skills/*/SKILL.md` or an ADR file, when `validate_bullet_retention` runs, then its `Mechanical`/`Promotable` rows are retention-checked against that source's text and not the per-turn surface, while rows attributed to the per-turn surface keep their current tier-scoped check
- [ ] REQ-0.35.0-10-09 [behavior]: Given a skill- or ADR-sourced row whose source file is missing or whose text is absent from it, when the audit runs, then it fails closed naming the row identity, the attributed source path, the rule that binds, and the runnable next step
- [ ] REQ-0.35.0-10-10 [support]: `docs/user/manpages/validate.md` § `--bullet-retention` and `docs/governance/advisory-rules-audit.md` state the source-aware retention scope. Witnessed by `artifact_edited` citing `docs/user/manpages/validate.md` + `gz validate --documents`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

Before: `CorpusEntry.classification` was schema-required and part of the
baseline identity fingerprint, and nothing in `src/` read it. The binding copy
of the same concept was a hand-maintained markdown table. 36 of 52 corpus rows
carried the capture-default `Ambiguous`, and that skew was invisible precisely
because no gate observed the field it drifted on.

After: the field decides a fail-closed verdict for the sections the corpus owns,
the scorecard keeps the sections it still owns, and a section cannot bind on an
unreviewed default.

### Key Proof

One concrete example recorded at completion: a corpus-owned bullet whose
`gz validate --bullet-retention` verdict changes when its `CorpusEntry.classification`
changes and its scorecard row does not — the observation that was impossible
before this OBPI, because the corpus value reached no consumer.

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Change Log

- 2026-10-05 — **Plan written after implementation.** The 2026-10-03 single-session trial skipped plan mode, so the plan audit had no subject. `.claude/plans/classification-reader-and-ownership-OBPI-0.35.0-10.md` records what was built and plans the remaining stages; it is labelled as written after the code. Operator ruling 2026-10-05, booked in the handoff rulings store: CI goes green by working item 10, its plan audit re-run to a pass.
- 2026-10-05 — **Parent ADR Decision item 9 amended** to carry the source-aware retention scope (REQ-08 to REQ-10), which the 2026-09-29 amendment had written into this brief only. Finding: plan audit, ADR to OBPI, no scope creep. Operator ruling, verbatim selection: "A: Amend Decision 9 (Recommended)". Checklist item 10 is unchanged.
- 2026-10-05 — **REQ-0.35.0-10-10 witness clause** now cites `docs/user/manpages/validate.md`. It read "citing both paths", which the support resolver parsed as a path named "both" and returned unproven. The requirement's statement is unchanged. Operator ruling, verbatim selection: "A: Cite the manpage (Recommended)". Every proof is re-run against the amended contract.
- 2026-10-05 — **Mapping reviewed.** The Identity and Reconciliation Contract requires the row-to-entry mapping to be reviewed at planning; the trial ran no planning step. Put to the operator on measured evidence: 31 rows cite a corpus entry; 25 carry rule text contained verbatim in the cited entry; 6 are paraphrases (Governance Core #17, #17c, #17d; Defect-fix Routing #46, #47; Agent Contract #53c), all Judgment in both surfaces. The mandatory source attribution, the two rows attributed to the scorecard itself and the requote of Local Agent Rules #8 were named in the same question. Operator ruling, verbatim selection: "A: Accept as measured (Recommended)".
- 2026-10-05 — **Six class disagreements reconciled in the corpus.** Local Agent Rules #7, #10 and Governance Core #14, #16, #17a were Mechanical in the scorecard and Judgment in the corpus; Local Agent Rules #8 was the reverse. All six corpus classes came from one batch capture on 2026-09-17. Operator ruling, verbatim selection: "A: Corpus adopts scorecard (Recommended)". Done by governed retire and remember of the unchanged text, published with an unchanged candidate through compose and commit, not through the item 7 orchestrator, because its generated candidate reorders two blocks of the root surface. Retirement and replacement ids are recorded in the Implementation Summary.
- 2026-10-05 — **Step 4b round 1, finding `codex-035010-missing-row-number` (REQ-0.35.0-10-02).** A scorecard row with a blank number cell was audited with an empty identity and no error, against the Identity and Reconciliation Contract's "missing row identities are named failures". Repair: the identity check now names such a row and refuses it; `test_missing_row_number_fails_closed_naming_the_row` was written first and observed failing on its assertion (`0 != 1`). The manpage and the scorecard's authority paragraph list the new condition. Independent closure: the round 2 review.
- 2026-10-05 — **Step 4b round 1, findings `codex-035010-scorecard-edit-witness` and `codex-035010-manpage-edit-witness` (REQ-0.35.0-10-06, -10).** The Stage 4 packet said a ledger `artifact_edited` event cites each document. None does; the reviewer searched all 5,395 such events. The canonical support resolver passes these two requirements on its documented second arm (the cited artifact exists on disk and its validator scope admits it), which is what the packet should have said. Repair: the packet states the arm that actually passed. No ledger row was written to manufacture a witness. Independent closure: the round 2 review.
- 2026-10-05 — **`req_atomic` note for REQ-0.35.0-10-05 corrected.** It said the live corpus needed no change, which stopped being true when the six reconciliations appended twelve rows. Found by the narrator while composing the Stage 4 packet.
- 2026-10-05 — **Third Demo command replaced.** `gz content show` takes a file and a content type and has no section option, so the command exited 2 and blocked the evidence packet; the trial recorded this as an insight on 2026-10-03. The replacement is `gz validate --corpus-retirement-witness`, which passes only when every retraction row in the corpus has its ledger witness. A `git diff --numstat` over the reconciliation commit was tried first and withdrawn: the Demo runs in a copy of the tree with no history. That figure, twelve lines added and none removed between 7c05949ee and 3c53720ab, is recorded here instead. No requirement changed.
- 2026-10-05 — **Allowed Paths bullet split.** The behave feature and its steps file shared one bullet; the plan audit reads the first path on a bullet and reported the steps file as out of scope. No path was added; the frontmatter allowlist already carried both.

## Tracked Defects

- GHI #939 — `advisory-scorecard: skill-declared doctrine is structurally unscorable`. Retention-scope arm folded here by operator ruling 2026-09-28 (REQ-08..10). Its skill-text arm landed separately in `74adc5fc1`.
- GHI #799 — the ADR-declared sibling cut of the same `bullet_retention` precondition. REQ-08's ADR-sourced arm covers its remedy branch (a). Its disposition is the operator's, recorded on #799.
- GHI #737 — `corpus: CorpusEntry.classification is required but has no consumer`. Folded into this ADR by operator ruling 2026-08-02 rather than repaired as a standalone direct fix, because the resolution depends on the section-ownership seam OBPI-0.35.0-04 introduces.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
