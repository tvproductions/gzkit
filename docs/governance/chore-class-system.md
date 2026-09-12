# The chore class system — 2026-09-12

> **Status:** design record, operator-ratified 2026-09-12. Discharges under the
> `doctrine-declared-without-mechanism` box of Movement C ("Reduce the accretion")
> in the active campaign — **agent-side arm**: *a skill mandate with no receipt*.
> Advances that box; does not close it. See § What this record does not license.

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
ADR.**

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
   current / due / overdue / paused. Announces; never gates.
3. **Class-conformance validator** — the ESLint/Ansible move. A chore whose `CHORE.md`
   contradicts its declared rung fails. This is what makes "internally consistent"
   mechanical rather than aspirational, and it retires the three contradictory chores and
   the nine stop-at-data chores in one pass.
4. **`src/gzkit/chores/README.md`** — today a packaging contract that never says what a
   chore *is*. It gains the class definitions, the ladder, the admission criterion, and
   the declaration requirement.
5. **Per-chore declarations** — by this point data entry against a validator, not 40
   judgment calls.

Cadence precedes content: adding classes to a registry nothing surfaces multiplies
dormant surface that *reads as coverage*.

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
# chore count, declared posture, recommendations, remediation steps
ls -d .gzkit/chores/*/ | wc -l
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
Information in Computer Systems*, 1975 · Renovate *automerge* docs.
