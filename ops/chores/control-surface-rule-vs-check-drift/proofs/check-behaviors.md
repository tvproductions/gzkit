# Check Behaviors — control-surface-rule-vs-check-drift (Pass C)

For each promoted scope flag, the concrete assertions the validator
implementation enforces. Derived by reading:

- `src/gzkit/commands/validate_cmd.py` (flag dispatch)
- `src/gzkit/commands/validate_frontmatter.py` (frontmatter scope)
- `src/gzkit/governance/trust_audits.py` (all other promoted scopes)

Dispatch table: `_explicit_scope_runners` at
`src/gzkit/commands/validate_cmd.py:369-395`.

Read-only tracing. No source was modified.

---

## `--pool-adr-isolation`

Implementation: `src/gzkit/governance/trust_audits.py:717-771` (`audit_pool_adr_isolation`)

Assertions:

1. Reads every line of `.gzkit/ledger.jsonl` as JSON.
2. Skips invalid JSON lines silently (`json.JSONDecodeError`).
3. Forbidden events: `gate_checked`, `attestation`, `obpi_completed`,
   `adr_attested`, `adr_audit`, `adr_closeout`, `lifecycle_transition`
   (line 731-739).
4. Pool ADR identification: event's `id` or `adr_id` field starts with
   literal `"ADR-pool."` (line 751).
5. Emits one error per `(artifact_id, event_type)` pair (dedup via
   `seen` set at line 741).
6. **Does NOT check the filesystem path `docs/design/adr/pool/`** — only
   the id prefix. An ADR living under `docs/design/adr/pool/` without the
   `ADR-pool.` id prefix is invisible to this audit.
7. **Does NOT flag Gate 1 events** specifically — the forbidden list is
   about lifecycle/attestation/closeout events, not Gate 1 (which fires as
   `gate_checked` for gate=1 and is caught generically).

---

## `--reconcile-freshness`

Implementation: `src/gzkit/governance/trust_audits.py:965-1045` (`audit_reconcile_freshness`)

Assertions:

1. Reads every line of `.gzkit/ledger.jsonl` as JSON.
2. Recognized reconcile events: `frontmatter_reconciled`, `reconcile_run`,
   `reconcile_completed`, `state_reconciled`, `obpi_reconciled`
   (line 982-988).
3. Compares the max `ts` over these events against HEAD's
   `git log -1 --format=%cI HEAD` commit timestamp.
4. Grace window: 24 hours (86400 seconds at line 1032).
5. Fails if `(head_ts - latest_reconcile) > 86400s`.
6. **Returns empty-list (passes) when the ledger has no reconcile events at
   all** (line 1024-1028: "Ledger has no reconcile events yet — the
   reconciliation pathway is still being mechanized. Skip rather than fail").
7. Returns empty-list on git error (line 1017-1018, 1021-1022).

---

## `--frontmatter`

Implementation: `src/gzkit/commands/validate_frontmatter.py:1-120`
(`validate_frontmatter_coherence` + helpers)

Assertions (extracted by scanning the four governed fields in
`_check_one_artifact` and siblings):

1. Compares four frontmatter fields against ledger: `id`, `parent`, `lane`,
   `status` (module docstring, line 1-9).
2. `id` canonicalization via status_vocab; mismatch flagged with
   `_field_error` (line 118-120).
3. `status` uses `_status_matches` supersetting: `attested_completed` is
   accepted for frontmatter `completed` (line 26-45).
4. Lookup keyed on filesystem path, never on `fm.id:` (line 59-86; the
   "GHI #166" guard).
5. Falls back to `_ADR_ID_PATTERN` and `_OBPI_ID_PATTERN` prefix matches
   when stem does not appear in graph (line 77-85).
6. Exit code 3 emitted via `_print_validation_result` when only
   frontmatter errors exist (validate_cmd.py:522-523).
7. Recovery-command hints per field: `id`/`parent` → `gz register-adrs
   --all`; `lane` → `gz adr promote ... --lane ...`; `status` →
   `gz chores run frontmatter-ledger-coherence` (line 51-56).

---

## `--event-handlers`

Implementation: `src/gzkit/governance/trust_audits.py:215-290` (`audit_event_handlers`)

Assertions:

1. Reads `src/gzkit/ledger_events.py` (AST) and extracts every `event=` kwarg
   that is a string literal (`_collect_emitted_event_types`, line 253-265).
2. Reads `src/gzkit/ledger.py` (AST) and extracts every string compared
   against `event.event` plus every string literal in a set/list/tuple that
   matches the event-type heuristic (`_collect_claimed_event_types`,
   line 268-290).
3. Emitted − Claimed − `_NO_GRAPH_IMPACT.keys()` = unclaimed events; each
   emits an error.
4. Stale waivers: `_NO_GRAPH_IMPACT.keys()` − Emitted = defunct entries;
   each emits an error (line 239-249).
5. Returns empty-list if either source file is missing (line 219-220).

---

## `--validator-fields`

Implementation: `src/gzkit/governance/trust_audits.py:298-342` (`audit_validator_fields` + `_collect_info_get_fields` + `_collect_ledger_written_fields`)

Assertions:

1. Reads `src/gzkit/commands/validate_frontmatter.py` (AST), collects every
   `info.get("<field>")` call's first string arg (line 325-342).
2. Reads `src/gzkit/ledger.py` (text + AST), collects every `graph[...]["X"]`
   write, `entry["X"]` read/write, and every string-literal dict key inside
   `_artifact_creation_entry` function (line 349-363).
3. Read fields − Written fields − `_VALIDATOR_FIELD_WAIVERS.keys()` =
   defects.
4. Returns empty-list if either source file is missing (line 302-303).
5. **Does NOT emit stale-waiver errors** for `_VALIDATOR_FIELD_WAIVERS`
   (unlike `audit_event_handlers` which does).

---

## `--taxonomy`

Implementation: `src/gzkit/governance/trust_audits.py:1057-1183`
(`audit_adr_taxonomy` + `_parse_adr_frontmatter`)

Assertions:

1. Scans `docs/design/adr/**/ADR-*.md`, skipping files with `obpis`,
   `briefs`, or `audit` in the path parts (line 1072).
2. Parses a **flat** YAML frontmatter block via stdlib-only
   `_parse_adr_frontmatter` (line 1153-1183): string-keyed, string-valued;
   no nested structures; double-quote unwrap.
3. Pool ADR detection: `adr_id` starts with `"ADR-pool."` (line 1081,
   constant at 1054).
4. For pool ADRs: errors when `kind:` is present (line 1083-1094). **Does
   not check semver presence.**
5. For non-pool ADRs:
   a. Errors when `kind:` is None/missing (line 1097-1110).
   b. Errors when `kind:` not in `{"foundation", "feature"}` (line 1112-1123).
   c. Errors when `kind: foundation` AND semver not matching
      `^0\.0\.\d+$` (line 1125-1138).
   d. Errors when `kind: feature` AND semver matches `^0\.0\.\d+$`
      (line 1139-1149).
6. **Does NOT check id-prefix ↔ semver coherence for non-pool ADRs** — only
   kind ↔ semver. (An ADR filename not matching `ADR-<semver>-*` is
   invisible.)

---

## `--utf8-prefix`

Implementation: `src/gzkit/governance/trust_audits.py:371-413` (`audit_utf8_prefix`)

Assertions:

1. Scans under these roots (if present): `docs`, `.gzkit/skills`,
   `.claude/skills`, `features` (line 379).
2. File extensions: `.md`, `.feature`, `.txt` (line 388).
3. Regex pattern `_PYTHONUTF8_PREFIX` at line 96:
   `PYTHONUTF8=1\s+uv\s+run\s+(?:gz|-m\s+gzkit)`.
4. Skips the file `advisory-rules-audit.md` specifically (line 400-401)
   because it names the anti-pattern as prose.
5. **Does NOT check for `python -c` / `uv run python <script>` helpers
   missing UTF-8 stdin/stdout reconfigure** — the rule-text assertion 2–3
   about fresh-interpreter helpers is entirely unenforced.
6. **Does NOT check shell files (`.sh`), Makefiles, CI workflows
   (`.github/workflows/*.yml`) — scope is doc/skill text only.**
7. **Does NOT check `tools/**` source scripts** for the reconfigure block
   required by `cross-platform.md:98`.

---

## `--version-release`

Implementation: `src/gzkit/governance/trust_audits.py:648-709` (`audit_version_release` + `_read_pyproject_version`)

Assertions:

1. Reads `pyproject.toml` with a naive line-oriented regex
   (`version = "..."`, line 701-709). First match wins — any `version`
   key in `[project]` or elsewhere is used.
2. Computes expected tag as `f"v{version}"`.
3. Early-exits (passes) if `docs/releases/PATCH-v{version}.md` exists
   (GHI #217 exemption, line 670-672).
4. Runs `git tag --list v*` and checks the expected tag is in the output.
5. **Does NOT validate `__init__.py` version string** (rule assertion 2
   names `pyproject.toml`, `__init__.py`, and README badge together, but
   the check covers only `pyproject.toml`).
6. **Does NOT validate the README badge version**.
7. **Does NOT validate release-note notes presence, target-branch, or
   `--latest` flag** — only tag existence.
8. Returns empty-list on git error (line 682-683).

---

## `--cli-alignment`

Implementation: `src/gzkit/governance/trust_audits.py:151-207` (`audit_cli_alignment` + `_known_cli_verbs`)

Assertions:

1. Sources scanned: `features/**/*.feature`, `docs/user/runbook.md`,
   `docs/user/commands/**/*.md`, `docs/user/manpages/**/*.md`
   (line 153-165).
2. Three regex patterns at line 92-94:
   - `_BACKTICKED_INVOCATION`: `` `gz <verb>...` ``
   - `_QUOTED_INVOCATION`: `"gz <verb>..."`
   - `_STEP_DEF_FIXTURE`: `the gz command "<verb>"` (feature step-def form).
3. Known verbs derived from `_build_parser` by walking `argparse`
   `_SubParsersAction` choices (line 196-207 — uses the private attribute
   `_actions`).
4. Emits one error per unknown verb (not per occurrence — line 182-192).
5. `_DOC_PROSE_VERBS` is an empty frozenset as of this audit (line 65) —
   no waivers currently applied.
6. **Does NOT scan `.gzkit/skills/**/SKILL.md` or `.claude/skills/**`** —
   skill files can reference verbs that do not exist and pass this audit.

---

## `--class-size`

Implementation: `src/gzkit/governance/trust_audits.py:590-640` (`audit_class_size`)

Assertions:

1. Scans every `*.py` under `src/gzkit/**`.
2. Span = `end_lineno - lineno + 1` for each `ast.ClassDef` (line 610-611).
3. Limit = 300 lines (line 598).
4. Classes over the limit not in `_CLASS_SIZE_WAIVERS` emit an error
   (line 614-628).
5. Stale-waiver check: entries in `_CLASS_SIZE_WAIVERS` that no longer
   match any `file.py::ClassName` emit an error (line 629-639).
6. **Does NOT check the 50-line function limit** (scorecard assigns that
   to ruff/xenon/pre-commit separately — see rule 19).
7. **Does NOT check the 600-line module limit** (scorecard rule 20 is
   pre-commit only).
8. **Waiver format is `relative/posix/path.py::ClassName`** (line 494,
   612) — tests must use the `.as_posix()` form, not the Windows
   backslash form.

---

## `--type-ignores`

Implementation: `src/gzkit/governance/trust_audits.py:110-143` (`audit_type_ignores`)

Assertions:

1. Scans every `*.py` under `src/` (line 119-123).
2. Uses `tokenize.tokenize` to walk only real Python COMMENT tokens
   (line 125-131) — string literals that happen to contain
   `# type: ignore[` are ignored.
3. Regex `_FORBIDDEN_TYPE_IGNORE` at line 91:
   `#\s*type:\s*ignore\[`.
4. Any match emits a policy-breach error with file path + line number.
5. Silently skips files that fail `tokenize` (line 127-128).
6. **Does NOT enforce the positive form: `# ty: ignore[<ty-code>]`** — the
   check is purely a blacklist of the mypy-style bracketed form. A stub
   file with no suppressions and a file with `# ty: ignore[bogus-code]`
   are equally "pass" to this check.
7. **Does NOT validate ty-code specificity** — if a user writes
   `# ty: ignore[totally-made-up-code]`, the validator passes because
   `# ty:` is not the forbidden prefix.
8. **Scope is `src/**` only** — `tests/**` is not scanned, even though
   rule text mentions "under `src/**`" specifically. That matches the
   rule's stated scope. (The companion test
   `tests/governance/test_type_ignore_syntax.py` also scopes to `src/**`.)

---

## `--pydantic-models`

Implementation: `src/gzkit/governance/trust_audits.py:475-582`
(`audit_pydantic_models` + `_has_dataclass_decorator` + `_extends_basemodel`
+ `_has_model_config` + `_extant_class_keys`)

Assertions:

1. Scans every `*.py` under `src/gzkit/**`.
2. For each `ast.ClassDef`:
   a. If has `@dataclass` decorator (Name, Call(Name), or Attribute form)
      AND key not in `_DATACLASS_WAIVERS` → error (line 495-506).
   b. If extends `BaseModel` AND no `model_config = ...` assignment in
      class body → error (line 507-517).
3. `_has_model_config` accepts both `Assign` and `AnnAssign` to
   `model_config` (line 556-568).
4. `_extends_basemodel` checks `ast.Name("BaseModel")` and
   `ast.Attribute(..., "BaseModel")` forms (line 547-553).
5. Stale-waiver check for `_DATACLASS_WAIVERS` (line 518-528).
6. **Does NOT check `ConfigDict(frozen=True, extra="forbid")` content** —
   any assignment to `model_config` counts as satisfying the check,
   including `model_config = {}` or `model_config = ConfigDict()`
   (no args). Rule assertions 2 and 7 about `frozen=True` and
   `extra="forbid"` are entirely unenforced at the content level.
7. **Does NOT check for `Optional[...]` or `List[...]` usage** (rule
   assertion 6 is delegated to ruff UP006/UP007 per scorecard rule 27).

---

## `--skill-alignment`

Implementation: `src/gzkit/governance/trust_audits.py:862-919` (`audit_skill_alignment`)

Assertions:

1. Derives known CLI verbs via `_known_cli_verbs()` (top-level
   `_SubParsersAction.choices.keys()`, same function used by
   `--cli-alignment`).
2. Scans every `.gzkit/skills/**/SKILL.md` file (line 879).
3. For each verb, checks two regex forms (line 886-888):
   - `\bgz\s+<verb>\b` anywhere in the file (body prose or code block).
   - `gz_command:\s*<verb>\b` (frontmatter form).
4. Emits one error per verb that is not in `_NO_SKILL_VERBS` and has no
   skill reference (line 891-907).
5. Stale-waiver check for `_NO_SKILL_VERBS` (line 908-918).
6. Returns empty-list on `_known_cli_verbs` exception (line 874-876).
7. **Does NOT check Invariants 2 or 3** (runbook prescription matching,
   output-form alignment) — those remain advisory per scorecard rows 29
   and 30.
8. **Does NOT check multi-word verbs or subcommand paths** — `gz adr
   status` is caught by the `gz\s+adr\b` match on "adr", but the skill's
   coverage of the subcommand `adr status` specifically is not
   verified.

---

## `--commit-trailers`

Implementation: `src/gzkit/commands/validate_cmd.py:122-158` (`_validate_commit_trailers`)

Assertions:

1. Runs `git log -1 --pretty=%B HEAD` and
   `git show --name-only --pretty= HEAD` to read HEAD's message and files
   (line 100-119).
2. Scope filter: only commits whose changed files include at least one
   path starting with `src/` or `tests/` (line 134-136).
3. Accepts either trailer form via
   `parse_task_trailers`/`parse_ceremony_trailers` (line 137) — the parsers
   live in `gzkit.tasks`.
4. Emits one error per HEAD commit that fails (by definition at most 1
   per run — scope is HEAD only).
5. Short-SHA included in error artifact (line 139-146).
6. **Does NOT check trailer positional discipline (assertion 3: "Task:
   trailer must be the final line")** — the parse functions are
   position-tolerant.
7. **Does NOT retroactively scan historical commits** — docstring
   explicitly states "advisory and focused on preventing *new* trailer
   omissions" (line 126-128).
8. Returns empty-list if not a git checkout (line 117-118).

---

## `--test-tiers`

Implementation: `src/gzkit/governance/trust_audits.py:421-467` (`audit_test_tiers`)

Assertions:

1. Forbidden directories: `tests/integration/`, `tests/e2e/`,
   `tests/slow/`, `tests/bdd/` — each `path.exists()` check emits an
   error (line 430-445).
2. Forbidden flags: `--integration`, `--e2e`, `--slow`, `--bdd-only`
   (line 449). Scans every `parser*.py` under `src/gzkit/cli/**`.
3. Uses naive `flag in text` substring search (line 456). Flag names
   appearing in a comment or docstring trigger the error.
4. **Does NOT check `gz test` subcommand help text** — only parser source
   files.
5. **Does NOT check for the `--bdd-only` flag on non-`gz test` verbs** —
   all `parser*.py` files are scanned, not scoped to `gz test`
   specifically.

---

## `--behave-req-tags`

Implementation: `src/gzkit/governance/trust_audits.py:782-822` (`audit_behave_req_tags`)

Assertions:

1. Scans every `features/**/*.feature` file (line 797).
2. Regex `_FEATURE_COVERS_REQ` at line 779:
   `#\s*@covers\s+(REQ-\d+\.\d+\.\d+-\d+-\d+)` (feature-level covers
   comments).
3. Regex `_SCENARIO_REQ_TAG` at line 98:
   `^\s*@(REQ-\d+\.\d+\.\d+-\d+-\d+)\b` (scenario-level tags).
4. For each file: declared REQs (via covers comments) − tagged REQs (via
   scenario tags) = missing set.
5. Emits one error per file with non-empty missing set; first 5 listed,
   remainder as "(+N more)" (line 814-821).
6. **Does NOT enforce the "heavy-lane / foundation-kind OBPI" scope
   stated in scorecard row #39 Notes** — the check fires on ALL feature
   files with feature-level covers comments, regardless of the parent
   OBPI's lane/kind.
7. **Does NOT check OBPI briefs directly** — only the reverse direction
   (feature-level covers → scenario tag). A Heavy-lane OBPI whose REQs
   have no feature file at all is invisible to this check.
8. **Does NOT check scenario-tag coverage without a corresponding
   feature-level `# @covers` comment** — if a feature has zero
   `# @covers` comments, no scenario tags are required (line 803-804).

---

## `--advisory-scorecard`

Implementation: `src/gzkit/governance/trust_audits.py:927-957` (`audit_advisory_scorecard`)

Assertions:

1. Reads `docs/governance/advisory-rules-audit.md` once (lowercased, line
   940).
2. For each `*.md` under `.gzkit/rules/`: if the file's stem (lowercased)
   does NOT appear as a substring in the scorecard text, emit an error
   (line 942-956).
3. **Does NOT validate the scorecard row's score** (Mechanical /
   Promotable / Judgment / Ambiguous) — only the presence of the stem.
4. **Does NOT validate that the row links to a GHI** when the score is
   Mechanical.
5. **Does NOT check for stale scorecard rows** (rules removed from
   `.gzkit/rules/` but still listed in the scorecard go unflagged).

---

## `--brief-headings`

Implementation: `src/gzkit/governance/trust_audits.py:1193-1239` (`audit_brief_headings`)

Assertions:

1. Scans every `OBPI-*.md` under `docs/design/adr/**` (line 1215).
2. Canonical H3-only headings (line 1186-1190):
   `Implementation Summary`, `Key Proof`, `Closing Argument`.
3. For each line starting with `"## "`: strip `(Lite)` / `(Heavy)`
   parenthetical, casefold, and compare exact match against canonical
   forms (line 1222-1225).
4. Case-insensitive match (casefold, line 1214).
5. Emits one error per `## <canonical-heading>` line found.
6. Exit 3 on drift (policy breach).
7. **Parenthetical stripping is `split("(")[0]`** — so
   `## Implementation Summary (Lite) extra text` correctly strips to
   `Implementation Summary`, but `## Implementation Summary — v2` is
   treated as-is and would NOT match.
8. **Does NOT validate that canonical H3 headings are present** — only
   that they do not appear as H2. A brief missing `### Implementation
   Summary` entirely is invisible to this check.
