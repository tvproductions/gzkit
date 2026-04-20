# ADR Taxonomy

Every ADR has a **kind**, a **lane**, and (except for pool entries) a
**semver**. This page is the canonical reference for choosing which.

gzkit recognizes three kinds of ADR:

- **pool** — a backlog entry; documented intent that has not yet earned promotion.
- **foundation** — an app/system invariant; identity-shaping doctrine, semantics, or conditions.
- **feature** — an active or queued release-carrying capability.

ADR-0.0.17 locks the vocabulary mechanically (`kind:` frontmatter, `--kind`
CLI flag, `--taxonomy` validator). This page documents the operator doctrine:
*when to choose which*, *why the axes matter*, and *how the kind binds semver*.

---

## The three kinds

### Pool

A pool ADR is a backlog/waiting-area entry. It captures intent — a problem
worth solving, a capability worth considering — without committing to deliver
it on any schedule. Pool ADRs are cheap to create and expensive to promote;
the doctrine is **pool freely, promote deliberately**. A pool ADR that has
sat for a year is not a problem per se — it is documented intent that has not
earned promotion yet.

Pool ADRs use the flat backlog id prefix `ADR-pool.<slug>` and have no semver
and no `kind:` frontmatter field. They live in `docs/design/adr/pool/`.

### Foundation

A foundation ADR codifies an app/system invariant — an identity-shaping fact,
condition, concept, or semantic boundary. If the decision changes *what the
system IS* rather than *what it does*, it is a foundation. Foundations are
load-bearing: downstream features, schemas, and skills rely on them staying
true.

Foundation ADRs use semver `0.0.x` and carry `kind: foundation` in
frontmatter. Because they can land at any time without forcing a release
cut, the invariant below is load-bearing:

> **Foundation never bumps release versioning.** A foundation ADR can land
> tomorrow, in two years, or never, without advancing the release minor or
> patch. This is not a convention — it is a contract adopters rely on when
> reasoning about when a foundation-level doctrine change may appear.

### Feature

A feature ADR is an active or queued release-carrying capability. It ships a
named thing to users — a CLI verb, a workflow, a schema field, an integration
— and its completion shows up in the next release's notes. Feature work that
is "someday maybe" belongs in the pool; promotion to feature signals *this is
next up or in flight*.

Feature ADRs use non-`0.0.x` semver (`0.y.z` and up) and carry `kind: feature`
in frontmatter.

---

## Kind × lane orthogonality

**Kind** describes *what the ADR is about*. **Lane** describes *external-contract
exposure* (Lite: internal surface, Gates 1–2; Heavy: external runtime contract,
Gates 1–5). The two axes are orthogonal — any kind can be any lane.

| | **Lite lane** | **Heavy lane** |
|---|---|---|
| **Foundation** | Internal invariant or doctrine change; no external contract touched (e.g., a doctrine page refresh). Foundation-kind attestation rigor still applies — doctrine drift is invariant drift. | Invariant change that also alters a runtime contract (e.g., schema field that encodes an invariant). All five gates required. |
| **Feature** | Capability ship with no external-contract surface (e.g., a developer-only workflow improvement). | Capability ship on a public surface (CLI, schema, API, runbook contract). The common shape for feature work. |
| **Pool** | *(no lane)* — pool ADRs are backlog entries. Lane is assigned at promotion, not at pool intake. | |

**Attestation note.** Attestation rigor attaches to **lane**, not kind —
a Heavy-lane ADR gates OBPI completion on Gate 5 human attestation regardless
of kind. Foundation-kind ADRs additionally follow the foundation attestation
walkthrough discipline (see `AGENTS.md` § OBPI Acceptance Protocol) regardless
of lane, because doctrine drift is invariant drift.

---

## Kind × semver binding

The binding is mechanical and enforced by `uv run gz validate --taxonomy`:

| Kind | Semver requirement | Frontmatter field |
|---|---|---|
| `foundation` | `0.0.x` | `kind: foundation` required |
| `feature` | non-`0.0.x` (i.e. `0.y.z` with `y > 0` or `x.y.z` with `x > 0`) | `kind: feature` required |
| `pool` | *(no semver)* | *(no `kind` field)* |

The validator fail-closes on mismatch: a `0.0.x` ADR that declares
`kind: feature` (or vice versa) will not pass `gz validate`. Scaffolding via
`gz plan create --kind {pool,foundation,feature}` and promotion via
`gz adr promote --kind {foundation,feature}` enforce the binding at
authoring time.

---

## Named invariant: foundation never bumps release versioning

The foundation ⇒ `0.0.x` binding is not an aesthetic choice. It is the
mechanical half of a two-part contract:

1. Foundation ADRs land at `0.0.x`.
2. Release versioning (`0.y.z` minor/patch, `x.y.z` major) is driven by feature ADRs.

Taken together, **landing a foundation ADR never advances the release
version.** Adopters reading the changelog can assume that the presence of
new invariants or doctrine in a release is additive to — never a precondition
of — the release's feature delivery. A foundation ADR can be added years
after the feature that depends on it; the feature's release cut is not held
hostage to a foundation-level debate. This is what makes the foundation
kind safe to grow over time: its cadence is detached from the release clock.

---

## Worked examples

### Foundation — ADR-0.0.9 state-doctrine-source-of-truth

- **Kind:** foundation
- **Semver:** 0.0.9
- **Why foundation:** The state-doctrine ADR defines which storage tier is
  source-of-truth (Layer 1 canon), which is derived (Layer 3 views), and which
  is log-of-record (Layer 2 ledger). It does not ship a feature — it shapes
  what gzkit *is* as a governance system. Every downstream feature that
  reads or writes state inherits the doctrine's invariants. A change here
  would re-shape the identity of the system, not the contents of a release.

### Feature — ADR-0.6.0 pool-promotion-protocol

- **Kind:** feature
- **Semver:** 0.6.0
- **Why feature:** The pool-promotion-protocol ADR ships a named workflow —
  how a pool ADR is promoted to an active foundation or feature ADR — with
  CLI surface (`gz adr promote`), brief-authoring expectations, and ledger
  events. Adopters use the capability directly; its arrival in a release
  note reads as "gzkit can now promote pool ADRs through a reviewed workflow."
  That is a feature ship, and its semver (0.6.0) reflects a minor release
  cut.

### Pool — ADR-pool.ai-runtime-foundations

- **Kind:** *(no kind — pool entries have no kind field)*
- **Semver:** *(none)*
- **Why pool:** AI-runtime-foundations documents a post-1.0 architectural
  intent (what AI-runtime control primitives gzkit would eventually need) that
  the project explicitly will not promote until after the graph spine and
  state doctrine stabilize. `CLAUDE.md` § Architectural Boundaries names it
  as a post-1.0 concern. It is real, documented intent — but it has not
  earned promotion, and pooling it is the right answer. A pool ADR is not a
  deferred feature ADR; it is a different object, with a different lifecycle
  and a different role.

---

## Related

- [ADR-0.0.17 (mechanical taxonomy)](../../design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md) — `kind:` field, `--kind` CLI, `--taxonomy` validator.
- [ADR-0.0.18 (this doctrine)](../../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md) — operator doctrine source.
- [Lanes](lanes.md) — the other axis (Lite vs Heavy).
- [Lifecycle](lifecycle.md) — how ADRs move from Draft through Attested.
