# Commands

All command surfaces use `gz [subcommand] [*] [*]`.

Command reference pages are operator manpages and part of Gate 3 proof.

---

## Governance

| Command | Description |
|---------|-------------|
| [`gz init`](init.md) | Initialize gzkit in a repository |
| [`gz prd`](prd.md) | Create a Product Requirements Document |
| [`gz constitute`](constitute.md) | Create a constitution artifact |
| [`gz specify`](specify.md) | Create an implementation brief (including OBPIs) |
| [`gz plan`](plan.md) | Create an ADR |
| [`gz implement`](implement.md) | Run Gate 2 and record results |
| [`gz gates`](gates.md) | Run lane-required gates |
| [`gz status`](status.md) | Show multi-ADR OBPI progress and lifecycle status |
| [`gz state`](state.md) | Show artifact graph and readiness filters |
| [`gz adr status`](adr-status.md) | Show focused OBPI progress for one ADR |
| [`gz adr promote`](adr-promote.md) | Promote a pool ADR into canonical ADR package structure |
| [`gz adr audit-check`](adr-audit-check.md) | Verify OBPI completeness/evidence for one ADR |
| [`gz closeout`](closeout.md) | Present closeout paths/commands and record closeout initiation |
| [`gz attest`](attest.md) | Record human attestation with prerequisite enforcement |
| [`gz audit`](audit.md) | Run strict post-attestation audit reconciliation |
| [`gz adr emit-receipt`](adr-emit-receipt.md) | Emit completed/validated receipt with optional evidence scope |
| [`gz obpi emit-receipt`](obpi-emit-receipt.md) | Emit completed/validated receipt for one OBPI |
| [`gz git-sync`](git-sync.md) | Run guarded sync ritual |
| [`gz migrate-semver`](migrate-semver.md) | Record SemVer ID rename events |
| [`gz register-adrs`](register-adrs.md) | Register existing ADR files into ledger |

---

## Validation And Maintenance

| Command | Description |
|---------|-------------|
| `gz check` | Run quality checks |
| `gz lint` | Run lint checks |
| `gz format` | Auto-format code |
| `gz test` | Run unit tests |
| `gz typecheck` | Run type checks |
| `gz validate` | Validate governance artifacts |
| [`gz skill audit`](skill-audit.md) | Audit skill lifecycle metadata and mirror parity |
| [`gz check-config-paths`](check-config-paths.md) | Validate configured + manifest path coherence |
| [`gz cli audit`](cli-audit.md) | Validate CLI docs/manpage coverage |
| [`gz agent sync control-surfaces`](agent-sync-control-surfaces.md) | Regenerate control surfaces |
| `gz tidy` | Run maintenance checks and cleanup |

---

## Operator Sequences

Primary daily loop (OBPI-first):

1. Orientation and ADR context (`gz status`, `gz adr status`)
2. One OBPI increment implementation and verification (`gz implement`, optional Gate 3 docs check)
3. OBPI evidence update in brief + OBPI receipt (`gz obpi emit-receipt`)

ADR closeout loop (after OBPI batch completion):

1. ADR/OBPI reconciliation (`gz adr audit-check`)
2. Closeout presentation (`gz closeout`)
3. Human attestation (`gz attest`)
4. Post-attestation audit (`gz audit`)
5. ADR-level receipt/accounting (`gz adr emit-receipt`)

---

## Global Options

All commands support:

- `--help`
- `--version`
