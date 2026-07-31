# Minor Release: v0.34.0

**Date:** 2026-07-31
**Previous Version:** 0.33.3
**Tag:** v0.33.3
**Driving ADR:** ADR-0.34.0-foundation-sunset

> **This is a minor release from an ADR closeout, not a patch release.** The
> `PATCH-` filename prefix is dictated by the lookup path in
> `audit_version_release` (`docs/releases/PATCH-v{version}.md`), which is the
> only in-flight-evidence path the audit accepts. Precedent:
> `PATCH-v0.30.0.md` is likewise a minor release. The naming mismatch and the
> fact that `gz closeout` never writes this manifest (only `gz patch release`
> does) are tracked as a defect — see § In-flight window below.

## Driving Work

| Artifact | Status | Attestor | Date |
|---|---|---|---|
| ADR-0.34.0-foundation-sunset | Completed (attested) | g0 | 2026-07-31 |
| OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion | attested_completed | g0 | 2026-07-19 |
| OBPI-0.34.0-02-authoring-time-kind-rejection | attested_completed | g0 | 2026-07-20 |
| OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement | attested_completed | g0 | 2026-07-29 |
| OBPI-0.34.0-04-execute-migration-populate-and-resense | attested_completed | g0 | 2026-07-30 |
| OBPI-0.34.0-05-activate-standing-taxonomy-gate | attested_completed | g0 | 2026-07-31 |

## Residuals Carried (not closed by this release)

| # | Title | Disposition |
|---|-------|-------------|
| 734 | register_adr_in_ledger: third adr_created ingress bypasses the foundation membrane | Accepted as deferred at attestation; membrane sealed at two of three ingresses |
| 735 | parse_frontmatter_value: a leading BOM silently hides the whole frontmatter block | Residual ingress hardening, named in OBPI-05's attestation |
| 736 | frontmatter ingress: three ad-hoc decoders disagree; no shared tri-state reader | Residual ingress hardening, named in OBPI-05's attestation |

## Gate Evidence

All 5 GovZero gates satisfied via `gz closeout ADR-0.34.0-foundation-sunset`:
Gate 2 (TDD) PASS, Lint PASS, Typecheck PASS, Gate 3 (Docs) PASS,
Gate 4 (BDD) PASS, Gate 5 human attestation recorded by `g0`.

Bound fidelity gate: 2 assertions, 2 pass, 0 fail.

Receipts: `arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4`,
`arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1` (7685 tests, OK),
`arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c`,
`arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2`;
behave 66 features / 401 scenarios / 0 failed.

## In-flight window

This manifest exists to satisfy `audit_version_release` during the window
between the version-bump commit and `gh release create v0.34.0`, which creates
the `v0.34.0` tag. Per GHI #217 the manifest is equivalent evidence for that
window.

The window is unavoidable here because the closeout ceremony's Step 10
prescribes `gz git-sync --apply --lint --test` **before** `gh release create`,
while `audit_version_release` fails the test gate until the tag exists — an
ordering conflict with no in-ceremony resolution, since `gz closeout` performs
the version bump but never writes this manifest.

## Operator Approval

Approved by operator ruling during the ADR-0.34.0 closeout ceremony,
2026-07-31 (verbatim: "attest completed", and "A" selecting the in-flight
manifest path over tag-first).
