# Universal OBPI Attestation — Doctrine, Axes, and Expansion

*Lifted from `AGENTS.md` § OBPI Acceptance Protocol §§ Universal OBPI
Attestation (ADR-0.0.36, GHI #342) under OBPI-0.0.54-02. The binding
paragraphs of the OBPI Acceptance Protocol remain canonical in
`AGENTS.md`; this file preserves the verbatim axis enumeration and
expansion that previously appeared inline, per the map-not-encyclopedia
doctrine (ADR-0.0.54).*

## Anchor in AGENTS.md

The OBPI Acceptance Protocol in `AGENTS.md` carries three binding
paragraphs that remain inline:

- Brief-level human attestation enforcement (ADR-0.0.36, GHI #342)
- REQ-coverage gate (ADR-0.0.25)
- Pipeline mandate (`gz obpi pipeline <OBPI-ID>` runtime ownership)

The Universal OBPI Attestation subsection that expanded the
brief-level-attestation paragraph with its three-axis decomposition is
lifted here.

## Universal OBPI Attestation (ADR-0.0.36, GHI #342)

**Brief-level human attestation is ALWAYS required for every OBPI completion, regardless
of parent ADR kind or lane. There is NO self-close path.**

`kind`, `lane`, and `sensitivity` remain three orthogonal axes that determine *which gates
fire* — they NEVER determine whether Gate 5 brief-level attestation fires. Gate 5 is universal:

- **`foundation` kind** — determines whether Gate 3 (docs scope) and Gate 4 (BDD scope)
  apply the foundation-tier bar.
- **`heavy` lane** — determines whether Gate 3 (docs) and Gate 4 (BDD) are required.
- **`security` sensitivity** — adds security-scan requirements to Gate 5.

Third-axis doctrine: [`.gzkit/rules/security-sensitivity.md`](../../.gzkit/rules/security-sensitivity.md).

## Related

- `AGENTS.md` § OBPI Acceptance Protocol — the binding paragraphs
- `ADR-0.0.36-universal-obpi-attestation` — origin doctrine
- `.gzkit/rules/security-sensitivity.md` — third-axis doctrine
- `ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine` — parent ADR for this lift
