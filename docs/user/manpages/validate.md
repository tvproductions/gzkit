# gz validate

Validate governance artifacts against schema rules.

## Usage

```bash
gz validate [--manifest] [--documents] [--surfaces] [--ledger]
            [--instructions] [--briefs] [--personas]
            [--interviews] [--decomposition]
            [--requirements] [--commit-trailers]
            [--taxonomy] [--chores-layout] [--distribution]
            [--bullet-retention] [--surface-weight] [--pointer-anchors]
            [--scenario-reachability] [--surface-fidelity]
            [--frontmatter [--adr <ID>] [--explain <ADR-ID>]]
            [--advisor-proof-binding] [--lock-handoff-coupling] [--qc-binding] [--fidelity-presence] [--vendor-manifest]
            [--setpoint-coherence] [--rendition-freshness]
            [--rendition-floor-coherence]
            [--invariant-coherence] [--brief-reconcile] [--router-tables]
            [--kind-invariance] [--req-kind-discipline] [--brief-command-shape] [--tautological-test-audit]
            [--closeout-proof]
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

### `--bullet-retention`

Enforces ADR-0.0.33 Invariant 1 (**tier-scoped** per the § Amendment 2026-06-03,
realized by OBPI-0.0.37-25): every bullet in
`docs/governance/advisory-rules-audit.md` classified **Mechanical** or
**Promotable** has its retention enforced according to its corpus tier.

The check reads the scorecard's pipe-delimited table, extracts the rule text
from each row, normalizes whitespace and leading markdown bullet markers, and
resolves each enforced bullet's **tier** from the append-only corpus store
(`.gzkit/corpus/<surface>.jsonl`). A bullet maps to the first corpus entry whose
text contains it; a bullet that maps to no corpus entry uses the conservative
**invariant** fallback. **Judgment** and **Ambiguous** bullets are not enforced.

| Tier | Retention contract | Fail-closed when |
|------|--------------------|------------------|
| `invariant` (and the unknown-tier fallback) | The Era-1 verbatim contract: the normalized bullet text MUST be a substring of the normalized per-turn surface corpus (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`). | The bullet is absent/altered in the rendered surface. |
| `compressible` | Retention is witnessed, not verbatim: the bullet's surface MUST carry a valid advisor-QC information-retention witness — the latest `rendition_advisor_verdict` ledger event for the surface, whose `arb-step-judge-*` receipt exists with `exit_status == 0` (the receipt the operator cites at Gate 5; ADR-0.0.39, OBPI-0.0.37-24). A reworded/combined compressible bullet that carries the witness does NOT fail. | No verdict event for the surface, the receipt is missing, or `exit_status != 0` — retention is unwitnessed. The compressible tier is not an unconditional escape from retention. |

A violation emits `ValidationError(type="bullet_retention")` naming the bullet,
its source classification, the tier-specific reason, and the governed recovery
step. Exit 3 on any violation; exit 0 when the surface is clean.

```bash
# Audit the per-turn surface against the advisory scorecard (tier-scoped)
uv run gz validate --bullet-retention
```

**Clean state:**

```
$ uv run gz validate --bullet-retention
Validated: bullet_retention

✓ All validations passed (1 scope).
$ echo $?
0
```

**Missing Mechanical bullet:**

```
$ uv run gz validate --bullet-retention
Validated: bullet_retention

❌ Validation failed with 1 error(s):

   → [bullet_retention] docs/governance/advisory-rules-audit.md
    Bullet-retention violation: 'Mechanical' bullet not found verbatim in
    per-turn surface.
      Bullet: 'use uv run for commands'
      Source: docs/governance/advisory-rules-audit.md
$ echo $?
3
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Surface is clean — every enforced bullet satisfies its tier-scoped retention contract | — |
| 3 (invariant tier) | One or more invariant-tier Mechanical/Promotable bullets absent from per-turn surface | Restore the missing bullet text verbatim to `AGENTS.md`, `CLAUDE.md`, or a `.claude/rules/*.md` file, then re-run |
| 3 (compressible tier) | One or more compressible-tier bullets lack a valid advisor-QC retention witness | Record the verdict with `uv run gz content advise-rendition <surface> --score <0.0-1.0> --explanation "<reasoning>"`, cite the receipt at Gate 5, then re-run |

### `--surface-weight`

Enforces ADR-0.0.33 Invariant 2: the per-turn surface corpus (`AGENTS.md`,
`CLAUDE.md`, `.claude/rules/**`) does not grow past the direction-binding
floor snapshot in `data/surface_weight_floor.json`.

Band constants (pinned by ADR-0.0.33 Decision):

| Band | Range | Exit Code |
|------|-------|-----------|
| Green | ≤ 1800 lines | 0 (clean) |
| Yellow | 1801–2200 lines | 3 unless an active waiver in `data/surface_weight_waivers.json` covers the delta |
| Red | > 2200 lines | 3 — no waiver dispensation |

The validator also detects **floor drift**: if the floor snapshot timestamp
predates the most recent `surface_weight_recalibrated` ledger event by more
than 24 hours, the check exits 3 citing drift. Floor recalibration is a
ledger event (`uv run gz adr emit-receipt` with `event
surface_weight_recalibrated`); silent floor mutation is never permitted.

```bash
# Check surface weight against the floor snapshot
uv run gz validate --surface-weight
```

**Clean state (corpus at or below floor):**

```
$ uv run gz validate --surface-weight
Validated: surface_weight

✓ All validations passed (1 scope).
$ echo $?
0
```

**Yellow-band violation (no active waiver):**

```
$ uv run gz validate --surface-weight
Validated: surface_weight

❌ Validation failed with 1 error(s):

   → [surface_weight] data/surface_weight_floor.json
    Surface weight in yellow band: 1850 lines (delta +82 from floor 1768).
    Yellow band (1801–2200) requires an active waiver.
    Add an entry to data/surface_weight_waivers.json or reduce the surface corpus.
$ echo $?
3
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Corpus at or below floor, or waiver covers yellow-band delta | — |
| 3 | Corpus in yellow band without active waiver | Add waiver entry to `data/surface_weight_waivers.json` or reduce corpus size |
| 3 | Corpus in red band (> 2200) | Reduce corpus size; no waiver dispensation in red band |
| 3 | Floor drift detected | Run `uv run gz adr emit-receipt` with `surface_weight_recalibrated` event, then update `data/surface_weight_floor.json` |

### `--pointer-anchors`

Enforces ADR-0.0.33 Invariant 3: every `> See [path#anchor]` blockquote
pointer in the per-turn surface corpus (`AGENTS.md`, `CLAUDE.md`,
`.claude/rules/**`) must resolve, and every destination must carry a
matching `<!-- lifted-from: <source-path>#<anchor> -->` back-pointer.

The validator parses each blockquote line containing the `See` keyword,
extracts every `(path#anchor)` markdown link target, then for each:

1. Confirms the destination file exists on disk.
2. Computes mkdocs-compatible heading slugs in the destination and asserts
   the anchor resolves to one.
3. Reads the destination content and asserts it contains a
   `<!-- lifted-from: -->` HTML comment (indicating it knows it carries
   lifted content from a forward pointer).

Any failed check emits a `ValidationError(type="pointer_anchors")` naming
both halves of the broken link: the source file plus line number, and the
unresolvable destination path/anchor or missing back-pointer.

Scope: only blockquote (`> ...`) lines containing the `See` keyword are
checked. Regular inline markdown links and unrelated blockquotes are
ignored — this matches the canonical `> See [...]` pointer style used
throughout `AGENTS.md` and the `.claude/rules/**` corpus.

```bash
# Check pointer integrity across the per-turn surface
uv run gz validate --pointer-anchors
```

**Clean state (all pointers resolve, every destination carries a back-pointer):**

```
$ uv run gz validate --pointer-anchors
Validated: pointer_anchors

✓ All validations passed (1 scope).
$ echo $?
0
```

**Unresolved anchor:**

```
$ uv run gz validate --pointer-anchors
Validated: pointer_anchors

❌ Validation failed with 1 error(s):

   → [pointer_anchors] AGENTS.md
    Pointer anchor unresolved: AGENTS.md:42 ->
    docs/governance/agent-contract-rationale.md#missing-section
    (no heading slugifies to 'missing-section' in
    docs/governance/agent-contract-rationale.md)
$ echo $?
3
```

**Missing back-pointer:**

```
$ uv run gz validate --pointer-anchors
Validated: pointer_anchors

❌ Validation failed with 1 error(s):

   → [pointer_anchors] AGENTS.md
    Missing back-pointer: destination
    docs/governance/agent-contract-rationale.md (referenced by
    AGENTS.md:42#stdlib-first-doctrine--rationale) lacks
    `<!-- lifted-from: -->` comment
$ echo $?
3
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All blockquote-See pointers resolve and every destination carries a back-pointer | — |
| 3 | One or more pointers unresolved (path missing or anchor not present) | Fix the link target or add the heading to the destination |
| 3 | Destination referenced by forward pointer lacks `<!-- lifted-from: -->` back-pointer | Add `<!-- lifted-from: <source-path>#<anchor> -->` to the destination file |

### `--scenario-reachability`

Enforces ADR-0.0.33 Invariant 4: every Mechanical/Promotable bullet in the
advisory scorecard (`docs/governance/advisory-rules-audit.md`) must be
reachable from at least one declared loading scenario in
`data/agent-control-surface-scenarios.json`.

**Era-1 behavior (registry absent):** The validator exits 0 and emits a
single advisory to stderr:

```
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
```

The registry is authored under ADR-0.0.34; registry-absent is a bootstrap
state, not drift.

**Era-2 behavior (registry present):**

1. Validates the registry against the declared JSON Schema (array of objects
   with `name: string` and `corpus: array[string]`). A schema violation exits 3.
2. For each Mechanical/Promotable bullet, checks that at least one scenario's
   `corpus` list includes a surface file containing the bullet. Orphan bullets
   emit `scenario-reachability: orphan bullet: <bullet_text>` warnings to
   stderr and exit 0 (advisory — escalation to fail-closed deferred to a
   follow-up `--strict` GHI per ADR-0.0.33 Decision).

```bash
# Era-1: check with no registry present
uv run gz validate --scenario-reachability
```

**Era-1 clean state (registry absent):**

```
$ uv run gz validate --scenario-reachability
$ echo $?
0
```

(Advisory line emitted to stderr, not stdout.)

**Era-2 schema violation:**

```
$ uv run gz validate --scenario-reachability

❌ Validation failed with 1 error(s):

   → [scenario_reachability] data/agent-control-surface-scenarios.json
    scenario-reachability: registry schema invalid: expected array, got dict
$ echo $?
3
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Registry absent (Era-1 advisory) or all bullets reachable (Era-2 clean) | — |
| 0 | Orphan bullets found (Era-2 advisory) | Review orphan warnings in stderr; fix coverage or await `--strict` escalation |
| 3 | Registry schema violation | Fix `data/agent-control-surface-scenarios.json` to match declared schema |

### `--vendor-manifest`

Validates `data/vendor-manifest.json` against `src/gzkit/schemas/vendor_manifest.json`
and checks that every declared `content_type_routes` entry maps to at least one vendor
mirror. Exits 3 when any registered content type is missing from the manifest or when
the manifest fails JSON Schema validation (ADR-0.0.34 OBPI-08).

**When to use:** After editing `data/vendor-manifest.json`, adding a new content type
to the registry, or verifying the render pipeline's routing is schema-consistent.

```bash
uv run gz validate --vendor-manifest
```

**Examples:**

```text
$ uv run gz validate --vendor-manifest
Validated: vendor_manifest
```

```text
$ uv run gz validate --vendor-manifest
❌ Validation failed with 1 error(s):

   → data/vendor-manifest.json
    Vendor manifest missing content_type_routes entry for: NewContentType
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Manifest validates clean | — |
| 3 | Schema violation or missing content-type route | Add the missing entry to `data/vendor-manifest.json` |

### `--setpoint-coherence`

Validates that every `(content_type, vendor)` pair declared in
`data/vendor-manifest.json` `content_type_routes` carries a legal declared
compression setpoint in `content_type_temperatures`. Legal tokens are `lite`,
`medium`, and `heavy`. Exits 3 when a routed pair has no declared setpoint, when
a declared token is illegal, or when the manifest is missing or malformed
(OBPI-0.0.37-20).

The setpoint is the compression target the authoring-time composer drives toward
(ADR-0.0.37 § Decision Re-Alignment, re-aimed mechanism part 2); this gate
asserts the declaration surface is coherent before the composer that consumes it
is built. Achieved byte size is an output, never a hand-tuned input.

**When to use:** After editing `content_type_routes` or
`content_type_temperatures` in `data/vendor-manifest.json`, or after adding a new
content type or vendor route.

```bash
uv run gz validate --setpoint-coherence
```

**Examples:**

```text
$ uv run gz validate --setpoint-coherence
Validated: setpoint_coherence
```

```text
$ uv run gz validate --setpoint-coherence
❌ Validation failed with 1 error(s):

   → data/vendor-manifest.json
    (Bullet, claude) is routed in content_type_routes but has no declared setpoint in content_type_temperatures; declare a compression target (['heavy', 'lite', 'medium']) for the pair (OBPI-0.0.37-20).
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Every routed pair has a legal declared setpoint | — |
| 3 | A routed pair lacks a setpoint, an illegal token, or the manifest is missing/malformed | Declare a legal setpoint (`lite`/`medium`/`heavy`) for the pair in `content_type_temperatures` |

### `--kind-invariance`

Validates that every ADR marked `kind: foundation` carries a substantive
`## Why foundation tier?` section in its design rationale. Foundation-kind ADRs
set system invariants and identity-shaping facts; the Why-foundation-tier
section explicitly states the architectural justification for foundation status
and articulates why this policy must survive across releases. Enforced under
ADR-0.0.35 (Foundation-Kind Doctrine).

**When to use:** After promoting a pool ADR to foundation kind, or as part of a
`gz check` validation sweep to audit tier-consistency.

```bash
uv run gz validate --kind-invariance
```

**Examples:**

```text
$ uv run gz validate --kind-invariance
Validated: kind_invariance
```

```text
$ uv run gz validate --kind-invariance
❌ Validation failed with 1 error(s):

   → docs/design/adr/foundation/ADR-0.0.35/ADR-0.0.35.md
    Foundation-kind ADR missing ## Why foundation tier? section
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All foundation ADRs have Why-foundation-tier section | — |
| 1 | Parsing or discovery error; foundation ADR missing the section | Add `## Why foundation tier?` section to the ADR and document the architectural justification |

### `--receipt-shape`

Validates every `obpi_receipt_emitted` event in `.gzkit/ledger.jsonl` against the
ADR-0.0.36 receipt-shape requirements. The cutoff date is read from the ADR-0.0.36
frontmatter `date:` field (currently 2026-04-26).

Three deprecated shapes are rejected on post-cutoff receipts:

1. `attestation_requirement: optional` — universal attestation is required; use `required`.
2. `obpi_completion` value without the `attested_` prefix (e.g., `completed`) — use
   `attested_completed`.
3. `attestor` matching `^agent:` (case-insensitive) — attestor must be a human identity.

**Pre-cutoff receipts with deprecated shapes** are handled as follows:

- If `data/historical_self_close_waivers.json` is present and the receipt ID appears
  in its `waivers` list → silent pass (waivered).
- If the waiver file is absent → warn-only, no policy-breach errors returned.
- If the waiver file is present but the receipt is not listed → fail-closed.

Pre-cutoff waivers are registered under OBPI-0.0.36-04.

**When to use:** Run after emitting new receipts, or as part of a governance sweep to
ensure the ledger contains no deprecated attestation shapes since the ADR-0.0.36 cutoff.
Also wired into `gz check`.

```bash
uv run gz validate --receipt-shape
```

**Examples:**

```text
$ uv run gz validate --receipt-shape
Validated: receipt_shape

✓ All validations passed (1 scope).
$ echo $?
0
```

```text
$ uv run gz validate --receipt-shape
Validated: receipt_shape

❌ Validation failed with 1 error(s):

   → [receipt_shape] obpi-receipt-abc123
    Post-cutoff receipt 'obpi-receipt-abc123' has deprecated attestor: 'agent:claude-code'
    (matches ^agent: pattern). Attestor must be a human identity per ADR-0.0.36.
    Recovery: re-emit the receipt with a human attestor.
$ echo $?
3
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All post-cutoff receipts use canonical shapes; pre-cutoff receipts are waivered or absent | — |
| 3 | Post-cutoff receipt has a deprecated shape, or pre-cutoff receipt is not waivered when a waiver file is present | Re-emit the receipt with the canonical shape, or register the legacy receipt ID in `data/historical_self_close_waivers.json` (OBPI-0.0.36-04) |

### `--surface-fidelity`

Composite scope: runs all four surface-fidelity invariants in declared order
(`bullet_retention` → `surface_weight` → `pointer_integrity` →
`scenario_reachability`) and aggregates their `ValidationError` lists. The
exit code is the worst of the four — if any constituent exits 3, the composite
exits 3. No masking.

**When to use:** Run after editing `AGENTS.md`, `CLAUDE.md`, or any file in
`.claude/rules/**` to verify the full fidelity doctrine in one pass. Also
wired into `gz check` (step "Surface fidelity") and the pre-commit cheap
subset (invariants 1, 2, 3 only — `--scenario-reachability` is CI-only in Era 1).

```bash
# Run the full composite
uv run gz validate --surface-fidelity
```

**Examples:**

```text
$ uv run gz validate --surface-fidelity
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
Validated: surface_fidelity
```

```text
$ uv run gz validate --surface-fidelity
Validated: surface_fidelity

❌ Validation failed with N error(s):

   →  docs/governance/advisory-rules-audit.md
    Bullet-retention violation: 'Mechanical' bullet not found verbatim in per-turn surface.
  Bullet: '<bullet text>'
  Source: docs/governance/advisory-rules-audit.md
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All four invariants clean | — |
| 1 | Non-policy-breach errors (e.g. pointer_anchors) | Fix unresolved lift pointers |
| 3 | Policy breach (bullet_retention or surface_weight violations) | Fix the flagged bullet or waive the surface weight per ADR-0.0.33 |

### `--distribution`

Static T0 distribution invariant audit (ADR-0.0.32-07). Verifies that every
file in a canonical surface tree (`src/gzkit/skills/`, `src/gzkit/rules/`,
`src/gzkit/personas/`, `src/gzkit/templates/`, and any surface tracked by
`data/distribution_baseline_manifest.json`) is wheel-deliverable — i.e.,
covered by a `[tool.hatch.build.targets.wheel] include:` glob in
`pyproject.toml` AND present in the baseline manifest.

The check is **purely static**: no wheel build, no `uv build` or `hatch build`
subprocess. Inputs are `pyproject.toml` (parsed via stdlib `tomllib`),
`data/distribution_baseline_manifest.json`, and on-disk file walks.

#### Drift classes

| Class | Meaning |
|-------|---------|
| `ON_DISK_NOT_INCLUDED` | File exists under a canonical surface tree but is not covered by any include glob in `pyproject.toml`. Resolution: extend the `include:` block. |
| `BASELINE_NOT_ON_DISK` | Baseline manifest names a file that does not exist on disk. Resolution: restore the missing file or remove the entry from `data/distribution_baseline_manifest.json`. |
| `ON_DISK_NOT_BASELINE` | File exists on disk and is covered by an include glob but is absent from the baseline manifest. Resolution: add the entry to `data/distribution_baseline_manifest.json`. |

#### Exit codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | No drift — all three inputs agree | — |
| 2 | System/IO error — `pyproject.toml` is malformed or missing, or baseline manifest is missing or unparseable | Fix the TOML/JSON syntax or restore the missing file |
| 3 | Policy breach — one or more drift violations detected | See per-violation report; extend include globs or update the baseline manifest |

#### Examples

```bash
# Run the distribution audit
uv run gz validate --distribution

# Machine-readable output
uv run gz validate --distribution --json
```

Clean state:

```
$ uv run gz validate --distribution
Validated: distribution

✓ All validations passed (1 scope).
$ echo $?
0
```

Drift detected (ON_DISK_NOT_BASELINE):

```
$ uv run gz validate --distribution
Validated: distribution

❌ Validation failed with 1 error(s):

   → [distribution] src/gzkit/skills/new-skill/SKILL.md
    ON_DISK_NOT_BASELINE: 'src/gzkit/skills/new-skill/SKILL.md' exists on disk
    and is covered by a wheel include glob but is NOT in the baseline manifest.
    Resolution: add to data/distribution_baseline_manifest.json.
$ echo $?
3
```

Malformed `pyproject.toml` (system error):

```
$ uv run gz validate --distribution
distribution-audit: cannot parse pyproject.toml: ...
$ echo $?
2
```

### `--regenerate`

Rewrite `data/distribution_baseline_manifest.json` from on-disk canonical surface
truth. Always combine with `--distribution`.

The regenerator is the canonical one-command recovery for `ON_DISK_NOT_BASELINE`
drift — new canonical surface files added after the baseline was frozen.
Symmetric to `gz register-adrs` for the ADR status index (per
`.gzkit/rules/governance-core.md` § ADR status index regeneration).

The regenerator:
1. Walks each surface root tracked by the manifest (`src/gzkit/skills/`, `rules/`, etc.)
2. Applies per-surface classifiers to skip `package_only` and `runtime_state` files
3. Writes the new manifest atomically via temp-file-and-rename
4. Appends a `distribution_baseline_regenerated` ledger event capturing hash before/after

After regeneration, `gz validate --distribution` should exit 0 on a clean tree.

#### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Regeneration completed; `data/distribution_baseline_manifest.json` updated |
| 2 | System/IO error reading `pyproject.toml` or the manifest |

#### Examples

```bash
# Before: validate fails with ON_DISK_NOT_BASELINE errors
uv run gz validate --distribution

# Fix: regenerate the baseline from on-disk truth
uv run gz validate --distribution --regenerate

# After: validate exits 0 on a clean tree
uv run gz validate --distribution
```

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

### `--doc-surface-parity`

Fail-closed if any `.md` file exists under `docs/user/commands/`.
That directory was decommissioned in favour of the canonical
`docs/user/manpages/` surface (GHI #418). Included in `--audits`
and `gz check`.

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

### `--orphaned-implementation`

Detects the silent broken state where a prior session claimed an OBPI
lock, made allowed-path edits, then force-released the lock without
running `gz obpi complete` (GHI #438). Walks every brief under
`docs/design/adr/**/obpis/`; for each whose frontmatter `status:` is
not `Completed`/`attested_completed`/`validated`/`Withdrawn`, the audit
inspects the brief's `## Allowed Paths` and the ledger:

1. Find the latest `obpi_lock_claimed` for this OBPI.
2. If any `obpi_completion_*` event exists at or after that claim, the
   brief is considered ceremonialized — skip.
3. Otherwise, look for an `obpi_lock_released` with `force: true` after
   the claim.
4. If a force-release exists, scan `artifact_edited` events between
   claim and release for paths covered by the brief's allowed-paths
   (literal, directory-prefix, or glob-root match).
5. If matches exist, the brief is fingerprinted as
   *implementation landed without ceremony*.

Opt-out marker (binding): an intentional implementation-without-ceremony
must place the line
`<!-- gz-validate-skip: orphaned-implementation GHI-<num> -->`
anywhere in the brief body and file a tracking GHI explaining why. The
marker shape follows the GHI #432 speculative-skip convention so both
validators share one opt-out vocabulary.

```bash
# Audit every non-completed brief against the ledger window
gz validate --orphaned-implementation

# Machine-readable per-brief records
gz validate --orphaned-implementation --json
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | No orphaned implementations, or all flagged briefs carry the skip marker | — |
| 3 | One or more non-completed briefs have lock-claim + force-release + allowed-path edits without `obpi_completion_*` | Run `uv run gz obpi pipeline <OBPI-ID> --from=verify` to finish the ceremony, or — if the implementation is intentional without ceremony — file a tracking GHI and add the skip marker to the brief body |

Included in `gz validate --audits` and `gz check` aggregate passes.

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

### `--intrinsic-attestation`

Validates every `intrinsic-complexity-attestation` event in the ledger against the canonical
schema (OBPI-0.0.29-07). Checks required string fields are non-empty, `crossing_band` is one
of `block`, `warn`, `advise`, and `crossing_value` is numeric. Returns no errors for a missing
ledger file (fail-open when attestation has never been used).

```bash
# Validate all intrinsic-complexity-attestation events in the ledger
gz validate --intrinsic-attestation
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All events valid or no events present | — |
| 1 | One or more events have missing/invalid fields | Inspect the ledger event and re-run `gz complexity advise --attest-intrinsic` |

### `--advisor-proof-binding`

Defense-in-depth backstop for the verdict <-> proof binding (ADR-0.0.29 /
OBPI-0.0.29-08). Model-layer enforcement (OBPI-0.0.29-01: `Field(min_length=1)`
on `AdvisorDiagnosis.proof`) and engine-layer enforcement (OBPI-0.0.29-02:
`EngineError` raised before model instantiation when proof is unavailable)
prevent empty-proof diagnoses at runtime; this validator is the gate-time
defense against a future regression in either lower layer.

Three scan scopes:

1. **Fixture scope** — walks `tests/fixtures/advisor/*.json`, asserts each
   diagnosis fixture has non-empty `proof`. A speculative-marker escape
   (`"_negative_case": true` at the fixture's top level) skips fixtures
   explicitly authored as negative-case tests of the empty-proof rejection.
2. **Ledger scope** — reads `.gzkit/ledger.jsonl`, finds
   `intrinsic-complexity-attestation` events whose payload references a
   diagnosis id (via the OBPI-07 event shape), cross-checks that the cited
   diagnosis carries non-empty `proof`.
3. **Schema scope** — loads `src/gzkit/schemas/advisor_diagnosis.json` and
   asserts `properties.proof.minItems >= 1`.

```bash
# Run the binding audit; integrates with --all and gz check
gz validate --advisor-proof-binding
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All scopes pass (vacuous when fixtures/ledger absent) | — |
| 1 | One or more diagnoses lack non-empty `proof` | Inspect named fixture/event/schema and restore the binding (or remove the empty-proof artifact) |

### `--lock-handoff-coupling`

Ledger-replay validator that fail-closes on any `obpi_lock_released` event
(post-OBPI-02 cutover) that violates the token-block discipline
(ADR-0.0.41 / OBPI-0.0.41-04). Enforced on the default `gz check` pipeline.

Four failure conditions:

1. **Missing `handoff_path`** — the release event carries no register-entry
   reference; event timestamp, OBPI id, and agent are surfaced in the error.
2. **Nonexistent file** — `handoff_path` references a path absent on disk.
3. **Predated timestamp** — the handoff document's frontmatter `timestamp`
   predates the matching `obpi_lock_claimed` event for the same
   `(obpi_id, agent)` pair.
4. **Missing minimum-information field** — the handoff document is missing any
   of the four Sub-Invariant 2 fields: `last_lock_event_timestamp`,
   `last_commit_sha`, `branch`, or `## Decisions Made` body section.

Cutover detection: the `obpi_receipt_emitted` event for
`OBPI-0.0.41-02-claim-release-safety-primitives` in the ledger; events before
that timestamp are grandfathered. When no cutover event exists, all events
are grandfathered (validator exits 0).

```bash
# Run on the live ledger (clean ledger exits 0)
gz validate --lock-handoff-coupling
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All post-cutover releases carry valid handoff_path and pass min-info checks | — |
| 3 | One or more releases violate the coupling invariant | Run `gz validate --lock-handoff-coupling` for diagnostic output; use `gz-session-handoff` to author the missing register entry before releasing the lock |

### `--qc-binding`

Behavioral QC-step binding audit (ADR-0.0.73 / OBPI-0.0.73-02). Flags any
bound QC step that passes its own negative-control fixture (a hollow step) or
exhibits one of the canonical theater signatures. The audit also classifies
advisory steps that self-register (e.g. `gz adr evaluate`), so a checker that
presents shape-graded scores as authoritative truth is a binding-mismatch
finding rather than a silent pass.

Detection is **behavioral**, not declarative: each `bound` step must fail its
registered negative control; a step that passes is theater regardless of its
docstring. Theater-signature detection is static, via the step's `theater_flags`
field; negative-control execution runs the step against a declared fixture.

The theater signatures (the first six calibrated on the ADR-0.0.37 facade; the
seventh on the GHI #624 evaluator defect, OBPI-0.0.73-07):

1. **mtime-where-name-says-content** — checks file mtime instead of content
2. **empty-input-passes** — always passes on empty or absent input
3. **copy-vs-self** — tautological fixture (fixture == expected)
4. **fixture-only** — runs only against its own fixture, never the real project
5. **skip-if-PASS** — short-circuits when a prior artifact is already PASS
6. **prose-graded-by-nothing** — emits prose never machine-verified
7. **shape-graded-not-substance** — renders an authoritative truth-score from
   prose shape or keyword presence rather than decision substance

Wired into the default `gz check` pipeline (fail-closed; exit 3 on findings).

```bash
uv run gz validate --qc-binding
uv run gz validate --qc-binding --json
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | No theater detected | — |
| 3 | Theater found — one or more bound steps exhibit a signature or pass their NC | Inspect findings; implement a genuine check that fails for the right reason; register an honest negative-control via `register_negative_control` (OBPI-06 fills in all existing steps) |

### `--fidelity-presence`

Fidelity-presence enforcement (ADR-0.0.73 / OBPI-0.0.73-08), mechanizing
Boundary Invariant #4: every non-pool ADR Decision must carry a parseable
`## Fidelity Assertions` block — runnable commands that exercise the ADR's
thesis against the real system. Without one, "VALIDATED = thesis exercised" is
false for that ADR (the block-less bypass the OBPI-04 adversarial audit
surfaced).

The scope walks every non-pool ADR Decision (`docs/design/adr/**/ADR-*.md`
whose stem matches its package directory; the `pool/` tree and
`ADR-CLOSEOUT-FORM.md` sidecars are excluded) and fails closed (exit 3) on any
whose block is absent, empty, or malformed. Pre-existing block-less ADRs are
enumerated in `data/fidelity_presence_grandfather.json` and pass — the
`sensitivity_floor_grandfather.json` cutover precedent: visible debt, fail-closed
on NEW ADRs only. A new block-less ADR (absent from the grandfather file) fails
closed; do **not** add new entries to silence a fresh violation. The ADR
template (`.gzkit/templates/adr.md`) seeds the stub so new ADRs carry the block
by construction.

Wired into the default `gz check` pipeline (fail-closed; exit 3 on findings).

```bash
uv run gz validate --fidelity-presence
uv run gz validate --fidelity-presence --json
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Every non-pool ADR Decision carries a block (or is grandfathered) | — |
| 3 | One or more non-pool ADR Decisions lack a parseable `## Fidelity Assertions` block | Add a block with at least one claim/command/expected-exit row (see the stub in `.gzkit/templates/adr.md`); re-run `uv run gz validate --fidelity-presence` |

### `--closeout-proof`

Derived closeout-proof view (ADR-0.0.69 / OBPI-0.0.69-03). Recomputes per-REQ
proof for in-closeout ADRs over the three REQ-kind channels every run. Never
reads proof from a stored artifact — proof is always live-computed.

**In-scope ADRs:** those with an active ceremony state file at
`.gzkit/ceremonies/<ADR-ID>.ceremony.json` where `completed_at` is null.

**Three proof channels:**

- **BEHAVIOR** — the REQ must have at least one `@covers("REQ-ID")`-decorated
  test in `tests/`. Missing decorator → unproven.
- **SUPPORT** — the REQ text must cite both a recognized ledger event type
  and a `gz validate --<scope>` command. The ledger must contain that event
  type AND the scope must dispatch clean (exit 0).
- **STRUCTURAL-FENCE** — the parent ADR's `## Boundary Invariants` section
  must contain an anchor for the REQ ID. Missing anchor → unproven.

REQs with no inline `[kind]` tag are always unproven — explicit tags are
required at closeout (ruling 6.2-A).

For failed SUPPORT REQs, the output prints the exact re-run command
(`uv run gz validate --<scope>`) so the failing channel can be reproduced in
one paste. Full stderr inlining is out of scope (ruling 6.2-A).

```bash
# Recompute per-REQ proof for all in-closeout ADRs
uv run gz validate --closeout-proof

# JSON output for machine consumption
uv run gz validate --closeout-proof --json
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All in-closeout ADR REQs are proven across all three channels | — |
| 2 | Dispatch I/O error (validator scope could not be invoked) | Check `gz validate` availability and retry |
| 3 | Any REQ is unproven | Add `@covers` decorator, fix SUPPORT citation, or add Boundary Invariants anchor |

This scope is included in the `gz check` default pipeline (memoized per scope
per run — ruling 6.1-A). The ceremony gate `_gate_closeout_proof` on the
`EXECUTE→ATTESTATION` edge calls this view directly; an unproven REQ blocks
the ceremony's advance to attestation.

### `--rendition-freshness`

Fail-closed when the corpus for a surface has mutated after its committed rendition
(corpus↔rendition drift). Scans `.gzkit/renditions/<surface>/<consumer>.md` artifacts
and compares each against the corresponding corpus at `.gzkit/corpus/<surface>.jsonl`
using file modification timestamps. Emits `composition_drift_detected` on drift.

Runs in the default `gz check` build (OBPI-0.0.37-22).

**Usage:**

```bash
gz validate --rendition-freshness
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All renditions are at least as recent as their corpus | — |
| 3 | Corpus mutated after committed rendition | Run `gz content compose <surface>` and attest |

**When to use:** After `gz content remember` appends a corpus entry, before `gz agent sync
control-surfaces`, or to diagnose a failing `gz check` Rendition freshness step.

**Related:** ADR-0.0.37 (CMS pipeline), OBPI-0.0.37-22 (this gate), `--invariant-coherence`.

### `--rendition-floor-coherence`

Fail-closed when a committed rendition omits an invariant-tier corpus entry. For every
`.gzkit/renditions/<surface>/<consumer>.md` artifact, asserts that each `tier: invariant`
entry of the surface's corpus (`.gzkit/corpus/<surface>.jsonl`) appears **verbatim** in the
rendition text. This is the content witness that `--rendition-freshness` (a timestamp
comparison) does not perform: it proves the committed rendition actually carries canon's
invariant floor, not merely that it is newer than the corpus. Emits
`composition_drift_detected` naming the missing entry ids on violation.

Runs in the default `gz check` build (GHI #623, corrective to ADR-0.0.37).

**Usage:**

```bash
gz validate --rendition-floor-coherence
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Every committed rendition carries its corpus invariant floor verbatim | — |
| 3 | A rendition omits one or more invariant-tier corpus entries | Run `gz content compose <surface>` with a candidate that includes every invariant entry verbatim, attest, and recommit the rendition |

**When to use:** Before attesting an ADR-0.0.37 closeout, or to prove a committed rendition
genuinely derives canon's invariants rather than passing a timestamp-only freshness check.

**Related:** ADR-0.0.37 (CMS pipeline), GHI #623 (corrective gate), `--rendition-freshness`,
`--invariant-coherence`.

### `--invariant-coherence`

Diff deterministic playback of the committed rendition against the committed rendered
surface (`AGENTS.md`). Fails closed (exit 3) on drift; emits `composition_rendered`
on every run (when a committed rendition exists); additionally emits
`composition_drift_detected` on drift.

Re-pointed in OBPI-0.0.37-22 from registry-re-render byte-compare to
rendition-playback-vs-committed-surface diff. Bootstrap-safe: exits 0 when no
committed rendition exists.

**Usage:**

```bash
gz validate --invariant-coherence
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Committed rendition matches AGENTS.md (or no rendition yet) | — |
| 3 | Playback of committed rendition differs from committed AGENTS.md | Run `gz content compose AGENTS.md` and attest, or `gz agent sync control-surfaces` to replay |

**Related:** ADR-0.0.37 (constitutional invariant composition), OBPI-0.0.37-22
(rendition playback gate), `--rendition-freshness`.

### `--brief-reconcile`

Validates the OBPI brief corpus against project shape across five drift dimensions. Detects:
(1) OBPI frontmatter incoherence, (2) lane mismatches between frontmatter and body,
(3) scaffold-template defaults that were never replaced, (4) missing or orphaned brief files,
and (5) parent ADR/OBPI reference drift. Fail-closed (exit 3) when any dimension detects drift.

**Usage:**

```bash
gz validate --brief-reconcile
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Brief corpus clean across all five dimensions | — |
| 3 | Drift detected in one or more briefs | Inspect the error message and update the affected brief's frontmatter, body structure, or parent references |

**Related:** OBPI-0.0.37-05 (brief reconciliation engine).

### `--router-tables`

Audits the six namespace-router skills authored under ADR-0.27.0 (`gz-workflow`,
`gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) plus any other
skill whose body carries a `| Intent | Skill |` intent-to-skill markdown table. Two
directional invariants:

1. **Routed slug resolves.** Every routed-skill cell (the slug wrapped in backticks in
   the right column of an intent table) must resolve to a real canonical skill at
   `.gzkit/skills/<slug>/SKILL.md`. Fail-closed (`router_tables` type, exit 3) — a
   router pointing at a non-existent skill is a structural break.
2. **Concrete skill is reachable.** Every concrete (non-router) canonical skill must be
   routed from at least one router. Advisory (`router_tables_coverage` type, exit 1) —
   surfaces coverage gaps without blocking `gz check`.

**Usage:**

```bash
gz validate --router-tables
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Every routed slug resolves AND every concrete skill is router-reachable | — |
| 1 | One or more concrete skills are not routed (advisory) | Route the orphaned skill under the appropriate router, or accept the coverage gap |
| 3 | A router routes an intent to a slug with no canonical SKILL.md | Fix the routed slug typo, or author the missing skill before the router edits land |

**Related:** ADR-0.27.0 / OBPI-0.27.0-03 (router-tables validator).

### `--req-kind-discipline`

Enforces the ADR-0.0.59 REQ kind discipline: every REQ in an OBPI brief's `## Acceptance
Criteria` must carry exactly one `[BEHAVIOR]`, `[SUPPORT]`, or `[STRUCTURAL-FENCE]` kind
tag, and each kind must satisfy its proof-channel requirement.

Rules enforced:

1. **Mixed-state fails closed** — a brief with some tagged and some untagged REQs exits 3.
   All-untagged legacy briefs pass (grandfathered mode).
2. **Per-kind proof-citation gaps fail closed:**
   - `[BEHAVIOR]` REQ without `tests/**` in the brief's `## Allowed Paths` → exit 3.
   - `[SUPPORT]` REQ without both a `gz validate --` scope reference and a ledger event
     keyword in the REQ text → exit 3. Citations naming a recognized concrete event type
     (e.g. `artifact_edited`) additionally enable closeout-time proof resolution; generic
     keyword citations stay green here but resolve unproven at closeout.
   - `[STRUCTURAL-FENCE]` REQ when the parent ADR has no `## Boundary Invariants` → exit 3.

**SUPPORT-channel proof semantics (ADR-0.0.69 / OBPI-0.0.69-01):**

The SUPPORT proof channel (`LEDGER_PLUS_VALIDATOR`) resolves a real per-REQ
`proof_status` instead of the former always-advisory placeholder. A SUPPORT REQ
proves only when **both** hold:

1. **Cited ledger event found** — the ledger contains an event of the type the
   REQ cites (e.g. `artifact_edited`).
2. **Cited validator exits 0** — the cited `gz validate --<scope>` dispatches
   in-process and reports no errors.

Either miss fail-closes to `unproven-support`; a cited scope that would re-enter
req-kind or closeout-proof resolution is not dispatched and resolves to
`unproven-recursion-fence`. The split is authoring-time vs closeout-time: this
validator (`--req-kind-discipline`) checks **citation shape** at authoring time
(a Draft brief whose cited events do not exist yet stays green); the resolved
proof status is consumed fail-closed at ADR closeout (the derived closeout-proof
view, OBPI-0.0.69-03).

**Usage:**

```bash
gz validate --req-kind-discipline
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All tagged REQs pass per-kind checks; or all briefs are all-untagged | — |
| 3 | Mixed-state brief or proof-citation gap | Add `[kind]` tags and citations per `.gzkit/rules/tests.md` § REQ Scope Discipline |

**STRUCTURAL-FENCE-channel proof semantics (ADR-0.0.69 / OBPI-0.0.69-02):**

The STRUCTURAL-FENCE proof channel (`PARENT_ADR_INVARIANT`) resolves a real per-REQ
`proof_status` instead of the former always-advisory `"grandfathered"` placeholder.
A STRUCTURAL-FENCE REQ proves only when the parent ADR carries a
`## Boundary Invariants` heading:

- **Anchor found** → `"pass"`.
- **Anchor absent** → `"unproven-fence"` (fail-close — never `"grandfathered"` or
  advisory). This applies whether or not a `project_root` is available at resolution
  time; absent anchor = unproven, always.

`"unproven-fence"` is a fail-closed status: it is NOT counted in `grandfathered_reqs`
(advisory-only REQs). Unlike `"advisory-support"` (legacy SUPPORT callers without
`project_root`), there is no advisory fallback for STRUCTURAL-FENCE.

**Related:** ADR-0.0.59 / OBPI-0.0.59-02 (req-kind-discipline validator).
See `docs/governance/req-scope-discipline.md` for the full three-kind taxonomy doctrine.

### `--brief-command-shape`

Enforces the OBPI-0.0.63-07 brief Verification contract: every fenced command in a
brief's `## Verification` block must be a single-program, shell-less invocation
(`shlex.split`-parseable argv with no `&&`, `||`, `|`, `;`, `$(...)`, or redirects).
Compound commands fail at authoring time so the mismatch with the shell-less pipeline
runtime (GHI #415, GHI #550) is caught before the verify stage.

Rules enforced:

1. **Compound commands fail closed** — any `## Verification` fenced command containing
   `&&`, `||`, `|`, `;`, `$(...)`, or shell redirects exits 3. Reports the offending brief
   and command with a "rewrite as separate single-program lines" message.
2. **Data operators exempt** — operators inside quoted arguments (e.g. `python -c "a | b"`)
   are not flagged; the BI-1 classifier (`brief_commands.is_shell_less_executable`) correctly
   distinguishes data from syntax.

**Usage:**

```bash
gz validate --brief-command-shape
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All Verification commands are single-program shell-less | — |
| 3 | One or more non-shell-less commands found | Rewrite as separate `uv run …` lines per authoring guidance in `.gzkit/templates/obpi.md` |

**Related:** ADR-0.0.63 / OBPI-0.0.63-07 (verify-stage-command-shape-gate). GHI #550.

### `--tautological-test-audit`

Enforces the ADR-0.0.59-04 tautological-test drift gate: the count of filesystem-shaped
operations co-occurring with assertions in `tests/**` must not exceed the baselined count
plus waived count. Fails closed (exit 3) when drift is detected.

**Drift gate formula:** `current_count > baseline_count + waived_count` → exit 3.

**Scope semantics:**

- Scanner walks all `.py` files under `tests/**` via AST.
- A _tautological test operation_ is a co-occurrence of a filesystem-shaped op
  (`open()`, `Path.read_text()`, `os.path.*`, etc.) and an assertion statement
  (`self.assert*` or bare `assert`) within the same function body.
- Baseline is persisted at `data/tautological_test_baseline.json`.
- Waivers are persisted at `data/tautological_test_waivers.json` (rationale-key indirection).
- The waivers file itself is unconditionally excluded from the scan (hardcoded
  self-exemption — the file that governs exemptions cannot be subject to the gate it governs).

**Usage:**

```bash
gz validate --tautological-test-audit
```

**Exit codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Current count ≤ baseline + waivers | — |
| 3 | Current count > baseline + waivers (drift detected) | Apply a disposition from the scan output, update baseline via the chore workflow, or add a waiver entry with rationale key |

**Waiver file (`data/tautological_test_waivers.json`):**

```json
{
  "default_rationale": {
    "my-rationale-key": "Explanation of why this file is exempt"
  },
  "file_waivers": {
    "tests/path/to/test_file.py": ["my-rationale-key"]
  }
}
```

Each entry in `file_waivers[file_path]` represents one waived operation for that file.

**Proposing dispositions:** The scanner emits one of four suggested dispositions per operation:

| Disposition | Meaning |
|-------------|---------|
| `convert` | Rewrite as a behavior test (inject state, assert on extracted value) |
| `replace-with-ledger` | Use ledger queries or `gz adr emit-receipt` instead of reading files |
| `fold-to-validator` | Delegate to `gz validate --<scope>` and assert exit code |
| `keep-as-fixture` | Legitimate fixture pattern in `setUp`/`tearDown` — no change needed |

**Related:** ADR-0.0.59-04 / OBPI-0.0.59-04 (decommission-tautological-tests chore).
See `.gzkit/chores/decommission-tautological-tests/CHORE.md` for the operator workflow.

### `--task-envelope-coherence`

Validates TASK attribution coherence across the four discovery channels (ADR-0.0.64 / OBPI-04).
Fail-closed (exit 3) on three Heavy-fail signatures:

- **(a) Attribution drift** — worklog events (`artifact_edited`, `gate_checked`, etc.) emitted
  under an active TASK with no `task_id` field in the ledger.
- **(b) Subdivision skipped** — a completed OBPI has only `seq=01` TASKs across all REQs and no
  `req_atomic` exemption declared in brief frontmatter.
- **(c) Layer-drift** — different TASK IDs declared for the same OBPI across the frontmatter
  `tasks:` channel and the ledger `task_id` channel.

**`req_atomic` exemption:** REQs listed under `req_atomic: list[str]` in brief frontmatter are
exempt from signature (b). When `req_atomic` covers every REQ in the brief, the check suppresses
entirely for that OBPI. This is the sole mechanical bypass for signature (b) — no CLI flag, env
var, or config file can override it.

**Historical bootstrap boundary:** rows at or before `2026-05-30T14:44:00+00:00` are treated as
pre-enforcement recovery history. The validator does not rewrite ledger history; it enforces the
three signatures prospectively after that epoch.

```bash
gz validate --task-envelope-coherence
```

**Exit codes:** 0 = clean, 3 = policy breach (Heavy lane).

**Related:** ADR-0.0.64 / OBPI-0.0.64-04. Use `gz task envelope diagnose <OBPI-ID>` to inspect
per-channel TASK declarations when layer-drift blocks a closeout.

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

### `--complexity-thresholds`

Enforces the ADR-0.0.28 complexity-thresholds rule body shape. Loads `.gzkit/rules/complexity-thresholds.json` via OBPI-0.0.28-02's `load_threshold_table`, which fail-closes (Pydantic `ValidationError`) on: missing `block` band per metric, percentile outside the canonical `{50, 75, 90, 95, 99}` enum, trigger-semantic outside `{block, warn, advise}`, missing percentile + absolute pairing, or unparseable citation tuple. The validator also asserts every canonical metric (the twelve metrics from `gzkit.complexity.measurement.CANONICAL_METRICS`) has at least one band in the loaded table. When the rule body declares the `## Bootstrap absolutes` carve-out section, the validator emits a `complexity_thresholds_bootstrap_mode` warning to operator-facing diagnostic — informational, non-policy-breach — naming the GHIs (#404, #405) that track resolution of the underlying upstream defects.

```bash
# Audit the threshold table is well-formed
gz validate --complexity-thresholds
```

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Rule body parses; every canonical metric has at least one band; citation tuple round-trips | — |
| 3 | Loader fail (missing block band, off-enum percentile, malformed citation, etc.) or canonical metric coverage gap | Re-author the rule body to match the schema; consult ADR-0.0.28 § Threshold table shape for the worked example |

Included in `gz check` (step "Complexity-thresholds") and runnable as `gz validate --complexity-thresholds` directly. The bootstrap-mode warning surfaces in operator output but does not fail the build — the carve-out is one-shot, named per metric in the rule body, and exempts portability checks against bootstrap rows until the upstream defect resolves.

## Scopes Reference

The following table catalogs every audit scope the `gz validate` surface
exposes. Scopes marked **default** run when no flag is supplied; the rest are
opt-in. Each scope can be invoked individually for focused verification or as
part of `gz validate --audits` / `gz check` aggregate passes.

| Scope flag | Default? | Purpose |
|------------|----------|---------|
| `--manifest` | yes | Validate `.gzkit/manifest.json` against the manifest schema |
| `--documents` | yes | Validate governance docs (PRDs, constitutions, ADRs); OBPI briefs are owned by `--briefs` |
| `--surfaces` | yes | Validate control-surface existence, frontmatter shape, and canonical sync parity |
| `--ledger` | yes | Validate ledger integrity (event ordering, payload schema, append-only invariant) |
| `--instructions` | yes | Validate agent-instruction surfaces (`AGENTS.md`, `CLAUDE.md`, hooks) |
| `--briefs` | yes | Validate OBPI briefs with lifecycle-aware authored/completed gates |
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
| `--line-endings` | opt-in | Fail closed on CRLF line endings in tracked text surfaces, or a `.gitattributes` missing the `* text=auto eol=lf` LF-normalization rule (GHI #570) |
| `--test-tiers` | opt-in | Forbid a third test tier under `tests/` (`integration`, `e2e`, `slow`, `bdd`) — runner boundary is the gate |
| `--pydantic-models` | opt-in | Governance classes use Pydantic `BaseModel` + `ConfigDict`, not `@dataclass` |
| `--class-size` | opt-in | Classes under `src/gzkit/` ≤300 lines unless explicitly waived |
| `--version-release` | opt-in | `pyproject.toml` version has a matching `vX.Y.Z` git tag |
| `--pool-adr-isolation` | opt-in | Pool ADRs never receive runtime-track lifecycle / gate events |
| `--behave-req-tags` | opt-in | Heavy-lane / Completed OBPI REQs have matching `@REQ-X.Y.Z-NN-MM` scenario tags under `features/` (GHI #323 lifecycle scope) |
| `--skill-alignment` | opt-in | Every CLI verb has a wielding skill (Tool / Skill / Runbook Alignment Invariant 1) |
| `--advisory-scorecard` | opt-in | Every `.gzkit/rules/*` file appears in the advisory-rules-audit scorecard |
| `--complexity-doctrine-links` | opt-in | ADR-0.0.27 complexity-doctrine citation link integrity (closes 2am-Scenario-2) |
| `--complexity-thresholds` | opt-in | ADR-0.0.28 complexity-thresholds rule body shape + canonical-metric coverage |
| `--reconcile-freshness` | opt-in | Flag if no reconcile event has fired since HEAD (24-hour grace window) |
| `--insights-shape` | opt-in | Validate `.gzkit/insights/agent-insights.jsonl` records against the canonical `InsightRecord` schema (GHI #358) |
| `--instructions-files-budget` | opt-in | AGENTS.md / CLAUDE.md / `.claude/rules/*.md` must stay within per-file char budgets defined in `data/instructions_files_budget.json` (GHI #373) |
| `--agents-md-map-conformance` | opt-in | AGENTS.md template + rendered shape conformance: four criteria (paragraph <=5 lines or binding-bullet marker; no prohibited subsection titles; relative links resolve with anchors; rendered AGENTS.md within budget). Tables and code fences exempt from criterion (a). Hard-rejection exit 3 with `/gz-context-diet` remediation pointer (ADR-0.0.54 / OBPI-0.0.54-03) |
| `--adr-status-fresh` | yes | `docs/governance/GovZero/adr-status.md` must agree with on-disk ADR canon (GHI #322) |
| `--session-green-gate` | opt-in | `.pre-commit-config.yaml` must declare a `stages: [pre-push]` hook running `gz check`; exits 3 when absent, unparseable, or missing — fail-closed floor (ADR-0.0.68 / OBPI-0.0.68-02) |
| `--orientation-freshness` | opt-in | The SessionStart orientation hook + script must remain wired (GHI #341) |
| `--brief-headings` | opt-in | OBPI brief evidence sections must be H3, not H2 (GHI #238) |
| `--brief-cross-references` | opt-in | Bare `OBPI-X.Y.Z-NN` / `ADR-X.Y.Z` identifiers in briefs must resolve to on-disk artifacts (GHI #436) |
| `--brief-demo-section` | opt-in | Heavy-lane CLI-shipping briefs must carry a `## Demo` H2 section so the closeout walkthrough does not fall back to `--help` (GHI #431) |
| `--sensitivity` | opt-in | ADR-0.0.22 sensitivity-binding (auto-detect floor; escalate-not-escape against `data/security_surfaces.json`) |
| `--absorption-duplicates` | opt-in | Same opsdev source path across parent ADRs needs `paired_with:` frontmatter waiver (GHI #376) |
| `--orphaned-implementation` | yes | Non-completed OBPI with lock-claim + force-release + allowed-path edits and no `obpi_completion_*` is a silent broken state (GHI #438) |
| `--evaluation-justify-binding` | opt-in | Fail-closed gate: `gz-justify` artifact required when evaluation scores are low (ADR-0.0.26) |
| `--intrinsic-attestation` | opt-in | Validate `intrinsic-complexity-attestation` ledger events against canonical schema (OBPI-0.0.29-07) |
| `--advisor-proof-binding` | opt-in | Verdict <-> proof binding audit across fixtures, ledger-cited diagnoses, and JSON Schema (OBPI-0.0.29-08) |
| `--lock-handoff-coupling` | opt-in | Ledger-replay audit: every post-OBPI-02 obpi_lock_released event must carry a valid handoff_path (ADR-0.0.41) |
| `--closeout-proof` | opt-in | Derived closeout-proof view: recomputes per-REQ proof over three live channels (BEHAVIOR/SUPPORT/STRUCTURAL-FENCE) for in-closeout ADRs; exit 3 on any unproven REQ (ADR-0.0.69 / OBPI-0.0.69-03) |
| `--distribution` | opt-in | T0 static distribution audit: ON\_DISK\_NOT\_INCLUDED / BASELINE\_NOT\_ON\_DISK / ON\_DISK\_NOT\_BASELINE drift classes (ADR-0.0.32-07) |
| `--receipt-shape` | opt-in | Fail-closed on post-cutoff `obpi_receipt_emitted` events with deprecated shapes (optional attestation, unprefixed completion, agent: attestor); pre-cutoff receipts can be waivered via `data/historical_self_close_waivers.json` (ADR-0.0.36, OBPI-0.0.36-03) |
| `--bullet-retention` | opt-in | Tier-scoped retention for every Mechanical/Promotable bullet in advisory-rules-audit.md: invariant-tier verbatim in per-turn surface; compressible-tier witnessed by a valid advisor-QC receipt + attestation (ADR-0.0.33-01; tier-scoped amendment OBPI-0.0.37-25) |
| `--scenario-reachability` | opt-in | Assert every Mechanical/Promotable bullet reachable from a declared loading scenario (ADR-0.0.33-04; Era-1 advisory) |
| `--surface-fidelity` | opt-in | Composite: run all four surface-fidelity invariants in declared order; exit code is worst-of-four (ADR-0.0.33-05) |
| `--req-kind-discipline` | opt-in | Fail closed (exit 3) on OBPI briefs with mixed-state [kind] tags or per-kind proof-citation gaps (ADR-0.0.59-02) |
| `--brief-command-shape` | opt-in | Fail closed (exit 3) when a brief Verification block contains non-shell-less commands (OBPI-0.0.63-07, GHI #550) |
| `--tautological-test-audit` | opt-in | Fail closed (exit 3) when tautological-test count exceeds baseline + waivers; `current > baseline + W` → exit 3; waivers at `data/tautological_test_waivers.json` (OBPI-0.0.59-04) |
| `--task-envelope-coherence` | opt-in | Fail closed (exit 3) on TASK attribution drift: worklog without task_id, all-seq=01 without req_atomic, or layer-drift across channels (ADR-0.0.64 / OBPI-04) |
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
