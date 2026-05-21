# Foundation/Feature Invariance Test

Every ADR has a **kind**: `foundation`, `feature`, or `pool`. The taxonomy
page ([ADR Taxonomy](adr-taxonomy.md)) defines the three kinds and explains
how kind binds to semver. This page answers a narrower question: *how do you
decide when you are not sure?*

The answer is a single test.

---

## The invariance test

> **"Foundation = without it, we wouldn't be doing the project."**

Apply the test by asking: *If this decision did not exist — if we removed it
from the doctrine entirely — would gzkit still be gzkit?*

- If **no** — the decision is load-bearing in the identity sense. It is a
  foundation.
- If **yes** — the decision is a capability, a backend choice, a tooling
  preference, or a workflow. It is a feature (or pool).

The test is binary. Degrees of "foundational-ness" are not a classification
category — an ADR is either a port or an adapter (see below). When the answer is
uncertain, default to feature (or pool) and promote later when downstream
work forces the invariant to be named.

---

## The hexagonal-ports lens

The invariance test maps cleanly onto the ports-and-adapters model from
[hexagonal architecture](../../governance/hexagonal-architecture.md):

- A **port** is the abstract contract — what the system requires from a
  collaborator. Ports define what the project *is*: ledger discipline, gate
  covenant, attestation surface, agent control-surface fidelity. Authoring a
  port is **foundation work**.

- An **adapter** is the concrete implementation behind the port — what fills the
  contract. Adapters ship named capabilities: JSONL storage, a specific renderer
  for control surfaces, the chosen test runner. Authoring an adapter is **feature
  work**.

When kind is ambiguous, ask: *am I authoring the port (the contract every
implementation must honor) or an adapter (one specific implementation behind a
port that already exists)?*

The port/adapter distinction does not depend on the topic's weight or technical
depth. An adapter can be highly sophisticated engineering. Sophistication does not
make it a port.

---

## Worked examples

### Ledger discipline (foundation) vs. ledger storage backend (feature)

**Foundation — ledger discipline:**

> "The ledger is the system-of-record; events are append-only and write-only;
> every governance decision must trace to a ledger entry."

This is the port. Without it, gzkit is not gzkit. The invariance answer:
*removing this decision would mean we are no longer building a ledger-first
governance system — we would be building something else entirely.*
**Kind: foundation.**

**Feature — JSONL→SQLite ledger backend:**

> "Replace the JSONL ledger backend with SQLite for query performance."

This is an adapter change. The project remains the project under either backend;
the discipline (append-only, write-only, system-of-record) is invariant. The
invariance answer: *removing this specific backend choice does not change what
gzkit is — a different backend still honors the same port.*
**Kind: feature.**

---

### ADR-0.0.33 and ADR-0.0.34 as paired foundations

These two ADRs illustrate how a port and a substrate can both be foundation
without one being more foundational than the other.

**ADR-0.0.33 — Agent Control Surface Fidelity Doctrine:**

ADR-0.0.33 is foundation because *without it, every other gzkit pillar's
binding-rule assumption is unprovable*. The fidelity contract is a port: every
rendering substrate must honor it. Invariance answer: *if the fidelity doctrine
did not exist, the fidelity validators would have no contract to enforce and
the agent control-surface guarantee would dissolve — gzkit would be a different
kind of system.*
**Kind: foundation.**

**ADR-0.0.34 — Agent Control Surface Rendering Substrate:**

ADR-0.0.34 is foundation because *without it, the per-turn surface is a
hand-authored vibing surface and the fidelity validators have nothing canonical
to diff against*. The canonical substrate is the port that fidelity validators
read against; a future renderer-of-the-month is the adapter. Invariance answer:
*if the canonical rendering substrate did not exist as a defined contract, the
fidelity doctrine (ADR-0.0.33) would be a policy with no reference implementation
— the system could not enforce what it claims to guarantee.*
**Kind: foundation.**

The pairing shows that two adjacent ADRs can both be foundation when each names
a distinct port: one names the fidelity contract, the other names the substrate
that contract operates over.

---

## The anti-pattern

**"Classifying as foundation because it feels foundational."**

Foundation is a *test answer*, not a *vibe*. If an adopter cannot articulate
"without this, the project would not be the project," the ADR is not foundation
regardless of how weighty the topic feels. Weighty topics that answer *yes* to
"does the project survive without this?" are features — or pool entries if they
have not yet earned promotion.

Vibe-classification produces doctrine bloat: ADRs that declare invariants
nobody violates and that no downstream work consults. The cost is real — every
adopter parsing the foundation layer reads decisions that never shaped anything
downstream, and the governance surface grows faster than the intent beneath it.

Apply the test. Name the invariance answer explicitly. If you cannot state it,
the ADR is not foundation.

---

## Why foundation tier? (the convention)

When `gz plan create <name> --kind foundation` scaffolds a new foundation ADR,
it pre-populates a `## Why foundation tier?` section positioned as the second
H2 in the body — between `## Persona` and `## Intent`. This section is
the canonical home for the invariance-test answer and the port-vs-adapter framing.

**The exact heading** (byte-identical — OBPI-04's validator pins this string):

```
## Why foundation tier?
```

Sentence case. Trailing question mark. No variation.

**The two scaffolded prompts:**

1. *Invariance-test answer:* "Without this ADR, would the project still be the
   project?" — answered in one sentence, naming the invariance explicitly.
2. *Port-vs-adapter framing:* "Is this ADR a port (an abstract contract every
   implementation must honor) or an adapter (one implementation behind an existing
   port)?" — answered with port or adapter and a one-line justification.

**Filled-in example** (from ADR-0.0.35 itself):

```
## Why foundation tier?

Without this ADR, kind classification for foundation candidates remains
heuristic-only — the project's ability to distinguish substrate from port
collapses to per-author judgment, and the foundation tier loses its meaning.
Foundation (the invariance test is load-bearing doctrine, not a preference).

This ADR is a port: it defines the abstract contract (the invariance test and
the hexagonal-ports lens) that every kind-classification decision must honor.
A future ADR that implements a specific classification tool is an adapter behind
this port.
```

**Scope:** Forward-only convention. Existing foundation ADRs are not backfilled
by this OBPI. When `gz validate --kind-invariance` ships (OBPI-04), it reports
drift on existing ADRs that lack the section — producing the work list for a
backfill sweep.

---

## Related

- [ADR Taxonomy](adr-taxonomy.md) — the three kinds (pool, foundation,
  feature), the kind × lane orthogonality table, and the semver binding.
- [Lanes](lanes.md) — the orthogonal axis: Lite vs Heavy.
- [Lifecycle](lifecycle.md) — how ADRs move from Draft through Attested.
- [Hexagonal Architecture](../../governance/hexagonal-architecture.md) —
  Cockburn's ports-and-adapters pattern and how gzkit maps it onto the
  ADR-kind taxonomy (the conceptual origin of the port/adapter framing).
