---
id: OBPI-0.35.0-14-meaning-preserving-landing
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 14
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/content/retention.py
  - src/gzkit/commands/content/commit.py
  - src/gzkit/commands/content/__init__.py
  - tests/content/test_retention.py
  - tests/commands/test_content_commit.py
  - features/content_commit_retention.feature
  - features/steps/content_commit_retention_steps.py
  - docs/user/manpages/content.md
  - .gzkit/skills/gz-content-compose/SKILL.md
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
- `tests/content/test_retention.py` — **CREATE**, following `tests/content/test_lineage.py`
- `tests/commands/test_content_commit.py`
- `features/content_commit_retention.feature` — **CREATE**, following `features/content_retire.feature`
- `features/steps/content_commit_retention_steps.py` — **CREATE**, following `features/steps/content_retire_steps.py`
- `docs/user/manpages/content.md` — the `commit` section: flag, sidecar, refusal and recovery
- `.gzkit/skills/gz-content-compose/SKILL.md` — the wielding skill: reviewer dispatch, map authoring, presenting drops to the operator
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
   - a sentence of a removed block not covered by any condition quote and not declared non-binding with a non-empty reason
   - a condition quote that is not a substring of its removed block
   - a KEPT span that is not a substring of the candidate
   - a DROPPED condition with an empty reason
   - `extracted_by` or `mapped_by` empty, or equal to each other after case-folding and whitespace trimming
   - a DROPPED condition whose id does not appear in the attestation text
4. REQUIREMENT: Any violation makes `gz content commit` exit 3 and write NOTHING: no rendition, no provenance sidecar, no retention sidecar, no ledger event. The refusal prints each violation with the removed block's first line and a three-part recovery (`.claude/rules/guardrail-feedback-prose.md`).
5. REQUIREMENT: On success, the validated map is written to `.gzkit/renditions/<surface>/<consumer>.retention.json`, in the same transaction order as the rendition and provenance writes. The next promotion overwrites it; history lives in git beside the rendition. A promotion with no removed blocks removes any stale retention sidecar, so a sidecar never describes a delta it did not govern.
6. REQUIREMENT: The `RetentionMap` model is Pydantic, `frozen=True`, `extra="forbid"` (`.gzkit/rules/models.md`). Condition ids are short, human-typable tokens (`C1`, `C2`, …), unique within a map, so the operator can name a drop in plain words.
7. NEVER call an LLM, the network or a subprocess from `retention.py` or the gate. Extraction is agent work recorded in the map. The tool checks only what a byte comparison can prove (ADR-0.35.0 § Alternatives L).
8. NEVER weaken an existing `commit` refusal: an empty attestation on a moved corpus, an absent candidate or an absent corpus still fail exactly as today. The retention gate runs after those checks and before any write.
9. ALWAYS treat the named residual as disclosed, not solved. The tool cannot prove that the reviewer extracted every sub-clause condition, that a drop id in the attestation text came from the operator, or that the reviewer was a different model rather than a different name. The sentence-coverage floor bounds the first at clause level. The rule against fabricating operator words holds the second. The third is left to the skill's dispatch record. The Layer-2 retention digest is deferred with the security-surface exclusion above and must be surfaced to the operator at completion.

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

Sentence coverage: split each removed block on sentence ends (`.`, `?`, `!`, `;` followed by whitespace or end of block) after stripping list markers and heading hashes. A sentence is covered when it overlaps at least one condition quote or `non_binding` quote. Use overlap, not containment, so that a sentence can be split across several conditions. The exact splitting rule belongs to the implementer, but the #1090 replay in REQ-06 MUST be refused under whatever rule is chosen.

**The #1090 replay, as a fixture:**
- Prior block: `c3582975f:AGENTS.md:234`, verbatim.
- Candidate: the compressed bullet the 2026-09-17 diet landed.

"`--accept-uncovered` is refused on every lane" has no KEPT span in that candidate. A map that marks it KEPT fails the span check. A map that omits it fails sentence coverage. Only a DROPPED disposition named in the attestation text passes, and that makes the loss visible and operator-owned.

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

_No substantive adjustments recorded yet._

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
