---
id: OBPI-0.35.0-10-classification-reader-and-ownership
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 10
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/trust_audits/bullet_retention.py
  - tests/governance/test_bullet_retention.py
  - src/gzkit/content/models/corpus.py
  - .gzkit/corpus/AGENTS.md.jsonl
  - docs/governance/advisory-rules-audit.md
  - features/**
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md
reqs:
  - REQ-0.35.0-10-01
  - REQ-0.35.0-10-02
  - REQ-0.35.0-10-03
  - REQ-0.35.0-10-04
  - REQ-0.35.0-10-05
  - REQ-0.35.0-10-06
  - REQ-0.35.0-10-07
verification:
  - uv run gz lint
  - uv run gz typecheck
  - uv run gz test
  - uv run gz validate --bullet-retention
  - uv run gz validate --advisory-scorecard
  - uv run gz validate --documents
  - uv run gz validate --req-kind-discipline
  - uv run mkdocs build --strict
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
means exactly one surface classifies any given bullet, the scorecard's 144-row
population is preserved, and no corpus section binds while its entries still
carry the capture-default.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 10 depends on
**OBPI-0.35.0-04**, which introduces the section-ownership declaration this
brief's resolution rule keys on — "corpus-owned" is not yet a property anything
can answer (`grep -rn "corpus-owned" src/gzkit/content` returns nothing as of
2026-08-02). 10 is independent of the 01 -> 02 -> 03 chain and of 05 -> 06 -> 07,
and MUST land after 04.

> **Amendment provenance.** This item was folded into ADR-0.35.0 on 2026-08-02
> by operator ruling, from GHI #737, while the ADR stood at 0/9 landed. It is a
> **correction, not an enhancement** (operator doctrine, verbatim: *"discovering
> that more is needed to fulfill the intent of a feature is not an enhancement,
> it is a correction"*): ADR-0.0.37 § Decision Re-Alignment part 1 declared
> `classification` one of the ten canonical `CorpusEntry` fields, and a field
> that nothing reads does not fulfill that declared intent. The Decomposition
> Scorecard's `Baseline Selected` moved 6 -> 7 in the same amendment; the
> dimension scores are unchanged, because this opens no new dimension.

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
- `.gzkit/corpus/AGENTS.md.jsonl` — the reconciliation of the 36 `Ambiguous` capture-defaults, appended never edited
- `docs/governance/advisory-rules-audit.md` — the scorecard states its own now-narrowed authority
- `features/**` — Gate 4 scenarios
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/schemas/corpus_entry.json` — `classification` stays schema-required; the operator ruling kept the corpus, so there is no demotion to make here
- `src/gzkit/content/models/bullet.py` — `Bullet.classification` is the *rendering* join (`markdown_parser.py:290`), a separate consumer; re-pointing it is not this OBPI's scope
- `src/gzkit/content/parse/markdown_parser.py` — same reason
- `src/gzkit/commands/content/**` — the writers (`remember.py:112,158`, `retire.py:66`, `__init__.py:296`) keep their current behavior; this OBPI adds a reader, never changes capture
- `src/gzkit/content/rendition_store.py` — `corpus_fingerprint()` must not move
- `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**` — the rendered surfaces are inputs to the audit, never edited to make it pass
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS resolve a corpus-owned bullet's classification from `CorpusEntry.classification`, and a non-owned bullet's from the scorecard. Exactly one surface answers for any given bullet; there is no merge, no union, and no "most severe wins."
2. NEVER shrink the audited population. The scorecard carries 144 rows against the corpus's 52 over 8 sections; a wholesale swap to the corpus is a ~64% coverage regression and is the shape the parent ADR § Decision 9 explicitly REJECTS. The post-change row count MUST be >= the pre-change count, asserted, not assumed.
3. NEVER let a corpus-owned section bind while any of its live entries carries the capture-default `Ambiguous`. 36 of 52 rows carry it today, every one with `origin: cli:content-remember` — the default was never revisited. Binding on an unreviewed default would let the capture path silently author gate verdicts. Fail closed with three-part recovery prose per `.claude/rules/guardrail-feedback-prose.md`.
4. NEVER mutate a corpus row to reconcile a classification. Reconciliation is an APPEND — the corpus is an append-only log and OBPI-0.35.0-01's tombstone algebra is the only retirement channel. An in-place edit destroys provenance and re-fingerprints the corpus.
5. NEVER change `corpus_fingerprint()` output for the already-committed corpus. `classification` stays in `BASELINE_IDENTITY_FIELDS` (`corpus.py:53-64`) in its current position; that tuple's own comment says reordering or removing "re-fingerprints every committed rendition."
6. ALWAYS surface a corpus/scorecard disagreement on an owned bullet rather than silently resolving it. Precedence decides which value BINDS; it never decides whether the operator gets to see that the two surfaces disagreed.
7. NEVER add a second classification model. `.claude/rules/hexagonal-architecture.md` § Operative rules 8 forbids "a second, differently-typed representation of the same objects" — this OBPI's whole purpose is to collapse one such pair, not to add a third resolver.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

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

# Provenance of the reconciliation — appended rows, never edited ones.
uv run gz content show AGENTS.md --section prime-directive-ownership
```

## Acceptance Criteria

- [ ] REQ-0.35.0-10-01 [behavior]: Given a bullet whose section is corpus-owned, when `validate_bullet_retention` runs, then the bullet's classification is read from that section's `CorpusEntry.classification` and NOT from `docs/governance/advisory-rules-audit.md`
- [ ] REQ-0.35.0-10-02 [behavior]: Given a bullet whose section is not corpus-owned, when `validate_bullet_retention` runs, then the bullet's classification is read from the scorecard, and the total number of classified bullets is not less than the pre-change count
- [ ] REQ-0.35.0-10-03 [behavior]: Given a bullet classified by BOTH surfaces with disagreeing values on an owned section, when the audit runs, then the corpus value binds AND the disagreement is reported to the operator rather than silently discarded
- [ ] REQ-0.35.0-10-04 [behavior]: Given a corpus-owned section with at least one live entry whose classification is the capture-default `Ambiguous`, when the audit runs, then it fails closed naming each unreconciled entry id, the rule that binds, and the runnable next step
- [ ] REQ-0.35.0-10-05 [behavior]: Given the committed corpus, when this OBPI's reconciliation has landed, then `corpus_fingerprint()` over the pre-existing rows is unchanged and every reconciliation is an appended row rather than an edited one
- [ ] REQ-0.35.0-10-06 [support]: `docs/governance/advisory-rules-audit.md` records that its authority is now narrowed to non-corpus-owned sections, so the scorecard cannot be read as the sole classification authority — `gz validate --documents` + `artifact_edited` event
- [ ] REQ-0.35.0-10-07 [structural-fence]: no classification surface exists without a reader, and no bullet resolves from two surfaces at once, after every ADR-0.35.0 OBPI has landed

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

## Tracked Defects

- GHI #737 — `corpus: CorpusEntry.classification is required but has no consumer`. Folded into this ADR by operator ruling 2026-08-02 rather than repaired as a standalone direct fix, because the resolution depends on the section-ownership seam OBPI-0.35.0-04 introduces.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
