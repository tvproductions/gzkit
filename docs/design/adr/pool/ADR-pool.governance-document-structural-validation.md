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
| ADR `## Persona` | **Discharged 2026-07-31 (`36f3e9f3f`) — by a standalone validator.** Was: no validator at all, five ADRs shipped carrying the literal scaffold token `{persona}`, four of them Validated/Completed. Now `persona_witness.py` enforces the section over `foundation/` + `pre-release/`, and `render_template` raises on every missing variable rather than emitting residue. Retained in this corpus because *how* it closed is itself evidence — see Alternatives Considered §2. | GHI #741 (CLOSED) |
| Doc-content REQ proof | Three rounds of regex hardening produced three rounds of new bypasses. Still accepted after round 3: nested blockquotes, tilde-fence decoys, four-space-indented markers, setext duplicates, case-variant duplicates, HTML comments spanning a closing fence. | GHI #615 (2026-07-29, and its correction) |
| Pool-ADR Step-0 interview | Answer JSON is unschema'd. | GHI #719 |
| Handoff sections | **Still regex-located; the typed-decision half is discharged.** `validate_sections_present` / `_populated` locate required sections by `re.search(rf"^##\s+{section}\s*$")` over raw Markdown (`handoff_validation.py:272,301`), as does every body reader. A decision *can* now be marked operator-ruled or settled — `validate_decision_markers` (`:325`) plus Settled-Rulings promotion landed under #696. The residue is the parse, not the vocabulary: #722 then dropped 10 operator rulings silently because `_section_items` required a list marker the attribution rule never named, under a clean validation pass. | GHI #696, #722 (both CLOSED) |
| Frontmatter parsing | **20 modules** parse frontmatter by hand, across skills, personas, rules, chores, handoffs, OKF, and briefs. (Re-measured 2026-08-03; GHI #615's original "~14 ADR parsers" understated the breadth and misstated the shape.) | GHI #615 instance 2 |
| `--brief-reconcile` escalation | Still keys on structural shape rather than lifecycle. Post-migration this stops mattering for the 146 migrated briefs; the keying itself is unchanged. | GHI #615 (2026-06-16) |
| `--brief-reconcile` dimensions | **All five dimensions are existence/resolution checks; none reasons about liveness or change-kind coupling.** Three measured failure classes, each returning the same clean `0` (see Decision item 6). Worst measured cost: the `gz content retire` collision sat unreconciled for 16 days under a green `brief-drift`, and implementing `OBPI-0.35.0-02` as written would have stood up a second retirement verb beside the shipped one. | GHI #581 (closed `superseded` into this ADR 2026-08-08) |

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
   declaration of required sections. Both one-off validators this item was
   meant to pre-empt have since shipped — `persona_witness.py` under GHI #741,
   `validate_decision_markers` under GHI #696 — so the scope is now
   *collapsing two existing readers* onto one declaration, not *absorbing two
   open needs*. The work grew while this ADR sat in pool; it did not shrink.
4. **A schema-coverage gate**: a governance artifact type with no enforced
   schema is itself reportable. Today an unenforced schema and an absent one
   are indistinguishable from outside.
5. **Escalation keyed on lifecycle, not structural shape** (`--brief-reconcile`).

6. **Reachability as a first-class dimension, three-valued** (`--brief-reconcile`).
   The five existing dimensions all ask *does this path resolve?*; none asks
   *is this surface's relationship to the brief what the brief says it is?*
   Three measured classes return a clean `0` today:

   | Class | Shape | Why every dimension misses it |
   |---|---|---|
   | cross-directory coupling | required surface absent from the allowlist | `_compute_missing_in_brief` filters by same-parent-directory neighborhood, so scattered couplings are structurally invisible |
   | exists-but-dead | cited surface resolves but has zero consumers | `_compute_citation_delta` flags only `not path.exists()`; existence is not liveness |
   | exists-but-should-not-yet | a planned-`CREATE` surface already ships, possibly under another name | absence is what a `CREATE` brief *should* look like; nothing compares the planned verb against the registered verb set |

   **The naive cure is worse than the disease, and this is the binding
   constraint on the item.** A two-valued liveness check would have flagged
   `.gzkit/schemas/ledger_events.json` — zero `src/`, `tests/`, or `features/`
   consumers — and acting on that flag would have deleted a file named as the
   literal subject of two sealed REQs (`REQ-0.0.37-03-04`,
   `REQ-0.0.37-08-07 [support]`) on a Validated ADR, falsifying Gate-5
   evidence. The operator ruled the file stays, retired only by forward
   supersession, never `git rm` (2026-07-26, verbatim: *"forward supersession,
   keep the file"*). So the dimension needs **evidence-reachability** (is this
   path named by any REQ, waiver, or attested brief?) as an input distinct from
   **code-reachability**, resolving to three states — `live`, `frozen`
   (runtime-dead, evidence-live: never remove) and `dead` — never two. A check
   that cannot separate `frozen` from `dead` is not safer than the existence
   check it replaces; it is more confidently wrong.

Sequencing note: item 1 is the precondition for item 3's content arm; items 2
and 5 are independent and could land first. Item 6 is independent of item 1 —
it needs a reachability index, not a document parse — but it must not land as a
standalone reader, which is the shape § Alternatives 2 rejects and the reason
GHI #581 rode here rather than direct-fixing.

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
   **Observed since filing (2026-08-04):** GHI #741 and GHI #696 were each
   discharged by precisely this shape, adding `persona_witness.py` and
   `validate_decision_markers` as two further independently-authored readers.
   The rejection is now evidenced rather than predicted — and #722 is what the
   prediction looks like when it lands: #696's composer was correct, the
   parser feeding it was not, and nothing asserted the two agreed.

3. **Accept the current state as advisory.** *Rejected.* It is not advisory in
   effect: four ADRs carrying a literal `{persona}` scaffold token passed Gate
   5 — remedied under GHI #741, and cited here as demonstrated consequence
   rather than as a live gap. A gate that admits an unfilled template is not
   reporting a preference.

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

State as of **2026-08-08**. This block is a snapshot, not a live view —
re-check it before promotion rather than reading it as current.

**Open:** `#719` (pool-interview JSON, unschema'd).

**Closed:** `#615` (class/catalogue surface; closed `superseded` into this ADR
2026-08-04), `#581` (`--brief-reconcile` existence-only dimensions; closed
`superseded` into this ADR 2026-08-08 — see Decision item 6), `#741` (ADR
`## Persona`; closed 2026-07-31 by a standalone validator), `#696` (handoff
sections; closed 2026-07-25) with its follow-on `#722` (closed 2026-07-26),
`#544` (grandfathering-cache fail-closed intent, whose guarantee this class
silently voided; closed 2026-07-01).

`#581` is the second issue to close `superseded` into this ADR, and it closed
for a reason worth carrying to promotion: it had been re-derived to the same
TRACK-ONLY answer **seven times** between 2026-06-05 and 2026-08-07, twice
against destinations that were themselves later retired (the 6→1 event-registry
collapse, withdrawn 2026-07-26 on measured evidence that the registries do not
drift and `audit_event_schemas` already holds the coupling). An issue that
accumulates diagnoses without converging is the shadow-tracker shape
§ Alternatives 5 names, arriving one level up.

A closed sibling does **not** shrink this ADR's scope. Each closed by adding a
reader of a document shape nothing else asserts agreement with — which is the
count Decision item 3 exists to collapse.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
