---
id: ADR-pool.mechanism-objective-and-scope-record
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.mechanism-objective-and-scope-record: Mechanism Objective and Scope Record

## Status

Pool

## Intent

**Nothing in gzkit records what an enforcement mechanism is *for*, or how far it
*reaches*.** The consequence is that a mechanism with the wrong blast radius is
discovered by an adopter's broken build rather than by an audit.

GHI #727 is the design home for closing that gap. It is a **pool** ADR because
the central question is genuinely unsettled and needs an operator design
conversation — see § Decision, which records the fork rather than resolving it.

### The instance that surfaced it

GHI #607 shipped a fail-closed gate that broke an adopter's build for two
months. The root cause was not a bad rule. It was that **two validators enforced
the same rule with different scopes, and no surface in the repo made that
visible.**

Re-verified against the current tree (2026-08-04):

| | `audit_pydantic_models` | `audit_code_contract_mismatches` |
|---|---|---|
| Home | `governance/trust_audits/models.py` | `instruction_audit.py:251` |
| Engine | AST walk, per-class | regex, per-file (`:300`) |
| Root | `src/gzkit` (always) | `src/gzkit` (since #607; was `src/`) |
| Waiver affordance | `_DATACLASS_WAIVERS` (`:18`, checked `:30`) | **none** |
| Stale-waiver check | yes (`:81`) | n/a |
| On the enforcement scorecard | yes (row 25) | **absent** |

`docs/governance/advisory-rules-audit.md` row 25 names **exactly one**
mechanism for the Pydantic rule. The second enforcer — wider blast radius, no
waiver escape — was invisible to the audit whose entire purpose is catching
this.

### Residual, still live

The `#607` fix narrowed the *root* and made the check structurally inert for
adopters. It did not close the other two halves, both confirmed live today:

1. **Arming is a bare substring.** `instruction_audit.py:292` arms a fail-closed
   gate on `"Pydantic" in body or "BaseModel" in body` — the word appearing
   anywhere in `.github/instructions/models.instructions.md` (4 occurrences
   today). A rule body that *mentions* Pydantic in passing arms the gate.
2. **No waiver parity.** The AST validator honours
   `src/gzkit/commands/obpi_precomplete.py::CheckResult`; the regex validator
   has no equivalent, so a legitimately-waived dataclass would be exempt under
   one mechanism and a build-breaker under the other. Currently latent only
   because the tree contains **zero** dataclasses under `src/gzkit/**`
   (`audit_code_contract_mismatches` returns 0 findings on the live tree).

**A third instance, found while re-deriving the above and not previously
recorded anywhere:** the sole `_DATACLASS_WAIVERS` entry is **inert**.
`CheckResult` is now a `BaseModel` (`obpi_precomplete.py:43`), not a dataclass,
so the waiver exempts nothing. The stale-waiver check at `models.py:81` does not
catch it because its predicate is *does this class still exist*, not *does this
class still need the exemption*. The waiver's **objective** was never recorded as
a condition, so the staleness check tests the wrong predicate — this ADR's thesis
reproduced inside the one mechanism that already has a staleness check.

### A second surface: thresholds are reach, too

Recorded on GHI #727 on 2026-07-28 after a full session was burned on it.
`219d23fd6` raised four numbers in `data/instructions_files_budget.json`
(AGENTS.md 31800→50000, CLAUDE.md 4000→15000, `.claude/rules/*.md`
15000→30000, ceiling 32768→65536). The *ceiling* move carried a verbatim
operator rationale pinned in a test; the three *budget* moves carried none —
not in the `_doc`, not in the commit message, not in a rule or ADR.

An agent later read a threshold raised 57% with a `_doc` narrative terminating
at the prior value, diagnosed drift under `AGENTS.md` § MAKE LLM STOCHASTIC
VIBES INERT claim 3, retuned, and committed (`2d55abccd`). The diagnosis was
wrong — the looseness was a deliberate operator posture:

> until we get gzkit stable, I want to relax limits. the cms system is meant to
> control this, but we don't have gzkit feature stable enough to be strict

Reverted in `5d6c18e84`. **A budget threshold is the *reach* of
`gz validate --instructions-files-budget`.** Nothing recorded why its reach was
what it was, so a deliberate posture and unwitnessed drift were
*indistinguishable on disk*. That indistinguishability — not the number — is
what cost the session.

### Class of failure

**Any enforcement mechanism whose objective and scope are unrecorded.** The
failure is not that a given mechanism is wrong; it is that nothing makes a wrong
one *visible*.

## Decision

**Not settled. This ADR records the fork; the operator rules it at promotion.**

Pool status is exactly right for this: the question below changes what gets
built, and no agent should pick it. Recording it here rather than in a GHI
thread means it reaches the promotion ceremony as a design question with its
evidence attached.

### The fork (operator ruling required before promotion)

**Is the per-mechanism objective+scope obligation documentary or mechanical?**

| Option | Shape | Cost |
|---|---|---|
| **Documentary** | Columns on the scorecard + a lodestar section; enforcement stays cultural | Cheap; consistent with the operator posture that gzkit should *"prefer advisory reflection chores over extensive mechanical checks"* |
| **Mechanical** | A `gz validate` scope asserting every enforcement mechanism declares an objective and a scan scope | Stronger — but it is itself a new mechanism, and **a mechanism to police mechanisms needs its own warrant before it is built** |

The **lodestar half is likely rulable independently of the fork** and is the
smaller of the two.

### The three candidate halves

1. **App level — a record of what gzkit chose and why, *and how far the choice
   reaches*.** `docs/design/lodestar/architectural-identity.md` has twelve
   sections and **none** for technology choices with their warrants. The warrants
   are scattered: the principle in `AGENTS.md` § STDLIB-FIRST, argparse in
   ADR-0.0.2, Pydantic in `.gzkit/rules/models.md`, unittest in
   `.gzkit/rules/tests.md`. Nothing states *"here is the choice, here is the
   warrant, here is the scope of the warrant."* **The missing third clause is
   what let a scoped departure be read as a blanket mandate.**

2. **Feature level — a per-mechanism statement of objective and scope.** The
   scorecard classifies *rules* by enforceability and names *one* mechanism each.
   It never asks a mechanism to declare what it is for or how far it reaches.

3. **Capture level — a rationale slot at write time.** Every surface in halves 1
   and 2 is **lookup-side**. `gz git-sync` bundles derived-surface regeneration;
   its commit template has slots for governance anchors and ledger events but
   none for *"why did this hand-tuned threshold change."* A value requiring
   rationale rode a ceremony structurally unable to carry one — so **even with
   every lookup surface built, the rationale would still be lost at write time
   and never reach them.** Suggested shape: a rationale slot (or fail-closed
   prompt) when a sync bundle touches hand-tuned values under `data/`, distinct
   from derived surfaces which legitimately need none. Precedent for treating
   capture as its own half: GHI #654's capture-silence gap was direct-fixed ahead
   of its ADR chain (`48a5f799`, `dcf29b95`) as a live footgun.

### Deliberately not decided here

The two Pydantic validators' disagreement is this ADR's **worked example, not a
defect to resolve by fiat.** They differ in intent as well as engine — one is
*conditional on the instruction document* (a contract-mismatch check), the other
*unconditional* (a rule check). Consolidating them, or keeping both with
recorded objectives, is precisely the decision this ADR exists to make with the
operator. Picking one unilaterally would be the *"silently picking one
interpretation"* failure `AGENTS.md` § Behavior Rules — Always #9 names.

## Alternatives Considered

1. **Fold into `ADR-pool.enforcement-claim-meta-validator` (ADR-0.0.75).**
   Rejected — the neighbour is close but answers a **different question.** That
   ADR asks *"is this claim actually enforced?"* and proves it with a live
   negative control: build a violation, run the real entrypoint, assert it fails.
   **Both** validators in the #607 pair would have **passed** such a control —
   each genuinely fails on a real dataclass. An NC proves the teeth bite; it
   cannot detect that they are biting the wrong leg. Objective-and-scope is
   orthogonal to enforcement-is-real, and folding would hide it behind a green
   meta-validator. (0.0.75's deferred *extension point F* — free-prose claim
   scanning — is adjacent to half 2 and should be reconciled at whichever
   promotes second.)

2. **Fold into `ADR-pool.contract-surface-mechanical-defenses`.** Rejected:
   that ADR converts `AGENTS.md` / `CLAUDE.md` prose into audited evidence. This
   one is about validators and thresholds, not the contract surface.

3. **Treat it as the #607 residual and direct-fix it.** Rejected: the arming and
   waiver-parity residuals *are* direct-fixable, but fixing them closes the two
   named instances and leaves the class open — the next mechanism ships with an
   unrecorded scope and the cycle repeats. `AGENTS.md` § DO IT RIGHT #1 (fix the
   class, not the instance) points at a record, not a patch.

4. **Mechanical enforcement from the start, skipping the fork.** Rejected as a
   unilateral agent choice. A mechanism policing mechanisms is exactly the shape
   that most needs a recorded warrant — building it without one would be the
   first violation of the rule it enforces.

5. **Documentary only, permanently.** Not rejected — it is a live arm of the
   fork. Recorded here so promotion does not treat "mechanical" as the default
   outcome.

## ADR Relationships

- **`ADR-pool.enforcement-claim-meta-validator` (ADR-0.0.75)** — nearest
  neighbour, orthogonal question. *Is the claim enforced?* (0.0.75) vs *what is
  the mechanism for and how far does it reach?* (this). See Alternative 1 for why
  an NC cannot substitute.
- **`docs/governance/advisory-rules-audit.md`** — the scorecard carrying the
  hole; half 2 amends it.
- **`docs/design/lodestar/architectural-identity.md`** — the app-level home with
  no tech-choices section; half 1 adds one.
- **ADR-0.0.2** — the stdlib CLI (argparse) choice; one of the scattered
  warrants half 1 would gather.
- **`ADR-pool.pydantic-schema-enforcement`** — historical: the dataclass→Pydantic
  migration whose completion is why the residual is latent rather than firing.

## Notes

### Related GHIs (snapshot 2026-08-04 — re-check before promotion)

- **#727** — the originating issue; closed `superseded` against this ADR.
- **#607** — the instance that surfaced the class. Export half fixed; arming and
  waiver-parity halves live, evidenced above.
- **#669** — sibling cut: mechanical audit absent, convention-only enforcement.
- **#691** — sibling cut, same doctrine-drift family; homed at
  `ADR-pool.rule-surface-aging-clock` 2026-08-04.
- **#533** — the `<15k` destination whose only mechanical pressure the budget
  thresholds affect.
- **#579** — sibling cut on the same surface: whether chars is even the right
  budget unit.
- **#654** — capture-side precedent for half 3.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
