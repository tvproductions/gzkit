---
id: OBPI-0.35.0-14-meaning-preserving-landing
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 14
lane: Heavy
status: Active
allowlist:
  - src/gzkit/content/retention.py
  - src/gzkit/commands/content/commit.py
  - src/gzkit/commands/content/__init__.py
  - src/gzkit/content/corpus_store.py
  - src/gzkit/content/rendition.py
  - tests/content/test_retention.py
  - tests/commands/test_content_commit.py
  - features/content_commit_retention.feature
  - features/steps/content_commit_retention_steps.py
  - docs/user/manpages/content.md
  - .gzkit/skills/gz-content-compose/SKILL.md
  - src/gzkit/skills/gz-content-compose/SKILL.md
  - .claude/skills/gz-content-compose/SKILL.md
  - .agents/skills/gz-content-compose/SKILL.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md
reqs:
  - REQ-0.35.0-14-01
  - REQ-0.35.0-14-02
  - REQ-0.35.0-14-03
  - REQ-0.35.0-14-04
  - REQ-0.35.0-14-05
  - REQ-0.35.0-14-06
  - REQ-0.35.0-14-07
  - REQ-0.35.0-14-08
verification:
  - uv run -m unittest tests.content.test_retention tests.commands.test_content_commit
  - uv run -m behave features/content_commit_retention.feature
  - uv run gz validate --documents --req-kind-discipline --cli-alignment
  - uv run gz cli audit
  - uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-14-01-01
  - TASK-0.35.0-14-02-01
  - TASK-0.35.0-14-03-01
  - TASK-0.35.0-14-04-01
  - TASK-0.35.0-14-05-01
  - TASK-0.35.0-14-06-01
  - TASK-0.35.0-14-07-01
  - TASK-0.35.0-14-08-01
---

# OBPI-0.35.0-14-meaning-preserving-landing: Meaning Preserving Landing

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #14 - "Meaning-preserving landing -- a candidate that removes any block of the prior committed rendition is promoted only with a retention map. Each condition of each removed block is either KEPT at a quoted candidate span or DROPPED with a reason the operator approves; the conditions are extracted by an independent reviewer; the map is persisted as `<consumer>.retention.json`. Sequenced before item 7 by operator ruling 2026-09-24 (GHI #1090)"

**Status:** Draft

## Objective

`gz content commit` refuses to promote a candidate that removes any block of the consumer's prior committed rendition unless a retention map accounts for every condition of every removed block. Each condition is either KEPT at a quoted candidate span or DROPPED with a reason the operator names. When the promotion succeeds, the map is persisted as `<consumer>.retention.json`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract changes are a new `--retention-map` flag on `gz content commit`, a new refusal (exit 3) and a new sidecar artifact.

## Allowed Paths

- `src/gzkit/content/retention.py` — **CREATE**, a pure core module (stdlib + Pydantic) beside `content/lineage.py`. It holds the block splitter, the removed-block delta, the `RetentionMap` model and the validator.
- `src/gzkit/commands/content/commit.py` — the promotion seam: load the map, run the gate, write the sidecar
- `src/gzkit/commands/content/__init__.py` — the `content commit` parser: `--retention-map` flag, help text and exit-3 documentation
- `src/gzkit/content/corpus_store.py`, `src/gzkit/content/rendition.py` — READ-ONLY fixture imports of the covering commit tests (`append_entry`, `candidate_path`); listed so the brief reconciles against the test tree, never modified by this OBPI (amendment 2026-09-25, pending operator ratification)
- `tests/content/test_retention.py` — **CREATE**, following `tests/content/test_lineage.py`
- `tests/commands/test_content_commit.py`
- `features/content_commit_retention.feature` — **CREATE**, following `features/content_retire.feature`
- `features/steps/content_commit_retention_steps.py` — **CREATE**, following `features/steps/content_retire_steps.py`
- `docs/user/manpages/content.md` — the `commit` section: flag, sidecar, refusal and recovery
- `.gzkit/skills/gz-content-compose/SKILL.md` — the wielding skill: reviewer dispatch, map authoring, presenting drops to the operator
- `src/gzkit/skills/gz-content-compose/SKILL.md`, `.claude/skills/gz-content-compose/SKILL.md`, `.agents/skills/gz-content-compose/SKILL.md` — generated mirrors, written only by `uv run gz agent sync control-surfaces`, never hand-edited
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md`

## Denied Paths

- `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` — `ledger_events.py` is a registered security surface (`data/security_surfaces.json`). Adding a retention digest to `rendition_committed` would bring this OBPI under `sensitivity: security`, so it is out of scope. See the named residual under Requirements.
- `src/gzkit/content/rendition_store.py` — `RenditionProvenance` stays `frozen=True` / `extra="forbid"` with no retention fields (BI-03, § Alternatives O). The sidecar path helper lives in `retention.py`, next to `lineage_path`, following its pattern.
- `src/gzkit/content/models/corpus.py`, `src/gzkit/commands/content/remember.py`, `src/gzkit/commands/content/retire.py` — the gate reads the rendition delta, not the corpus log. Capture stays unblockable (BI-06).
- `src/gzkit/content/composer.py`, `src/gzkit/content/lineage.py` — generation and lineage are read, never changed. A lossy candidate is caught at promotion, not at generation.
- `.gzkit/corpus/**`, `.gzkit/renditions/**`, `AGENTS.md` — no canon or rendition is published by this OBPI. Fixtures live in temporary directories.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The prior rendition is the consumer's COMMITTED rendition (`rendition_path(root, surface, consumer)`). With no prior rendition (first commit), nothing was removed and the gate is vacuous. A missing prior is never evidence that nothing was lost, so the vacuous branch MUST test for the committed file's absence, never for an empty delta after a read failure. An unreadable prior rendition is exit 2.
2. REQUIREMENT: A BLOCK is a markdown heading, paragraph, list item or table row, as separated in the rendered surface. Fenced code blocks count as one block. A prior block is REMOVED when its text (LF-normalized, trailing whitespace per line stripped) is not a substring of the candidate. Moving or reordering a block never removes it.
3. REQUIREMENT: The map validator is pure and total. Given (removed blocks, candidate text, map, attestation text) it returns every violation, never the first only, so one refusal names every gap. Violations:
   - a removed block with no map entry
   - a meaningful character of a removed block (any non-whitespace character except markdown markup `*`, `_`, `` ` ``, `#`, `|`, `>` and the block's leading list marker) that lies inside no condition quote and no non-binding quote (reported per sentence, naming the uncovered text). This is ADR-0.35.0 Decision 10's "every sentence ... lies inside at least one condition", allowing a sentence to be split across several conditions whose quotes together cover it
   - a condition quote that is not a substring of its removed block
   - a KEPT span that is not a substring of the candidate
   - a DROPPED condition with an empty reason
   - `extracted_by` or `mapped_by` empty, or equal to each other after case-folding and whitespace trimming
   - a DROPPED condition whose id does not appear in the attestation text at a token boundary
   - a map entry naming no removed block of this delta, or two entries for the same removed block (every map entry is validated; none is silently ignored)
   - two conditions sharing an id anywhere in the map
4. REQUIREMENT: Any violation makes `gz content commit` exit 3 and write NOTHING: no rendition, no provenance sidecar, no retention sidecar, no ledger event. The refusal prints each violation with the removed block's first line and a three-part recovery (`.claude/rules/guardrail-feedback-prose.md`).
5. REQUIREMENT: On success, the validated map is written to `.gzkit/renditions/<surface>/<consumer>.retention.json`, in the same transaction order as the rendition and provenance writes. The next promotion overwrites it; history lives in git beside the rendition. A promotion with no removed blocks removes any stale retention sidecar, so a sidecar never describes a delta it did not govern.
6. REQUIREMENT: The `RetentionMap` model is Pydantic, `frozen=True`, `extra="forbid"` (`.gzkit/rules/models.md`). Condition ids are short, human-typable tokens (`C1`, `C2`, …), unique within a map, so the operator can name a drop in plain words.
7. NEVER call an LLM, the network or a subprocess from `retention.py` or the gate. Extraction is agent work recorded in the map. The tool checks only what a byte comparison can prove (ADR-0.35.0 § Alternatives L).
8. NEVER weaken an existing `commit` refusal: an empty attestation on a moved corpus, an absent candidate or an absent corpus still fail exactly as today. The retention gate runs after those checks and before any write.
9. ALWAYS treat the named residual as disclosed, not solved. The tool cannot prove that the reviewer extracted every sub-clause condition, that a KEPT span carries the same meaning as its quote (a KEPT span is checked only for presence in the candidate), that a drop id in the attestation text came from the operator, or that the reviewer was a different model rather than a different name. The sentence-coverage floor bounds the first at clause level. The rule against fabricating operator words holds the second. The third is left to the skill's dispatch record. The Layer-2 retention digest is deferred with the security-surface exclusion above and must be surfaced to the operator at completion.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Retention Map Contract

```json
{
  "surface": "AGENTS.md",
  "consumer": "root",
  "extracted_by": "<reviewer agent identity>",
  "mapped_by": "<author agent identity>",
  "blocks": [
    {
      "removed": "<the removed block, verbatim>",
      "conditions": [
        {"id": "C1", "quote": "<substring of removed>", "disposition": "kept", "span": "<substring of candidate>"},
        {"id": "C2", "quote": "<substring of removed>", "disposition": "dropped", "reason": "<why>"}
      ],
      "non_binding": [{"quote": "<substring of removed>", "reason": "<why this sentence binds nothing>"}]
    }
  ]
}
```

Coverage: mark every character of the removed block that lies inside any occurrence of a non-empty condition quote or non-binding quote. Every meaningful character must be marked: any non-whitespace character except markdown markup (`*`, `_`, `` ` ``, `#`, `|`, `>`) and the block's leading list marker. Symbols such as `<=`, `≥`, `%` and `--` count, because they change meaning. Report each sentence that holds an unmarked alphanumeric character, quoting the unmarked text. Mere overlap is NOT coverage: a condition quoting three words of a sentence leaves the rest of the sentence unaccounted for, and that residue is exactly where a dropped qualifier hides (Change Log 2026-09-24).

**The #1090 replay, as a fixture:**
- Prior block: `c3582975f:AGENTS.md:234`, verbatim.
- Candidate: the compressed bullet the 2026-09-17 diet landed.

"`--accept-uncovered` is refused on every lane" has no KEPT span in that candidate. A map that marks it KEPT fails the span check. A map that omits it, or that quotes only "cannot be waived" from the same sentence, fails coverage. Only a DROPPED disposition named in the attestation text passes, and that makes the loss visible and operator-owned.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 10, "NO LANDING LOSES MEANING WITHOUT AN APPROVED DROP".
- [ ] Parent ADR § Intent — the 2026-09-24 amendment. It explains why the gate reads the rendition delta rather than the corpus retirement log.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] GHI #1090 and its two comments: the motivating loss and its restore at `5d6b9d173`
- [ ] BI-03, BI-06 and BI-10 in the parent ADR. BI-10 is this OBPI's fence against OBPI-07's `content land`.
- [ ] OBPI-0.35.0-07 brief: `land` must call this gate (BI-10), so the gate's entry point must be callable without the CLI

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/commands/content/commit.py`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/content/lineage.py` (pattern for the sidecar path helper)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/commit.py` — the check order (candidate, corpus, attestation) and the write order (`save_rendition`, `save_fingerprint`, `emit_rendition_committed`)
- [ ] `src/gzkit/content/lineage.py` — `lineage_path` / candidate-lineage sidecar layout to mirror
- [ ] `src/gzkit/content/rendition_store.py` — `rendition_path`, `load_fingerprint`; confirm no field is added to `RenditionProvenance`
- [ ] `src/gzkit/commands/content/__init__.py` — the `commit` parser registration near the `--attestation-text` help
- [ ] `tests/commands/test_content_commit.py` and `features/content_retire.feature` — fixture and step conventions
- [ ] Parent ADR integration points reviewed for local conventions

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
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run -m unittest tests.content.test_retention tests.commands.test_content_commit
uv run -m behave features/content_commit_retention.feature
uv run gz validate --documents --req-kind-discipline --cli-alignment
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

Run against a temporary copy of the repository so no canon moves. Retain the refusal text, not only the exit code.

```bash
uv run gz content compose AGENTS.md --consumer root --candidate lossy-candidate.md
uv run gz content commit AGENTS.md --consumer root --attestor g0 --attestation-text "demo"
uv run gz content commit AGENTS.md --consumer root --attestor g0 --attestation-text "demo, drop C2 approved" --retention-map retention.json
```

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-14-01 [BEHAVIOR]: Given a prior committed rendition and a candidate from which one or more prior blocks are absent, when `gz content commit` runs without `--retention-map`, then it exits 3, names every removed block, and writes no rendition, provenance sidecar, retention sidecar or ledger event
- [ ] REQ-0.35.0-14-02 [BEHAVIOR]: Given a retention map, when any condition quote is not a substring of its removed block, any KEPT span is not a substring of the candidate, any DROPPED condition has an empty reason, or any sentence of a removed block is covered by no condition and no non-binding declaration, then the commit exits 3 and the output names every violation, not only the first
- [ ] REQ-0.35.0-14-03 [BEHAVIOR]: Given a retention map whose `extracted_by` or `mapped_by` is empty, or whose two identities are equal after case-folding and trimming, when `gz content commit` runs, then it exits 3 and names the independence violation
- [ ] REQ-0.35.0-14-04 [BEHAVIOR]: Given a map with a DROPPED condition, when the condition's id is absent from `--attestation-text` the commit exits 3; when it is present and every other check passes, the commit succeeds and `<consumer>.retention.json` holds the validated map
- [ ] REQ-0.35.0-14-05 [BEHAVIOR]: Given no prior committed rendition, a byte-identical re-render, a candidate that only adds or reorders blocks, or a whitespace-only difference, when `gz content commit` runs without a map, then it succeeds exactly as before this OBPI. A promotion with no removed blocks leaves no stale retention sidecar behind.
- [ ] REQ-0.35.0-14-06 [BEHAVIOR]: Given the #1090 replay fixture (prior block from `c3582975f:AGENTS.md:234` verbatim; candidate carrying the 2026-09-17 compressed bullet), when a map marks every condition KEPT, then the commit exits 3 on the `--accept-uncovered` condition, whose span is absent from the candidate. The same map with that condition DROPPED and its id in the attestation text succeeds.
- [ ] REQ-0.35.0-14-07 [SUPPORT]: `docs/user/manpages/content.md` documents `--retention-map`, the map schema, the sidecar, exit 3 and the recovery. `.gzkit/skills/gz-content-compose/SKILL.md` instructs dispatching an independent reviewer to extract conditions before the author maps them, and presenting every DROPPED condition to the operator by id before commit. Witnessed by `artifact_edited` citing both paths + `gz validate --documents --cli-alignment`.
- [ ] REQ-0.35.0-14-08 [STRUCTURAL-FENCE]: Every path that promotes a candidate to a committed rendition enforces the retention gate over the same prior-rendition delta. None reaches `save_rendition` around it — audited at ADR closeout against § Boundary Invariants BI-10.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Change Log

- 2026-09-24, Requirement 3 and § Retention Map Contract (REQ-0.35.0-14-02, -06): coverage changed from "a sentence is covered when it overlaps a condition quote" to "every alphanumeric character lies inside some condition or non-binding quote". The overlap rule was an authoring error that weakened ADR-0.35.0 Decision 10, which says every sentence "lies inside at least one condition". Observed counterexample on the Task 1 code: a map quoting only "REQ-coverage gate", "BEHAVIOR REQ" and "cannot be waived" as KEPT returned zero violations while the #1090 clause "`--accept-uncovered` is refused on every lane" went unaccounted. The brief now matches the operator-ruled ADR; no operator ruling was changed.
- 2026-09-24, Task 1 orchestrator findings before review (REQ-02/-03/-06): empty-quote coverage bypass, unnormalized candidate, substring drop-id match, list/table/numbered/bold block boundaries, missing duplicate-id check, and missing splitter/delta tests. All fixed red-first by a sonnet fix dispatch (37 tests).
- 2026-09-24, Stage-2 review of Task 1 (findings q1-req06-dropped-attested-weak, F-REQ06-success-half-unproven, F-REQ06-covers-misbinding; spec receipt arb-step-specreview-ca344ab5c4424eaeb9c8065c4aa34812, quality receipt arb-step-qualityreview-28adece31aa64afb8171cef106776dd4): REQ-06's success half was unasserted and its fixture was not verbatim; unit tests were bound to the CLI-level REQ-01/-04; the duplicate-id tests were bound to REQ-06. The quality review also noted that alphanumeric-only coverage misses meaning-bearing symbols (`<=`, `%`), that the span check read the unnormalized candidate, that there were two divergent sentence splitters, and that duplicate or unknown map entries went unvalidated. Requirement 3 and the contract were widened to meaningful-character coverage and whole-map validation accordingly. Follow-up round findings (spec receipt arb-step-specreview-7bf7c9a414754f22864ba43cd8159e43, quality receipt arb-step-qualityreview-7b6728d1f769451d94f8ada4cb45d025; both refused at import because the envelope was malformed): REQ-02/-03 proofs lacked mutations for quote-in-block, empty reason and empty identities, so the specs were extended and re-proved; REQ-05 was bound on two unit tests, and the orchestrator removed those bindings; `lower()` was used where the contract says case-folding, and the orchestrator changed it to `casefold()`. A KEPT span is not related to its quote: this is disclosed as a judgment residual in ADR Decision 10 and Requirement 9, and mitigated by the reviewer check and by operator display (Task 2 prints every KEPT pair; Task 4's skill requires the reviewer to verify each pair). 2026-09-25, full `gz check` before the session sync (orchestrator corrections; they stale all proofs, which are re-run after the block ruling): removed an unused `# type: ignore` in test_retention.py; removed the hardcoded manpage path from the commit refusal prose (GHI #425 single-source rule); shortened the `--retention-map` help to 80 characters or fewer; and ALLOWLIST AMENDMENT pending operator ratification: `src/gzkit/content/corpus_store.py` and `src/gzkit/content/rendition.py` added as read-only fixture imports, because brief_reconcile counts the covering tests' imports as subjects. Task 2 follow-up review (spec receipt arb-step-specreview-497d837133ce4457a4be5cda74bcb4c3, imported, refuted, REQ-06 approval withheld; quality receipt arb-step-qualityreview-(t2r2), imported, accepted all six): the REQ-04 refusal-content repair was confirmed. New counterexample (REQ-04/-06, Requirement 6): an empty condition id satisfies the token-boundary attestation check against any text. Sent to review fix cycle 2 with id-pattern validation, map-level violation labels, one first_line helper, a stronger recovery assertion, and CLI selectors added to the REQ-06 proof. Task 2 Stage-2 review (spec receipt arb-step-specreview-a29c996114b44c0b8a445499b3802bb3, refused at import for an extra field; quality receipt arb-step-qualityreview-f9f8452a243d418a820d15904ec419ad, imported and accepted all six proofs): the spec review's mapped finding spec-t2-req04-refusal-content-unproven (the REQ-04 tests did not assert first-line naming, the recovery prose, or provenance/ledger non-writes on a validator refusal) is acted on even though the import failed. The quality review found that a non-UTF-8 map escaped as a traceback and that the CLI replay asserted only 'C1'; both were sent back as review fix cycle 1. Known limitation, deferred to its owner rather than rebuilt here: a partial IO failure after save_rendition and save_fingerprint leaves the rendition promoted without its retention sidecar. The two existing writes already share that exposure, and atomic multi-file publication is OBPI-0.35.0-07's journaled landing (ADR-0.35.0 Decision 6). Task 2, orchestrator finding before review (REQ-0.35.0-14-04, Requirement 3): the gate checked drop ids against the EFFECTIVE attestation, which can be a standing attestation carried forward from an earlier commit when an explicit candidate removes text without moving the corpus, so an old attestation containing 'C1' would satisfy a new drop. The defect was the orchestrator's Task 2 prompt ('effective'), not the contract, which says 'the attestation text'. It was sent back to the Task 2 implementer to fix red-first: drop ids must appear in the --attestation-text supplied with this commit. Closing round (spec receipt arb-step-specreview-d693eccc4f954fa3a7b904ceb445f79d, quality receipt arb-step-qualityreview-75b2e197a72f438a8d22c2862414d056): both accepted proofs proof-49bc68858ce44563942747ae9f7d116c (REQ-02), proof-78fb1ea595d74fdf9da641bf68a2824f (REQ-03) and proof-af0671c7d7cc4fc285a04866a0d058f9 (REQ-06), and closed all three mapped findings; Task 1 Stage-2 status is ready. Advisory, unmapped: split_blocks exceeds the lizard nloc/ccn bands (xenon C passes). Repaired in review fix cycle 1 (sonnet): verbatim #1090 fixture with a complete map and three REQ-06 assertions (passes / only the unattested drop fires / absent KEPT span fires); meaningful-character coverage; normalized span check; one sentence splitter; duplicate and unknown map entries; validate_retention split into per-check helpers (xenon C ceiling clean). The orchestrator rebound the last two REQ-04 unit tests to REQ-02. Re-proved REQ-02 (coverage, symbol, span and drop-attestation mutations), REQ-03 and REQ-06 (coverage, drop-attestation and span mutations); 46 tests OK.

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

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #1090 — the motivating loss (lane scope dropped by the 2026-09-17 compression); restored at `5d6b9d173`, independently of this OBPI.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
