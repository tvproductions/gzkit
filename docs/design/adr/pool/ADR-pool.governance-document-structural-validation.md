---
id: ADR-pool.governance-document-structural-validation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.governance-document-structural-validation: Structural Validation for Governance Documents

## Status

Pool

## Intent

A governance document's meaning is currently inferred from **string presence**
rather than from an enforced parse. Where a schema exists it is often not the
only reader; where no schema exists, ad-hoc regex is the whole contract. The
consequence is not theoretical — it has passed Gate 5.

This ADR carries the residual class catalogued on GHI #615 after that issue's
three filed instances were closed (`995bc86b`, `8f284a36`, `5111b7dd`,
`a0a2e10e`, `72f65a7a`, `e5494fd3`, `3e761f6b`, `4a256b7a`). The remaining
instances arrived afterwards as sibling cuts across *different artifact types*,
which is why they need one surface rather than one fix each.

### Evidence corpus (measured, not asserted)

| Surface | Observed state | Source |
|---|---|---|
| ADR `## Persona` | **No validator at all.** Five ADRs shipped carrying the literal scaffold token `{persona}`; four are Validated/Completed, i.e. they passed Gate 5. Its neighbour `## Why foundation tier?` *is* mechanically enforced. | GHI #741 |
| Doc-content REQ proof | Three rounds of regex hardening produced three rounds of new bypasses. Still accepted after round 3: nested blockquotes, tilde-fence decoys, four-space-indented markers, setext duplicates, case-variant duplicates, HTML comments spanning a closing fence. | GHI #615 (2026-07-29, and its correction) |
| Pool-ADR Step-0 interview | Answer JSON is unschema'd. | GHI #719 |
| Handoff sections | `validate_sections_present` / `_populated` locate required sections by `re.search(rf"^##\s+{section}\s*$")` over raw Markdown; section bodies are untyped, so a decision cannot be marked operator-ruled or settled. | GHI #696 |
| Frontmatter parsing | **20 modules** parse frontmatter by hand, across skills, personas, rules, chores, handoffs, OKF, and briefs. (Re-measured 2026-08-03; GHI #615's original "~14 ADR parsers" understated the breadth and misstated the shape.) | GHI #615 instance 2 |
| `--brief-reconcile` escalation | Still keys on structural shape rather than lifecycle. Post-migration this stops mattering for the 146 migrated briefs; the keying itself is unchanged. | GHI #615 (2026-06-16) |

### Why the closed instances are the argument for this ADR

The three closed instances each ended the same way: **one grammar, derived, not
re-spelled.**

- Briefs: `BriefStructure` existed and was never enforced; 597/600 fell to
  regex-scraped `LegacyBriefShape`. Enforcing it required migrating 146
  non-terminal briefs and fencing 514 terminal ones.
- REQ kind: four hand-synced copies of a three-member taxonomy (the enum, a
  string→enum map, a regex alternation, a frozenset). The copies disagreed
  silently, and a `dict[str, str]` schema admitted `STRUCTURAL_FENCE` — the
  Python member name — then coerced it to `BEHAVIOR`, re-imposing the exact
  proof channel the operator had waived.
- REQ identifier: ~20 regexes disagreeing on component width, so
  `REQ-0.0.37-1-1` was decomposable but unvalidatable. Corpus measurement
  settled it: 0 of 4396 occurrences used a non-canonical width.

In every case the defect was invisible to `ty` and `unittest` because nothing
asserted that the copies agreed. That is the property this ADR must supply
generally.

## Decision

*(Pool — noted, not committed. Promotion requires the operator's ruling on
scope and sequencing.)*

Establish **one structural-validation surface for governance documents**: each
artifact type parses once into a typed representation, every reader derives
from that representation rather than restating it, and "does this surface have
a schema, and is it enforced?" becomes a mechanical question with a
fail-closed answer.

Candidate decomposition, in dependency order:

1. **A parsed-document representation** for governance Markdown — headings,
   fences, blockquotes, and frontmatter as structure rather than lines. The
   doc-content instance cannot be closed without this; a fourth regex round is
   the symptom, not the remedy.
2. **Frontmatter through one parser.** Collapse the 20 hand-rolled sites onto
   the existing per-artifact models, so a document has one shape, not N.
3. **Section-presence and section-content validation** driven by a per-artifact
   declaration of required sections — absorbing GHI #741's persona audit and
   GHI #696's typed-decision need instead of shipping two one-off validators.
4. **A schema-coverage gate**: a governance artifact type with no enforced
   schema is itself reportable. Today an unenforced schema and an absent one
   are indistinguishable from outside.
5. **Escalation keyed on lifecycle, not structural shape** (`--brief-reconcile`).

Sequencing note: item 1 is the precondition for item 3's content arm; items 2
and 5 are independent and could land first.

## Alternatives Considered

1. **Harden the regexes per surface.** *Rejected on measured evidence.* Three
   independent adversarial passes against the doc-content proof defeated three
   successive hardenings; the accepted bypasses satisfied every string check
   while asserting the opposite meaning (one enumerated the correct tokens,
   cited the right ADR, then instructed the reader to do the forbidden thing).
   The adversary's own root-cause statement is the refutation: the proof
   *"treats Markdown as a few raw string patterns rather than checking the
   rendered document or a real Markdown structure."*

2. **One validator per artifact type, as each defect surfaces.** *Rejected.*
   This is the proliferation GHI #741 explicitly warns against, and it
   reproduces the very failure being fixed — N independently-authored readers
   of one document shape, free to disagree, with nothing asserting they agree.
   It is the four-copies-of-the-taxonomy pattern at a larger grain.

3. **Accept the current state as advisory.** *Rejected.* It is not advisory in
   effect: four ADRs carrying a literal `{persona}` scaffold token passed Gate
   5. A gate that admits an unfilled template is not reporting a preference.

4. **Full Markdown AST for every governance surface, uniformly.** *Rejected as
   over-reach.* The doc-content instance genuinely needs a parsed document; the
   frontmatter and identifier instances need only one parser and one grammar,
   which are cheaper and independently landable. Uniform AST would couple a
   large dependency decision to defects that do not require it, against
   STDLIB-FIRST.

5. **Route each remaining instance back to its own GHI for direct fix.**
   *Rejected as the status quo that produced this catalogue.* GHI #615 has
   accreted sibling cuts since 2026-06-14 without converging, because each cut
   is individually small and collectively architectural. That is the shadow
   -tracker shape `docs/governance/state-doctrine.md` names.

## ADR relationship

| ADR | Relationship |
|---|---|
| `ADR-0.0.37` | Shipped `BriefStructure` (OBPI-04), the schema whose non-enforcement GHI #615 filed on. Terminal since 2026-07-18; no work lands there. |
| `ADR-0.0.59` | Owns the REQ three-kind taxonomy and calls its enum *"a deliberate one-way door"* — an amendment previously had to update four hand-synced copies with nothing checking. Now one. |
| `ADR-0.0.20` | Rule-scoping enforcement (`--unscoped-rules`) — precedent for a mechanical structural check over a governance surface. |
| `ADR-0.35.0` | Corpus→candidate landing. Adjacent, not overlapping: that ADR governs how canon *content* is materialized; this one governs whether a governance document's *structure* is parsed or scraped. |

## Related GHIs

`#615` (class/catalogue surface), `#741` (ADR `## Persona`, absent enforcement),
`#719` (pool-interview JSON), `#696` (handoff sections), `#581` (dead citations
— consumes the class-B corpus), `#544` (grandfathering-cache fail-closed intent,
whose guarantee this class silently voided).

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
