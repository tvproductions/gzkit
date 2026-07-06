# Plan — OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants

**OBPI:** OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants
**Parent ADR:** ADR-0.32.0-gzkit-ontology
**Lane:** Lite (parent ADR Heavy — Gate 5 attestation fires at completion)

## Context

This OBPI is the corpus-first MVP spine's doctrine surface (ADR-0.32.0 checklist
item #4). It authors ONE governance doctrine document —
`docs/governance/ontology-ownership-plane-doctrine.md` — that writes down:

1. The ontology's two-axis type separation: ownership (`harness|product`) ×
   plane (`product|process`).
2. The Harness-Purity Invariant (`ownership:harness` admits only GovZero-universal
   object types; gzkit's own product objects are `ownership:product`).
3. The parent ADR's five `## Boundary Invariants` recorded as STRUCTURAL-FENCE
   claims, each mapping 1:1 to a parent-ADR entry, audited at ADR closeout by the
   existing `gz validate --closeout-proof` machinery (no new check wired).

It ships NO ontology model, substrate, CLI verb, JSON schema, validator scope, or
runtime contract — those are OBPIs 01–03, 05–07 and are fenced off by Denied Paths.

## Files

- `docs/governance/ontology-ownership-plane-doctrine.md` — **CREATE**. The only
  net-new artifact. The ownership/plane + Harness-Purity doctrine surface plus the
  five Boundary-Invariant STRUCTURAL-FENCE records.
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants.md`
  — evidence recording only (Stage 4/5 evidence sections).

## Steps

1. **Reconcile the brief against the parent ADR `## Boundary Invariants`** (REQ-07):
   confirm all five entries (rebuild-fidelity; derived-never-authority; sense images
   structure only; harness-purity; OKF-absorption-open) exist verbatim in the ADR
   so each STRUCTURAL-FENCE REQ anchors to a real entry. (Already confirmed:
   ADR-0.32.0 lines 51–75.)
2. **Author `docs/governance/ontology-ownership-plane-doctrine.md`** (REQ-01, REQ-02):
   - Header + Source-ADR pointer (match the state-doctrine.md doc shape/tone).
   - § Two-Axis Type Model: ownership (`harness|product`) × plane (`product|process`),
     with the dormant `ontology.schema.json` plane field continuity note.
   - § Harness-Purity Invariant: `ownership:harness` admits only GovZero-universal
     types; gzkit's product objects (CliVerb/Validator/Skill/Chore) are
     `ownership:product`.
   - § Boundary Invariants (STRUCTURAL-FENCE), five subsections mapping 1:1 to the
     parent ADR entries #1–#5, each naming the parent-ADR anchor and the closeout
     proof channel.
   - § Derived-never-authority note: the doctrine is an orientation surface audited
     at closeout, NEVER consumed as governance authority by any `gz validate` scope,
     gate, or closeout step (REQ-05, honoring parent BI #2).
3. **Record evidence** in the brief's evidence sections (three-channel proof outputs).

## Denied (do NOT touch)

- Parent ADR body (REFERENCE ONLY — do not rewrite its `## Boundary Invariants`) — REQ-04.
- `src/gzkit/**`, `src/gzkit/schemas/**`, `src/gzkit/commands/**`, `src/gzkit/cli/**` — REQ-03.
- `mkdocs.yml`, `.gzkit/manifest.json`, CI/lockfiles/new deps, generated vendor mirrors.

## Verification

```bash
uv run gz obpi validate --authored
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --closeout-proof
uv run gz covers OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants
uv run gz lint
uv run gz test
```

## Notes — Plan-Before-Exploration Disclosure (Step 6a)

- **Destination-in-mind:** Before writing this plan I had already formed the
  approach: a single markdown doctrine doc under `docs/governance/` modeled on the
  existing `state-doctrine.md` shape, with a two-axis section, a Harness-Purity
  section, and five STRUCTURAL-FENCE subsections. The brief's Objective and
  Requirements are prescriptive enough that the approach is largely dictated —
  there is one net-new file and its required contents are enumerated in REQ-01/02.
- **Rejected alternatives:** (a) Splitting the doctrine across multiple docs (one
  per axis) — rejected: the brief mandates ONE document at a named path, and the
  two axes are a single coupled type model that reads as one surface. (b) Adding a
  new `gz validate --ontology-*` closeout check to mechanically audit the fences —
  rejected: that would be a validator/CLI contract → Heavy, and the brief
  explicitly relies on the EXISTING `gz validate --closeout-proof` machinery
  (`resolve_fence_proof` resolves a state-property fence when the parent ADR
  carries `## Boundary Invariants`). Wiring a new check is REQ-03 scope creep.
  (c) Rewriting/augmenting the parent ADR's Boundary Invariants for clarity —
  rejected: REQ-04 forbids it; they are already authored and the doctrine
  references them.
