---
id: ADR-pool.attested-record-edit-doctrine
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI #549
---

# ADR-pool.attested-record-edit-doctrine: Attested-Record Edit Doctrine

## Status

Pool

## Date

2026-06-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Close the **write-side gap** in gzkit's layer doctrine. `AGENTS.md` § Behavior
Rules — Never #7 and `docs/governance/state-doctrine.md` canonize the *read*
rule — *"frontmatter is Layer-1 authorship and can be hand-edited, so read the
ledger (Layer-2) for completion"* — but there is **no write-side companion**
answering the symmetric question: *may an agent edit a record whose ledger says
`attested_completed`, and if so, which edits preserve the attestation and which
reopen it?*

Today the answer is per-OBPI judgment, and the same question re-fires on every
coupled-surface rename. The canonical instance (GHI #549, follow-up to #532):
five attested OBPI briefs carry a stale manpage pointer (`gz-validate.md`) after
the canonical file was renamed (`validate.md`); correcting the pointer is a
zero-semantic-change edit, yet no doctrine says whether it may land on an
attested brief without re-attestation. The same shape recurs for schema-field
renames, CLI-verb renames, ledger-event renames, and the immediate
`ln:`→`req_evidence:` evidence-frontmatter key-rename folded into GHI #593's fix.

Codify the answer once as a binding, record-kind-agnostic doctrine so the
recurring per-incident operator decision becomes a mechanical rule.

## Decision

_(Pool — doctrine ruled via `gz-design` on 2026-06-08; mechanization surface
decisions deferred to promotion.)_

### The discriminating principle (operator-ratified)

> An edit to an attested record is admissible **without re-attestation** iff it
> preserves the attested semantics — it changes only how a fact is *rendered or
> pointed at*, never what a reader extracts about **(1)** what the REQs require,
> **(2)** what proves them, or **(3)** whether they are done.

### The CLOSED enumeration (three buckets)

| Bucket | Edit shapes | Disposition |
|--------|-------------|-------------|
| **Admit** (no re-attestation) | renamed-target pointer updates (stale path → current on-disk name); pure key-renames of evidence frontmatter (`ln:`→`req_evidence:`); typo/spelling fixes in non-REQ prose; schema-conformance heading rewrites | Permitted; semantics-preserving by construction |
| **Re-attest required** | any change to REQ text or acceptance criteria; **any change to the evidence-binding layer — including `@covers` decorator backfill and ceremony-trailer additions** | The attestation was a statement that the proof, as it stood, was sufficient; touching the proof layer reopens that statement |
| **Forbid outright** | silently re-pointing which receipt/proof proves a REQ | Covert mutation of axis (2) — the core of what was attested |

**Strict-on-proof-binding** is the ratified stance: the evidence-binding layer is
never a free edit on an attested record. The rejected lenient reading would have
admitted `@covers` backfill as "omission-repair," but a backfilled `@covers`
pointing at a non-covering test would then slip past the human witness.

### Coherence with the existing covers-backfill heuristic

The strict ruling **generalizes a stance gzkit already enforces mechanically.**
The covers-backfill heuristic (`.gzkit/rules/adr-audit.md`; GHI
#272/#309/#382/#466) already treats adding a `@covers` decorator in an attested
context as requiring an explicit operator attestation — the
`# audit-exempt: regression-invariant-overlay <reason>` inline marker, whose
reason text is mechanically required so it "can't be a one-token escape hatch."
This doctrine lifts that surface-specific rule to a record-kind-agnostic
principle: the proof layer of an attested record is witness-bearing, and
touching it requires a witness.

### Reach

Record-kind-agnostic. Primary surface: attested OBPI briefs. Attested ADR
metadata is covered by the same principle, coordinated with
`ADR-pool.adr-layer-coherence` (which owns the *mechanism* — `gz adr amend` +
`adr_amended` events + cross-layer drift validators — for that surface). This
doctrine owns the *admissibility ruling*; that ADR owns the *amendment
mechanism*.

### Open surface decisions (resolve at promotion)

- **Validator scope** that mechanizes the three buckets fail-closed: standalone
  `gz validate --attested-brief-edits` vs. folding into `gz validate --documents`.
- **Where the admit-list is encoded:** brief-schema annotation vs. a validator
  constant (closed-set enum, extensible only by ADR like the abandon-category
  enum in `.gzkit/rules/token-block-discipline.md`).
- **Whether an admissible edit must emit a provenance ledger event** (reusing
  `adr-layer-coherence`'s `adr_amended` machinery) or is recorded only in git
  history. The strict bucket already forces re-attestation for proof edits; the
  question is whether *admit*-bucket edits also warrant a Layer-2 trace.

## Alternatives Considered

1. **Extend `ADR-pool.adr-layer-coherence` in place.** Lowest artifact count;
   that ADR already proposes the `gz adr amend` / `adr_amended` machinery this
   doctrine's enforcement would consume. **Rejected** (operator scope ruling,
   2026-06-08): couples a *doctrine* (admissibility ruling) to a *mechanism*
   (drift-validator) across two surfaces; the doctrine must be crisp and
   schedulable on its own. The two compose by reference, not by merger.
2. **Fold into `ADR-pool.obpi-state-machine`** as a transition-precondition.
   Maximally consolidated and the eventual absorber GHI #549's body names.
   **Rejected:** buries a narrow, shippable doctrine ruling inside an unscheduled
   architectural rewrite of ~30 audits; the ruling is needed before that ADR is
   scheduled (it gates #593's rename).
3. **Lenient-on-omission-repair principle** — admit `@covers` backfill and
   ceremony-trailer additions as proof-strengthening, not proof-changing.
   **Rejected** (operator fork ruling, 2026-06-08): blurs the strengthen-vs-change
   line; a backfilled `@covers` pointing at a non-covering test would land on an
   attested brief with no human witness — the exact failure the covers-backfill
   heuristic exists to prevent.
4. **No doctrine — keep per-OBPI judgment.** The status quo. **Rejected:** this
   *is* the defect. It produces a recurring per-incident operator decision on
   every coupled-surface rename (#532, #549, and every future schema/verb/event
   rename), which is precisely what #549 was filed to end.

## Notes

**Sibling routing receipts (on promotion):**

- GHI #549 (the doctrine gap — admissible-edit-shapes on attested records) closes
  `superseded` against this ADR.
- GHI #532 (the manpage-pointer instance that surfaced the gap) closes
  `superseded` against this ADR once the mechanization lands the 5-reference fix.

**Relationships:**

- **Consumes** `ADR-pool.adr-layer-coherence`'s amend machinery (`gz adr amend`,
  `adr_amended` ledger event) for the attested-ADR-metadata surface.
- **Becomes a transition-precondition** in `ADR-pool.obpi-state-machine` if/when
  governance consolidates onto the canonical state machine.
- **Sibling** to `ADR-pool.doctrine-amendment-protocol` (both govern
  post-authoring amendment; that ADR's subject is foundation-doctrine documents
  and their citation cascades, not attested briefs).
- **Authorizes GHI #593's `ln:`→`req_evidence:` rename** across the 17 affected
  attested briefs: a pure evidence-frontmatter key-rename is an **Admit**-bucket
  edit under this doctrine. #593's fix depends on this ruling.

**Promotion criteria:** before `gz adr promote --kind foundation`, resolve the
three § Open surface decisions with operator preference. Likely promotes as a
**foundation** ADR (a governance invariant — *without a write-side rule for
attested records, the ledger-of-truth doctrine is half-specified*). May promote
**alongside GHI #593's fix**, since #593 cannot land its rename until this
doctrine authorizes it. Promotion semver assigned at promotion time (next
foundation slot).

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
