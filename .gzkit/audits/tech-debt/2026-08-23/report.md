# gzkit Session-Handoff Audit Dossier

**Date:** 2026-08-23
**Re-based:** 2026-08-23 against `origin/main @ a50937481`
**Audience:** gzkit operator and gzkit agents
**Posture:** External diagnostic input; not canon, not a ledger event, and not
implementation authority

## Re-base provenance (read this first)

The original dossier was produced in a **local clone stranded seven days behind
`origin/main`**. That clone had missed a whole-history `filter-repo` author
rewrite (the `g0` authorship directive — root trees byte-identical, only author
identity changed), so `git merge-base` returned nothing and the working tree sat
at 2026-08-16 while origin carried work through 2026-08-23.

Every line number in the first edition therefore pointed at a superseded tree,
and the audit was blind to seven days of repair. This edition re-verifies all
twelve findings against current main and records, per finding, an
`original_location` / `original_severity` / `original_route` alongside the
re-based verdict in [`findings.json`](findings.json).

**What the re-base changed:**

| Change | Finding |
|---|---|
| One Critical **partially resolved upstream**, downgraded to High | retired resume-gate doctrine |
| One Medium **raised to High** on repo-specific blast radius | secret screening |
| Six findings **re-routed** off pool intake - two to a feature-ADR re-home, two to GHIs, one to an already-open GHI | see § Routing correction |
| Five **open GHIs** on this surface the first edition never saw | see § Open GHI queue |
| Two findings **narrowed** — one arm each did not survive verification | resume-gate; documentation generations |
| Ten findings **confirmed unchanged in substance** | — |

No finding was invented and none was withdrawn outright.

## Executive verdict

gzkit is the strongest complete repository-governed handoff system examined in
this review. That conclusion survives a confirmation-bias check against Matt
Pocock's handoff, Claude Code and Cursor memory, Aider's repository map, Cline's
Memory Bank, LangGraph checkpointing, current Superpowers proposals, and the
Handoff Debt research. It also survives the re-base: nothing in the seven days
of upstream work weakened the architecture, and one Critical was already being
repaired.

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

The re-base sharpened that thesis rather than softening it. The single best
piece of evidence is now one file disagreeing with itself: `parser_handoff.py`
line 35 says the resume gate "gates nothing — retired 2026-08-15", and line 86
tells the operator that "only proceed lifts the gate."

## Reproducible evidence

- Scope: [`scope.txt`](scope.txt)
- Focused verification and corpus results:
  [`probes/verification.txt`](probes/verification.txt)
- Re-base verification against current main:
  [`probes/rebase-verification.txt`](probes/rebase-verification.txt)
- Line-grounded local evidence:
  [`probes/surface-evidence.txt`](probes/surface-evidence.txt)
- Comparative primary sources:
  [`probes/comparative-sources.md`](probes/comparative-sources.md)
- Machine-readable findings: [`findings.json`](findings.json)

Fresh observations, re-measured on current main:

- **246 focused handoff tests passed** in 8.081 seconds. The first edition
  recorded 234 against the stale tree; the twelve added tests arrived with the
  upstream repair work.
- The 30-day archive dry run **would move 11 entries while protecting 87 by lock
  and 111 by chain participation** — byte-identical to the first edition. That
  finding is stable across the re-base.

Passing tests and corpus validation mean these findings are predominantly
uncovered semantic or contract gaps, not presently failing regression cases.

## Finding summary

| Severity | Status | Finding | Primary surface | Recommended route |
|---|---|---|---|---|
| Critical | Confirmed | RESUME contract is broader than the mechanized assessment | `src/gzkit/handoff_api.py:1103` | Re-home ADR-0.38.0 |
| Critical | Confirmed | CREATE can overwrite a deterministic historical path | `src/gzkit/handoff_api.py:960` | Single GHI candidate |
| High | **Narrowed** | Retired resume-gate doctrine survives in CLI help and docs | `src/gzkit/cli/parser_handoff.py:86` | `skill-command-doc-parity` chore |
| High | Confirmed | Runtime staleness is time-only and treats unknown as fresh | `src/gzkit/handoff_api.py:833` | Re-home ADR-0.38.0 |
| High | **Narrowed** | Multiple generations of storage/schema doctrine coexist | `docs/governance/GovZero/session-handoff-schema.md:189` | `skill-command-doc-parity` chore |
| High | Confirmed | Lineage errors are silently skipped or collapsed | `src/gzkit/handoff_api.py:484` | **Existing GHI #870** |
| High | Confirmed | Session-entry semantics differ by harness | `src/gzkit/session_start.py:1` | Pool via `pool-triage` |
| High | Confirmed | Required identity strings may be empty | `src/gzkit/handoff_api.py:880` | New GHI (cross-ref #813) |
| High | Confirmed | RESUME does not project the bearing of prior state | `src/gzkit/handoff_api.py:222` | Pool via `pool-triage` |
| High | Confirmed | Skill title and version metadata disagree | `.gzkit/skills/gz-session-handoff/SKILL.md:8` | `skill-authoring-quality` chore |
| High | **Raised** | Secret screening is narrower than a general guarantee | `src/gzkit/handoff_validation.py:124` | `skill-authoring-quality` chore |
| Medium | Unchanged | Conservative protections make most old entries ineligible for archive | archive dry run | Deliberate tradeoff; clarify or design separately |

**Counts (re-based):** Critical: 2 | High: 9 | Medium: 1 | Low: 0 | Total: 12
**Counts (first edition):** Critical: 3 | High: 7 | Medium: 2 | Low: 0 | Total: 12

## Routing correction (re-base)

The first edition routed **six of twelve findings to `pool-triage`** — design
intake. That is wrong for five of them, but so was this edition's first attempt
to fix it. Both errors are recorded here, because the second one is instructive.

### Why pool intake is wrong

`AGENTS.md` § Operator Doctrine, verbatim:

> "discovering that more is needed to fulfill the intent of a feature is not an
> enhancement, it is a correction." … routed as corrective work under the owning
> ADR, **never a fresh pool ADR, new-design ceremony, or "enhancement"**.

The declared intent exists and is explicit.
`ADR-0.0.65-handoff-system-consolidation` line 88 declares that the API wraps
`handoff_validation.py` "so handoff authoring routes through the validation
gate", and OBPI-0.0.65-02 names `resume_handoff` among the functions it ships.
`validate_handoff_document` is reachable from exactly one call site — inside
`create_handoff`. The intent test fails, so the work is corrective.

### Why "correction under ADR-0.0.65" is ALSO wrong

`ADR-0.0.65` is **status Validated**. A settled operator ruling in the carried
corpus governs residual scope on a closed ADR, verbatim:

> "Residual scope from a Validated ADR is RE-HOMED to a feature ADR, never
> appended to the closed one; appending would drag it back to Pending and
> falsify an honest attestation. Precedent: ADR-0.35.0 re-homing ADR-0.0.37's
> composition engine."

Foundation is sealed (`ADR-0.34.0`), so the home must be a **feature** ADR. No
in-flight feature ADR fits — 0.35.0 is the canon corpus, 0.36.0 the cross-family
critic, 0.37.0 the airlock. The next free slot is **0.38.0**.

### Why most of these still are not ADR work

Operator Doctrine again, verbatim: *"GHIs are AUTHORIZED for direct repair,
always … the GHI is the work order and the receipt"* and *"Never spin up an ADR
or OBPI merely to discharge a GHI."* Applying the `AGENTS.md` § Defect-fix
routing thresholds finding-by-finding leaves only two that genuinely need an ADR
home — the two that change a published runtime contract.

### Corrected routes

| Finding | Route | Why |
|---|---|---|
| RESUME contract not mechanized | **re-home ADR-0.38.0** | Changes the resume-path contract and `ResumeResult` shape |
| Time-only staleness | **re-home ADR-0.38.0** | Adds `UNVERIFIED` to a published enum; crosses into orientation |
| Lineage errors collapsed | **existing GHI #870** | Already filed — see § Open GHI queue |
| Empty identity fields | **new GHI**, cross-ref #813 | Single module, inside defect-fix thresholds |
| Dual session-entry semantics | Pool (unchanged) | Genuinely new; rendering half overlaps #870 |
| Bearing projection | Pool (unchanged) | Genuinely new; needs the advisory-boundary ruling |

## Open GHI queue the first edition could not see

The first edition's scheduling packet reads as if this surface had no open issue
queue. It has five, and the audit's stale clone predated four of them:

| GHI | Title | Relation to this dossier |
|---|---|---|
| **#870** | `continues_from` is protected from archival but never traversed on resume | **Filed 2026-08-23T15:42Z, the same day as this audit.** Covers the rendering arm of the lineage finding; this dossier adds the error-swallowing arm |
| **#813** | no authorship event, so 387 documents have zero Layer-2 provenance | Same identity surface as the empty-identity-fields finding; distinct defect |
| **#767** | frontmatter carries no transcript reference | **Not surfaced by this audit at all** — a coverage gap |
| **#766** | session-exit floor bookmark emits constants, so it informs nothing | **Not surfaced by this audit at all** — a coverage gap, and directly relevant: the register is accumulating these bookmarks |
| **#851** | session-green-gate delivery witness covers 1 of 4 declared hook types | Adjacent session-lifecycle surface |

**Triage this queue before opening ADR-0.38.0.** Two of the twelve findings
resolve into it, and two open GHIs (#766, #767) name handoff defects this audit
did not find — which is itself a finding about the audit's coverage.

## Critical findings

### Critical — RESUME does not mechanize its full published contract

**Status:** Confirmed on current main. Re-routed.

**Evidence**

> `resume_handoff` (`handoff_api.py:1103`) selects, reads, age-classifies,
> chains, and extracts content. `validate_handoff_document` is reachable at
> exactly ONE call site — `handoff_api.py:945`, inside `create_handoff` — so
> RESUME never validates the document it loads. Branch reconciliation is absent
> entirely: no `recorded_branch` / `current_branch` comparison exists anywhere
> in `handoff_api.py` or `session_start.py`.

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

**Route:** correction under `ADR-0.0.65`. See § Routing correction. The Pool
records remain the right home for the *bearing* design, not for the unmet
validation contract.

### Critical — CREATE can overwrite append-only history

**Status:** Confirmed on current main, and stronger than first stated.

**Evidence**

> `create_handoff` derives `<timestamp>-<slug>.md` and calls
> `path.write_text(document, ...)` at `handoff_api.py:960` without refusing an
> existing destination. The same module already checks `Path.exists()` at lines
> 864 and 867 inside `resolve_continues_from`.

**Why this matters**

The register is historical evidence. Same timestamp plus slug can replace a
prior handoff silently, whereas archive code already treats collisions as an
integrity concern. The re-base strengthens this: existence-checking is not a
missing concept in this module, it is an inconsistently applied one.

**Recommended fix**

Refuse an existing destination before writing, constrain the slug to its safe
canonical form, and add API and CLI behavior tests proving the original bytes
remain unchanged after a collision attempt.

**Route:** the dossier's one GHI candidate; see § Scheduling packet.

## High findings

### Retired resume-gate doctrine survives in CLI help and docs — NARROWED

**Was Critical; now High.** The session-entry arm was **resolved upstream** by
`6a301e03f` (GHI #805, 2026-08-20) — the strings the first edition cited at
`session_start.py:22` are absent from current main. The dossier could not have
known: that commit landed four days after the stale clone's last sync.

Eight live sites survive, and the sharpest is a single file contradicting
itself 51 lines apart:

- `src/gzkit/cli/parser_handoff.py:35` — "ADVISES and gates nothing — the resume
  gate was retired 2026-08-15"
- `src/gzkit/cli/parser_handoff.py:86` — `help="Transit decision; only proceed
  lifts the gate (default: proceed)"`

Line 86 is published external contract: it is what `gz handoff decide --help`
prints. The same claim survives at `events.py:963`, `session_start.py:22`
(docstring), `handoff_api.py:1134`, `handoff_resume_gate.py:145`,
`docs/user/manpages/handoff-decide.md:55`,
`docs/user/manpages/handoff-authorize.md:20`, and `docs/user/runbook.md:776`.

Remove every gate-armed, gate-lifted, and mutation-refusal claim from active
surfaces. Add a semantic parity witness that fails if retired gate language
returns to current skill/help/session-entry/manpage scope. This is a coupled-
surface coherence failure under `AGENTS.md` Invariant 1a.

### Time-only freshness conflicts with multi-factor doctrine

`_classify_staleness` (`handoff_api.py:833`) computes age only and buckets it at
24h / 72h / 7d, while governance and the skill asset describe commits, changed
files, and branch divergence. `StalenessLevel` (line 78) has no `UNVERIFIED`
member, so absent evidence cannot be represented and anything under 24h reads
`FRESH` regardless of what changed. The richer orientation account already
computes some of this information separately. Merge them into one assessment.
Unknown evidence must remain `UNVERIFIED`, never `Fresh`.

### Current documentation contains several architectural generations — NARROWED

`docs/governance/GovZero/session-handoff-schema.md:189` still states that
"Handoff documents are stored per-ADR in the ADR package directory" — retired
architecture on a live governance page; the actual store is `.gzkit/handoffs/`.

The **removed-test-module arm did not survive verification and is withdrawn.**
All four surviving citation sites are sealed or correct: `ADR-0.0.65` and
`OBPI-0.0.65-02` are the record of the change that removed the module;
`ADR-pool.handoff-system-consolidation.md` is status `Superseded`; and
`OBPI-0.11.0-02` (`attested_completed`) line 253 states the module "does not
exist" — it documents the absence correctly. The first edition treated these as
current-contract drift; none is live contract.

### Lineage doctrine is stronger than lineage validation

The chain walk (`handoff_api.py:484`) swallows every failure with three bare
`continue` arms, and `resolve_continues_from` (line 844) deliberately returns an
unresolved sibling path rather than raising — so a dangling parent is
indistinguishable from a genuine chain root. No dangling pointer, cycle, or
truncation is ever reported. RESUME should report them rather than silently skip
or collapse them. If historical mutation matters, record a predecessor revision
or digest rather than relying only on path identity.

### Session entry has two overlapping semantic paths

**Reproduced live during the re-base session:** the agent received two
independently-authored session-entry texts — the `scripts/session_orientation.py`
account plus a separate `session_start.py` "Resumed handoff" advisement block.
Neither consumes a shared assessment; each selects and interprets state
independently. Make both consume the same structured assessment. Harness
adapters may format differently but should not select or interpret state
independently.

### Identity fields are required in prose but weak in the model

`create_handoff` takes `branch: str, agent: str` (`handoff_api.py:880-881`) with
no `min_length` and no strip check, and `HandoffRecord.agent` is
`str | None = None` (line 222). Require stripped non-empty branch and agent
values. Reuse the canonical session identifier model instead of maintaining a
looser handoff-only interpretation.

### The missing output is bearing, not more summary

The incoming session needs an evidence-backed choice among:

- `CONTINUE` — objective and next step remain valid;
- `REVISE` — objective remains live but the route changed;
- `ABANDON` — current authority completed, superseded, or rejected it;
- `VERIFY` — a load-bearing contradiction or unknown must be resolved first.

Each result should finish with: `Start here because: <evidence-backed reason>`.

**Operator ruling required before design.** This is advice and must never become
a resurrected resume gate — and the gate was retired 2026-08-15 on an operator
ruling, verbatim: *"the handoff should be an advisor, not a gate-keeping nanny."*
A four-verdict projection sits one inch from that boundary. Fix where advisory
ends before designing it, not after.

### Skill identity metadata is incoherent

`.gzkit/skills/gz-session-handoff/SKILL.md` carries three identities in one
file: `metadata.skill-version: "7.1.0"` (line 8),
`govzero-framework-version: "v6"` (line 9), and the H1 title
`# gz-session-handoff (v6.21.0)` (line 19). The first edition recorded `7.0.0` —
the version moved during the seven-day gap, but the incoherence did not close.
Choose one identity rule, reconcile the canonical skill, and run
`gz agent sync control-surfaces`. Route through `skill-authoring-quality` and
the existing `ADR-pool.skill-version-review-coupling.md` prior art.

### Secret detection needs an honest boundary — RAISED TO HIGH

`_SECRET_RE` (`handoff_validation.py:124`) is **broader than the first edition
implied** — a correction made during the re-base. It covers `password=`,
`secret=`, `token=`, and `api_key=` assignment forms, plus `Bearer <token>`,
`PRIVATE KEY`, and two provider shapes (`sk-[A-Za-z0-9]{20,}`,
`ghp_[A-Za-z0-9]{20,}`).

What it does not cover: colon forms (`token: value` — the shape handoff
frontmatter itself uses), credential URLs (`https://user:pass@host`), any
entropy test, and every provider outside OpenAI and GitHub PAT — AWS, Anthropic,
Slack, GCP service-account JSON. So the finding is an honest-boundary problem,
not an absence of screening.

**Severity raised from Medium — on blast radius, not coverage breadth.**
Handoffs are *committed to the repository*, and `CLAUDE.md` records a 2026-04-19
leak whose recovery cost a `filter-repo` rewrite plus force-push. A screening gap
on a repo-bound artifact with that recovery cost is not a Medium in this repo,
even though the regex is wider than first described. Either call it
common-pattern screening everywhere
or adopt a governed detector with explicit coverage and false-positive policy.
Do not claim that regex success proves a handoff has no secrets.

## Medium findings and deliberate tradeoffs

### Archive retention is conservative to the point of limited compaction

Re-measured on current main and **unchanged**: 11 movable, 87 locked, 111
chained. This is not evidence of incorrect deletion behavior. It shows that the
current feature is best described as archiving isolated eligible entries. If
whole closed histories must compact, design an atomic chain move with stable
identifiers and pointer repair; do not weaken current protections piecemeal.

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

Run `skill-command-doc-parity` on the handoff CLI help, manpages, runbook, and
governance schema page. Retire the eight surviving gate-language sites — starting
with `parser_handoff.py:86`, which is published CLI contract — and correct the
per-ADR storage claim at `session-handoff-schema.md:189`. Run
`skill-authoring-quality` to repair the version/title identity and tighten the
secret-screening promise.

These are corrections under already-settled intent; they do not require a new
feature ADR.

### Single GHI candidate

**Title:** Refuse handoff CREATE collisions before writing append-only history

**Problem:** `create_handoff` writes a deterministic path with `write_text`
(`handoff_api.py:960`) and can replace an existing historical document, while
the same module already guards existence at lines 864 and 867.

**Acceptance:**

- Existing destination causes a diagnostic refusal and non-zero CLI result.
- Original bytes remain unchanged.
- A safe slug contract rejects noncanonical separators and traversal-like
  input before path construction.
- API and CLI behavior tests cover collision and safe-slug refusal.
- Current successful CREATE behavior remains unchanged for a free destination.

**Step 0 prior-art search: RUN, and it clears.** Searched `create_handoff`,
`handoff collision`, `handoff overwrite`, `append-only handoff` across all issue
states. The nearest neighbour is **#859** (CLOSED 2026-08-22) — "a REFUSED create
still writes to the append-only rulings store" — which is the store-ordering
defect already fixed at `handoff_api.py:951-953`, not destination collision.
**No duplicate exists.** File it.

### Second GHI candidate

**Title:** Reject empty branch and agent identity on handoff CREATE

`create_handoff` takes `branch: str, agent: str` with no `min_length` and no
strip check. Single module, inside the defect-fix thresholds, so it routes to
direct fix. Cross-reference open **#813** before filing — same identity surface,
distinct defect — and decide whether to fold or file adjacent.

### Fold into existing GHI #870

The lineage finding's error-swallowing arm belongs in #870, which already owns
the traversal arm. Do not open anything new for it.

### Re-home to feature ADR-0.38.0

Only two findings need an ADR home (see § Routing correction): RESUME contract
not mechanized, and time-only staleness. Both change a published runtime
contract, and both are residual scope from a Validated ADR that may never be
appended to. The design nucleus is one shared `SessionEntryAssessment` or
equivalent projection owning validation, multi-factor drift, lineage findings,
claim verdicts, and next-step preconditions — and it is the natural absorber for
the two Pool records if the operator promotes them.

**Sequencing caveat.** The active campaign is Magna Carta and its topmost item is
Movement B (airlock calibration before widening). Handoff work is not campaign
work. ADR-0.38.0 is a real ceremony cost and should be opened only on an operator
decision to spend it — the four chore and GHI routes below discharge most of this
dossier without it.

### Existing Pool design intake

Run `pool-triage` over these existing records rather than creating duplicates:

- `ADR-pool.pause-resume-handoff-runtime.md` — dual session-entry semantics; bearing
- `ADR-pool.artifact-staleness-propagation.md`
- `ADR-pool.skill-version-review-coupling.md`
- `ADR-pool.cross-session-search.md`
- `ADR-pool.cross-session-history-query.md`

Bearing needs the operator's advisory-boundary ruling before it enters design.

### Later retention decision

Decide explicitly whether archive means isolated-entry retention or atomic
closed-chain compaction. Until then, preserve the conservative behavior and
document its practical eligibility limits.

## Final recommendation

1. **Triage the five open handoff GHIs first** (#870, #813, #767, #766, #851).
   Two findings resolve into that queue, and two of those GHIs name defects this
   audit did not find.
2. **Run the correction sweep** — `skill-command-doc-parity` and
   `skill-authoring-quality`. Incoming agents still receive false doctrine from
   published CLI help (`parser_handoff.py:86`).
3. **File the two GHIs** — CREATE collision (Step 0 run and clear) and empty
   identity fields (cross-ref #813).
4. **Only then** decide whether to spend ADR-0.38.0 on the two contract gaps that
   genuinely need an ADR home.

That order repairs trust immediately, discharges most of the dossier through
GHIs and chores, and does not let an architecture effort delay a small
historical-integrity defect — or duplicate work already filed.

**Standing re-base lesson.** This dossier was authored against a tree seven days
stale and did not know it. One of its three Criticals was already being repaired
upstream while it was being written. Any audit that reads a working tree should
state the revision it verified against — this edition names
`origin/main @ a50937481` in every finding record — and should re-verify before
its findings are scheduled.
