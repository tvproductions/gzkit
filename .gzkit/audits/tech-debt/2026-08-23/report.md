# gzkit Session-Handoff Audit Dossier

**Date:** 2026-08-23
**Audience:** gzkit operator and gzkit agents
**Posture:** External diagnostic input; not canon, not a ledger event, and not
implementation authority

## Executive verdict

gzkit is the strongest complete repository-governed handoff system examined in
this review. That conclusion survives a confirmation-bias check against Matt
Pocock's handoff, Claude Code and Cursor memory, Aider's repository map, Cline's
Memory Bank, LangGraph checkpointing, current Superpowers proposals, and the
Handoff Debt research.

The qualification matters:

- LangGraph is stronger at exact transactional runtime checkpoints, pending
  writes, replay, and forks.
- Matt Pocock is stronger at minimal portability, tailoring to the incoming
  session's purpose, and choosing the right mechanism at a phase boundary.
- Claude Code and Cursor are stronger at automatic loading or extraction.
- Aider is stronger at automatic code-topology reconstruction.

Those are narrower advantages. None of the examined alternatives combines
gzkit's durable register, lineage, issue citations, decision attribution,
settled-ruling carry-forward, exit bookmarks, orientation account, archive
protections, and focused regression suite.

The audit found no collapsing foundation. It found a mature system whose
principal risk is **semantic divergence among individually plausible
surfaces**. gzkit validates document shape strongly; it is currently less able
to prove that skill doctrine, CLI help, session-entry rendering, governance
pages, and runtime interpretation still mean the same thing.

## Reproducible evidence

- Scope: [`scope.txt`](scope.txt)
- Focused verification and corpus results:
  [`probes/verification.txt`](probes/verification.txt)
- Line-grounded local evidence:
  [`probes/surface-evidence.txt`](probes/surface-evidence.txt)
- Comparative primary sources:
  [`probes/comparative-sources.md`](probes/comparative-sources.md)
- Machine-readable findings: [`findings.json`](findings.json)

Fresh observations:

- **234 focused handoff tests passed** in 6.314 seconds.
- The current corpus audit passed: all post-cutover register entries are valid;
  14 legacy entries are grandfathered and 4 hollow entries remain explicitly
  marked as not preserving context.
- The 30-day archive dry run would move 11 entries while protecting 87 by lock
  and 111 by chain participation.

Passing tests and corpus validation mean these findings are predominantly
uncovered semantic or contract gaps, not presently failing regression cases.

## Finding summary

| Severity | Finding | Primary surface | Recommended route |
|---|---|---|---|
| Critical | Retired resume gate still appears in live help and session entry | `src/gzkit/session_start.py:22` | `skill-command-doc-parity` chore |
| Critical | RESUME contract is broader than the mechanized assessment | `src/gzkit/handoff_api.py:953` | Existing handoff Pool design via `pool-triage` |
| Critical | CREATE can overwrite a deterministic historical path | `src/gzkit/handoff_api.py:810` | Single GHI candidate |
| High | Runtime staleness is time-only and treats unknown as fresh | `src/gzkit/handoff_api.py:693` | Existing handoff Pool design via `pool-triage` |
| High | Multiple generations of storage/schema doctrine coexist | `docs/user/skills/gz-session-handoff.md:37` | `skill-command-doc-parity` chore |
| High | Lineage errors are silently skipped or collapsed | `src/gzkit/handoff_api.py:704` | Existing handoff Pool design via `pool-triage` |
| High | Session-entry semantics differ by harness | `src/gzkit/session_start.py:1` | Existing handoff Pool design via `pool-triage` |
| High | Required identity strings may be empty | `src/gzkit/handoff_api.py:740` | Existing handoff Pool design via `pool-triage` |
| High | RESUME does not project the bearing of prior state | `src/gzkit/handoff_api.py:217` | Existing handoff Pool design via `pool-triage` |
| High | Skill title and version metadata disagree | `.gzkit/skills/gz-session-handoff/SKILL.md:8` | `skill-authoring-quality` chore |
| Medium | Conservative protections make most old entries ineligible for archive | archive dry run | Deliberate tradeoff; clarify or design separately |
| Medium | Secret screening is useful but narrower than a general guarantee | `src/gzkit/handoff_validation.py:124` | `skill-authoring-quality` chore |

**Counts:** Critical: 3 | High: 7 | Medium: 2 | Low: 0 | Total: 12

## Critical findings

### Critical — retired resume-gate doctrine remains live

**Evidence**

> `c772497c` retired the final enforcement arm, but session start, parser help,
> command copy, CLI output, and the manpage still say that only `proceed` lifts
> a gate that refuses mutations.

**Why this matters**

This is a coupled-surface coherence failure under `AGENTS.md` Invariant 1a and
a published external-contract defect. It can orient an incoming agent to a
false operational state before work begins.

**Recommended fix**

Remove every gate-armed, gate-lifted, and mutation-refusal claim from active
surfaces. Add a semantic parity witness that fails if retired gate language
returns to current skill/help/session-entry/manpage scope.

**Route:** `skill-command-doc-parity` chore. This finding already has a precise
bulk-remediation home and should not consume the one-GHI budget.

### Critical — RESUME does not mechanize its full published contract

**Evidence**

> `resume_handoff` selects, reads, age-classifies, chains, and extracts content,
> but does not return full-document validation, recorded-vs-current branch
> reconciliation, per-claim verdicts, or an overall bearing result.

**Why this matters**

The canonical skill describes RESUME as discovering, loading, validating, and
reconciling. A parseable malformed or stale handoff can therefore receive more
confidence than the doctrine intends. Session-start exception suppression can
also turn a bad document into absent advisement rather than an explicit finding.

**Recommended fix**

Create one structured session-entry assessment consumed by RESUME and every
harness renderer. It should validate the selected handoff, compare authorities,
classify claims as confirmed/drifted/unverified, assess next-step preconditions,
and render an advisory bearing.

**Route:** run `pool-triage` against
`ADR-pool.pause-resume-handoff-runtime.md` and
`ADR-pool.artifact-staleness-propagation.md`. The design opportunity is already
represented; do not file a duplicate GHI from this dossier.

### Critical — CREATE can overwrite append-only history

**Evidence**

> `create_handoff` derives `<timestamp>-<slug>.md` and calls `Path.write_text`
> without refusing an existing destination.

**Why this matters**

The register is historical evidence. Same timestamp plus slug can replace a
prior handoff silently, whereas archive code already treats collisions as an
integrity concern.

**Recommended fix**

Refuse an existing destination before writing, constrain the slug to its safe
canonical form, and add API and CLI behavior tests proving the original bytes
remain unchanged after a collision attempt.

**Route:** the dossier's one GHI candidate; see § Scheduling packet.

## High findings

### Time-only freshness conflicts with multi-factor doctrine

The runtime labels freshness from age while governance and the skill asset
describe commits, changed files, and branch divergence. The richer orientation
account already computes some of this information separately. Merge them into
one assessment. Unknown evidence must remain `UNVERIFIED`, never `Fresh`.

### Current documentation contains several architectural generations

User and GovZero pages still prescribe per-ADR handoff storage, omit current
modes, and cite removed test modules. These pages mix newer edits with retired
architecture, making them more misleading than a clearly archived historical
page. Route through `skill-command-doc-parity` and update or explicitly retire
every current-contract page in one coupled correction.

### Lineage doctrine is stronger than lineage validation

Predecessor resolution should be repository-contained and canonical-store
aware. RESUME should report dangling parents, cycles, and truncation rather
than silently skip or collapse them. If historical mutation matters, record a
predecessor revision or digest rather than relying only on path identity.

### Session entry has two overlapping semantic paths

Claude can receive both legacy advisement and the richer orientation account;
Codex primarily receives orientation. Make both consume the same structured
assessment. Harness adapters may format differently but should not select or
interpret state independently.

### Identity fields are required in prose but weak in the model

Require stripped non-empty branch and agent values. Reuse the canonical session
identifier model instead of maintaining a looser handoff-only interpretation.

### The missing output is bearing, not more summary

The incoming session needs an evidence-backed choice among:

- `CONTINUE` — objective and next step remain valid;
- `REVISE` — objective remains live but the route changed;
- `ABANDON` — current authority completed, superseded, or rejected it;
- `VERIFY` — a load-bearing contradiction or unknown must be resolved first.

Each result should finish with: `Start here because: <evidence-backed reason>`.
This is advice and must never become a resurrected resume gate.

### Skill identity metadata is incoherent

The active mirrors say `skill-version: 7.0.0`, framework `v6`, and title
`v6.20.0`. Choose one identity rule, reconcile the canonical skill, and run
`gz agent sync control-surfaces`. Route through `skill-authoring-quality` and
the existing `ADR-pool.skill-version-review-coupling.md` prior art.

## Medium findings and deliberate tradeoffs

### Archive retention is conservative to the point of limited compaction

The observed 11 movable / 87 locked / 111 chained split is not evidence of
incorrect deletion behavior. It shows that the current feature is best
described as archiving isolated eligible entries. If whole closed histories
must compact, design an atomic chain move with stable identifiers and pointer
repair; do not weaken current protections piecemeal.

### Secret detection needs an honest boundary

The regex catches common patterns but not every provider token, colon form,
credential URL, or high-entropy secret. Either call it common-pattern
screening everywhere or adopt a governed detector with explicit coverage and
false-positive policy. Do not claim that regex success proves a handoff has no
secrets.

## Advantages to import from other systems

gzkit should borrow narrowly without surrendering its stronger architecture:

1. **Incoming-purpose tailoring from Matt Pocock.** CREATE should ask what the
   next session is for and shape emphasis and suggested skills accordingly.
2. **Phase-boundary choice from Matt Pocock.** At a real boundary, decide among
   continue, clear, handoff, subagent, and compact. Handoff is not automatically
   the right answer.
3. **State/replay distinction from LangGraph.** Explicitly label a handoff as a
   human-readable advisory projection, not a transactional checkpoint.
4. **Automatic reconstruction where safe.** Reuse orientation's Git/ledger
   account and repository topology rather than requiring the outgoing agent to
   narrate derivable facts.
5. **Measure rediscovery debt.** Track repeated probes, contradicted decisions,
   and tokens/events to first productive action when evaluating future changes.

Do not import raw-transcript defaulting, passive unreviewed memory, a large
always-loaded Memory Bank, or harness-specific state as the only authority.

## Scheduling packet

### Immediate correction sweep

Run `skill-command-doc-parity` on the handoff skill, help, session-start, and
manpage surfaces. Retire the remaining gate language and reconcile old storage,
mode, and test-module documentation. Run `skill-authoring-quality` to repair the
version/title identity and tighten the secret-screening promise.

These are corrections under already-settled intent; they do not require a new
feature ADR.

### Single GHI candidate

**Title:** Refuse handoff CREATE collisions before writing append-only history

**Problem:** `create_handoff` writes a deterministic path with `write_text` and
can replace an existing historical document.

**Acceptance:**

- Existing destination causes a diagnostic refusal and non-zero CLI result.
- Original bytes remain unchanged.
- A safe slug contract rejects noncanonical separators and traversal-like
  input before path construction.
- API and CLI behavior tests cover collision and safe-slug refusal.
- Current successful CREATE behavior remains unchanged for a free destination.

Before filing, run `ghi-author` Step 0 prior-art search using `create_handoff`,
`collision`, `overwrite`, and `append-only`. This dossier does not file it.

### Existing Pool design intake

Run `pool-triage` over these existing records rather than creating duplicates:

- `ADR-pool.pause-resume-handoff-runtime.md`
- `ADR-pool.artifact-staleness-propagation.md`
- `ADR-pool.skill-version-review-coupling.md`
- `ADR-pool.cross-session-search.md`
- `ADR-pool.cross-session-history-query.md`

If the operator promotes the session-entry work, the design nucleus should be
one shared `SessionEntryAssessment` or equivalent projection. It should own
validation, multi-factor drift, lineage findings, claim verdicts, next-step
preconditions, and bearing. CREATE collision refusal remains a separate defect
fix and should not wait for that architecture.

### Later retention decision

Decide explicitly whether archive means isolated-entry retention or atomic
closed-chain compaction. Until then, preserve the conservative behavior and
document its practical eligibility limits.

## Final recommendation

Schedule the correction sweep first because incoming agents currently receive
false doctrine. File at most the one scoped CREATE-collision GHI after prior-art
search. Then use existing Pool records to design the unified session-entry
assessment. That order repairs trust immediately without letting a larger
architecture effort delay a small historical-integrity defect.
