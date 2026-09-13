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
novel problems."*

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
  operator ruling worth recording; a dismissed one is not a ruling at all.

---

## The admission criterion

**Not every refactoring is a chore.** Operator, 2026-09-12: *"not all refactorings are
chores, but most chores can lead to refactorings."*

Google SRE supplies the test. Toil is *"manual, repetitive, automatable, tactical,
devoid of enduring value, and … scales linearly as a service grows."* Two
characteristics decide admission:

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
An undeclared chore does not run.

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
specification 2025-06-18, *Elicitation* · Research transcript: session `5f61ae2b`,
2026-09-12, three background research threads (autonomy and human-in-the-loop;
housekeeping and staleness; Python check/fix conventions).
