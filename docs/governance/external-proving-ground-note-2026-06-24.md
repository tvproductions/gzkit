# External Proving Ground Note — 2026-06-24

**Status:** Operator-supplied strategy synthesis. Captured from the operator
design dialogue of 2026-06-24. It is not a new campaign, not an ADR, and not
an authority layer — a direction to align the apparatus to, deferred for
later routing. Natural home when picked up: a design note that may seed a
pool-ADR candidate.

## Thesis

gzkit cannot validate its own theories — the airlock / seam-map discipline,
reasoning-mode induction, "governed loop engineering" — by dogfooding on
itself. gzkit-governing-gzkit is a maximally self-referential, confounded
test surface: it exercises *governance-meta* seams, never the *real
application* seams (imports, call-sites, product contracts) the theories
actually make claims about. Self-dogfooding therefore cannot show whether a
theory **generalizes**, and it can get messy.

An external project is the **live negative control for gzkit's strategic bet
itself**. The North Star claim is "governed loop engineering improves
agent-driven work." If the only loop gzkit ever governs is its own, that
claim is unfalsifiable — meta-level vibing, the exact failure class the
apparatus exists to make inert. A proving ground is what turns "gzkit helps"
into a claim a negative control can refute.

## The missing forcing function

"Wait-and-see" caution — e.g. deferring tool-computed AIRLOCK-IN until the
graph engine lands — is only legitimate if there is a mechanism to actually
*see*. Today gzkit has **no forcing function, no trial-run surface, no
scouting loop**, so that caution is currently indistinguishable from plain
deferral. The Loop Leverage Test asks "does it enable faster failure before
state corrupts?" — you cannot fail fast with no external surface to fail on.
A skunk-works problem set is the prerequisite that makes both the caution and
the theories falsifiable.

## Candidate selection — rhea

Three candidate proving grounds exist, all at `github.com/tvproductions`
(exact repo slugs to confirm):

| repo | shape | fit |
|---|---|---|
| **rhea** | small repository pattern library | **best fit** — small, bounded scope = clean trial surface |
| **pueo** | more ambitious "afk" (away-from-keyboard) agent framework | too large/ambitious for a controlled first trial |
| **gzfactor** | more ambitious "afk" agent framework | too large/ambitious for a controlled first trial |

rhea has been used as a test target, but only briefly. Its small,
pattern-library scope is the reason it is the right first proving ground:
fewer confounds, real-but-bounded application seams.

## Mechanism — genesis-forward, lateral branches, gzkit bootstrapping

The affordance the operator named: take rhea back to its **genesis document**
— the earliest commit, when it is "just its original design doc" — and from
that clean start:

- **start lateral branches** off the genesis document, each a discovery probe;
- **allow gzkit bootstrapping** into each branch (init the apparatus from
  scratch on a real, non-gzkit project);
- run the work forward through gzkit's full apparatus, exercising
  design → build → fix → refactor on real product seams.

This is a controlled from-clean trial: known starting state, real seams, gzkit
as the *instrument* rather than the *subject*.

## Relationship to current work

This is upstream of the AIRLOCK-IN sequencing question (judgment-grade vs
tool-computed, and the time-vs-contract-adjacency tradeoff): a proving ground
may be the thing that *resolves* that fork by letting the theories be scouted
under real use, rather than a peer to it. It touches the Build-to-1.0
campaign (Magna Carta) because it concerns *how gzkit validates anything at
all* — so any adoption is operator-ratified, not agent-initiated.

Explicitly deferred — not yet routed to any ADR, OBPI, or GHI.

## Provenance

Captured from the operator design dialogue, 2026-06-24. Operator anchors:

- gzkit needs a "problem set" within which it can perform "skunk works"
  validation and discovery.
- applying gzkit outside its own dogfooding — which can get messy — is needed;
  otherwise we have no places to test our theories.
- rhea is the right scope; start lateral branches with just the "genesis"
  document and allow for gzkit bootstrapping.
- rhea is a small repository pattern library; pueo and gzfactor are more
  ambitious "afk" agent frameworks; rhea is likely the best fit.

**Related:** [Harness Loop Engineering Strategy Note](harness-loop-engineering-strategy-note-2026-06-23.md)
· [Work Phases and the Airlock](work-phases-and-airlock.md)
· [Build-to-1.0 Campaign](build-to-1.0-campaign-2026-06-20.md)
