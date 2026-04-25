---
id: ADR-pool.cross-vendor-confirmation-policy
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.cross-vendor-confirmation-policy: Cross Vendor Confirmation Policy

## Status

Pool

## Intent

Explore exposing gzkit's `lane × kind × Gate-5` confirmation matrix as a
structured artifact that both Claude Code and Codex agents can consume
identically. The GPT-5.5 system card (§ 3.4) documents a developer-
configurable confirmation policy for high-risk computer-use actions,
delivered via the system message. gzkit's analogue is the foundation/heavy-
lane attestation requirement enforced at runtime by
`_requires_human_obpi_attestation` and `_enforce_human_attestation_authenticity`
in `src/gzkit/commands/adr_audit.py`.

The two surfaces are conceptually identical (gate high-risk action on a
layer the model can't unilaterally override), but gzkit's policy is
expressed in Python invariants and AGENTS.md prose rather than a
machine-readable artifact agents from different vendors can read uniformly.
A shared confirmation-policy artifact under `.gzkit/` (mirrored via the
existing vendor-mirror infrastructure) would let Codex and Claude Code
honor the same gates without each vendor re-implementing the lane × kind
matrix.

## Decision

1. Defer authoring until at least one of:
   - Codex exposes a confirmation-policy intake surface analogous to
     OpenAI's developer-message policy.
   - A second vendor (Copilot, Gemini CLI) lands attestation-aware tooling
     that would consume such a policy.
2. When promoted, the artifact will live at `.gzkit/confirmation-policy.json`
   (or .yaml, TBD by vendor consumption shape) and mirror to
   `.claude/`, `.agents/`, `.github/` per the existing skill-surface-sync
   protocol.
3. Schema captures the same invariants `_requires_human_obpi_attestation`
   encodes today: `kind=foundation` ⇒ require human + TTY confirm;
   `lane=heavy` ⇒ require human + TTY confirm; otherwise self-closeable.

## Alternatives Considered

1. **Author now** — rejected. Speculative until at least one second-vendor
   consumer exists. The gzkit invariant is already enforced at runtime; a
   policy artifact without a second consumer is documentation duplication.
2. **Author as a vendor-neutral spec without an artifact** — rejected.
   Without a machine-readable surface other vendors can read, the spec
   becomes a doctrine note without enforcement value beyond AGENTS.md.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
