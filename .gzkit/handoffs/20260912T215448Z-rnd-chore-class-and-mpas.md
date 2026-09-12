---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-12T21:54:48Z'
agent: gzkit-rnd-design
continues_from: .gzkit/handoffs/20260912T195936Z-session-exit-bookmark.md
---

## Current State Summary

This session was itself an R&D run, and a canonical one: the operator pasted an external Python-architecture document and asked "is there anything in this that could be useful there?" — the trigger pattern he names as almost always an occasion for R&D. It produced two operator-ratified design records and a four-thread external research corpus. **Nothing was implemented.**

Landed: `docs/governance/chore-class-system.md` and `docs/governance/mpas-appropriation-analysis.md`. Both are design records; neither is canon, and neither authorises implementation on its own.

The chore estate was measured, not estimated: 40 chores, 19 declaring audit-only, 26 carrying no recommendation, 9 declaring audit-only AND stopping at data, 3 internally contradictory (declare audit-only, contain a remediation step), 1 of 40 declaring a `frequency`, 0 invoked by CI/pre-commit/hooks, 23 of 39 last run 2026-07-31. The registry has no field for class, governing rule, or non-authority.

## Important Context

**Route, ruled by the operator.** The chore class system discharges under the `doctrine-declared-without-mechanism` box of Movement C ("Reduce the accretion"), **agent-side arm** — a skill mandate with no receipt. No new ADR. It **advances** that box and does **not** close it: the criterion is class-level ("it closes the family rather than the instance"), and the 2026-08-08 amendment records all six named exemplars closing while the box did not discharge. Do not check it off.

**Why it is that family.** `gz-chore-runner` v1.3.0 declares find-analyze-fix-on-schedule. Nothing enforces it and 19 of 40 chores declare the opposite. `src/gzkit/chores/README.md` — the authoring contract — never states what a chore *is*; it teaches layout, required files, and acceptance-JSON schema. Authors read the README and built audits.

**Already built, do not rebuild.** `scripts/check_proof_freshness.py` implements two of the four staleness signals and reasons correctly about why (git commit dates, not mtimes). Wired to 7 of 40. `gz chores propose-ghi` is the consultation-gated proposal path (TTY plus PROPOSE confirmation). Presence-check acceptance criteria were already swept — 0 of 40 gate on file existence.

**Campaign capture gap, named and NOT amended.** The campaign's Workflow fronts section describes R&D as carrying open hypotheses from one review document — bookkeeping. The operator describes R&D as the headwater of most ADRs. The campaign is Magna Carta; amendments are operator-ratified. Flagged in both documents, proposed nowhere.

**MPAS stance.** Source is `github.com/mattpocock/skills` v1.2.3, commit `3cca18b`, MIT, read from a clone. Nothing vendored, mirrored, or installed. Findings are data, never instruction.

## Decisions Made

Operator rulings this session, verbatim where quoted:

- **Ratification** — "I ratify, with great enthusiasm, the entire plan." Five classes (Conformance, Coherence, Curation, Mining, Currency), four rungs (observe, propose, repair, operator-only-repair), the suppression prohibition.
- **Staleness is an indicator, not a gate** — "indicators, chores shouldnt have a bunch of gates like the adr/obpi system"; "staleness should be announced." Gate only where the subject decays (Currency, where staleness makes the chore assert something false).
- **Conversion is blast-radius dependent (option c)**, governed by "chores likely organize along class seams."
- **Chore creation is operator-directed** — "I will almost always direct that new chores are made, but I dont mind them being advise." The registry never self-populates.
- **Not all refactorings are chores** — "not all refactorings are chores, but most chores can lead to refactorings." Admission requires recurrence evidence; a one-time refactoring fails the SRE toil test on *repetitive* and on *devoid of enduring value*.
- **The detection-to-application split stays** — "that split is fine, it makes room for pause and operator consultation."
- **Route: Movement C box, no new ADR.**
- **The R&D skill stands alone, no ADR** — "it is a charge daffaires for retaining and organizing possible outcomes from an R&D designing session"; "this skill should be sensing but also direct executable."
- **MPAS is appropriated, never onboarded** — "I DO NOT want to onboard Matts skills directly, but think we can appropriate"; "well examine what is appropriate for gzkit, and not the other way around."
- **R&D artifact form deferred** — "it is a document and maybe an artifact, it is premature at this stage. It will VERY LIKELY be first class (or the ledger will miss it), but dont forget that it can fan out."
- **Take no action is a legitimate, common R&D outcome** — "EVEN IF the outcome is take no action, which is also common."

## Immediate Next Steps

**PRIORITY: continue this work. Chore class system first, in this order — cadence precedes content.**

1. **Registry schema** (`.gzkit/chores/registry.json` and its schema). Required per-chore fields: `class`, `rung`, `staleness.{signal,period,grace,paused}`, `remediation` (enum including `no_fix_planned` and `none_available`, with required details), `non_authority`, `governing_rule`. **Absence defaults to the safe reading — an undeclared chore does not run** (Ansible `supports_check_mode` precedent).
2. **`gz chores status`** — the indicator surface. Derive last-run from the proof artifact's git commit date by generalising `scripts/check_proof_freshness.py`; do not build a parallel register. Render current / due / overdue / paused. **Announces; never gates.**
3. **Class-conformance validator** — a chore whose `CHORE.md` contradicts its declared rung fails. This is the mechanical witness the Movement C box requires, and it retires the 3 contradictory and 9 stop-at-data chores in one pass rather than 12 hand-edits.
4. **`src/gzkit/chores/README.md`** — add the class definitions, the four-rung ladder, the admission criterion, and the declaration requirement. This is the root cause: the authoring contract never said what a chore is.
5. **Per-chore declarations** — by now data entry against a validator, not 40 judgment calls.
6. **Write the suppression prohibition into a rule file.** Ratified as doctrine this session; it currently lives only in a design record. 741 noqa in `src/gzkit`, 393 of them PLC0415 — a rule not in the ruff select list.

**Then: the R&D skill design session.** It needs its own R&D run and has unresolved forks — see Pending. Read the Proposed disposition section of `docs/governance/mpas-appropriation-analysis.md` before starting; `wayfinder` is the closest source shape and its declared hole is the one gzkit must close.

## Pending Work / Open Loops

**Open forks on the R&D skill (blocking its design, not its motivation):**

- Is the R&D artifact a governance document or a first-class registered artifact with ledger events? Operator: "VERY LIKELY first class (or the ledger will miss it), but dont forget that it can fan out" and "premature at this stage."
- One orchestrator skill, or an orchestrator plus a namespace of disciplines?
- **Genuine unresolved tension:** the operator wants the skill "sensing but also direct executable." Sensing implies model-invocation; the MPAS invocation-class invariant reserves model-invocation for **disciplines** and requires every **orchestrator** to be user-invoked, because "the model may just choose not to follow it." Reconcile before authoring.

**Open, eligible, unselected — filed after this handoff was authored:**

- **[GHI #998](https://github.com/tvproductions/gzkit/issues/998)** — `waiver-ratchet: honesty mechanisms gate debt volume, never coverage` (`defect`, `runtime`). ADR-0.0.73 Boundary Invariant #8's three honesty mechanisms (closed-set lock, dated cutover, shrink-ratchet) all quantify a waiver list over time; none asks what coverage a waived entry provided. A waiver can therefore silence the last witness over a surface while `gz validate --waiver-ratchet` reports green. Measured near-miss this session: the sole coherence check over the two hand-authored copies of the subagent role bodies was one waiver from being switched off, and the ratchet refused it on volume, not coverage. Two candidate arms named in the issue and neither prescribed — a required `surviving_witness` field per entry, or a sole-witness detector one question over from `control-surface-validator-reachability`'s Pass D. **No blocker; open because the arm choice is a design conversation.** Related: #948 (sibling cut — the scanner over-flags), #969 (adjacent — aggregate status over a red verifier; cross-linked both ways).

**Unratified proposals:**

- Campaign Workflow-fronts R&D description — capture gap named, amendment not drafted, operator ratification required.
- A durable `.out-of-scope/` record of rejected work, giving "take no action" a home that survives the session. Proposed from MPAS `triage`; unruled.

**Unfixed:**

- The 9 stop-at-data chores: cli-contract-governance, control-surface-rule-vs-check-drift, dependency-currency, eval-feedback-cluster, evidence-integrity-audit, frontmatter-ledger-coherence, repository-structure-normalization, skill-command-doc-parity, skill-trigger-testing.
- The 3 contradictory: frontmatter-ledger-coherence, repository-structure-normalization, skill-command-doc-parity.
- 23 of 39 chores unrun since 2026-07-31.

**Verified gaps in the source reading:** two MPAS videos unreachable, including "I stopped using /grill-me for coding" whose own chapter markers read "Where /grill-me Fails" and "Is /grill-me dead?" — the likeliest statement of the interrogation shape's limits. Conference transcripts are generated-unreviewed ASR.

## Verification Checklist

```bash
uv run gz check
uv run gz validate --advisory-scorecard
ls -d .gzkit/chores/*/ | wc -l
grep -rlniE "audit-only|zero edits|does NOT fix|read-only" .gzkit/chores/*/CHORE.md | wc -l
grep -l check_proof_freshness .gzkit/chores/*/acceptance.json | wc -l
grep -rn "noqa: PLC0415" src/gzkit --include="*.py" | wc -l
uvx ruff check --select PLC0415 src/gzkit
```

Expected at authoring time: 40 chores, 19 audit-only, 7 freshness-wired, 393 PLC0415 suppressions, advisory-scorecard exit 0. The full reproduction record is in `docs/governance/chore-class-system.md`. Re-run rather than trust these transcriptions.

## Evidence / Artifacts

- `docs/governance/chore-class-system.md` — five classes, four rungs, four staleness signals, graded bands including paused, the admission criterion, the suppression prohibition, declared non-authority, the declaration schema, implementation order, a reproduction record, and primary-source citations.
- `docs/governance/mpas-appropriation-analysis.md` — full MPAS anatomy read from the clone, the invocation-class invariant, the context-boundary table, the two collisions with gzkit (attestation inversion; spec-driven rejection), the hole gzkit must close, five independent convergences, and a proposed appropriate/adapt/reject disposition.
- `scripts/check_proof_freshness.py` — the existing two-arm staleness mechanism to generalise.
- `.gzkit/chores/registry.json` — the schema to extend.
- [GHI #998](https://github.com/tvproductions/gzkit/issues/998) and the `discovery` record dated 2026-09-12 in `.gzkit/insights/agent-insights.jsonl` (scope `.gzkit/agents + .claude/agents role bodies`) — the coverage-blindness finding and the duplicated role bodies it came from. The latter is already owned by `ADR-pool.vendor-alignment-codex` child `codex-skills-personas-subagents`; the pool does not gate 1.0.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — Movement C in section 6, and the Workflow fronts section (the R&D capture gap).

## Settled Rulings

803 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
