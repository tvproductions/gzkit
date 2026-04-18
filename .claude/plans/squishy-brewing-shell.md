# OBPI-0.0.16-02 Gate Integration — Implementation Plan

## Context

ADR-0.0.16 mandates mechanical frontmatter-ledger coherence checks at every `gz gates` invocation. OBPI-01 already built the validator (`gz validate --frontmatter` → exit 3 on drift) and OBPI-05 built the canonical `STATUS_VOCAB_MAPPING`. This OBPI (02) wires those two upstream artifacts into `gz gates` Gate 1 so frontmatter drift blocks gate progression with an operator-visible, per-field drift listing and a named executable recovery command. Without this wiring, the validator exists but is never invoked during the normal gate flow, leaving the ADR-0.0.16 intent un-enforced at the operator's daily surface.

Both prerequisites are satisfied: OBPI-01 and OBPI-05 are `attested_completed` (verified via `gz adr status ADR-0.0.16`).

## Design Decisions

1. **Exit-code routing.** `gates_cmd` currently `raise SystemExit(1)` for any failure. Add a second accumulator for policy breaches; final exit routes to `EXIT_POLICY_BREACH` (3) when any gate returned a policy-breach result, else `EXIT_USER_ERROR` (1) when any plain failure. Reuses existing constants in `src/gzkit/cli/helpers/exit_codes.py:12-22`.
2. **Gate 1 return type.** Widen `_run_gate_1` from `-> bool` to `-> Literal["pass", "fail", "policy_breach"]`. Existing callers only read falsiness — update the dispatcher explicitly; do not introduce a new Enum (overkill for one call site).
3. **Rendering.** Build a gate-local `_render_gate1_frontmatter_drift()` inside `gates.py`. Do **not** reuse validator's private `_render_frontmatter_explain` (different format contract: gate prefix, explicit recovery-command line per field, `STATUS_VOCAB_MAPPING` canonicalization for `status` fields).
4. **DRY contract.** Import `_RECOVERY_COMMANDS` from `validate_frontmatter` rather than duplicating it.
5. **Closeout migration breadcrumb.** `gz gates` is deprecated in favor of `gz closeout`. Add a docstring on the new gate helper noting the migration target (`closeout.py:533` Stage 1 vicinity).
6. **Scope amendment.** Brief's Allowed Paths omits `features/`. Heavy-lane Gate 4 requires `@REQ-*`-tagged behave scenarios (`.claude/rules/tests.md` GHI #185). **Amend** to add `features/gates.feature` (new). No `docs/user/manpages/gates.md` exists today; OBPI defers manpage creation as a tracked defect (filed at completion) — this matches how the brief scoped itself.

## Files to Modify

| Path | Change |
|---|---|
| `src/gzkit/commands/gates.py` | Wire validator into `_run_gate_1`; widen return type; add `_render_gate1_frontmatter_drift()`; adjust `gates_cmd` exit routing |
| `tests/commands/test_gates_frontmatter.py` | New test module (8 tests, all `@covers`-decorated) |
| `features/gates.feature` | New feature file with `@REQ-*` scenario tags for Gate 4 |
| `docs/user/commands/gates.md` | Update Gate 1 section; add drift-block example + exit-3 note |
| `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-02-gate-integration.md` | Evidence + tracked defects + human attestation |

## Files to Read (no edit)

- `src/gzkit/commands/validate_frontmatter.py:22-27,183` — `_RECOVERY_COMMANDS`, `_validate_frontmatter_coherence`
- `src/gzkit/governance/status_vocab.py` — `STATUS_VOCAB_MAPPING`, `canonicalize_status`
- `src/gzkit/cli/helpers/exit_codes.py:12-22` — `EXIT_POLICY_BREACH`, `EXIT_USER_ERROR`
- `src/gzkit/validate.py` — `ValidationError` model
- `tests/commands/common.py` — `_quick_init()`, `CliRunner`
- `features/steps/state_repair_steps.py:14-26` — drift-seeding step precedent

## Implementation Steps (TDD order)

### Step 1 — Red: drift-blocks test

Write `test_gate1_blocks_on_status_drift_exit_3` in `tests/commands/test_gates_frontmatter.py`:
- `_quick_init()`, create an ADR via `plan create 0.1.0`, seed a drifted `status:` in the ADR frontmatter
- Invoke `gates --adr ADR-0.1.0`, assert `result.exit_code == 3`

Run it. Watch it fail (currently exits 0 or 1 — validator is not wired).

### Step 2 — Green: minimum viable wiring

In `src/gzkit/commands/gates.py`:
1. Import `_validate_frontmatter_coherence`, `_RECOVERY_COMMANDS` from `gzkit.commands.validate_frontmatter`; import `canonicalize_status` from `gzkit.governance.status_vocab`; import `EXIT_POLICY_BREACH`, `EXIT_USER_ERROR` from `gzkit.cli.helpers.exit_codes`.
2. Widen `_run_gate_1` to return `Literal["pass", "fail", "policy_breach"]`. After the `resolve_adr_file` success path, call `errors = _validate_frontmatter_coherence(project_root, adr_scope=adr_id)`. If non-empty, call the renderer, record `gate_checked` with `returncode=3` and per-field evidence, return `"policy_breach"`.
3. Update `gates_cmd` dispatcher: track `policy_breaches` counter alongside `failures`. At end:
   ```python
   if policy_breaches:
       raise SystemExit(EXIT_POLICY_BREACH)
   if failures:
       raise SystemExit(EXIT_USER_ERROR)
   ```
4. Add `_render_gate1_frontmatter_drift(errors: list[ValidationError]) -> None` emitting per-field lines to console with recovery command per field.

Re-run Step 1's test → GREEN.

### Step 3 — Red+Green per remaining REQ

Add tests one-at-a-time (red, watch fail, implement, watch pass):

| Test | REQs covered | Implementation adjustment |
|---|---|---|
| `test_gate1_passes_when_no_drift` | REQ-01 | (already passes post Step 2) |
| `test_gate1_drift_lists_each_field` | REQ-02 | Renderer emits one line per error |
| `test_gate1_error_names_recovery_command_per_field` | REQ-03 | Renderer looks up `_RECOVERY_COMMANDS[field]` and prints it inline |
| `test_gate1_status_drift_uses_canonical_vocab` | REQ-05 | For `field == "status"`, renderer calls `canonicalize_status(frontmatter_value)` and shows both raw and canonical term |
| `test_gate1_unmapped_status_term_blocks` | REQ-05 | When `canonicalize_status` returns `None`, emit a distinct "unmapped status term" line |
| `test_gates_rejects_skip_frontmatter_flag` | REQ-04 | (passes without implementation — argparse rejects unknown flags; verify explicit assertion) |
| `test_gate1_latency_within_validator_budget` | REQ-06 | Measure validator standalone on fixture via `time.perf_counter`; measure gate1 path; assert `gate_cost <= validator_cost + 0.05s` |

All tests use `_quick_init()` fixture with 1–3 ADRs. Seeding drift uses the same inline-filesystem-write pattern as `features/steps/state_repair_steps.py:20-26`.

### Step 4 — Refactor

Once all tests green, inspect for: size-cap compliance (gates.py is 327 lines, stays under 600); function length (≤50 lines per rule); extract any rendering helpers that grew past 30 lines.

### Step 5 — BDD (Gate 4)

Create `features/gates.feature`:
- Scenario "Gate 1 blocks on frontmatter drift" — tags `@REQ-0.0.16-02-02 @REQ-0.0.16-02-03`. Reuse `@given("an OBPI brief exists with frontmatter status")`-style step from `state_repair_steps.py` (adapt for ADR).
- Scenario "gz gates rejects --skip-frontmatter" — tag `@REQ-0.0.16-02-04`.

Add step definitions in `features/steps/` only if necessary — prefer reuse.

### Step 6 — Docs (Gate 3)

Update `docs/user/commands/gates.md`:
- Update Gate 1 description: "Gate 1 resolves the ADR file AND verifies frontmatter-ledger coherence across the four governed fields (id, parent, lane, status)."
- Add an example block showing a drift-block output including recovery-command line.
- Add a note under the existing options table: "Exit code 3 indicates a frontmatter policy breach. There is no bypass flag — resolve the drift via `gz chore run frontmatter-ledger-coherence` or the named recovery command."

### Step 7 — Update brief

In the OBPI brief, fill the Evidence section with:
- Gate 2 TDD output (unittest)
- Code Quality outputs (ruff, ty)
- Gate 3 output (mkdocs --strict)
- Gate 4 output (behave)
- Value Narrative / Key Proof
- Implementation Summary (files modified, tests added, date)
- Tracked Defects (manpage deferral with follow-up GHI if filed; deprecation migration breadcrumb)

## Verification (Heavy-lane, ARB-wrapped)

```bash
# Lint/format/type
uv run gz arb ruff src tests
uv run gz arb step --name ty -- uvx ty check . --exclude 'features/**'

# OBPI-scoped tests first (fast)
uv run gz arb step --name unittest-obpi -- \
  uv run gz test --obpi OBPI-0.0.16-02-gate-integration

# Full suite (pre-commit would run this anyway)
uv run gz arb step --name unittest-full -- uv run -m unittest -q

# Docs (Gate 3)
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# BDD OBPI-scoped (Gate 4)
uv run gz arb step --name behave-obpi -- \
  uv run gz test --obpi OBPI-0.0.16-02-gate-integration --bdd

# Coverage parity (Stage 3 Phase 1b gate)
uv run gz covers OBPI-0.0.16-02-gate-integration --json
# assert: summary.uncovered_reqs == 0

# Manual proof
uv run gz gates --adr ADR-0.0.16  # observe real gate pass/fail behavior
```

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Dispatcher's `handler()` return type changes from `bool` to tri-state string — other gate handlers still return bool | Add a normalization in the dispatcher: treat `True` as `"pass"`, `False` as `"fail"`, the string value as-is. Keeps gate 2–5 handlers unchanged. |
| Policy-breach exit 3 hides a Gate 2 test failure in same run | Every gate renders its output before the exit is raised; ledger records both events. Document precedence in `gates_cmd` docstring. |
| Latency test flakes on slow CI | Measure validator-only cost in the same test and assert relative delta (`gate_cost - validator_cost < 50ms`) rather than an absolute bound. |
| `_quick_init` fixture's ADR has no ledger drift today → status drift requires re-writing ledger or frontmatter | Seed drift by rewriting the frontmatter `status:` field post-registration (matches OBPI-01 drift-test precedent). |
| Manpage deferral leaves CLI Doctrine gap | File tracked defect at OBPI completion; note in brief's `Tracked Defects`; reference in ADR closeout. |

## Tracked Defects (filed at completion)

1. **Gates manpage absent.** No `docs/user/manpages/gates.md` exists. CLI Doctrine (`.claude/rules/cli.md:87`) prescribes a manpage for heavy-lane subcommand contract changes. Pre-existing state; brief did not scope manpage creation. File `gh issue create --label defect` at completion.
2. **Deprecation migration.** `gz gates` emits a deprecation notice; the frontmatter guard must migrate to `gz closeout` Stage 1 when `gz gates` is removed. Breadcrumb placed in new `_render_gate1_frontmatter_drift` docstring.

## Completion Contract

- All 6 REQs pass `gz covers OBPI-0.0.16-02-gate-integration` with `uncovered_reqs == 0`
- Full `unittest -q` passes
- `uv run mkdocs build --strict` passes
- `uv run -m behave features/gates.feature` passes
- `uv run gz gates --adr ADR-0.0.16` behaves correctly on the real repo (manual)
- Brief evidence populated with ARB receipt IDs for lint, type, tests, coverage, mkdocs, behave
- Human attestation recorded (Heavy lane Gate 5)
