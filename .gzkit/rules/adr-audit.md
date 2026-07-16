---
id: adr-audit
paths:
  - "docs/design/adr/**"
description: ADR audit verification procedures
---

# ADR Audit (gzkit)

<!-- rule-version: 0.2.0 -->

> **Rule version:** `0.2.0` — reconciled to ADR-0.0.24 and ADR-0.0.59 (Pass A
> conflict-matrix rows 18 and 19, run 2026-07-16); adds the body-level version
> marker this file never carried, which is how both drifts survived unnoticed.
> § Audit sequence step 2 prescribed bare commands that emit no ARB receipt,
> making step 4 fail closed at exit 3 on every foundation ADR this rule
> governs. § Rules offered only two diagnosis branches, the first of which
> (`author a @covers test`) is the anti-pattern `tests.md` § REQ Scope
> Discipline names for SUPPORT and STRUCTURAL-FENCE REQs. Prior: unversioned
> since authoring.

Purpose: verify ADR completion claims using reproducible evidence.

## Audit sequence

1. Verify linked OBPI evidence:

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

2. Run quality checks via the **ARB-wrapped canonical invocations**. Bare commands emit no receipt; step 4 then fail-closes at exit 3 on Heavy lane and `foundation` kind (`_zero_receipt_result(fail_closed=True)`). Locked by `CANONICAL_STEP_COMMANDS`; see `AGENTS.md` § Attestation.

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

3. Run closeout/audit lifecycle in order:

```bash
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz attest ADR-<X.Y.Z> --status completed
uv run gz audit ADR-<X.Y.Z>
```

4. Emit audit receipt. The `--evidence-json` payload MUST carry the `arb-*` receipt IDs emitted by step 2 — a payload with zero receipt citations fail-closes at exit 3 before the attestation is recorded:

```bash
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" \
  --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD","receipts":["arb-ruff-<id>","arb-step-typecheck-<id>","arb-step-unittest-<id>","arb-step-mkdocs-<id>"]}'
```

## Rules

- Do not run `gz audit` before attestation.
- If audit-check fails, **first read the flagged REQ's kind tag** (`[behavior]` / `[support]` / `[structural-fence]`), then diagnose:
  - **(a) BEHAVIOR REQ, genuinely uncovered** — author a REQ-derived test and decorate with `@covers(REQ-X.Y.Z-NN-MM)`. `@covers` is BEHAVIOR's only proof channel.
  - **(b) BEHAVIOR REQ, covered by a test whose assertion drifted from REQ semantics** — re-derive the assertion per `.gzkit/rules/tests.md` § "Tests assert semantics, not strings" (Invariant 6f).
  - **(c) SUPPORT or STRUCTURAL-FENCE REQ** — **do NOT author a `@covers` test.** Each kind has exactly one proof channel (SUPPORT → ledger event + structural validator; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` entry). Supply that channel instead. Authoring a `@covers` test here is the anti-pattern `tests.md` § REQ Scope Discipline names — the resulting filesystem-grep assertion cannot fail when production behavior changes. See ADR-0.0.59 and `gz validate --req-kind-discipline`.
- Never backfill a cosmetic `@covers` decorator to silence audit-check without re-deriving the assertion.
- Keep `docs/user/runbook.md` and `docs/governance/governance_runbook.md` aligned with runtime behavior.

## Legitimate-authoring exemptions (covers-backfill heuristic)

The same-commit-window backfill heuristic exempts five structurally distinct shapes from the cosmetic-backfill anti-pattern. Each exemption preserves the GHI #272/#309 protection against decorators silencing audit-check without re-derived semantics; if the receipt is anchored to the same commit as the decorator AND the file/block was created in the same commit, the exemption is suppressed (the GHI #309 triple still flags).

| Shape | Source | Source-side annotation | Receipt-coupled flag? |
|-------|--------|------------------------|------------------------|
| Same-commit FILE creation | GHI #382 | none — file went 0→N lines in intro commit | suppressed (still flags) |
| Same-commit BLOCK creation | GHI #466 Component B | none — function `def` line shares decorator's intro SHA | suppressed (still flags) |
| Inline regression-invariant overlay marker | GHI #466 Component A | `# audit-exempt: regression-invariant-overlay <reason>` on decorator line; reason text required | NOT suppressed (operator attestation by design) |
| `Ceremony:` trailer | GHI #386 | trailer in `_EXEMPT_CEREMONIES` (e.g. `Ceremony: gz-git-sync`) | n/a (trailer governs) |
| Subject-suffix marker | GHI #390 | parenthesized suffix at end of subject (e.g. `(gz git-sync)`) | n/a (subject governs) |

**When to use the inline marker (Component A):** A new `@covers(REQ-X)` decorator is being added to an existing test whose assertion structurally IS the REQ being claimed — typical case is a regression-invariant REQ pointing at a test that already enforces the prior invariant (e.g. byte-parity tests covering a "no regression of OBPI-N" REQ). The marker is the operator's explicit attestation that the overlay is legitimate, not cosmetic backfill. Reason text is mechanically required so the exemption can't be a one-token escape hatch — keep it terse but informative (typical form: pointer to the OBPI/REQ relationship). Do NOT use the marker when the right move is to author a new REQ-derived assertion; the marker is reserved for the genuine overlay shape.
