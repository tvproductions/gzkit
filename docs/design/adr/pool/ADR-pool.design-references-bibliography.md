# ADR-pool.design-references-bibliography

- **Status:** Pool
- **Lane:** Lite
- **Date:** 2026-04-13
- **Origin:** OBPI-0.25.0-30 pattern-absorption review — airlineops `references.py` Exclude decision surfaced the need for a gzkit-native bibliography surface

## Intent

Curate a design-references bibliography inside gzkit for the SDD, AI-governance, and agent-engineering literature that grounds gzkit's design reviews. Today this material exists only as URLs shared in-session and embedded informally in ADR rationales — there is no durable, citable surface the project can reference when justifying architectural choices. A bibliography would give reviewers, operators, and future maintainers a stable anchor for "why does gzkit do X this way?" that does not rot as context windows shift.

## Target Scope

### Bibliography surface

- `docs/references/` — root directory for reference material (URLs, PDFs, or
  hybrid — the design decision is deferred to promotion)
- `docs/REFERENCES.md` — canonical bibliography index, with entries in a
  consistent citation format (author, title, publisher/venue, year, URL or
  DOI)
- Optional `docs/ANNOTATED_BIBLIOGRAPHY.md` — narrative notes explaining why
  each reference matters to gzkit and which ADRs it grounds

### Citation tooling

- A minimal generator that reads structured entries (JSON/YAML/frontmatter —
  format decided at promotion) and renders the canonical bibliography block
  into `docs/REFERENCES.md`
- AUTO-marker block substitution so hand-written prose and generated entries
  coexist cleanly (pattern borrowed from airlineops `references.py:763-779`
  `_replace_block` — twelve-line helper, worth re-implementing in gzkit
  style rather than absorbing the entire 797-line PDF-centric module)
- No `pypdf` dependency unless a concrete PDF-first use case emerges after
  promotion

### Seed content

Confirmed references to anchor the bibliography at promotion:

- Anthropic — [Project Sustainable Model](https://alignment.anthropic.com/2026/psm/)
- Anthropic — [Abstractive Red-Teaming](https://alignment.anthropic.com/2026/abstractive-red-teaming/)
- Anthropic — [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- GitHub — [Spec Kit](https://github.com/github/spec-kit)
- AWS / Kiro — [Kiro documentation](https://kiro.dev/docs/)
- Tessl — [Spec Driven Development registry tile](https://tessl.io/registry/tessl-labs/spec-driven-development)
- Specmatic — [Contract Driven Development](https://docs.specmatic.io/contract_driven_development)
- BMAD Method — [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- GSD — [get-shit-done](https://github.com/gsd-build/get-shit-done)
- Superpowers — [Claude plugin](https://claude.com/plugins/superpowers)
- EveryInc — [compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin)

The first three have already grounded substantial gzkit design reviews and
establish the kind of material the bibliography should curate: practical
engineering guidance for building governance and agent systems.

The comparator entries added on 2026-05-07 are not cited as trend-chasing
authority. They are prior-art anchors for bounded lessons: front-door ergonomics,
workflow staging, executable contracts, context-package portability, prompt
injection defense, review discipline, and compounding learning loops. The
annotated bibliography should name the specific gzkit destination ADR for each
lesson and reject any citation whose only value is popularity.

## Non-Goals

- No academic paper management — this is a design-references surface, not a
  research-library surface. PDF scanning and APA journal-article citation
  formatting are out of scope unless a real PDF-first consumer appears.
- No absorption of airlineops `references.py` wholesale — that module is
  PDF-first, `pypdf`-dependent, and carries an aviation-industry textbook
  fixture (`ROSETTA_REFERENCES_LIST`) that does not generalize. The
  capability is valuable; the specific implementation is not the right fit.
  See OBPI-0.25.0-30 Exclude rationale for the detailed comparison.
- No bibliography-as-database — entries are Markdown-first, human-editable,
  and git-versioned. No SQLite or external index.

## Dependencies

- **Blocks on:** None
- **Blocked by:** None
- **Complements:** ADR-0.25.0 (pattern absorption) — this ADR is the
  intentional follow-up to the `references.py` Exclude decision; the
  architecture here is gzkit-native rather than airlineops-inherited.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Citation entry format is decided (structured frontmatter vs flat list vs
   JSON sidecar).
3. URL-first vs PDF-first vs hybrid input format is decided — the three seed
   references are all URLs, but the design should leave room for PDFs if a
   future use case requires them.
4. Integration with ADR rationale sections is designed — how does an ADR
   cite the bibliography without fragile hand-copied URLs?
5. AUTO-marker block convention is chosen — borrow the twelve-line
   `_replace_block` pattern from airlineops or re-derive it in gzkit style.
6. Comparator entries are annotated with an "absorbed lesson" and a "rejected
   imitation" field so references cannot be used as vague authority.

## Notes

- Origin story: OBPI-0.25.0-30 evaluated airlineops `opsdev/lib/references.py`
  (797 L) for absorption and decided Exclude. The module is PDF-first, tied
  to a `docs/references/*.pdf` corpus that gzkit does not have, carries an
  aviation-industry `ROSETTA_REFERENCES_LIST` fixture, and requires `pypdf`
  as a mandatory dependency. However, the *need* it addresses — curated
  bibliography management for design reviews — is legitimate for gzkit. This
  pool ADR captures that need at the right granularity: gzkit-native design,
  seeded with material that has already grounded gzkit design reviews,
  unburdened by airlineops's implementation choices.
- The bibliography is a Layer 1 (canon) artifact in gzkit state doctrine —
  hand-authored content that lives in git, not a derived view. The citation
  generator is Layer 3 (derived) and must be rebuildable from the Layer 1
  entries.
- Risk: the bibliography becomes a link farm with no curation discipline.
  Mitigation: the annotated-bibliography companion document forces each
  entry to justify its presence by naming the design review it grounded.
- Risk: citation format churn. Mitigation: pick a simple format at promotion
  (author, title, publisher, year, URL) and resist adding fields until a
  consumer demands them.
