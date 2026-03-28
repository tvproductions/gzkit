# gz closeout(1) -- ADR closeout pipeline with Defense Brief

## SYNOPSIS

```
gz closeout <ADR-ID> [--json] [--dry-run]
```

## DESCRIPTION

Initiate the end-to-end closeout pipeline for an ADR. Validates OBPI
completion, product proof, and quality gates, then prompts for human
attestation. On success, bumps the project version and records the
attestation in the ledger.

The closeout ceremony presents a **Defense Brief** — a structured evidence
presentation where the completing agent makes its case for closure. The
Defense Brief includes:

- **Closing Arguments** — per-OBPI text authored from delivered evidence
- **Product Proof** — per-OBPI documentation proof status table
- **Reviewer Assessment** — independent reviewer verdicts from REVIEW-*.md

The ceremony is blocked when any OBPI is missing its closing argument or
product proof. For Heavy-lane ADRs, the reviewer assessment is also required.

## OPTIONS

`--json`
:   Emit machine-readable closeout payload to stdout.

`--dry-run`
:   Show the full closeout plan (including Defense Brief preview) without
    writing any ledger events or changing ADR status.

## CEREMONY FLOW

1. **OBPI Completion** — all linked OBPIs must be Completed
2. **Product Proof Gate** — each OBPI has runbook/command-doc/docstring proof
3. **Defense Brief** — closing arguments + proof table + reviewer assessment
4. **Quality Gates** — lint, typecheck, test (+ docs, BDD for Heavy)
5. **Human Attestation** — Completed / Partial / Dropped
6. **Version Bump** — pyproject.toml, __init__.py, README badge
7. **ADR-CLOSEOUT-FORM.md** — written with Defense Brief and attestation

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success (or dry-run preview) |
| 1 | Blocked: missing OBPI completion, product proof, or gate failure |

## EXAMPLES

Preview closeout with Defense Brief:

```bash
uv run gz closeout ADR-0.23.0 --dry-run
```

Run full closeout pipeline:

```bash
uv run gz closeout ADR-0.23.0
```

## SEE ALSO

`gz attest`(1), `gz gates`(1), `gz adr status`(1)
