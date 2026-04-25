---
id: ADR-pool.multimodal-evidence-binding
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.multimodal-evidence-binding: Multimodal Evidence Binding

## Status

Pool

## Intent

Extend the captured-stdout receipt-binding model (ADR-0.46.0) to non-text
artifact bytes — screenshots, rendered diagrams, video walk-throughs,
PDF outputs, image diffs. The hash-binding shape is identical (artifact
bytes → SHA-256 → receipt field); the storage tier and the proof-of-
freshness check differ.

The gap this addresses: a heavy-lane attestation that ships UI changes,
mkdocs-rendered diagram updates, or any visual deliverable has no
mechanical floor for "this is what I actually produced, not what I want
the reviewer to think I produced." The Anthropic Prompt Engineering 101
talk's multimodal example (form image + sketch image fed to Claude)
demonstrates that the agent surface is multimodal-ready; gzkit's
evidence surface is not.

## Decision

Promotion criteria — defer authoring until at least one of:

1. A consuming gzkit project lands a heavy-lane attestation whose primary
   deliverable is non-text (UI surface, image-rendering library, video
   tutorial corpus). The current consuming projects are text-only.
2. The captured-stdout binding (ADR-0.46.0) has shipped and accumulated
   a corpus of bindings sufficient to surface the natural extension
   points (e.g., manpage EXAMPLES that include rendered ANSI escape
   sequences, mkdocs strict builds with embedded diagrams).
3. The Anthropic API or vendor surface evolves to make multimodal
   evidence cheaper to capture and verify than today.

When promoted, the design will mirror ADR-0.46.0's schema:
`captured_artifact_path`, `captured_artifact_hash`, `captured_artifact_mime`
on the receipt model, with `gz arb step --capture-artifact <path>` as
the opt-in capture surface.

## Alternatives Considered

1. **Author now, defer implementation** — rejected. Pool ADRs are
   backlog items; authoring an active ADR with no implementation slot
   bloats the active tree without value.
2. **Fold into ADR-0.46.0** — rejected. ADR-0.46.0 is text-tier and
   the schema mechanism (stdout capture wrapping) doesn't trivially
   extend to arbitrary artifact bytes. A cleaner separation makes the
   text-tier work shippable without solving the multimodal storage
   question.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
