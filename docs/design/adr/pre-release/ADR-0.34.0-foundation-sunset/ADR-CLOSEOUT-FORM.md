# ADR Closeout Form: ADR-0.34.0-foundation-sunset

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.34.0-foundation-sunset` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion](OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion.md) | Grandfather Manifest And Closed Kind Assertion | Completed |
| [OBPI-0.34.0-02-authoring-time-kind-rejection](OBPI-0.34.0-02-authoring-time-kind-rejection.md) | Authoring Time Kind Rejection | Completed |
| [OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement](OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement.md) | REQ-0.34.0-03-01 is deliberately ABSENT — its labor genuinely subdivided across | Completed |
| [OBPI-0.34.0-04-execute-migration-populate-and-resense](OBPI-0.34.0-04-execute-migration-populate-and-resense.md) | the body-preservation round-trip is | Completed |
| [OBPI-0.34.0-05-activate-standing-taxonomy-gate](OBPI-0.34.0-05-activate-standing-taxonomy-gate.md) | Activate Standing Taxonomy Gate | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion | docstring | FOUND |
| OBPI-0.34.0-02-authoring-time-kind-rejection | command_doc | FOUND |
| OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement | docstring | FOUND |
| OBPI-0.34.0-04-execute-migration-populate-and-resense | docstring | FOUND |
| OBPI-0.34.0-05-activate-standing-taxonomy-gate | docstring | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `attest completed — ADR-0.34.0 Foundation Sunset seals the foundation kind. gz validate --taxonomy exits 0 on the terminal post-migration tree (was exit 3 / 74 findings at OBPI-01, earned green by OBPI-04's migration, never held green by a staging flag), and the bound fidelity gate passes 2/2 (gz adr fidelity ADR-0.34.0: closed-kind refusal expected 1 observed 1; no-limbo partition expected 0 observed 0). All 5 OBPIs attested_completed by g0, 2026-07-19 through 2026-07-31. All four authoring/registration doors were demonstrated refusing in-ceremony with zero writes: gz plan create --kind foundation, gz adr promote --kind foundation, and gz interview adr with a 0.0.x-embedding id each exit 1 with three-part guardrail prose, and the registration membrane's 9 negative controls refuse an un-grandfathered package while still booking the grandfathered roster; newest adr_created in the ledger remains 2026-07-26. gz ontology resense corroborates the migration from a read-only instrument at 23 removed / 23 added nodes, one-to-one foundation-to-pool. Receipts: arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4, arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1 (7685 tests OK), arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c, arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2; behave 66 features / 401 scenarios / 0 failed. Residual frontmatter-ingress hardening accepted as deferred at GHI #734 (third adr_created ingress), #735, #736.`

**Attested by**: g0
**Timestamp (UTC)**: 2026-07-31T11:47:13Z
