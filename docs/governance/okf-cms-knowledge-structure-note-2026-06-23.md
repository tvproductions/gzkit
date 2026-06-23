# OKF CMS Knowledge Structure Note - 2026-06-23

Status: operator-ratified design note. This note preserves the OKF/CMS
placement decision for the Build-to-1.0 campaign; it is not a new steering
surface and does not supersede the campaign.

## Decision

The CMS should become OKF-conformant for documentation knowledge: a small,
typed markdown knowledge bundle over existing explanatory docs, rationale docs,
research sources, and historical context that control surfaces can reference for
progressive disclosure.

OKF is not an authority layer in gzkit. ADRs, OBPIs, the ledger, active
campaign, and binding rules remain the truth surfaces. OKF provides type hints,
descriptions, tags, links, and indexes so agents can navigate the large
documentation corpus without inferring structure from filename search and prose
alone.

## Scope

Initial scope is documentation knowledge, not control surfaces first.

Included candidates:

- `docs/governance/` doctrine, rationale, appraisal, and research notes
- `docs/user/concepts/` explanatory concept docs
- selected `docs/governance/research_sources/` entries as cited sources
- selected handoffs only when they preserve historical context or failure
  analysis that remains useful after campaign reconciliation

Out of scope for the first pass:

- treating OKF as a source-of-truth replacement for ADRs, OBPIs, the ledger, or
  the campaign
- adding another bespoke gzkit doc-type taxonomy
- requiring control surfaces such as `AGENTS.md`, skills, or rules to become OKF
  concept documents before the documentation bundle works
- using OKF links or frontmatter as enforcement evidence

## Fit With Existing Architecture

gzkit already trains control surfaces to be compact pointers into deeper docs.
OKF strengthens that progressive-disclosure model by making the pointed-to docs
self-describing enough for agents to traverse.

The useful OKF shape is intentionally light:

- markdown concept documents
- YAML frontmatter with a required `type`
- optional `title`, `description`, `resource`, `tags`, and `timestamp`
- directory `index.md` files for progressive disclosure
- markdown links as graph edges

gzkit may add producer-defined keys where useful, but consumers must preserve
the OKF posture: unknown fields and unknown `type` values are not errors.

## Campaign Placement

This work should not interrupt Movement I. The Build-to-1.0 campaign currently
prioritizes the 0.0.74 substrate: gates-as-sensors residual, MX lean kernel and
hardening, then the enforcement-claim meta-validator. Those pieces give gzkit
the enforcement spine that OKF should orient around.

OKF/CMS belongs after the `0.29.0` MX substrate release, next to the Movement II
repair of the hollow antibody and inert rendition gates. The CMS/rendition
repair should make the documentation-knowledge output OKF-conformant instead of
reviving the cut doc-type taxonomy.

## Tracer Bullet

The first implementation should be a narrow, generated OKF bundle over a small
documentation slice:

1. Generate an OKF root `index.md`.
2. Generate concepts for state doctrine, trust doctrine, agent-contract
   rationale, and the active campaign reference.
3. Include only the minimal frontmatter fields needed for agent navigation:
   `type`, `title`, `description`, `resource`, `tags`, and `timestamp`.
4. Preserve source docs as the canonical authored documents.
5. Add a validator that checks OKF conformance only for the generated bundle:
   every non-reserved markdown file has parseable frontmatter and non-empty
   `type`; reserved `index.md` and `log.md` follow OKF structure.

Success is not "all docs tagged." Success is one working progressive-disclosure
path where a control surface can point an agent to the OKF bundle and the agent
can find the relevant explanatory document without reading the whole corpus.

## Rejected Alternatives

Inline the reasoning into the campaign.
: Rejected because the active campaign is intentionally slim; inline
  accretion killed its predecessor.

Invent a gzkit-specific documentation taxonomy.
: Rejected because Movement I already cuts the 0.0.74 doc-type taxonomy as a
  smuggled classification system. OKF supplies the lighter external convention.

Make OKF an enforcement or truth layer.
: Rejected because gzkit truth already lives in canon and ledger surfaces. OKF
  helps agents find and understand knowledge; it does not prove claims.

Convert control surfaces first.
: Rejected because control surfaces are already compact operational pointers.
  The immediate gap is the semantic structure of the documentation they point
  into.

## References

- [Open Knowledge Format v0.1 draft](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
- [Build-to-1.0 campaign](build-to-1.0-campaign-2026-06-20.md)
- [Agent control surface rendering substrate](agent-control-surface-rendering-substrate.md)
