# Security Sensitivity — Rationale

*Lifted from `.gzkit/rules/security-sensitivity.md` under GHI #327 diet pass.
The binding rule remains canonical in `.gzkit/rules/security-sensitivity.md`;
this page holds extended walkthrough details and failure-mode rationale.*

## Rationale

The rationale is doctrine-drift cost. Security-relevant work concentrates
the failure surfaces an audit must catch: agent-synthesized payload
fabrication (GHI #290), credential / PII / authentication regressions, and
the trust-poisoning class the layered-trust doctrine names (T1/T2/T3
poisoning at every layer boundary). These failures rarely surface in
verification commands; they surface in operator review of the change.
The third axis exists because the cost of *missing* heightened review on a
security change is structurally larger than the cost of a redundant
walkthrough on a non-security one.

## Registry categories

The registry's nine initial categories cover credential / secret stores,
authentication and session boundaries, signing and verification surfaces,
sandbox escape paths, RBAC enforcement, audit-log emission, the ledger
authorship surface, the attestation receipt surface, and the chore /
hook execution surface. New categories are additive only; categories may
not be removed without a brief declaring `sensitivity: security`.

## Heightened walkthrough enumeration

`gz obpi complete`, when emitting attestation for a brief carrying
`sensitivity: security`, fires an extended Gate 5 walkthrough (OBPI-0.0.22-05):

1. **Surface enumeration** — every security surface this brief touched
   (from the registry) is named explicitly; the operator confirms each.
2. **Receipt confirmation** — the canonical security-scan ARB step
   (`arb-step-security-scan-*`, reserved in `CANONICAL_STEP_COMMANDS`)
   is required as a cited receipt ID.
3. **Classification confirmation** — the operator confirms the
   sensitivity declaration matches reality.
4. **Co-presence proxy** — agent-relayed attestation (`--attestor-present`)
   permitted only with registered pipeline marker; otherwise PTY-fed
   `ATTEST` required.

## Scanner-unavailable failure mode

The security-scan ARB step is the single mechanical witness. **When the
canonical scanner is unavailable** — missing binary, network-isolated
environment, registry-unhealthy — `gz obpi complete` fail-closes rather
than degrading: no receipt, no walkthrough completion, no attestation.

This is intentional. Security doctrine that degrades gracefully under
tool absence is doctrine that an attacker can suppress by removing the
tool. The validator, the registry, and the receipt are each independent
witnesses, and no two may substitute for the third.

## Related

- ADR-0.0.22 — `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/`
- AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix
- `docs/governance/arb-middleware.md` — ARB middleware contract
- `docs/governance/trust-doctrine.md` — T1/T2/T3 invariants

## Origin

GHI #327 — instructions-files-diet pass (2026-05-07).
