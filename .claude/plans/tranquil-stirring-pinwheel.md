# OBPI-0.0.18-02 — Runbook: PRD → ADR Derivation Guidance

## Context

ADR-0.0.17 landed the mechanical taxonomy (`kind:` field, `--kind` CLI flag,
`--taxonomy` validator). ADR-0.0.18 lands the *doctrine* — the operator-facing
guidance that explains when to choose which kind. OBPI-01 (the
`docs/user/concepts/adr-taxonomy.md` concepts page) has already shipped and is
the one-page canonical reference.

What's still missing — and what this OBPI closes — is the **runbook-level
"given a PRD and a Constitution, how do I decide which ADRs to write"**
guidance. The runbook currently jumps from operating-model loops to
`gz plan create` commands without ever answering the upstream decomposition
question. Adopters reading the runbook see *how to scaffold an ADR* but not
*how to decide which ADRs to scaffold*.

This OBPI is Lite-lane, doc-only, and parallel-root with OBPI-01 (which has
completed, so its concepts-page anchors are available to link to).

## Files to modify

| File | Change |
|------|--------|
| `docs/user/runbook.md` | Insert a new `## PRD → ADR Derivation` section immediately before `## Governance Planning Commands` (currently at line 525) |
| `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/obpis/OBPI-0.0.18-02-runbook-prd-to-adr.md` | Tag all seven REQs with `[doc]` prefix so `gz covers --json` correctly classifies them as `ReqKind.DOC` (scope amendment — see below) |

## Files explicitly NOT touched

- `docs/governance/governance_runbook.md` — The brief's Allowed Paths lists it
  "if warranted," but the exploration confirmed governance_runbook.md is
  procedural (lifecycle command checklists), not conceptual. The PRD→ADR
  decomposition gap is user-facing; governance_runbook has no analogous gap
  to parallel-fill. Per behavioral-invariants §2/§4 scope boundary: fix what
  the OBPI broke or surfaced; leave what is independently intact alone.

## Scope amendment — REQ tagging

**Nature:** The brief's REQs 1–7 are not tagged `[doc]`. Without the tag,
`gz covers` classifies them as `ReqKind.CODE` (default), and the Stage 3
Phase 1b parity gate (`uv run gz covers OBPI-0.0.18-02 --json`) will fail
because no `@covers` decorators exist — nor can any, because this OBPI ships
prose, not code.

**Precedent:** OBPI-0.9.0-05 REQs (pure-doc REQs in a Heavy-lane OBPI) use
`[doc]` prefix to route past the parity gate. OBPI-0.0.18-01 (doc-only)
completed its own Gate 2 with the explicit clause "Pure-documentation OBPI —
no `@covers` unit tests expected."

**Mechanical behavior:** `extract_reqs_from_brief()` at
`src/gzkit/traceability.py` detects the `[doc]` marker and sets
`kind=ReqKind.DOC`. `compute_coverage()` filters doc-kind REQs out of the
testable set unless `--include-doc` is passed. The gate then reports 0
uncovered.

**Alternative rejected:** Authoring a `tests/docs/test_runbook_sections.py`
grep test with `@covers` decorators. Rejected because (a) the brief's
Allowed Paths explicitly closes with "Nothing else" excluding `tests/`, and
(b) mkdocs-strict is already the mechanical gate for doc correctness and
will catch anchor-resolution drift. Adding a grep test would be surface
sprawl for no new coverage.

## Section content (to be written into runbook.md)

The new section sits immediately before `## Governance Planning Commands` at
line 525. Content spec (draft below; wording may tighten in the edit itself):

1. **One-paragraph framing** naming the decision question verbatim: *"Given a
   PRD and a Constitution, how do you decide which ADRs to write, what kind
   each one should be, and what to defer into the pool?"* First mention of
   each kind links to the concepts page: `[foundation](concepts/adr-taxonomy.md#foundation)`,
   `[feature](concepts/adr-taxonomy.md#feature)`, `[pool](concepts/adr-taxonomy.md#pool)`.
   Satisfies **REQ-01** and **REQ-06**.
2. **Heuristic subsection (`### Heuristic`)** — three-row decision table:
   foundation = "shapes what the app IS (invariant/identity-shaping
   semantic)"; feature = "ships a named capability to users"; pool = "noted
   but not yet committed." Points back to concepts page for the kind × lane
   orthogonality table. Satisfies **REQ-02**.
3. **Worked example subsection (`### Worked example: PRD-GZKIT-1.0.0`)** —
   takes three bullets from `docs/design/prd/PRD-GZKIT-1.0.0.md` Goals and
   walks each to its kind:
   - Lane model / Gate rails → **foundation** (ADR-0.0.9 state-doctrine)
   - `gz patch release --full` ceremony → **feature** (ADR-0.0.15)
   - AI-runtime foundations → **pool** (ADR-pool.ai-runtime-foundations)

   Each bullet names the rationale in one line. An operator unfamiliar with
   gzkit should be able to trace the decomposition from the example alone
   (brief's evidence requirement). Satisfies **REQ-03**.
4. **Anti-pattern subsection (`### Anti-pattern: foundation-first,
   features-on-top`)** — names the pattern directly, explains why it fails
   (foundation ADRs earn their place by being load-bearing for a feature or
   pool entry, not by establishing layers defensively). Satisfies **REQ-04**.
5. **Pool's role subsection (`### The pool's role`)** — quotes the decision
   statement "I can see the concern but I can't commit to it yet." Forward
   cross-reference to OBPI-0.0.18-03's pool curation policy as prose ("the
   forthcoming pool curation policy at `docs/governance/pool-curation.md`,
   authored in OBPI-0.0.18-03") — *prose only, no live link*, because
   OBPI-03 has not shipped and a live link would break mkdocs --strict.
   Satisfies **REQ-05**.

Total prose budget: ~400–500 words. Style matches the runbook's existing
tone (terse, cross-linked, no essay padding — see "Storage Tiers and
Recovery" at line 158 as the representative reference).

## Anchor-resolution risk (mkdocs --strict)

The concepts page has headings like `## Kind × lane orthogonality` — mkdocs
default slugify drops the `×` and produces `kind-lane-orthogonality`. I'll
link to `#the-three-kinds`, `#pool`, `#foundation`, `#feature`, and
`#worked-examples` (all confirmed by the exploration). Any `#kind-lane-*`
anchors used must be verified by running `mkdocs build --strict` before the
ceremony. If strict-build rejects an anchor, repair by pointing at a
stable heading instead of amending the concepts page (out of scope).

## Verification

| Check | Command | Expected |
|-------|---------|----------|
| mkdocs strict build passes | `uv run mkdocs build --strict` | Exit 0, no warnings |
| mkdocs under ARB (canonical receipt) | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | Receipt `arb-step-mkdocs-*` exit_status=0 |
| Lint | `uv run gz lint` | Clean |
| REQ parity | `uv run gz covers OBPI-0.0.18-02 --json` | `summary.uncovered_reqs == 0` after `[doc]` tagging |

No unit tests added; doc-only OBPI convention per OBPI-0.0.18-01 precedent.

## Reading test for the worked example

Per brief Evidence section: "Worked example as a standalone reading test
(operator unfamiliar with gzkit should be able to trace the PRD→ADR
decomposition from the example alone)." This is a self-review gate at
Stage 4 — the Normal-mode ceremony presents the rendered section and asks
the attester to confirm the example reads standalone.

## Stage sequence (post-plan-approval)

1. **Stage 1 (context load)**: plan-audit-receipt will be written on
   ExitPlanMode; lock claimed against `OBPI-0.0.18-02-runbook-prd-to-adr`.
2. **Stage 2 (implement)**: two atomic edits — brief `[doc]` tags, then
   runbook section insertion. Inline (no subagent dispatch warranted for a
   400-word doc edit).
3. **Stage 3 (verify)**: mkdocs --strict, lint, ARB-wrapped mkdocs for the
   canonical receipt, `gz covers` parity.
4. **Stage 4 (ceremony, Normal mode)**: present the rendered section + ARB
   receipts + REQ coverage table. Wait for operator attestation — this ADR
   is Foundation-kind, so Gate 5 walkthrough applies regardless of Lite lane.
5. **Stage 5 (sync)**: `gz obpi precomplete` → `gz obpi complete` with
   operator's attestation text → git-sync ×2 → reconcile → `gz adr status`.
