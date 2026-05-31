# ADR-0.0.59 Follow-up Audit — Unit Testing Doctrine

Date: 2026-05-31
Trace: GHI #571
Related: GHI #531, GHI #537, GHI #547, GHI #562

## Purpose

This follow-up does not replace ADR-0.0.59. It records the 2026-05-31
unit-testing doctrine deep dive against the validated ADR package and routes
each finding into ADR-0.0.59 or its related GHIs.

ADR-0.0.59 is the design move that ameliorates GHI #531: it separates
BEHAVIOR, SUPPORT, and STRUCTURAL-FENCE requirements so the REQ-to-proof
surface no longer forces every requirement into an `@covers` unit test. The
remaining work is recurrence defense: align hot-path instructions, stale
skills, completion-layer enforcement, and cleanup inventory with that design.

## External Unit-test Standard, Mapped to gzkit

A useful unit test checks one required behavior of a narrow unit quickly,
deterministically, and in isolation. It fails because the behavior contract
breaks, not because prose, file shape, or implementation scaffolding changed.

For gzkit this means:

- use stdlib `unittest`, never pytest;
- BEHAVIOR REQs may require `@covers` unit tests;
- SUPPORT REQs route to ledger event plus structural validator proof;
- STRUCTURAL-FENCE REQs route to parent-ADR boundary invariants;
- exact strings, table text, and rendered output are unit-test material only
  when output form is the named behavior contract.

Reference sources used for the standard:

- Python `unittest` documentation:
  <https://docs.python.org/3/library/unittest.html>
- Agile Alliance unit test glossary:
  <https://agilealliance.org/glossary/unit-test/>
- Microsoft unit testing best practices:
  <https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices>
- Martin Fowler, Unit Test:
  <https://martinfowler.com/bliki/UnitTest.html>

## Current Mechanical Evidence

The ADR-0.0.59 validators are passing:

```text
$ uv run gz validate --req-kind-discipline
Validated: req_kind_discipline
✓ All validations passed (1 scopes).

$ uv run gz validate --tautological-test-audit
Validated: tautological_test_audit
✓ All validations passed (1 scopes).
```

The tautological-test scanner is acting as a growth gate, not as proof that
the test suite is clean:

```text
current_ops 768
baseline_ops 765
waiver_entries 3
current_minus_baseline_minus_waiver 0
by_disposition {'convert': 663, 'replace-with-ledger': 60, 'fold-to-validator': 43, 'keep-as-fixture': 2}
```

Top current scanner files:

```text
32 tests/commands/test_init.py
27 tests/test_persona_schema.py
22 tests/test_audit_pipeline.py
21 tests/test_sync.py
19 tests/commands/test_plan.py
18 tests/governance/test_agents_md_map_doctrine_obpi04.py
18 tests/test_rules.py
17 tests/commands/test_runtime.py
16 tests/test_skills.py
14 tests/commands/test_adr_promote.py
```

A broader AST triage screen for output/render assertions found:

```text
render_like_assertions 1846
by_reason {'output-like variable assertion': 915, 'cli/render output assertion': 847, 'file-content assertion': 84}
files_with_hits 193
```

Top files from that advisory triage:

```text
96 tests/test_hooks.py
69 tests/commands/test_status.py
64 tests/test_formatters.py
60 tests/commands/test_adr_promote.py
57 tests/commands/test_chores.py
52 tests/test_audit_pipeline.py
50 tests/commands/test_runtime.py
41 tests/commands/test_register_adrs.py
40 tests/test_closeout_ceremony_cmd.py
38 tests/test_templates.py
```

This second screen is not a defect count. Formatter and CLI output-contract
tests can be legitimate. It is a triage queue for identifying string/prose
assertions that preserve current shape rather than required behavior.

## Findings Routed to ADR-0.0.59

### F1 — ADR-0.0.59 is the correct design response

GHI #531 identified the category error: REQ-to-`@covers` parity generated
tautological filesystem-grep tests for content and governance-support REQs.
ADR-0.0.59 addresses that root cause by routing each REQ kind to one proof
channel. This follow-up should therefore strengthen ADR-0.0.59 rather than
open a competing design.

### F2 — Hot-path rule wording is weaker than the doctrine

`.gzkit/rules/tests.md` correctly says to use stdlib `unittest`, not pytest,
and to assert semantics rather than strings. It also carries ADR-0.0.59's
REQ Scope Discipline section.

The risk is that the strongest operational classifier lives in
`docs/governance/req-scope-discipline.md`, while the hot-path rule still lets
agents treat "tests assert semantics, not strings" as a slogan. The rule
should say directly that only BEHAVIOR REQs produce `@covers` unit tests.

Recommended control-surface wording:

```markdown
**Unit-test purpose.** A gzkit unit test is a stdlib `unittest.TestCase`
check of one required code behavior. It is fast, isolated, deterministic,
and fails when the behavior contract breaks. It does not preserve current
implementation structure, current prose, or current rendered output unless
that exact output form is the named behavior contract.

**No pytest.** Do not use pytest syntax, fixtures, parametrization,
plugins, or bare pytest-style assertions. Use `unittest`, `unittest.mock`,
and stdlib fixtures such as `tempfile.TemporaryDirectory()`.

**Proof-channel routing.** BEHAVIOR REQs use `@covers` tests. SUPPORT
REQs use ledger event plus structural validator proof. STRUCTURAL-FENCE
REQs use parent-ADR boundary invariants. Do not add a unit test merely to
make a non-BEHAVIOR REQ appear covered.

**String/output assertions.** Prefer structured fields, domain objects,
state transitions, exception types, ledger event fields, and parsed values.
Assert exact strings or table markers only when rendering behavior is the
named contract, and keep those tests in dedicated output-form fixture
classes.
```

### F3 — `gz-obpi-pipeline` still pressures misuse

`.gzkit/skills/gz-obpi-pipeline/SKILL.md` still says the `@covers location`
column is not optional and includes `test ! -e <path>` as a Test Coverage
example. That language conflicts with ADR-0.0.59 because non-BEHAVIOR REQs
must not be forced into unit tests.

Recommended Stage 3 evidence wording:

```markdown
The proof-location column is proof-channel specific, not always
`@covers`. For BEHAVIOR REQs, cite the `@covers` test location. For
SUPPORT REQs, cite the ledger event type/path and structural validator
scope. For STRUCTURAL-FENCE REQs, cite the parent-ADR Boundary Invariants
anchor. A missing BEHAVIOR `@covers` location is a blocker; a non-BEHAVIOR
REQ must not be forced into a unit test to fill the cell.
```

Recommended replacement example:

```text
# req-01:support-proof
proof: artifact_edited ledger event + uv run gz validate --documents

# req-02:behavior-proof
proof: tests.commands.test_validate.TestReqKindDiscipline.test_missing_kind_fails
```

Recommended generic skill reminder:

```markdown
Before authoring a test, classify the REQ proof channel. Write a
`unittest` only for BEHAVIOR. For SUPPORT or STRUCTURAL-FENCE, update the
ledger/validator/boundary-invariant evidence instead of creating a
filesystem-grep or rendered-prose assertion.
```

### F4 — Completion-layer enforcement still uses old pressure

`src/gzkit/req_kind.py` maps:

- BEHAVIOR -> `TEST_COVERS`
- SUPPORT -> `LEDGER_PLUS_VALIDATOR`
- STRUCTURAL-FENCE -> `PARENT_ADR_INVARIANT`

`gz covers OBPI --json` exposes the taxonomy fields and separates
BEHAVIOR uncovered REQs from advisory non-`@covers` REQs.

`src/gzkit/commands/obpi_complete.py` still calls `discover_covers()` for
every parsed REQ in `_enforce_req_coverage_gate`, applies
`--accept-uncovered`, and tells the operator to add `@covers` entries for
gaps. That can still push agents toward unit-test misuse. This is already
tracked by GHI #537 and should remain a required follow-up for ADR-0.0.59.

### F5 — Existing scanner blocks growth but does not clean debt

`uv run gz validate --tautological-test-audit` proves current growth is
blocked at baseline plus waivers. It does not prove the remaining tests are
effective. The `by_disposition` inventory still contains hundreds of
`convert`, `replace-with-ledger`, and `fold-to-validator` candidates.

The scanner needs an operator-facing inventory/reporting mode so cleanup
work can be routed deterministically instead of being rediscovered ad hoc.

### F6 — Output/string assertion detection should start advisory-only

The broader 1,846-hit output/render screen is useful but too broad for a
fail-close gate. Many formatter and CLI output-form tests are legitimate
behavior tests. The right next move is advisory classification plus an
explicit output-contract marker or dedicated fixture class convention before
fail-closing on exact output assertions.

## Cleanup Strategy

1. Keep `--tautological-test-audit` as the growth gate.
2. Add scanner inventory output, for example:
   `uv run gz validate --tautological-test-audit --inventory --json`.
3. Add an advisory output/render assertion scanner for `result.output`,
   `stdout`, `stderr`, `getvalue()`, `read_text()`, `assertIn`,
   `assertRegex`, and `assertMultiLineEqual`.
4. Require explicit output-contract markers or dedicated fixture class names
   before turning output/render assertion detection into a fail-close gate.
5. Sweep in waves:
   - wave 1: current tautological scanner top files;
   - wave 2: command/status tests with unstructured prose assertions;
   - wave 3: hooks/templates/control-surface tests;
   - wave 4: formatter/output-contract tests, mostly classification and
     fixture isolation rather than deletion.
6. Classify each candidate as one of:
   - BEHAVIOR semantic unit test: keep or strengthen;
   - output-contract behavior test: keep, mark, or isolate as fixture;
   - SUPPORT content proof: delete or replace with ledger plus validator
     proof;
   - STRUCTURAL-FENCE proof: move to parent ADR boundary invariant;
   - broad integration or user flow: move out of unit-test framing.

## Related GHIs

| GHI | Relationship |
|-----|--------------|
| #531 | Original category-error report; closed as superseded by ADR-0.0.59. |
| #571 | This follow-up audit and recurrence-defense tracker. |
| #537 | Completion-layer gap: `gz obpi complete` still treats REQs as `@covers`-first. |
| #538 | STRUCTURAL-FENCE parent-shape / per-REQ-anchor validator gap. |
| #543 | SUPPORT proof-channel implementation gap: prose match instead of ledger query. |
| #547 | Suite-level SUPPORT / STRUCTURAL-FENCE ambiguity and proof-channel boundary clarification. |
| #562 | Existing tautological-test scanner issue and concrete cleanup signal. |
| #551 | Adjacent completion-gate doctrine/runtime trigger mismatch; coordinate with #537 implementation. |
| #516 | Adjacent closeout-ceremony mechanical-verification gap; not routed under #571 unless a wider T1/T2 consolidation absorbs it. |
| #552 | Adjacent TASK-spine governance drift receipt; not reopened or superseded by #571. |

## Recommendations

1. Treat ADR-0.0.59 as the governing design; use GHI #571 as the traceable
   receipt for this follow-up audit.
2. Close GHI #537 before relying on wording alone; runtime completion
   pressure is stronger than rule prose.
3. Update `.gzkit/rules/tests.md` and relevant skills under a governed
   control-surface change, then run `uv run gz agent sync control-surfaces`.
4. Add inventory mode to the tautological-test scanner before starting large
   cleanup waves.
5. Add advisory output/render assertion triage before creating a hard gate.

## Operator Decisions Requested

1. Cleanup wave order: start with existing tautological scanner top files, or
   with command/status output assertions?
2. Output-contract marker: require an explicit marker such as
   `# output-contract: <reason>` before accepting exact CLI prose assertions?
3. Promotion order: promote GHI #537 ahead of wording updates, since runtime
   completion behavior can still force the wrong proof channel?
