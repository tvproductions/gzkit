# Audit Plan: ADR-0.0.29-complexity-advisor

## Scope
- ADR: `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- Generated: 2026-05-09
- Trigger: standalone `gz-adr-audit` invocation (Layer-2 ledger consumption + Step-3 value demonstration)

## Claims Under Test

| # | ADR Claim | Verification |
|---|-----------|--------------|
| 1 | Trigger-time doctrinal frame replaces opaque numeric verdicts | Demo 2 (warn-band crossing emits archetype + authority + citation + recommendation) |
| 2 | Verdict-proof binding closes "advice without evidence" | Demo 4 (--json) + `gz validate --advisor-proof-binding` validator |
| 3 | Four-code CLI exit map (0/1/2/3) | Demos 1, 2, 3 (clean=0, warn=0, block=3) |
| 4 | Heavy-lane CLI surface wired (manpage + runbook + index) | `gz cli audit` 93/93 covered (Demo 6) |
| 5 | REQ coverage discipline (no cosmetic backfill) | `gz adr audit-check` zero-flag (post-remediation); `gz covers OBPI-0.0.29-03` 7/7 |
| 6 | Documentation/code alignment (Gate 3) | `mkdocs build --strict` clean (proof: docs.txt) |
| 7 | All 9 OBPIs attested_completed | `gz adr report ADR-0.0.29` (lifecycle: Validated; closeout phase: validated) |

## Verification Commands
- `uv run gz test`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run mkdocs build --strict`
- `uv run gz adr audit-check ADR-0.0.29`
- `uv run gz cli audit`
- `uv run gz validate --advisor-proof-binding`
- `uv run gz covers OBPI-0.0.29-03 --json`
- `uv run gz complexity advise <fixture>` (live demos 1-5)

## Risk Focus
- Cosmetic-backfill anti-pattern (`@covers` decorating tests that don't assert REQ semantics) — surfaced and remediated in this audit (3 decorators removed from `tests/test_ceremony_demo_discovery.py`).
- Walkthrough demo discovery (GHI #427) — closed by commit dff7496 prior to this audit; demos exercise actual diagnosis runs, not `--help`.

## Proof Output
- Directory: `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/audit/proofs`
