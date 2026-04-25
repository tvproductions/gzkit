# ADR Closeout Form: ADR-0.0.28-complexity-threshold-doctrine

**Status**: Phase 0 — Proposed (closeout pending OBPI completion)

---

## Pre-Attestation Checklist

Closeout evidence to be verified after OBPI completion:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes (mkdocs --strict)
- [ ] Gate 4 (BDD): Behave suite passes (scenarios tagged `@REQ-0.0.28-NN-MM`)
- [ ] Code reviewed
- [ ] Foundation-kind closeout walkthrough per ADR-0.0.18 (heavy lane + foundation kind)
- [ ] `.gzkit/rules/complexity-thresholds.md` lands with body-level rule-version marker and visible block quote in agreement
- [ ] `ThresholdTable` Pydantic model is `frozen=True, extra="forbid"`; loader round-trips against rule body
- [ ] `gz validate --complexity-thresholds` integrates into `gz validate --all` and `gz check`
- [ ] Citation tuple `(distilled_characteristics_path, section_anchor, corpus_revision)` parses against OBPI-0.0.27-05's `parse_citation`
- [ ] Every metric in the rule body has a `block` band (mandatory) and at least one of `warn` / `advise`
- [ ] Manpage `docs/user/manpages/gz-validate.md` documents the new flag with at least one example invocation
- [ ] Runbook `docs/user/runbook.md` has an entry under "Complexity doctrine surfaces"

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/ADR-0.0.28-complexity-threshold-doctrine.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | Behave suite passes | `uv run behave features/complexity_thresholds.feature` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Validator (new) | Threshold validator exits 0 | `uv run gz validate --complexity-thresholds` |
| Validator (cluster) | Link integrity holds | `uv run gz validate --complexity-doctrine-links` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.28-complexity-threshold-doctrine` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.28-01-threshold-rule-file](obpis/OBPI-0.0.28-01-threshold-rule-file.md) | Threshold table rule file (`.gzkit/rules/complexity-thresholds.md`) — per-metric (advise/warn/block) bands, trigger-semantic vocabulary, percentile + absolute pairing | Pending |
| [OBPI-0.0.28-02-threshold-loader](obpis/OBPI-0.0.28-02-threshold-loader.md) | `ThresholdTable` Pydantic loader (`src/gzkit/complexity/thresholds.py`) — frozen models, rule-body parser, band-lookup methods | Pending |
| [OBPI-0.0.28-03-threshold-validator](obpis/OBPI-0.0.28-03-threshold-validator.md) | `gz validate --complexity-thresholds` — fail-closes on unmapped bands, missing block band, missing percentile + absolute pairing, unparseable citation | Pending |

## Parallelism

`OBPI-01 → OBPI-02 → OBPI-03`

OBPI-01 produces the rule body; OBPI-02 parses it into the model surface; OBPI-03 validates the rule body against the model contract. Strictly sequential — OBPI-02's loader cannot land before the rule it parses; OBPI-03's validator cannot land before the model it asserts against.

## Cluster Citations

ADR-0.0.28 cites:
- ADR-0.0.27 OBPI-04 (distilled-characteristics document) — empirical basis for every threshold absolute number
- ADR-0.0.27 OBPI-05 (citation contract) — required citation tuple form for every cited boundary
- ADR-0.0.18 (taxonomy doctrine) — foundation-kind brief-level Gate 5 attestation rigor

ADR-0.0.28 is cited by:
- ADR-0.0.29 (advisor — forthcoming) — consumes `ThresholdTable` for `warn` / `advise` band-driven recommendations
- ADR-0.0.30 (authoring guidance — forthcoming) — consumes `ThresholdTable` for `advise` band-driven hints
- `complexity-reduction-xenon` chore — consumes `ThresholdTable` for xenon-as-gate `block` band invocation

## Defense Brief

*To be authored at closeout — populated by `gz closeout` ceremony from OBPI Closing Arguments.*

## Human Attestation

*Pending OBPI completion. Foundation-kind + heavy-lane stacks attestation rigor — TTY + ATTEST gate required at brief level for every OBPI per AGENTS.md § Lane & Kind Attestation Matrix.*
