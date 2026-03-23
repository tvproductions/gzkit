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
| [`gz adr report`](adr-report.md) | Deterministic tabular report (summary or single ADR) |
| [`gz adr promote`](adr-promote.md) | Promote a pool ADR into canonical ADR package structure |
| [`gz adr evaluate`](adr-evaluate.md) | Evaluate ADR/OBPI quality (deterministic scoring with verdict) |
| [`gz adr audit-check`](adr-audit-check.md) | Verify OBPI completeness/evidence for one ADR |
| [`gz adr covers-check`](adr-covers-check.md) | Verify ADR/OBPI @covers traceability in tests |
| [`gz closeout`](closeout.md) | Present closeout paths/commands and record closeout initiation |
| [`gz attest`](attest.md) | Record human attestation with prerequisite enforcement |
| [`gz audit`](audit.md) | Run strict post-attestation audit reconciliation |
| [`gz adr emit-receipt`](adr-emit-receipt.md) | Emit completed/validated receipt with optional evidence scope |
| [`gz obpi status`](obpi-status.md) | Show focused runtime status for one OBPI |
| [`gz obpi pipeline`](obpi-pipeline.md) | Launch the OBPI pipeline runtime surface |
| [`gz obpi validate`](obpi-validate.md) | Validate OBPI brief(s) for scaffold detection and completion readiness |
| [`gz obpi reconcile`](obpi-reconcile.md) | Fail-closed reconciliation for one OBPI |
| [`gz obpi emit-receipt`](obpi-emit-receipt.md) | Emit completed/validated receipt for one OBPI |
| [`gz git-sync`](git-sync.md) | Run guarded sync ritual |
| [`gz chores list`](chores-list.md) | List declared chores from the config registry |
| [`gz chores plan`](chores-plan.md) | Show deterministic plan details for one chore |
| [`gz chores run`](chores-run.md) | Execute one chore and append a dated log |
| [`gz chores audit`](chores-audit.md) | Audit chore log presence for one/all chores |
| [`gz migrate-semver`](migrate-semver.md) | Record SemVer ID rename events |
| [`gz register-adrs`](register-adrs.md) | Register existing ADR packages and linked OBPIs into ledger |
| [`gz roles`](roles.md) | List pipeline agent roles and handoff contracts |

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
| [`gz parity check`](parity-check.md) | Run deterministic parity regression checks |
| [`gz readiness audit`](readiness-audit.md) | Audit agent-readiness maturity across core disciplines |
| [`gz readiness evaluate`](readiness-evaluate.md) | Run instruction architecture eval suite with positive/negative controls |
| [`gz check-config-paths`](check-config-paths.md) | Validate configured + manifest path coherence |
| [`gz cli audit`](cli-audit.md) | Validate CLI docs/manpage coverage |
| [`gz agent sync control-surfaces`](agent-sync-control-surfaces.md) | Regenerate control surfaces |
| `gz tidy` | Run maintenance checks and cleanup |

---

## Operator Sequences

Primary daily loop (OBPI-first, pipeline-governed):

1. Orientation and ADR/OBPI context (`gz status`, `gz adr status`, `gz obpi status`)
2. Plan the OBPI, then execute it through `uv run gz obpi pipeline` (wrapper skill `/gz-obpi-pipeline` remains available and defers to the same shared runtime)
3. Present the Heavy-lane acceptance ceremony when required
4. Run guarded sync (`gz git-sync --apply --lint --test`)
5. Emit final OBPI completion accounting from the synced state (`gz obpi emit-receipt`)
6. Reconcile/update brief and ADR state (`gz obpi reconcile`, `gz adr status`)

ADR closeout loop (after OBPI batch completion):

1. ADR/OBPI reconciliation (`gz adr audit-check`)
2. Spec-test traceability reconciliation (`gz adr covers-check`)
3. Closeout presentation (`gz closeout`)
4. Human attestation (`gz attest`)
5. Post-attestation audit (`gz audit`)
6. ADR-level receipt/accounting (`gz adr emit-receipt`)

---

## Global Options

All commands support:

- `--help`
- `--version`
