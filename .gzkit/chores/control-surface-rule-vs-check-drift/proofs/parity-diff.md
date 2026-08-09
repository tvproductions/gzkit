# Parity Diff — Pass C

> Chore: `control-surface-rule-vs-check-drift` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 ledger.
> Method: for each row, the rule prose AND the validator implementation were
> **re-opened**. Line numbers drifted and were re-read, never copied.

**Accounting commitment honoured — all 43 prior rows have a verdict.**

| Class | Count |
|---|---|
| `carried` — the prose/check gap still exists | **35** |
| `closed` — gap resolved (commit named) | **6** |
| `refuted` — the original row was wrong | **1** |
| `not re-verified this run` (recorded, not hidden) | **1** |

| Verdict shift | Count |
|---|---|
| → `parity` (gap closed) | 6 |
| `parity` → `divergent` (row was mis-scored) | 1 |
| `parity` → `divergent` (rule's own claim went stale) | 1 |
| unchanged | 35 |

---

## Closed this run

| Row | Subject | Closed by | Basis |
|---|---|---|---|
| **P1** | `foundation-adr-registers-invariant` named a witness `--foundation-registers-invariant` that never existed | `08289b87f` | Claim text and witness both replaced with `gz validate --taxonomy`, which resolves. File retained rather than deleted to preserve REQ-0.0.37-01-03. |
| **P2** | the invariant-witness meta-check itself was unregistered | `7290bde62` (GHI #746) | Now `_ScopeEntry("invariant_witness", "default", …)` (`validate_cmd.py:372`) and in `_POLICY_BREACH_ERROR_TYPES` (`:1147`) → exit 3, reached by bare `gz validate` inside `gz check`. |
| **S0** | no `gz check` step ran a bare `gz validate`, so 10 default-tier scopes were unreachable | `0f671b31c` (GHI #744) | `("Validate default scopes", run_validate_default_scopes)` (`quality.py:453`) → `run_command("uv run gz validate", …)`. Re-derived: 52 check steps (was 47); 88 registered scopes; **zero of 13 default-tier scopes now unreachable.** |
| **S1** | `--rule-version-markers` unreachable | `0f671b31c` | Same commit; its message names this scope — *"which is how a real `--rule-version-markers` marker mismatch survived eight days of green commits"*. The live violation is also gone (`afa215257` bumped `mx-mode.md` to a coherent `1.1.0`). |
| **M1** | multi-word subcommands did not resolve (`gz adr bogus` passed) | GHI #588/#748 | `verify_gz_chain` (`verb_references.py:220`) walks subparser levels; docstring: *"Verbs at intermediate levels MUST be registered choices, so typos fail closed."* |
| **M7** | `--advisory-scorecard` checked *mention*, not score | GHI #754 | Filename-stem presence — a proxy *"no edit to an existing rule file could ever falsify"* — replaced by coverage-ledger **version equality** plus four new arms (summary recount, ruff reachability, witness-path existence, prose-Promotable). |

## Refuted

| Row | Original claim | Verification |
|---|---|---|
| **=4** | `--invariant-coherence` has parity with `AGENTS.md:360` | **The row was mis-scored, not regressed.** `AGENTS.md:360` says the check *"re-renders the registry and byte-compares"*. `invariant_coherence.py:67` calls `render_agents_md`, which (`compose.py:8-30`) *"loads the committed rendition … and returns its bytes verbatim"* — no registry is read. The registry-render parameters were deleted in `4f9c7d2bd` (GHI #623) **two weeks before the prior ledger was written**. The prior run scored only the byte-compare/scope half. Verdict corrected to `divergent`; **prose is the stale side.** |

## Not re-verified this run

| Row | Subject | Why |
|---|---|---|
| **M6** | `model_config` presence is checked; its contents are not | The expected module path returned no match this run, so the claim could be neither confirmed nor closed. **Recorded rather than dropped** — the stability commitment forbids a row silently disappearing, and an unverified row is not a closed one. Next run: locate the `--pydantic-models` implementation and give it a verdict. |

---

## Carried — the notable rows

Full per-row detail for all 35 carried rows is preserved in the run transcript;
the rows below are those whose status changed materially or whose evidence moved.

### Exit-code contract drift — four rows, one shape

| Row | Rule claims | Code does | Evidence |
|---|---|---|---|
| **M2** | `governance-core.md:53` — *"Exit 3 on any unresolvable reference"* | exit 1 | `cli.py:224` `type="cli_alignment"`, `:298` `type="manpage_alignment"`; neither in `_POLICY_BREACH_ERROR_TYPES` (`validate_cmd.py:1130-1165`) |
| **M4** | `--brief-headings` *"Exits 3"* | exit 1 | `"brief_headings"` registered at `validate_cmd.py:357`, absent from the breach set |
| **M5** | `changelog-release-notes.md` *"fails closed"* | exit 1 | `"changelog"` registered at `validate_cmd.py:427`, absent from the breach set |
| **M15** | `cli.md:15` names `gz cli audit` a *"Mechanical check"* under a 4-code map where 3 = Policy Breach | exit 1 | `cli_audit.py:243` — `raise SystemExit(1)`, the module's only non-zero exit |

**New instance found this run, not in the prior ledger:** `--transcribed-adr-counts`
(GHI #768, shipped v0.34.2) is **registered in the breach set**
(`validate_cmd.py:1153`) yet emits `type="surface"`
(`transcribed_counts.py:165, :182`), so the registration matches nothing and the
scope exits 1 while its flag help says *"Exit 3 on any (#768)"*. This is the
inverse of M2/M4/M5 — there the rule over-claims; here the *registration* is inert.

**Also found this run:** scorecard row **17e**, added earlier the same day, asserted
*"exit 3 on any unresolvable reference"* for `--cli-alignment` — copied from the
rule rather than read from the code. Corrected in place; the correction is recorded
in the row itself rather than silently applied. It is the same defect as M2, one
layer up, and it demonstrates that `_missing_witness_path_errors` cannot catch this
class: the row cited a real flag, a real module, and a real registration. **Every
path resolved; the behavior claim was still false.**

### Reachability — three rows where the check exists but no gate runs it

| Row | Scope | Status |
|---|---|---|
| **S2** | `--cli-alignment` | Enumeration was widened by `c49557f38` (GHI #745) — but that fixed the *source set*, not reachability. No dedicated `gz check` step; absent from `.pre-commit-config.yaml`. The step labelled *"CLI audit"* (`quality.py:457`) calls `cli_audit.py:172`, which **never invokes `audit_cli_alignment`.** The binding on the only `paths: "**/*"` rule runs in no gate. |
| **S3** | `--commit-trailers` | Four rules name it as the enforcer; it runs in no gate on any surface an operator or CI executes. The only commit-time surface is the **producer** (`task-trailer-stamp`), not the validator. |
| **S4** | `--deprecated-verb-prescription` | Two of three legs closed (the over-claim left binding prose; the live instance is adjudicated in-band at `handoff_resume_gate.py:177-184` as a *read*, not a prescription). The plain reachability fact carries. Verdict improved `divergent` → `prose-wider`. |
| **S5** | `--pointer-anchors` | `_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")` plus `.claude/rules/**` (`pointer_integrity.py:28, :48-54`). `.gzkit/rules/complexity-thresholds.md` — the file whose own version note credits this check — is **not walked**; only its vendor mirror is. |

### Scope narrower than the prose claims

- **M3** — `--cli-alignment`'s enumeration was materially widened (GHI #745) but two residuals remain: the rule declares `docs/**/*.feature`, which the code never globs (it globs `docs/**/*.md` and `features/**/*.feature`), and `docs/releases/` is excluded at enumeration (`cli.py:20-22`) without the rule mentioning it.
- **M8** — `AGENTS.md` credits `--advisor-proof-binding` with *"`Field(min_length=1)` on `AdvisorDiagnosis.proof`"*. The validator reads `properties.proof.minItems` from the **JSON schema** (`advisor_proof_binding.py:122`), never the Pydantic field. Two different artifacts; the credited one is unchecked.
- **M10** — `--unscoped-rules` is credited with a vendor-surface prohibition it cannot see: `unscoped_rules.py:171` globs `.gzkit/rules` only, non-recursive; no `.claude/`, `.agents/`, or `.github/` path appears in the module. Allowlist `added_date` is stored (`:244`) and never compared to today.
- **M11** — `AGENTS.md:212` says `--taxonomy` enforces *"`pool` ⇒ no `kind`/`semver` frontmatter"*. `_check_pool_taxonomy` (`taxonomy.py:241-248`) inspects `kind` only; `semver` is read at `:310` then short-circuited at `:313-315`. **A pool ADR carrying `semver:` passes.** Untouched in range.
- **M16** — `tests.md:18` states the smoke gate *"exit 3 on breach or on an empty tier"* unconditionally. `smoke_cmd.py:37-57` returns `_EXIT_OK` on an empty tier unless `smoke.required`, whose default is `False` (`config.py:163-164`). **The rule ships in the wheel, so it is false for any adopter that has not opted in.**
- **M17** — `AGENTS.md:266` lists `uv run gz arb ruff` in a table *"Locked by `CANONICAL_STEP_COMMANDS`"*. That mapping (`arb/validator.py:62-104`) has no `"ruff"` key; ruff receipts route through `LINT_SCHEMA_ID` with no `step.name`, so `_provenance_error` returns `None` (`:277-278`). **The lock covers 4 of 5 rows in its own table.**
- **P3** — `AGENTS.md:354` says the authoring-guide protocol envelope is *"schema-validated at runtime"*. `rg --fixed-strings authoring_guide_protocol -g '*.py'` returns **zero** hits repo-wide. Scorecard row 55 scores this **Mechanical**.
- **P4** — `complexity-thresholds.md:97` says *"**Silent edits are forbidden** by the validator"*. `complexity_thresholds.py:45-67` asserts only that the file exists, parses, and covers the canonical metrics. **An operator can change `radon_cc` block from 11.0 to 40.0 and the scope stays green.** (The row's own sub-note is refuted: `_every_metric_has_block_band` was already present at baseline.)
- **M9** — `--complexity-doctrine-links` asserts four citation facts only; the "empirically-measured exemplar corpus" claim is not among them.

### Divergent — prose and check assert different things

- **M12** — `task-discovery.md:130` names eight worklog event types as *"the set `--task-envelope-coherence` signature (a) checks"*. `_TASK_WORKLOG_TYPES` (`validate_task_envelope.py:27-38`) is a **different** eight. Overlap is exactly two: six named types unchecked, six checked types unnamed. Both lists byte-identical to the prior capture.
- **M13** — `task-discovery.md:140` promises *"Heavy lane closeouts … Lite lane warns."* `grep -n lane` over `validate_task_envelope.py` returns **zero hits**; `_sig_c_layer_drift` emits unconditionally (`:865-878`) and the type is in the breach set → exit 3 for both lanes. GHI #731's lineage bucketing made the skip fire *less* often, so the missing Lite branch is more consequential now, not less.
- **D3** — `pythonic.md:50-51` accuses the scorecard of miscoding its size limits as Mechanical. **That accusation is now false:** `d01ad2c13` rewrote rows 19/20 to **Judgment**. The scorecard no longer miscodes anything; the rule still says it does — a citation loop where each surface describes a stale version of the other. Verdict changed `parity` → `divergent`.
- **D6** — `task-discovery.md:107`'s *"Witness status unruled — GHI #752"* points at a **closed** issue, for the second time (`dbd138ce9` repointed #731→#752 because #731 closed; `16360ba13` then closed #752). An unruled question parked on a closed issue with no successor. Scorecard row 60 still cites the pre-repoint #731.

### Parity — checks that match their prose

**=1** universal attestation (`adr_audit.py:462-475` returns `True`, fenced by
`mx/invariants.py:110-125`) · **=2** `--chores-layout` (breach type → exit 3) ·
**=3** token-block minimum-information (renamed in lockstep with its rule) ·
**=5** `Task:` trailer strict mode · **=6** distribution content classes (rule
table and `_is_package_only` gained `project_local` in the same change) ·
**=7** `forbid-pytest` · **=8** changelog hermetic/networked split (each side
cites the other by name) · **=9** `--utf8-prefix` reconfigure carve-out ·
**D1** `gh issue create` (rule says nothing mechanical can tell caller apart;
scorecard agrees at Judgment) · **D2** failure-mode taxonomy (advisory by its own
text) · **D4** security-sensitivity direct-fix gap (self-disclosed) ·
**D5** release-notes non-validation (prose, code, and scorecard agree three ways).

**These are the healthy shape:** in every one, the rule states its own enforcement
posture and the scorecard agrees. Where a rule *discloses* its gap, prose and check
stay in parity; where a rule *asserts* a mechanism, it rots.
