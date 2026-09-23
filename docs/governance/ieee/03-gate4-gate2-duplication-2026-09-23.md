<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# 03 — What Gate 4 actually adds over Gate 2 (`M-F`)

> **This is a dated record.** Every figure below was observed on the tree at
> `43d63da8de6d067cbc47ecfdf1546c777058b743`. The values are ILLUSTRATIVE, never
> authoritative (`AGENTS.md` § Governance doctrine surfaces). The authority is
> the script: re-run
> [`03-gate4-gate2-duplication-evidence/measure.py`](03-gate4-gate2-duplication-evidence/measure.py)
> rather than trusting a number transcribed here. It carries no literals from
> this date, so it reports whatever tree it is run against.

**Origin.** Measurement item `M-F` of the program in
[`01 § 12`](01-engineering-method-2026-09-22.md): *"Measure the real duplication
between Gate 4 and Gate 2 before proposing removal."* Executed 2026-09-23 on
operator ruling. `M-F` is also the measurement home of
[`DISAGREEMENTS.md`](DISAGREEMENTS.md) `D-08`, where Phase 1 asserted that the
BDD gate largely duplicates unit tests, Phase 2 answered **NEEDS MORE EVIDENCE**
— *"Same lines/REQs can be exercised under different conditions and
assertions"* — and neither side had measured anything. This piece supplies the
measurement. **It does not dispose of `D-08`**; § What this does not settle says
why, and authoring a finding remains an open operator question.

---

## Method

`M-F`'s method, followed as written: execute the behave suite under coverage
instrumentation, compare the covered set against the unit suite's, identify
which scenarios reach code no unit test reaches, verify the behave-only REQ
count, and count the `@wip` scenarios separately because they never execute.

Both suites were instrumented **identically**, which matters more than it
sounds. A third of the step files drive `gz` as a subprocess, and in-process
coverage would have scored those runs as reaching nothing — understating Gate 4
in exactly the direction the hypothesis under test predicts. Subprocess capture
was enabled for both sides (`COVERAGE_PROCESS_START` against a parallel-mode
config, which the venv's `a1_coverage.pth` activates in every child): the behave
run produced 90 coverage data files and the unit run 528, so both sides' child
processes were in fact measured.

Attribution to individual features was done by re-running each of the 74 feature
files alone under the same instrumentation and intersecting its covered set with
the behave-only set. All 288 behave-only statements attributed, so nothing is
unexplained.

**One read-path note, because it changes the absolute numbers by a third.**
Every figure below is *executed statements*, read back through `coverage json`
— coverage's own reporting basis, the same denominator `coverage report` uses.
Reading the raw line records out of the data files instead (`CoverageData.lines`)
gives 40,491 for the same behave run rather than 25,366, because the tracer
records line events that the parser does not count as statements. The **ratios
are unaffected** — 1.09% against 1.14% behave-only — but a reader who re-derives
this by the other path and finds different totals is not finding a discrepancy.
The script uses the reporting basis deliberately, and is the authority.

---

## Result 1 — 98.9% of what Gate 4 reaches, Gate 2 already reached

```
statements executed by behave     25,366
statements executed by unittest   48,481
executed by BOTH                  25,078
behave-only                          288   (1.14% of behave's own reach)
unit-only                         23,403
```

The behave suite reaches 288 statements of `src/gzkit` that the unit suite never
executes, out of 25,366 it touches. Put the other way: **the unit suite already
covers 98.9% of everything the BDD suite reaches**, and reaches 23,403
statements beyond it.

The 288 are concentrated. 31 files carry any of them; three carry 48%:

```
  51  src/gzkit/justify/complexity_hints.py
  47  src/gzkit/commands/init_cmd.py
  39  src/gzkit/commands/airlock.py
  17  src/gzkit/commands/ontology.py
  15  src/gzkit/commands/validate_cmd.py
```

## Result 2 — 47 of 74 feature files add no reach at all

Attributed by feature:

```
features adding >0 behave-only statements   27 of 74, holding 177 of 467 scenarios
features adding ZERO                        47 of 74, holding 290 of 467 scenarios
```

**Sixty-two percent of the scenarios reach nothing the unit suite misses.**
The largest zero-contribution features are `brief_reconcile` (35 scenarios —
these are the `@wip` ones, which never run), `constitutional_invariants` (31),
`subagent_pipeline` (29), `task_governance` (12) and `validate_receipt_shape`
(10).

The 27 that do contribute are led by `justify_complexity_hints` (51 statements,
36 of them reached by no other feature), `airlock` (50, all 50 exclusive), `init`
(46, 42 exclusive), `adr_audit_covers_backfill` (17), `ontology` (17, all
exclusive) and `upgrade` (16). Three feature files account for 147 of the 288.

## Result 3 — the behave-only REQ count is 55, not 54

```
REQs tagged in feature files                 338
feature REQs that also have a @covers test   283   (83.7%)
behave-only REQs                              55
```

`01 § 8.3` estimated *"~54 behave-only REQs"* and *"84% of feature-tagged REQs
already have `@covers`"*. Both verify: 55 and 83.7%. The estimate was sound.

Where those 55 live is new information the estimate did not carry:

```
living only in features that add ZERO reach    23
living in a feature that does add reach        32
```

So the behave-only REQ set and the behave-only statement set are **not the same
residue**. Twenty-three REQs are proven exclusively by scenarios that execute no
code the unit suite misses — they are REQ-level coverage over already-covered
code. Nine of those sit in `distribution_invariant` alone, six in `adr_promote`,
three in `waiver_ratchet`.

## Result 4 — the 35 `@wip` scenarios prove nothing that is not already proven

`brief_reconcile.feature` carries 35 scenarios, all tagged `@wip`, and behave's
own report confirms they are skipped: *"433 scenarios passed, 0 failed, 35
skipped."* `M-F` required counting them separately. Counting them turns out to
settle them:

**All 25 REQ tags inside that file already have a `@covers` unit test.** Not
some — all. The file's own comment says as much (*"the verb's REQ behavior is
proven by `tests/commands/test_brief_reconcile.py` `@covers`"*), and the
measurement confirms it independently. The 35 scenarios are measurably inert:
they execute nothing and they are the sole proof of nothing.

*(Counting note: `grep` finds 37 lines containing `@wip` in that file. Two are
prose in `#` comments describing the convention. The tag count is 35, matching
behave's skip count exactly. The script excludes comment lines for this reason —
counting a comment as a tag would inflate the very figure `M-F` asks to isolate.)*

## Result 5 — `subagent_pipeline` duplicates, but not "name-for-name"

`01 § 8.3` claims `subagent_pipeline.feature` *"restates
`tests/test_pipeline_dispatch.py` name-for-name."*

The duplication claim holds on the stronger evidence: **`subagent_pipeline`
contributes 0 behave-only statements.** Its 29 scenarios reach nothing
`tests/test_pipeline_dispatch.py` and its neighbours do not already reach. It
also carries **zero REQ tags**, so it adds no REQ-level coverage either.

The *"name-for-name"* characterisation is literally false and should not be
re-cited. Normalised, **zero** of the 29 scenario names match a test method name
exactly; 11 of 29 reach a token-overlap of 0.5 or better against their nearest
unit test. The pairing is real and visible by inspection — *"Simple task routes
to haiku model"* against `test_simple_routes_to_haiku` — but it is semantic
correspondence, not identity, and 83 unit tests sit against 29 scenarios. A
later reader checking the literal claim would find it fails and might discard
the sound conclusion with it.

## Corrections to `01 § 8.3`

| `01 § 8.3` | Measured here |
|---|---|
| ~54 behave-only REQs | **55** |
| 84% of feature-tagged REQs have `@covers` | **83.7%** (283/338) |
| 34 of 58 step files call production code in-process | **34 of 58** — verified |
| 9 subprocess-driving step files | **10** |
| 35 `@wip` scenarios never run | **35** — verified |
| `subagent_pipeline.feature` restates the unit file name-for-name | duplication verified by coverage; **"name-for-name" is false** |

Five of six figures verify. The two that move are small and move against the
argument's convenience in one case (55 > 54, a slightly larger residue to keep)
and toward it in the other.

---

## What this does not settle

**Line coverage cannot see a different assertion over the same line.** This is
precisely Phase 2's challenge at `D-08` — *"Same lines/REQs can be exercised
under different conditions and assertions"* — and this measurement does not
answer it. A scenario that drives `gz obpi complete` through the CLI with a
malformed attestation executes the same lines as a unit test that calls the
function with a valid one, and the two assert different things. Every such
scenario appears in this piece's "zero contribution" column.

So the result is one-sided, and the side it establishes should be stated
exactly: **the BDD suite's code reach is 98.9% redundant.** It does *not*
establish that 98.9% of the BDD suite's *assertions* are redundant, and no
coverage instrument can. Reading the first as the second is the error this
register exists to prevent.

Two things the measurement does settle on their own terms, because they do not
depend on assertion content:

- the 35 `@wip` scenarios execute nothing and are the sole proof of nothing;
- `subagent_pipeline.feature` adds neither line reach nor a single REQ tag.

**What a further measurement would need.** Distinguishing condition from
coverage needs mutation testing or assertion-level analysis, not line counts —
substantially more expensive than `M-F`, and not proposed here. `M-F` was
scoped as *"independent and cheap"* and that scoping is also its ceiling.

## What a Gate-4 retirement would cost — the question `M-F` was asked

Stated as cost, not as a recommendation. `01 § 12` is explicit that the
measurement program *"proposes no implementation."*

Retiring Gate 4 as a separate gate would give up, in descending order of what
this measurement can actually vouch for:

1. **288 statements of reach**, concentrated in `justify/complexity_hints`,
   `init_cmd`, `airlock` and `ontology` — 1.14% of the BDD suite's own
   footprint, and the only part of it no unit test reaches today.
2. **55 REQs whose only proof channel is a feature tag**, 32 of them in features
   that also carry reach and 23 in features that do not.
3. **The subprocess-boundary property.** Ten step files drive `gz` as a real
   process and assert on exit codes and stderr. Whether any unit test asserts
   that property is not answerable from coverage data — the lines coincide — and
   it is the most credible candidate for genuinely additive value.
4. **Two `@expected-warning` negative controls**, the only scenarios in the
   suite that assert a warning is produced rather than absent.

And it would give up, measurably, nothing at all in: the 35 `@wip` scenarios,
and the 29 scenarios of `subagent_pipeline.feature`.

## Classification

**REFINE**, not REMOVE, on this evidence — and the refinement this measurement
supports is narrower than `01 § 8.3`'s framing.

- The `@wip` block and `subagent_pipeline.feature` are **REMOVE** candidates on
  their own evidence, independent of any decision about Gate 4 as a gate. Nothing
  in this measurement defends them, and `brief_reconcile.feature`'s `@wip` tags
  additionally leave a gate reporting *"73 features passed, 1 skipped"* as a pass.
- Gate 4 as a **gate** is not dispositionable from here. The 288 statements and
  55 REQs are real, and the assertion-level question is untouched.

---

## Relationship to the register

- **`D-08`** now has its measurement. Its disposition is `MISSING EVIDENCE`;
  whether the claim should be carried into [`FINDINGS.md`](FINDINGS.md) as a
  finding with a status — the open question `D-08` records — is for the operator,
  and this piece does not decide it.
- **`M-F`** moves from proposed to executed in
  [`README.md`](README.md) § The measurement program. `M-F` follows no finding,
  which is `D-08`'s point: the claim is homeless in the register, not in the
  investigation.
- **Nothing here binds.** These records are analysis, not canon
  (`README.md` § Reading posture). No gate, rule or ADR changes because of this
  piece, and Phase 4 remains unauthorised.
