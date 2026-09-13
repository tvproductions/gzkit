# The chore class system — 2026-09-12

> **Status:** design record, operator-ratified 2026-09-12. Discharges under the
> `doctrine-declared-without-mechanism` box of Movement C ("Reduce the accretion")
> in the active campaign — **agent-side arm**: *a skill mandate with no receipt*.
> Advances that box; does not close it. See § What this record does not license.
>
> **Motivating map:** [`rules-tools-audits-refactors-alignment.md`](rules-tools-audits-refactors-alignment.md)
> — the rules / tools / audits / refactors alignment goal this system is the first
> mechanism for, including the missing rule ↔ chore and chore ↔ cadence edges.

---

## The question behind the design

`gz-chore-runner` v1.3.0 declares what a chore is:

- description — *"executing **scheduled maintenance, refactoring, or code quality work items**"*
- Outputs — *"**Updated repository files** (as defined by the chore)."*
- Step 5 — *"If criteria fail, read the CHORE.md workflow and **implement fixes** … Iterate: fix, validate, repeat"*
- Step 8 — `gz chores propose-ghi`, i.e. a GHI is a *proposal*, not the default exit

Operator statement of the same contract (2026-09-12, verbatim): *"a chore should
diagnose and fix, with needed consultations with the operator, for input and judgment,
as needed … A chore is authorized to find, analyze, solve and fix. I don't need to
debate cleaning and taking out the trash from the house on a regular basis, I need to
organize that tidying."*

**Nothing enforces any of it.** 19 of 40 chores declare themselves audit-only. Three
declare audit-only and contain a remediation step. Nine stop at data with no
recommendation to act on. Nothing schedules any chore, and nothing surfaces that a
chore has gone unrun.

That is the `doctrine-declared-without-mechanism` shape exactly — *"Layer X declares a
discipline that Layer X does not mechanically enforce."*

## Purpose and authority

This record defines the **class system** that makes a chore's nature declarable,
uniform within its class, and mechanically checkable. It is a design record, not
canon: the binding surfaces it implies are `src/gzkit/chores/registry.json` (schema),
`src/gzkit/chores/README.md` (authoring contract), and a conformance validator. Until
those land, this document is the design and nothing more.

Operator ruling on route (2026-09-12): **discharge under the Movement C box, no new
ADR.** Verbatim: *"Movement C box — discharge it there, no new ADR. but is not likely
simple."*

## Operator directives

Each directive below is operator verbatim from 2026-09-12. They bind the per-chore
declarations in § Implementation order, step 5, and they were given **before** the
class system existed. Where one names a set, the class system refines that set rather
than overturning it.

**What a chore is** (20:30Z): *"chores are there to identify issues, provide an
analysis, recommend a solution approach, and execute on solutions. a chore should
diagnose and fix, with needed consultations with the operator, for input and judgment,
as needed … I run chores at intervals to for normal upkeep and health, which is
somewhat distinct from GHIs. A chore doesn't always need to make a GHI and should do so
sparringly and in consultation with the operator."*

**Conversion** (20:41Z): *"the control-surface five stay diagnostic, the rest convert
- update readme if we now see it as inadequate."* Qualified in the same message: *"on
audit-only, we'll need to examine - they are not all uniform. Most should be suggesting
fixes and solutions even if they stop at audit. even when they stop with results the
intention is almost always a subsequent fix phase … the control-surface five *might* be
exceptions, but they also may not. We need big picture calibration here."* The class
system is that calibration. **Agent reading, not yet operator-confirmed:** the
conversion is read through the class system, so a chore's terminal stage comes from its
class and declared rung, and "stay diagnostic" lands at the **propose** rung, which
still owes a recommendation. § The control-surface five are not uniform records why
the five cannot be declared as a block.

**Internal consistency** (20:41Z): *"I'd like for chores to be proactive and most are
there to help me fix/tidy, but, as you see, some are diagnostic/audit - each should be
internally-consistent and clear about this."* On the three contradictory chores: *"so
with 1. please fix/make consistent."*

**The split stays** (20:41Z): *"that split is fine, it makes room for pause and
operator consultation."* This refers to the detection→application pairing. A chore that
stops at a plan artifact and hands off to a paired repair chore is a legitimate shape,
not a defect.

**Last run** (20:41Z): *"I maintain frequency, but each should at least indicate a
'last run' for relative staleness."*

**Stopping at data is a defect** (20:53Z), of the chores that declare audit-only and
carry no recommendation: *"this is an addressable shortcoming and needs rememdy."*

**Class awareness** (20:53Z): *"uniformity within class is important to me - the chore
system should be aware of these classes, how/why each class of chore should be handled
uniformly and what the conseqeuences of staleness means per class."*

**Conversion is blast-radius dependent** (20:53Z), answering *(a)* an inline fix phase,
*(b)* a paired fix chore, or *(c)* depends on blast radius: *"it depends, but we may use
my 'chores likely organize along class seams' as my overaching response."*

**Ratification** (21:10Z): *"I think the entire system surfaced from our discussion,
and from the research is outstanding. I ratify, with great enthusiasm, the entire plan.
I love the inclusion of suppression. I love the references to the external
systems/exemplars and hope to maximally benefit from then."*

## Evidence standard

Every count below was measured on 2026-09-12 against the working tree, by command.
Commands are recorded in § Reproduction record so a later reader re-runs rather than
trusts a transcription (`.claude/rules/governance-core.md` — a value written in a
Markdown doc is illustrative, never authoritative).

External patterns are cited to primary sources. They are **exemplars, not authority**:
gzkit's needs govern the appropriation, never the reverse.

---

## The measured state

| Measurement | Value |
|---|---|
| Chores in the registry | 40 |
| Declare audit-only / read-only / "does NOT fix" | 19 |
| Carry no recommendation of any kind | 26 |
| **Declare audit-only AND carry no recommendation** | **9** |
| **Declare audit-only AND contain a remediation step** | **3** |
| Acceptance criteria that gate only on file existence | **0** — already swept |
| Wired to `scripts/check_proof_freshness.py` | 7 |
| Declare a `frequency` in the registry | **1 of 40** |
| Invoked by CI, pre-commit, or any hook | **0** |
| Last ran 2026-07-31 (one manual sweep) | 23 of 39 |

Registry fields available today: `frequency`, `lane`, `path`, `projectLocal`, `slug`,
`timeoutSeconds`, `title`, `vendor`, `version`. **There is no field in which a chore
can declare its class, its governing rule, or what it refuses to touch.**

The nine that stop at data:

`cli-contract-governance` · `control-surface-rule-vs-check-drift` · `dependency-currency` ·
`eval-feedback-cluster` · `evidence-integrity-audit` · `frontmatter-ledger-coherence` ·
`repository-structure-normalization` · `skill-command-doc-parity` · `skill-trigger-testing`

The three that contradict themselves:

`frontmatter-ledger-coherence` · `repository-structure-normalization` · `skill-command-doc-parity`

### The control-surface five are not uniform

The operator's conversion directive exempted these five as a set. Measured, they do not
behave as one:

| Chore | Terminal stage today | Class reading |
|---|---|---|
| `control-surface-rule-conflicts` | a prioritized follow-up list | Coherence — conformant |
| `control-surface-skill-rule-reachability` | a recommendation per row | Coherence — conformant |
| `control-surface-validator-reachability` | recommendations, plus a shrink-only baseline | Coherence **carrying a ratchet** |
| `control-surface-rule-vs-check-drift` | **a parity table, no recommendation** | Coherence — **violates the class contract**; one of the nine |
| `control-surface-permission-consent-drift` | a routing list, each live row sized for a direct-fix GHI | Coherence — conformant; to calibrate, since GHI-shaped exits are meant to be sparing |

`control-surface-validator-reachability` describes itself as "audit-plus-ratchet", and
it is **not a sixth class**. A ratchet is a policy on a finding count, not a reason a
chore exists, and any class could carry one. Its subject — does a declared witness
actually fire — is a declared surface disagreeing with observed behavior, which is
Coherence.

So the set the operator was ready to exempt contains a class violation. Calibrating
all five against the class contract is part of § Implementation order, step 5, and they
are not declared as a block.

---

## The discriminator

Not audit-versus-repair. **Is one side the declared authority?**

`frontmatter-ledger-coherence` finds ADR/OBPI frontmatter disagreeing with the ledger
and *automatically rewrites the frontmatter*, because the ledger is Layer-2 truth and
frontmatter is Layer-1 authorship (`docs/governance/state-doctrine.md`). The correct
output is derivable, so the chore repairs.

`control-surface-rule-conflicts` finds two rules disagreeing. Neither is presumptively
right. Resolving it is a **ruling**, so the chore recommends and stops.

Same shape of finding, opposite terminal stage, and the thing that decides is gzkit's
own layer doctrine.

The Python ecosystem draws the identical line from the other direction: linters default
to diagnosis, formatters default to writeback, and `ruff` embodies both in one binary —
`ruff check` diagnoses and requires `--fix`; `ruff format` writes and requires
`--check`. **The subject determines the default, not the vendor.** A formatter's output
is canonical and machine-decidable; a lint fix is a judgment about intent.

Sorted by default behavior, the surveyed corpus splits cleanly:

| Default | Tools |
|---|---|
| **Diagnose only** | `ruff check`, mypy, pyright, pylint, flake8, bandit, pip-audit, safety, ty (without `--fix`) |
| **Rewrite in place** | black, `ruff format`, isort, pyupgrade, add-trailing-comma, reorder-python-imports |
| **Print the result to stdout** | autopep8, yapf, autoflake, docformatter |

So the honest question for a chore is never *"should it report or fix by default?"* It
is **"is this chore's correct output machine-decidable, or is it a judgment?"** That is
the line the ecosystem actually draws, and it is the same line gzkit's layer doctrine
draws when one side is the declared authority.

**Three modeling errors to fence out of this axis:**

- **A finding's severity is not a fix's destructiveness.** bandit's `-l/-ll/-lll`
  (severity) and `-i/-ii/-iii` (confidence) are *report filters on the finding* —
  inputs to whether a human should look. safety's `patch|minor|major` describes *how
  destructive the repair is*. They sit on opposite sides of the finding/remediation
  boundary: a high-severity finding can have a trivially safe fix, and a low-severity
  one can require a breaking major bump. A chore's rung is set by the repair's
  consequences, never by the finding's severity.
- **black's `--safe` is not a safety tier.** Verbatim: *"By default, Black performs an
  AST safety check after formatting your code. The `--fast` flag turns off this check
  and the `--safe` flag explicitly enables it."* It verifies the formatter's own output.
  Two unrelated concepts share the word; do not seat `--safe` on a fix-safety axis.
- **No rationale for "type errors are not autofixed" exists.** mypy and pyright are pure
  diagnosis at the CLI, while ty (`--fix`, `--add-ignore`) and pyrefly (`suppress`,
  `infer`) both rewrite source — a generational split (2012/2019 against 2025-era), not
  a philosophical one. No tool in the category states why it does or does not autofix.
  Do not synthesize a "type errors need human judgment" rationale; it is in none of
  their documentation.

**The deepest external statement of why a machine-authored change stops for a human** is
pre-commit's, and it lives only in its maintainer's issue comments, not on
pre-commit.com. Its rule to hook authors: *"The hook must exit nonzero on failure or
modify files."* Its reason (pre-commit/pre-commit#806): *"Since software is imperfect in
the general case, pre-commit will not commit anything until it has been looked at by a
human."* And #747: *"hooks are very frequently not perfect and magically changing what's
being committed should not be taken lightly."* pre-commit detects modification itself —
it diffs the worktree before and after each hook and fails on
`files_modified or bool(retcode)` — so the distinction is legible **without the tool's
cooperation**, and there is no opt-out. That is the same shape as the detection→
application split the operator kept: a machine-authored change is seen and re-affirmed
before it enters the record.

---

## The five classes

`class` answers *why the chore exists and what its staleness costs*.

| Class | The finding is | Staleness signal | What staleness costs |
|---|---|---|---|
| **Conformance** | code deviates from a standard gzkit declares | content delta | gradual decay; high where no commit-path gate exists |
| **Coherence** | two authored surfaces disagree, **no declared authority** | content delta | an agent hits the contradiction mid-work and rules silently |
| **Curation** | a corpus accumulated past usefulness | accumulated work | bloat; per-turn context weight; signal decay |
| **Mining** | history holds a recurring pattern worth acting on | elapsed time | lost feedback loop; the same failure keeps recurring |
| **Currency** | the outside world moved | elapsed time | **assertions become false** — incorrectness, not decay |

**Currency is the only class where staleness makes the chore lie.** Measured instance:
`frontier-model-card-currency` passed both criteria on 2026-09-02 while its `current`
entry had been superseded since 2026-09-01, found only because an operator supplied the
new card URL. That is why it is the sole member of `_SCAN_INTERVALS` today — the
existing mechanism found the seam one chore at a time.

**Mining stays separate from Coherence** even though both stop at the same rung: their
staleness has different physics (content delta vs. elapsed time), so collapsing them
would force one staleness arm onto two mechanisms.

---

## The four rungs

`rung` answers *where the chore stops*. It is **orthogonal to class** — class predicts
rung in most cases but does not determine it.

| Rung | Writes | Exemplar |
|---|---|---|
| **observe** | nothing | `ANALYZE` · `make -q` · `git maintenance is-needed` · Django system checks |
| **propose** | a plan artifact, never the subject | Terraform `plan` · SARIF `result.fixes` · ESLint *suggestion* · gzkit's `proposal-*.json` |
| **repair** | the subject; safe changes by default | `VACUUM` · `ruff --fix` · Ansible normal run |
| **operator-only repair** | the subject, **excluded from any automatic run** | autovacuum *"will never issue `VACUUM FULL`"* · `git maintenance register` disables `gc` · a Terraform speculative plan **cannot** be applied |

The fourth rung is the one half-designed registries omit. It is not a lesser class — it
is a declared policy the runner honors. Anything whose repair touches canon lives here.

**How the surveyed systems grade the same ladder:**

| Grade | ESLint | Ruff | Ansible | Postgres | CSAF | SARIF |
|---|---|---|---|---|---|---|
| observe only | (no fix) | no fix | info/facts modules | `ANALYZE` | `none_available` / `no_fix_planned` | result, no `fixes` |
| propose, a human applies | suggestion | unsafe fix (opt-in) | check mode + `--diff` | — | `workaround` / `mitigation` | `fixes` present, not applied |
| repair in place, safe by default | auto-fix (`--fix`) | safe fix | normal run | `VACUUM` | `vendor_fix` | the consumer applies |
| disruptive, never automatic | — | — | — | `VACUUM FULL` | `restart_required` | — |

**Postgres is the cleanest precedent for the fourth rung, with its reason stated.**
`ANALYZE` samples and writes only planner statistics; `VACUUM` repairs in place and
*"runs concurrently with reads and writes"*; `VACUUM FULL` takes `ACCESS EXCLUSIVE` and
rewrites the table. *"The usual goal of routine vacuuming is to do standard `VACUUM`s
often enough to avoid needing `VACUUM FULL`. The autovacuum daemon attempts to work this
way, and in fact will never issue `VACUUM FULL`."* Its reasons: it blocks, and *"there is
not much point in this if the table will just grow again in the future."* The automatic
runner is forbidden from reaching the disruptive rung, and a routine rung exists so the
disruptive one is rarely needed.

**git declares background-safety as a property of each task.** `git maintenance
register` enables only tasks that are *"safe for running in the background without
disrupting foreground processes"*; under the `incremental` strategy the full `gc` —
*"can be expensive… can also be disruptive in some situations, as it deletes stale
data"* — is disabled. The task registry classes each task as additive
(`commit-graph`, `prefetch`), repair (`loose-objects`, `incremental-repack`,
`pack-refs`) or destructive (`reflog-expire`, `rerere-gc`, `worktree-prune`, `gc`).

**The consequence is a property of the declaration, not of the check logic.**
Kubernetes runs one observation mechanism — the probe — with three declared
consequences: a failing **liveness** probe restarts the container, a failing
**startup** probe kills it inside the init window, and a failing **readiness** probe
only removes the Pod from Service endpoints while the container keeps running. The
documentation warns that an incorrect liveness probe can cascade, to be used *"only when
you're certain the condition indicates unrecoverable failure"*; readiness is the safe
default because it degrades reported status without mutating anything. Kubernetes solved
*"half audit, half repair, inconsistently declared"* by moving the consequence into the
declaration.

**Finer grading inside the repair rung**, where a chore needs it:

- **Ruff's published fix-safety definition** — *"an unsafe fix could lead to a change in
  runtime behavior, the removal of comments, or both, while safe fixes are intended to
  preserve runtime behavior and will only remove comments when deleting entire
  statements or expressions."* Unsafe fixes are *hidden but announced* (*"1 hidden fix
  can be enabled with the `--unsafe-fixes` option"*), enabled by one flag or config key,
  machine-readable (`applicability` in JSON output), and re-gradable per rule in both
  directions (`lint.extend-safe-fixes` / `lint.extend-unsafe-fixes`). Preview mode is a
  separate, orthogonal **maturity** axis. Ruff is the only surveyed tool that has
  generalized a per-fix safety class.
- **Conservative default with named widening flags** (autoflake): *"By default,
  autoflake only removes unused imports for modules that are part of the standard
  library. (Other modules may have side effects that make them unsafe to remove
  automatically.)"* Each widening flag is named for what it widens, and the most
  dangerous one ends its own help text with `(unsafe)`.
- **A blast-radius ceiling** (safety): repair is bounded by a declared magnitude, and
  anything beyond it prompts instead of applying — *"This threshold is necessary to
  prevent Safety from applying updates that could impact projects."*
- **Structural incapacity** (pre-commit `language: fail`): a unit with no executable at
  all, *"A lightweight `language` to forbid files by filename"*, which cannot modify by
  construction rather than by convention. The strongest form of the observe rung.

**Autonomy is earned per capability, and its endpoint is policy.** IBM's five levels of
autonomic maturity — Basic, Managed, **Predictive** (*"recognizes patterns and advises
the administrator on a course of action"*), **Adaptive** (*"itself performs appropriate
actions"*), Autonomic — place the diagnose/act boundary at the Predictive→Adaptive step,
as a maturity transition expected per capability rather than declared globally. At the
end state the human states policy instead of approving actions. That is the direction a
chore's rung moves when it moves at all: one chore at a time, on evidence.

Parasuraman, Sheridan & Wickens (2000) decompose automation into four independently
settable stages — information acquisition, information analysis, decision and action
selection, action implementation. IBM's MAPE-K (Monitor, Analyze, Plan, Execute over
shared Knowledge, 2005) is the same decomposition for self-managing software and is the
reference architecture for periodic maintenance units. **A two-value audit/repair field
collapses a four-stage model and the collapse leaks** — a chore that plans a fix without
applying it is a real third thing.

The stages are independently settable, and that is the point of the decomposition: a
chore can be fully autonomous at monitor and analyze while stopping at propose for plan
and execute. **Class and rung are orthogonal for the same reason** — class says why
the chore exists and what its staleness costs, rung says where it stops. Class predicts
rung in most cases, which is why the operator's "chores likely organize along class
seams" holds, but they are separate declarations.

**Capability is not authorization.** Morris et al., *Levels of AGI* (DeepMind,
arXiv:2311.02462): *"lower levels of autonomy may be desirable for particular tasks and
contexts (including for safety reasons) even as we reach higher levels of AGI."* A
chore's rung is a policy about consequences, never a claim about the model's
competence. "The model is good enough now" is not an argument for raising one.

---

## Two licenses: scheduling and writing

Two distinct properties license a chore to run unattended, and they answer different
questions.

**Idempotence licenses scheduling** — *may this run on a cadence?* Google SRE, ch. 7
"The Evolution of Automation at Google", verified verbatim: *"Requiring idempotent fixes
meant teams could run their 'fix script' every 15 minutes without fearing damage to the
cluster's configuration."* Chef states the same for convergent recipes, which are
*"meant to be run periodically to override out-of-band changes."* Neither argues that
idempotence makes a repair *correct* — only that re-running it does not compound.

**Reversibility licenses writing** — *may this touch the subject?* OpenAI, *Practices
for Governing Agentic AI Systems* (2023), names irreversibility as the criterion that
forces approval: *"Some decisions may be too important for users to delegate to agents,
if there is even a small chance that they're done wrong (such as independently
initiating an irreversible large financial transaction)."* AWS Well-Architected pairs
the two in one principle: *"Make frequent, small, reversible changes … reduces the
blast radius and allows for faster reversal when failures occur."* Amazon's 2015
shareholder letter attaches *"consultation"* specifically to one-way doors, and calls
two-way-door decisions ones that *"can and should be made quickly."* Applying the door
framework to agent authorization is **gzkit's extension**; no primary source makes it.

The research that separated the two was explicit that the distinction is its own
synthesis, not any source's claim. The separation is still sound: a chore can be safe
to schedule and unsafe to write, or the reverse.

**Scope must fail closed on empty.** SRE ch. 7's Diskerase incident: *"the empty set
was used as a special value, interpreted to mean 'everything.' This means the
automation sent almost all the machines we have in all colos to Diskerase."* The failure
was not a bad decision; it was an unbounded scope. A chore whose target set resolves to
empty does nothing.

**Level-triggered, not edge-triggered.** Kubernetes API conventions: *"conditions are
observations and not, themselves, state machines… The system is level-based rather than
edge-triggered, and should assume an Open World."* A level-triggered chore derives its
need from present state — Postgres from `n_dead_tup` now, git from the loose-object
count now, `make` from mtimes now — so it is safe to re-run and its "should I run?"
answer never depends on trusting a run log. **That is what makes an operator-paced
cadence survivable:** no history is reconstructed; the present is re-measured. It is the
scheduling license stated as a design property rather than a test. Kubernetes controllers
are the reference form — *"control loops that watch the state of your cluster, then make
or request changes where needed"* — and observation is separated from action by an
indirection, not only a phase boundary (*"The Job controller does not run any Pods or
containers itself. Instead, the Job controller tells the API server to create or remove
Pods."*). The API's `spec` / `status` split names the two sides: *"the specification of
the desired state of an object"* against *"the status of the object at the current
time."* A chore's declaration is its spec; its last observation is its status.

**Automation with guardrails is the licensed middle.** AWS Well-Architected, alongside
the reversibility principle: *"Safely automate where possible: … you can employ
automation safety by configuring guardrails, including rate control, error thresholds,
and approvals."* That is structurally the observe / propose / repair / consult split.
OpenAI's default-behavior heuristic points the same way: *"err toward actions that are
the least disruptive ones possible, while still achieving the agent's goal."*

**Mechanical verifiability substitutes for judgment where it exists.** Renovate
automerges only after *"the required tests … pass"*; Dependabot inherits
branch-protection required checks. Pre-authorization is granted to action classes whose
correctness has a **cheap, automatic, falsifiable proof**, and where no such proof
exists the rung drops. For a gzkit chore the proof is the acceptance criteria — which is
why a criterion that gates on file existence is no proof at all, and why the estate's
already-completed sweep of `test -f` criteria matters.

**Authorization can expire — recorded, not adopted.** OpenAI's *Practices* offer the only
mechanism found that keeps standing authorization without either per-action prompting
or unbounded drift: *"system deployers can cause agents to periodically 'time out' until
a human reviews and reauthorizes them."* Authorization attaches to a class of action and
lapses on a cadence, so the operator re-ratifies the policy rather than the actions.
Devin's five persistence scopes — once, session, project, project-local, global — are
the shipping analogue. The ratified field list carries no expiry. Whether a chore's rung
lapses is a question for the schema step, alongside the two licenses above.

**Unreconciled against the ratified fields.** § The declaration, and the fence lists the
ratified per-chore fields. `rung` carries most of the writing license and `staleness`
carries cadence, but **neither license is an explicit declaration.** The session
proposed that each chore declare both, then ratified a field list without them. Whether
`rung` fully discharges reversibility, and whether idempotence needs its own field, is
open. It is settled in the schema step, with the operator — never by adding a field on
the strength of this note.

---

## Consultation points

The operator's model is a chore that finds, analyzes, solves and fixes, *"with needed
consultations with the operator, for input and judgment, as needed."* The literature
has precise names for that model and for how consultation points fail.

### The model, located

| Scheme | Level | Text |
|---|---|---|
| Sheridan & Verplank (1978) | **7** — routine chores | *"Executes automatically, then necessarily informs the human"* |
| Sheridan & Verplank (1978) | **5** — a consultation point | *"Executes the suggestion if the human approves"* |
| Sheridan & Verplank (1978) | 6 — rarely designed | *"Allows the human a restricted time to veto before execution"* |
| Feng, McDonald & Zhang (2025) | **L4, User as Approver** | *"The user is only required to interact with the agent when the agent encounters a blocker it cannot resolve on its own"* |

Levels 8 and 9 — inform only if asked, or only if the system decides to — are *worse*
than 7 for gzkit. Level 7's discipline is **mandatory disclosure after the fact**, and
that is what makes standing authorization auditable.

**In, on, or out of the loop.** The three-way split originates with Bonnie Docherty in
Human Rights Watch's *Losing Humanity* (2012), classifying weapon systems: **in** the
loop cannot act without positive human authorization; **on** the loop acts without it
but under supervision with override; **out** of the loop acts with neither. The
discriminator is who must act for the action to happen: in the loop needs a positive act
to proceed, on the loop needs a positive act to *stop*. The operator's model is **on the
loop** for routine chores, with declared **in-the-loop** points for judgment.

**The obligation is on the design surface, not the frequency of asking.** DoD Directive
3000.09 (2012, updated 2023): *"Autonomous and semi-autonomous weapon systems will be
designed to allow commanders and operators to exercise appropriate levels of human
judgment over the use of force."* It mandates that the system be *designed to allow*
judgment, not approval per action. Pre-authorized routine action is compatible with that
doctrine so long as the judgment surface exists and can be reached.

**The vocabulary has not settled for LLM agents.** Shi & DiFranzo, *Human Control Is the
Anchor, Not the Answer* (arXiv:2602.09286, 2026), document that agentic-AI communities
diverge substantially on where the boundary sits. Cheng & Cheng (arXiv:2604.23049, 2026)
rename the same in/on distinction as AI-in-the-Loop against HITL. Treat new names for it
as the old idea.

### Where to put one: pre-declared, never computed

**A consultation point is declared in the chore definition. It is never computed at
runtime from the agent's confidence.**

Bainbridge, *Ironies of Automation* (1983): *"the designer who tries to eliminate the
operator still leaves the operator to do the tasks which the designer cannot think how
to automate."* Automating the routine leaves the human only the rare, hard residue,
exactly where they have the least practice. Aviation envelope protection supplies the
remedy: a short list of hard, human-authored boundaries decided before the system runs.
The selective-prediction literature (Chow 1970; Madras, Pitassi & Zemel 2018) shows a
principled stop rule is definable, but it assumes a calibrated posterior, and LLM
self-reported confidence is not one.

**The criterion that is decidable at authoring time** is Feng, McDonald & Zhang's
fourth determinant: escalate where **the operator holds information the agent
structurally cannot** — intent, priority, whether a rule still says what the operator
means. That is Coherence exactly: which of two conflicting rules still reflects intent
exists only in the operator's head. Google SRE's workbook reaches a compatible line from
operations: *"a truly mature system should only require human intervention for truly
novel problems."* Novelty and irreversibility are properties of the situation, not a
self-report, which is why they are more robust triggers than confidence.

**Why escalation must be designed rather than emergent.** Two more aviation findings
complete Bainbridge's. Sarter & Woods, *"How in the World Did We Ever Get into That
Mode?"* (Human Factors 37, 1995), originate *mode confusion*: as automation gains
autonomous modes, operators lose track of which mode it is in, even when it tries to
communicate its state. Envelope protection (Airbus Normal Law) is the inverse direction —
automation refusing the human rather than asking. Together: a design in which *"the agent
will say something when it's confused"* reproduces the documented failure; the fix is a
short list of hard, human-authored boundaries the automation cannot cross on its own
judgment. The research that assembled these three states that synthesis as its own
reading, not as any source's claim.

**A declarable shape for a consultation point.** Cheng & Cheng, *A Decoupled
Human-in-the-Loop System for Controlled Autonomy in Agentic Workflows* (2026), argue that
human-in-the-loop should be *"an independent system component within the agent operating
environment"* rather than approval logic embedded in each workflow, and decompose an
intervention point into four dimensions: **WHEN** (intervention conditions), **WHO**
(role resolution), **WHAT** (interaction semantics — approve or reject, versus supply
context or corrections), **WHERE** (channel). That is a usable schema for declaring a
consultation point in a chore definition, with the operator's role (below) filling WHO.

**Pre-declared stop conditions have no established name.** The best-provenanced primitive
is OpenAI's **tripwire** — a pre-declared check, *"purposefully ignored and infrequently
triggered"*, that halts the run. Anthropic's *Building Effective Agents* (2024) uses
*"stopping conditions (such as a maximum number of iterations) to maintain control"* and
has agents *"pause for human feedback at checkpoints or when encountering blockers."* A
tiered `AUTONOMOUS / INFORM / APPROVE_FIRST / HARD_STOP` scheme circulates in 2026 vendor
material — a useful shape, but coinage, not lineage. A paraphrase attributing specific
triggers to Anthropic (*"confidence below threshold / outside defined scope / safety rule
triggered"*) could not be found in the primary post; treat it as derivative.

**Where the circuit breaker fits, and where it does not.** Nygard's circuit breaker
(*Release It!*) trips on a count of a pre-classified event — "what counts as failure" was
decided at design time, and the breaker only counts. An LLM chore's hard problem is the
opposite: deciding whether a situation *is* a policy conflict or ambiguous intent at all.
The breaker fits exactly one sub-case — **the same repair attempted N times and reverted
or failed** — as a safety net underneath judgment, never a substitute for it.
Out-of-distribution detection is likewise not an established operational trigger for
agent self-escalation; in software the shipping mechanism is plain confidence or entropy
thresholding.

### What the operator is for at each one

Crootof, Kaminski & Price, *Humans in the Loop* (2023), enumerate nine roles a human
checkpoint can serve — corrective, resilience, justificatory, dignitary, accountability,
**stand-in**, friction, "warm body", interface — and warn: *"If we don't know what the
human is intended to do, it's impossible to assess whether a human is improving a
system's performance."* The stand-in role is *"proof of work — whether that work has
actually happened or not."*

**Each declared consultation point names the operator's role there.** An unnamed
checkpoint decays into a stand-in:

| Class | The operator is there to |
|---|---|
| Coherence | **supply the ruling** — information only the operator holds |
| Curation | judge what is still useful — **the likeliest rubber-stamp site**; name the role or expect decay |
| Mining | decide whether a recurring pattern is worth a work order |
| Conformance, Currency | normally nothing at write time; the operator-only-repair rung handles canon |

Anthropic, *How we contain Claude* (2026), quantifies the decay: *"users approved
roughly 93% of permission prompts"* and *"The more approvals a user sees, the less
attention they pay to each."* A gate approved 93% of the time carries almost no
information. And its governing principle is this system's lever: *"A tight perimeter
also means you can relax oversight."* Declared non-authority and a declared rung are that
perimeter.

**The failure an ill-specified checkpoint produces has a name.** Elish, *Moral Crumple
Zones* (2019): *"the moral crumple zone protects the integrity of the technological
system, at the expense of the nearest human operator."* A consultation that hands the
operator a decision without the context to make it relocates blame; it adds no safety.
Crootof, Kaminski & Price name the design error behind it the **MABA-MABA trap** (from
the Fitts-list tradition, "Men Are Better At / Machines Are Better At"): assuming *"that
human-machine systems represent the best of both worlds and don't introduce new issues
of their own."* Their worked example is Tesla disengaging Autopilot under one second
before impact — the human inserted at exactly the moment they could not help.

**An accountability role and a corrective role want opposite designs.** Accountability
wants the operator to sign; correction wants the operator to hold genuinely reviewable
evidence. A consultation point that declares one and is built as the other fails both.

**Frame the question so the operator's knowledge is recruited.** Dropbox's SREcon16
Europe talk, *Bridging the Safety Gap from Scripts to Full Auto-Remediation*, describes
an auto-remediation platform where the tool finds the problem and decides the fix, and a
human audits that decision before execution, on the question *"Why might I NOT want to
run this script?"* The shape is the point: not *"is this right?"*, which invites a
rubber stamp, but *"why might I not want this?"*, which draws on the context only the
operator holds.

> **Verification caveat.** USENIX returned HTTP 403; the Dropbox talk is known only from
> search-result extraction. Verify the abstract before quoting it anywhere else.

**Fewer, better prompts are a security improvement, not a convenience.** Saltzer &
Schroeder (1975) list eight protection principles, and four bear here: **least
privilege**, **fail-safe defaults** (*"base decisions on permission, not exclusion"*),
**complete mediation**, and **psychological acceptability** — *"the human interface be
designed for ease of use, so that users routinely and automatically apply the protection
mechanisms correctly."* A burdensome mechanism gets routed around, and a routed-around
mechanism is worse than none because it still supplies assurance. That anticipated the
93% approval finding by fifty years. OpenAI's *Practices* leave the remedy open: *"What
are the best practices for users reviewing approvals for high-cost actions (such as
minimum review times) to avoid their turning into a 'rubber stamp'…?"*

### Consent versus exception — a real disagreement, reconciled

Billings, *Aviation Automation* (1997; NASA TM-110381, 1996), distinguishes
**management by consent** — automation proposes, the human consents, automation acts —
from **management by exception** — automation acts, and the human intervenes to stop it.
The human-factors consensus reported around that work **prefers consent**, because
operators under exception mode reliably fail to notice when machine action conflicts
with their intent.

The operator wants exception, and nearly every shipping agentic tool ships it. **The
literature is against the industry here**, and this record states that rather than
resolving it by citing only the tools. The reconciliation the literature itself offers
is **predictable scope plus mandatory disclosure**. gzkit supplies both: the declared
rung and non-authority are the predictable scope; the staleness announcement and the
ledger are the disclosure.

> **Verification caveat.** Billings's own definitional sentences were not retrieved —
> the NASA TM PDF exceeded the research fetch limit — so the distinction and the
> reported preference rest on secondary sources. Do not quote Billings verbatim from
> this record.

### Operational forms

- **Pre-authorize what would have been rubber-stamped.** Renovate: *"enable automerge
  for any dependency update where you would select 'merge' anyway. Keep automerge
  disabled for updates where you want to read the changelogs or code before the
  merge."* Renovate also names its own proxy's failure — pre-1.0 packages are excluded
  because *"those can make breaking changes at any time"* — a discipline to copy when
  declaring a rung.
- **The plan artifact is the durable primitive.** Terraform's saved plan: *"When you
  pass a saved plan file to `terraform apply`, Terraform performs the operations in the
  saved plan without prompting you for confirmation."* The guarantee is that what was
  approved is what runs. The detection→application split the operator kept is this
  shape; the candidates report is the plan.
- **Gate the artifact, not every action.** GitHub's Copilot coding agent gates nothing
  mid-run and reviews at the pull request. For a chore producing one coherent repair,
  one reviewable artifact is stronger than a stream of prompts.
- **An agent reviewer does not discharge a human role.** Codex CLI's `auto_review`
  substitutes an agent for the human at the approval gate. That converts a
  human-judgment point into a second machine gate, and it does not satisfy a
  consultation point whose declared role is the operator's.
- **A consultation must not hang.** PagerDuty escalation policies walk an
  unacknowledged incident to the next tier on a timeout. A chore that raises a
  consultation and gets no answer stops at its plan artifact; it never proceeds by
  default and never deadlocks.
- **Declined and dismissed are different answers.** MCP elicitation (spec revision
  2025-06-18) returns `accept`, `decline` or `cancel`. A declined recommendation is an
  operator ruling worth recording; a dismissed one is not a ruling at all. The request
  carries a `requestedSchema` of flat primitive fields, and the spec forbids using
  elicitation for sensitive information: a consultation is a **typed question with a
  validated answer**, not free text.
- **Suspend with state, resume exactly there.** LangGraph's `interrupt()` raises
  `GraphInterrupt`, the checkpointer persists full graph state, and execution resumes via
  `Command(resume=...)`. In the OpenAI Agents SDK a tool flagged `needsApproval` produces
  an interruption, the run returns serializable state, and **the same run** resumes after
  review. A chore that pauses for the operator serializes enough to resume where it
  stopped, never re-deriving the finding from scratch. AutoGen's `human_input_mode` —
  `ALWAYS` / `TERMINATE` / `NEVER` — is the cleanest named tri-state dial in any
  framework.
- **Promotion is argued by override rate.** Dash0's *The Six Levels of Agentic Software
  Engineering* (2026) sets its levels by *"what humans look at and approve"*, not by how
  much code the agent writes, promotes per service on evidence, and proposes the human
  override rate as the metric — if the operator overrides a unit's proposals rarely
  enough, the unit has earned standing authorization. It also holds that high-risk
  surfaces *"may never qualify, and that is correct."* The axis and per-surface promotion
  transfer. **The numeric floors do not:** they are the author's proposal, not measured
  industry data, from practitioner synthesis rather than peer review.
- **Three vendors trust the same classifier three ways.** Anthropic ships a permission
  classifier and publishes its miss rate (auto mode *"catches roughly 83% of overeager
  behaviors"*; *"~17% of overeager actions get through"*, *"roughly 0.4% of benign
  commands blocked"*). Cursor states its classifier *"is not a security boundary."* Devin
  puts a hard denylist **underneath** its classifier — package installs, `rm`, `sudo` and
  mutating git operations are blocked whatever the classifier says — and org-admin deny
  rules survive every user mode. Devin's posture, classifier for convenience and a hard
  floor for safety, is the most defensible, and it is the posture declared non-authority
  gives a chore.

### What the sources converge on, and where they split

**Converge.** (1) Reversibility is the primary criterion for pre-authorized action, and
close to unanimous — OpenAI, AWS, Amazon and Google SRE reach it independently. (2)
Bounded blast radius is second, and it is what makes reversibility *checkable*: scope
constraint and oversight frequency are substitutes. (3) Idempotence licenses repetition,
which is a different thing from licensing repair. (4) Mechanical verifiability
substitutes for judgment where it exists. (5) Post-hoc legibility substitutes for
pre-hoc approval — *standing authorization is defensible when it is auditable*, and not
otherwise. (6) Pre-authorize what the human would have rubber-stamped; reserve the human
for where their reading is the value, and especially where they hold information the
agent cannot. (7) Authorization should expire rather than be permanent.

**Split — stated, not papered over.**

| | The disagreement | This record's reading |
|---|---|---|
| A | **Consent versus exception.** Human factors prefers consent; the industry and the operator want exception. | Reconciled by predictable scope plus mandatory disclosure (above). |
| B | **May an LLM classifier be the gate?** Anthropic ships one with a published miss rate; Cursor says it is no boundary; Devin floors it. | A hard, declared floor beneath any judgment. |
| C | **Confidence versus pre-declared conditions** as the escalation trigger. OpenAI's practices and the decoupled-HITL paper lean on uncertainty; selective prediction needs calibration LLMs lack; SRE says novelty; envelope protection says pre-declared bounds. | Pre-declared is the only route with an operational track record; confidence is at most an unproven supplement. |
| D | **Per-action versus per-artifact gating.** Claude Code, Cursor and Devin gate each tool call; Copilot gates only the pull request. | For a chore producing one coherent repair, the artifact gate has the stronger argument. |
| E | **Does adding a human help at all?** The MABA-MABA trap and the moral crumple zone argue an ill-specified checkpoint degrades the system and relocates blame. | The minority position in the source set and the best argued; it is the rebuttal to *"just add an approval step."* |

---

## The admission criterion

**Not every refactoring is a chore.** Operator, 2026-09-12: *"not all refactorings are
chores, but most chores can lead to refactorings."*

Google SRE supplies the test. *Site Reliability Engineering* ch. 5, verbatim: *"Toil is
the kind of work tied to running a production service that tends to be manual,
repetitive, automatable, tactical, devoid of enduring value, and that scales linearly as
a service grows."* The six characteristics, each with the book's own gloss:

| Characteristic | The book's wording |
|---|---|
| Manual | *"Running a script may be quicker than manually executing each step, but the hands-on time a human spends running that script is still toil time."* |
| **Repetitive** | *"If you're performing a task for the first time ever, or even the second time, this work is not toil."* |
| Automatable | *"If a machine could accomplish the task just as well as a human, or the need for the task could be designed away, that task is toil."* |
| Tactical | *"Toil is interrupt-driven and reactive, rather than strategy-driven and proactive."* |
| **No enduring value** | *"If your service remains in the same state after you have finished a task, the task was probably toil."* |
| O(n) with growth | *"If the work involved in a task scales up linearly with service size, traffic volume, or user count, that task is probably toil."* |

SRE caps operational work at below 50% of each engineer's time, and the Workbook
(ch. 6) treats toil as *"seemingly unavoidable for any team that manages a production
service"* — a bounded quantity, not zero — and measures it in *"Minutes and hours …
because they are objective and universally understood."* **SRE supplies the accounting
frame for a chore, not its data model:** a chore could declare its recurrence cost in
minutes, but nothing in SRE says what fields a chore carries. (The Workbook's strategy
list and toil taxonomy came through a page summarizer; the ch. 5 quotes are verbatim.)

Two characteristics decide admission:

- **Repetitive** — *"If you're performing a task for the first time ever, or even the
  second time, this work is not toil."*
- **No enduring value** — *"If your service remains in the same state after you have
  finished a task, the task was probably toil."*

And the qualification that settles the refactoring case: *"Cleaning up the entire
alerting configuration for your service and removing clutter may be grungy, but it's
not toil."* The discriminator is enduring value, not unpleasantness. SRE's contrast term
is **engineering work** — *"novel and intrinsically requires human judgment,"*
*"produces a permanent improvement,"* *"guided by a strategy."*

A one-time system-wide refactoring is engineering. It fails *repetitive* and it fails
*devoid of enduring value*. Admitting it to the registry corrupts the staleness model,
because a one-time refactoring can never be *due* again.

**Admission requires recurrence evidence, and the operator directs creation.** A chore
or an R&D run may *advise* that a new chore is warranted; the registry never
self-populates. Operator, 2026-09-12: *"I will almost always direct that new chores are
made, but I don't mind them being advise."*

**What "chore" means outside gzkit.** The Conventional Commits specification does not
define `chore`; it defines only `feat` and `fix`, and says other types are *"not
mandated"* and have *"no implicit effect in Semantic Versioning."* The original AngularJS
convention (2013) glossed it in one word: *"chore (maintain)"*. The live normative
definition is `@commitlint/config-conventional`: *"Other changes that don't modify src
or test files."* **Angular itself has since dropped `chore`** from its commit guidelines,
so the spec's citation of *"the Angular convention"* no longer holds for this type. The
outside meaning is a release-neutral residual bucket — tidying that changes no contract —
which is how gzkit's own `chore: … (gz git-sync)` commits read. gzkit's chore is a
larger thing: authorized, recurring maintenance labor that may repair source. The shared
word should not be read as a shared definition.

---

## Staleness

### Four signals, not interchangeable

| Signal | Mechanism | Fits |
|---|---|---|
| **Accumulated work** | counter vs. `constant_floor + scale_factor × size` | Curation |
| **Content delta** | observed fingerprint ≠ current fingerprint | Conformance, Coherence |
| **Elapsed time** | now − last successful run | Mining, Currency |
| **Heartbeat absence** | dead-man's switch | proving the *runner* lives, not the chore |

The two-part threshold — a constant floor plus a term proportional to size — is worth
copying verbatim; Postgres (`autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor
× reltuples`) and git (`maintenance.<task>.auto`) converged on it independently, so small
units do not churn and large ones do not starve.

Content delta is strictly better than a timestamp for repo-resident work: it never
reports a chore stale when nothing it inspects has changed, and it reports immediately
when something has. Kubernetes calls the same idea `observedGeneration`; `make` has used
mtimes for it since 1976.

**How each signal is specified in its home system:**

- **Accumulated work — Postgres.** `vacuum threshold = Min(autovacuum_vacuum_max_threshold,
  autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × reltuples)`, with a
  separate analyze pair and an insert-driven pair. Wraparound is the one *absolute*
  trigger: a table is always vacuumed once `relfrozenxid` passes
  `autovacuum_freeze_max_age`. **Postgres keeps two surfaces apart:** the *decision* reads
  accumulated work (`n_dead_tup` against the threshold), while the *human-facing*
  display reads timestamps (`last_vacuum`, `last_autovacuum`, `last_analyze`). A chore
  system can decide by one signal and show another. The scale-factor default reads 0.1 in
  the current manual and 0.2 across much secondary literature: **cite the parameter,
  never the number** — the same rule gzkit applies to its own thresholds.
- **Accumulated work — git.** `maintenance.<task>.auto` carries a shared three-valued
  semantic: `0` never runs under `--auto`, a negative value forces every run, a positive
  value runs when the observed count reaches it. `git gc --auto` *"checks whether any
  housekeeping is required; if not, it exits without performing any work."*
- **Content delta — `make`.** *"The recompilation must be done if the source file, or any
  of the header files named as prerequisites, is more recent than the object file, or if
  the object file does not exist."* A target is stale relative to what it depends on,
  never relative to how long ago.
- **Content delta — Kubernetes.** *"if `.metadata.generation` is currently 12, but the
  `.status.conditions[x].observedGeneration` is 9, the condition is out of date with
  respect to the current state of the instance."* For a chore: record the fingerprint of
  the inputs it last observed — commit SHA, a content hash of the scanned surface, a
  corpus fingerprint.
- **Elapsed time — Prometheus practice.** There is no registered standard metric name;
  the stable convention is a gauge of Unix seconds named
  `<prefix>_last_<thing>_timestamp_seconds` (the naming doc's example is
  `data_pipeline_last_record_processed_timestamp_seconds`), set **only on success** and
  queried as `time() - metric > threshold` (Robust Perception's batch-job idiom alerts on
  `time() - mybatchjob_last_success > 3600 * 26`; Pushgateway adds `push_time_seconds` and
  `push_failure_time_seconds` per group). **The timestamp is the failure detector.**
  Push only on success and the value ages on its own when a run fails; a separate "did
  it fail?" boolean is redundant and tends to go stale too. The trap is the converse:
  anything that re-stamps on failure hides the failure.
- **Heartbeat absence — the dead-man's switch.** Alert when something good *stops*
  firing. Prometheus's `Watchdog` alert is always firing and is routed to an external
  receiver that pages when the heartbeat stops. The design rule generalizes: **the
  watcher must not be part of the thing it watches**, or the failure takes the noticer
  with it. For gzkit, a staleness announcement that runs only when a session runs cannot
  report that sessions stopped — acceptable for an indicator, and worth knowing.

### Graded bands

| Band | HTTP (RFC 9111 / 5861) | Cron monitoring | Loudness |
|---|---|---|---|
| current | `fresh` | `up` | silent |
| **due** | `stale`, still serveable | **`late`** | **announced** |
| overdue | `must-revalidate` | `down` | loud |
| **paused** | — | **`paused`** | silent, and not a failure |

Two declared numbers, not one: **Period** (*"the expected time between pings"*) and
**Grace Time** (*"the additional time to wait before sending an alert when a check is
late"*).

Healthchecks.io schedules nothing; it only observes pings against a declared
expectation. Its state machine runs `new → up → late → down`, plus `paused`: a check goes
**late** when the period expires and **down** only after grace elapses. RFC 9111 supplies
the vocabulary — *"A 'fresh' response is one whose age has not yet exceeded its freshness
lifetime"*, with `response_is_fresh = (freshness_lifetime > current_age)` — and §4.2.4
makes stale **usable by default**, with `must-revalidate` as the opt-in that makes it
unusable. RFC 5861's `stale-while-revalidate` exists so a stale response can be served
*"without blocking"* while revalidation happens. **The middle band is the whole design:**
it is where the operator is told a chore is due without anything being claimed broken.
(The five-state list came through a documentation summarizer; the Period and Grace Time
definitions are verbatim.)

**The scheduler is genuinely optional, and mature systems say so.** git's `run`,
`is-needed` and `--auto` all work with no scheduler; scheduling sits behind an explicit
`git maintenance start --scheduler=auto|crontab|systemd-timer|launchctl|schtasks` that
uses the operating system's scheduler rather than its own. Enablement
(`maintenance.<task>.enabled`) and cadence (`maintenance.<task>.schedule`) are separate
fields from the task definition. **The declared expectation is a property of the unit;
the invocation is somebody else's problem.** That separation is what lets one registry
serve an operator who keeps the cadence today — *"I maintain frequency"* — and a
scheduler later, without redefining a single chore.

**`paused` is load-bearing for gzkit specifically.** 23 of 39 chores last ran
2026-07-31. Without an intentional-dormancy state, enabling indicators paints the whole
board red and the display decays into noise within a quarter.

### Indicator, not gate

Operator ruling, 2026-09-12: *"indicators, chores shouldn't have a bunch of gates like
the adr/obpi system"* and *"staleness suggests need for a chore run — letting trash pile
up in the household would surely be preceded by foul odors, so staleness should be
announced."*

Staleness **announces**. The one exception is Currency, where staleness makes the chore
assert something false; that class may gate.

This is not a concession. Sheridan & Verplank's Level 7 — *"Executes automatically, then
necessarily informs the human"* — makes disclosure the obligation that licenses standing
authorization at all. The announcement *is* the thing that makes pre-authorized
autonomous action defensible.

### Derive last-run from the artifact

`scripts/check_proof_freshness.py` already implements two of the four signals and
already reasons correctly about why: it compares **git commit dates, not filesystem
mtimes**, because *"a fresh clone or a branch switch rewrites every mtime, which would
make an mtime comparison report whatever the checkout did last."*

Generalize it. Do not build a parallel register — node_exporter's
`node_textfile_mtime_seconds` is the precedent: derive the last-run signal from the
proof artifact itself. One fewer thing to keep honest.

> **Caution.** `git` *documents* a `maintenance.<task>.lastRun` config field and **does
> not implement it** (verified 2026-09-12 four ways: source grep, code search, binary
> `strings`, empirical run). Cite git for `is-needed` and per-task thresholds; never for
> last-run bookkeeping.

---

## Suppression — the fifth posture, prohibited

A chore may **never** discharge a finding by suppression.

`ruff --add-noqa`, `ty --add-ignore`, `pyrefly suppress`, `bandit # nosec` all write to
source, **turn the exit code green, and change nothing about correctness**. Observed:
`ty --add-ignore` takes a file from exit 1 to exit 0 with both type errors still
present.

For gzkit this is not theoretical. Measured in `src/gzkit` on 2026-09-12:

| | count |
|---|---|
| `# noqa` total | **741** |
| `noqa: PLC0415` | **393** — suppressing a rule that is **not in `[tool.ruff.lint] select`** |
| `noqa: BLE001` | 28 |
| `type: ignore` / `ty: ignore` | 51 |

`pyproject.toml` already catalogues this failure class in its own comments: a
`# noqa: BLE0001` typo that suppressed nothing and was undetectable *because the rule
was off*. 393 PLC0415 suppressions are the same shape at 65× the scale.

**gzkit's attestation evidence is exit codes.** A posture that turns exit codes green
without changing correctness is therefore not a lesser repair — it is the manufacture of
false evidence, and it belongs in neither the audit nor the repair bucket.

**A repair run's exit 0 is not "nothing was found" either.** This is a neighboring
hazard, not suppression, and a chore's evidence must not conflate the two readings. In
`pip-audit` fix mode the gate is `if pkg_count != fixed_pkg_count: sys.exit(1)` (source,
not documentation), so a `--fix` run that repairs everything exits **0** despite having
found vulnerabilities. `ruff check --fix-only` exits 0 on leftovers by design; ruff
offers `--exit-non-zero-on-fix` and `ruff format --exit-non-zero-on-format` precisely so
a run can repair *and* report drift. A repair-rung chore's result must say whether the
subject was already clean or was made clean. Note also `pip-audit`'s stance on its own
signal: *"`pip-audit`'s exit code cannot be suppressed."*

If a fenced exception is ever wanted, `bandit`'s discipline is the model: narrow scope
(`# nosec B602, B607`, because *"a separate vulnerability may be added to the line later
causing the new vulnerability to be ignored"*), a recorded justification, and an
`--ignore-nosec`-style override that ignores all suppressions during audit runs.

---

## Declared non-authority

**Every fixer surveyed publishes what it will not touch, with a reason.** This is the
one convention that was unanimous.

- `pip-audit` — *"We don't support fixing dependencies in lockfiles, since **lockfiles
  should be managed/updated by their packaging tool**."*
- `safety` — *"Safety CLI does not download or install packages. Instead, requirements
  files are updated."*
- `autovacuum` — *"will never issue `VACUUM FULL`."*

gzkit invented this independently: `docs/governance/capability-control-review-2026-09-12.md`
carries a `## What this record does not license` section. It should be a **required
field of every chore**, not an artifact of one document.

And "there is no repair" must be a **declared value, never an absence.** CSAF's
remediation `category` enum is the model — `no_fix_planned` (deliberately
diagnosis-only) and `none_available` (repair not yet built) are first-class members, and
the schema requires `["category", "details"]` so a bare category cannot be emitted.
Empty is indistinguishable from unfinished.

**This is the remedy for the nine.** They are not nine hand-edits; they are nine
violations of one class contract: *Coherence and Mining must carry a remediation field,
whose value may be `no_fix_planned` — but never nothing.*

Three systems independently require remediation prose on a finding that stops short of
repair:

- **Django's System Check Framework** — *"a set of static checks for validating Django
  projects. It detects common problems and provides hints for how to fix them."* Each
  `CheckMessage` carries `level`, `msg`, **`hint`**, `obj` and a stable **`id`**, is
  registered with a tag, and `manage.py check --fail-level` sets which level exits
  non-zero (*"Default is ERROR"*). A registry of named diagnostic units, each with a
  stable id, a severity, a selection tag, a hint by convention and a caller-tunable exit
  threshold — the closest structural analogue to a gzkit chore finding.
- **CSAF** — *"Specifies details on how to handle (and presumably, fix) a
  vulnerability"*, with `required: ["category", "details"]`. Its `restart_required`
  category enumerates the **disruption cost** of applying a remediation — `connected`,
  `dependencies`, `machine`, `none`, `parent`, `service`, `system`,
  `vulnerable_component`, `zone` — a declared cost field a chore's repair could carry.
- **SARIF** — *"A `fix` object represents a proposed change that addresses a result"*;
  `fix.description` sits beside the machine-applicable `artifactChanges`, which the
  schema requires to be non-empty. The result and the fix are separate linked objects, a
  fix is machine-applicable but normatively a *proposal*, and the consumer decides
  whether to apply it. (SARIF section quotes came through a summarizer of the OASIS
  errata document; they agree with the schema's own constraints.)

osv-scanner ships the most explicit remediation-risk vocabulary seen — `in-place`,
`relax`, `override`, with *"'In-place'… is usually less risky, but will often fix less
vulnerabilities than the relax strategy"* — but its fixer supports npm and Maven, not
Python.

---

## The declaration, and the fence

Declaration is metadata on the unit; the runner enforces it. This is the single most
consistent finding across every registry surveyed — **nobody leaves it to naming or to
the reader.**

| System | Declaration | Enforcement when undeclared |
|---|---|---|
| ESLint | `meta.fixable` / `meta.hasSuggestions` | a rule that fixes without declaring ⇒ **hard error** |
| Ansible | `supports_check_mode` | module is **skipped, not run** — absence defaults to the *safe* reading |
| Ruff | per-fix `applicability` | machine-readable; re-gradable per rule in both directions |
| git | `maintenance.<task>.{enabled,schedule,auto}` | `gc` excluded from the default preset by policy |
| CSAF | `required: ["category","details"]` | a remediation **cannot exist** without both |

Required per-chore fields:

| Field | Values |
|---|---|
| `class` | `conformance` · `coherence` · `curation` · `mining` · `currency` |
| `rung` | `observe` · `propose` · `repair` · `operator-only-repair` |
| `staleness.signal` | `accumulated-work` · `content-delta` · `elapsed-time` |
| `staleness.period` / `.grace` | the two declared numbers |
| `staleness.paused` | intentional dormancy, distinguishable from neglect |
| `remediation` | `vendor-fix` · `workaround` · `no_fix_planned` · `none_available` — plus required details |
| `non_authority` | what this chore refuses to touch, and why |
| `governing_rule` | the `.gzkit/rules/**` clause it serves, or an explicit `none` |

Ansible's failure direction is the one to copy: **absence defaults to the safe reading.**
An undeclared chore does not run. Verbatim: *"Modules that support check mode report the
changes they would have made. Modules that do not support check mode report nothing and
do nothing."* Its developer guide makes read-only a contract for a whole class: info and
facts modules *"MUST support check_mode"* and *"MUST NOT make any changes to the
system."*

**Naming is not a declaration.** pre-commit-hooks is the natural test. Classified by
reading each hook's code for actual writes (34 ids, 2 tombstones):

| Naming class | Count | Modifying | Reporting |
|---|---|---|---|
| `check-*` prefix | 16 | **0** | 15 (+1 tombstone) |
| `*-fixer` suffix | 3 | **3** | 0 |
| `fix-*` prefix | 2 | 1 | 0 (+1 tombstone) |
| no marker | 13 | 5 | 8 |

`check-*` ⇒ reporting and `-fixer` / `fix-*` ⇒ modifying hold with zero counterexamples,
but five modifying hooks carry no marker at all (`trailing-whitespace`,
`file-contents-sorter`, `sort-simple-yaml`, `mixed-line-ending`,
`pretty-format-json --autofix`). **A reliable positive marker, not an exhaustive
partition.** pre-commit itself has no linter/formatter vocabulary — no hook field, config
key or schema enum encodes the difference; its distinction is behavioral and discovered
at runtime. A gzkit chore named `*-audit` or `*-coherence` has declared nothing, and the
three contradictory chores are the local proof.

**What happens when nothing is declared** is on record too. Rails/rake has no
convention distinguishing read-only from mutating tasks — only `desc`-gated visibility
(*"Only tasks with descriptions will be displayed with the `-T` switch"*), namespacing,
and third-party confirmation gems. The gap was real enough that people patched it, and it
was never standardized.

---

## The indicator surface — command-line conventions

Step 2 of § Implementation order builds a command. The research surveyed how the tools
this project already depends on spell diagnosis, preview and repair, and what their exit
codes mean. This section records it so the verb is designed against conventions rather
than against memory. **gzkit's own CLI doctrine governs** where they conflict
(`AGENTS.md` § Behavior Rules — Always #15; `.gzkit/rules/cli.md`); the ecosystem is
evidence, never authority.

### Diagnosis is a verb with an exit status

Mature systems answer *"is maintenance needed?"* with a dedicated question whose answer
is the exit status, not with a mode flag bolted onto the repair verb:

- `make -q` — *"Question mode. Do not run any commands, or print anything; just return an
  exit status that is zero if the specified targets are already up to date, nonzero
  otherwise."*
- `git maintenance is-needed` — *"Check whether maintenance needs to be run without
  actually running it. Exits with a 0 status code if maintenance needs to be run, 1
  otherwise."* **The polarity is inverted from `make -q`**: exit 0 means work is needed.
  Two canonical question verbs disagree on what zero means, which is reason enough to
  document the polarity of any gzkit status verb explicitly.
- Django's `--check` family — *"exit with a non-zero status when"* the condition is
  detected (`makemigrations --check`, `migrate --check`, `optimizemigration --check`).
- `git fsck` — *"Verifies the connectivity and validity of the objects in the database"*,
  a pure check with no repair sibling in the same verb.
- The GNU Coding Standards' *Standard Targets* reserve **`check`** as the verifying
  target (*"Perform self-tests (if any)"*) beside `installcheck`, `clean`, `distclean` and
  `maintainer-clean`, which carries an explicit danger note: *"This command is intended
  for maintainers to use; it deletes files that may need special tools to rebuild."* The
  read-only/mutating distinction there is by naming only — nothing mechanical enforces it.

**Tension with the operator's ruling, recorded not resolved.** An exit-status answer is a
gate-shaped signal. The operator ruled staleness an *announced indicator*, gating only
where the subject decays. Whether the planned status verb exits non-zero on overdue chores,
and under which flag, is a design decision for step 2 — and the four-code map below
already reserves 3 for policy breach.

### `--check` asserts state; `--dry-run` previews a mutation

They are not synonyms. `uv` ships both on the same subcommands (observed, `uv` 0.12.5):

```
uv sync --check      Check if the Python environment is synchronized with the project
uv sync --dry-run    Perform a dry run, without writing the lockfile or modifying the
                     project environment
uv lock  --check     Check if the lockfile is up-to-date
uv lock  --dry-run   Perform a dry run, without writing the lockfile
```

- **`--check` is a state predicate** — "is the world already correct?" — answered as a
  boolean exit code.
- **`--dry-run` is a mutation preview** — "what would this command do?" — answered as a
  plan on output.

Django composes the two: `makemigrations --check` *"Implies `--dry-run`."* `make` ships
four spellings of its preview flag (`-n`, `--just-print`, `--dry-run`, `--recon`), which
is why "dry run" is the term everyone recognizes. Terraform `plan` and Puppet `--noop` are
the infrastructure forms.

Where each lives:

| Domain | `--dry-run`? |
|---|---|
| `pip install`, `uv sync` / `lock` / `publish`, poetry (12 subcommands), `pip-audit` | yes |
| ruff, black, isort, autoflake, docformatter, autopep8, yapf, the pyupgrade family | **no — zero occurrences across 17 primary sources** |
| mypy, pyright, ty, bandit | no |
| `pyrefly infer` | yes — the one source-rewriting exception, 2025-era and experimental |

**The source-artifact family spells it differently.** `--check` is the settled diagnostic
flag (black, `ruff format`, autoflake, docformatter; isort's `--check-only` accepts
`--check` as an alias) and **`--diff`** is its universal companion — `--check` says
*whether*, `--diff` says *what*; black documents the two as composable. Repair is opted
into by **`--fix`** where the tool decides *what* to change (ruff, ty, pip-audit;
safety's `--apply-fixes`) or **`--in-place`** where the output is a whole rewritten file
and the only question is where it goes (autopep8, yapf, autoflake, docformatter). No
surveyed tool spells top-level repair `--repair`, `--remediate` or `--autofix`. The
pyupgrade family has no check mode at all — rewriting *is* the diagnostic and the
non-zero exit *is* the report — and autopep8 signals change through its exit code only
with `--exit-code`, numbering drift 2. autopep8's repeatable `--aggressive` is a *scope*
dial, not a safety tier, and isort's `--atomic` (refuse to save syntax-broken output) is
self-verification of the same kind as black's `--safe`.

### The vocabulary the field has settled on

Recorded so gzkit's names for the chore system are chosen against it, not reinvented.

- **The work:** *toil* (SRE) · *housekeeping* and *maintenance tasks* (git) · *routine
  maintenance* (Postgres) · *chore* (commitlint's `type-enum` — not the Conventional
  Commits spec, and no longer Angular)
- **The diagnose side:** *check* · *is-needed* · *question mode* · *dry run* · *check
  mode* · *no-op* · *plan* and *speculative plan* · *probe* · *verify* / *fsck* · *static
  check*
- **The repair side:** *run* · *apply* · *fix* (safe / unsafe) · *suggestion* ·
  *remediation* (`vendor_fix` / `mitigation` / `workaround` / `none_available` /
  `no_fix_planned`) · *reconcile*
- **The staleness side:** *fresh* / *stale* / *freshness lifetime* / *age* (RFC 9111) ·
  *period* / *grace time* / *late* (cron monitoring) · *last success timestamp* ·
  *threshold plus scale factor* · *observedGeneration* · *out of date* (make) ·
  *dead-man's switch* / *watchdog*
- **The consequence side:** *level-triggered versus edge-triggered* · *desired state*
  (`spec`) versus *observed state* (`status`) · *safe for background execution* (git) ·
  *supports check mode* (Ansible) · *fixable* (ESLint)

**gzkit's own vocabulary leans the other way.** Measured 2026-09-13 across `src/gzkit`:
`"--dry-run"` 12, `"--apply"` 6, `"--write"` 3, `"--fix"` 3, `"--check"` 3. That is the
packaging-and-environment convention (`--dry-run` / `--apply`, the pip, uv and poetry
family), not the source-artifact one. Both are legitimate and answer different
questions. **Decide per verb:** if a chore answers "is this already clean?", `--check`
conforms; if it simulates a multi-step mutation, `--dry-run` does. Note that `--apply`,
gzkit's existing repair spelling, is exactly the spelling the source-rewriting family
never uses.

### Exit codes

| Code | Ecosystem status |
|---|---|
| **0 = clean** | universal — the only value every tool agrees on |
| **1 = findings** | strong majority: ruff, black, ty, pyright, mypy, flake8, bandit, isort, autoflake, pyupgrade, pip-audit, `ruff format` |
| **2 = usage or config error** | strong majority: ruff, ty, mypy, bandit, black, pyright (which splits it 3 / 4) |

Ruff names the lineage: *"This convention mirrors that of tools like ESLint, Prettier,
and RuboCop."* Then it fragments. black uses **123** for an internal error;
docformatter **3** for "would reformat"; autopep8 **2** for differences and 99 for
argparse errors; yapf's `--diff` deliberately conflates drift with crash; pylint's exit
code is a **bitmask** (1 fatal, 2 error, 4 warning, 8 refactor, 16 convention, 32 usage,
so *"an exit code of 20 means there was at least one warning message (4) and at least
one convention message (16)"*); ty and pyrefly use **101** for a panic, the Rust
convention; safety uses sysexits-style codes from 64, undocumented; pyright alone
distinguishes config-parse failure (3) from bad arguments (4). mypy's exit codes are
undocumented — python/mypy#6003 has been open since 2018-12-04.

Two stdlib anchors: **argparse exits 2 on a usage error** (observed), almost certainly
why 2 means usage error across the ecosystem; and **`os.EX_*`** (BSD sysexits:
`EX_USAGE=64`, `EX_DATAERR=65`, `EX_SOFTWARE=70`, …) exists in stdlib and the linting
ecosystem essentially ignores it. The escape hatch is a real convention — `--exit-zero`
in ruff, ty, flake8, bandit and pylint — and pip-audit is the deliberate holdout.

**gzkit's four-code map is authoritative here and differs from the ecosystem.**
`.gzkit/rules/cli.md` § Exit Codes: `0` success, `1` user or config error, `2` system or
IO error, `3` policy breach. `scripts/check_proof_freshness.py`, which step 2
generalizes, already returns 3 on stale evidence.

> **Defect found while writing this section (2026-09-13).** `StableArgumentParser.error()`
> in `src/gzkit/cli/parser.py` exits **2** on a parse error, and its docstring calls that
> *"consistent with the CLI Doctrine 4-code map"*. The map assigns 2 to system/IO errors
> and 1 to user errors. Observed: `uv run gz chores --bogus-flag` exits 2. The two
> surfaces disagree with no declared authority, and argparse's default sides with the
> parser. Recorded as a defect insight in `.gzkit/insights/agent-insights.jsonl`
> (scope `cli/exit-codes`); an exit-code change is contract-bearing, so it is the
> operator's to route.

---

## Implementation order

1. **Registry schema** — the fields above, plus a `paused` state.
<!-- gz-validate-skip: command-shape -->
2. **`gz chores status`** — the indicator surface. Reads proof commit dates, renders
   current / due / overdue / paused. Announces; never gates. Generalizes
   `scripts/check_proof_freshness.py` rather than building a parallel register, and
   puts the overdue announcement in `scripts/session_orientation.py`. GHI #936 —
   *"chore currency gates are only readable by running the chore they gate"* — is the
   existing work order for this step, and its Expected section names that announcement
   site.
3. **Class-conformance validator** — the ESLint/Ansible move. A chore whose `CHORE.md`
   contradicts its declared rung fails. This is what makes "internally consistent"
   mechanical rather than aspirational, and it retires the three contradictory chores and
   the nine stop-at-data chores in one pass.
4. **`src/gzkit/chores/README.md`** — today a packaging contract that never says what a
   chore *is*. It gains the class definitions, the ladder, the admission criterion, and
   the declaration requirement.
5. **Per-chore declarations** — by this point data entry against a validator, not 40
   judgment calls. This step applies § Operator directives: it fixes the three
   contradictory chores, remedies the nine that stop at data, calibrates the
   control-surface five individually rather than as a block, and resolves the Pass D
   label collision recorded in
   [`rules-tools-audits-refactors-alignment.md`](rules-tools-audits-refactors-alignment.md).
   GHI #997 (`eval-feedback-cluster` runs fixtures, not live clustering) and GHI #808
   overlap members of the nine; read both before declaring those chores.
6. **The suppression prohibition in a rule file** — § Suppression, stated as binding
   rule text where chore authors and runners load it, with its witness designed
   alongside so it does not land as a new Promotable row.

Cadence precedes content: adding classes to a registry nothing surfaces multiplies
dormant surface that *reads as coverage*.

**Work orders.** GHI #936 covers step 2. Steps 1 and 3–6 have no GHI. The Movement C
box discharges through *"GHI-shaped direct repair"*, so one issue filed through
`/ghi-author` is the natural carrier. That filing is advised and not yet ruled on.

**Follow-on, once `governing_rule` exists:** the rule ↔ chore pass and the middle-scale
rule clauses in
[`rules-tools-audits-refactors-alignment.md`](rules-tools-audits-refactors-alignment.md)
§ Advised order.

---

## What this record does not license

- **It does not close the Movement C box.** That box's criterion is class-level — *"it
  closes the family rather than the instance"* — and its 2026-08-08 amendment records
  that all six named exemplars closed while the box did **not** discharge. This work
  advances the agent-side arm. Checking the box on its strength would be the
  enumerate-the-exemplars habit the criterion was written to resist.
- **It does not authorize a new ADR or OBPI.** Operator ruling: discharge under the
  Movement C box, no new ADR.
- **It does not admit any chore to the registry.** Admission is operator-directed on
  recurrence evidence.
- **It does not re-open settled rulings.** `.gzkit/rules/pythonic.md` § Imports records
  that the lazy-import posture is *"ACCEPTED, not deferred (operator ruling
  2026-08-08)"* and that reclassification does not follow from *"the count moving."*
  Nothing here disturbs that.
- **It does not make the external exemplars authoritative.** They are cited so the
  reasoning is auditable. gzkit's needs govern.

---

## Research limits — what the three threads could not verify

Carried from each research report's own "do not assert" list, so the limits travel with
the findings.

**Autonomy and human-in-the-loop thread.**

- Billings's verbatim definitions of management by consent and by exception — the NASA
  TM PDF exceeded the fetch limit; secondary sources only.
- The Dropbox SREcon16 abstract and its "Human Authorized Execution" phrasing — USENIX
  returned 403; search extraction only.
- FDA clinical decision support criterion 4 (21 U.S.C. §360j(o)(1)(E)) — the
  "independently review the basis" criterion is corroborated by several law-firm
  analyses of the revised final guidance (January 2026), but the statutory text was not
  retrieved. The pattern is worth pursuing separately: a regulator declaring the
  diagnose/act boundary, with the discriminator being whether the human can meaningfully
  review the basis — the sharpest external answer to the rubber-stamp problem found.
- Any peer-reviewed source on closed-loop auto-remediation guardrails. Vendor material
  converges on a manual → semi-automatic → full-automatic ladder; no academic or standards
  anchor exists. A genuine gap.
- Any primary source applying Bezos's door framework to agent authorization — the
  application is an extension.
- A formal definition of "blast radius" — none exists. It is load-bearing industry jargon
  with stable operational meaning (AWS re:Invent 2018 ARC338, *How AWS Minimizes the Blast
  Radius of Failures*), not a measured quantity.
- Anthropic naming specific escalation triggers — widely paraphrased, not in the primary
  post.
- Cursor hook extensibility; a Codex CLI per-command persistent allowlist beyond mode and
  sandbox configuration; OpenHands' LOW/MEDIUM/HIGH risk rubric — none found in primary
  documentation.
- Parisel, *A Theory of Least Autonomy in AI* (arXiv:2607.09744, 2026) — generalizes least
  privilege to composition with a per-agent blast-radius budget. Recent, single-author,
  no adoption found; cite the framing, not the formalism.
- Ansible's documentation defines idempotence as a property; the conclusion "therefore
  safe to run unattended" appears in secondary sources, not Ansible's primary text.
  Puppet's equivalent page was not verified.

**Housekeeping and staleness thread.**

- `maintenance.<task>.lastRun` is documented by git and not implemented (§ Staleness).
- Angular no longer defines `chore`; the live definition is commitlint's.
- Healthchecks.io's five-state list and the SRE Workbook's strategies and taxonomy came
  through summarizers.
- SARIF section quotes came through a summarizer of the OASIS document.
- The Postgres scale-factor default differs between the current manual and secondary
  literature.
- JVM and Go garbage collection, LSM-tree compaction (RocksDB, Cassandra) and index
  rebuild strategies (`REINDEX CONCURRENTLY`, Elasticsearch force-merge) were in the brief
  and **not researched**; Postgres and git were judged sufficient, and agreement from the
  others is not asserted.
- Highest-confidence citations — fetched raw and grepped: CSAF, commitlint,
  node_exporter, git source, Angular's guidelines, Kubernetes API conventions.

**Python check/fix conventions thread.**

- mypy's exit codes have no documented source; 0/1/2 is observed.
- Why ty has no `--unsafe-fixes`, and what class of fix ty's `--fix` applies — ty's
  documentation is silent; one changelog line (0.0.73, *"Do not prefer unsafe fixes in
  the language server"*) proves an internal tier exists.
- The exit codes of pyupgrade, add-trailing-comma and reorder-python-imports are
  source-verified only; their READMEs are silent.
- isort's `--diff` combined with `--check-only` works in source and is undocumented.
- docformatter returns 3 in default diff mode too, wider than its documentation states.
- autopep8's and yapf's default-to-stdout behavior is observed, not documented.
- safety's documentation contradicts its 3.8.1 source in two places (a nonexistent
  `-afl` flag, a mismatched positional threshold form); safety's free-versus-paid gating
  on `--apply-fixes` is server-side and unobservable.
- `pyrefly infer --dry-run` exit semantics came from a search summary.
- pip-tools `--dry-run` could not be verified (documentation pages returned 404).
- ruff claims style-output compatibility with black, never CLI-flag compatibility.
- The causal link between pre-commit's stash and its modification detection is
  inference; pre-commit's rationale lives only in the maintainer's tracker comments, and
  that search is not provably exhaustive.

---

## Reproduction record

```bash
# chore count — from the registry, not a directory listing. `.gzkit/chores/` also holds
# a non-chore data directory, `owasp-top10-2025-scan/` (present since 2026-05-10), so
# `ls -d .gzkit/chores/*/ | wc -l` returns 41 against 40 registered chores. This record
# originally cited that listing for its 40; corrected 2026-09-13. The canonical wheel
# registry, src/gzkit/chores/registry.json, holds 37.
python -c "import json,pathlib;print(len(json.loads(pathlib.Path('.gzkit/chores/registry.json').read_text())['chores']))"

# declared posture, recommendations, remediation steps
grep -rlniE 'audit-only|audit only|zero edits|does NOT fix|diagnosis only|read-only' \
  .gzkit/chores/*/CHORE.md | wc -l

# acceptance-criteria shape (presence-gated vs state-gated)
grep -h '"command"' .gzkit/chores/*/acceptance.json | grep -c 'test -f'

# freshness wiring
grep -l 'check_proof_freshness' .gzkit/chores/*/acceptance.json | wc -l

# declared cadence, and whether anything schedules a chore
python -c "import json,pathlib;r=json.loads(pathlib.Path('.gzkit/chores/registry.json').read_text());print(sum(1 for c in r['chores'] if c.get('frequency')),'of',len(r['chores']))"
grep -rn 'gz chores' .github/workflows/ .pre-commit-config.yaml .claude/hooks/ 2>/dev/null

# real last-run per chore (ISO run headings written by `gz chores run`)
for f in .gzkit/chores/*/proofs/CHORE-LOG.md; do
  printf '%s %s\n' "$(basename "$(dirname "$(dirname "$f")")")" \
    "$(grep -oE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}' "$f" | tail -1)"
done | sort -k2 -r

# suppression inventory
grep -rn 'noqa' src/gzkit --include='*.py' | wc -l
grep -rn 'noqa: PLC0415' src/gzkit --include='*.py' | wc -l
uvx ruff check --select PLC0415 src/gzkit    # the rule is NOT in [tool.ruff.lint] select
```

## Sources

Parasuraman, Sheridan & Wickens, *A Model for Types and Levels of Human Interaction with
Automation*, IEEE Trans. SMC-A 30(3), 2000 · Sheridan & Verplank, *Human and Computer
Control of Undersea Teleoperators*, MIT, 1978 · IBM, *An Architectural Blueprint for
Autonomic Computing*, 2005 · Google, *Site Reliability Engineering* ch. 5 "Eliminating
Toil" and ch. 7 "The Evolution of Automation at Google" · PostgreSQL manual ch. 24
*Routine Database Maintenance Tasks* · `git-maintenance(1)`, `git-gc(1)` · Kubernetes
*Controllers*, *Probes*, and `sig-architecture/api-conventions.md` · GNU Make manual,
*How Make Works* · Django *django-admin reference* and *System check framework* · RFC
9111 (HTTP Caching) · RFC 5861 (`stale-while-revalidate`) · Prometheus *Metric and label
naming*; `node_exporter` textfile collector · Healthchecks.io *Configuring checks* ·
OASIS *SARIF 2.1.0* · OASIS *CSAF 2.0* JSON schema · ESLint *Custom rules* · Astral
*Ruff — The Linter* (fix safety) · Astral *ty* CLI reference · `pre-commit` *New hooks*
and maintainer rationale (pre-commit/pre-commit#285, #747, #806) · HashiCorp *Terraform
plan/apply* · Ansible *Check mode* · `pip-audit`, `safety` · AWS Well-Architected,
Operational Excellence design principles · Anthropic, *How we contain Claude* (2026) ·
OpenAI, *Practices for Governing Agentic AI Systems* (2023) · Feng, McDonald & Zhang,
*Levels of Autonomy for AI Agents*, Knight First Amendment Institute (2025) · Crootof,
Kaminski & Price, *Humans in the Loop*, 76 Vand. L. Rev. 429 (2023) · Bainbridge,
*Ironies of Automation*, Automatica 19(6), 1983 · Saltzer & Schroeder, *The Protection of
Information in Computer Systems*, 1975 · Renovate *automerge* docs · Billings, *Aviation
Automation: The Search for a Human-Centered Approach*, 1997, and NASA TM-110381, 1996
(secondary sources only — see caveat) · Elish, *Moral Crumple Zones*, Engaging Science,
Technology, and Society 5, 2019 · Morris et al., *Levels of AGI*, arXiv:2311.02462 ·
Amazon.com 2015 Letter to Shareholders · Chef documentation (convergence) · Chow, *On
Optimum Recognition Error and Reject Tradeoff*, IEEE Trans. Inf. Theory, 1970 · Madras,
Pitassi & Zemel, *Predict Responsibly*, NeurIPS 2018 · Google, *The Site Reliability
Workbook*, "Eliminating Toil" · GitHub *About Copilot coding agent* · OpenAI Codex *agent
approvals & security* · PagerDuty *Escalation policies* · Model Context Protocol
specification 2025-06-18, *Elicitation* · Docherty / Human Rights Watch, *Losing
Humanity*, 2012 · DoD Directive 3000.09, *Autonomy in Weapon Systems*, 2012 (updated 2023)
· Shi & DiFranzo, arXiv:2602.09286, 2026 · Cheng & Cheng, arXiv:2604.23049, 2026 · IBM,
autonomic computing maturity levels (z/VSE technical conference, 2004) · Blackmore,
*The Six Levels of Agentic Software Engineering*, Dash0, 2026 (practitioner synthesis) ·
Anthropic, *Building Effective Agents*, 2024 · Claude Code, Cursor, Devin and OpenHands
permission documentation · Nygard, *Release It!*; Fowler, *CircuitBreaker* · Geifman &
El-Yaniv, NeurIPS 2017 · Mozannar & Sontag, ICML 2020 · LangGraph *interrupts* · OpenAI
Agents SDK *guardrails* · AutoGen `human_input_mode` · Sarter & Woods, Human Factors 37,
1995 · Dropbox, SREcon16 Europe (unverified) · Parisel, arXiv:2607.09744, 2026 (weak) ·
Kubernetes *Liveness, Readiness and Startup Probes* · GNU Coding Standards, *Standard
Targets* · Rake documentation · Conventional Commits 1.0.0; `@commitlint/config-conventional`;
Angular commit message guidelines; the original AngularJS commit conventions gist · Prometheus
*Pushing metrics*; Robust Perception, *Monitoring batch jobs in Python*; PromLabs watchdog
alerts · black, isort, autoflake, docformatter, autopep8, yapf, pyupgrade, mypy
(python/mypy#6003), pyright, pyrefly, bandit, flake8, pylint and osv-scanner
documentation and source · `uv`, pip and poetry CLI references · python/cpython
`argparse` and `os.EX_*` (observed) · pre-commit/pre-commit#2346 · Research transcripts:
session `5f61ae2b`, 2026-09-12 — subagents `ade19cb02045dc739` (autonomy and
human-in-the-loop), `a8c96828c63ff41ae` (housekeeping and staleness) and
`a5d9f4b1dd63cfb20` (Python check/fix conventions), preserved under the session's
`subagents/` directory in the harness transcript store.
