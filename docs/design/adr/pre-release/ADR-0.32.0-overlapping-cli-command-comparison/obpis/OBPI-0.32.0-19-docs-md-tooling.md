---
id: OBPI-0.32.0-19-docs-md-tooling
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 19
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-19: docs-md-tooling

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-19 -- "Compare docs/docs-lint/md-lint/md-fix/md-tidy -- opsdev docs_tools.py+md_docs.py vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's documentation tooling commands (`docs`, `docs-lint`, `md-lint`, `md-fix`, `md-tidy`) from docs_tools.py and md_docs.py against gzkit's equivalents in cli.py. This is a multi-command bundle covering documentation building, markdown linting, fixing, and tidying. Determine whether opsdev's implementations across two modules provide capabilities gzkit lacks.

## SOURCE MATERIAL

- **opsdev:** `docs_tools.py` + `md_docs.py` -- documentation and markdown tooling
- **gzkit equivalent:** `cli.py` (docs/md subcommand sections)

## ASSUMPTIONS

- Documentation tooling is critical for Gate 3 (Docs) compliance
- opsdev splits across two modules; gzkit consolidates in cli.py
- Markdown linting/fixing may have different rule sets or configurations

## NON-GOALS

- Changing markdown linting rules
- Adding new documentation build targets

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely for all five subcommands
1. Document comparison per subcommand: docs, docs-lint, md-lint, md-fix, md-tidy
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementations are sufficient

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed improvements
- `tests/` -- tests for absorbed improvements
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
