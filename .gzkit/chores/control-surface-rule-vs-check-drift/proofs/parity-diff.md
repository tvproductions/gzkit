# Parity Diff — Rule Prose vs. Actual Check Behavior

**Generated:** 2026-08-01 (audit-only re-run; supersedes the 2026-05-10 artifact)
**Inputs:** `prose-assertions.md` (claim IDs `C-nn`), `check-behaviors.md`
(behavior IDs `A-nn` / `B-nn`), `promoted-inventory.md` (scope registry + `gz check`
membership).

Every row carries both halves of the citation the chore requires: the rule's claim
(file + line) and the validator's observed behavior (module:line or CLI output).

## Verdict classes

| Class | Prefix | Meaning |
|---|---|---|
| **Phantom check** | `P-` | Prose names an enforcer that does not exist, or exists but is unreachable from any operator surface |
| **Misdescribed check** | `M-` | The check exists but asserts something narrower than, wider than, or different from what the prose says — including exit-code mismatches |
| **Out-of-scope check** | `S-` | The check exists and matches its prose, but never runs in the pipeline the prose implies |
| **Parity** | `=-` | Prose and code agree; recorded so the diff is not a bug list |
| **Self-disclosed** | `D-` | The rule states its own gap in-band; no drift, and the model for the rest of the corpus |

---

## Class P — Phantom checks (4)

### P1 · `gz validate --foundation-registers-invariant` has never existed
- **Claim:** `.gzkit/invariants/foundation-adr-registers-invariant.json` —
  `"structural_witness": ["gz validate --foundation-registers-invariant"]`, backing the
  claim *"Every foundation-kind ADR registers at least one invariant in `.gzkit/invariants/`."*
- **Behavior:** the flag is absent from all 96 option strings in
  `proofs/validate-help.txt` and from every `_ScopeEntry` in `VALIDATOR_REGISTRY`
  (`src/gzkit/commands/validate_cmd.py:227`). The other three registry entries
  (`CIC-1.json`, `CIC-2.json`, `skill-first-execution-invariant.json`) resolve.
- **Verdict:** phantom. Confirmed live 2026-08-01 — the finding named in the chore
  brief still holds unchanged.
- **Standing:** operator-gated, not agent-fixable.
  `tests/governance/test_invariant_witness.py:102-130` pins it in a shrink-only fence
  whose docstring states *"Disposition (retire the claim, or add ADR linkage and
  backfill) is operator canon work, not an agent call."* The claim is also
  unenforceable as written: `constitutional_invariant.json` carries no field naming
  which ADR registered an entry, and the ratio is 4 invariants to 74 foundation ADRs.

### P2 · The meta-check for P1 is unreachable from the CLI
- **Claim:** implicit in `ADR-0.0.37` and the campaign doc — a structural witness that
  does not resolve is *"structural-witness theater"* and is caught.
- **Behavior:** `validate_invariant_witnesses`
  (`src/gzkit/governance/trust_audits/invariant_witness.py:78`) implements exactly that
  check and is **correct** — `_resolves` (`:50-61`) resolves both `gz validate --<scope>`
  and `gz <verb> [<subverb>…]` shapes. But a whole-repo search returns only the
  definition and `tests/governance/test_invariant_witness.py`. It is **not** exported
  from `trust_audits/__init__.py`, appears in **no** `_ScopeEntry`, and there is **no
  `--invariant-witness` flag** in `gz validate --help`.
- **Verdict:** phantom at the operator surface. The chore brief framed this as
  *"deliberately fenced OUT of `gz check`"* — the live tree is stronger: it is fenced
  out of the CLI entirely. It runs only under `unittest`.

### P3 · `authoring_guide_protocol.json` is "schema-validated at runtime" — nothing validates it
- **Claim:** C-103, root `AGENTS.md` § Governance doctrine surfaces — *"The editor/IDE
  authoring-guide protocol envelope is defined by
  `src/gzkit/schemas/authoring_guide_protocol.json` — schema-validated at runtime
  (ADR-0.0.30)."*
- **Behavior:** the schema file exists (3951 bytes). A repo-wide search for
  `authoring_guide_protocol` outside `.gzkit/chores/` returns `AGENTS.md`, the schema
  itself, and six documentation/ADR artifacts. **No `.py` file references it.** The only
  generic loader, `load_schema(name)` (`src/gzkit/schemas/__init__.py:30`), is by-name
  and is never called with `"authoring_guide_protocol"`.
- **Verdict:** phantom. "Schema-validated at runtime" names no runtime.

### P4 · `--complexity-thresholds` forbids "silent edits" — it has no amendment arm
- **Claim:** C-34, `complexity-thresholds.md:97` — **[V]** *"**Silent edits are
  forbidden** by the validator (OBPI-0.0.28-03 -- `gz validate --complexity-thresholds`)."*
- **Behavior:** `validate_complexity_thresholds`
  (`src/gzkit/governance/trust_audits/complexity_thresholds.py:45`) makes exactly three
  assertions — the JSON exists (`:54-56`); `load_threshold_table` parses it (`:59-63`);
  every `CANONICAL_METRICS` member has >= 1 band (`_check_canonical_metric_coverage`,
  `:104-118`). **No band value, ordering, polarity, citation, or provenance is
  inspected.** An operator can silently change `radon_cc` from `block at 11.0` to
  `block at 40.0` and the scope stays green.
- **Verdict:** phantom capability inside a real flag. The prose's specific promise —
  *silent edits are forbidden* — has no implementing code.
- **Note:** C-31/C-32 (*every metric MUST carry a `block` band; the loader fails closed
  when a canonical metric is missing a block-band row*) are **wider than the code too**:
  `_check_canonical_metric_coverage` asserts >= 1 band of *any* trigger semantic per
  metric. A metric declaring only a `warn` band satisfies it.

---

## Class M — Misdescribed checks (17)

### M1 · Multi-word subcommands do not resolve *(unchanged since 2026-05-10)*
- **Claim:** C-44, `governance-core.md:75` — **[V]** *"**Multi-word subcommands count
  (`gz adr status`, `gz obpi complete`), not just top-level verbs.**"*
- **Behavior:** `audit_cli_alignment` (`trust_audits/cli.py:133`) matches
  ``_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")`` (`cli.py:28`).
  `group(1)` captures **one** token; the rest is swallowed. It resolves against
  `_known_cli_verbs()` (`cli.py:222-232`), which enumerates only top-level
  `_SubParsersAction` choices and does not recurse. A nested-path helper
  `_known_cli_verb_paths()` exists at `cli.py:257` and is used by
  `audit_skill_alignment` — **not** by this audit.
- **Impact:** a reference to `gz adr <typo>` passes the check the rule says should fail
  it. The fix is one call site away (`_known_cli_verb_paths` already exists), which is
  why this row has now survived two audit passes.
- **Verdict:** misdescribed — the single highest-leverage row in the diff.

### M2 · `--cli-alignment` says "Exit 3", exits 1
- **Claim:** C-45, `governance-core.md:79` — **[V]** *"Enforced by `gz validate
  --cli-alignment`. **Exit 3 on any unresolvable reference.**"*
- **Behavior:** `type="cli_alignment"` and `type="manpage_alignment"` are absent from
  `_POLICY_BREACH_ERROR_TYPES` (`validate_cmd.py:1081-1129`), so
  `_print_validation_result` (`:1151-1173`) raises `SystemExit(1)`.
- **Verdict:** misdescribed. A CI job gating on `rc == 3` treats an operator-doc break
  as a user error.

### M3 · `--cli-alignment` scope is narrower than the rule's declared scope
- **Claim:** C-43, `governance-core.md:73` — scope is *"`docs/**/*.md`,
  `docs/**/*.feature`, `features/**/*.feature`, `.gzkit/skills/**/SKILL.md`, and
  runbooks under `docs/user/runbook.md` + `docs/governance/governance_runbook.md`."*
- **Behavior:** `_cli_alignment_sources` (`cli.py:104-117`) walks
  `features/**/*.feature`, `docs/user/runbook.md`, `docs/user/commands/**/*.md`, and
  `docs/user/manpages/**/*.md`. **`.gzkit/skills/**/SKILL.md` and
  `docs/governance/governance_runbook.md` are not in it**, and `docs/**/*.md` narrows to
  two subdirectories. (The sibling `audit_manpage_alignment` *does* walk skills and all
  of `docs/**`, `cli.py:155-186` — so the wider scope exists in the module and is wired
  to the other predicate.)
- **Verdict:** misdescribed — the rule that is the canonical home for this binding
  overstates the surface it covers.

### M4 · `--brief-headings` says "Exits 3", exits 1
- **Claim:** C-11, `brief-heading-conventions.md:48` — **[V]** *"Exits 3 on drift."*
- **Behavior:** `type="brief_headings"` (`trust_audits/briefs.py:104`) is not in
  `_POLICY_BREACH_ERROR_TYPES` → **exit 1**.
- **Also narrower than the frontmatter claim (C-10, "Brief evidence sections must use
  H3"):** `_canonical_h3_heading` (`briefs.py:69-74`) fires only on **H2 drift of four
  named headings** in `_BRIEF_EVIDENCE_H3_HEADINGS` (`:58-66`). A brief that omits all
  four passes clean; H4+ drift is invisible.
- **Verdict:** misdescribed on both exit code and coverage.

### M5 · `--changelog` says "fails closed", exits 1
- **Claim:** C-13, `changelog-release-notes.md:48` — **[V]** *"`gz validate --changelog`
  **fails closed** on changelog shape."*
- **Behavior:** `type="changelog"` (`validate_pkg/changelog.py:40`) is not in the breach
  set → **exit 1**.
- **Partial credit:** the four named assertions (SemVer, ISO date, category set, one
  `GHI #N` per entry) all genuinely exist (`_VERSION_RE` `:36`, `_ALLOWED_CATEGORIES`
  `:20-30`, `_GHI_RE` `:37`). Only the disposition word is wrong. C-15 and C-16 of the
  same rule are exactly right.
- **Verdict:** misdescribed (disposition only).

### M6 · `model_config` presence is checked; its contents are not *(unchanged since 2026-05-10)*
- **Claim:** C-55, `models.md` § Verify — *all models have `model_config` with at least
  `extra="forbid"`*; immutable snapshots use `frozen=True`.
- **Behavior:** `_has_model_config` (`trust_audits/models.py:117-131`) returns `True` for
  **any** `Assign`/`AnnAssign` whose target is the bare name `model_config`, regardless
  of RHS. `model_config = None`, `= {}`, and `= ConfigDict()` all pass. `frozen=True`
  and `extra="forbid"` are never read — even though the emitted error message says
  `model_config = ConfigDict(...)`.
- **Verdict:** misdescribed. Prior run flagged this as the #3 gap; still open.

### M7 · `--advisory-scorecard` checks mention, not score *(unchanged since 2026-05-10)*
- **Claim:** C-122, root `AGENTS.md` § Governance doctrine surfaces — the scorecard is
  *"the Mechanical/Promotable/Judgment/Ambiguous scorecard; **self-tested via
  `gz validate --advisory-scorecard`**"*.
- **Behavior:** `audit_advisory_scorecard` (`trust_audits/release.py:84`) asserts
  `rule_md.stem.lower() in scorecard_text` — a case-folded **substring** search over the
  whole file. A rule stem appearing in a stray cross-reference passes; no table row and
  no score is required. `type="advisory_scorecard"` is not in the breach set → **exit 1**.
  Fails open when either the scorecard or the rules dir is missing.
- **Verdict:** misdescribed. The word doing the work in the prose is *scorecard*; the
  code implements *mention*.

### M8 · `--advisor-proof-binding` never reads the Pydantic field it is credited with
- **Claim:** C-104, root `AGENTS.md` — **[V]** *"`Field(min_length=1)` on
  `AdvisorDiagnosis.proof` — `gz validate --advisor-proof-binding` (OBPI-0.0.29-08)."*
- **Behavior:** `validate_advisor_proof_binding`
  (`trust_audits/advisor_proof_binding.py:30`) has three arms — fixture JSONs under
  `tests/fixtures/advisor/*.json` (`:40-65`), ledger events resolved **against the
  fixture index only** (`:89-91`, `if diag is None: continue`), and the JSON Schema's
  `properties.proof.minItems` (`:107-134`, missing file → `[]`). **No line reads
  `AdvisorDiagnosis`** (`src/gzkit/complexity/advisor/diagnosis.py:129`).
- **Compounding:** `type="advisor_proof_binding"` is not in the breach set → **exit 1**,
  though the module docstring calls itself a *"Fail-closed audit"*.
- **Verdict:** misdescribed on both the asserted surface and the disposition. The
  constraint the bullet names does exist in the model (docstring `diagnosis.py:136-139`)
  — it is simply not what this scope checks.

### M9 · `--complexity-doctrine-links` is credited with the seven selection criteria
- **Claim:** C-105, root `AGENTS.md` — **[V]** *"Complexity calibration is grounded in an
  empirically-measured exemplar corpus (**seven selection criteria**) — `gz validate
  --complexity-doctrine-links` (OBPI-0.0.27-07)."*
- **Behavior:** the audit (`trust_audits/complexity_doctrine_links.py:188`) checks four
  things about **citations** — `parse_citation` succeeds; the distilled-characteristics
  path is a file; the section anchor resolves against a slugified H1–H3; the citation is
  inside the portability window (`:196-242`). Nothing reads
  `complexity-doctrine.md`'s seven selection criteria (C-25) or seven disqualifiers
  (C-26). Its own line-selection heuristic (`:98`) requires a section marker **and**
  `"(corpus revision"` on the line, so a bare doc-path reference is never link-checked
  either. If no `distilled-characteristics-*.md` exists, the portability check is
  skipped entirely (`:231`).
- **Verdict:** misdescribed. C-29 (`complexity-doctrine.md:120`, *"flags but does NOT
  auto-rewrite"*) is accurate — the rule is right and the AGENTS.md summary of it is not.

### M10 · `--unscoped-rules` is credited with a vendor-surface prohibition it cannot see
- **Claim:** C-107, root `AGENTS.md` — **[V]** *"`.gzkit/rules/*.md` with `paths: '**'`
  or missing `paths:` **may not live under any vendor-surface rules directory**
  (ADR-0.0.20) — `gz validate --unscoped-rules`."*
- **Behavior:** the validator's file scope is `.gzkit/rules/*.md`, **non-recursive,
  excluding `AGENTS.md`** (`src/gzkit/validators/unscoped_rules.py:169-171`). It never
  opens `.claude/rules/`, `.agents/`, or `.github/`. The clause about vendor-surface
  directories has no implementing code in this scope.
- **Secondary:** allowlist entries validate `rationale` >= 20 chars and a `tracking_ref`
  pattern (`UnscopedAllowlistEntry`, `:233`), but `added_date` is stored and **never
  compared to today** — allowlist entries never expire.
- **Verdict:** misdescribed. The canonical-side check is real and fail-closed (`exit 3`,
  MX-immune); the vendor-side half of the sentence is not enforced anywhere.

### M11 · `--taxonomy` does not check `semver` on pool ADRs
- **Claim:** C-112, root `AGENTS.md` § Kinds — **[V]** *"`gz validate --taxonomy`
  enforces: `foundation` ⇒ `0.0.x`, `feature` ⇒ non-`0.0.x`, **`pool` ⇒ no `kind`/`semver`
  frontmatter**"*.
- **Behavior:** `_audit_one_adr_taxonomy` (`trust_audits/taxonomy.py:156-175`) reads
  `semver` at `:165`, then:

  ```python
  if is_pool:
      pool_err = _check_pool_taxonomy(rel, kind)
      return [pool_err] if pool_err else []
  ```

  `_check_pool_taxonomy` (`:112-120`) inspects **`kind` only**. A pool ADR carrying
  `semver:` frontmatter passes.
- **Compounding:** `type="taxonomy"` is not in the breach set → **exit 1**, and because
  `other_errors` is evaluated first (`validate_cmd.py:1168-1171`), a single taxonomy
  finding **downgrades the co-running `audit_foundation_closure` breaches from 3 to 1**.
- **Verdict:** misdescribed on the pool half of the claim.

### M12 · `--task-envelope-coherence` signature (a) checks a different eight event types
- **Claim:** C-79, `task-discovery.md:98` — **[V]** *"The eight validator-enforced worklog
  event types in `src/gzkit/events.py` (`artifact_edited`, `gate_checked`,
  `evidence_emitted`, `policy_breach`, `validator_run`, `tool_invoked`, `agent_message`,
  `lint_run` — **the set `gz validate --task-envelope-coherence` signature (a) checks**)"*.
- **Behavior:** `_TASK_WORKLOG_TYPES`
  (`src/gzkit/commands/validate_task_envelope.py:27-38`) is:

  ```python
  {"artifact_edited", "attested", "gate_checked", "audit_receipt_emitted",
   "artifact_renamed", "obpi_completion_uncovered_accept",
   "intrinsic-complexity-attestation", "composition_rendered"}
  ```

  Overlap with the rule's named eight is **exactly two** (`artifact_edited`,
  `gate_checked`). Six types the rule names are never checked; six types the code checks
  are never named.
- **Verdict:** misdescribed. Both lists are eight long, which is how the drift reads as
  parity at a glance.

### M13 · `--task-envelope-coherence` has no Heavy-fails / Lite-warns branch
- **Claim:** C-78, `task-discovery.md` § Layer-drift fail-close — **[V]** *"The OBPI-04
  validator will fail Heavy lane closeouts on layer-drift; **Lite lane warns.**"*
- **Behavior:** `_sig_c_layer_drift` (`validate_task_envelope.py:813-879`) never reads a
  lane. It emits the same `type="task_envelope_coherence"` finding regardless, and that
  type is in the breach set → exit 3 for both lanes. The signature is also skipped
  unless >= 2 channels are non-empty (`:857`), and the commit-trailer channel returns `{}`
  on any `git log --all` nonzero or 30s timeout (`:750-763`) — so the common failure
  mode is *not firing at all*, not warning.
- **Verdict:** misdescribed — the lane-conditional described in the rule does not exist
  in either direction.
- **Adjacent, accurate:** C-80 (default-bucket-only fail-close) **does** exist
  (`_sig_b_subdivision_skipped`, `:521-546`), though the `req_atomic` exemption is a bare
  list with no rationale parsed (`:542`), and it fires only for OBPIs already carrying a
  `completed` receipt (`:475-476`).

### M14 · `--rule-version-markers` declares exit 3 on a dead code path — and is failing now
- **Claim:** C-75, `skill-surface-sync.md` § Version discipline (non-negotiable rule #2)
  — rule files carry a body-level `<!-- rule-version: X.Y.Z -->` marker, with the
  conflict-resolution procedure naming the version as *"the primary signal"*.
- **Behavior:** `run_rule_version_markers`
  (`src/gzkit/validators/rule_version_markers.py:109-120`) builds
  `RuleVersionMarkersResult(..., exit_code=3 if violations else 0)` — but **has no caller
  anywhere in `src/`**. The live registry path is `audit_rule_version_markers_errors`
  (`:123`), which stamps **`type="surface"`** (`:135`), not `"rule_version_markers"`.
  `"surface"` is not in `_POLICY_BREACH_ERROR_TYPES` → **exit 1**.
- **Live failure:** `.gzkit/rules/mx-mode.md:12` carries `<!-- rule-version: 1.0.1 -->`
  while `:16` carries `> **Rule version:** \`1.0.0\` — initial authoring under ADR-0.0.74
  (OBPI-0.0.74-08)`. That is `marker-blockquote-drift` by `_MARKER_RE` (`:41`) and
  `_BLOCKQUOTE_RE` (`:42`).
- **Verdict:** misdescribed **and** out-of-scope — a check that exists, is failing right
  now, exits 1 instead of the 3 its own dead path declares, and never runs in `gz check`
  (see S1). The drift it exists to catch is present in the corpus it audits.

### M15 · `gz cli audit` exits 1 where `cli.md`'s own exit-code map says 3
- **Claim:** C-21 + C-23, `cli.md:33` and `:49-58` — the same file names
  `uv run gz cli audit` as *"**Mechanical check**"* and binds a 4-code map in which
  **3 = Policy Breach**. A documentation-contract breach is a policy breach by that map.
- **Behavior:** `cli_audit_cmd` (`src/gzkit/commands/cli_audit.py:172-243`) ends
  `if issues: raise SystemExit(1)` (`:242-243`). **There is no exit-3 path in the module.**
- **Partial credit:** C-22's specific promise — usage-line agreement on required-ness
  and value-taking — genuinely exists (`check_flag_doc_truth`, `:220-233`), and C-24's
  disclaimer about lane adjudication is accurate.
- **Also weaker than it reads:** the index check is a bare basename substring (`:203-204`,
  a link target is never validated); the manpage heading check is `startswith` on
  `lstrip()` (`:198-200`); `check_surfaces_report` returns `passed=True` on
  `FileNotFoundError` (`:114-122`).
- **Verdict:** misdescribed — a rule contradicting its own exit-code map about its own
  named mechanical check.

### M16 · `gz smoke`'s empty-tier fail-close is opt-in, not intrinsic
- **Claim:** C-83, `tests.md:18` — **[V]** *"Enforced by that verb (**exit 3 on breach or
  on an empty tier**)"*.
- **Behavior:** `smoke_gate` (`src/gzkit/commands/smoke_cmd.py:37-57`):

  ```python
  if not smoke_marked_files(root):
      if not GzkitConfig.load(root / ".gzkit.json").smoke.required:
          ... return _EXIT_OK
      ... return _EXIT_POLICY_BREACH
  ```

  `SmokeConfig.required` defaults to **`False`** (`src/gzkit/config.py:163-164`). gzkit
  opts in (`.gzkit.json:16-18`), so the claim holds **here** and is false as a statement
  about the verb — which matters because this rule ships in the wheel.
- **Also unstated:** `--budget` (`parser_maintenance.py:329-334`, `default=None`) is an
  unbounded per-run override of the 60s ceiling; an actual test failure returns
  `_EXIT_TEST_FAILURE = 1` (`:63-69`), a third outcome the rule does not name; tier
  membership is a regex scan (`_SMOKE_DECORATOR_RE`, `src/gzkit/smoke.py:48`), so a
  `@smoke` inside a comment counts as a populated tier.
- **Verdict:** misdescribed for any consumer repo. The breach half of the claim (exit 3
  at `> 60.0s`) is exactly right.

### M17 · `CANONICAL_STEP_COMMANDS` does not lock row 1 of the attestation table
- **Claim:** C-116, root `AGENTS.md` § Attestation — a five-row canonical-invocation
  table whose first row is `uv run gz arb ruff` / `arb-ruff-`, closed with **[V]**
  *"**Locked by `CANONICAL_STEP_COMMANDS`; `gz arb validate` flags drift.**"*
- **Behavior:** `CANONICAL_STEP_COMMANDS` (`src/gzkit/arb/validator.py:53-72`) has keys
  `typecheck`, `unittest`, `coverage`, `mkdocs`, plus two deliberately-empty reserved
  slots (`security`, `meta-receipt-bind`). **There is no `"ruff"` key.**
  `_canonical_provenance_error` (`:200-214`) returns `None` unless the receipt carries a
  `step` dict whose `name` is a key of that mapping; ruff receipts take the
  `LINT_SCHEMA_ID` path (`:78`) and have no `step.name`.
- **Verdict:** misdescribed. The lock covers 4 of 5 rows. The same claim is repeated
  verbatim in `adr-audit.md:32` and `gate5-runbook-code-covenant.md:43`, so the drift is
  replicated across three surfaces.

---

## Class S — Out-of-scope checks (5 named + 1 structural)

### S0 · **Structural:** no `gz check` step runs a bare `gz validate`
- **Observed:** `_build_check_steps()` (`src/gzkit/commands/quality.py:385-487`) returns
  47 steps, each a dedicated runner. None invokes `gz validate` without flags.
- **Consequence:** a scope reaches `gz check` only via its own step. **29 of 81 registry
  scopes do; 52 do not** — including **nine of the twelve default-tier scopes**
  (`manifest`, `surfaces`, `ledger`, `instructions`, `briefs`, `documents`, `personas`,
  `frontmatter`, `version`) plus `rule_version_markers`. The tier label `default` names
  behavior under bare `gz validate`, not under `gz check`; nothing in rule canon says so.
- **Verdict:** the root cause of every row below.

### S1 · `--rule-version-markers` is default-tier and never runs in `gz check`
See M14. Default tier + no dedicated step = the marker discipline in
`skill-surface-sync.md` #2 is unenforced in the operator loop, while a real violation
(`mx-mode.md`) sits in the tree.

### S2 · `--cli-alignment` is not in `gz check`; `gz cli audit` is a different check
- **Claim:** C-43–C-46, `governance-core.md:73-81` — the section that declares itself
  **[V]** *"the canonical rule home"* for operator-doc verb resolution, on the only rule
  scoped `paths: "**/*"` (loaded on every edit, every session).
- **Behavior:** `cli_alignment` is `explicit` tier with no `gz check` step. `gz check`
  runs `("CLI audit", run_cli_audit)` (`quality.py:447`) → `uv run gz cli audit`, which
  audits manpage/index/README/flag coverage (`cli_audit.py:172-243`) and does **not**
  resolve `gz <verb>` strings in operator docs.
- **Verdict:** out-of-scope, with a naming collision that makes the gap invisible — a
  green `gz check` shows a step labelled "CLI audit" while the cli-alignment binding
  never ran.

### S3 · `--commit-trailers` is claimed by four rules and runs in no gate
- **Claim:** C-76/C-77 (`task-discovery.md:24,26`), C-85 (`tests.md:87`), C-121
  (`AGENTS.md` Always #12), C-05 (`agent-failure-modes.md:27`) — all name it as the
  enforcer of the `Task:` trailer floor.
- **Behavior:** `explicit` tier, no `gz check` step, not in `.pre-commit-config.yaml`.
  The only commit-time surface is `.gzkit/hooks/prepare-commit-msg-task-trailers`
  (`.pre-commit-config.yaml:10-12`), a **producer** that stamps trailers — it never
  validates. `task-discovery.md` § Convention: Commit trailer already flags this:
  **[V]** *"Witness status unruled — GHI #731."*
- **Compounding:** the validator inspects **HEAD only**
  (`validate_commit_trailers.py:23-49`), so it could not gate history even if wired.
  `type="commit_trailers"` is not in the breach set → exit 1 (M-class).
  Arm B (`:109-131`) shells `gh issue view` and **fails open** on any network or auth
  failure.
- **Verdict:** out-of-scope. The most-claimed check in the corpus runs in no gate.

### S4 · `--deprecated-verb-prescription` cannot see `.py` surfaces — and there is a live instance
- **Claim:** C-48, `governance-core.md:25` — **[V]** *"`gz validate
  --deprecated-verb-prescription` fails closed on **any governed surface** that
  prescribes a deprecated verb."* Repeated at `chores.md:16-17`.
- **Behavior:** `_SURFACE_GLOBS` (`trust_audits/deprecated_verb_prescription.py:47-52`)
  and `_SURFACE_FILES` (`:54-59`) are **markdown-only** — `.gzkit/rules/**/*.md`,
  `.gzkit/skills/**/SKILL.md`, `src/gzkit/rules/**/*.md`, `src/gzkit/skills/**/SKILL.md`,
  `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, `AGENTS.md`,
  `CLAUDE.md`. **No `.py` path is in scope.**
- **Live instance:** `src/gzkit/handoff_resume_gate.py:102` grants the tuple
  `("gz", "gates")` and `:360` prescribes it, while the declared successor `gz closeout`
  (`src/gzkit/governance/deprecations.py:40-42`) is **absent from that allowlist** —
  i.e. a Python surface actively routes agents onto the retired verb and steers them away
  from its replacement, invisibly to the audit that exists to prevent exactly this.
- **Also:** the escape marker `_ESCAPE_MARKER = "deprecated-verb-ok"` (`:45`) is a bare
  substring test (`:92`) — no reason is parsed, despite the error prose implying
  `deprecated-verb-ok: <reason>`. And the scope is not in `gz check`.
- **Verdict:** out-of-scope **and** under-scoped. The word *"any"* in the rule is the drift.

### S5 · `--pointer-anchors` audits the vendor mirror, not canonical rules
- **Claim:** C-30, `complexity-thresholds.md:16` — pointer paths corrected *"so
  `gz validate --pointer-anchors` resolves them correctly (ADR-0.0.33 Invariant 3)"*.
- **Behavior:** `_iter_surface_files` (`trust_audits/pointer_integrity.py:41-56`) walks
  `AGENTS.md`, `CLAUDE.md`, and **`.claude/rules/**/*.md`** — the vendor mirror.
  `.gzkit/rules/complexity-thresholds.md`, the file whose pointers the version note is
  about, is **not** in scope; it is covered only transitively via its mirror.
- **Also weaker than documented:** the back-pointer predicate is
  `"<!-- lifted-from:" in dest_content` (`:128`) — a **substring** test. The docstring
  claims the comment must be `<!-- lifted-from: <source-path>#<anchor> -->`, but path and
  anchor are never checked, so one `lifted-from` comment anywhere satisfies every pointer
  aimed at that file.
- **Mitigation:** it *is* wired into `.pre-commit-config.yaml:65` (`surface-fidelity-cheap`),
  so it runs pre-commit even though it is absent from `gz check`.
- **Verdict:** out-of-scope relative to the canonical surface the rule lives on.

---

## Class D — Self-disclosed gaps (6) — no drift

| ID | Rule | The disclosure | Confirmed against code |
|---|---|---|---|
| D1 | `gh-cli.md:30` (C-40) | **[V]** *"the sanctioned and forbidden invocations are byte-identical commands. Nothing mechanical can tell them apart — the discipline is yours to keep."* | Accurate. No check exists and the rule says so. **The model for the corpus.** |
| D2 | `agent-failure-modes.md:27` (C-05) | **[V]** *"Advisory vocabulary, not a mechanical gate."* | Accurate. |
| D3 | `pythonic.md:45-52` (C-61–C-64) | An in-band `Enforced by` column marking functions<=50 and modules<=600 as backed by nothing, and naming xenon as **[V]** *"a *third* ceiling, matching neither authority"* | Accurate. `.pre-commit-config.yaml:47-49` runs `uvx xenon --max-absolute C`; `.gzkit/rules/complexity-thresholds.json` blocks `radon_cc` at 11.0. Both live, disagreeing, disclosed. |
| D4 | `security-sensitivity.md:23` (C-69) | **[V]** *"the self-bootstrapping floor is **unenforced on the path operator canon mandates** … a discipline obligation, not a mechanical one."* | Accurate — `audit_sensitivity_binding` reads brief frontmatter only. |
| D5 | `changelog-release-notes.md:50,53-54` (C-15, C-16) | **[V]** *"no mechanical release-notes validator"* and *"not in the default `gz check`"* | Both accurate. |
| D6 | `task-discovery.md` § Convention: Commit trailer (C-82) | **[V]** *"Witness status unruled — GHI #731."* | Accurate — the hook is a producer with no witness (see S3). |

**One partial.** `security-sensitivity.md:29` (C-68) discloses that the MX hangar demotes
the sensitivity floor to advisory — **but overstates it.** `sensitivity` is indeed absent
from `GATE5_INVARIANTS` (`src/gzkit/mx/invariants.py:23-31`), so the registry/umbrella
path would resolve ADVISORY; that path (`_sensitivity_umbrella_runner`,
`validate_cmd.py:543`) is **unreachable from the CLI**. `--sensitivity` short-circuits to
`_run_sensitivity_scope` (`validate_cmd.py:1341-1342`), which never consults the
checkpoint and raises `SystemExit(3)` (`:915-916`). The flag an operator runs stays
fail-closed in the hangar. Classed `M`-adjacent: a disclosure that is more pessimistic
than the code. Same for `--unscoped-rules`, the other solo handler.

---

## Class = · Parity (9) — recorded so this is a diff, not a bug list

| ID | Claim | Verified behavior |
|---|---|---|
| =1 | C-42/C-114 — Gate 5 universal, **[V]** *"`_requires_human_obpi_attestation` returns `True` unconditionally"* | `src/gzkit/commands/adr_audit.py:462-475` — literally `return True`; docstring confirms the branching was collapsed |
| =2 | C-17/C-18 — `--chores-layout` fail closed exit 3 | `type="chores_layout"` in `_POLICY_BREACH_ERROR_TYPES` (`validate_cmd.py:1084`) |
| =3 | C-91/C-92/C-96 — `--lock-handoff-coupling` exit 3, per-field frontmatter/body channel | `lock_handoff_coupling.py:26-27` (3 frontmatter keys + `_DECISIONS_RE` body section), `:178-212`; type in breach set (`validate_cmd.py:1121`). v0.3.0's per-field correction landed cleanly |
| =4 | C-108 — `--invariant-coherence` byte-compare, in default `gz check` scope | `invariant_coherence.py:67-73`; step at `quality.py:455`; type in breach set |
| =5 | C-77/C-85 — `Ceremony:`/`Eval-feedback-source:` no longer substitute for `Task:` on src/tests | `has_task_trailer` (`tasks.py:327-347`) matches only `_ANY_TASK_TRAILER_RE`; `parse_ceremony_trailers` is never consulted |
| =6 | C-74 — `--distribution` honors `package_only` / `runtime_state` classifier verdicts | `_is_package_only` (`distribution.py:66-79`) suppresses drift classes 1 and 3 |
| =7 | C-118 — `forbid-pytest` pre-commit hook | `.pre-commit-config.yaml:40-45` |
| =8 | C-14 — changelog **coverage** is a release-time networked cross-check, not a hermetic one | `validate_changelog` docstring `:9-12` explicitly scopes coverage out to `gz-patch-release` |
| =9 | C-36 — `--utf8-prefix` covers the `PYTHONUTF8=1` prefix and the fresh-interpreter pipe carve-out | `cross_platform.py:85`, `:89-95`; the rule's *"the runtime guard covers only `uv run gz ...`"* matches the reconfigure-escape logic exactly |

---

## Tally

| Class | Count |
|---|---|
| **P** — phantom check | 4 |
| **M** — misdescribed check | 17 |
| **S** — out-of-scope check | 5 named + 1 structural (S0) |
| **D** — self-disclosed, no drift | 6 (+1 partial, over-pessimistic) |
| **=** — parity | 9 |
| **Z** — binding prose naming no enforcer (no parity row) | see `prose-assertions.md` § Z |

122 enforcement claims extracted; 41 carry a parity verdict; the remainder are either
unclaimed doctrine (§ Z) or restatements of a claim already scored.
