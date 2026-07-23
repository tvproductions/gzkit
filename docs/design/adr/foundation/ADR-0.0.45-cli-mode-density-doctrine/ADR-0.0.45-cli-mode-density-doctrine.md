---
id: ADR-0.0.45-cli-mode-density-doctrine
status: Draft
kind: foundation
semver: 0.0.45
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-16
paired_ghis:
  - "#471"
  - "#472"
---

# ADR-0.0.45-cli-mode-density-doctrine: CLI Mode-Density Doctrine

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
This ADR is identity-shaping work; the implementing agent treats the
three-pillar cutover (refactor + two validators + three-lane rule) as one
coherent move, not three loosely-related changes. The hard cutover blast radius
across ~481 files is approached as a single whole-file reasoning pass, not an
incremental shim sequence.

## Why foundation tier?

Without this ADR, CLI mode density (subcommand depth, flag count per verb, mode interactions) is undisciplined — the operator surface accretes verbs and flags without structural pushback, and `gz` drifts toward unusable complexity.

This ADR authors a port: the CLI mode-density doctrine every new-verb / new-flag authoring surface (and its validator) binds to.

## Intent

Bound CLI mode-density mechanically. **Today**, the 40+ `--<scope>` flags that
accreted on `gz validate` (each individually clig.dev-compliant in spirit and
Lite-lane-cheap in mechanics) are evidence that the **existing** Lite/Heavy
lane economics in `.claude/rules/cli.md` produced a doctrinal gradient that
consumed clig.dev's noun-verb preference 39+ times in a row. The **current**
state is a `gz validate` verb that humans can no longer read at a glance and
that has no mechanical defense against further accretion.

**After this ADR**, the **target** state is: (a) `gz validate` refactored to
noun-verb subverbs (`gz validate suite <name>` / `gz validate audit <name>`)
that **will** restore clig.dev shape; (b) two mechanical density validators
(`cli-flag-density`, `suite-density`) with named registries and bands that
**will** fail-close on further accretion; (c) `.claude/rules/cli.md` amended
to three lanes (Behavior Mode / Scope Selector / New Verb) that name what
the prior binary collapsed. The **outcome** is that CLI mode-density becomes
fail-closed at Gate 1 rather than aspirational at Gate 5.

The cure (#471) and prophylaxis (#472) are operationally inseparable — cure
without prophylaxis re-accretes within ~12 months; prophylaxis without cure
is a paper gate with no precedent to cite. Single foundation ADR is the
correct ceremony shape for that coupling.

## Decision

1. **Single foundation ADR, not paired** — because the cure (#471) and the
   prophylaxis (#472) are operationally inseparable; splitting them across
   `paired_with:` frontmatter re-instantiates the T1/T2 drift this ADR exists
   to prevent. Both #471 and #472 land under one ADR-0.0.45 ceremony; both
   close `superseded` on its completion. **Rationale:** the coupling is the
   doctrine; a paired ADR shape would lose it.

2. **Hard cutover, no deprecation shim** — because shims are vibing surfaces:
   accept-either-form semantics would force the density validator to either
   ignore the deprecated form (defeating its purpose) or fail-close on its own
   ADR. **Rationale:** single-sweep blast radius is shorter pain than
   indefinite shim maintenance. ~99 `--<scope>` references across ~481 files
   flip atomically in OBPI-0.0.45-04; pre-commit hook `.pre-commit-config.yaml`
   changes from `gz validate --bullet-retention --surface-weight --pointer-anchors`
   to `gz validate suite cheap-fidelity` in the same commit.

3. **Suite-named composites plus single-audit verb** — because noun-verb shape
   is the clig.dev preference the prior flag-accretion gradient consumed.
   **Rationale:** restoring noun-verb shape costs one cutover; deferring it
   keeps the gradient active. Two CLI shapes:

- `gz validate suite <name>` — runs a named composite (e.g. `default`,
  `surface-fidelity`, `cheap-fidelity`).
- `gz validate audit <name>` — runs one named audit
  (e.g. `cli-flag-density`, `suite-density`).

Registries: `data/validate_suites.json` (suite → list of audit names),
`data/validate_audits.json` (audit name → scope metadata).

4. **Two-surface density validator with distinct registries and bands** —
   because flag-per-verb (UI memory load) and audits-per-suite (doctrinal-coherence
   drift) are genuinely different failure modes. **Rationale:** a unified
   "intent-density" framework would require one counting predicate to capture
   both with comparable accuracy — empty-framework risk. Distinct registries
   make calibration debuggable; distinct receipts make recalibration auditable
   per-surface.

| Surface | Green | Yellow | Red | Subject |
|---------|-------|--------|-----|---------|
| `cli-flag-density` | ≤7 | 8–12 | >12 | Per-verb flag count (`parser_*.py`) |
| `suite-density` | ≤6 | 7–10 | >10 | Per-suite audit membership |

Distinct registries:

- `data/cli_flag_density_thresholds.json`,
  `data/cli_flag_density_floor.json`,
  `data/cli_flag_density_waivers.json`
- `data/suite_density_thresholds.json`,
  `data/suite_density_floor.json`,
  `data/suite_density_waivers.json`

Yellow requires waiver naming why not subcommand promotion;
Red fail-closed.

5. **Annual + receipt-triggered recalibration via two parallel receipts** —
   because thresholds are calibrated to an empirically measured corpus state,
   and the corpus evolves. **Rationale:** without a recalibration cadence and
   receipt, the bands quietly become theatre when the corpus moves past them.

   - `cli_flag_density_recalibrated`
   - `suite_density_recalibrated`

   Receipt schema is Pydantic with `extra="forbid"` per `.claude/rules/models.md`.
   The receipt-read path is the only consumer.

6. **Three-lane rule replacement in `.claude/rules/cli.md`** — because the prior
   Lite/Heavy binary lossy-compressed three structurally distinct CLI moves
   (behavior mode, scope selector, new verb) into one ceremony axis.
   **Rationale:** Heavy-laning textbook clig.dev-compliant behavior modes
   (`--json`, `--dry-run`) goes past clig.dev's actual prescriptions; deleting
   the Lite lane entirely is worse. Three lanes name the genuine distinction.

| Lane | Surface | Mechanics |
|------|---------|-----------|
| **Lite (Behavior Mode)** | Closed enum: `--json`, `--dry-run`, `--check`, `--apply`, `--quiet`, `--verbose`, `--plain` | No density check; closed-enum extensions require foundation ADR |
| **Mode (Scope Selector)** | New `--<scope>` flags or audit names | Subject to `cli-flag-density`; Yellow needs waiver naming why not subcommand promotion; Red fail-closed |
| **Heavy (New Verb / Subcommand)** | New top-level verb or subcommand | Existing procedure unchanged (ADR or brief, manpage, behave smoke, release notes) |

7. **Scorecard promotion.** `docs/governance/advisory-rules-audit.md` moves
   the clig.dev baseline entry from advisory to "Promoted: Mechanical —
   enforced by `gz validate audit cli-flag-density`". **Rationale:** promotion
   follows the same pattern that landed `--adr-status-fresh` (GHI #322) and
   other Layer-1-to-Layer-2 conversions; the binding rule is meaningless until
   its mechanical enforcer ships.

### Anti-patterns (do not do)

- **Do not** add a `--<scope>` flag instead of a noun-verb subverb after this
  ADR lands. The `cli-flag-density` validator will fail-close in Red band; the
  follows-existing-pattern remediation is `gz validate audit <name>` or
  `gz validate suite <name>`.
- **Do not** add an audit to `data/validate_suites.json` past the Red threshold
  with a one-word waiver reason (`'TODO'`, `'TBD'`, `'pending'`). The waiver
  validator fail-closes on single-token `next_action`; this is the prohibited
  hiding-place pattern named in § Consequences.
- **Do not** silent-disable the pre-commit hook with `--no-verify` to bypass
  a density-band fail-close. The legitimate path is the auditable
  `--accept-flag-density-band Yellow --accept-reason <text>` override that
  emits a `density_band_accepted` ledger event.
- **Do not** shim the old `--<scope>` form back in to ease migration. Shims
  are vibing surfaces (see § Rationale).
- **Avoid** authoring a new behavior-mode flag outside the closed enum without
  a foundation ADR — the closed enum is the doctrine boundary.

**Kind: foundation.** Identity-shaping — changes what gzkit IS
(mode-density-governed CLI) rather than producing a release-carrying capability.

**Lane: heavy.** New CLI verbs (`gz validate suite`, `gz validate audit`),
new validator scopes, new registry files, new ledger event types, change to
`.claude/rules/cli.md` and `.pre-commit-config.yaml`. External-contract
surface across the board.

**Sensitivity: absent.** No security surface.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Every `gz <verb>` reference across docs and skills resolves to a registered parser verb — the CLI-surface-discipline this mode-density doctrine governs. | uv run gz validate --cli-alignment | 0 |

## Consequences

### Positive

- Mechanical pre-Gate-1 backstop against CLI mode-density accretion — what was
  a doctrinal gradient becomes a fail-closed validator.
- Operationally inseparable cure + prophylaxis land in one ceremony; neither
  half can re-fail in isolation.
- Three-lane rule names the genuine distinction between behavior modes
  (`--json`, `--dry-run`), scope selectors (subject to density check), and new
  verbs (Heavy ceremony) — replaces the lossy Lite/Heavy binary on this axis.
- Two surfaces with distinct bands honor that flag-per-verb (UI memory load)
  and audits-per-suite (doctrinal-coherence drift) are genuinely different
  failure modes deserving distinct calibration.
- Recalibration receipts make threshold drift observable and auditable; annual
  cadence plus receipt-triggered recalibration prevents bands from quietly
  becoming theatre.
- Suite-named composites (`gz validate suite <name>`) and single-audit verbs
  (`gz validate audit <name>`) restore clig.dev noun-verb shape that the
  flag-accretion gradient consumed.
- Foundation-attested waiver path with mandatory `next_action` forces the
  unwaivering to be planned, not deferred indefinitely.

### Negative

- **Hard cutover blast radius.** ~99 `--<scope>` references across ~481 files
  flip atomically in OBPI-0.0.45-04. Pre-commit hook contents change in the
  same commit.
- **Pre-mortem failure mode — accretion hides in suites with empty waiver
  reasons.** Operators add audits to suites without bumping the suite-density
  count if waiver validation accepts a blank `reason`. Mitigation:
  `next_action` field required on every waiver entry; empty or generic reasons
  (`'TODO'`, `'TBD'`, single-word) fail-closed by validator.
- **Pre-mortem failure mode — density audit perf budget misses pre-commit
  ship.** If `cli-flag-density` + `suite-density` add >100ms to
  `gz validate suite cheap-fidelity`, operators silent-disable the hook
  locally with `--no-verify` and the prophylaxis collapses. Mitigation:
  OBPI-0.0.45-04 measures wall-clock on the gzkit corpus; if >100ms, suite
  wiring moves to `default`/`surface-fidelity` only, not `cheap-fidelity`.
  Threshold measured, not assumed.
- **Pre-mortem failure mode — recalibration receipt schema drifts.** After
  the first annual cadence, a schema change (e.g. added `methodology_version`
  field) could be silently treated as `null` by older validator-read code and
  the recalibration check skipped. Mitigation: Pydantic models with
  `extra="forbid"`; receipt-read path is the only consumer; explicit
  schema-evolution discipline same as ledger event types.
- **Goes against repo precedent of transitional shims.** Operators reading
  prior ADRs may expect deprecation aliases. The anti-vibing mantra (shims are
  vibing surfaces) is the rationale; single-sweep blast radius is shorter pain
  than indefinite shim maintenance.
- **Surface area growth.** Two new registries, two new validator scopes, one
  new CLI verb pair, two new receipt types. Acknowledged cost, not denied.
- **GHIs #471 and #472 close `superseded`** on ADR-0.0.45 completion (per
  `ghi-close` skill at ADR closeout, NOT at ADR creation).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.45-01: **registry-and-models** — Define `data/cli_flag_density_*.json`, `data/suite_density_*.json`, `data/validate_suites.json`, `data/validate_audits.json`, and Pydantic models at `src/gzkit/governance/trust_audits/cli_density_models.py` per `.claude/rules/models.md`.
- [ ] OBPI-0.0.45-02: **cli-flag-density-validator** — AST walker over `src/gzkit/cli/parser_*.py`; counts per-verb flag accretion against bands (Green ≤7, Yellow 8–12, Red >12); Yellow requires waiver naming why not subcommand promotion; Red fail-closed.
- [ ] OBPI-0.0.45-03: **suite-density-validator** — Walker over `data/validate_suites.json`; counts per-suite audit membership against bands (Green ≤6, Yellow 7–10, Red >10); includes orphan-member detection.
- [ ] OBPI-0.0.45-04: **cli-surface-and-cutover** — `gz validate audit cli-flag-density`, `gz validate audit suite-density`, `gz validate suite density`; suite wiring (`default`/`surface-fidelity`/`cheap-fidelity`) pending ≤100ms perf measurement; recalibration receipt emission/read paths; manpage; folds in #471's noun-verb refactor (parser cutover + ~481-file sweep).
- [ ] OBPI-0.0.45-05: **doctrine-landing** — `.claude/rules/cli.md` three-lane amendment; `docs/governance/advisory-rules-audit.md` scorecard promotion; `.gzkit/rules/governance-core.md` § Proof commands update; Heavy-lane behave smoke.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Recorded as sidecar artifact at
[`adr-interview.json`](./adr-interview.json) — Tier-1 pro-forma answers and
Tier-2 forcing-function record (pre-mortem, WWHTBT, constraint archaeology,
assumption surfacing, 2am operator, reversibility, scope minimization,
closing-question downstream-commitments). The sidecar precedent matches
ADR-0.0.43.

Design dialogue Q1–Q5 settled (single ADR / suite+audit verb shape / hard
cutover / two surfaces / three-lane rule). Operator confirmation token:
`book`.

## Rationale

The two design moves under #471 (cure: refactor `gz validate` to noun-verb
subverbs) and #472 (prophylaxis: install mechanical density validators) are
**operationally inseparable**. Cure without prophylaxis re-accretes within
~12 months — the doctrinal gradient that produced 40+ flags in the first place
is unchanged. Prophylaxis without cure is a paper gate with no precedent to
cite — the existing 40+ flag accretion would be grandfathered, and the
validator would fail-close on its own historical state. Single foundation ADR
is the correct ceremony shape for that coupling.

**Hard cutover (Q3-A) is chosen against repo precedent of transitional shims.**
Shim semantics would be "accept either form" — the density validator would
then have to either (a) ignore the deprecated form, defeating its purpose, or
(b) fail-close on the deprecated form, putting a shim and a fail-close on the
same surface. The anti-vibing mantra binds here: shims are vibing surfaces.
Single-sweep blast radius is shorter pain than indefinite shim maintenance.
The constraint that "shim is canonical" is inherited convention from
ADR-0.0.32's surface-renaming work, where shims were genuinely load-bearing
for byte-parity tests during a rolling cutover; that constraint is not
load-bearing for this ADR's situation.

**Two surfaces over a unified framework (Q4-C over Q4-D)** because flag-per-verb
(UI memory load) and audits-per-suite (doctrinal-coherence drift) are
genuinely different failure modes deserving distinct bands. A unified
"intent-density" framework would require one counting predicate to capture
both with comparable accuracy — empty-framework risk: uniform predicate scores
high on neither failure mode well. Distinct registries make calibration
debuggable; distinct receipts make recalibration auditable per-surface.

**Three-lane rule over hard-deletion of Lite (Q5-4 over Q5-1/Q5-3)** because
behavior modes (`--json`, `--dry-run`, `--check`, `--apply`, `--quiet`,
`--verbose`, `--plain`) are genuine clig.dev-compliant flags that should not
bear Heavy-lane ceremony. Inverting or removing the Lite lane would Heavy-lane
textbook clig.dev-compliant behavior, going past clig.dev's actual
prescriptions. The three-lane rule names what the prior binary collapsed: a
Behavior Mode is a closed enum; a Scope Selector is subject to density check;
a New Verb is unchanged Heavy procedure.

### Rejected alternatives

1. **Two paired foundation ADRs (Q1-B).** Splits a single doctrine across
   `paired_with:` frontmatter; re-instantiates the T1/T2 drift this ADR exists
   to prevent.
2. **Multi-positional CLI shape (Q2-A).** Re-imports the additive-cost
   gradient under a different syntax; density would still hide in positional
   accretion.
3. **Dual-acceptance migration window (Q3-B).** Deprecated form becomes a
   hiding place for new accretion OR forces the density validator to
   fail-close on its own ADR.
4. **Unified intent-density framework (Q4-D).** Empty-framework risk; uniform
   counting predicate papers over genuinely-different failure modes.
5. **Inversion / removal of Lite lane (Q5-1 / Q5-3).** Heavy-lanes textbook
   clig.dev-compliant behavior modes; goes past clig.dev's actual
   prescriptions.

## Evidence

<!-- Pending ADR — evidence cells fill at OBPI closeout per gate. -->

- **Gate 1 (ADR recorded):** this document; `adr_created` ledger event;
  `gz validate --documents` clean.
- **Gate 2 (Tests pass):** pending OBPI-0.0.45-01 through -05 implementation;
  `tests/governance/test_cli_density_validators.py` (anticipated path);
  `gz arb step --name unittest -- uv run -m unittest -q`.
- **Gate 3 (Docs updated):** pending OBPI-0.0.45-04 manpage
  (`docs/user/manpages/gz-validate-suite.md`,
  `docs/user/manpages/gz-validate-audit.md`); OBPI-0.0.45-05 doctrine
  (`.claude/rules/cli.md`, `docs/governance/advisory-rules-audit.md`).
- **Gate 4 (BDD verified):** pending OBPI-0.0.45-05 Heavy-lane behave smoke
  (`features/cli_mode_density.feature`).
- **Gate 5 (Human attests):** pending — heavy-lane + foundation-kind requires
  explicit human attestation per AGENTS.md § Lane & Kind & Sensitivity
  Attestation Matrix. Per-OBPI attestation also required (foundation-kind
  inheritance).

## OBPI Acceptance Note (Human Acknowledgment)

This ADR is **heavy-lane + foundation-kind**. Per AGENTS.md § OBPI Acceptance
Protocol and § Lane & Kind & Sensitivity Attestation Matrix, **every** OBPI
under this ADR requires explicit human attestation (`ATTEST` gate). None of
the five OBPIs is self-closeable.

Each OBPI brief records its acceptance note with:

- The exact `uv run gz` reproduction command.
- The canonical attestation invocation per AGENTS.md § Attestation.
- The ARB receipt IDs (`arb-step-unittest-*`, `arb-step-mkdocs-*`,
  `arb-step-typecheck-*`) — heavy-lane is fail-closed on missing receipt IDs.

## Evidence Ledger

### Provenance

- **Git tag:** `adr-0.0.45` (anticipated on release ceremony)
- **Paired GHIs:** #471 (cure — `gz validate` noun-verb refactor), #472
  (prophylaxis — CLI mode-density doctrine). Both close `superseded` on
  ADR-0.0.45 closeout per `ghi-close` skill destination-routing rule.
- **Operator dialogue:** `/gz-design` Q1–Q5; confirmation token `book`.

### Sidecar artifacts

- [`adr-interview.json`](./adr-interview.json) — Tier-1 + Tier-2 interview
  record (sidecar convention per ADR-0.0.43).

### Inputs & Config

- Anticipated registries: `data/cli_flag_density_thresholds.json`,
  `data/cli_flag_density_floor.json`, `data/cli_flag_density_waivers.json`,
  `data/suite_density_thresholds.json`, `data/suite_density_floor.json`,
  `data/suite_density_waivers.json`, `data/validate_suites.json`,
  `data/validate_audits.json`.

### Source & Contracts

- Anticipated CLI surface: `src/gzkit/cli/parser_validate.py` (refactor to
  noun-verb subverbs).
- Anticipated models: `src/gzkit/governance/trust_audits/cli_density_models.py`.
- Anticipated validators: `src/gzkit/governance/trust_audits/cli_flag_density.py`,
  `src/gzkit/governance/trust_audits/suite_density.py`.

### Tests

- Anticipated unit: `tests/governance/test_cli_density_validators.py`,
  `tests/governance/test_cli_density_models.py`,
  `tests/cli/test_validate_suite_audit.py`.
- Anticipated BDD: `features/cli_mode_density.feature`,
  `features/steps/cli_mode_density_steps.py`.

### Docs

- Anticipated manpages: `docs/user/manpages/gz-validate-suite.md`,
  `docs/user/manpages/gz-validate-audit.md`.
- Anticipated rule update: `.claude/rules/cli.md` (three-lane amendment via
  canonical `.gzkit/rules/cli.md` + sync).
- Anticipated scorecard promotion: `docs/governance/advisory-rules-audit.md`.
- Anticipated proof-command update:
  `.gzkit/rules/governance-core.md` § Proof commands.

### Ledger Event Surface

- `adr_created` (this ADR, Gate-1 emission)
- `obpi_created` × 5 (OBPI-0.0.45-01 through -05)
- `cli_flag_density_recalibrated` (anticipated, post-implementation annual)
- `suite_density_recalibrated` (anticipated, post-implementation annual)
- `density_band_accepted` (anticipated, per operator waiver)

## Alternatives Considered

See § Rationale — Rejected alternatives for the full enumeration with
verbatim Q1–Q5 framings. Summary:

1. Two paired foundation ADRs (Q1-B).
2. Multi-positional CLI shape (Q2-A).
3. Dual-acceptance migration window (Q3-B).
4. Unified intent-density framework (Q4-D).
5. Inversion / removal of Lite lane (Q5-1 / Q5-3).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.45 | Pending | | | Awaiting OBPI-0.0.45-01 through -05 completion + heavy/foundation closeout ceremony |
