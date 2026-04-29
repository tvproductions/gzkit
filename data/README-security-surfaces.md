# Security Surface Registry — Governance Contract

`data/security_surfaces.json` is the canonical registry of file globs that
classify code as security-sensitive under [ADR-0.0.22 (Security Sensitivity
Doctrine)](../docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md).
The registry is consumed by `gz validate --sensitivity` (OBPI-0.0.22-03) which
intersects each brief's `## ALLOWED PATHS` against the registry; any
intersection forces `sensitivity: security` on the brief regardless of
frontmatter, and that classification stacks Gate 5 attestation rigor at the
brief level.

## Self-bootstrapping governance contract

> Edits to `data/security_surfaces.json` require a brief carrying
> `sensitivity: security`.

This is the "who classifies the classifier" closure: the same rigor the
registry imposes on code that touches security surfaces also governs edits to
the registry itself. Adding, removing, or modifying a glob is a security-policy
change and is authored under a `sensitivity: security` brief — declared in
frontmatter, since the registry's own paths are not auto-detectable as
security-sensitive without circularity.

## One-time bootstrap exception

The very first registry commit (this OBPI, `OBPI-0.0.22-02-security-surface-registry`)
cannot itself carry `sensitivity: security` because the registry does not exist
before this commit lands. The bootstrap exception is recorded by:

1. The parent ADR brief `ADR-0.0.22-security-sensitivity-doctrine` declaring
   `sensitivity: security` in frontmatter (see the canonical rule file authored
   in OBPI-0.0.22-06 for the formal waiver entry).
2. This README documenting the bootstrap as a one-time event closed by the
   ADR's own attestation.

After this commit, every future edit to either `data/security_surfaces.json`
or this README is governed by the contract above without exception.

## Categories

The nine canonical categories are pinned in the parent ADR's `## Decision`
section:

- `credential_handling`
- `subprocess_user_input`
- `crypto_primitives`
- `auth_boundaries`
- `external_api_surfaces`
- `ledger_integrity`
- `arb_receipt_chain`
- `secret_handling`
- `deserialization_user_input`

Adding a new category is a foundation-doctrine change and requires a follow-up
foundation ADR — not a registry-edit brief — per the YAGNI scope boundary in
ADR-0.0.22.

## Schema

Validated against `src/gzkit/schemas/security_surfaces.json`. Each entry
declares `category` (enum), `globs` (non-empty array of strings), and
`rationale` (non-empty string); `additionalProperties: false`. The Pydantic
model `gzkit.models.security_surfaces.SecuritySurfaceEntry` is the runtime
loader and exposes the `match_globs(allowed_paths, registry)` helper consumed
by `validate_sensitivity_binding` (OBPI-0.0.22-03).
