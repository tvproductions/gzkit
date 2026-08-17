---
id: ADR-pool.skill-efficacy-measurement
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.skill-efficacy-measurement: Skill Efficacy Measurement and Canon Provenance

## Status

Pool

## Intent

**Skills shape agent behavior and nothing measures whether they still earn it.**
Operator framing 2026-08-17, verbatim: *"when we have poor outcomes, we need to
audit our skills. do we have a chore that reviews the efficacy of skills? perhaps
look at arb, insights, and the ledger to see if a skill is still pulling its
weight?"*

Four skill-adjacent chores exist and every one is **static** — measured
2026-08-17:

| Chore | Question it asks | Reads ARB / insights / ledger? |
|---|---|---|
| `skill-authoring-quality` | is it written well? | no |
| `skill-command-doc-parity` | do its docs match the commands? | no |
| `skill-trigger-testing` | does it fire and produce output? | no |
| `control-surface-skill-rule-reachability` | is it reachable from a rule? | no |

A skill can therefore be well-authored, documented, reachable, trigger cleanly,
and be worthless — and nothing observes it. That is the
doctrine-declared-without-mechanism family (campaign Movement C) applied to the
skill corpus: 70 skills load into agent turns on the claim that they improve
outcomes, and the claim has no witness.

**Second, coupled gap: canon provenance.** Corpus entries shape every agent turn
and 55% carry no attribution. Measured 2026-08-17 against
`.gzkit/corpus/AGENTS.md.jsonl`:

```
entries: 65 | default-constant origin: 36 (55%)
   36  cli:content-remember     <- names the TOOL, not the author
    2  operator ruling 2026-08-17 (session 2ad6f031)
    ...
has witness field set: 0 of 65
```

`--origin` is optional and its default names the tool. The loss is
**directional**, not random: entries with real provenance are almost all ones a
human ruling forced, so the default systematically hides agent-authored canon
among operator-authored canon. Operator framing: *"I think we'd want to at least
'git blame' record remember. these are consequential entries because they shape
agent behavior."*

The two halves are one ADR because they share a subject — **behavior-shaping
surfaces with no accountability channel** — and one substrate.

## Decision

*(Pool item — this states the shape well enough to promote against, not the
final design. Promotion authors the Decision proper.)*

1. **BUILD ON `gzkit.efficacy`, DO NOT AUTHOR A SECOND MEASUREMENT MODEL.**
   `src/gzkit/efficacy.py` already exists — *"measure whether a capability
   actually reaches its input"* — with `StoreCoverage(present, eligible,
   covered, truncated)` and a `reach` fraction that refuses to be read without
   its denominator. It has exactly one consumer today
   (`src/gzkit/arb/coverage.py`). It is the substrate; a parallel model would be
   the differing-semantics-under-a-shared-name drift
   `.claude/rules/hexagonal-architecture.md` operative rule 8 forbids.

2. **EFFICACY IS MEASURED FROM RUNTIME EVIDENCE, NEVER FROM THE SKILL'S OWN
   TEXT.** Three stores, three questions: the **ledger** (was it invoked, and
   when last), **insights** (did invocations precede `improvement` records —
   i.e. did the operator have to course-correct through it), and **ARB** (did
   its steps emit receipts, or does it claim work it never witnessed). A skill
   scoring well on authoring quality and zero on all three is the finding this
   ADR exists to surface.

3. **DIAGNOSIS ONLY; NEVER AUTONOMOUS RETIREMENT.** The deliverable is a ranked
   report the operator adjudicates. Precedent: `ADR-0.0.57`'s triage skill
   (*"cross-references insights + GHIs + invariants … diagnosis only, ephemeral
   ranked report"*) is the structural sibling — same shape, different store.

4. **PROVENANCE ON CAPTURE CONVERGES WITH THE 2026-08-17 ATTESTATION RULING.**
   `.gzkit/rules/agents-md-map-doctrine.md` § Attestation granularity already
   rules that adding and removing corpus entries are attested. **Attestation IS
   the git-blame record**, so `--attestor` on `remember`/`retire` closes both
   gaps with one change. It must be **recorded provenance, never a blocking
   gate** — `ADR-0.35.0` § Decision 7 (*"Capture must never be blocked"*)
   stands.

5. **THE 36 UNATTRIBUTED ENTRIES ARE A DECLARED DECISION, NEVER A GUESS.**
   Either backfilled from `git log -L` over the JSONL, or declared
   permanently-unknown in a dated record. Inferring an author from a commit that
   merely *touched* the line would manufacture provenance, which is worse than
   admitting its absence.

6. **DELIVERED AS A SKILL UNDER AN ADR — the ordinary path here.** Measured
   2026-08-17: **117** OBPI briefs carry `.gzkit/skills/` in their allowlist and
   **38 of 70** skills cite a parent ADR. Worked chain: `ADR-0.0.15` declares
   *"Ceremony skill (`gz-patch-release`)"* as a checklist item, decomposes it to
   `OBPI-0.0.15-05`, and the built skill's frontmatter cites the ADR back.

## Alternatives Considered

**A — A chore rather than a skill.** Rejected as the primary shape, not as a
component. A chore is a scheduled maintenance procedure; the operator's framing
is *"when we have poor outcomes, we need to audit our skills"* — reactive and
diagnostic, which is the skill shape (`ADR-0.0.57` precedent). A chore wrapper
for cadence remains available and is cheap to add on top.

**B — Extend `skill-authoring-quality` in place.** Rejected: it measures the
artifact, this measures the artifact's *effect*. Folding a runtime-evidence
reader into a static linter would give one surface two subjects — the exact
collision this session spent its length untangling on `Gate 5` and `handoff`.

**C — Invocation count alone as the metric.** Rejected as the *sole* metric. A
rarely-invoked skill may be load-bearing at a rare moment (release ceremony,
incident repair), and a frequently-invoked one may be actively harmful if its
invocations correlate with course-corrections. Frequency without the insights
axis reproduces the reach-without-denominator error `efficacy.py` was written to
refuse.

**D — Split provenance into its own ADR.** Deliberately open. The halves are
separable and the provenance half is small enough to route as a GHI direct fix
under the 2026-08-17 attestation ruling. Kept together here because they share
the accountability subject; **split at promotion if the provenance half lands
first as a GHI.**

**E — Autonomous retirement of low-scoring skills.** Rejected outright. Skill
retirement is `delete-on-retire` across five surfaces
(`.gzkit/rules/skill-surface-sync.md` § Retirement policy) and irreversible in
one pass. A measurement surface that also acts is how a miscalibrated metric
becomes destructive.



## Notes

**Sequencing (operator ruling 2026-08-17, verbatim: *"pool the skill-efficacy
ADR, then get back to 0.35.0"*).** Pooled deliberately rather than pulled. ADR
order is absolute (*"i will NOT go out of adr order, whatsoever"*) and three
feature ADRs are queued: `ADR-0.35.0` in flight at 0/10, then `ADR-0.36.0`, then
`ADR-0.37.0`. This is not a deferral of merit — it is the queue.

**Origin.** Surfaced in the 2026-08-17 session that recovered the root-contract
doctrine (`--vendor=root`, `OBPI-0.35.0-09`). The operator's question followed
three findings that shared one shape — a declared property with no witness — and
asked the generalizing question: *"when we have poor outcomes, we need to audit
our skills."* The session's own worked example is the evidence: a chore's § 5a
cited the wrong authority for months and the failure surfaced only because a
human read it aloud.

**Unclaimed residual, stated rather than implied.** Measured 2026-08-17: **38 of
70** skills cite a parent ADR, so roughly half the skill corpus has no declared
parent. Whether those are legitimately parentless (scaffolded, vendor-mirrored)
or merely unattributed is **not investigated** — recorded here as a question, not
a finding, so promotion re-measures rather than inherits the number.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
