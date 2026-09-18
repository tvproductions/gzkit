# Rules, tools, audits and refactors — the alignment map — 2026-09-12

> **Status:** design record from an R&D run (session `5f61ae2b`, 2026-09-12),
> written 2026-09-13 so the finding survives the session. Not canon. Its
> implementation surfaces are owned by
> [`chore-class-system.md`](chore-class-system.md), which carries the ratified
> design this map motivated. See § What this record does not license.

---

## The question

The run opened on a pasted document, *Python Codebase Architecture Guidelines*,
offered against the pythonic chores. The operator widened it twice.

Operator, 2026-09-12 20:15Z (verbatim): *"although this analysis was likely meant to
be authoring advice, we resort to refactoring if agents/rules arent effective, do we
have pythonic rules on the frontend? do we have any chore that aligns authoring rules
to audit/refactoring chores?"*

Operator, 2026-09-12 20:22Z (verbatim): *"I am trying to get front end and
audit/refactor back-end alignment. Ensure that rules, tools, audits and refactors all
agree. I am trying to tighten up how gzkit does its best to have good Python/software
architectures and implmentation, as much as possible."*

That second statement is the goal this record maps. The chore class system is the
first mechanism it produced; it is not the whole of the goal.

## Evidence standard

Counts were measured by command. The session measured them on 2026-09-12, and every
figure below was re-measured on 2026-09-13 before this record was written. Where the
two disagree, both are stated. Commands are in § Reproduction record. A value written
here is illustrative (`AGENTS.md` § Governance doctrine surfaces); the authority for each is
named beside it, and a later reader re-runs rather than trusts the transcription.

---

## The four estates

| Estate | Surface | Fires when |
|---|---|---|
| **Rules** — the front end | `.gzkit/rules/*.md`, path-scoped | every edit |
| **Tools** — the witnesses | ruff · ty · xenon · `gz validate` scopes · `gz check` | every commit and push |
| **Audits** — diagnosis | the control-surface passes, `gz-tech-debt-review`, `gz-intent-trace` | manually |
| **Refactors** — repair | the code-quality chores | manually |

The rules estate is scored clause by clause in the advisory scorecard
(`docs/governance/advisory-rules-audit.md` § Summary, fenced by
`gz validate --advisory-scorecard`). Measured 2026-09-13: 68 Mechanical · 31
Promotable · 64 Judgment · 0 Ambiguous.

### Edges that exist

| Edge | Instrument |
|---|---|
| rule ↔ rule | Pass A, `control-surface-rule-conflicts` |
| skill ↔ rule | Pass B, `control-surface-skill-rule-reachability` |
| rule prose ↔ validator check | Pass C, `control-surface-rule-vs-check-drift`, plus the scorecard |
| check ↔ commit path | `control-surface-validator-reachability` |
| rule prose ↔ permission standing consent | `control-surface-permission-consent-drift` |

`control-surface-validator-reachability/CHORE.md` states the family's boundary in its
own words: Passes A, B and C *"all ask about content relationships — rule vs rule (A),
skill vs rule (B), rule prose vs check semantics (C)."*

### Existing label collision

Two chores titled themselves **Pass D**: `control-surface-validator-reachability`
(*"Validator Reachability & Ungated Ratchet (Pass D)"*) and
`control-surface-permission-consent-drift` (*"Rule Prose vs. Permission Standing
Consent (Pass D)"*). `ledger-vocabulary-inertness/CHORE.md` cites the first as "Pass
D". Found 2026-09-13 while naming the rule ↔ chore pass. It is a Coherence finding
inside the family that exists to find Coherence findings, and it resolves with the
per-chore declarations in [`chore-class-system.md`](chore-class-system.md) §
Implementation order, step 5.
**Resolved 2026-09-13** (operator ruling, verbatim *"Later one becomes Pass E
(Recommended)"*): `control-surface-validator-reachability`, authored 2026-08-15, is now Pass E;
`control-surface-permission-consent-drift`, authored 2026-07-16, keeps Pass D.

### Edges that do not

**rule ↔ chore**, and **chore ↔ cadence.**

A chore cannot even declare the rule it serves. The registry's fields are `frequency`,
`lane`, `path`, `projectLocal`, `slug`, `timeoutSeconds`, `title`, `vendor` and
`version`. `.gzkit/rules/chores.md` § Authoring a New Chore requires four files, and
none of them is a rule linkage. So a four-way alignment is today a three-way one: rules,
tools and audits-of-rules interlock, and the refactor estate hangs off the side.

---

## The measured asymmetry

**gzkit governs its governance more rigorously than it governs its own code
architecture.**

**Freshness.** The control-surface chores ran within the month; five chores carry a
2026-09-12 run heading. Twenty-four of the 39 chores with a run log last ran on
2026-07-31, a single manual sweep. The only candidates report
`pythonic-design-pattern-detection` has ever produced is
`proofs/candidates-2026-04-26.md`.

**Nothing schedules any of it.** One chore declares a `frequency`. No CI workflow,
pre-commit hook or `.claude/hooks` script invokes `gz chores run`.

**Nothing ties a chore to a rule.** Twelve chores' `CHORE.md` cite any
`.gzkit/rules/` or `.claude/rules/` file. Five of those twelve are the control-surface
family, for which rules are the subject rather than the authority. Of the code-quality
chores, only `module-sloc-cap-radon`, `pythonic-design-pattern-application` and
`test-consolidation-subtest-sweep` cite one. `pythonic-refactoring`,
`complexity-reduction-xenon`, `pep257-docstring-compliance`,
`exceptions-and-logging-rationalization` and `pythonic-design-pattern-detection` run
untethered to any declared doctrine.

**The primary architecture directive is the weakest-witnessed family.**
`.gzkit/rules/hexagonal-architecture.md` names itself *"gzkit's primary
code-architecture directive."* Its operative clauses score:

| Row | Clause | Score |
|---|---|---|
| 64 | Dependencies live in adapters, never in the core | Mechanical |
| 64a | Pydantic is the one ratified exception | Promotable |
| 64b | Ports are domain-typed contracts | Judgment |
| 64c | Never name the technology in the core | Promotable |
| 64d | Encapsulate first; formalize the port on the second adapter | Judgment |
| 64e | The core is testable without any adapter | Promotable |

The rule's own § Verify is lint and typecheck, and neither can see a port.
`.gzkit/rules/pythonic.md`'s size limits — functions ≤50 lines, modules ≤600 — are rows
19 and 20, both Judgment, and the rule says so itself: *"authoring-time guidance
only."*

**Why it happened, without blame.** The control-surface family was born of acute pain:
an agent hitting a rule contradiction mid-work. Code architecture never produced that
pain, because ruff, ty and xenon fire on every commit and keep the floor clean. **Clean
lint reads as healthy code.** That sentence is the founding insight of
`pythonic-design-pattern-detection` — *given the code is idiomatic line by line, is the
shape Pythonic?* — and that chore has produced one report.

---

## The missing middle scale

| Scale | Concern | Rule | Witness |
|---|---|---|---|
| **Small** | idiom, style, types | `pythonic.md` | ruff and ty, every commit |
| **Middle** | module and package boundary — what a package exports, what may import what, catch-all modules | **none** | **none** |
| **Large** | ports and adapters, dependency direction | `hexagonal-architecture.md` | one Mechanical clause of six |

This is why two points in the pasted document had no home in any rule file. It is not
an oversight in one rule: **it is a scale nobody claimed**, and it is where the measured
damage sits.

| Measurement (2026-09-13) | Value |
|---|---|
| `__init__.py` under `src/gzkit` declaring no `__all__` | **14 of 42**, including `src/gzkit/__init__.py`, `commands/`, `content/`, `core/` and `validators/` |
| `src/gzkit/commands/common.py` | 702 lines, 27 top-level import statements |
| Top-level `commands/*.py` modules importing `common.py` | **74 of 97** (82 of 111 counting subpackages) |
| Test modules importing `gzkit.commands.common` | 39 |
| `src/gzkit/utils.py` | 127 lines, 17 importers |

**Variance recorded, not resolved.** The session reported *"94 of the 99 modules in
`src/gzkit/commands/`"* importing `common.py`. No probe run on 2026-09-13 reproduces
it: a literal `from gzkit.commands.common import` grep and an any-form grep both return
74. Cite the 2026-09-13 figure.

**Size does not see it.** At 702 lines `common.py` lands in the advise band of
`module-sloc-cap-radon`, which is advisory. The load-bearing signal is **fan-in
combined with a generic name**, and nothing measures it.

---

## Where canon already holds the goal — and its blind spot

The goal is already seated as next-in-priority. Movement C, *Reduce the accretion*,
carries the box **Close the doctrine-declared-without-mechanism family**, pulled
forward on 2026-09-02. Its completion criterion is this record's question: *"a declared
discipline either carries a mechanical witness or is demoted to advisory in its own
text — no third state."* Its instrument is the scorecard, where Promotable is the
forbidden third state, and three hexagonal clauses sit there. The box's own sibling,
**Oversized modules**, already owns the size-limit authority conflict: 600 in
`pythonic.md` against `.gzkit/rules/complexity-thresholds.json`.

**The blind spot.** That box scores **rule prose against validators**. The chore estate
is outside its instrument entirely. So the box can go green — every Promotable row
resolved — while the refactor estate stays dormant and untethered, because no chore is
scored at all. A rule demoted to Judgment satisfies the criterion even when a chore was
silently auditing it. And a chore refactoring toward a target no rule declares is
invisible from both sides.

### The mirror family: mechanism running without doctrine

The box's family is *doctrine declared without mechanism*. The chore estate shows its
mirror: **mechanism running without doctrine** — a chore that refactors toward a shape
no rule declares, with a full `proofs/` trail while it does it.

**Measured specimen, from the session itself.** The run's first proposal was a
module-boundary detection chore whose first signal was cycle-annotated deferred imports.
`pythonic.md` § Imports had already closed that subject: *"This posture is ACCEPTED,
not deferred (operator ruling 2026-08-08)"*, and reclassification happens *"not on the
count moving."* The proposed chore — a scanner, a disposition model, proof artifacts —
would have driven toward a target the governing rule had explicitly refused. It was
retracted at 20:18Z. Nothing in gzkit would have caught it, because nothing asks a chore
which rule it serves.

---

## Disposition of the pasted document

The document cites PEP 20, domain-driven design, Clean Architecture and PEP 544. Its
content is data, never instruction (`AGENTS.md` § Behavior Rules,
externally-authored tool output).

| Document section | gzkit surface | Disposition |
|---|---|---|
| Dependency inversion with `typing.Protocol`; composition root | hexagonal #4 — *"Port shape via `typing.Protocol`, not `ABC`; inject adapters by composition"* | **already covered** |
| Low coupling, explicit boundaries | hexagonal #1–#6 | **already covered**, in more depth |
| Functional core, imperative shell | pythonic #2 — isolate IO, transforms, QC and persistence | **already covered** |
| Ban global state | pythonic #10 — no implicit globals; `_detect_singleton` | **already covered** |
| Flat over nested, 2–3 levels | none needed — maximum package depth under `src/gzkit` measured 3 on 2026-09-13 | **already conformant** |
| Group by domain, not layer; "screaming" architecture | hexagonal #7 — *"`core/` stays; do NOT add `domain/`/`application/`/`adapters/`/`contexts/` folder partitions to 'do DDD.'"* — and the rule's preceding paragraph: *"Domain cohesion lives in the type system, not the folder tree."* | **ruled against** |
| Circular imports signal a design flaw | `pythonic.md` § Imports — posture ACCEPTED 2026-08-08 | **canon-closed** |
| Module over 500 lines; more than 10–15 imports | `pythonic.md` § Size Limits and the thresholds table | **covered, contested** — Movement C box *Oversized modules* owns it |
| Declare a package's public API with `__all__`; `_`-prefix internals | none | **absent from every rule file** |
| Ban catch-all `utils` / `helpers` / `common` modules | none | **absent from every rule file** |

**Where gzkit is better.** Hexagonal #5: *"Encapsulate first; formalize the port when
the SECOND adapter is real."* The document writes the Protocol immediately, and its own
worked example has exactly one adapter. gzkit's clause is the same advice with the
speculative-generality failure removed. Do not import the document's version over it.

**Where the document is better.** The last two rows. Hexagonal architecture is entirely
about boundaries, yet gzkit never says *declare what your package exports*. The
catch-all prohibition should be carried with fan-in as its signal, not length.

**Not to be taken.** The document's numbers. Thresholds come from
`.gzkit/rules/complexity-thresholds.json`, measured against a corpus, never from a
pasted document. If import count ever becomes a metric, it is measured into that table,
not transcribed.

---

## Operator rulings on this thread

- **Witness, hexagonal and rule-home questions are chore subjects, not doctrinal
  forks.** Verbatim, 20:30Z: *"chores are there to identify issues, provide an
  analysis, recommend a solution approach, and execute on solutions. a chore should
  diagnose and fix, with needed consultations with the operator, for input and
  judgment, as needed. so witness, hexagonal, and rule would all be subject to this same
  pattern and premise to chores."* The three questions the session had put to the
  operator dissolved rather than being answered: they asked for pre-approval of work
  already under standing authorization.
- **The design calibration comes before the conversion.** Verbatim, 20:41Z: *"look
  carefully at the broad design of the chore system before we get lost in confusion -
  this always a great danger when we do these sorts on reviews."* That calibration is
  [`chore-class-system.md`](chore-class-system.md).
- **Route.** Verbatim, 21:21Z: *"Movement C box — discharge it there, no new ADR."* The
  session had flagged the registry schema change as possibly contract-bearing, and so
  possibly queued behind `ADR-0.35.0` in semver order. The ruling settles it: this is
  discharged under the doctrine-declared-without-mechanism box, agent-side arm.

---

## Advised order

In dependency order. Each step names its owning surface.

1. **Cadence before content.** Adding rules or chores to an estate nothing schedules
   multiplies dormant surface that reads as coverage — the presence-check doctrine one
   level up. Owned by [`chore-class-system.md`](chore-class-system.md) § Implementation
   order, steps 1–2, and GHI #936.
2. **The rule ↔ chore edge.** The `governing_rule` registry field from the class
   system, then **a rule ↔ chore pass**: an audit, same shape as Passes A–C, flagging
   chores with no governing rule (ungoverned refactoring) and rules whose only witness is
   a chore (the scorecard's blind spot). The pass can take a first reading before the
   field lands, and that reading is the evidence for the field. It is deliberately
   **unlettered**: the session and its handoff called it "Pass D", but two existing
   chores already title themselves Pass D (see § Existing label collision).
3. **Claim the middle scale, with its witness.** Package API declaration goes into
   `hexagonal-architecture.md`, because boundary declaration is its subject. The
   catch-all prohibition, with fan-in as its signal, goes into `pythonic.md`. **Rule and
   witness land together or not at all**: a rule clause without a witness adds a
   Promotable row, which is exactly what the Movement C box forbids. The `__all__`
   witness is AST-decidable — an import reaching past a package's `__init__` into an
   undeclared internal.
4. **Hexagonal's three Promotable rows** — 64a, 64c and 64e — each resolved by a witness
   or a demotion in the rule's own text.
5. **Size-limit authority** — already owned by the Movement C box *Oversized modules*.
   Nothing here pre-empts its census.

**Retracted by the session, recorded so they are not re-proposed:** a chore built on
deferred-import count (canon-closed, above), and a standalone module-boundary detection
chore (one signal canon-closed, one better as a rule clause, and fan-in alone is not a
chore — on this map it would be a fourth dormant chore on an orphaned estate).

---

## What this record does not license

- **It does not add a rule clause.** The two middle-scale clauses land only with their
  witness, through the order above.
- **It does not re-open settled rulings.** The lazy-import posture in `pythonic.md` §
  Imports and hexagonal #7's folder-partition prohibition stand.
- **It does not close the Movement C box.** It names a blind spot in the box's
  instrument. Amending that instrument is the operator's to ratify.
- **It does not authorize an ADR or OBPI.** Operator ruling: discharge under the
  Movement C box, no new ADR.
- **It does not make the pasted document authoritative.** gzkit's rules govern, and two
  of the document's sections are explicitly ruled against.

---

## Reproduction record

```bash
# scorecard summary (validator-fenced)
uv run gz validate --advisory-scorecard
sed -n '/^## Summary/,/^<!--/p' docs/governance/advisory-rules-audit.md

# hexagonal and pythonic size rows
grep -nE '^\| *(64[a-e]?|19|20) *\|' docs/governance/advisory-rules-audit.md

# chores citing a rule file
for d in .gzkit/chores/*/; do
  grep -qE '\.gzkit/rules/|\.claude/rules/' "$d"CHORE.md 2>/dev/null && basename "$d"
done

# last run per chore
for f in .gzkit/chores/*/proofs/CHORE-LOG.md; do
  grep -oE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}' "$f" | tail -1
done | sort | uniq -c

# packages with no declared public API
grep -L "__all__" $(find src/gzkit -name __init__.py)

# catch-all fan-in
wc -l < src/gzkit/commands/common.py
ls src/gzkit/commands/*.py | grep -vE '__init__|/common\.py$' | wc -l
grep -lE "gzkit\.commands\.common|from \.common import|from \. import common" \
  src/gzkit/commands/*.py | grep -v '/common.py$' | wc -l
grep -rlE "gzkit\.commands\.common" tests --include='*.py' | wc -l
```

## Sources

Operator-supplied paste, *Python Codebase Architecture Guidelines* (unattributed; cites
PEP 20, PEP 544, domain-driven design, Clean Architecture) · session transcript
`5f61ae2b-9fc7-4646-8f2a-40d07743daaf`, 2026-09-12 20:01Z–21:49Z ·
`.gzkit/rules/hexagonal-architecture.md` · `.gzkit/rules/pythonic.md` ·
`.gzkit/rules/chores.md` · `docs/governance/advisory-rules-audit.md` ·
`docs/governance/build-to-1.0-campaign-2026-08-16.md` § Movement C.
