# Attested REQ Whose Subject a Later Ruling Retired

*Canonical expansion for the binding bullet in
[`.gzkit/rules/governance-core.md`](../../.gzkit/rules/governance-core.md)
§ Non-negotiable rules. Authored under GHI #823 after the transition had been
resolved correctly twice from first principles and recorded nowhere an agent
would find it. Home ruled by the operator 2026-08-18: the binding bullet lives
in `governance-core.md` because it is the only rule whose `paths:` scope
(`**/*`) loads for both known instances — one edited `tests/**`, the other
edited a JSON data file, and a `tests/**`-scoped rule would have missed the
second by construction.*

## The transition

An attested REQ asserts something about a surface. A later doctrine ruling
retires that surface's subject. The REQ's parent ADR is **terminal** and
cannot be amended.

The population is bounded and non-empty: every terminal ADR carrying attested
REQs whose subject a later ruling can retire. `ADR-0.0.37` alone produced two
instances in sixteen days.

## Why the usual repair is unavailable

Ordinary doctrine drift is repaired by amending the artifact that carries the
claim. Here that move is unavailable **by construction** — a terminal ADR
(`ADR-0.0.37` § Terminal Disposition, "Split-and-Supersede", 2026-07-18)
cannot accept an amendment, and its permanently-withdrawn OBPIs cannot accept
new work. So the disposition has to live somewhere other than the ADR, which
is what makes this a distinct class rather than an instance of doc drift.

Note where an agent is actually standing when this fires: in `tests/`, or in
`data/`, or wherever the retired surface lives — **not** in
`docs/design/adr/**`. Nobody edits a terminal ADR, because it is terminal.
A rule scoped to the ADR tree would never load.

## The two wrong answers

Both are locally plausible, which is why this needs writing down:

| Wrong answer | Why it fails |
|---|---|
| **Delete the covering test / retire the file** | Orphans an attested REQ. The attestation record then claims proof that no longer exists — the record is falsified, not updated. |
| **Keep it unchanged** | The surface now asserts retired doctrine. The suite fails, or the fence encodes a claim the codebase has ruled against. |

## The disposition (binding)

1. **Read what the REQ *literally* asserts** — not what its surface currently
   demonstrates, and not what you assume it was for. These routinely differ,
   and the difference is the whole procedure.
2. **Repair the surface so that literal assertion stays true.** The surface is
   repairable; the attested assertion is the invariant.
3. **Preserve the proof-channel binding.** The `@covers` tag, the ledger
   citation, or the `## Boundary Invariants` entry stays attached. Moving or
   dropping it is the delete answer wearing a repair's clothes.
4. **Record the amendment and its reason at the surface** — the test docstring,
   the file, the commit body. A silent repair leaves the next reader deriving
   this again, which is the failure GHI #823 was filed on.

## The discriminator — when this does NOT apply

The procedure works because in both known instances the REQ's literal
assertion was **doctrine-neutral**: it survived the ruling untouched, and only
the surface underneath it was stranded.

If a REQ *literally* asserts the retired doctrine, step 2 has nothing to
repair toward — no rewriting of the surface can make a retired claim true.
**There is no known instance of this, and no procedure is claimed for it.**
The honest disposition is operator escalation: the attestation is a true
historical record of what was decided on its date, the ruling is a true
statement of what is decided now, and reconciling two true records on an
unamendable artifact is a governance decision rather than an editing task.
Do not stretch the procedure above to cover it.

## Worked example 1 — four `@covers` tests (GHI #819, `da935dc35`, 2026-08-17)

`TestPerVendorTemperatureRouting` carried four `@covers` tests for
`REQ-0.0.37-15-01` through `-04`, naming codex and claude as `AgentContract`
consumers — which `OBPI-0.35.0-09` retired. The commit body records the
reasoning verbatim:

> They cover REQ-0.0.37-15-01 through -04 on ADR-0.0.37, which is TERMINAL and
> cannot be amended, so the tests are repaired rather than deleted -- deleting
> them would orphan attested REQs.
>
> The assertions were doctrine-neutral all along; only the vendor names were
> stranded

Step 1 is visible in that second sentence: the REQ asserted that the resolver
routes, not that `AgentContract` routes per-vendor. `REQ-15-01` was repointed
to exercise two content types — `Rule` (genuinely per-vendor) and
`AgentContract` (root-only) — proving the mechanism without asserting the
retired claim.

Step 4 is visible too. `REQ-15-04`'s docstring had reserved space for *"the
intended future where codex and claude are tuned to diverge"*; the amendment
records that the future is foreclosed rather than quietly deleting the
sentence.

## Worked example 2 — a JSON invariant seed file (2026-08-02)

The `foundation-adr-registers-invariant` entry in
`data/constitutional_invariant.json` declared a structural witness that never
existed, and the Foundation Sunset froze its subject set permanently. The
reasoning, verbatim from
`docs/governance/build-to-1.0-campaign-2026-08-16.md`:

> The **file is retained, not deleted** — `REQ-0.0.37-01-03` (attested,
> OBPI-0.0.37-01) asserts only that the three seed files exist, load via
> `load_invariants`, and validate against the schema, never that the claim
> text is true; rewriting `claim` + `structural_witness` preserves attested
> canon exactly, deleting the file would falsify it.

This is the instance that fixes the rule's home. It touched a JSON data file,
not a test — so the `@covers` side of the transition was not where an agent
was standing, and a `tests/**`-scoped rule would have been silent.

Note also *"asserts only that … never that the claim text is true"*. That is
step 1 performed explicitly, and it is the sentence to imitate.

## What this is not

- **Not GHI #611** (open) — that covers undoing agent or human *error*. Here
  the attestation was **correct when made**; a later ruling retired its
  subject. Nothing needs undoing. Same neighbourhood — append-only
  corrections to attested canon — different premise.
- **Not `gz obpi repudiate` or `gz obpi withdraw`.** Per
  `.gzkit/rules/governance-core.md` § Withdraw vs Repudiate, repudiate is for
  a fraudulent or invalid completion and withdraw is for an OBPI that is no
  longer needed. This completion was neither.
- **Not an ADR amendment.** The ADR is terminal. That is the premise, not an
  obstacle to route around.

## Related

- GHI #823 — the class; this document is its discharge
- GHI #819 — closed 2026-08-18; the instance the class was named in
- GHI #611 — open; adjacent, see § What this is not
- GHI #804 — open; adjacent on attested-REQ lifecycle (an attested deferred
  frontier with no owner)
- `ADR-0.0.37-constitutional-invariant-composition` § Terminal Disposition —
  terminal 2026-07-18; the source of both known instances
- [`docs/governance/req-scope-discipline.md`](req-scope-discipline.md) — REQ
  kinds and proof channels at authoring time; this document covers the
  post-attestation case that one does not
