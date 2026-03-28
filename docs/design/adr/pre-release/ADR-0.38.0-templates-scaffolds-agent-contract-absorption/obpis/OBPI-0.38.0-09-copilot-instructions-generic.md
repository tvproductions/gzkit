---
id: OBPI-0.38.0-09-copilot-instructions-generic
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 9
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-09: Copilot-Instructions.md Generic Sections Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-09 — "Compare copilot-instructions.md generic sections — non-domain-specific guidance and rules"`

## OBJECTIVE

Compare the generic (non-domain-specific) sections of copilot-instructions.md between airlineops and gzkit. Evaluate coding conventions, toolchain instructions, governance workflow references, file handling rules, error handling patterns, and cross-platform guidance. Determine which file provides better generic agent guidance and absorb the best elements into gzkit's canonical version.

## SOURCE MATERIAL

- **airlineops:** `.github/copilot-instructions.md` — generic sections
- **gzkit equivalent:** `.github/copilot-instructions.md` — generic sections

## ASSUMPTIONS

- copilot-instructions.md provides vendor-specific agent guidance complementary to AGENTS.md
- Generic sections (coding conventions, toolchain, file handling) should be consistent across repos
- Domain-specific sections are out of scope — only generic guidance is compared
- These instructions are consumed by GitHub Copilot agents and affect code generation quality

## NON-GOALS

- Comparing domain-specific sections of copilot-instructions.md
- Changing the relationship between copilot-instructions.md and AGENTS.md
- Modifying GitHub Copilot configuration beyond instruction content

## REQUIREMENTS (FAIL-CLOSED)

1. Read both copilot-instructions.md files completely
1. Identify and extract generic sections (non-domain-specific guidance)
1. Compare section-by-section: coding conventions, toolchain instructions, governance workflow references, file handling, error handling, cross-platform guidance
1. Document which guidance exists in one file but not the other
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `.gzkit/templates/` — template storage
- `.github/copilot-instructions.md` — for comparison reference only
- `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
