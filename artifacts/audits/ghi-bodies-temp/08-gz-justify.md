## What it is

A pre-execution reasoning skill that produces an evidence-grounded justification walkthrough for any proposed change anchor (GHI, OBPI, or draft description) *before* work begins. Output is an 8-section structured report that forces the agent or operator to surface evidence, calibrate severity, justify scope, name routing, and declare residual uncertainty — before any source edits land.

## Why it matters

- **Enforces the Prime Directive "if <90% sure, ask" invariant** (`AGENTS.md` § Behavior Rules). The 8th section ("Residual uncertainty") is a forcing function for honest calibration — an agent that can't name what's uncertain hasn't understood the change.
- **Closes the class of "confident-wrong-direction" runs** that waste session context and produce discarded work.
- **Every code and artifact change in gzkit traces to a GHI or OBPI.** `gz-justify` becomes the canonical pre-execution gate for that trace.
- **Surfaces design corrections before implementation.** The 8-section walkthrough structure was developed ad-hoc during the 4.7 governance hardening audit (umbrella #224). The structure repeatedly caught errors that would have shipped (e.g. *"agent has no clock"* → *"tool has a clock via arb receipt"* correction). Operator recognized the pattern as reusable and prioritized it for extraction as a durable skill.

## Invocation

```
/gz-justify <GHI-N>                    # reason about an existing GHI before implementation
/gz-justify <OBPI-X.Y.Z-NN>            # reason about an OBPI before Stage 2
/gz-justify draft: <description>       # reason about a proposed change without a filed anchor yet
```

Optional flags:
- `--severity-gate <P0|P1|P2>` — require at least one finding at this severity or emit a warning
- `--related <GHI-M,GHI-K>` — cross-reference other anchors as evidence input
- `--write-receipt` — emit an ARB-style receipt of the walkthrough to `artifacts/receipts/justify/`

## Output — the 8-section walkthrough

1. **What I see (the problem)** — bounded problem statement grounded in file:line citations and quoted text
2. **Per-instance severity** — honest P0/P1/P2 calibration when the anchor covers a set of instances
3. **Why this scope** — not-too-narrow, not-too-broad justification of the anchor's boundary
4. **What it proposes** — specific actions with file:line targets
5. **Routing decision** — direct-fix vs OBPI ceremony, with threshold citations from `defect-fix-routing.md`
6. **Why this design is right-sized** — explicit trade-off articulation
7. **What convinces me (evidence)** — ledger events, prior GHIs, recent commits, vendor documentation with citations
8. **Residual uncertainty** — honest "I don't know" surfacing with probability calibration (e.g. "Confidence 85% on X because Y")

## Grounding contract

Before producing the walkthrough, the skill MUST read:

- The anchor itself — `gh issue view <N>` for GHIs, brief file for OBPIs, operator description for drafts
- Relevant ledger events — `gz state --json` filtered to anchor ID
- Recent commits — `git log --since='60 days ago' --grep=<scope>`
- Related rules under `.gzkit/rules/` whose `paths` frontmatter matches the anchor's touched surface
- The hygiene taxonomy at `docs/governance/model-regression-taxonomy.md`
- Any related ADRs referenced by the anchor

The grounding step is NON-OPTIONAL. A walkthrough produced without grounding evidence is explicitly flagged by the skill as "provisional — evidence not gathered" and the operator is prompted before proceeding.

## Implementation shape

- `src/gzkit/commands/justify.py` — CLI handler with Click subcommand under `gz justify`
- `.gzkit/skills/gz-justify/SKILL.md` — skill definition with frontmatter, `gz_command: justify`, body
- `tests/commands/test_justify.py` — unit tests for walkthrough structure assertion (each of 8 sections present, grounding evidence captured)
- `features/justify.feature` — BDD scenarios covering `@REQ-*` for operator flows (invoke with GHI, with OBPI, with draft; grounding-missing path; receipt emission)

## Routing

Heavy-lane OBPI under a new ADR — adds a CLI surface, establishes a load-bearing governance gate, requires Gate 5 attestation. Not direct-fix territory; the skill itself becomes precedent-setting infrastructure.

## Dogfooding proposal

Once landed, `gz-justify` should be used to produce the walkthroughs for:
- Any remaining 4.7 governance hardening GHIs not yet hand-authored (the 4.7 series started pre-skill; later GHIs should use the skill)
- Every new OBPI before Stage 2 implementation
- Any `fix(...)` commit over the direct-fix threshold per `defect-fix-routing.md`

## Out of scope

- Post-execution review (that's `gz-obpi-reconcile` and `gz-adr-closeout-ceremony`)
- Mid-execution course correction (operator intervention, not a skill concern)
- Automatic fix generation — `gz-justify` is reasoning about a change, not implementing it

## Precedents

- `.gzkit/rules/attestation-enrichment.md` — same shape (forcing mechanical evidence before a claim)
- `.gzkit/skills/gz-plan-audit` — pre-flight alignment; `gz-justify` sits UPSTREAM of `gz-plan-audit` (justify before planning)
- `.gzkit/skills/gz-design` — forcing-function-driven dialogue skill; similar structure-producing-discipline pattern

## Origin

Authored 2026-04-18 during the 4.7 governance hardening audit (umbrella GHI #224). The 8-section walkthrough was developed ad-hoc while presenting sub-GHIs (#225 through #230) to the operator. The structure repeatedly surfaced weaknesses (e.g. `chores.md:19` correction — original fix shape "drop the threshold" was wrong; operator observed "tools have a clock via arb receipts" and the correct fix became tool-enforcement rather than removal). Operator identified the pattern as reusable across any GHI or OBPI pre-execution review. This issue tracks its formalization as a durable skill.

## Priority

Prioritized by operator during the 4.7 audit session (2026-04-18). Filed standalone (not as part of the 4.7 series, umbrella #224). Draft the skill in parallel with completing the 4.7 GHI remediation; once landed, use for the multi-agent surface ADR discussion and any post-4.7 governance work.
