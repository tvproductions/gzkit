# Tech-Debt Review — ADR-0.0.21-chores-as-gzkit-surface

**Audit date:** 2026-04-29
**Scope mode:** `adr ADR-0.0.21`
**Scope resolution:** union of OBPI-0.0.21-01..09 Allowed Paths
**Probes:** size-cap, complexity, lint, types, governance, validators, cli-drift, todo-rot, tests
**Raw probe outputs:** `.gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/`

## Headline

**No Critical findings.** ADR-0.0.21 ships clean on lint, types, governance,
CLI drift, validators, and TODO rot. The debt is concentrated in
**module size and function complexity** — most of it pre-existing, not
caused by the ADR but exposed because the ADR added new code to already-
oversized modules. One probe-health defect in the skill itself surfaced
during this run.

## Severity counts

| Critical | High | Medium | Low | Total |
|----------|------|--------|-----|-------|
| 0 | 9 | 3 | 2 | 14 |

## Top findings

1. **High** — `src/gzkit/governance/trust_audits.py` is **2129 LOC** (3.5× the 600 LOC cap) with **14 rank-C complexity functions**. ADR-0.0.21 added one more `audit_chores_layout` to a file that was already deeply over budget. **Route: OBPI** — this is a refactor brief, not a one-liner.
2. **High** — Three more cli-parser / command modules over the size cap: `parser_artifacts.py` (1057), `validate_cmd.py` (1032), `parser_maintenance.py` (1024). **Route: chore** (`module-sloc-cap-radon`).
3. **High** — Newly-added `chores_doctor` (line 543) and `_render_doctor_table` (line 511) in `chores.py` are both rank C. Direct from OBPI-0.0.21-09. **Route: GHI**, scoped fix.

## Findings table

| Severity | Class | Location | Recommendation (one-line) | Route |
|----------|-------|----------|----------------------------|-------|
| High | size-cap | `src/gzkit/governance/trust_audits.py` (LOC=2129) | Split by audit family into `trust_audits/<family>.py` | OBPI |
| High | size-cap | `src/gzkit/cli/parser_artifacts.py` (LOC=1057) | Split per artifact family (`adr`, `obpi`, `chores`, `ghi`) | chore |
| High | size-cap | `src/gzkit/commands/validate_cmd.py` (LOC=1032) | Split per scope into `commands/validate/<scope>.py` | chore |
| High | size-cap | `src/gzkit/cli/parser_maintenance.py` (LOC=1024) | Split per family (quality / validate / governance) | chore |
| High | size-cap | `src/gzkit/commands/init_cmd.py` (LOC=676) | Extract `_repair_missing_artifacts` and `_register_existing_artifacts` to `init_repair.py` | chore |
| High | size-cap | `src/gzkit/commands/common.py` (LOC=627) | Extract path-resolution helpers to `commands/resolve.py` | chore |
| High | size-cap | `src/gzkit/commands/chores.py` (LOC=625) | Extract doctor handlers to `chores_doctor.py` | GHI |
| High | complexity | `validate_cmd.py:817 validate` (CC=17) | Replace if/elif chain with scope→handler dispatch table | chore |
| High | complexity | `trust_audits.py:1345 audit_adr_taxonomy` (CC=18) | Extract `_kind_semver_consistent`, `_lane_kind_consistent`, `_pool_no_kind_or_semver` predicates | chore |
| High | complexity | `chores.py:543 chores_doctor` (rank C) | Pull slug iteration into `_doctor_iter_slugs(...)` | GHI |
| Medium | complexity | `trust_audits.py` (14 rank-C functions) | Resolve naturally during the size-cap split | OBPI |
| Medium | frontmatter-drift | `OBPI-0.0.21-05.md` Allowed Paths | Append Implementation Summary note: `chores.py` landed as `chores/__init__.py` | GHI |
| Medium | probe-health | `gz-tech-debt-review` skill | Drop ARB wrapping from coverage probe — caused exit_status=1 receipt pollution | in-flight |
| Low | tests | `validate_cmd.py` 69% scoped coverage | Add tests for `_print_validation_result` unhappy paths during validate split | chore |
| Low | frontmatter-drift | `OBPI-0.0.21-05.md` test-path | Bundle into the path-drift note | discard |

**Counts:** Critical: 0 | High: 9 | Medium: 3 | Low: 2 | Total: 14

---

## Per-finding detail (Critical & High inline; Medium & Low collapsed)

### [High] size-cap: `src/gzkit/governance/trust_audits.py`

**Evidence**
> radon raw: LOC=2129. Module cap per `.claude/rules/pythonic.md` § Size Limits & Refactoring is **600 LOC**. The file houses ~30 `audit_*` functions across CLI alignment, governance, taxonomy, sensitivity, chores layout, brief headings, behave coverage, and orientation freshness. ADR-0.0.21 added `audit_chores_layout` at line 1541 to an already 2000+ LOC file.

**Why this is debt**
`.claude/rules/pythonic.md` § Size Limits is binding. A 3.5× cap violation is the dominant smell when a contributor opens this file — the structural answer to *"where does my new audit go?"* is no longer obvious, and the file is already too big for a fresh reader to hold in head. AGENTS.md § DO IT RIGHT #1 ("Fix the class of failure") names the right move: not "trim a few functions" but "establish a partition that makes the next audit add additive instead of growing the C-rank floor."

**Recommended fix**
Split by audit family into a `trust_audits/` package:

```
src/gzkit/governance/trust_audits/
├── __init__.py          # re-exports all audit_* names
├── cli.py               # audit_cli_alignment, audit_skill_alignment
├── governance.py        # audit_pydantic_models, audit_class_size, audit_test_tiers
├── taxonomy.py          # audit_adr_taxonomy, audit_pool_adr_isolation
├── sensitivity.py       # audit_sensitivity_binding, _extract_sensitivity_allowed_paths
├── chores.py            # audit_chores_layout
├── briefs.py            # audit_brief_headings, _extract_heavy_obpi_briefs, audit_behave_req_tags
├── orientation.py       # audit_orientation_freshness, _settings_session_start_command_strings
├── reconcile.py         # audit_reconcile_freshness
└── _ledger.py           # _collect_claimed_event_types, _collect_emitted_event_types
```

`__init__.py` re-exports keep every existing import site working unchanged.

**Route:** `OBPI` — this is a refactor brief; multiple ADRs depend on these audits and the partition deserves an architectural ADR slot, not a chore-runner pass.

---

### [High] size-cap: `src/gzkit/cli/parser_artifacts.py`

**Evidence**
> radon raw: LOC=1057. Houses `_register_*` parser functions for every artifact subcommand (adr, obpi, ghi, chores, etc.).

**Why this is debt**
Same rule as above. parser_artifacts is the single point of friction every time a new subcommand lands — and ADR-0.0.21-09 just added `chores doctor` here.

**Recommended fix**
Split per artifact family into `src/gzkit/cli/parsers/<family>.py`. `parser_artifacts.py` keeps the dispatcher that calls each family's `register(parser)` function. Adding a new subcommand becomes one small file, not a 1057-line edit.

**Route:** `chore` — `module-sloc-cap-radon` chore exists for exactly this class.

---

### [High] size-cap: `src/gzkit/commands/validate_cmd.py`

**Evidence**
> radon raw: LOC=1032. Houses every `_run_<scope>_scope` and `_<scope>_records` helper for every `gz validate` flag, plus the `validate()` dispatcher (line 817, CC=17).

**Why this is debt**
Same rule. Worse here because the file's `validate()` dispatcher is also a complexity hot-spot — both findings have the same root and the same fix.

**Recommended fix**
Split per scope into `src/gzkit/commands/validate/<scope>.py`. Each scope's `_run_<scope>_scope` and `_<scope>_records` move together. `validate_cmd.py` keeps the CLI handler + scope registry. The dispatch in `validate()` becomes a `SCOPE_HANDLERS: dict[str, Callable]` lookup — kills the CC=17 finding too.

**Route:** `chore` — `module-sloc-cap-radon`.

---

### [High] size-cap: `src/gzkit/cli/parser_maintenance.py`

**Evidence**
> radon raw: LOC=1024. Houses `_register_quality_parsers` and the maintenance flag registrations including `--chores-layout` (line 385) added by OBPI-0.0.21-08.

**Recommended fix**
Same partition pattern as parser_artifacts. Quality / validate-flag / maintenance / governance — each its own small module.

**Route:** `chore` — `module-sloc-cap-radon`.

---

### [High] size-cap: `src/gzkit/commands/init_cmd.py`

**Evidence**
> radon raw: LOC=676. ADR-0.0.21 added `scaffold_core_chores` call sites at lines 242 and 525. Two of the three rank-C functions are here: `_repair_missing_artifacts` (265) and `_register_existing_artifacts` (371) and `init` (421).

**Recommended fix**
Extract `_repair_missing_artifacts` and `_register_existing_artifacts` into `src/gzkit/commands/init_repair.py`. Each is rank C, so the move kills two findings at once and pulls 200+ LOC out of init_cmd. The remaining `init()` handler stays focused on the scaffolding flow itself.

**Route:** `chore` — `module-sloc-cap-radon`. Two complexity hits resolved as a side-effect.

---

### [High] size-cap: `src/gzkit/commands/common.py`

**Evidence**
> radon raw: LOC=627. Houses `resolve_obpi` (line 336, rank C) and `resolve_adr_file` (line 212, rank C).

**Recommended fix**
Extract path-resolution helpers (resolve_obpi, resolve_adr_file, brief-frontmatter parsing) into `src/gzkit/commands/resolve.py`. `common.py` becomes CLI-utility helpers only (`_confirm`, `console`, etc.).

**Route:** `chore` — `module-sloc-cap-radon`.

---

### [High] size-cap: `src/gzkit/commands/chores.py`

**Evidence**
> radon raw: LOC=625. Houses `chores_doctor` (line 543, rank C — added by OBPI-0.0.21-09), `_render_doctor_table` (line 511, rank C), `_load_chores_registry` (line 218, rank C).

**Why this is debt**
The doctor command is freshly added and is already pushing the file over cap. Easy to address now while the design is fresh.

**Recommended fix**
Extract the doctor scope (chores_doctor, _render_doctor_table, doctor option parsing) into `src/gzkit/commands/chores_doctor.py`. Per OBPI-0.0.21-09 the doctor scope is self-contained — clean cut line.

**Route:** `GHI` — single-issue, scoped, directly tied to a Validated foundation ADR.

---

### [High] complexity: `validate_cmd.py:817 validate` (CC=17)

**Evidence**
> xenon: rank C, CC=17. Top-level dispatcher over every `--<scope>` flag (chores-layout, frontmatter, requirements, behave-req-tags, etc.).

**Recommended fix**
Replace the if/elif chain with a `SCOPE_HANDLERS: dict[str, Callable[[Args], list[ValidationError]]]` lookup. Each entry maps a flag name to its existing `_run_<scope>_scope` helper. Adding a new scope becomes additive (one dict entry + one helper) instead of growing the C-rank function further.

**Route:** `chore` — `complexity-reduction-xenon`. Naturally resolved when validate_cmd is split.

---

### [High] complexity: `trust_audits.py:1345 audit_adr_taxonomy` (CC=18)

**Evidence**
> xenon: rank C, CC=18 (highest C in the file). Audit logic for kind/lane/semver consistency is one fat function.

**Recommended fix**
Extract three predicates that map cleanly to the rules in AGENTS.md § Kinds:
- `_kind_semver_consistent(kind, semver) -> bool` — foundation ⇒ 0.0.x; feature ⇒ non-0.0.x
- `_lane_kind_consistent(kind, lane) -> bool` — pool ⇒ no lane required
- `_pool_no_kind_or_semver(frontmatter) -> bool` — pool ⇒ no kind/semver

Each predicate is independently testable and the audit body becomes a list comprehension over `(adr_id, predicate, message)` tuples.

**Route:** `chore` — `complexity-reduction-xenon`.

---

### [High] complexity: `chores.py:543 chores_doctor` (rank C)

**Evidence**
> xenon: rank C. Newly added in OBPI-0.0.21-09; bundles fan-out over slugs, before/after diff, dry-run handling, and JSON shaping.

**Recommended fix**
Pull the slug-iteration loop into a pure function:

```python
def _doctor_iter_slugs(
    project_root: Path,
    registry: ChoresRegistry,
    dry_run: bool,
) -> Iterator[DoctorRecord]:
    ...
```

`chores_doctor` keeps argument parsing, the iter call, and the render dispatch. Pure function is also trivially testable.

**Route:** `GHI` — direct from OBPI-0.0.21-09; small, scoped fix.

---

<details>
<summary>Medium and Low findings (5)</summary>

### [Medium] complexity: `trust_audits.py` (14 rank-C functions)

**Evidence**
> 14 rank-C functions: audit_sensitivity_binding (1969), _collect_claimed_event_types (326), _scan_doc_pipe_patterns (449), audit_reconcile_freshness (1253), audit_skill_alignment (1150), _script_section_headings (1706), audit_cli_alignment (209), _extract_heavy_obpi_briefs (1006), _parse_adr_frontmatter (1441), _settings_session_start_command_strings (1659), audit_orientation_freshness (1753), audit_pydantic_models (637), audit_pool_adr_isolation (879), audit_chores_layout (1541).

**Why this is debt**
Each function individually deserves a complexity reduction, but addressing them one at a time fragments the architectural opportunity.

**Recommended fix**
Combine with the size-cap-trust-audits split. Each audit family becomes its own module; complex functions break naturally during the move because the helpers come with them.

**Route:** `OBPI` — cluster; tracked under the size-cap split.

---

### [Medium] frontmatter-drift: OBPI-0.0.21-05 Allowed Paths

**Evidence**
> Brief Allowed Paths: `src/gzkit/chores.py — new module at this path`. Implementation: `src/gzkit/chores/__init__.py` (the package's init). Both produce the same import surface (`from gzkit.chores import scaffold_core_chores`); call sites at `init_cmd.py:9, 242, 525` and `chores.py:545, 567` confirm. The brief's Allowed Paths is now stale relative to disk.

**Why this is debt**
Trust-doctrine T2 says the ledger is canon and Layer-1 (brief frontmatter) must be reconciled against canon. ADR-0.0.21 is `Validated` — the brief is supposed to record what was decided, but the chosen path differs from disk. The package form (`chores/__init__.py`) was required because chores ship per-slug subdirectories as `importlib.resources` data; that decision didn't make it back into the brief.

**Recommended fix**
Append a `### Implementation Summary` note to OBPI-0.0.21-05:

> `scaffold_core_chores` landed at `src/gzkit/chores/__init__.py` rather than the brief's planned `src/gzkit/chores.py` — the package form was required to ship per-slug subdirectories as `importlib.resources` data. Import surface (`from gzkit.chores import ...`) is identical.

Do **not** rewrite Allowed Paths — that erases the audit trail. The brief is Layer-1 authorship; a post-hoc clarification preserves the historical record.

**Route:** `GHI` — file as defect-class, link to ADR-0.0.21.

---

### [Medium] probe-health: `gz-tech-debt-review` skill

**Evidence**
> Running `uv run gz arb coverage run -m unittest discover -s tests -t .` as a probe writes an ARB receipt with `exit_status=1` (the coverage report exits 1 by default in some configurations). AGENTS.md § Attestation anti-patterns: *"Authoring `arb-step-*` receipts with `exit_status=1` as 'RED receipts' — pollutes ARB corpus"*. Receipt `arb-step-coverage-63f9be310af44cb9a85d43926a8a75ca.json` was just created by this audit run.

**Why this is debt**
Skill defect in the very skill that produced this report. The diagnostic-vs-attestation boundary leaked: ARB is for attestation evidence, debt review is diagnostic.

**Recommended fix**
In `.gzkit/skills/gz-tech-debt-review/SKILL.md` Step 2 probe table, change the `tests` row from `uv run gz arb coverage ...` to:

```bash
uv run coverage run -m unittest discover -s tests -t . && \
uv run coverage report --include="<scope-glob>"
```

Reserve `gz arb step` for attestation-bound contexts (the `--draft-ghis` path, where receipt IDs go into the GHI bodies).

**Route:** `in-flight` — meets `AGENTS.md § Defect-fix routing` thresholds (≤10 lines, ≤2 files, single bounded scope, fix surfaced in flight).

---

### [Low] tests: `validate_cmd.py` 69% scoped coverage

**Evidence**
> Scoped coverage: chores/__init__.py 93%, trust_audits.py 84%, chores.py 79%, chores_exec.py 77%, init_cmd.py 76%, validate_cmd.py 69%. Total scoped: 80% — well above the 40% floor.

**Recommended fix**
Add unit tests covering `_print_validation_result` (line 771, also a complexity hot-spot) and the unhappy-path branches in `_run_<scope>_scope`. Bundle with the validate_cmd split.

**Route:** `chore` — `coverage-40pct`.

---

### [Low] frontmatter-drift: OBPI-0.0.21-05 test-path

**Evidence**
> Brief Allowed Paths: `tests/test_chores_scaffold.py — optional new test module if test_init.py becomes >600 lines`. The optional module was not created; chores tests live under `tests/commands/test_init.py` and `tests/governance/test_audit_chores_layout.py`.

**Recommended fix**
Bundle into the same Implementation Summary note as the path drift above. Optional Allowed Paths that did not materialize do not need separate tracking.

**Route:** `discard`.

</details>

---

## Clean classes

| Class | Result |
|-------|--------|
| `lint` | `uv run ruff check <scope>` — clean |
| `types` | `uvx ty check <scope>` — All checks passed |
| `types-suppression` | grep `# type: ignore[code]` — only docstring/help-text matches; no real suppressions |
| `governance` | `gz validate --frontmatter --requirements --behave-req-tags` — all clean |
| `validators` | `gz validate --chores-layout --advisory-scorecard` — clean |
| `cli-drift` | `gz cli audit` (89/89 covered) and `gz validate --cli-alignment` — clean |
| `todo-rot` | git grep `TODO|FIXME|XXX|HACK` in scope — no hits |

ADR-0.0.21 ships clean on every signal **except** module-size and
function-complexity — which is the classic foundation-ADR shape: the new
audit is fine, but it landed in modules that were already over cap.

---

## Recommended next operator action

**Route the 9 High findings.** Most consolidate cleanly into one move:

1. **Open one OBPI** (or refactor ADR) for the trust_audits split — picks up `size-cap-trust-audits` plus the 14-function complexity cluster in one stroke.
2. **Queue 5 chores under `module-sloc-cap-radon`** for parser_artifacts, validate_cmd, parser_maintenance, init_cmd, common.
3. **File 2 GHIs** for the chores.py size split + chores_doctor complexity (both directly tied to OBPI-0.0.21-09; small, scoped).
4. **Apply the probe-health fix in-flight** to gz-tech-debt-review SKILL.md (replace ARB-wrapped coverage with a plain coverage probe).
5. **File one frontmatter-drift GHI** for the OBPI-0.0.21-05 implementation note.

The Lows (one coverage gap, one optional-path note) bundle into existing chore lanes — no separate routing.
