# REQ Scope Discipline and Test Shape Doctrine

**Source ADR:** `ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine`
**Rule file:** `.gzkit/rules/tests.md` § REQ Scope Discipline (version `0.5.0`)
**Authored:** OBPI-0.0.59-01 (2026-05-26)

---

## The failure pattern

gzkit's REQ→@covers parity machinery (inherited from airlineops via GHI #113) applied a
single mechanical gate — "a `@covers`-decorated test reachable from Allowed Paths" — to
every REQ uniformly. The gate was correct for airlineops's REQ profile (predominantly
code-behavior REQs against data-warehouse operations; 17% whole-tree filesystem-shaped
ratio). It is structurally wrong for gzkit's REQ profile.

**Quantification (verified 2026-05-25):**

| Scope | Files | Assertions | Filesystem-shaped ops | Ratio |
|-------|-------|-----------|----------------------|-------|
| `tests/` whole tree | 338 | 10,619 | 3,404 | **32%** |
| `tests/governance/` | 68 | 1,314 | 555 | **42%** |
| airlineops (upstream) | — | — | — | ~17% / ~30% |

These filesystem-shaped operations — `grep`-ing prose from production docs to satisfy
`@covers` parity gates — have only one failure mode: a human edits the asserted text.
They detect zero code regressions. The operator's characterization (2026-05-25):
*"staggering find."*

The root cause: gzkit accumulates governance-content REQs (doctrine docs, rule files,
scorecard rows) alongside code-behavior REQs, but the parity gate treats them
identically. The fix is a categorical distinction at the REQ-authoring layer, not a
workaround at the gate layer.

> **The invariance this ADR names:** *The test suite signals what changed in CODE
> BEHAVIOR; it does not signal what changed in CONTENT.* Violating this invariance
> produces ceremony with zero regression-detection signal — worse than no gate, because
> it creates false confidence.

---

## The invariant

Every REQ in an OBPI brief's `## Acceptance Criteria` MUST declare exactly one kind
using the bracketed inline tag syntax:

```text
REQ-X.Y.Z-NN-01 [BEHAVIOR]: the system does X when Y
REQ-X.Y.Z-NN-02 [SUPPORT]: the rule file carries subsection Z
REQ-X.Y.Z-NN-03 [STRUCTURAL-FENCE]: cross-OBPI boundary invariant P holds
```

### Tag case (operator ruling 2026-08-11)

**Tag case carries no meaning; author UPPERCASE; existing lowercase tags are
correct and are NOT to be rewritten.** The binding one-liner lives at
`.gzkit/rules/tests.md` § REQ Scope Discipline; this is its rationale.

Case was never a correctness question. Both readers have always been
case-insensitive — `_REQ_KIND_TAG` (`src/gzkit/governance/trust_audits/briefs.py`)
and `_REQ_KIND_TAG_RE` (`src/gzkit/governance/req_coverage.py`) are both
`re.IGNORECASE`, and the first canonicalizes via `.lower()`.

What owed a ruling was that the *documenting* surfaces disagreed, and one of them
disagreed with itself: until 2026-08-11 this document gave lowercase at § The
invariant and UPPERCASE at § Tag syntax, so an agent consulting the canonical
expansion got both answers from one source and the question recurred per brief.

UPPERCASE wins as the authored form because it is what the majority of every
surface already does, measured 2026-08-11:

| Surface | Case |
|---|---|
| ADR brief corpus | 597 UPPERCASE / 370 lowercase (86 files upper-only, 55 lower-only, 1 mixed) |
| `gz-obpi-specify` SKILL.md | UPPERCASE — the authoring skill agents actually read |
| AGENTS.md § Governance doctrine surfaces | UPPERCASE in prose |

The 370 lowercase tags across 55 briefs are **correct and out of scope for
rewriting**. A ~970-tag sweep buys nothing mechanical — the validators accept
both — and is exactly the taste-driven cleanup `AGENTS.md` § DO IT RIGHT #11
forbids. The ruling settles which form a *new* brief is authored in; it does not
license a migration.

REQs MUST NOT:

- Omit the `[kind]` tag (enforced by `gz validate --req-kind-discipline`, OBPI-0.0.59-02)
- Declare a BEHAVIOR REQ without a `tests/**` path in the brief's Allowed Paths
- Declare a SUPPORT REQ without citing both a validator scope and a ledger event
- Declare a STRUCTURAL-FENCE REQ without a parent-ADR `## Boundary Invariants` anchor

**Port-vs-adapter framing:** This doctrine is a **port** — it declares the abstract
shape every REQ must satisfy. The validator mechanics, the parity-gate proof-channel
resolution, and the decommissioning chore are adapters behind the port.

---

## Three-kind taxonomy with proof-channel detail

### BEHAVIOR

**What it covers:** Code behavior — functions, commands, CLI outputs, state transitions,
error paths, configuration parsing.

**Proof channel:** A `@covers`-decorated test in `tests/**`. This is the existing
pattern, unchanged. The test MUST assert semantics (per `.gzkit/rules/tests.md`
§ invariant 6f), not strings.

**Examples:**
- `REQ-0.0.59-02-01 [BEHAVIOR]: gz validate --req-kind-discipline exits 3 when a brief REQ is missing the [kind] tag`
- `REQ-0.0.3-01-02 [BEHAVIOR]: the FileStore adapter raises StorageError on permission-denied writes`

**Anti-pattern:** A test that `grep`s a production doc for the presence of a substring
is NOT a BEHAVIOR proof. It is a SUPPORT artifact asserting nothing about code behavior.

**GHI #270 reconciliation:** Output-form fixture tests (per
`.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3) are BEHAVIOR REQ proofs.
They test CLI render-code behavior — table box-drawing, JSON parsability, tree
indentation — not file content. The apparent contradiction between tests.md § 6f
(no prose-content assertions) and Invariant 3 (render-form markers required) dissolves
once REQ kind is named: render-form fixture tests target BEHAVIOR (the rendering code),
not CONTENT (the underlying data).

### SUPPORT

**What it covers:** Governance artifacts, doctrine docs, rule files, data files, and
configuration surfaces that *support* behavior but are not behavior themselves. The
artifact exists and has the right shape; its content is not tested by code.

**Proof channel:** The conjunction of two signals:
1. A ledger `artifact_edited` (or equivalent: `artifact_created`, `adr_created`,
   `obpi_created`) event citing the asserted artifact path.
2. A structural validator scope (e.g. `gz validate --documents`, `gz validate
   --advisory-scorecard`, `mkdocs build --strict`) that admits the artifact's shape.

Neither signal alone is sufficient. The ledger event proves the artifact was touched;
the validator proves it passes structural acceptance.

**Examples:**
- `REQ-0.0.59-01-01 [SUPPORT]: .gzkit/rules/tests.md carries a new ## REQ Scope Discipline subsection`
- `REQ-0.0.54-01-03 [SUPPORT]: docs/governance/advisory-rules-audit.md gains scorecard row 58`

**The witness clause (binding, GHI #888).** A SUPPORT REQ **declares** its proof
channel; the resolver never infers one. The declaration is a single trailing clause:

```
Witnessed by `<event_type>` [citing `<path>`] + `gz validate --<scope>`.
```

Exactly one clause per REQ, naming exactly one recognized ledger event type and
exactly one validator scope. `parse_support_citation` reads **only** the clause, so
everything before it is commentary and cannot become the proof channel.

Zero clauses is a **missing** declaration; two clauses, two event types, or two
scopes is an **ambiguous** one. Both are refused — `resolve_support_proof` returns
`undeclared-support`, which never passes — rather than resolved by preference.
Picking a favourite among competing claims is exactly the inference this rule ends.

*Why declaration and not inference.* The parser previously scanned the whole REQ
body for known event names with `in`, a substring test over free text. It could not
distinguish a REQ that **cites** an event from one that **denies the event exists**:
a REQ reading *"the ledger carries NO `corpus_entry_retired` event — measured 0 of
8"* returned that event as its proof channel and resolved green for the very reason
it had been amended. The failure was directional and silent — substring presence can
only **add** types, so a REQ could only ever look more proven than it was. Negation
detection was considered and refused: it is the same substring guessing one level
deeper, and it fails open on the first rephrasing. Reading only a declared clause
closes the class for every phrasing at once.

*Migration state, measured 2026-09-06.* All **13** SUPPORT REQs in live briefs
declare a clause. **162** in terminal (sealed) briefs do not: a sealed brief is a
historical record and is not rewritten to satisfy a later rule. Those resolve
`undeclared-support` if their ADR is ever re-gated at closeout — tracked, not
silently tolerated. Superseded in passing: GHI #647's `_RECURSION_FENCE_SCOPES`
*preference* heuristic for scope selection, which the clause makes unnecessary (the
fence set still guards recursion at resolution time).

**Anti-pattern:** A Python test that does `subprocess.run(["grep", "-q", "## REQ Scope Discipline", ".gzkit/rules/tests.md"])` is NOT a SUPPORT proof. It is a tautological filesystem operation that fails only when a human deletes the heading — zero code regression value.

### STRUCTURAL-FENCE

**What it covers:** Integration-state properties scoped to the parent ADR's boundary.
These are cross-OBPI invariants that cannot be verified per-OBPI (because the invariant
spans multiple OBPIs) and audit at ADR closeout, not at OBPI completion.

**Proof channel:** A parent-ADR `## Boundary Invariants` entry. The entry names the
invariant and the OBPI combination whose completion jointly satisfies it. The parity
gate reports STRUCTURAL-FENCE REQs as `grandfathered` (advisory) at the OBPI layer;
the binding audit runs at ADR closeout.

**Anchor-token syntax (binding — GHI #538).** The entry MUST carry the OBPI-combination
anchor as an explicit token so the binding is mechanical, not merely prose: append
`(OBPI-NN)` — or `(OBPI-NN, OBPI-MM, …)` when the invariant spans several OBPIs — to the
invariant that establishes the claim. The number is the OBPI's own index under its
parent ADR (short form; `OBPI-0.32.0-04` and `OBPI-04` are both accepted). A fence REQ
`REQ-X.Y.Z-NN-MM` resolves `pass` only when its OBPI (`NN`) appears in some invariant's
anchor token — heading presence alone is not proof, because an invariant list that names
no OBPI cannot say *which* invariant proves *which* fence. The exemplar is ADR-0.0.74
(every invariant closes with its `(OBPI-…)` combination). A per-REQ token
(`(REQ-X.Y.Z-NN-MM STRUCTURAL-FENCE — verified at ADR closeout via this invariant)`, the
ADR-0.0.71 form) is an accepted **stricter** variant — it names the exact REQ, which
implies the OBPI. Enforced by `resolve_fence_proof` (`src/gzkit/req_kind_fence.py`) and
`gz validate --req-kind-discipline`.

**Examples:**
- `REQ-0.0.59-NN-NN [STRUCTURAL-FENCE]: after OBPI-02 and OBPI-03 both complete, gz covers OBPI-X --json correctly routes per-kind proof channels for all three kinds`
- `REQ-0.0.3-NN-NN [STRUCTURAL-FENCE]: all adapters in gzkit/adapters/ import only from gzkit/core/ports/, never from gzkit/commands/`

**Origin:** Path D from ADR-pool.obpi-req-taxonomy-scope-fence: "promote scope-fence
REQs to parent-ADR REQs, audited at the parent layer." Adopted as the STRUCTURAL-FENCE
proof channel.

---

## Proof-channel matrix

| Kind | Test `@covers`? | Ledger event? | Structural validator? | Parent-ADR invariant? |
|------|:--------------:|:------------:|:--------------------:|:--------------------:|
| BEHAVIOR | **required** | — | — | — |
| SUPPORT | — | **required** | **required** | — |
| STRUCTURAL-FENCE | — | — | — | **required** |

### Boundary case: suite-level post-conditions (GHI #547)

A *suite-level post-condition* — "`gz test` exits 0 after the decommission sweep",
"the suite still passes after operation X" — is **STRUCTURAL-FENCE**, not SUPPORT.

| Pattern | Kind | Why |
|---------|------|-----|
| "the suite passes after operation X" | **STRUCTURAL-FENCE** | Asserts a suite-integrity *boundary* the operation must not breach — proven by a parent-ADR `## Boundary Invariants` entry, not by a produced ledger event |
| "validator `gz validate --<scope>` exits 0 citing REQ-level evidence" | **SUPPORT** | Asserts a specific validator *dispatch* that produces a ledger event |

The discriminator is **produces-evidence vs. names-a-boundary**: SUPPORT names the
proof artifact that *produces* evidence (a validator run that emits a ledger event);
STRUCTURAL-FENCE names the *boundary* the operation must not breach (the suite
staying green). A suite-pass post-condition is a boundary claim — the suite itself
is the architectural fence — so its proof channel is the parent-ADR `## Boundary
Invariants` entry, never a validator dispatch.

> **Historical note.** `OBPI-0.0.59-05` REQ-05-04 ("gz test exits 0 after the
> decommission sweep") shipped retagged `[BEHAVIOR]→[SUPPORT]`; under this ruling the
> doctrinally-correct kind is STRUCTURAL-FENCE. That attested completion stands — its
> proof was discharged at the time — but this ruling binds *future* suite-invariance
> REQs, closing the gray zone the ADR-0.0.59 closeout spec-reviewer flagged.

---

## Lift targets: what migrates from @covers to ledger+validator

The ~3,404 filesystem-shaped operations in `tests/` are dispositioned by kind:

| Current test shape | Correct disposition |
|-------------------|---------------------|
| `grep` for presence of subsection heading in a rule file | Delete — SUPPORT REQ; ledger event + `gz validate --documents` is the proof |
| `grep` for scorecard row in advisory-rules-audit.md | Delete — SUPPORT REQ; ledger event + `gz validate --advisory-scorecard` is the proof |
| `test -f path/to/doc.md` existence check | Delete or replace — SUPPORT REQ; ledger `artifact_created` + `gz validate --documents` covers it |
| `subprocess.run(["grep", ...])` inside a test asserting doc content | Delete — SUPPORT REQ; structural validator covers it |
| Render-form fixture test (table box-drawing, JSON structure, tree indentation) | Keep — BEHAVIOR REQ proof per GHI #270 reconciliation |
| Test that exercises CLI command and observes output structure | Keep — BEHAVIOR REQ proof |

<!-- gz-validate-skip: command-shape -->
The re-runnable decommissioning chore (`gz chore decommission-tautological-tests`,
OBPI-0.0.59-04) automates this matrix with per-file AST analysis and operator-paced
disposition.

---

## Consequences

### What changes

- Brief authoring requires `[kind]` tag on every REQ (enforced by `gz validate
  --req-kind-discipline` after OBPI-0.0.59-02 ships; advisory until then).
- SUPPORT-kind REQs no longer produce `@covers` test obligations — the parity gate
  accepts ledger event + structural validator as complete proof.
- STRUCTURAL-FENCE-kind REQs are advisory at OBPI layer; binding at ADR closeout.
- New briefs authored after ADR-0.0.59 ships cannot reproduce the GHI #531 anti-pattern.

### What does not change

- BEHAVIOR-kind REQs use the existing `@covers` decorator pattern unchanged.
- `gz covers OBPI --json` still runs; its output schema is extended in OBPI-0.0.59-03
  with per-REQ `kind`, `proof_channel`, and `proof_status` fields.
- The 32%/42% existing rot is not removed by ADR-0.0.59 authoring; it is dispositioned
  by the decommissioning chore (OBPI-0.0.59-04/05) over multiple sessions.

### Reversibility

The three-kind taxonomy is a one-way door (closed-set Pydantic StrEnum). Adding a
fourth kind requires a follow-up foundation ADR amendment. The 18-month pre-mortem
named "process-evidence as undiscovered fourth kind" as the most plausible future
amendment surface.

---

## Brief-time validation

`gz validate --req-kind-discipline` enforces the three-kind taxonomy at brief-authoring
time (ADR-0.0.59 Decision item 2; OBPI-0.0.59-02). It exits 3 (policy breach) on:

- **Mixed-state brief** — a brief whose `## Acceptance Criteria` section contains at
  least one REQ with a `[kind]` tag and at least one without. All-untagged legacy briefs
  pass (grandfathered mode).
- **Per-kind proof-citation gap:**
  - `[BEHAVIOR]` REQ with no `tests/**` path in the brief's `## Allowed Paths` section
  - `[SUPPORT]` REQ whose text lacks both a `gz validate --` scope reference and a ledger
    event keyword (`artifact_edited`, `obpi_created`, `adr_created`, etc.)
  - `[STRUCTURAL-FENCE]` REQ when the parent ADR file has no `## Boundary Invariants` heading

**Tag syntax:**

```text
REQ-X.Y.Z-NN-01 [BEHAVIOR]: code behavior claim
REQ-X.Y.Z-NN-02 [SUPPORT]: artifact claim — gz validate --documents + artifact_edited event
REQ-X.Y.Z-NN-03 [STRUCTURAL-FENCE]: cross-OBPI boundary invariant
```

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | All tagged REQs pass per-kind checks; or all briefs are all-untagged (legacy) |
| 3 | Policy breach — mixed-state or proof-citation gap |

**Preview (dry-run):** run `gz validate --req-kind-discipline` before completing an OBPI
to see the full error list before the completion gate fires.

**gz check integration:** `uv run gz check` includes a "REQ kind discipline" step that
invokes this validator. Failing briefs cause `gz check` to report failure.

---

## Three-channel parity gate (`gz covers OBPI --json`)

`gz covers OBPI-X.Y.Z-NN --json` runs the parity gate at Stage 3 Phase 1b of
the OBPI pipeline. As of OBPI-0.0.59-03, the gate is three-channel-aware:

### Per-REQ fields in JSON output

When an OBPI-scoped target is supplied, each entry in `entries[]` gains:

| Field | Description |
|-------|-------------|
| `taxonomy_kind` | `BEHAVIOR` / `SUPPORT` / `STRUCTURAL-FENCE` / `null` |
| `proof_channel` | `TEST_COVERS` / `LEDGER_PLUS_VALIDATOR` / `PARENT_ADR_INVARIANT` |
| `proof_status` | `pass` / `fail` / `advisory-support` / `grandfathered` / `inferred-*` |
| `ledger_event_ids` | Event IDs (advisory; SUPPORT channel — deferred to future OBPI) |
| `parent_adr_anchor` | Parent ADR invariant anchor (STRUCTURAL-FENCE channel) |

### Rollup fields

`summary` (and per-OBPI / per-ADR rollups) gain:

| Field | Semantics |
|-------|-----------|
| `behavior_uncovered_reqs` | BEHAVIOR-kind REQs without `@covers` — the fail-close count |
| `grandfathered_reqs` | Advisory-only REQs (SUPPORT + STRUCTURAL-FENCE + inferred) |
| `uncovered_reqs` | Total uncovered across all kinds (unchanged for backward compat) |

**Fail-close rule:** only `behavior_uncovered_reqs > 0` triggers a pipeline Stage
3 Phase 1b failure. SUPPORT and STRUCTURAL-FENCE REQs are advisory at the OBPI
layer; they are never fail-closed per-OBPI.

### Grandfathering (legacy untagged REQs)

Legacy briefs without `[kind]` tags receive a one-shot inference classification
(`infer_req_kind`). The inferred kind is stored in `data/req_kind_grandfathering.json`
for operator amendment. Inferred REQs carry `proof_status` of `inferred-behavior`,
`inferred-support`, or `inferred-structural-fence` and are always advisory (never
fail-closed), regardless of coverage state.

### Emergency bypass (`--bypass-req-kind-discipline-once`)

```bash
gz covers OBPI-X.Y.Z-NN --json \
  --bypass-req-kind-discipline-once \
  --bypass-reason "unblocking CI: SUPPORT REQ ledger query deferred"
```

Skips the three-channel parity fail-close for the run and emits a `bypass_used`
ledger event with the mandatory reason string. `--bypass-reason` is required.

**The bypass is deliberately asymmetric — it lives on `gz covers` only, not on
`gz validate --req-kind-discipline` (GHI #546).** The two surfaces enforce the same
discipline at different operator moments, and only one gets an escape hatch by
design:

- `gz covers OBPI-X --json` is the **completion-flow** surface — it gates whether
  work can proceed, so an operator who hits a deferred-SUPPORT-query false-positive
  in CI needs an auditable, ledger-recorded way through. Hence the bypass, which
  *writes* a `bypass_used` event.
- `gz validate --req-kind-discipline` is a **read-only CI/check gate**. It has no
  ledger-write side effect and is intentionally kept that way: a validator that can
  be told to pass is no longer a validator. Adding a bypass would give a pure check
  command a state-mutating escape hatch and a second, redundant place to record
  bypasses. The strict, bypass-free gate is the feature, not a gap.

An operator who genuinely needs to unblock uses the `gz covers` bypass (the
completion-flow surface); `gz validate` stays absolute.

### SUPPORT advisory note

SUPPORT proof-channel verification (ledger-event query at scan time) is advisory
in the current implementation — `gz covers` cannot query live ledger events during
a scan. SUPPORT REQs always receive `proof_status="advisory-support"`. Full
ledger-event querying is deferred to a future OBPI.

---

## Related artifacts

- `ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine` — parent ADR; § Decision
  is the canonical statement; § Alternatives Considered preserves ADR-pool.obpi-req-taxonomy-scope-fence Path A/B/C/D credit
- `.gzkit/rules/tests.md` § REQ Scope Discipline — the binding rule (version `0.5.0`)
- `GHI #531` — categorical category error that prompted this ADR (closed superseded)
- `GHI #165` — non-code REQ evidence channels (closed; SUPPORT + STRUCTURAL-FENCE channels address the request)
- `GHI #270` — tests.md § 6f vs tool-skill-runbook-alignment.md § Invariant 3 contradiction (resolved above)
- `GHI #517` — historical ceremony failure report; ADR-0.0.59 is one of the validation-machine remediations
- `docs/governance/return-to-health-plan-2026-05-30.md` — current recovery plan; the prior emergency plan was removed
- `docs/governance/advisory-rules-audit.md` — scorecard row 59 (Mechanical)
