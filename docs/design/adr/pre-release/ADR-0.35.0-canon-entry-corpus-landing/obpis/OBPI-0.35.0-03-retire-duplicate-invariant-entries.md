---
id: OBPI-0.35.0-03-retire-duplicate-invariant-entries
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 3
lane: Heavy
status: Draft
allowlist:
- .gzkit/corpus/AGENTS.md.jsonl
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md
reqs:
- REQ-0.35.0-03-01
- REQ-0.35.0-03-02
- REQ-0.35.0-03-03
- REQ-0.35.0-03-04
verification:
- uv run gz validate --rendition-floor-coherence
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz test
---

# OBPI-0.35.0-03-retire-duplicate-invariant-entries: Retire Duplicate Invariant Entries

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #3 - "Retire the 8 duplicate invariant entries -- 7 byte-identical + the operator-ruled divergent pair; corpus 50 -> 42 (GHI #635)"

**Status:** Draft

## Objective

Retire exactly EIGHT redundant `invariant`-tier entries from the AGENTS.md corpus under one Gate 5 batch — one redundant copy from each of the seven byte-identical groups, plus the operator-ruled loser of the divergent quote-style pair — taking the live invariant count from 50 to 42 and discharging GHI #635.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 03 depends on 01 (tombstone fields + fold) and 02 (the withdraw verb). 01 -> 02 -> 03 is the minimum shippable slice: it alone discharges GHI #635 and removes the live double-render, and it is a PREREQUISITE for 05, not a parallel workstream (ADR § Alternatives H).

<!-- gz-validate-skip: command-shape -->
> **PARTIALLY PRE-LANDED — read before implementing (reconciled 2026-07-22).**
> ONE of this brief's eight retirements landed ahead of the chain as a direct fix:
> commit `42ba6c25` retired the divergent-pair loser under GHI #635, using the
> already-landed `gz content retire` verb (`852e8a25`) rather than the
> `gz content withdraw` verb this brief's Prerequisites name. Measured
> 2026-07-22 at HEAD `9393b750`:
>
> | Requirement | Target | Observed | State |
> |-------------|--------|----------|-------|
> | REQ-0.35.0-03-01 | 8 `corpus_entry_retired` events | 1 | **1/8 landed** |
> | REQ-0.35.0-03-02 | operator ruling on the divergent pair recorded in this brief | Requirement 10 plus this note | **landed** |
> | REQ-0.35.0-03-03 | 59 raw corpus rows | 52 | **open** |
> | REQ-0.35.0-03-04 | no two live invariant entries byte-identical | 7 duplicate texts remain | **open (structural-fence)** — audited at ADR closeout |
>
> **The landed retirement is Requirement 10's target only** — the divergent pair,
> `corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00` retired,
> `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.960384+00:00`
> retained, matching the ruling recorded there. Requirements 3-9 (the seven
> byte-identical groups) are UNTOUCHED.
>
> **This brief is correctly `PENDING` and must not be completed.** Its
> Prerequisites are not met: `gz content withdraw` does not exist
> (`gz content` admits `retire` but not `withdraw`), so OBPI-0.35.0-02 has not
> landed, and the tombstone fold of OBPI-0.35.0-01 is unproven here. Re-measure
> per Requirement 2 before appending anything — the corpus has moved since this
> brief was authored (51 rows at authoring, 52 now), so the enumerated ids must
> be re-derived, not trusted.
>
> Note: as on OBPI-0.35.0-08, `gz obpi brief-drift` cannot see pre-landed REQ
> satisfaction, so this note is authored rather than computed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/corpus/AGENTS.md.jsonl` — eight appended tombstone rows, written ONLY via gz content withdraw
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` — this brief's evidence sections, including the eight entry ids and the operator ruling

## Denied Paths

- `src/gzkit/**` — this OBPI writes NO code; the mechanism is OBPI-0.35.0-01 and OBPI-0.35.0-02
- `tests/**` — a test asserting that this repository's corpus file holds 42 rows is a filesystem-grep that cannot fail when production behavior changes (`.gzkit/rules/tests.md` § REQ Scope Discipline). The fold's behavior is proven in OBPI-0.35.0-01; this OBPI's proof channels are the ledger and the parent ADR's Boundary Invariants.
- `AGENTS.md`, `.gzkit/renditions/**` — recomposing the rendition is OBPI-0.35.0-05 and OBPI-0.35.0-07
- Direct edits to `.gzkit/corpus/AGENTS.md.jsonl` by any means other than gz content withdraw — hand-editing an append-only store is alternative E under another name
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: EXACTLY EIGHT entries are retired. Not seven, not nine. The count was re-measured against `.gzkit/corpus/AGENTS.md.jsonl` before this brief was written: 51 rows total, 50 `invariant` + 1 `compressible`; seven byte-identical `invariant` groups of size two each (seven redundant copies) plus the operator-ruled divergent pair (one more). An off-by-one inside a Gate 5 batch is a fabricated receipt.
2. REQUIREMENT: ALWAYS re-measure before appending. Re-derive the group membership from the corpus on disk at implementation time and compare it to the ids enumerated in this brief. If the sets differ, STOP and emit BLOCKERS — do not reconcile silently.
3. REQUIREMENT: GROUP 1 (cross-section, `attestation` / `operator-doctrine-verbatim-canon`) — retire `corpus-attestation-2026-06-06T06:20:27.327411+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:19.779516+00:00`. ("Never, ever again give me that TTY or PTY bullshit …")
4. REQUIREMENT: GROUP 2 (cross-section, `behavior-rules` / `operator-doctrine-verbatim-canon`) — retire `corpus-behavior-rules-2026-06-10T07:53:55.264205+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:28.077865+00:00`. ("The ACTIVE campaign plan …")
5. REQUIREMENT: GROUP 3 (cross-section, `behavior-rules` / `operator-doctrine-verbatim-canon`) — retire `corpus-behavior-rules-2026-06-10T08:12:41.048588+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:44.407717+00:00`. ("Magna Carta refinement …")
6. REQUIREMENT: GROUP 4 (cross-section, `attestation` / `operator-doctrine-verbatim-canon`) — retire `corpus-attestation-2026-06-10T23:22:11.236941+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:44.783639+00:00`. ("Operator authorship … recorded as 'g0' …")
7. REQUIREMENT: GROUP 5 (cross-section, `obpi-acceptance-protocol` / `operator-doctrine-verbatim-canon`) — retire `corpus-obpi-acceptance-protocol-2026-06-11T10:50:22.318951+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.194671+00:00`. ("There is no such thing as a 'headless' OBPI …")
8. REQUIREMENT: GROUP 6 (cross-section, `defect-fix-routing` / `operator-doctrine-verbatim-canon`) — retire `corpus-defect-fix-routing-2026-06-11T11:12:06.972640+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.563168+00:00`. ("GHIs are AUTHORIZED for direct repair, always …")
9. REQUIREMENT: GROUP 7 (WITHIN `operator-doctrine-verbatim-canon` — the only intra-section group) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-16T11:52:39.917448+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:46.373270+00:00`. ("Never create feature branches …")
10. REQUIREMENT: DIVERGENT PAIR (operator-ruled) — the two rows are 571 characters each and differ ONLY in quote style at four sites (`'discovering'`/`"discovering"`, `correction.'`/`correction."`, `'enhancement'`/`"enhancement"`, `'capability not yet built'`/`"capability not yet built"`). The SINGLE-QUOTE row `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.960384+00:00` IS CANON; retire `corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00`. This is the pair that already double-renders in AGENTS.md today.
11. REQUIREMENT: NEVER let the tool elect the winner. The divergent pair is settled by the recorded operator ruling above, never by a dedup heuristic — a silently-picked quote style is doctrine drift with no attestation (ADR § Alternatives D; AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 3).
12. REQUIREMENT: ALWAYS retire the cross-section duplicate and RETAIN the `operator-doctrine-verbatim-canon` row in groups 1-6. The verbatim-canon section is the operator's own home for these utterances; retaining the sibling and retiring the canon row would invert the ruling.
13. REQUIREMENT: ALWAYS supply a non-empty `--attestor` and `--reason` on every one of the eight invocations. All eight targets are `invariant` tier, so all eight are Gate 5 fail-closed (OBPI-0.35.0-02).
14. REQUIREMENT: AFTER the batch: the raw log holds 59 rows (51 + 8 tombstones) and `effective_corpus()` yields 42 live `invariant` entries and 1 `compressible`. No two live invariant entries share byte-identical text.
15. REQUIREMENT: NEVER delete, edit, or re-tier a row. All eight originals stay in the raw log verbatim; provenance survives (alternatives E and F).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision item 2 and § Consequences (Positive) #3 — corpus 50 -> 42.
- [ ] ADR § Alternatives D, E, F, G, H — the four rejected retirement shapes and the rejected generator-first ordering.
- [ ] GHI #635 — the defect this OBPI discharges.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 3 Constraint Archaeology — append-only has never been tested against attested canon; this batch is its FIRST real test, which is why the tombstone route is right and the delete route is not.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-01 landed: `effective_corpus()` folds tombstones under the pinned algebra
- [ ] OBPI-0.35.0-02 landed: gz content withdraw exists and is Gate-5 fail-closed on invariant tier
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` present and loading; 51 rows, 50 invariant + 1 compressible, re-measured at implementation time
- [ ] All sixteen entry ids enumerated in Requirements resolve against the corpus on disk
- [ ] A human attestor is available — all eight retirements are Gate 5 and there is no self-close path

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:72` — `entry.text not in rendered_text`, the substring test that hides the seven byte-identical groups today
- [ ] `src/gzkit/content/models/corpus.py` — `Corpus.append` returns a new corpus; there is no delete path anywhere in `corpus_store.py`
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` — the eight target rows and their eight retained twins

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz validate --rendition-floor-coherence
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz test
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content withdraw AGENTS.md --entry corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00 --attestor "g0" --reason "GHI #635: divergent quote-style duplicate; the single-quote operator-doctrine-verbatim-canon row is canon by operator ruling."
uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.models.corpus import effective_corpus; from gzkit.content.tier_policy import invariant_entries; c = load_corpus(Path('.'), 'AGENTS.md'); print('raw rows', len(c.entries), '| live invariant', len(invariant_entries(c)))"
uv run python -c "import collections; from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.tier_policy import invariant_entries; t = collections.Counter(e.text for e in invariant_entries(load_corpus(Path('.'), 'AGENTS.md'))); print('duplicate texts remaining:', sum(1 for v in t.values() if v > 1))"
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-03-01 [support]: The ledger carries exactly eight `corpus_entry_retired` events, one per entry id enumerated in this brief's Requirements (groups 1-7 plus the divergent-pair loser), each retirement citing a non-empty attestor and reason. Witnessed by eight `corpus_entry_appended` ledger events citing `.gzkit/corpus/AGENTS.md.jsonl`; `gz validate --rendition-floor-coherence` passes over the resulting corpus.
- [ ] REQ-0.35.0-03-02 [support]: The operator ruling on the divergent pair is recorded in `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` with both ids, the retained/retired disposition, and the four quote-style divergence sites — so a future maintainer reads a witnessed ruling rather than re-deriving a winner. Witnessed by an `artifact_edited` ledger event citing that path; `gz validate --documents` admits the brief's shape.
- [ ] REQ-0.35.0-03-03 [support]: `.gzkit/corpus/AGENTS.md.jsonl` holds 59 raw rows after the batch — the original 51 plus eight appended tombstones, with all eight retired originals still present verbatim — proving retirement was append-only and no row was deleted, edited, or re-tiered. Witnessed by eight `corpus_entry_appended` ledger events citing `.gzkit/corpus/AGENTS.md.jsonl`; `gz validate --documents` admits the resulting store.
- [ ] REQ-0.35.0-03-04 [structural-fence]: No two LIVE `invariant`-tier entries in the AGENTS.md effective corpus share byte-identical text, and this property holds after every subsequent ADR-0.35.0 OBPI lands. This is the regression fence that alternative H names: the byte-identical groups are invisible today only because the floor check is a substring test, and they become literal double-emissions the instant the OBPI-0.35.0-05 generator materializes — so the property must be audited at ADR closeout across the whole decomposition, not per-OBPI.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
