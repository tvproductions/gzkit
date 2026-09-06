<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Governance Runbook (gzkit)

**Purpose:** Operator procedures for executing GovZero workflows in gzkit: ADR/OBPI lifecycle work, reconciliation, closeout, audit, and parity maintenance.

**Version:** GovZero v6 extraction surface
**Scope:** Governance operations in this repository
**Companion:** [Operator Runbook](../user/runbook.md) (daily execution loop)

This document is procedural ("how to"), not policy ("what the rules are"). Canonical policy remains in `docs/governance/GovZero/**`.

---

## Governance Quick Reference

### Status and health

```bash
uv run gz status --table
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz adr report
uv run gz state --json
uv run gz adr audit-check ADR-<X.Y.Z>
uv run gz adr fidelity ADR-<X.Y.Z>   # bound gate; closeout + audit invoke it (ADR-0.0.73)
uv run gz adr covers-check ADR-<X.Y.Z>
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz obpi status OBPI-<X.Y.Z-NN>
uv run gz roles
uv run gz personas list               # List agent personas
uv run gz personas list --json         # List personas as JSON
```

### Lifecycle execution

```bash
uv run gz init                        # Initialize governance scaffolding
uv run gz upgrade                     # Surface-only refresh from installed wheel (no manifest mutation)
uv run gz prd                         # Create Product Requirements Document
uv run gz constitute                  # Create constitution artifact
uv run gz plan create <name> --kind feature --semver X.Y.Z  # Create an ADR
uv run gz plan audit OBPI-<X.Y.Z-NN> # Structural prereq check for plan alignment
uv run gz specify                     # Create implementation brief (OBPI)
uv run gz obpi pipeline OBPI-<X.Y.Z-NN>  # Execute OBPI pipeline
uv run gz obpi dispatch OBPI-<X.Y.Z-NN> --role <Role> --model <tier>  # Record a Stage-2 dispatch (credit is never inferred)
uv run gz obpi audit OBPI-<X.Y.Z-NN> # Gather evidence and record in audit ledger
uv run gz obpi sync OBPI-<X.Y.Z-NN> # Fail-closed reconciliation
uv run gz obpi brief-drift OBPI-<X.Y.Z-NN> # Reconcile brief content vs project (5 drift dimensions)
uv run gz ontology sense                  # Image the current governance shape (read-only sonar; STRUCTURAL seams)
uv run gz ontology trace <ID>             # Walk one node's vertical lineage + lateral proof + edge provenance (read-only)
uv run gz ontology resense                # Diff the shape vs the last sweep — the airlock re-sense gate (read-only)
uv run gz ontology seams                  # Fast contacts-only STRUCTURAL seam check (read-only)
uv run gz ontology reach <ID>             # One node's downstream blast-radius / transitive dependents (read-only)
uv run gz airlock in --target <OBPI> --dry-run # Airlock-IN preflight membrane (diagnostic-only; NO-GO reports but exits 0)
uv run gz airlock out --target <OBPI> --dry-run # Airlock-OUT exit drift-diff membrane (diagnostic-only; surfaced drift reports but exits 0; never writes L1)
uv run gz obpi repudiate OBPI-<X.Y.Z-NN> --cause <enum> --reason "..." --attestor "<human>" # Repudiate fraudulent/erroneous completion (reverse-and-keep; OBPI stays live)
uv run gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..." --attestor "<human>" # Withdraw OBPI from counts (permanent retirement; witnessed transition)
uv run gz obpi supersede OBPI-<X.Y.Z-NN> --by OBPI-<X.Y.Z-MM> --rationale "..." --attestor "<human>" # Supersede one OBPI by another (witnessed transition; superseded node marked in graph)
uv run gz obpi block OBPI-<X.Y.Z-NN> --reason "..." --next-action "..." # Record an outstanding operator ruling (reversible, unattested; blocks pipeline launch)
uv run gz obpi unblock OBPI-<X.Y.Z-NN> --ruling "..." --operator "<who>" # Record the ruling verbatim and release the block
uv run gz obpi lock claim OBPI-<X.Y.Z-NN>  # Claim OBPI work lock
uv run gz obpi lock release OBPI-<X.Y.Z-NN> # Release OBPI work lock
uv run gz obpi lock check OBPI-<X.Y.Z-NN>  # Check if OBPI is locked
uv run gz obpi lock list               # List active OBPI work locks
uv run gz obpi complete OBPI-<X.Y.Z-NN> --attestation-text "<verbatim user words — session evidence>"
uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN> --event completed --attestor "<name>" --evidence-json '{...}'
uv run gz mx enter --reason "<text>" --attestor "<operator>"  # Open the MX hangar (operator only)
uv run gz mx exit --attestor "<operator>"                    # Close the MX hangar (hard gate; operator signs)
# While the hangar is open, normal releases are refused (exit 3): gz patch release and
# gz closeout block until you gz mx exit (ADR-0.0.74 hardening). Dry-run preview is unaffected.
uv run gz permitted-entry --target <path> --recon  # Airlock ad-hoc door (recon; light repair at most)
uv run gz flags                       # Display feature flags
uv run gz flag explain <flag>         # Inspect one flag
uv run gz migrate-semver              # Record SemVer rename events
uv run gz register-adrs               # Register existing ADR packages
```

Skill-based entry points:

```text
/gz-adr-create
/gz-adr-manager   # compatibility alias for /gz-adr-create
/gz-obpi-brief
/gz-obpi-pipeline OBPI-<X.Y.Z-NN>
/gz-obpi-sync ADR-<X.Y.Z>
/gz-adr-sync ADR-<X.Y.Z>
/gz-adr-sync
```

### Validation and proof surfaces

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz validate --documents --surfaces
uv run gz preflight                           # Detect stale artifacts
uv run gz obpi validate --adr ADR-<X.Y.Z> --authored
uv run gz adr evaluate ADR-<X.Y.Z>
uv run gz readiness evaluate
uv run gz parity check
uv run mkdocs build --strict
```

### Receipt-shape integrity (ADR-0.0.36)

```bash
uv run gz validate --receipt-shape  # Refuse post-cutoff deprecated receipt shapes (exit 3 on violation)
```

Fails closed when any `obpi_receipt_emitted` event dated on or after the ADR-0.0.36 cutoff
(`2026-04-26`, read from ADR frontmatter) carries: `attestation_requirement: optional`,
`obpi_completion: completed` without the `attested_` prefix, or `attestor` matching `^agent:`.
Pre-cutoff receipts: warn-only when `data/historical_self_close_waivers.json` is absent;
fail-closed on unwaivers when the waiver list is present (authored under OBPI-0.0.36-04).

### Complexity doctrine surfaces (ADR-0.0.27 cluster)

```bash
uv run gz validate --complexity-doctrine-links  # Citation link integrity
uv run gz governance render --target agents-md --check   # Drift-check AGENTS.md against invariant registry
uv run gz governance render --target agents-md           # Write AGENTS.md from invariant registry
uv run gz complexity distill                     # Run a distillation pass
uv run gz complexity distill --no-prior          # Cold-start invocation
uv run gz complexity distill --allow-dated-sibling  # Same-date sibling
uv run gz complexity guide <path>                # Authoring-time hint preview (advise-band only)
uv run gz complexity guide <path> --json         # Machine-readable AuthoringHint JSON
uv run gz complexity advise <path>               # Trigger-time advisor diagnosis
uv run gz complexity advise <path> --json        # Machine-readable JSON
```

`gz complexity distill` is the destination CLI verb for the
[`gz-complexity-distill`](../../.gzkit/skills/gz-complexity-distill/SKILL.md)
skill (parent ADR-0.0.27, OBPI-0.0.27-06). It composes the OBPI-03
measurement pipeline with the OBPI-04 distillation render and emits a
dated `distilled-characteristics-{YYYY-MM-DD}.md` under
`docs/governance/complexity/`. Operator follow-up at Gate 5 fills the
per-metric Practitioner-eye observation placeholders the verb leaves
intact (REQ-0.0.27-04-10 — the OEE seam). Full options + exit codes in
[`gz complexity distill`](../user/commands/complexity-distill.md).

`gz complexity guide` (ADR-0.0.30, OBPI-0.0.30-01) is the authoring-time preview surface. Wraps the OBPI-0.0.30-03 hint engine; emits `AuthoringHint` blocks for `advise`-band crossings only. Never blocks (exit 3 unused). Full reference in [`gz complexity guide`](../user/commands/complexity-guide.md).

`gz complexity advise` (ADR-0.0.29, OBPI-0.0.29-03) is the trigger-time
response surface that consumes the threshold table at
`.gzkit/rules/complexity-thresholds.json` and emits an `AdvisorDiagnosis`
for every per-function `radon_cc` band crossing. Each diagnosis names the
canonical refactor archetype, the cited doctrinal authority
(Fowler / Martin / Page-Jones / Constantine), a non-empty proof tuple
linking to AST nodes, and the recommended-move excerpt sourced from the
active distilled-characteristics document. Operator moment: preview
advisor diagnosis on a file before commit. Exit codes follow the
four-code map: `0` clean or warn-band, `3` block-band crossing. Full
options + exit codes in
[`gz complexity advise`](../user/commands/complexity-advise.md).

### Cross-repo defect routing

When a defect or enhancement against a gzkit-owned surface (the `gz` CLI,
schemas under `src/gzkit/schemas/`, validator scopes, ledger event semantics,
files under `.gzkit/**` or `src/gzkit/**`, rules under `.gzkit/rules/**`)
is surfaced from inside a consuming repository, the canonical wrapper is:

```bash
uv run gz issue file --title T --body "<gzkit-surface description>" --defect [--dry-run]
uv run gz issue file --title T --body "<gzkit-surface description>" --enhancement [--dry-run]
```

The wrapper auto-stamps a provenance trailer and routes against
`tvproductions/gzkit` regardless of the consuming repo's `git remote`. Bodies
without a gzkit-surface marker (`gz <verb>`, `.gzkit/`, `src/gzkit/`,
`gzkit.<module>`) are hard-rejected with exit 1. Doctrine: `.gzkit/rules/gh-cli.md`
§ Cross-repo filing. Operator runbook entry:
[`docs/user/runbook.md` § Cross-Repo Defect Filing](../user/runbook.md#cross-repo-defect-filing-gzkit-owned-surfaces).

---

## Concepts

### Gate system

| Gate | Name | Verification |
|---|---|---|
| 1 | ADR recorded | `uv run gz validate --documents` |
| 2 | TDD | `uv run gz test` (fast build-verification pass: `uv run gz smoke`) |
| 3 | Docs | `uv run gz lint` + `uv run mkdocs build --strict` |
| 4 | BDD | `features/` scenarios if present |
| 5 | Human attestation | `uv run gz attest ADR-<X.Y.Z> --status completed` |

Lane rule: `lite` requires Gates 1-2; `heavy` requires Gates 1-5.

### Layered trust

See [State Doctrine](state-doctrine.md) for the full three-layer model, five authority rules, and conflict decision table.

| Layer | Trust source | Typical tooling |
|---|---|---|
| 1 | Runtime evidence generation | `gz implement`, `gz check`, `gz adr audit-check` |
| 2 | Ledger-driven reconciliation | `/gz-obpi-sync`, `gz audit` |
| 3 | File sync and indexing | `/gz-adr-sync`, `gz agent sync control-surfaces` |

**T0 — Distribution layer:** When promoting a new canonical surface, read [`docs/governance/distribution_invariant_catalog.md`](distribution_invariant_catalog.md) first and check it against the "Is this a T0 breach?" decision tree before authoring the surface's packaging OBPI.

### Persona framing

Every agent context frame includes a mandatory `## Persona` section (ADR-0.0.11).
Persona files live in `.gzkit/personas/` as structured markdown with YAML frontmatter
defining composable traits, anti-traits, and a behavioral grounding statement.

**Key constraints:**

- Persona frames describe behavioral identity — values, craftsmanship standards,
  and relationship to the work
- Never use generic expertise claims ("You are an expert X developer") — the PRISM
  study shows these degrade accuracy while adding no knowledge
- Traits compose orthogonally per the PERSONA/ICLR 2026 framework

**Commands:**

```bash
uv run gz personas list               # Enumerate defined personas
uv run gz personas list --json         # Machine-readable output
```

**Where persona appears:**

| Surface | Location |
|---------|----------|
| Agent contract | `AGENTS.md` § Persona |
| ADR context frames | `## Persona` section in each ADR |
| Persona files | `.gzkit/personas/*.md` |

### Storage tier escalation

Moving data from Tier A/B to Tier C is a **tier escalation** — a Heavy-lane decision
requiring its own ADR. See [Storage Tiers Reference](storage-tiers.md) for full
definitions and the exhaustive storage catalog.

**Rule:** No Tier C storage dependency (database, external server, protocol) may be
introduced without an explicit Heavy-lane ADR authorizing the escalation.

**Anti-pattern to watch for:** A Tier B cache (derived/rebuildable) that gradually
accumulates state not derivable from Tier A sources — silently becoming Tier C without
governance authorization. Periodic rebuild tests (delete Tier B, rebuild, verify no
data loss) guard against this drift.

### Feature flag system

Feature flags are **transition controls** — mechanisms for routing between old and new
behavior during migration, with the explicit expectation that the old path and the toggle
will be removed. They are not A/B experiments or analytics features.
See [Feature Flags Reference](feature-flags.md) for the full specification.

**Categories:**

| Category | Purpose | Deadline type |
|----------|---------|---------------|
| `release` | Transient feature gates | `remove_by` |
| `ops` | Operational kill switches | `review_by` |
| `migration` | Internal representation transitions | `remove_by` |
| `development` | Incomplete work gating (default `false`) | `remove_by` |

**Lifecycle:** Every flag has a deadline. A CI time-bomb test fails if any flag is past
its deadline, enforcing cleanup discipline.

**Commands:**

```bash
uv run gz flags                       # List all flags with resolved values and sources
uv run gz flags --stale               # Show only overdue flags (past review/remove dates)
uv run gz flag explain <key>          # Full metadata for one flag (category, owner, deadlines)
```

### Persona control surface

Personas define behavioral identity for pipeline agents. Files live in
`.gzkit/personas/` as markdown with YAML frontmatter.

**Schema:** `name`, `traits` (list), `anti-traits` (list), `grounding` (text).

**Read-only contract:** `gz personas list` enumerates personas without mutation.
No commands exist to create, edit, or switch personas at runtime.

**Pipeline integration:** The pipeline dispatch layer reads
`.gzkit/personas/{role}.md` at dispatch boundaries and passes the persona
body as `extra_context` to the subagent prompt.

**Exemplar:** `.gzkit/personas/implementer.md` ships with the repository.

### Cross-project persona workflow

Validating persona portability in an external GovZero-governed repository
(ADR-0.0.13 item 6):

1. Initialize the target project (creates `.gzkit/personas/` with defaults):

    ```bash
    cd ../airlineops
    uv run gz init
    ```

2. Verify persona files were scaffolded:

    ```bash
    ls .gzkit/personas/
    # Expected: default-agent.md  default-reviewer.md
    ```

3. Validate personas against the portable schema:

    ```bash
    uv run gz validate --surfaces
    ```

4. Sync personas to vendor mirrors:

    ```bash
    uv run gz agent sync control-surfaces
    ls .claude/personas/
    ```

5. Confirm no gzkit-specific content leaked:

    ```bash
    grep -ri "gzkit\|obpi\|pipeline" .gzkit/personas/
    # Expected: no output (exit 1)
    ```

**Key constraint:** The target project's persona content must be
project-specific. Default personas are starters that projects customize to
reflect their workflow. If the portable surface requires gzkit source
modifications to work in an external project, the surface is broken
(REQ-0.0.13-06-07).

### OBPI discipline

- OBPI is the atomic implementation unit.
- ADR status is a roll-up of OBPI completion plus attestation.
- **Lane inheritance:** `kind` and `lane` are orthogonal axes (ADR-0.0.17 § Decision #2). Attestation rigor keys on lane: if the parent ADR is heavy-lane (any kind), human attestation is required for all OBPIs regardless of their individual lane designation. Foundation-kind ADRs additionally follow the attestation walkthrough doctrine in ADR-0.0.18 regardless of lane.

### ADR series selection

When creating or promoting an ADR, pick the next available version in the correct series:

- **0.0.x (Foundation):** Infrastructure, governance framework, developer tooling. No GitHub releases.
- **0.x.0+ (Feature):** User-facing capability, external contracts, observable behavior changes. Release tags created on validation.

---

## Workflow: Create or Promote ADR

**When:** New governance work must be planned.

Skill shortcuts for ADR creation and planning:

- [`/gz-design`](../user/skills/gz-design.md) — collaborative design dialogue that produces ADR artifacts (use before formal creation)
- [`/gz-adr-create`](../user/skills/gz-adr-create.md) — create and book a GovZero ADR with OBPI briefs
- [`/gz-adr-promote`](../user/skills/gz-adr-promote.md) — promote a pool ADR into canonical package structure
- [`/gz-adr-evaluate`](../user/skills/gz-adr-evaluate.md) — score ADR quality and run red-team challenges before proceeding

### Before proposing a foundation-kind ADR

Foundation kind requires a structural witness — a registry entry in
`.gzkit/invariants/` with a non-empty `structural_witness` array. A prose-only claim
(in AGENTS.md, a pool-ADR body, or ADR prose) does not qualify.

**Three-step algorithm (from ADR-0.0.37 and ADR-0.0.18 Amendment 2026-06-06):**

1. **Identify the constitutional invariant** the proposed ADR registers. What is the
   invariant intent — the property of the system this ADR is here to guarantee? State it
   in one sentence.

2. **If no registered invariant exists yet, propose the invariant first.** Author a
   `.gzkit/invariants/<slug>.yaml` draft (schema:
   `src/gzkit/schemas/constitutional_invariant.json`) with `structural_witness` named.
   Do not author the ADR until the invariant is registered and its structural witness
   is named.

3. **Only then promote to ADR.** With the invariant registered and the structural
   witness named, the ADR can be authored — its Decision section will reference the
   registry entry. **Author it as `--kind feature`:** ADR-0.34.0 (Foundation Sunset)
   closed the `foundation` kind to new authoring, so a foundation-kind proposal is
   refused at the command handler. The grandfathered foundation ADRs already on disk
   continue to validate.

**Reference:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

1. Inspect active and pending ADR state.

```bash
uv run gz status --table
```

2. If promoting from pool, use deterministic promotion.

```bash
uv run gz adr promote ADR-pool.<slug> --kind feature --semver X.Y.Z --status proposed
```

3. If reversing a promotion (e.g., the get-out-of-jail prequel sweep, or any
   ADR that was promoted but is not actually committed work), use the
   deterministic inverse:

```bash
uv run gz adr demote ADR-<X.Y.Z>-<slug> --ghi <NUMBER>
```

Demotion strips `kind`/`semver` frontmatter, moves the file from
`pre-release/` or `foundation/` to `pool/`, deletes the source package
directory (briefs + closeout form per Q1=b of the 2026-05-23 prequel), and
emits an `artifact_renamed` ledger event with `reason="pool_demotion"`. The
`--ghi` flag is mandatory for auditability. See `docs/user/manpages/adr-demote.md`.

#### Foundation ADR IDs (closed kind)

Foundation ADR IDs (0.0.x) are **nominal integers**, not sequence positions —
sparse sets (`0.0.54`, `0.0.56`, no `0.0.55`) are valid, and the IDs must never
be sorted or compared as semver (ADR-0.0.57).

**The kind is closed to new authoring** by ADR-0.34.0 (Foundation Sunset): both
`gz plan create --kind foundation` and `gz adr promote --kind foundation` are
rejected at the command handler, so no new 0.0.x ID is allocated and the
gap-filling allocator has been retired. The kind is sealed, not deleted —
`foundation` remains a valid schema enum value so the grandfathered on-disk
foundation ADRs keep validating. Route new work with `--kind feature` or
`--kind pool`.

Use `/gz-foundation-triage` to rank the existing in-flight foundations by
priority.

3. Create or update OBPI briefs for checklist items.

```text
/gz-obpi-brief
```

4. Validate briefs are authored (not template stubs).

```bash
uv run gz obpi validate --adr ADR-<X.Y.Z> --authored
```

5. Evaluate ADR and OBPI quality before proceeding.

```bash
uv run gz adr evaluate ADR-<X.Y.Z>
```

A NO GO verdict blocks pipeline execution. Address action items and re-evaluate.

5b. Pre-execution reasoning when quality signals are weak.

When `/gz-adr-evaluate` returns a low score, or when an OBPI's
implementation pass has ambiguous scope, scaffold an 8-section
reasoning walkthrough before continuing into Step 6. The CLI is
deterministic — every byte of the scaffold is rendered, never
generated by an LLM.

Two upstream skills route operators here:

- **`gz-adr-evaluate`** flags low-score dimensions (Problem Clarity,
  Decision Justification, Architectural Alignment, etc.) in its
  output and recommends `gz justify` so the missing reasoning is
  authored before the ADR is taken to defense.
- **`gz-obpi-pipeline`** at the Stage 1→2 Confidence Gate routes the
  agent to `gz justify` when self-reported confidence in the planned
  implementation is below 90%. This gate mechanizes Prime Directive
  invariant 11 (`AGENTS.md` § Behavior Rules — Always, item 7):
  *"If you are less than 90% sure of the direction, ask the human
  before proceeding."* The walkthrough is the structured form of
  that ask.

```bash
# Anchor on a GHI, an OBPI, or a free-text draft
uv run gz justify <anchor> --save

# Validate the filled walkthrough before citing in attestation
uv run gz justify validate artifacts/justify/<saved-file>.md
```

The validate subverb exits 0 only when every `_[To be filled]_`
block is closed; exit 1 lists which sections remain unfilled.
Citing a validated walkthrough in OBPI Key Proof or ADR Evidence
preserves the operator's pre-implementation reasoning rather than
post-hoc reconstruction (per `docs/governance/arb-middleware.md`
§ Why receipts, not narrative).

See [`/gz-justify`](../user/skills/gz-justify.md) and
[`commands/justify.md`](../user/commands/justify.md) for the full
walkthrough protocol.

### Step 5c: Focused-context payload (`gz context`)

When loading a single ADR's worth of context into an agent harness
(target ADR body, every OBPI brief under that ADR, the covering-test
file paths grouped by REQ, and a governance-rules section naming lane
/ lifecycle / current gate / next action), invoke `gz context` rather
than asking the agent to discover the bundle by repeated reads.

```bash
# Render the focused-context payload to stdout
uv run gz context ADR-<X.Y.Z>
```

The payload is plain Markdown without ANSI escapes, suitable for
verbatim piping. Exit 1 with a `BLOCKERS:`-prefixed stderr line names
an unresolvable ADR ID. See [`manpages/context.md`](../user/manpages/context.md)
for the option reference and exit-code matrix.

6. Validate artifact and document integrity.

```bash
uv run gz validate --documents
uv run gz check-config-paths
```

---

## Workflow: OBPI Increment

**When:** Implementing one checklist item.

Skill shortcuts for OBPI execution:

- [`/gz-obpi-pipeline`](../user/skills/gz-obpi-pipeline.md) — post-plan execution pipeline (implement, verify, present, sync)
- [`/gz-obpi-brief`](../user/skills/gz-obpi-brief.md) — generate a new OBPI brief with correct headers and evidence stubs
- [`/gz-obpi-lock`](../user/skills/gz-obpi-lock.md) — claim or release OBPI work locks for multi-agent coordination
- [`/gz-plan-audit`](../user/skills/gz-plan-audit.md) — pre-flight audit to verify plan aligns with OBPI brief scope
- [`/gz-specify`](../user/skills/gz-specify.md) — create OBPI briefs linked to parent ADR items

1. Orient on current state and the parent ADR.

```bash
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz status --table
```

2. Validate the target brief is authored (not a template stub).

```bash
uv run gz obpi validate <path-to-brief> --authored
```

3. Plan the OBPI and exit plan mode with an approved plan.
4. Invoke the OBPI execution pipeline.

```text
/gz-obpi-pipeline OBPI-<X.Y.Z-NN>
```

Use compatibility entry points when implementation or verification already
exists:

```text
/gz-obpi-pipeline OBPI-<X.Y.Z-NN> --from=verify
/gz-obpi-pipeline OBPI-<X.Y.Z-NN> --from=ceremony
```

4. Inside the pipeline, implement + verify Gate 2 (+ Gate 3 when docs change).

```bash
uv run gz implement --adr ADR-<X.Y.Z>
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz lint
```

5. Present the OBPI acceptance ceremony before marking the brief `Completed`.
6. Sync audit and ADR table state after the ceremony.

Pipeline rules:

- verify -> reviewer dispatch -> ceremony -> sync is mandatory
- Heavy-lane work (any kind) stays fail-closed on human attestation; foundation-kind work (any lane) additionally follows ADR-0.0.18 walkthrough discipline
- if concurrent execution is needed before lock parity exists, stop with
  `BLOCKERS`

### Reviewer agent protocol (ADR-0.23.0)

After verification passes and before the ceremony, the pipeline dispatches an
independent **reviewer agent** with fresh context to verify the OBPI delivery:

1. The reviewer receives: OBPI brief, closing argument, changed files, doc files
2. The reviewer produces a structured assessment:
   - **promises-met** — yes/no per requirement, with evidence
   - **docs-quality** — substantive / boilerplate / missing
   - **closing-argument-quality** — earned / echoed / missing
   - **verdict** — PASS / CONCERNS / FAIL
3. The assessment is stored as `REVIEW-OBPI-X.Y.Z-NN.md` in the ADR's `briefs/` directory
4. The Stage 4 ceremony presents the assessment to the human attestor

The reviewer is read-only and does not fix problems — it identifies them.
A FAIL verdict does not block the pipeline; the human attestor decides.

```bash
# Verify reviewer assessment artifact exists after pipeline
ls docs/design/adr/**/briefs/REVIEW-OBPI-*.md
```

---

## Workflow: Reconciliation and Drift Detection

**When:** Before closeout, after multi-session work, or when status drift is suspected.

Skill shortcuts for reconciliation (run in trust order — Layer 2 before Layer 3):

- [`/gz-obpi-sync`](../user/skills/gz-obpi-sync.md) — audit briefs against evidence, fix stale metadata, write ledger proof (Layer 2)
- [`/gz-adr-sync`](../user/skills/gz-adr-sync.md) — end-to-end ADR governance sync: evidence discovery, ledger reconciliation, and registration (Layers 1-3)

Run in trust order:

```text
/gz-obpi-sync ADR-<X.Y.Z>   # OBPI brief evidence (Layer 2)
/gz-adr-sync ADR-<X.Y.Z>         # ADR-scoped reconciliation (Layers 1-2)
/gz-adr-sync                     # Full registration and status refresh (Layer 3)
```

Then verify no unresolved evidence gaps:

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
uv run gz adr status ADR-<X.Y.Z> --json
```

If `audit-check` fails, fix the referenced OBPI brief evidence and rerun until PASS.

---

## Workflow: ADR Closeout and Audit

**When:** All linked OBPIs are completed and evidenced.

Skill shortcuts for the closeout and audit ceremony:

- [`/gz-adr-closeout-ceremony`](../user/skills/gz-adr-closeout-ceremony.md) — execute the full closeout ceremony protocol for human attestation
- [`/gz-closeout`](../user/skills/gz-closeout.md) — initiate ADR closeout with evidence context
- [`/gz-attest`](../user/skills/gz-attest.md) — record human attestation with prerequisite enforcement
- [`/gz-audit`](../user/skills/gz-audit.md) — run strict post-attestation reconciliation audits (only after attestation)
- [`/gz-adr-audit`](../user/skills/gz-adr-audit.md) — Gate-5 audit templates and procedure for ADR verification

1. Pre-closeout blocking check.

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

2. Closeout ceremony initiation (dry-run first, then live).

```bash
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz closeout ADR-<X.Y.Z>
```

3. Human attestation.

```bash
uv run gz attest ADR-<X.Y.Z> --status completed
```

4. Post-attestation audit and accounting.

```bash
uv run gz audit ADR-<X.Y.Z>
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

Rules:

- Do not run `gz audit` before attestation.
- Do not treat passing checks as implied attestation.
- Record attestation terms explicitly (`Completed`, `Completed — Partial: <reason>`, `Dropped — <reason>`).
- Both the closeout ceremony (EXECUTE→ATTESTATION edge) and `gz audit` invoke the **same bound fidelity gate** (`gz adr fidelity`), which RUNS the ADR Decision's `## Fidelity Assertions` against the running system — the bound replacement for the prose 'Demonstrate Value' step (ADR-0.0.73). A failed assertion blocks the ceremony; a missing block is flagged with a warning (presence is hard-enforced at ADR closeout, Boundary Invariant #4). Do not substitute agent prose for the gate.
- **Test-shape inventory (GHI #571):** `uv run gz test-shape` reports advisory test-shape debt — tautological content-echo operations with their proposed disposition, and output/render assertions with whether the `# output-contract:` carve-out is declared. It always exits 0. The fail-closed *growth* gate is `uv run gz validate --tautological-test-audit`; the inventory routes the cleanup the gate cannot describe. Only **BEHAVIOR** REQs carry `@covers` tests — never author one to make a SUPPORT or STRUCTURAL-FENCE REQ appear covered (ADR-0.0.59).
- **RED falsifiability gate (GHI #642):** `@covers` parity proves a BEHAVIOR REQ has a covering test; it never proves that test can fail. `uv run gz arb red --req REQ-<X.Y.Z-NN-MM> --obpi OBPI-<X.Y.Z-NN>` runs the covering test against the base tree with the production hunks withheld and records a `red_receipt_emitted` event carrying a `failure_class` of `assertion` (strong RED), `error` (weak RED — failed for the wrong reason), or `none` (the test passed without its implementation and therefore cannot fail). `uv run gz validate --red-parity`, a bound `gz check` step, fails closed on a missing witness or a `none` verdict.
- **REQ-coverage gate (ADR-0.0.25):** `gz obpi complete` exits 3 when any REQ in the closing brief's `## Acceptance Criteria` lacks a passing `@covers`-decorated test. Use `uv run gz covers OBPI-<X.Y.Z-NN>` to check coverage before invoking completion. The same gate mirrors to `gz adr emit-receipt --event closed`: an ADR cannot close while any OBPI has an unwaived REQ gap. A **BEHAVIOR** REQ cannot be waived: `--accept-uncovered` is refused on every lane, because BEHAVIOR's only proof channel is a `@covers` test (ADR-0.0.59, GHI #537). SUPPORT and STRUCTURAL-FENCE REQs never reach the waiver path — they are exempt from the coverage gate by proof channel — so the flag has no REQ kind it may waive. The refusal fires on kind, before the `--attestor-present` gate; no transport mechanism gates it (GHI #587 stands).

---

## Workflow: Task-Level Governance

**When:** Managing TASK entities (fourth tier: ADR > OBPI > REQ > TASK).

```bash
uv run gz task list OBPI-<X.Y.Z-NN>              # List tasks for an OBPI
uv run gz task start TASK-<id>                    # Start a pending task
uv run gz task complete TASK-<id>                 # Complete an in-progress task
uv run gz task block TASK-<id> --reason "..."     # Block with reason
uv run gz task escalate TASK-<id> --reason "..."  # Escalate with reason
```

---

## Workflow: Chores and Maintenance

**When:** Running scheduled maintenance, code quality checks, or repository hygiene.

Skill shortcuts for maintenance workflows:

- [`/gz-chore-runner`](../user/skills/gz-chore-runner.md) — run a chore end-to-end (show, plan, advise, execute, validate)
- [`/gz-check`](../user/skills/gz-check.md) — run full quality checks in one pass (lint, typecheck, test, docs)
- [`/gz-arb`](../user/skills/gz-arb.md) — quality evidence workflow with structured JSON receipts
- [`/gz-tidy`](../user/skills/gz-tidy.md) — run maintenance checks and cleanup routines

```bash
uv run gz chores list                      # List declared chores
uv run gz chores show <slug>               # Display CHORE.md for one chore
uv run gz chores advise <slug>             # Dry-run criteria and report status
uv run gz chores plan <slug>               # Show plan details for one chore
uv run gz chores run <slug>                # Execute and log one chore
uv run gz chores audit --all               # Audit log presence for all chores
uv run gz chores propose-ghi <slug>        # File GHIs for unfiled cluster proposals in proofs/
```

Frontmatter-ledger reconciliation (ADR-0.0.16 OBPI-03):

```bash
uv run gz frontmatter reconcile --dry-run  # Preview ledger-wins rewrites
uv run gz frontmatter reconcile            # Apply rewrites; emit receipt under artifacts/receipts/frontmatter-coherence/
uv run gz frontmatter reconcile --json     # Receipt JSON to stdout
```

Maintenance gate commands:

```bash
uv run gz tidy                             # Run maintenance checks
uv run gz format                           # Auto-format code
uv run gz typecheck                        # Static type checks
uv run gz drift                            # Detect spec-test-code drift
uv run gz covers ADR-<X.Y.Z>              # Trace test-to-requirement coverage
uv run gz skill new <name>                 # Create a new skill scaffold
uv run gz skill list                       # List all discovered skills
uv run gz interview                        # Run interactive governance interviews
uv run gz knowledge generate               # Generate the OKF knowledge bundle
uv run gz knowledge refresh                # Refresh the bundle idempotently from current sources
```

The generated bundle lives at `.gzkit/governance/knowledge/`. It is an **orientation aid**
only — never cite its frontmatter or links as governance evidence (Boundary Invariant 1,
ADR-0.30.0). The progressive-disclosure navigation path is documented in
`docs/user/concepts/okf-navigation.md`.

The doctrine governing which content belongs under `.gzkit/` (gzkit-core canon) vs
`docs/` (adopter-authored project content) is at
`.gzkit/governance/knowledge/content-boundary.md`.

---

## Workflow: Session Handoffs

**When (MUST):**

- Session ending with incomplete OBPI work
- Scope switch between ADRs
- Explicit human request

See [`/gz-session-handoff`](../user/skills/gz-session-handoff.md) for full details on creating and resuming session handoffs with staleness classification.

**Procedure:**

```text
/gz-session-handoff CREATE
/gz-session-handoff RESUME
```

The skill wields the `gz handoff` verb, which routes handoff authoring through
the fail-closed validation gate (ADR-0.0.65):

```bash
uv run gz handoff list --adr ADR-<X.Y.Z>       # list handoffs newest-first
uv run gz handoff resume --adr ADR-<X.Y.Z>     # newest handoff + staleness + next step
uv run gz handoff create --adr ADR-<X.Y.Z> --slug <slug> --agent <id> --decisions "<text>"
uv run gz handoff rulings [--limit N] [--search TEXT]  # the append-only settled-ruling corpus (GHI #838)
uv run gz handoff decide --handoff <path> --session-id <id> --decision proceed --operator-text "<verbatim>"
uv run gz handoff authorize --handoff <path> --session-id <id> --operator-text "<verbatim>"  # deprecated alias for `decide`
uv run gz handoff archive --older-than 30d --dry-run  # preview move-not-delete retention
uv run gz handoff archive --older-than 30d            # move eligible handoffs into archive/
```

The ARB receipt store carries the sibling retention verb (GHI #594), on the same
move-not-delete shape and the same `--older-than` grammar. A receipt cited in the
ledger is never relocated — receipt ids are the canonical Heavy-lane attestation
evidence, so a citation must keep resolving:

```bash
uv run gz arb archive --older-than 30d --dry-run  # preview; reports the cited-skip count
uv run gz arb archive --older-than 30d            # move eligible receipts into archive/
```

**Resuming requires an operator ruling, at every freshness level (GHI #574).**
This is an agent obligation, not a mechanism: the resume gate that refused
mutating tool calls was retired 2026-08-15 (operator ruling — a handoff is an
advisor, not a gate-keeping nanny), and `.claude/hooks/handoff-resume-gate.py`
no longer exists. Book the ruling with `gz handoff decide`. It is an
**acknowledge-and-decide transit**, never a completion attestation
(ADR-0.0.33 § Alternatives; GHI #757) — `pause`, `hold`, and `revert` are
equally bookable, and `--set-aside` records any advised step the ruling
declines. Staleness escalates *re-verification depth*, never the
authorization requirement:

- `Fresh` (<24h) — present the advised steps, obtain the ruling, book it. Fresh
  shortens verification; it never converts an advisory into a license.
- `Slightly stale` (24-72h) resume with explicit verification.
- `Stale` (>72h) or `Very stale` (>7d) require human re-validation before proceeding.

---

## Workflow: Parity Maintenance Against AirlineOps

**When:** Weekly cadence, before pool ADR promotion, or after canonical governance changes in AirlineOps.

Filter rule:

- Apply the [Parity Intake Rubric](parity-intake-rubric.md) to each candidate import before implementation.

1. Resolve canonical root deterministically and fail closed.

```bash
test -d ../airlineops && test -d .
```

2. Run parity-scan ritual checks.

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-<target>
uv run mkdocs build --strict
```

3. Write dated reports.

- `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`
- `docs/proposals/REPORT-airlineops-govzero-mining-YYYY-MM-DD.md`

4. Convert each `Missing`, `Divergent`, or high-impact `Partial` item into tracked ADR/OBPI follow-up.

Compatibility note:

- `gz-adr-create` is canonical in gzkit.
- `gz-adr-manager` is retained as a legacy alias for cross-repository parity.

---

## Workflow: Skill Maintenance and Deprecation Operations

**When:** Weekly hygiene cadence, before ADR closeout touching skills, or when deprecating/retiring any skill.

Skill shortcuts for agent and skill infrastructure:

- [`/gz-agent-sync`](../user/skills/gz-agent-sync.md) — synchronize generated control surfaces and skill mirrors after updates
- [`/gz-cli-audit`](../user/skills/gz-cli-audit.md) — audit CLI documentation coverage and headings

1. Run lifecycle audit with explicit cadence threshold.

```bash
uv run gz skill audit --json --max-review-age-days 90
```

2. If stale review findings exist, update canonical `.gzkit/skills/*/SKILL.md`:

- set `last_reviewed` to current review date,
- confirm `owner` remains accurate,
- re-run audit until stale findings are zero.

3. If a skill is `deprecated` or `retired`, ensure metadata evidence is present:

- `deprecation_replaced_by`
- `deprecation_migration`
- `deprecation_communication`
- `deprecation_announced_on`
- `retired_on` (retired only)

4. Sync mirrors from canonical source of truth.

```bash
uv run gz agent sync control-surfaces
uv run gz skill audit
```

Rules:

- Canonical `.gzkit/skills` is authoritative; mirrors are derived artifacts.
- Do not deprecate/retire without communication and migration evidence.
- Do not bypass stale review failures; they are blocking policy failures.

---

## Foundation-Triage Planning Workflow

Run foundation triage before committing to a foundation increment, especially
when multiple Draft/Proposed foundations compete for the next sprint.

**Trigger:** Operator invokes `/gz-foundation-triage` in Claude Code.

**Procedure:** The skill executes a three-step triage:
1. Mechanical pre-pass gathering all in-flight foundations with governance-signal counts
2. Cognitive pass — agent reads each candidate, classifies severity
3. Deterministic rendering — ranked report delivered as markdown

**Acting on results:**
- `urgent` severity → prioritize this quarter
- `next-quarter` → queue for planning
- `latent` → leave in backlog

**Constraints:**
- The skill output is diagnosis only — it does NOT modify any ADR or ledger
- Promotion remains a manual decision: `gz adr promote --kind feature <slug>` (the `foundation` kind is closed to new authoring by ADR-0.34.0)
- Do not run foundation triage as a commit gate; it is on-demand

**Cross-reference:** Operator runbook `§ Foundation Triage`, manpage `foundation-triage.md`

---

## Workflow: Git Sync Ritual

Use [`/git-sync`](../user/skills/git-sync.md) for the guarded repository sync ritual with lint/test gates.

```bash
uv run gz git-sync
uv run gz git-sync --apply --lint --test
```

### Append-only JSONL conflicts

`.gzkit/ledger.jsonl` and its sibling JSONL surfaces are appended to by the
runtime every session, so two clones in flight conflict over disjoint tail
additions. `gz git-sync --apply` registers a merge driver
([`gz ledger merge-driver`](../user/manpages/ledger-merge-driver.md)) that
reconciles them as a timestamp-ordered union, so the ritual no longer forces a
hand-edit of the ledger — the action `AGENTS.md` § Never #2 prohibits.

### Correcting an erroneous ledger row

The same prohibition that forbids hand-editing a conflicted ledger forbids
editing out a row recorded in error, so corrections are appended forward
([`gz ledger correct`](../user/manpages/ledger-correct.md)). One verb covers
every event type: a wrongly-started pipeline, a TASK blocker whose reason the
operator has since resolved, a factually-false evidentiary row. It generalizes
the port ADR-0.0.71 declared, whose first adapter was
[`gz obpi repudiate`](../user/manpages/obpi-repudiate.md).

Three dispositions, and the split is load-bearing. `void` says the row records
something that was not true, and no reader may count it — state derivation or
evidence audit alike. `discharged` says the row was TRUE when written and its
condition has ended, so it leaves the liveness reading but stays evidence.
`reinstated` clears a prior correction and is the only way to undo one.
Corrections compose by last-correction-wins, the netting rule
`obpi_parked`/`obpi_unparked` already use.

Operator-gated on ADR-0.0.71 Boundary Invariant 1's terms: `--attestor` and
`--reason` are required and fail closed when empty. A subject reference that
matches no row is refused and writes nothing.
[`gz ledger corrections`](../user/manpages/ledger-corrections.md) is the census
of what is currently in force.

Registration is per-clone (git reads a driver command from local config, which
cannot be committed) and idempotent, so it self-heals on any clone that
predates it. When the driver exits 1 the sides were not plain appends — a row
was edited, removed, or carries no sortable `ts` — and the conflict is left for
you deliberately. Resolve it as a timestamp-ordered union; never append one
side to the other.

Rules:

- No `--no-verify`.
- No force push.
- Keep governance docs, runbook, and command references synchronized in the same change set.

---

## Workflow: Readiness-Driven Design

Use [`/gz-state`](../user/skills/gz-state.md) to query artifact relationships and readiness state, or [`/gz-validate`](../user/skills/gz-validate.md) to validate governance artifacts against schema rules.

```bash
uv run gz readiness audit
uv run gz readiness audit --json > docs/proposals/AUDIT-agent-readiness-gzkit-YYYY-MM-DD.json
```

Use readiness as a design input, not a one-time score:

1. Run `gz readiness audit` before parity extraction or major governance edits.
2. Cross-check findings against [`docs/user/reference/agent-input-disciplines.md`](../user/reference/agent-input-disciplines.md) and record which discipline/primitive each gap maps to.
3. Capture a dated audit artifact in `docs/proposals/`.
4. Convert the top three gaps into tracked ADR/OBPI follow-up work.
5. Use Gate 2 (TDD) and Gate 4 (BDD) evidence as primary inputs for acceptance/evaluation improvements.
6. Re-run readiness after implementation and record score delta in the same proposal.
7. Only claim maturity improvements when quality gates (`gz check`) also pass.

---

## Quick Governance Checklist

### Before starting OBPI work

- [ ] `uv run gz status --table`
- [ ] `uv run gz adr status ADR-<X.Y.Z> --json`
- [ ] Brief scope and acceptance criteria reviewed
- [ ] Existing handoff reviewed if present
- [ ] No Tier C dependency introduced without ADR authorization ([Storage Tiers](storage-tiers.md))

### Before requesting ADR closeout

- [ ] `/gz-obpi-sync ADR-<X.Y.Z>` complete
- [ ] `/gz-adr-sync ADR-<X.Y.Z>` complete
- [ ] `uv run gz adr audit-check ADR-<X.Y.Z>` passes
- [ ] `uv run gz closeout ADR-<X.Y.Z> --dry-run` reviewed
- [ ] No unaudited tier escalation (Tier A/B to C requires Heavy-lane ADR)

### After closeout

- [ ] `uv run gz attest ADR-<X.Y.Z> --status completed`
- [ ] `uv run gz audit ADR-<X.Y.Z>`
- [ ] ADR-level receipt emitted
- [ ] `/gz-adr-sync` run

---

## Persona Design Principles

Persona is a governed control surface stored in `.gzkit/personas/` (ADR-0.0.11). Agent identity framing mechanistically affects which behavioral clusters activate during inference — it is engineering, not decoration.

**Three operator-relevant principles:**

1. **Don't claim expertise — frame behavioral identity.** Generic expert personas ("You are an expert X developer") decrease accuracy by 3.6pp (PRISM study). Instead, describe values, craftsmanship standards, and relationship to the work.
2. **Traits compose orthogonally.** Multiple behavioral traits combine without interference (PERSONA/ICLR 2026). Design persona frames as composable trait specifications with structured YAML frontmatter, not monolithic character descriptions.
3. **Virtue-ethics framing over prohibition lists.** Frame positive behavioral identity (curiosity, thoroughness, craftsmanship) rather than listing what NOT to do. The model infers a complete persona from the identity frame — prohibitions imply inclination.

### Trait Composition Rules

Traits compose by orthogonal concatenation — each trait activates an independent
behavioral dimension without interfering with existing traits.  The canonical
composition operation is implemented in `src/gzkit/personas.py` and follows this
deterministic template:

```text
[grounding text verbatim]

You are {trait-1}: {description from Behavioral Anchors}

You are {trait-2}: {description from Behavioral Anchors}

What this persona does NOT do:
- {anti-trait-1}: {description from Anti-patterns}
```

**Composition rules:**

1. **Grounding first.** The `grounding` field is emitted verbatim as the opening
   behavioral anchor — it sets the persona's relationship to the work.
2. **Traits in declaration order.** Each trait from the `traits` list is emitted
   as `You are {name}: {description}` when a `## Behavioral Anchors` section
   provides a description, or `You are {name}.` otherwise.
3. **Anti-trait suppression.** Anti-traits are collected under `What this persona
   does NOT do:` with descriptions from the `## Anti-patterns` section when
   available.  Anti-traits define behavior that is actively suppressed — not
   merely absent.
4. **Conflict rejection.** If two traits conflict (e.g., "move-fast" vs
   "meticulous"), the anti-trait mechanism rejects the conflicting trait at
   validation time rather than attempting runtime resolution.
5. **Determinism.** Two implementers given the same persona file MUST derive the
   same resulting persona frame.  No randomness, no ordering heuristics.

**Exemplar:** `.gzkit/personas/implementer.md` exercises all composition rules
with four traits and three anti-traits.

**Full research synthesis:** [`docs/design/research-persona-selection-agent-identity.md`](../design/research-persona-selection-agent-identity.md)
**Governing ADR:** ADR-0.0.11 — Persona-Driven Agent Identity Frames

---

## Instruction Files

`AGENTS.md`, `CLAUDE.md`, and `.gzkit/rules/*.md` MUST conform to the map-not-encyclopedia shape contract (ADR-0.0.54). These files are maps of binding bullets, structured tables, and canonical links — not encyclopedias of rationale prose, worked examples, or anti-pattern catalogs.

Shape enforcement: `uv run gz validate --agents-md-map-conformance`

Recovery: `/gz-context-diet` (or `uv run gz chores show instructions-files-diet`) lifts prohibited shapes to `docs/governance/` expansion docs behind one-line pointers.

Prohibited shapes in any instruction file:
- Multi-paragraph rationale prose (paragraph > 5 lines without binding-bullet anchor)
- Subsections titled "Anti-patterns", "Worked example", "Rationale", or "Why X is canon"
- "Why X is canon" blockquote codas
- Narrative pedagogical sections
- Operative-claims expansions restating rules already stated as binding bullets

## Reference Links

- [State Doctrine — Three-Layer Model and Authority Rules](state-doctrine.md)
- [Storage Tiers Reference — Three-Tier Storage Model](storage-tiers.md)
- [GovZero Charter](GovZero/charter.md)
- [ADR Lifecycle](GovZero/adr-lifecycle.md)
- [Audit Protocol](GovZero/audit-protocol.md)
- [Agent Readiness Audit Template](GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md)
- [Agent-Era Prompting Summary (Nate B. Jones)](GovZero/agent-era-prompting-summary.md)
- [Agent Input Disciplines: Practitioner Reference](../user/reference/agent-input-disciplines.md)
- [Gate 5 Architecture](GovZero/gate5-architecture.md)
- [Layered Trust](GovZero/layered-trust.md)
- [Session Handoff Obligations](GovZero/session-handoff-obligations.md)
- [Staleness Classification](GovZero/staleness-classification.md)
