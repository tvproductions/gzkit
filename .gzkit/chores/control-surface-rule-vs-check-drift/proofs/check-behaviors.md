# Check-Behavior Extraction

**Generated:** 2026-08-01 (audit-only re-run; supersedes the 2026-05-10 artifact)
**Method:** every entry below was read out of the implementation, not from a
`--help` string or a docstring. Where a docstring and the code disagree, the
code is recorded and the disagreement is flagged.

Read-only pass. No validator, rule, or source file was modified.

**Global machinery that qualifies every row (read this first):**

- **Exit is type-driven, not scope-driven.** `_print_validation_result`,
  `src/gzkit/commands/validate_cmd.py:1151-1173`:
  `policy_errors = [e for e in errors if e.type in _POLICY_BREACH_ERROR_TYPES]`;
  `if other_errors: raise SystemExit(1)` is evaluated **before**
  `if policy_errors: raise SystemExit(3)`. A scope whose `type` string is absent
  from `_POLICY_BREACH_ERROR_TYPES` (`validate_cmd.py:1081-1129`) exits **1**
  regardless of what its prose claims, and one non-breach finding in a mixed run
  downgrades genuine breaches from 3 to 1.
- **MX hangar drops most scopes wholesale.** `_run_scope_checks`,
  `validate_cmd.py:974-993`, appends findings only if
  `disposition.grounds(checkpoint.resolve(scope, levels.ERROR, project_root))`.
  `checkpoint.resolve` (`src/gzkit/mx/checkpoint.py:29-33`) returns
  `Route.ADVISORY` for any guard outside
  `GATE5_INVARIANTS = {"gate5-attestation","secrets","operator-pii","ledger","grader-gaming"}`
  (`src/gzkit/mx/invariants.py:23-31`) whenever `.gzkit/mx.json` exists.
  Of 81 registry stems exactly one (`ledger`) is a floor member. Errors are
  **dropped from the list**, not demoted-and-printed.
- **Two scopes bypass that machinery entirely** via solo handlers that never
  consult the checkpoint: `--unscoped-rules` (`validate_cmd.py:680-733`) and
  `--sensitivity` (`validate_cmd.py:857-917`). Both stay exit-3 fail-closed
  inside the hangar.
- **`--audits` is refused, not run.** `parser_maintenance.py:1077,1110,1113` fold
  `--audits` into `check_type_ignores`, `check_unscoped_rules`, and
  `check_sensitivity`, making `other_scopes_active` true, so
  `_dispatch_early_return_scopes` hits `_refuse_combined_solo_scopes` and exits 1
  without running anything (`validate_cmd.py:1237-1259`, `:1316-1330`).

---

## A. Scopes claimed by canonical rule prose

### A1. `--advisory-scorecard` → `audit_advisory_scorecard`
`src/gzkit/governance/trust_audits/release.py:84` · tier `explicit` · not in `gz check`

- **Predicate (one, substring-only):** for each `rules_root.glob("*.md")`,
  `rule_md.stem.lower() in scorecard_text` where
  `scorecard_text = scorecard.read_text().lower()`. It asserts the stem appears
  *anywhere in the file as a substring* — not that a table row exists, not that
  one of the four scores (Mechanical / Promotable / Judgment / Ambiguous) was
  assigned. A stray cross-reference satisfies it.
- **Scope:** `.gzkit/rules/*.md` (non-recursive) vs `docs/governance/advisory-rules-audit.md`.
- **Fails open:** `if not scorecard.is_file() or not rules_root.is_dir(): return []`.
- **Exit:** `type="advisory_scorecard"` not in breach set → **exit 1**.

### A2. `--utf8-prefix` → `audit_utf8_prefix`
`src/gzkit/governance/trust_audits/cross_platform.py:92` · `explicit` · not in `gz check`

Four regex predicates over text:

1. `_PYTHONUTF8_PREFIX = re.compile(r"PYTHONUTF8=1\s+uv\s+run\s+(?:gz|-m\s+gzkit)")` (`:85`)
2. `_GZ_PIPE_PYTHON` (`:89`) matched **and** `_STDOUT_RECONFIGURE = re.compile(r"sys\.stdout\.reconfigure\s*\(\s*encoding\s*=\s*['\"]utf-?8['\"]")` (`:95`) absent on the same logical line
3. `_GZ_PIPE_NON_PYTHON` (`:93`), matching a `gz` pipe into `jq|awk|sed` — unconditional
4. `tools/**/*.py`: AST-detected `if __name__ == "__main__"` + a `print` call (`_is_entry_point_script`, `:267`) with no `_STDOUT_RECONFIGURE` anywhere

- **Scope:** `_DOC_PIPE_SCAN_ROOTS = ("docs", ".gzkit/skills", ".claude/skills", "features")` (`:187`), suffixes `{.md,.feature,.txt}`; backslash continuations coalesced (`_coalesce_continuations`, `:166`).
- **Waivers:** `_UTF8_PIPE_WAIVERS` — hardcoded `"<relpath>:<lineno>"` dict, 10 entries (`:27-80`); blanket skip for any file named `advisory-rules-audit.md` (`:159-161`).
- **Exit:** not in breach set → **exit 1**.

### A3. `--cli-alignment` → `audit_cli_alignment` **+** `audit_manpage_alignment`
Registry lambda `validate_cmd.py:266-271` · `explicit` · **not in `gz check`**

**A3a. `audit_cli_alignment`** — `src/gzkit/governance/trust_audits/cli.py:133`

Verb-resolution regexes, verbatim (`cli.py:28-30`):

```python
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION     = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE      = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')
```

- **Only the first token is resolved.** `group(1)` captures one
  `[a-z][a-z0-9-]*` run; everything after the first whitespace is swallowed by
  the trailing `[^...]*`. It is compared against `_known_cli_verbs()`
  (`cli.py:222-232`), which enumerates **only top-level `argparse._SubParsersAction`
  choices** and does not recurse. A nested-subparser-aware helper
  `_known_cli_verb_paths()` exists at `cli.py:257` but is used by
  `audit_skill_alignment`, **not** here. Net observable behavior: a reference to
  `gz adr status` is checked as `adr`; `gz adr <typo>` passes.
- **Scope** (`_cli_alignment_sources`, `cli.py:104-117`): `features/**/*.feature`,
  `docs/user/runbook.md`, `docs/user/commands/**/*.md`, `docs/user/manpages/**/*.md`.
  Briefs, ADRs, and `.gzkit/skills/**/SKILL.md` are **not** scanned — though the
  rule's own § scope names skills and both runbooks.
- `_DOC_PROSE_VERBS: frozenset[str] = frozenset()` (`cli.py:19`) — declared, empty.
- **Exit:** `type="cli_alignment"` not in breach set → **exit 1**.

**A3b. `audit_manpage_alignment`** — `cli.py:188`

- **Predicate:** `_MANPAGE_GZ_PREFIX_REF = re.compile(r"manpages/(gz-[a-z0-9-]+\.md)")`
  (`cli.py:24`) per physical line. A dead-string check only — it never verifies the
  de-prefixed manpage exists.
- **Scope** (`_manpage_alignment_sources`, `cli.py:155-186`): all `docs/**/*.md`
  except `docs/releases/`, plus `features/**/*.feature`, plus
  `.gzkit/skills/**/SKILL.md`. Wider than A3a.
- **Exemption:** paths containing `design/adr` whose `^status:` frontmatter satisfies
  `is_terminal_brief_status` (`src/gzkit/governance/brief_structure.py:69`).
- **Exit:** `type="manpage_alignment"` not in breach set → **exit 1**.

### A4. `--class-size` → `audit_class_size`
`src/gzkit/governance/trust_audits/code_quality.py:73` · `explicit` · not in `gz check`

- Predicates: (a) every `ast.ClassDef` reachable via `ast.walk` with
  `end_lineno - lineno + 1 > 300` (limit is a **local** `limit = 300`, not a module
  constant); (b) stale-waiver assertion — every `_CLASS_SIZE_WAIVERS` key must name
  an extant class.
- **Scope:** `src/gzkit/**/*.py`. `SyntaxError` files silently skipped. Includes
  nested/inner classes.
- **Waivers:** `_CLASS_SIZE_WAIVERS` (`code_quality.py:23-32`), 2 entries:
  `src/gzkit/ledger.py::Ledger`, `src/gzkit/hooks/obpi.py::ObpiValidator`.
- **Exit:** not in breach set → **exit 1**.

### A5. `--pydantic-models` → `audit_pydantic_models`
`src/gzkit/governance/trust_audits/models.py:69` · `explicit` · not in `gz check`

- Predicates: (1) a `dataclass` decorator (`_has_dataclass_decorator`, `:93`) not
  waived; (2) a class with a base literally named `BaseModel` (`:108`) and no
  `model_config` assignment; (3) stale-waiver assertion over `_DATACLASS_WAIVERS`.
- **It never inspects `ConfigDict` keyword arguments.** `_has_model_config`
  (`models.py:117-131`) returns `True` for *any* `Assign`/`AnnAssign` whose target is
  the bare name `model_config`, regardless of RHS. `model_config = None`,
  `model_config = {}`, and `model_config = ConfigDict()` all pass. `frozen=True` and
  `extra="forbid"` are never read, even though the emitted error message says
  `model_config = ConfigDict(...)`.
- **Waivers:** `_DATACLASS_WAIVERS` (`:18-23`), 1 entry
  (`src/gzkit/commands/obpi_precomplete.py::CheckResult`). No waiver channel for the
  missing-`model_config` arm.
- **Exit:** not in breach set → **exit 1**.

### A6. `--test-tiers` → `audit_test_tiers`
`code_quality.py:126` · `explicit` · not in `gz check`

- Predicates: (a) `(project_root/"tests"/name).exists()` for
  `("integration","e2e","slow","bdd")` — existence only, file or dir;
  (b) plain substring `flag in text` for `("--integration","--e2e","--slow","--bdd-only")`
  over `src/gzkit/cli/**/parser*.py` (`rglob("parser*.py")`) — a mention inside a
  comment or help string counts.
- No waivers. **Exit:** not in breach set → **exit 1**.

### A7. `--type-ignores` → `audit_type_ignores`
`code_quality.py:37` · `explicit` · not in `gz check`

- Predicate: `_FORBIDDEN_TYPE_IGNORE = re.compile(r"#\s*type:\s*ignore\[")` (`:34`)
  applied **only to `tokenize.COMMENT` tokens**, so string literals and docstrings do
  not match. It does **not** verify the sanctioned `# ty: ignore[...]` form is used —
  it only forbids the bracketed mypy form.
- **Scope:** `src/**/*.py` (note: `project_root / "src"`, *not* `src/gzkit`, unlike A4/A5).
- No waivers; `SyntaxError`/`TokenError` files silently skipped.
- **Exit:** not in breach set → **exit 1**.

### A8. `--chores-layout` → `audit_chores_layout`
`src/gzkit/governance/trust_audits/chores.py:29` · `explicit` · not in `gz check`

- Predicates: (a) any file whose relpath starts with `ops/chores/`; (b) a file named
  `CHORE.md` or `acceptance.json` (`_CHORES_LAYOUT_FILES`) not under
  `src/gzkit/chores/` or `<config.paths.chores>/`. (a) short-circuits with `continue`,
  so a file yields at most one finding.
- **Scope:** full `os.walk`, pruning dot-dirs and
  `_CHORES_LAYOUT_EXCLUDED_SEGMENTS = {"__pycache__",".venv","dist","build","node_modules"}` (`:13-15`).
- **Waivers:** `data/chores_layout_waivers.json` (bare JSON list of posix relpaths,
  `_load_chores_layout_waivers`, `:117`); malformed/missing → empty set.
- **Exit:** `type="chores_layout"` **in** breach set (`validate_cmd.py:1084`) → **exit 3**. Matches prose.

### A9. `--unscoped-rules` → `run_unscoped_rules` (solo handler)
Handler `validate_cmd.py:680-733`; validator `src/gzkit/validators/unscoped_rules.py:149` · **in `gz check`**

- Predicates: `classify_paths_field` (`:52`) yields `"missing"` (no `paths:` key, or
  present but empty/`null`/`~`) or `"universal-glob"` (all parsed values `== "**"`);
  `"concrete"` passes. Manifest or rule file unreadable → `exit_code=2`.
- **Scope:** `.gzkit/rules/*.md` **non-recursive, excluding `AGENTS.md`** (`:169-171`).
  **It never reads any vendor mirror** — not `.claude/rules/`, `.agents/`, or `.github/`.
- **Allowlist:** `.gzkit/manifest.json → rules.unscoped_allowlist`, entries validated
  by `UnscopedAllowlistEntry` (`:233`): `rationale` >= 20 chars, `tracking_ref` matching
  `^(GHI-\d+|ADR-[\d.]+[-\w]*)$`. `added_date` is stored but **never compared to today** —
  no expiry is enforced.
- **Exit:** solo handler raises **3** on any non-allowlisted violation, 2 on IO error.
  Bypasses `_print_validation_result` and the MX checkpoint — **fail-closed inside the hangar**.

### A10. `--instructions-files-budget` → `audit_instructions_files_budget` **+** `audit_surface_delivery_witness`
Registry lambda `validate_cmd.py:308-319` · `explicit` · **in `gz check`**

**A10a. Budget** — `src/gzkit/governance/trust_audits/instructions_files_budget.py:61`

- Predicate: `len(target.read_text())` (**chars**, not bytes) `> budget`, for each
  `config["files"]` entry and each file matched by each `config["globs"][].pattern`.
- Config: `data/instructions_files_budget.json` if present, else `_PACKAGED_DEFAULTS`
  (`:32-35`) = `{"files": {"AGENTS.md": 40000, "CLAUDE.md": 40000},
  "globs": [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 16000}]}`.
  Editing that JSON is the de-facto waiver.
- **Exit:** `type="instructions_files_budget"` in breach set → **exit 3**.

**A10b. Delivery witness** — `src/gzkit/governance/trust_audits/surface_delivery_witness.py:192`

- **Fail-closed arm** (`_declaration_errors`, `:76-117`, `type="surface_delivery_witness"`,
  in breach set → exit 3): coherence between `data/agents_md_survival_declaration.json`
  and the rendered surface — invalid JSON; no `surfaces` map; malformed entry; declared
  surface missing on disk; `rank` values not exactly contiguous `1..len(declared)`;
  `must_survive_through_rank` not an int in range; a rendered `## ` heading id absent
  from the declaration; a declared id no longer rendering.
- **Advisory arm** (`_observe_delivery`, `:124-156`): rendered byte count vs
  `delivery_cap_for(content_type, vendor)` — emits `NOTE …headroom` / `WARNING …B OVER`
  to stderr via `emit_advisory`, **never returned**, never changes the exit code
  (2026-07-06 decoupling ruling, cited `:17-24`).
- **Escape:** absence of `data/agents_md_survival_declaration.json` → `return []`.

### A11. `--agents-md-map-conformance` → `audit_agents_md_map_conformance`
`src/gzkit/governance/trust_audits/agents_md_map_conformance.py:95` · `explicit` · **in `gz check`**

- **Two-layer, asymmetric scope — the load-bearing fact.** Criteria (a)/(b)/(c) and
  the advisory arm run **only against the template `src/gzkit/templates/agents.md`**;
  criterion (d) runs **only against the rendered root `AGENTS.md`**. The rendered
  `AGENTS.md` is never shape-checked; the template is never budget-checked.
- (b) prohibited H2+ heading title, case-insensitive, in
  `_PROHIBITED_TITLES = {"worked example","anti-patterns","rationale","why this is canon"}`
  or matching `re.compile(r"^why\s+.+\s+is\s+canon$", re.IGNORECASE)` (`:66-79`).
- (a) any paragraph (consecutive non-blank, non-heading, non-table, non-fenced
  lines) longer than 5 lines whose first line does not start with a bullet, `**`,
  or `^\d+\.\s` (`_check_paragraph_shape`, `:194`).
- (c) every markdown link resolving to an existing file; when `#anchor` present, the
  anchor must slug-match a heading in the target (`_check_link_resolution`, `:277`).
- (d) rendered `AGENTS.md` char count `> budget`.
- **Advisory arm** (`_check_per_bullet_advisory`, `:395`): per-bullet 3-line heuristic
  over `_BINDING_RULE_SECTION_TITLES`, emitted as
  `type="agents_md_map_conformance_advisory"`. Its docstring (`:398-399`) claims it
  "does not change exit code" — **false**: it is returned in the same list, is not in
  the breach set, and therefore forces `SystemExit(1)`, which also **downgrades**
  co-occurring hard findings from 3 to 1.
- **Exit:** hard `type="agents_md_map_conformance"` in breach set → 3 (subject to the above).

### A12. `--adr-status-fresh` → `audit_adr_status_fresh`
`src/gzkit/governance/trust_audits/taxonomy.py:545`, delegating to `compute_drift`
(`src/gzkit/governance/adr_status_index.py:212`) · `explicit` · **in `gz check`**

- Predicates: index missing → one `(file)` entry; on-disk ADR with no table row
  (`missing`); table row with no on-disk ADR (`obsolete`); per-ADR signature mismatch
  across the 7-tuple `("adr_id","title","kind","lane","status","date","rel_path")`
  (`adr_status_index.py:231`), reported field-by-field.
- No waivers. **Exit:** `type="adr_status_fresh"` not in breach set → **exit 1**
  (prose at `governance-core.md:94` says "fail-closed").

### A13. `--taxonomy` → `_taxonomy_runner` = `audit_adr_taxonomy` + `audit_foundation_closure`
Registry `validate_cmd.py:252`, tier **`default`**; runner `:477-491` · **in `gz check`**

**A13a. `audit_adr_taxonomy`** — `taxonomy.py:416`, decision tree at `_audit_one_adr_taxonomy` (`:156-175`)

```python
if is_pool:
    pool_err = _check_pool_taxonomy(rel, kind)
    return [pool_err] if pool_err else []
```

- `_check_pool_taxonomy` (`taxonomy.py:112-120`) inspects **`kind` only** and returns
  immediately. `semver` is read at `:165` but, on the pool branch, is **never
  examined**. A pool ADR carrying `semver:` frontmatter passes.
- Non-pool: missing `kind` → error; `kind not in ("foundation","feature")` → error;
  `kind == "foundation"` failing `_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")` → error;
  `kind == "feature"` matching it → error.
- **Scope:** `_iter_adr_files` (`:227`) — union of `docs/design/adr` and
  `GzkitConfig.paths.adrs`, `rglob("ADR-*.md")`, skipping paths containing
  `obpis`/`briefs`/`audit` (`_NESTED_ADR_DIRS`, `:95`). A file with no `---`
  frontmatter block is **silently skipped** (`_parse_adr_frontmatter` → `None`).
- **Exit:** `type="taxonomy"` not in breach set → **exit 1**.

**A13b. `audit_foundation_closure`** — `taxonomy.py:353`

- `foundation_kind_closed` / `grandfather_dangling` / `foundation_limbo` (the last
  requiring an **attested** `foundation_grandfathered` ledger event, attestor non-blank
  after `.strip()`, `:283-309`).
- Grandfather manifest `data/foundation_grandfather.json` (`:180`); missing file →
  `set()`, which turns every on-disk foundation ADR into a finding.
- **Exit:** all three types **in** breach set (`validate_cmd.py:1115-1117`) → 3 —
  unless an A13a finding co-occurs, which drags the run to 1.

### A14. `--behave-req-tags` → `audit_behave_req_tags`
`src/gzkit/governance/trust_audits/briefs.py:557` · `explicit` · not in `gz check`

- Predicate: a REQ-ID whose kind is `behavior` appearing in **neither** the behave tag
  set **nor** the `@covers` set. Kinds from
  `_REQ_KIND_TAG = re.compile(r"\[(behavior|support|structural-fence)\]", re.IGNORECASE)`;
  an untagged REQ defaults to `behavior` (fail-closed).
  Tag sources: `_SCENARIO_REQ_TAG = re.compile(r"^\s*@(REQ-\d+\.\d+\.\d+-\d+-\d+)\b", re.MULTILINE)`
  over `features/**/*.feature` (`:28`); `_COVERS_REQ_TAG` over `tests/**/*.py` (`:35`).
- **Eligibility filter** (`_extract_one_heavy_brief`, `:179`): `docs/design/adr/**/OBPI-*.md`
  excluding any path with a `pool` part; requires frontmatter `lane: heavy`, `status` in
  `_BDD_GATED_BRIEF_STATUSES = frozenset({"completed","validated"})` (`:56`), a parseable
  `id:`, and a `## Acceptance Criteria` section. Any brief failing any of these is
  silently out of scope.
- **Waivers:** `data/behave_coverage_waivers.json`, keyed by OBPI id — **whole-brief,
  not per-REQ** (`:134`).
- **Exit:** not in breach set → **exit 1** (the rule claims no exit code, so no gap).

### A15. `--sensitivity` → `audit_sensitivity_binding` (solo handler `_run_sensitivity_scope`)
Audit `src/gzkit/governance/trust_audits/sensitivity.py:222`; handler `validate_cmd.py:857-917` · `explicit` · not in `gz check`

- Six finding types: `sensitivity-registry-missing`, `sensitivity-registry-malformed`
  (both returned as the sole finding, aborting the walk), `sensitivity-malformed-allowlist`,
  `sensitivity-escape-attempt` (overlap + `declared not in (None,"security")`),
  `sensitivity-floor-violation` (overlap + `declared is None`), `sensitivity-floor-info`
  (same, grandfathered).
- **Scope:** `docs/design/adr/**/{obpis,briefs}/*.md` (`_iter_sensitivity_briefs`, `:113`);
  allowed paths parsed from the `## ALLOWED PATHS` block; registry
  `data/security_surfaces.json`.
- **Escapes:** terminal-status briefs skipped (`is_terminal_brief_status`, `:154-157`);
  `data/sensitivity_floor_grandfather.json` demotes a floor violation to info (`:34`);
  runtime discharge via `gz obpi complete --accept-security-floor`.
- **MX interaction — the rule's clause 3 is half right.** `sensitivity` is indeed absent
  from `GATE5_INVARIANTS` (`mx/invariants.py:23-31`), so the registry/umbrella path
  (`_sensitivity_umbrella_runner`, `validate_cmd.py:543`) would resolve ADVISORY. **But
  that path is unreachable from the CLI**: `--sensitivity` short-circuits into
  `_run_sensitivity_scope` (`validate_cmd.py:1341-1342`), which never consults
  `checkpoint`/`disposition` and raises `SystemExit(3)` on any breach-set type
  (`:915-916`). The flag an operator actually runs stays **fail-closed inside the hangar**.
- **Exit:** **3**, MX-immune.

### A16. `--commit-trailers` → `_validate_commit_trailers` **+** `_validate_eval_feedback_trailer`
`src/gzkit/commands/validate_commit_trailers.py:52` and `:109` · `explicit` · not in `gz check`

- **Arm A:** `git log -1 --pretty=%B HEAD` + `git show --name-only --pretty= HEAD` (`:23-49`).
  If no changed path starts with `_CODE_PATH_PREFIXES = ("src/","tests/")` (`:20`) → `[]`.
  Else `has_task_trailer(message)` (`src/gzkit/tasks.py:327-347`) matching **only**
  `_ANY_TASK_TRAILER_RE` (`tasks.py:220-222`):
  `r"^Task:\s+TASK-(?:\d+\.\d+\.\d+-\d+-\d+-\d+|[a-z][a-z0-9-]*(?:-#\d+)?)\s*$"`.
  `Ceremony:` and `Eval-feedback-source:` do **not** substitute — `parse_ceremony_trailers`
  (`tasks.py:350`) is never consulted here. **This matches `tests.md:87` exactly.**
- **HEAD only.** No range; historical commits are never inspected.
- **Arm B** (`:109`): scope `_RULE_PATH_PREFIXES = (".gzkit/rules/","AGENTS.md")` (`:104`);
  requires `(?:closes|fixes)\s+#(\d+)` in the message; then shells
  `gh issue view <n> --json labels` (`:123-131`) and fires only on an `eval-feedback`
  label. **Any `gh` failure — offline, unauthenticated, rate-limited — returns nonzero
  and the arm silently emits nothing.** Fails open, network-dependent.
- **Exit:** `type="commit_trailers"` (`:89`, `:156`) **not** in breach set → **exit 1**.

### A17. `--task-envelope-coherence` → `_validate_task_envelope_coherence`
`src/gzkit/commands/validate_task_envelope.py:949-968` · `explicit` · **in `gz check`**

Four signatures, summed.

**(a) `_sig_a_attribution_drift` (`:362-425`)** — scans `.gzkit/ledger.jsonl`; fires when
`any_active and not task_id` (`:412`). The checked set is `_TASK_WORKLOG_TYPES` (`:27-38`):

```python
{"artifact_edited", "attested", "gate_checked", "audit_receipt_emitted",
 "artifact_renamed", "obpi_completion_uncovered_accept",
 "intrinsic-complexity-attestation", "composition_rendered"}
```

Escapes, all live: epoch cutoff `_TASK_ENVELOPE_ENFORCEMENT_EPOCH = 2026-05-30T14:44:00+00:00` (`:44`);
`audit_receipt_emitted` with `receipt_event == "meta-receipt-bind"` (`:303`);
`composition_rendered` blanket-excused (`:314`); OBPI-brief reflection (`:165-186`);
ADR-decision-doc reflection via `_ADR_DECISION_DOC_RE` (`:193`); manpage reflection (`:222-242`);
REQ-attributed uncovered-accept (`:245-263`);
`_POOL_DEMOTION_ATTRIBUTION_CUTOVER = 2026-07-30T09:00:00+00:00` (`:343-359`).

**(b) `_sig_b_subdivision_skipped` (`:521-546`, predicate `:496-518`)** — the
"default-bucket-only OBPI without a `req_atomic` exemption" fail-close **does exist**,
but fires only for OBPIs already carrying an `obpi_receipt_emitted` with
`receipt_event == "completed"` (`:475-476`). The exemption is a bare `req_atomic:` list
in frontmatter (`:542`) — **no rationale is parsed or required**.

**(c) `_sig_c_layer_drift` (`:813-879`)** — four channels (`advances`, `frontmatter`,
`commit_trailer`, `ledger`) bucketed by `_OBPI_LINEAGE_RE` (`:68`); skipped unless
`len(non_empty) >= 2` (`:857`). Grandfather
`_SIG_C_DRIFT_GRANDFATHER = {"OBPI-0.0.41-03","OBPI-0.0.63-01"}` (`:91`).
The commit-trailer channel runs `git log --all` with `timeout=30` and **returns `{}` on
any nonzero/timeout** (`:750-763`) — fails open. `_advances_channel_map` swallows all
exceptions → `{}` (`:719-720`). **There is no Heavy-fails / Lite-warns branch anywhere in
this signature** — the lane is never read.

**(d) `_sig_d_obpi_id_divergence` (`:882-946`)** — one `task_id` carrying >1 `obpi_id`
across `_TASK_LIFECYCLE_TYPES` (`:94`). Grandfather `_OBPI_ID_DIVERGENCE_GRANDFATHER` (`:77-79`)
plus `_OBPI_ID_CANONICAL_CUTOVER = 2026-07-29T09:45:00+00:00` (`:67`).

- **Exit:** `type="task_envelope_coherence"` in breach set (`validate_cmd.py:1119`) → **3**.

### A18. `--lock-handoff-coupling` → `validate_lock_handoff_coupling`
`src/gzkit/governance/trust_audits/lock_handoff_coupling.py:30` · `explicit` · **in `gz check`**

- **Scope:** `.gzkit/ledger.jsonl`, `event == "obpi_lock_released"` (`:46`) with
  `ev_ts >= cutover_ts` (`:49`).
- **Cutover is derived, not constant** (`_find_cutover_ts`, `:102-113`): the latest
  `obpi_receipt_emitted` whose `id` starts with
  `_CUTOVER_ID_PREFIXES = ("OBPI-0.0.41-02-","OBPI-0.0.41-03-")` (`:25`).
  **If neither receipt exists, `cutover_ts is None` and the validator returns `[]`
  (`:41-42`)** — a silent whole-scope no-op in any repo that is not gzkit.
- **The "four fields" as the code has them:** `_MIN_INFO_FRONTMATTER_FIELDS` (`:27`) is a
  **three**-tuple — `"last_lock_event_timestamp"`, `"last_commit_sha"`, `"branch"` — and the
  fourth requirement is a body-section regex,
  `_DECISIONS_RE = re.compile(r"^##\s+Decisions\s+Made", re.MULTILINE | re.IGNORECASE)` (`:26`).
  `_check_min_info` (`:178-212`) emits **one error per missing field**.
  This is exactly what `token-block-discipline.md` v0.3.0 § Sub-Invariant 2 now says.
- Other predicates on the same event: missing `handoff_path` in `ev.extra` (`:53-66`);
  path not on disk (`:68-80`); unreadable (`:81-94`); `_check_timestamp` (`:147-175`).
  `_check_timestamp` **fails open**: returns `[]` when the handoff has no `timestamp`
  or it will not parse (`:157-162`).
- **Exit:** `type="lock_handoff_coupling"` in breach set (`validate_cmd.py:1121`) → **3**. Matches prose.

### A19. `--brief-headings` → `audit_brief_headings`
`src/gzkit/governance/trust_audits/briefs.py:104` · `explicit` · not in `gz check`

- Predicate (`_canonical_h3_heading`, `:69-74`): a line starting `"## "` whose text,
  `.split("(")[0].strip().casefold()`, folds into
  `_BRIEF_EVIDENCE_H3_HEADINGS` (`:58-66`) =
  `("Implementation Summary", "Key Proof", "Closing Argument", "Step 4b — Independent Adversarial Validation")`.
  It detects **H2 drift of four named headings only**. A brief that omits all four
  passes clean; H4+ drift is invisible.
- **Scope:** `docs/design/adr/**` `rglob("OBPI-*.md")` (`:159`); missing dir → `[]`.
  `UnicodeDecodeError` → file silently skipped (`:81-83`). No waivers.
- **Exit:** `type="brief_headings"` **not** in breach set → **exit 1**
  (the rule at `brief-heading-conventions.md:48` says "Exits 3 on drift").

### A20. `--changelog` → `validate_changelog`
`src/gzkit/validate_pkg/changelog.py:40` · `explicit` · not in `gz check` (documented as deliberate)

- Scope: exactly `CHANGELOG.md` at project root; missing → 1 error (`:43-50`).
- Three line-wise predicates: `_VERSION_RE = r"^## (?:\[Unreleased\]|v?\d+\.\d+\.\d+ \(\d{4}-\d{2}-\d{2}\))$"` (`:36`);
  `### ` text in `_ALLOWED_CATEGORIES` (`:20-30`); any top-level bullet under an
  allowed non-exempt category matching `_GHI_RE = r"GHI #\d+"` (`:37`).
- Exemption `_CITATION_EXEMPT = frozenset({"Release highlights"})` (`:34`). A bullet under
  a **disallowed** heading gets the category error but its citation is never checked;
  indented bullets are never checked. Closed-GHI *coverage* is explicitly out of scope
  (docstring `:9-12`) — it lives in `gz-patch-release`, exactly as the rule says.
- **Exit:** `type="changelog"` **not** in breach set → **exit 1**
  (the rule at `changelog-release-notes.md:48` says "fails closed").

### A21. `--deprecated-verb-prescription` → `audit_deprecated_verb_prescription`
`src/gzkit/governance/trust_audits/deprecated_verb_prescription.py:116` · `explicit` · not in `gz check`

- **Deprecated-verb source:** `DEPRECATED_VERBS` in
  `src/gzkit/governance/deprecations.py:40-42` — a hand-maintained Pydantic tuple with
  **one** entry today: `DeprecatedVerb(verb="gates", successor="gz closeout", ghi="#705")`.
  Not derived from the parser or from runtime deprecation notices.
- Predicate: per line, per entry, `_pattern()` = `re.compile(rf"\bgz\s+{re.escape(entry.verb)}\b")` (`:62-68`).
- **`_SURFACE_GLOBS` (`:47-52`) and `_SURFACE_FILES` (`:54-59`) are markdown-only:**
  `.gzkit/rules/**/*.md`, `.gzkit/skills/**/SKILL.md`, `src/gzkit/rules/**/*.md`,
  `src/gzkit/skills/**/SKILL.md`, plus `docs/user/runbook.md`,
  `docs/governance/governance_runbook.md`, `AGENTS.md`, `CLAUDE.md`.
  **No `.py` surface is in scope**, so a deprecated verb prescribed from Python code is
  invisible to this audit. Live instance:
  `src/gzkit/handoff_resume_gate.py:102` grants the tuple `("gz","gates")` and `:360`
  prescribes it, while the declared successor `gz closeout` is absent from that
  allowlist. Also deliberately excluded: `.claude/`, `.agents/`, `.github/` mirrors,
  `RELEASE_NOTES.md`, and all of `docs/design/`.
- **Escape marker:** `_ESCAPE_MARKER = "deprecated-verb-ok"` (`:45`), a **bare substring
  test** on the line (`:92`) — no reason is parsed or required, despite the error prose
  suggesting `deprecated-verb-ok: <reason>`.
- **Exit:** in breach set (`validate_cmd.py:1123`) → **3**. Matches prose.

### A22. `--complexity-doctrine-links` → `validate_complexity_doctrine_links`
`src/gzkit/governance/trust_audits/complexity_doctrine_links.py:188` · `explicit` · **in `gz check`**

- **Scope** (`_enumerate_in_scope_artifacts`, `:52-76`): `docs/design/adr/foundation/<dir>/**/*.md`
  where the dir starts with `_CLUSTER_ADR_PREFIXES = ("ADR-0.0.27-","ADR-0.0.28-","ADR-0.0.29-","ADR-0.0.30-")` (`:44-49`);
  plus `.gzkit/rules/complexity-doctrine.md`; plus **non-recursive**
  `docs/governance/complexity/*.md` excluding `distilled-characteristics-*`.
- **Candidate selection is a two-signal heuristic, not a parse** (`:98`): a line counts as
  a citation only if it matches `_DOC_PATH_PATTERN` **AND** contains a section marker
  **AND** contains `"(corpus revision"`. A bare `docs/governance/complexity/x.md`
  reference with no section marker is never link-checked — "link integrity" does not
  cover plain paths.
- Four `continue`-gated predicates (`:196-242`): `parse_citation` succeeds;
  `distilled_characteristics_path` is a file; `_resolve_section_anchor` matches a
  slugified H1–H3 (`_HEADING_PATTERN`, `:40`); `is_portable(citation, current_revision)`.
- Revision source: the filename-descending-newest `distilled-characteristics-*.md`
  frontmatter `corpus_revision` (`:144-167`). **If none exists, check 4 is skipped
  entirely** (`:231`).
- Escape marker: `_SPECULATIVE_MARKER = "<!-- gz-validate-skip: complexity-doctrine-links -->"` (`:38`)
  on the immediately preceding line (`:100-101`).
- **Nothing in this audit reads the seven selection criteria or seven disqualifiers of
  `complexity-doctrine.md`.**
- **Exit:** in breach set (`validate_cmd.py:1085`) → **3**.

### A23. `--complexity-thresholds` → `validate_complexity_thresholds`
`src/gzkit/governance/trust_audits/complexity_thresholds.py:45` · `explicit` · **in `gz check`**

- **Exactly three assertions:** (1) `.gzkit/rules/complexity-thresholds.json` exists (`:54-56`);
  (2) `load_threshold_table` parses it without `PydanticValidationError`/`ValueError` (`:59-63`);
  (3) `_check_canonical_metric_coverage` (`:104-118`) —
  `set(CANONICAL_METRICS) - {band.metric for band in table.bands}` is empty.
- **It never validates band values, ordering, polarity, provenance, or any citation.**
  "At least one band per canonical metric" is the whole coverage bar. There is no
  amendment-protocol arm of any kind.
- Advisory side-channel: if `.gzkit/rules/complexity-thresholds.md` contains
  `_BOOTSTRAP_HEADING_PATTERN = r"^##\s+Bootstrap\s+absolutes"` (`:39-42`),
  `_emit_bootstrap_mode_notice` prints to **stdout** (`:126-136`) and returns nothing,
  announcing that portability checks against bootstrap rows are skipped.
- **Exit:** all three type constants alias `"complexity_thresholds"` (`:36-38`), in breach
  set (`validate_cmd.py:1086`) → **3**.

### A24. `--pointer-anchors` → `validate_pointer_integrity`
`src/gzkit/governance/trust_audits/pointer_integrity.py:33` · `explicit` · not in `gz check`, **but in `.pre-commit-config.yaml:65`**

- **Scope** (`_iter_surface_files`, `:41-56`): `_SURFACE_FILES = ("AGENTS.md","CLAUDE.md")` (`:28`)
  plus `.claude/rules/**/*.md` — **the vendor mirror, not canonical `.gzkit/rules/`.**
- Line filter `_is_blockquote_see` (`:81-86`): lstripped line starts `">"` and contains
  `" See "` (or starts `"> See "`). Inline links are out of scope by design.
- Three predicates per `_LINK_RE = r"\(([^()\s]+#[^()\s]+)\)"` (`:30`) match:
  destination `is_file()` (`:98`); anchor in `_heading_slugs(dest_content)` where
  `_slugify` (`:141-154`) is the mkdocs `toc` slugifier; and
  `"<!-- lifted-from:" in dest_content` (`:128`) — **substring only**. The docstring
  claims the back-pointer must be `<!-- lifted-from: <source-path>#<anchor> -->`, but the
  path and anchor inside it are never checked: one `lifted-from` comment anywhere in the
  destination satisfies every pointer aimed at that file.
- **Exit:** in breach set (`validate_cmd.py:1101`) → **3**.

### A25. `--distribution` → `audit_distribution`
`src/gzkit/governance/trust_audits/distribution.py:82` · `explicit` · not in `gz check`

- Inputs: `pyproject.toml` `[tool.hatch.build.targets.wheel].include` globs and
  `data/distribution_baseline_manifest.json` (`_load_inputs`, `:99-141`).
- Three set-difference predicates (`_collect_errors`, `:175-229`): `ON_DISK_NOT_INCLUDED`,
  `BASELINE_NOT_ON_DISK`, `ON_DISK_NOT_BASELINE`.
- Exemptions: `_EXCLUDED_SEGMENTS` plus **any path segment starting with `__`** (`:28-30`, `:161-162`);
  `_is_package_only` (`:66-79`) — per-surface classifier verdicts `"package_only"` /
  `"runtime_state"` suppress classes 1 and 3 (never class 2). An unrecognized surface has
  no classifier and nothing is exempt. **This is exactly the carve-out
  `skill-surface-sync.md` § Retirement policy describes, and the rule's claim is accurate.**
- **Distinct disposition:** IO/parse failure **raises `SystemExit(2)` from inside the
  validator** (`:107-132`), bypassing `_print_validation_result` — the only scope in this
  set that can terminate the run with 2.
- **Exit:** in breach set (`validate_cmd.py:1098`) → **3** for drift.

### A26. `--invariant-coherence` → `validate_invariant_coherence`
`src/gzkit/governance/trust_audits/invariant_coherence.py:44` · tier **`default`** · **in `gz check`**

- **Predicate is a single byte-equality:** `render_agents_md(root) == (root/"AGENTS.md").read_bytes()` (`:67-73`).
  Despite the scope name it is **AGENTS.md rendition-playback drift**, not an
  invariant-registry check — nothing here reads `.gzkit/invariants/*.json`.
- Bootstrap escape: `if not rendered_bytes: return []` (`:68-69`).
- **Side effect on failure:** emits a `composition_drift_detected` ledger event (`:76-80`).
  Clean runs are read-only by explicit design (`:52-57`).
- **Exit:** in breach set (`validate_cmd.py:1108`) → **3**. Matches the AGENTS.md claim.

### A27. `--brief-reconcile` → `validate_brief_reconcile`
`src/gzkit/governance/trust_audits/brief_reconcile.py:56` · `explicit` · not in `gz check`

- **Scope** (`_find_obpi_briefs`, `:29-37`): `docs/design/adr/**/obpis/OBPI-*.md` and
  `**/briefs/OBPI-*.md` — **only those two subdirectory names** (contrast the flat
  `rglob("OBPI-*.md")` used by A14 and A28).
- **The load-bearing exemption:** `if not _is_structured_brief(brief_path): continue` (`:68-69`).
  `_is_structured_brief` (`:40-53`) returns `isinstance(parse_brief(path), BriefStructure)`
  and **swallows every exception → `False`**. Legacy (`LegacyBriefShape`) briefs and any
  brief that raises during parse are walked past **without a single assertion** — a de
  facto grandfather over the entire unmigrated corpus (the docstring calls it the
  "CIC-2 permissive-mode boundary", `:6-16`).
- Six drift dimensions on structured briefs (`:86-152`): `allowlist_delta.missing_on_disk`,
  `allowlist_delta.missing_in_brief`, `discovery_delta.unresolved_paths`,
  `verification_delta.unresolved_verbs`, `req_count_delta` (only when `.measurable and .delta != 0`),
  `citation_delta.stale_citations`.
- **Exit:** in breach set (`validate_cmd.py:1109`) → **3**.

### A28. `--req-kind-discipline` → `_validate_req_kind_discipline`
`src/gzkit/commands/validate_req_kind.py:232` · `explicit` · **in `gz check`**

- Scope: `validate_briefs._find_obpi_briefs` → flat `docs/design/adr/**` `rglob("OBPI-*.md")`.
- **Grandfather:** if `_REQ_KIND_TAG_RE` finds **zero** tagged REQs in `## Acceptance
  Criteria`, the brief passes wholesale (`:198-201`) — all-untagged = legacy = clean; only
  *mixed* state is flagged. `if not ac_section: return []` (`:195-196`).
- Tag regex (`:21-24`):
  `r"-\s+\[[ xX]\]\s+\*{0,2}(REQ-[\d.]+[-\d]+)\s+\[(BEHAVIOR|SUPPORT|STRUCTURAL-FENCE)\]:"`, `re.IGNORECASE`.
- Per-kind predicates, each weaker than the doctrine prose:
  - **BEHAVIOR** (`:64-73`): `"tests/" in allowed_section` — a bare substring test over the
    whole `## Allowed Paths` section. One `tests/` path anywhere satisfies **every**
    BEHAVIOR REQ in the brief. It does not check that a `@covers` test exists.
  - **SUPPORT** (`:76-99`): `parse_support_citation(req_line) is not None`, else a legacy
    fallback passing on `"gz validate --" in req_line` **AND** any of
    `_LEDGER_EVENT_KEYWORDS = {"artifact_edited","obpi_created","obpi_completed","adr_created","ledger","event"}` (`:31-33`)
    — the bare word `"event"` in prose satisfies it.
  - **STRUCTURAL-FENCE** (`:102-142`): parent ADR from `parent:` frontmatter (`:47-57`);
    requires a `## Boundary Invariants` section; then **`if _is_enforcement_asserting(req_text)`
    → unconditional pass** (`:129-130`); otherwise `_fence_obpi_anchored(section, req_id)`.
- **Exit:** in breach set (`validate_cmd.py:1112`) → **3**.

### A29. `--advisor-proof-binding` → `validate_advisor_proof_binding`
`src/gzkit/governance/trust_audits/advisor_proof_binding.py:30` · `explicit` · not in `gz check`

- Three arms: (1) **fixtures** — every `tests/fixtures/advisor/*.json`,
  `_has_non_empty_proof` = `isinstance(payload["proof"], list) and len(...) > 0` (`:163-165`);
  (2) **ledger** — `intrinsic-complexity-attestation` events resolved against the
  **fixture index only** (`:89-91`), `if diag is None: continue`, so an event citing a
  non-fixture diagnosis is never validated; (3) **schema** —
  `src/gzkit/schemas/advisor_diagnosis.json` must have `properties.proof.minItems` an
  `int >= 1` (present today at `:39`), but **missing file → `[]` (`:109-110`)**.
- **It never inspects the Pydantic model.** `AdvisorDiagnosis`
  (`src/gzkit/complexity/advisor/diagnosis.py:129`) does carry the constraint the
  AGENTS.md bullet names — its docstring at `:136-139` describes `Field(min_length=1)`
  plus a `_check_proof_nonempty` belt-and-braces validator — but no line of this audit
  reads it.
- Escape: `_NEGATIVE_CASE_KEY = "_negative_case"` (`:27`) skips a fixture (`:49-50`).
- **Exit:** `type="advisor_proof_binding"` **not** in breach set → **exit 1**, despite the
  module docstring calling itself a "Fail-closed audit".

### A30. `--rule-version-markers` → `audit_rule_version_markers_errors`
`src/gzkit/validators/rule_version_markers.py:123` · tier **`default`** · **NOT in `gz check`**

- **Scope** (`canonical_rule_files`, `:69-73`): **non-recursive** `.gzkit/rules/*.md`
  minus `_EXEMPT_FILENAMES = frozenset({"AGENTS.md"})` (`:39`). Vendor mirrors not scanned.
- Two predicates (`audit_rule_version_markers`, `:76-106`), verbatim:
  - `_MARKER_RE = re.compile(r"<!--\s*rule-version:\s*(\d+\.\d+\.\d+)\s*-->")` (`:41`) — absent → `missing-marker`
  - `_BLOCKQUOTE_RE` (`:42`) matching a `> **Rule version:** \`X.Y.Z\`` blockquote —
    absent, or version `!=` marker version → `marker-blockquote-drift`

  Early-`continue`d, so one violation per file. Only exemption is `AGENTS.md`.
- **Live failure right now.** `.gzkit/rules/mx-mode.md:12` carries
  `<!-- rule-version: 1.0.1 -->` while `:16` carries
  `> **Rule version:** \`1.0.0\` — initial authoring under ADR-0.0.74 (OBPI-0.0.74-08)`.
  That is `marker-blockquote-drift` by the regexes above — a check that exists, is
  failing, and is out of default scope.
- **Sharpest exit mismatch in the set.** `run_rule_version_markers` (`:109-120`) builds
  `RuleVersionMarkersResult(..., exit_code=3 if violations else 0)` — but that function
  has **no caller anywhere in `src/`**. The live registry path is
  `audit_rule_version_markers_errors`, which stamps **`type="surface"`** (`:135`), not
  `"rule_version_markers"`. `"surface"` is not in the breach set → **exit 1**. The
  declared exit-3 disposition lives only on a dead code path.
- **And it never runs in `gz check`:** it is default-tier, and no `gz check` step
  invokes a bare `gz validate`.

---

## B. Non-`gz validate` enforcers named by rule prose

### B1. `gz cli audit` → `cli_audit_cmd`
`src/gzkit/commands/cli_audit.py:172-243` · **in `gz check`** (`quality.py:447`; `run_cli_audit` at `src/gzkit/quality.py:617-624`)

Asserts:

1. `docs/user/manpages/index.md` exists (`:176-180`).
2. Per `manifest.commands` entry with `entry.surfaces.manpage` truthy (`:186-188` —
   `manpage: false` entries are skipped entirely): manpage file exists (`:192-195`); its
   content `lstrip()`-starts with `f"# gz {command_name}"` (`:198-200`); its basename
   appears as a **substring** of the index content (`:203-204`) — a link target is never
   validated.
3. README `## Quick Start` fenced block: every `gz …` / `uv run gz …` line must
   `parser.parse_args()` without `SystemExit` (`_collect_readme_quickstart_issues`, `:67-104`).
4. AST cross-coverage via `check_surfaces_report` (`:106-147`); `FileNotFoundError` →
   **empty report with `passed=True`** (`:114-122`), i.e. fails open.
5. **Flag presence AND flag truth** (`:220-233`): `check_flag_doc_coverage` and
   `check_flag_doc_truth` over `scan_command_flag_specs` — the GHI #693 usage-line
   agreement arm. **`cli.md` § Consistency is substantively accurate about this.**

- **Exit:** `if issues: raise SystemExit(1)` (`:242-243`). There is **no exit-3 path in
  the module** — see parity-diff row M15.

### B2. `gz smoke` → `smoke_gate`
`src/gzkit/commands/smoke_cmd.py:21-83`; wrapper `:86-95` · **in `gz check`** (`quality.py:481`)

- Budget: `SMOKE_BUDGET_SECONDS = 60.0` (`src/gzkit/smoke.py:40`), defaulted at
  `smoke_cmd.py:35`; overridable per run by `--budget` (`parser_maintenance.py:329-334`, `default=None`).
- Breach → `_EXIT_POLICY_BREACH = 3` (`:18`, `:71-80`); strict `>`, so exactly 60.00s passes.
- **Empty tier → 3 only when opted in** (`:37-57`):
  `if not GzkitConfig.load(root / ".gzkit.json").smoke.required: return _EXIT_OK`.
  `SmokeConfig.required` defaults to **`False`** (`src/gzkit/config.py:163-164`).
  gzkit itself opts in — `.gzkit.json:16-18` has `"smoke": {"required": true}` — so the
  claim holds *here* and is false as a statement about the verb.
- Third outcome the rule omits: an actual test failure returns `_EXIT_TEST_FAILURE = 1` (`:63-69`).
- Tier membership is a static regex scan, not an import:
  `_SMOKE_DECORATOR_RE = re.compile(r"^\s*@smoke\b", re.MULTILINE)` (`smoke.py:48`) over
  `tests/**/*.py` excluding `NON_PACKAGE_DIRS` (`:46`) — a `@smoke` inside a comment or
  string literal counts as a populated tier.

### B3. `CANONICAL_STEP_COMMANDS` + `gz arb validate`
`src/gzkit/arb/validator.py:53-72`; provenance check `:200-214`

```python
CANONICAL_STEP_COMMANDS: dict[str, list[str]] = {
    "typecheck": ["uv", "run", "ty", "check", "src"],
    "unittest":  ["uv", "run", "-m", "unittest", "-q"],
    "coverage":  ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-t", "."],
    "mkdocs":    ["uv", "run", "mkdocs", "build", "--strict"],
    "security":  [],            # reserved, ADR-0.0.22 OBPI-05
    "meta-receipt-bind": [],    # reserved, ADR-0.0.24 OBPI-02
}
```

`_canonical_provenance_error` (`:200`) returns `None` unless the receipt has a `step`
dict whose `name` is a key of that mapping. **There is no `"ruff"` key.** Ruff receipts
take the lint-receipt path (`LINT_SCHEMA_ID`, `:78`) and carry no `step.name`, so the
provenance lock does not reach them. The lock covers 4 of the 5 rows in the AGENTS.md
§ Attestation table; row 1 (`uv run gz arb ruff` / `arb-ruff-`) is unlocked.
`gz arb validate` surfaces the count as `non_canonical_provenance` (`render_validation_text`, `:226-227`).

### B4. `_requires_human_obpi_attestation`
`src/gzkit/commands/adr_audit.py:462-475`

```python
def _requires_human_obpi_attestation(parent_adr, parent_lane, brief_frontmatter=None) -> bool:
    ...
    return True
```

Unconditional; the docstring states the foundation/lane/security branching was collapsed
per ADR-0.0.36 / OBPI-0.0.36-02 and the three parameters "are accepted but not evaluated."
**AGENTS.md § OBPI Acceptance Protocol and `governance-core.md` § Non-negotiable rules are
exactly right about this.** Recorded as a parity match.

### B5. `forbid-pytest`, `xenon`
`.pre-commit-config.yaml:40-45` (`entry: uv run -m gzkit.hooks.guards`, `stages: [pre-commit]`)
and `:47-49` (`entry: uv run xenon --max-absolute C --max-modules C --max-average C src/`).
Both exist as claimed. `pythonic.md:52` already names the xenon / threshold-table
three-ceiling conflict itself and is scored as self-disclosed.

### B6. `validate_invariant_witnesses` — **defined, registered nowhere**
`src/gzkit/governance/trust_audits/invariant_witness.py:78`

Whole-repo search for the symbol and the module name returns: the definition;
`tests/governance/test_invariant_witness.py` (its only caller); and prose mentions in
`docs/governance/build-to-1.0-campaign-2026-07-18.md` and
`docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-01-invariant-schema-and-registry.md`,
plus chore logs and handoffs.

It is **not** re-exported from `trust_audits/__init__.py`, appears in **no** `_ScopeEntry`
in `VALIDATOR_REGISTRY`, and there is **no `--invariant-witness` flag** in the 96-flag
`gz validate --help` surface. Its `type="invariant_witness"` string is likewise absent
from `_POLICY_BREACH_ERROR_TYPES`.

The function itself is correct: `_resolves` (`:50-61`) resolves `gz validate --<scope>`
against `VALIDATOR_REGISTRY` stems and `gz <verb> [<subverb>…]` against registered parser
leaf paths, stripping a trailing parenthetical (`:27-33`).
`tests/governance/test_invariant_witness.py:102-130` pins the committed registry to a
`_KNOWN_UNRESOLVED = frozenset({"foundation-adr-registers-invariant"})` shrink-only fence
whose docstring states the disposition is "operator canon work, not an agent call."

**Net:** the meta-check that would catch a phantom structural witness runs only under
`unittest`. It is unreachable from the CLI entirely — not merely absent from `gz check`.

### B7. `src/gzkit/schemas/authoring_guide_protocol.json` — **no runtime consumer**
The file exists (3951 bytes, `$id: https://gzkit.tvproductions.dev/schemas/authoring_guide_protocol.json`).
A repo-wide search for the string `authoring_guide_protocol` outside `.gzkit/chores/`
returns only: `AGENTS.md`, the schema file itself, and documentation/ADR artifacts
(`docs/governance/advisory-rules-audit.md`, `docs/governance/agent-contract-rationale.md`,
`docs/governance/complexity/authoring-guide-protocol.md`, and the ADR-0.0.30 package).
**No `.py` file references it.** The only generic loader, `load_schema(name)`
(`src/gzkit/schemas/__init__.py:30`), is by-name and is never called with
`"authoring_guide_protocol"`.

### B8. `.gzkit/invariants/foundation-adr-registers-invariant.json` — **phantom witness, still live**

```json
{
  "id": "foundation-adr-registers-invariant",
  "claim": "Every foundation-kind ADR registers at least one invariant in .gzkit/invariants/.",
  "structural_witness": ["gz validate --foundation-registers-invariant"],
  "composition_targets": []
}
```

`--foundation-registers-invariant` is absent from the 96-flag help surface and from
`VALIDATOR_REGISTRY`. The other three registry entries (`CIC-1.json`, `CIC-2.json`,
`skill-first-execution-invariant.json`) resolve. Confirmed live 2026-08-01.
