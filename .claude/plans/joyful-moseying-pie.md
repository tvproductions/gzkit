# Plan: OBPI-0.0.18-01 — Taxonomy Concepts Page

**OBPI:** `OBPI-0.0.18-01-concepts-page`
**Parent ADR:** `ADR-0.0.18-adr-taxonomy-doctrine` (Lite / Foundation)
**Execution mode:** Normal

## Context

ADR-0.0.17 landed the mechanical ADR taxonomy (`kind:` frontmatter, `--kind`
CLI flag, `--taxonomy` validator). ADR-0.0.18 adds the *operator doctrine*
layer: guidance, worked examples, and decision heuristics that adopters read
to ground kind/lane/semver choices.

OBPI-0.0.18-01 authors the canonical one-page concepts reference
(`docs/user/concepts/adr-taxonomy.md`) that the runbook (OBPI-02), CLI `--help`
recovery messages (ADR-0.0.17 OBPI-02/03/04), and skill prompts (OBPI-05) all
link to. Lane is **Lite** — pure documentation, no external contracts touched.

## Brief requirements

Seven FAIL-CLOSED requirements from the brief:

1. Names all three kinds (pool/foundation/feature) with one-sentence definitions.
2. Documents kind/lane orthogonality with a 2×2-plus-pool matrix.
3. Documents kind/semver binding (foundation ⇒ 0.0.x; feature ⇒ non-0.0.x; pool ⇒ no semver).
4. Documents "foundation never bumps release versioning" as a named invariant.
5. Includes one worked example per kind, sourced from gzkit's own ADR history.
6. Cross-links to ADR-0.0.17 (mechanical) and ADR-0.0.18 (this ADR).
7. `mkdocs build --strict` passes; internal links resolve.

## Worked example selections

- **Foundation**: `ADR-0.0.9 state-doctrine-source-of-truth` — canonical
  foundation ADR (defines system identity/invariant; 0.0.x semver).
- **Feature**: `ADR-0.6.0 pool-promotion-protocol` — ships a named capability
  (the promotion workflow); non-0.0.x semver.
- **Pool**: `ADR-pool.ai-runtime-foundations` — documented intent, not
  committed work; cited in `CLAUDE.md` § Architectural Boundaries.

**Brief drift to flag at completion.** The brief suggests ADR-0.0.15 as a
"feature example," but ADR-0.0.15 is 0.0.x — by the kind/semver binding the
page documents, it is a **foundation** ADR, not a feature. Using it as a
feature example would contradict the doctrine being taught. I'm substituting
ADR-0.6.0, which satisfies the binding, and will file a GHI noting the brief
drift so ADR-0.0.18 can be corrected.

## Files to modify

### New

- `docs/user/concepts/adr-taxonomy.md` — the concepts page (~150-200 lines).

### Existing

- `mkdocs.yml` — register the new page under `Concepts:` nav (insert near
  the other lifecycle/lanes entries around line 65-72).
- `docs/user/index.md` — the "Concepts" entries are nav-driven via mkdocs,
  so no explicit edit needed there; the runbook + CLI help cross-links come
  in OBPI-02 and ADR-0.0.17's follow-on OBPIs and are out of scope here.

## Page structure

1. **Title + intro paragraph** naming the three kinds (REQ-01).
2. **The three kinds** — short subsection per kind with one-sentence
   definition + "when to choose."
3. **Kind × lane orthogonality** — the 2×2-plus-pool matrix (REQ-02),
   with a sentence per cell explaining the combination.
4. **Kind × semver binding** — table showing the mechanical binding (REQ-03),
   citing `--taxonomy` validator.
5. **Named invariant: "Foundation never bumps release versioning"** —
   admonition/callout naming the invariant explicitly (REQ-04).
6. **Worked examples** — one each for foundation / feature / pool (REQ-05),
   each with link, kind, semver, and one-paragraph justification for the
   classification.
7. **Related** — cross-links to ADR-0.0.17, ADR-0.0.18, lanes.md, lifecycle.md (REQ-06).

## Style match

Match the existing concepts pages (e.g., `docs/user/concepts/lanes.md`):
- `#` title; `---` hrules separating sections
- Tables for matrices and mappings
- "Related" footer with bullet links
- No fluff; one idea per section

## Verification (Stage 3)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.18-01          # no @covers tests expected — pure doc OBPI
uv run gz validate --documents
uv run mkdocs build --strict                   # REQ-07 gate
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict   # receipt for Stage 4
uv run gz covers OBPI-0.0.18-01 --json        # REQ parity gate
```

**REQ → @covers note.** This is a pure-documentation OBPI with no unit tests.
The REQs (REQ-0.0.18-01-01 through -07) are content assertions about the
rendered markdown — they are verified by the page itself + the strict mkdocs
build, not by Python tests. Expected outcome: `gz covers` may flag all 7 REQs
as uncovered. If parity is enforced strictly, I will either (a) add a minimal
`tests/docs/test_adr_taxonomy_page.py` that asserts the page contains each
required section heading / token, each test carrying `@covers` for one REQ,
or (b) escalate to operator if tests-for-docs is out of scope. Default path:
add the minimal assertion-by-token test file under `tests/docs/` since it's a
cheap mechanical backstop and satisfies the parity gate without scope creep.

## Stage 4 evidence plan

- REQ coverage table populated from the 7 REQs with either `@covers` locations
  (if test file added) or explicit section-anchor references in the new page.
- mkdocs strict-build receipt ID from Stage 3.
- Key proof: `uv run mkdocs build --strict` output showing the new page builds
  cleanly.
- Foundation-kind attestation walkthrough per ADR-0.0.18 attestation discipline
  (doctrine drift = invariant drift).

## Stage 5 sync plan

Standard two-sync pattern:
1. `gz obpi precomplete OBPI-0.0.18-01` (pre-flight checklist)
2. `gz obpi complete OBPI-0.0.18-01 --attestor "g0" --attestation-text "<user text> — <enrichment>"`
3. `gz obpi lock release OBPI-0.0.18-01`
4. Clean pipeline markers
5. git-sync #1 (governance edits)
6. `gz obpi reconcile OBPI-0.0.18-01`
7. `gz adr status ADR-0.0.18 --json`
8. git-sync #2 (reconcile output)

## Defect to file at completion

GHI: "ADR-0.0.18 brief suggests ADR-0.0.15 as feature-kind worked example,
but ADR-0.0.15 is 0.0.x (foundation by the binding rule)." Suggested fix:
update ADR-0.0.18 OBPI-01 brief REQ-05 guidance to cite a non-0.0.x example
(e.g., ADR-0.6.0) or reclassify the guidance text.
