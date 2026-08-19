---
id: ADR-pool.documentation-type-templates
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.documentation-type-templates: Documentation Type Templates — The Good Docs Project Model

## Status

Pool

## Intent

Give gzkit and its adopters **a template and a shape for each kind of
document they need to write**, so that authoring a tutorial, a glossary, or a
troubleshooting page stops being a blank page every time.

The gap is a clean one, and it is orthogonal to what gzkit already has.
`docs/governance/documentation-taxonomy.md` answers *which documentation
layers are required for which artifact type, and what enforces that* — a
coverage-and-gate model across manpages, runbook entries, and docstrings.
Nothing in gzkit answers *what goes inside the document*. The two questions do
not compete; the second one is simply unanswered.

The absence is visible on disk. Every file under `.gzkit/templates/` is a
**governance** artifact — ADR, OBPI, PRD, constitution, audit, closeout,
changelog, release notes, and the vendor contract surfaces. There is no
template for any document an operator or an adopter would write *about their
software*. The rule surface is the same shape: `.gzkit/rules/` governs the
authoring of gzkit's *own* artifacts — `changelog-release-notes.md`,
`agents-md-map-doctrine.md` — and nothing governs user-facing software
documentation.

### Prior art: The Good Docs Project

The Good Docs Project publishes an open template library for software
documentation, currently release 1.6.0 ("Iron"), at
<https://gitlab.com/tgdp/templates>. Its contribution is not the templates
themselves but the **five-deliverable model** it defines per document type
(`template_deliverables.md`):

| Deliverable | Purpose |
|---|---|
| `template_<type>.md` | the fill-in skeleton, guidance in `{curly brackets}` |
| `guide_<type>.md` | how to fill in each section |
| `resources_<type>.md` | the sources the template author researched, cited |
| `process_<type>.md` | how to research, write, and maintain this type |
| `example_<type>.md` | a worked instance |

Not every type ships all five — `how-to` carries two, `reference` carries
four. A machine-readable `index.json` carries name, summary, contributors,
file list, and pack membership per type.

**That model already matches gzkit's layering**, which is the substantive
reason to adopt it rather than a preference for its prose:

| TGDP deliverable | gzkit surface that already plays this role |
|---|---|
| `template_` | `.gzkit/templates/` |
| `guide_` | `.gzkit/skills/<name>/SKILL.md` |
| `process_` | `docs/governance/*-doctrine.md` |
| `example_` | the manpage EXAMPLES requirement (AGENTS.md § Prime Directive 2) |
| `resources_` | **no home** — the nearest thing is the unpromoted design-references bibliography pool ADR |

The `resources_` row is the interesting one. Per-document-type source
citation is standard practice for TGDP and is a capability gzkit has parked.

### Measured warrant

**Every figure below is a dated record of a measurement, not an authoritative
value** (`.gzkit/rules/governance-core.md` § Non-negotiable rules). Re-measure
before acting on any of them.

Measured 2026-08-19:

- `.gzkit/templates/` holds 13 files; **13 are governance artifacts and 0 are
  user-documentation templates**
- `.gzkit/rules/` holds 25 rule files (excluding the `AGENTS.md` directory
  contract); **3 touch document authoring and all 3 are about gzkit's own
  artifacts** — changelog/release notes, the agent-contract map doctrine, and
  complexity doctrine. None addresses user-facing software documentation.
- `docs/user/` already carries `concepts/`, `reference/`, `manpages/`,
  `quickstart.md`, `runbook.md`, `why.md` — so gzkit has partially converged on
  a type-shaped layout without a template behind any of it
- TGDP repository: created 2022-09-23, last activity 2026-08-11, 123 stars, 69
  forks (GitLab API). The repository is 3y11m old; the project predates it.
  gzkit's five-year ecosystem-trust signal (AGENTS.md § STDLIB-FIRST claim 4)
  is **not** cleanly met by the repository age alone — recorded here as a known
  weakness rather than argued away. That doctrine is scoped to runtime
  dependencies in `pyproject.toml`; this adoption adds no runtime dependency.

### Licence position

Verbatim from `https://gitlab.com/tgdp/templates/-/raw/main/LICENSE`, read
2026-08-19:

> # MIT No Attribution License
>
> Copyright (c) 2024 The Good Docs Project
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so.

MIT-0 removes even MIT's notice-retention clause. Vendoring the templates into
`.gzkit/templates/`, shipping them in the wheel, and scaffolding them into
adopters via `gz init` is therefore unencumbered.

**This is the opposite disposition from ASD-STE100**
(`docs/governance/research_sources/asd-ste100-issue-9.md`), which was onboarded
cite-only because its licence denies redistribution and gzkit ships publicly.
The two sources were read the same way and came out differently because their
licences differ — the reasoning is the same, the outcome is not.

Attribution is **not** required by MIT-0 and is proposed anyway: a
`resources_`-shaped citation naming TGDP. That is both the house practice and
TGDP's own.

## Decision

Adopt the five-deliverable model as gzkit documentation doctrine, and adopt the
document types gzkit currently has no template for. Four parts:

**1. The model is the doctrine.** A gzkit document type is defined by its
deliverable set, not by a single template file. The mapping table above binds:
a new document type declares which of the five deliverables it carries and
where each lives, reusing the gzkit surface that already plays that role rather
than creating a parallel tree.

**2. Adopt the gap-filling types only.** `tutorial`, `how-to`, `concept`,
`glossary`, `troubleshooting`, `installation-guide`, `readme`, and
`contributing-guide` — the types for which gzkit has no template today.

**3. Framework-wide mechanism, project-local commitment.** Following the
precedent ADR-0.34.0 § Decision (DATA FLOW) set for the foundation kind — *"the
mechanism ... ships framework-wide; the DECISION to close is project-local"* —
the templates and the model ship in the wheel and scaffold into adopters, while
**which types gzkit itself mandates** stays gzkit's own decision. gzkit's
existing manpage/runbook/docstring taxonomy is unchanged and no existing gzkit
document is rewritten; new types are adopted as gaps are filled.

**4. Four collisions are fenced out, not resolved here.**

| Excluded | Why |
|---|---|
| `style-guide`, `terminology-system` | `ADR-pool.controlled-language-for-control-surfaces` owns this territory and is parked post-1.0 pending its own operator ruling. Adopting these would pre-empt it. |
| `changelog`, `release-notes` | `.gzkit/rules/changelog-release-notes.md` and two existing templates already own them. |
| `reference` | `docs/user/manpages/<verb>.md` is mechanically enforced by `gz validate --cli-alignment`, including the no-`gz-`-prefix rule. Any mapping onto TGDP's reference template is a separate decision against a live validator. |
| `code-of-conduct` (×4), `our-team`, `user-personas`, `contact-support` | Community and project-governance documents rather than software documentation. `user-personas` additionally collides by name with `.gzkit/personas/`, which is agent behavioural framing and a different subject entirely — the shape AGENTS.md § Operator Doctrine forbids inferring across. |

## Alternatives Considered

1. **Adopt all 24 types wholesale.** REJECTED — requires resolving all four
   collisions at once, and would pre-empt a pool ADR the operator explicitly
   parked pending its own ruling.

2. **Adopt the model only; author gzkit-native templates in that shape.**
   REJECTED — re-authoring MIT-0 content that is already reviewed and community
   maintained is work without a product. The licence exists precisely to make
   this unnecessary.

3. **Take the `template_` files, skip the five-deliverable model.** REJECTED —
   the model is the part that matches gzkit's existing layering. Taking the
   skeletons without it yields a directory of orphan files with no doctrine
   saying who maintains them or where their rationale lives.

4. **Adopt for gzkit only; ship to adopters in a later ADR.** REJECTED —
   the operator's request named "gzkit and any adopting projects", and
   ADR-0.34.0 already provides the framework-wide/project-local pattern that
   makes shipping safe without forcing adoption.

5. **Map `docs/user/manpages/` onto TGDP's reference template.** REJECTED for
   this ADR — the manpage convention is enforced by a live validator, so the
   change is a validator-scope decision rather than a template adoption. Fenced
   above, available as follow-on work.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree is performed via `gz adr promote`.

**Promotion requires its own operator ruling** and would be `--kind feature`.
The `foundation` kind is sealed for gzkit by ADR-0.34.0 and is not available
here; it remains open for adopter projects, whose `gz init` scaffolds no
grandfather manifest (`foundation_kind_is_closed()` in
`src/gzkit/models/foundation_grandfather.py`).

Sequencing: authored 2026-08-19 under an operator ruling to capture the design
and the licence finding without competing for the release track. The active
campaign's topmost item is unchanged by this ADR.

Related:

- `docs/governance/documentation-taxonomy.md` — the coverage-and-gate model
  this ADR is orthogonal to and does not modify
- `ADR-pool.controlled-language-for-control-surfaces` — owns the style-guide
  and terminology territory fenced out above
- `ADR-0.34.0-foundation-sunset` — source of the framework-wide/project-local
  precedent adopted in Decision part 3
- `ADR-0.0.31` distribution invariant — binds any template vendored into the
  wheel, via `gz validate --distribution`
