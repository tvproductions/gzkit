# Plan: OBPI-0.0.37-10 — Doctrine Refresh

**OBPI:** `OBPI-0.0.37-10-doctrine-refresh`
**Parent ADR:** `ADR-0.0.37-constitutional-invariant-composition`
**Lane:** Lite
**Date:** 2026-06-06

---

## Context

ADR-0.0.37 ships CIC-1 (composition) and CIC-2 (brief↔reality coherence) as the structural
foundation for constitutional invariants. Before this ADR, the two pool stubs
`ADR-pool.brief-authoring-evidence-checks` and `ADR-pool.obpi-pipeline-dispatch-attestation`
each rejected foundation-kind framing by citing "the invariant already exists in AGENTS.md
operative-claim-4" — a textbook instance of the inversion ADR-0.0.37 fixes. ADR-0.0.18's
kind-axis doctrine also predates the structural-witness vs. prose-assertion distinction.

OBPI-10 is a docs-only refresh. No CLI, no schema, no runtime contract surface changes.
Denied: AGENTS.md, all src/ files, manpages, CI files.

---

## Files (Allowed Paths)

| File | Change |
|------|--------|
| `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` | Append amendment H2 section (dated 2026-06-06, referencing ADR-0.0.37 as structural anchor; explicit structural-witness vs prose-assertion distinction; pointer to `.gzkit/invariants/`) |
| `docs/design/adr/pool/ADR-pool.brief-authoring-evidence-checks.md` | Append "Re-routing note (post-ADR-0.0.37)" block: CIC-2 as prerequisite foundation; stub promotes to feature-kind once CIC-2 lands |
| `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md` | Append "Re-routing note (post-ADR-0.0.37)" block: same shape as above |
| `docs/governance/governance_runbook.md` | Add new section "Before proposing a foundation-kind ADR" with the three-step algorithm |
| `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-10-doctrine-refresh.md` | Update brief (this file) at completion — read-only during implementation |

---

## Implementation Steps

### Step 1: Amend ADR-0.0.18

**File:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`

Append a new H2 amendment section after the existing `## Amendment 2026-05-23 — ADR-0.0.57`
and before `## Attestation Block`:

```markdown
## Amendment 2026-06-06 — ADR-0.0.37

ADR-0.0.37 (Constitutional Invariant Composition, 2026-06-06) sharpens the kind-axis
distinction this ADR establishes. The binding addition:

**Foundation kind carries a structural-witness requirement.**

A "foundation ADR" is not merely an ADR about identity/invariants — it must register its
invariant in the constitutional invariant registry at
[`.gzkit/invariants/`](../../../.gzkit/invariants/) with a non-empty `structural_witness`
array (schema + validator + ledger event). A claim that appears only in AGENTS.md or in
ADR prose, without a corresponding registry entry and mechanical witness, does NOT qualify
as foundation kind — it is a prose-asserted claim that can drift without mechanical detection.

**Structural-witness foundation vs. prose-asserted claim (additive to Decision items 1–4):**

- **Structural-witness foundation:** Invariant intent registered in `.gzkit/invariants/`
  with `structural_witness: [schema, validator, ledger_event]` ≥ 1 entry. The witness is
  the thing that guarantees the invariant cannot be silently undermined. ADR-0.0.37's CIC-1
  and CIC-2 are the canonical examples.
- **Prose-asserted claim:** An invariant stated only in AGENTS.md operative claims, a
  pool-ADR Alternatives-Considered rejection, or an ADR body paragraph. Real, documented —
  but structurally unwitnessed. Pool stubs whose Alternative-C rejection cited AGENTS.md
  § operative-claim-4 as their anchor were relying on a prose-asserted claim.

**Consequence for future foundation proposals:** Before proposing a foundation-kind ADR,
identify the constitutional invariant the proposed ADR registers. If none exists yet, propose
the invariant first (author a `.gzkit/invariants/<slug>.yaml` draft). Only then promote to
ADR. This algorithm is documented in
[`docs/governance/governance_runbook.md`](../../../docs/governance/governance_runbook.md)
§ "Before proposing a foundation-kind ADR".

**Reference:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
```

### Step 2: Re-route pool stub — brief-authoring-evidence-checks

**File:** `docs/design/adr/pool/ADR-pool.brief-authoring-evidence-checks.md`

Append after the last paragraph in the `## Notes` section (or after `## Decision` if Notes
doesn't exist) but before `Pool ADRs are backlog items`:

```markdown
## Re-routing note (post-ADR-0.0.37)

**Added 2026-06-06 (OBPI-0.0.37-10).**

This pool stub's Alternative-C self-rejection read: *"Foundation kind is reserved for
app/system invariants per ADR-0.0.18; these are mechanical defenses *of* an invariant
(observed-evidence discipline at authoring time), not the invariant itself."*

That reasoning was grounded in AGENTS.md § operative-claim-4 as the claimed foundation
invariant — a prose-asserted claim, not a structurally-witnessed one. ADR-0.0.37 ships
**CIC-2** (brief↔reality coherence) as the actual foundation invariant: registered in
`.gzkit/invariants/`, schema-validated, ledger-witnessed (`brief_reconciled` /
`brief_reconcile_drift_detected` event family), and mechanically fail-closed at pipeline
Stage 1 and Stage 5.

**Consequence for this stub:** Once ADR-0.0.37 is Validated (CIC-2 landed and attested),
this pool stub promotes to a **feature-kind ADR** — a mechanical defense *of* CIC-2 at
the authoring-time surface, not a foundation candidate. The Alternative-C reasoning is
retroactively correct in form but was pointing at the wrong anchor; CIC-2 is the right one.

**Prerequisite for promotion:** ADR-0.0.37 Validated (OBPI-0.0.37-05/06/07/08 attested-complete).

**Reference:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
```

### Step 3: Re-route pool stub — obpi-pipeline-dispatch-attestation

**File:** `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md`

Append the same shape of re-routing note after the last paragraph in `## Notes` but before
`Pool ADRs are backlog items`:

```markdown
## Re-routing note (post-ADR-0.0.37)

**Added 2026-06-06 (OBPI-0.0.37-10).**

This pool stub's Alternative-C self-rejection read: *"Foundation kind is reserved for
app/system invariants per ADR-0.0.18; these are mechanical defenses *of* an invariant
(ledger-of-truth), not the invariant itself."*

That reasoning was grounded in AGENTS.md § operative-claim-4 as the claimed foundation
invariant — a prose-asserted claim, not a structurally-witnessed one. ADR-0.0.37 ships
**CIC-2** (brief↔reality coherence) as the actual foundation invariant: the dispatch
attestation gap this stub scopes is a feature-shaped defense *of* that foundation
invariant, not a foundation candidate in its own right.

**Consequence for this stub:** Once ADR-0.0.37 is Validated (CIC-2 landed and attested),
this pool stub promotes to a **feature-kind ADR** — a mechanical defense *of* CIC-2's
execution-time dispatch surface. The Alternative-C reasoning is correct in form but was
pointing at the wrong anchor; CIC-2 is the right one.

**Prerequisite for promotion:** ADR-0.0.37 Validated (OBPI-0.0.37-05/06/07/08 attested-complete).

**Reference:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
```

### Step 4: Add foundation-kind guidance to governance_runbook.md

**File:** `docs/governance/governance_runbook.md`

Locate the `## Workflow: Create or Promote ADR` section. Insert a new sub-section
**before** step 1 ("Inspect active and pending ADR state"):

```markdown
### Before proposing a foundation-kind ADR

Foundation kind requires a structural witness — a registry entry in
`.gzkit/invariants/` with a non-empty `structural_witness` array. A prose-only claim
(in AGENTS.md, a pool-ADR body, or ADR prose) does not qualify.

**Three-step algorithm (from ADR-0.0.37 and ADR-0.0.18 Amendment 2026-06-06):**

1. **Identify the constitutional invariant** the proposed ADR registers. What is the
   invariant intent — the property of the system this ADR is here to guarantee? State it
   in one sentence.

2. **If no registered invariant exists yet, propose the invariant first.** Author a
   `.gzkit/invariants/<slug>.yaml` draft (schema: `src/gzkit/schemas/constitutional_invariant.json`)
   with `structural_witness` named. Do not author the ADR until the invariant is
   registered and its structural witness is named.

3. **Only then promote to ADR.** With the invariant registered and the structural witness
   named, the ADR can be authored as a foundation-kind proposal — its Decision section
   will reference the registry entry, and `gz validate --taxonomy` will accept it.

**Reference:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
```

---

## Gate 2 Note (Docs-Only OBPI)

No code changes → no unit tests added. Gate 2 satisfied with:
> "no test deliverable — docs-only OBPI; verification is `uv run gz lint` + `uv run mkdocs build --strict` + cross-reference grep checks"

---

## Verification Commands

```bash
uv run gz lint
uv run mkdocs build --strict

# REQ-01: ADR-0.0.18 amendment references ADR-0.0.37
rg -n "ADR-0\.0\.37|CIC-1|CIC-2|structural.witness" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/

# REQ-02/03: pool stubs reference CIC-2
rg -nl "CIC-2" docs/design/adr/pool/

# REQ-04: contributing doc has the new section
rg -n "Before proposing a foundation-kind ADR" docs/governance/

# REQ-05: this OBPI did NOT touch AGENTS.md or any src/ file
git diff --name-only
```

---

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

**Destination already formed:** Append amendment section to ADR-0.0.18, append re-routing
notes to both pool stubs, insert foundation-kind guidance section in governance_runbook.md.

**Rejected alternatives considered:**

1. Author a standalone new foundation ADR for the structural-witness doctrine — rejected
   because ADR-0.0.37 is the structural home and this OBPI's scope is explicitly limited to
   amending/annotating the downstream surfaces that need updating.

2. Edit AGENTS.md directly to add the structural-witness distinction — explicitly denied by
   the brief ("AGENTS.md: OBPI-09 owns the rewrite-through-registry path; this OBPI must
   not edit AGENTS.md directly").

3. Add `gz adr amend` CLI invocation — the brief says "via the `gz adr amend` flow if it
   exists; otherwise via amendment-pool stub." No such CLI verb exists yet; direct file
   edit is the correct path.

---

## Notes

- All four edits include full path cross-references to ADR-0.0.37 per REQ-06.
- The re-routing notes go in `## Notes` sections (the pool stubs already have a Notes section
  with content). If Notes ends before `Pool ADRs are backlog items`, insert the new section
  between them.
- No sync required: these are doc files, not skill/rule canonical surfaces.
