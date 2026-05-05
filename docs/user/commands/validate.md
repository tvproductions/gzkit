# gz validate

Validate governance artifacts against schema rules.

## Usage

```bash
gz validate [--manifest] [--documents] [--surfaces] [--ledger]
            [--instructions] [--briefs] [--personas]
            [--interviews] [--decomposition]
            [--requirements] [--commit-trailers]
            [--taxonomy] [--chores-layout]
            [--frontmatter [--adr <ID>] [--explain <ADR-ID>]]
            [--attestation-receipts <text|@file> [--lane heavy|lite] [--kind foundation|feature]]
```

## Description

Verifies governance artifacts against their schema definitions and enforces
canonical/mirror sync parity for generated control surfaces. When no flag is
supplied, the manifest, documents, surfaces, ledger, instructions, briefs, and
personas scopes all run. The `--interviews`, `--decomposition`,
`--requirements`, and `--commit-trailers` scopes are opt-in and only run when
explicitly requested.

### `--attestation-receipts`

Validate ARB receipt citations in an attestation string. Argument is either
literal text or `@path` to a file whose content is the attestation. The scope
parses inline `arb-(ruff|step-<name>)-[a-f0-9]{32}` IDs, reads each receipt
from `artifacts/receipts/`, and asserts each cited receipt exists, has
`exit_status == 0`, and matches the category named adjacent to the citation.
Pair with `--lane` (default `heavy`) and `--kind` (default `feature`) so the
zero-receipts policy fails closed on heavy or foundation work and warns on
lite-non-foundation. Authored under
[ADR-0.0.24-attestation-receipt-binding](../../design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md);
the gate's invocation point, the `arb-meta-receipt-bind-…` self-attesting
receipt family, and the failure-mode taxonomy live in
[`docs/governance/arb-middleware.md` § Receipt-binding gate](../../governance/arb-middleware.md#receipt-binding-gate).

The same gate fires pre-emission inside `gz obpi complete --attestation-text …`
and `gz adr emit-receipt … --attestor …`, so an attestation string that fails
this scope on heavy or foundation work will also fail the corresponding
completion / receipt-emission command.

#### Failure modes

| Verdict | Cause |
|---------|-------|
| `no_ids` | Attestation contains zero `arb-…` citations |
| `missing` | A cited receipt file is not present in `artifacts/receipts/` |
| `status_mismatch` | A cited receipt has `exit_status != 0` |
| `claim_mismatch` | A cited receipt's category does not match the category named adjacent to the citation (e.g. `lint:` adjacent to an `arb-step-typecheck-…` receipt) |

On heavy lane or foundation kind, any verdict other than clean exits 3
(fail-closed). On lite lane with feature kind and no security sensitivity,
the same verdicts emit a warning and the attestation still records as
narrative-only.

#### Examples

Heavy / foundation, citation resolves cleanly:

```bash
$ uv run gz validate --attestation-receipts \
    "Tests pass — full unittest sweep clean (lint: receipt arb-ruff-008dda0e47384e89bea69e3b8b5cb6d4)" \
    --lane heavy --kind foundation
✓ 1 attestation receipt(s) resolved.
$ echo $?
0
```

Heavy / foundation, narrative-only attestation (zero citations) — fail-closed:

```bash
$ uv run gz validate --attestation-receipts \
    "Implementation complete; all checks green." \
    --lane heavy --kind foundation
❌ No ARB receipt IDs cited (heavy or foundation: fail-closed).
$ echo $?
3
```

### `--lane`

Lane axis for `--attestation-receipts`: `heavy` (default) or `lite`.

### `--kind`

Kind axis for `--attestation-receipts`: `foundation` or `feature` (default).

### `--requirements`

Flags OBPI briefs whose `## REQUIREMENTS` sections contain no
`REQ-X.Y.Z-NN-MM` identifiers. Such briefs are invisible to `gz covers` and
break the REQ → test traceability chain. Added under GHI-160 Phase 6 to
prevent the governance-graph rot that surfaced in ADR-0.23.0 and the 18
ADRs using the legacy fail-closed requirements template.

### `--commit-trailers`

Flags HEAD commits that touch `src/` or `tests/` without a `Task:` trailer.
The trailer format is `Task: TASK-X.Y.Z-NN-MM-PP` and provides the
execution-level link from a code change back to the governing REQ. Added
under GHI-160 Phase 6 as an advisory guard against the TASK-registry
bypass pattern observed across GHI-141 through GHI-156.

Non-code commits (docs-only, config-only) and commits with a valid
trailer pass the check. The scope scans HEAD only.

### `--taxonomy`

Enforces the ADR taxonomy contract from ADR-0.0.17: every non-pool ADR
carries `kind: foundation` or `kind: feature` in frontmatter, `foundation`
ADRs use `0.0.x` semver, `feature` ADRs use any other semver, and pool
ADRs (id prefix `ADR-pool.`) carry no `kind:` field (their kind is
derived from the id prefix). Runs under bare `gz validate` as a default
scope and is also accessible as a discrete flag for focused invocation.

Violations include:

- Pool ADR carrying a `kind:` field.
- Non-pool ADR missing `kind:`.
- `kind: foundation` paired with a non-`0.0.x` semver.
- `kind: feature` paired with a `0.0.x` semver.
- Any `kind:` value other than `foundation` or `feature` on a non-pool ADR.

The audit never mutates files.

### `--surfaces`

The surfaces scope enforces three contracts:

1. **Existence and shape** — required control surface files exist and their
   YAML frontmatter + required headers validate against the schema.
2. **Frontmatter models** — SKILL.md and `.github/instructions/*` frontmatter
   validate against the canonical Pydantic models.
3. **Canonical sync parity** — every generated surface file (`AGENTS.md`,
   `CLAUDE.md`, `.claude/rules/**`, `.claude/hooks/**`, `.claude/skills/**`,
   `.agents/skills/**`, `.github/skills/**`, `.github/instructions/**`,
   `.github/copilot-instructions.md`, `.github/discovery-index.json`,
   `.claude/settings.json`, `.copilotignore`, and nested `AGENTS.md` under
   `src/`, `tests/`) must match what `sync_all()` would write for the current
   canonical state. Hand edits to generated surfaces surface as drift findings
   pointing at `uv run gz agent sync control-surfaces` for repair.

Sync parity is checked via a snapshot-sync-compare-restore protocol: the
validator reads each tracked surface, runs `sync_all()` in place, compares the
regenerated content to the snapshot, and restores the pre-check state. From
the caller's perspective the check is non-mutating. The operational
`- **Updated**: YYYY-MM-DD` line in `AGENTS.md` is normalized before
comparison so stale sync timestamps never trigger false drift.

### `--frontmatter`

Validates the four governed frontmatter fields (`id`, `parent`, `lane`,
`status`) on every ADR and OBPI file against the ledger's artifact graph.
Keys lookups on filesystem path only — never on frontmatter `id:` (that
pattern reproduces GHI #166). The check uses the same canonical ledger
semantics API that `gz adr report` uses, so drift reported by this scope
is the same drift the operator sees in the report surface.

Ungoverned frontmatter keys (`tags:`, `related:`, any key outside the
four governed fields) are ignored. The validator never mutates files —
reconciliation belongs to `gz chores run frontmatter-ledger-coherence`
(ADR-0.0.16 / OBPI-03). Exits 3 on drift per CLI doctrine 4-code map.

#### `--adr <ID>`

Scopes `--frontmatter` validation to one ADR (and its child OBPIs).
Useful for iterating on a single artifact without reprinting repo-wide
drift.

#### `--explain <ADR-ID>`

Prints step-by-step remediation per drifted field for the named ADR.
Every drifted field gets a one-line recovery command naming an executable
`gz` verb (`gz register-adrs`, `gz adr promote`,
`gz chores run frontmatter-ledger-coherence`). Never suggests hand-editing
frontmatter — frontmatter is L3 derived state, not a source of truth.

#### Examples

```bash
# Repo-wide frontmatter coherence check
gz validate --frontmatter

# Machine-readable drift report (emits drift[] array in payload)
gz validate --frontmatter --json

# One ADR at a time
gz validate --frontmatter --adr ADR-0.1.0

# Remediation guidance for a drifted ADR
gz validate --frontmatter --explain ADR-0.1.0
```

### `--chores-layout`

Enforces the chores-tree layout invariant from
[ADR-0.0.21](../../design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md).
Walks the working tree and flags any `CHORE.md` or `acceptance.json` file
located outside the two canonical roots — `src/gzkit/chores/` (the packaged
canonical source in this repo) and `.gzkit/chores/` (the project-local
overlay in consumer projects, or the configured `paths.chores` value).

Stray files outside those roots reproduce the pre-ADR-0.0.21 layout this
audit exists to close. The walk skips `.git/`, `__pycache__/`, `.venv/`,
`dist/`, `build/`, `node_modules/`, and any dotfile-hidden path. Explicit
exemptions live in `data/chores_layout_waivers.json` — waiver drift across
ADRs requires an explicit add rather than a silent skip.

```bash
# Fail-closed audit
gz validate --chores-layout

# Machine-readable result
gz validate --chores-layout --json
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Clean tree (or all violations waived) | — |
| 3 | One or more unwaived stray `CHORE.md` / `acceptance.json` | Move the file under `src/gzkit/chores/<slug>/` or `.gzkit/chores/<slug>/`, or add an explicit waiver entry |

### `--unscoped-rules`

Enforces the agent-rule placement invariant ([ADR-0.0.20](../../design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md)). Non-path-scoped agent rules (`paths: "**"` or missing `paths:`) may not live under any vendor-surface rules directory — they belong in `AGENTS.md` (root or hierarchical per-directory) at the narrowest appropriate scope.

- Enumerates canonical `.gzkit/rules/*.md` files (mirrors under `.claude/rules/`, `.github/instructions/` etc. are not checked — the sync contract guarantees mirror fidelity).
- Parses YAML frontmatter and classifies each file as `concrete` (PASS), `missing-paths` (VIOLATION), or `universal-glob` (VIOLATION).
- Consults `.gzkit/manifest.json#/rules/unscoped_allowlist` for explicit exceptions.

```bash
# Check the canonical rule files
gz validate --unscoped-rules

# Machine-readable result (parseable via json.loads, roundtrips through UnscopedRulesResult)
gz validate --unscoped-rules --json

# List current allow-list entries and exit 0
gz validate --unscoped-rules --allowlist-only
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All rule files PASS or ALLOWLISTED | — |
| 2 | I/O error — missing or malformed `.gzkit/manifest.json`, or unreadable rule file | Restore the manifest from git; fix the file referenced in the error |
| 3 | Policy breach — one or more non-allowlisted violations | Narrow the file's `paths:` to a concrete glob, fold the content into `AGENTS.md`, or add an explicit allow-list entry under `rules.unscoped_allowlist` in `.gzkit/manifest.json` (entry must include `file`, `rationale` ≥20 chars, `tracking_ref` matching `GHI-\d+` or `ADR-[\d.]+[-\w]*`, and ISO `added_date`) |

No `--fix` variant: recovery is a judgment call (narrow vs. fold vs. allow-list) and the wrong automatic choice is worse than a prompted fix.

Included in `gz validate --audits` and `gz check` aggregate passes — future unscoped rules cannot silently accrete.

### `--absorption-duplicates`

Detects parallel OBPI evaluations of the same opsdev/airlineops source
module across different parent ADRs (GHI #376). Walks every OBPI brief
under `docs/design/adr/**/obpis/`, extracts the opsdev source path from
each brief's `## Source Material` block, and groups records by source
path. When the same source path appears in briefs under two or more
distinct parent ADRs, each unwaived brief is flagged.

A legitimate by-reference closure (e.g. ADR-0.26.0 confirming a module
ADR-0.25.0 already absorbed) opts out by declaring
`paired_with: <prior-brief-id>` in frontmatter. Either side of the pair
may carry the marker; pairing is mutual. A third brief arriving without
its own pairing fires the audit on itself alone — the prior pair is an
acknowledged closure, not a recurrence.

```bash
# Audit every brief tree against the duplicate-evaluation invariant
gz validate --absorption-duplicates

# Machine-readable per-brief records
gz validate --absorption-duplicates --json
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | No cross-ADR duplicates, or all duplicates have a `paired_with:` waiver | — |
| 3 | Same opsdev source path appears in OBPIs across distinct parent ADRs without a pairing | Add `paired_with: <prior-brief-id>` to the by-reference brief's frontmatter, or — if the second evaluation is genuinely independent — document the rationale and pair the briefs explicitly |

### `--evaluation-justify-binding`

Enforces the ADR-0.0.26 evaluation feedback-loop doctrine (§ Decision #2). Reads the most
recent `adr-evaluation` ledger event for the specified artifact (or all artifacts when no ID
is given). If any dimension score is below `low_score_threshold` **or** the number of
red-team challenges fired is at or above `red_team_count_threshold` (both configured in
`data/eval_feedback_thresholds.json`, defaults 3.0 / 3), a qualifying `gz-justify` artifact
must exist at `artifacts/justify/`. The gate is also called automatically before any artifact
advances past `Pending` lifecycle state.

```bash
# Check a specific artifact
gz validate --evaluation-justify-binding ADR-0.0.26

# Check all artifacts that have adr-evaluation events
gz validate --evaluation-justify-binding
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | No violations — gate not triggered, or trigger + justify artifact present | — |
| 3 | Gate triggered (low score or high red-team count) with no qualifying `gz-justify` artifact | Run `uv run -m gzkit justify <artifact-id> --save` then commit the filled artifact |

### `--sensitivity`

Enforces the ADR-0.0.22 security-sensitivity invariant. Reads `data/security_surfaces.json` (the canonical glob-to-category registry) and walks every OBPI brief's `## ALLOWED PATHS` block. Any intersection between a brief's allowlist and the registry forces `sensitivity: security` (the auto-detect floor); frontmatter MAY escalate to `sensitivity: security` when paths don't trigger detection, but MAY NOT declare a value below the detected floor (escalate-not-escape). Fail-closed when the registry is missing, malformed, or schema-invalid.

```bash
# Audit every brief against the registry
gz validate --sensitivity

# Machine-readable per-brief records
gz validate --sensitivity --json

# Predict classification for an ad-hoc path list (no artifact mutation)
gz validate --sensitivity --explain "src/gzkit/ledger.py,tests/governance/**"
```

`--explain ALLOWED_PATHS_LIST` is the predictive sub-form (the 2am-operator pressure-relief valve): pass a comma- or newline-separated path list and the validator prints the predicted `detected_sensitivity` plus matching category labels without reading the on-disk brief tree. This is prediction, not bypass — the runtime validator still fails closed on actual escape attempts.

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Clean tree (auto-detect floor may have fired without escape) | — |
| 3 | Escape attempt (brief declares less than detected) **or** registry missing/malformed | Set `sensitivity: security` in frontmatter, drop the lower-priority declaration, or restore `data/security_surfaces.json` |

Included in `gz validate --audits` and `gz check` aggregate passes — sensitivity drift cannot silently land alongside other governance work.

### `--complexity-doctrine-links`

Enforces the ADR-0.0.27 citation contract: every citation in cluster ADRs (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) plus `.gzkit/rules/complexity-doctrine.md` and any document under `docs/governance/complexity/` must resolve. The validator parses each citation via the canonical `parse_citation` surface (OBPI-0.0.27-05) and asserts: (a) the cited distilled-characteristics file exists, (b) the section anchor resolves to a heading in that file, and (c) the cited `corpus_revision` is portable against the most recent distilled-characteristics document's frontmatter (default supported window: 2 revisions). Closes the 2am-Scenario-2 failure mode — an operator following an advisor diagnosis cannot silently land on a missing or stale artifact.

A line is treated as a citation candidate only when it carries both the section marker `§` and the canonical `(corpus revision` token. Bare path mentions in prose, allowed-path lists, code-fences, and ADR `§ <heading-name>` cross-references are not flagged.

```bash
# Audit every citation in the cluster
gz validate --complexity-doctrine-links
```

**Speculative-citation marker.** When a citing ADR forward-references a planned-but-unlanded distillation (rare; reserved for cluster-internal coordination), prefix the citation line with the HTML-comment marker on the line above:

```markdown
<!-- gz-validate-skip: complexity-doctrine-links -->
docs/governance/complexity/distilled-characteristics-2027-01-15.md § new-metric (corpus revision 2)
```

The marker is a per-citation escape, not a global allowlist. Use only when the parent ADR's amendment ceremony explicitly tracks the unlanded reference.

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Every citation resolves (file + anchor + portable revision) | — |
| 3 | Missing file, unresolved anchor, non-portable revision, or malformed canonical form | Re-author the citation against the current distilled-characteristics document, or amend the citing ADR through `ADR-pool.doctrine-amendment-protocol` |

Included in `gz check` (step "Complexity-doctrine links") and runnable as `gz validate --complexity-doctrine-links` directly. Pre-commit / pre-merge gates fire automatically.

## Scopes Reference

The following table catalogs every audit scope the `gz validate` surface
exposes. Scopes marked **default** run when no flag is supplied; the rest are
opt-in. Each scope can be invoked individually for focused verification or as
part of `gz validate --audits` / `gz check` aggregate passes.

| Scope flag | Default? | Purpose |
|------------|----------|---------|
| `--manifest` | yes | Validate `.gzkit/manifest.json` against the manifest schema |
| `--documents` | yes | Validate governance docs (PRDs, constitutions, ADRs, OBPI briefs) |
| `--surfaces` | yes | Validate control-surface existence, frontmatter shape, and canonical sync parity |
| `--ledger` | yes | Validate ledger integrity (event ordering, payload schema, append-only invariant) |
| `--instructions` | yes | Validate agent-instruction surfaces (`AGENTS.md`, `CLAUDE.md`, hooks) |
| `--briefs` | yes | Validate every OBPI brief against the canonical OBPI schema |
| `--personas` | yes | Validate persona files in `.gzkit/personas/` |
| `--interviews` | opt-in | Verify ADRs with OBPIs have interview-transcript artifacts |
| `--decomposition` | opt-in | Validate ADR decomposition scorecards and checklist-to-brief alignment |
| `--requirements` | opt-in | Flag OBPI briefs whose `## REQUIREMENTS` sections lack REQ-ID identifiers |
| `--commit-trailers` | opt-in | Flag HEAD commits touching `src/` or `tests/` without a `Task:` trailer |
| `--frontmatter` | opt-in | Validate the four governed frontmatter fields against the ledger graph (exits 3 on drift) |
| `--taxonomy` | yes | Enforce ADR `kind`/`semver`/id-prefix consistency (ADR-0.0.17) |
| `--chores-layout` | opt-in | Forbid `CHORE.md` / `acceptance.json` outside the canonical chore roots |
| `--unscoped-rules` | opt-in | Flag agent rules with `paths: "**"` or missing `paths:` outside `AGENTS.md` (ADR-0.0.20) |
| `--version` | opt-in | Validate version consistency across all version-bearing locations (`pyproject.toml`, `__init__.py`, README badge) |
| `--type-ignores` | opt-in | Fail on `# type: ignore[<code>]` under `src/` (ty does not honor the bracketed-code form — see GHI #197) |
| `--cli-alignment` | opt-in | Every `gz <verb>` reference in operator docs / features / skills must resolve to a registered parser verb |
| `--event-handlers` | opt-in | Every ledger event type must be claimed by a graph handler |
| `--validator-fields` | opt-in | Every validator `info.get(field)` lookup must have a matching graph writer |
| `--utf8-prefix` | opt-in | Forbid the `PYTHONUTF8=1`-as-`uv-run-gz`-prefix anti-pattern in docs / skills / features (GHI #275) |
| `--test-tiers` | opt-in | Forbid a third test tier under `tests/` (`integration`, `e2e`, `slow`, `bdd`) — runner boundary is the gate |
| `--pydantic-models` | opt-in | Governance classes use Pydantic `BaseModel` + `ConfigDict`, not `@dataclass` |
| `--class-size` | opt-in | Classes under `src/gzkit/` ≤300 lines unless explicitly waived |
| `--version-release` | opt-in | `pyproject.toml` version has a matching `vX.Y.Z` git tag |
| `--pool-adr-isolation` | opt-in | Pool ADRs never receive runtime-track lifecycle / gate events |
| `--behave-req-tags` | opt-in | Heavy-lane / Completed OBPI REQs have matching `@REQ-X.Y.Z-NN-MM` scenario tags under `features/` (GHI #323 lifecycle scope) |
| `--skill-alignment` | opt-in | Every CLI verb has a wielding skill (Tool / Skill / Runbook Alignment Invariant 1) |
| `--advisory-scorecard` | opt-in | Every `.gzkit/rules/*` file appears in the advisory-rules-audit scorecard |
| `--complexity-doctrine-links` | opt-in | ADR-0.0.27 complexity-doctrine citation link integrity (closes 2am-Scenario-2) |
| `--reconcile-freshness` | opt-in | Flag if no reconcile event has fired since HEAD (24-hour grace window) |
| `--insights-shape` | opt-in | Validate `.gzkit/insights/agent-insights.jsonl` records against the canonical `InsightRecord` schema (GHI #358) |
| `--instructions-files-budget` | opt-in | AGENTS.md / CLAUDE.md / `.claude/rules/*.md` must stay within per-file char budgets defined in `data/instructions_files_budget.json` (GHI #373) |
| `--adr-status-fresh` | yes | `docs/governance/GovZero/adr-status.md` must agree with on-disk ADR canon (GHI #322) |
| `--orientation-freshness` | opt-in | The SessionStart orientation hook + script must remain wired (GHI #341) |
| `--brief-headings` | opt-in | OBPI brief evidence sections must be H3, not H2 (GHI #238) |
| `--sensitivity` | opt-in | ADR-0.0.22 sensitivity-binding (auto-detect floor; escalate-not-escape against `data/security_surfaces.json`) |
| `--absorption-duplicates` | opt-in | Same opsdev source path across parent ADRs needs `paired_with:` frontmatter waiver (GHI #376) |
| `--evaluation-justify-binding` | opt-in | Fail-closed gate: `gz-justify` artifact required when evaluation scores are low (ADR-0.0.26) |
| `--audits` | opt-in | Run all four trust-doctrine pattern audits in one pass |

The `--allowlist-only` flag is a sub-modifier for `--unscoped-rules` —
it lists current allow-list entries and exits 0 without running the
full audit.

## Exit Codes

Follows the CLI doctrine 4-code map:

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All artifacts valid | — |
| 1 | User/config error or non-frontmatter validation error | Fix invocation or address reported errors |
| 2 | System/IO error | Check filesystem and retry |
| 3 | Frontmatter-ledger policy breach (drift) | Run `gz validate --frontmatter --explain <ADR>` then the suggested recovery command |
