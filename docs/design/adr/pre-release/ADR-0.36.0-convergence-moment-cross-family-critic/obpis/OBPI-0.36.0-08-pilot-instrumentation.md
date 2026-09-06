---
id: OBPI-0.36.0-08-pilot-instrumentation
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 8
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/second_opinion_pilot.py
  - docs/governance/second-opinion-pilot.md
  - tests/governance/test_second_opinion_pilot.py
  - tests/governance/fixtures/second_opinion_receipts/
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-08-01
  - REQ-0.36.0-08-02
  - REQ-0.36.0-08-03
  - REQ-0.36.0-08-04
  - REQ-0.36.0-08-05
  - REQ-0.36.0-08-06
  - REQ-0.36.0-08-07
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_pilot -v
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-08-pilot-instrumentation: Pilot Instrumentation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #8 - "OBPI-0.36.0-08: **pilot-instrumentation** — The calibrated pilot measuring false blocks, latency, operator reading time, and decisions changed"

**Status:** Draft

## Objective

Build the four measurements that alone can light the dark door. § Target Scope
states the unit definition exactly that way: *"The four measurements that alone
can light the dark door: false blocks, latency, operator reading time, and
decisions changed."* The same four are named in the staging paragraph as the
precondition for OBPI-09 going live — the automatic door ships dark, *"lit only
after a calibrated pilot measures 'false blocks, latency, operator reading time,
and decisions changed.'"*

**And this brief must not light it.** § Why nine forced the split precisely to
prevent that: merging pilot and gate *"makes the gate's own OBPI the judge of
whether it should be on, which is the self-referential shape
`docs/governance/advisory-rules-audit.md` § Self-referential scope domains
names."* Boundary Invariant #3 fences both units by name. This brief produces a
report; an operator, reading it, decides. Nothing shipped here may set, default,
or flip OBPI-09's registry flag.

The honest constraint is that only two of the four are mechanically derivable,
and the brief says so rather than papering it:

| Measurement | Source | Character |
|---|---|---|
| Latency | `duration_ms` on the ARB step receipt of the adversary dispatch, resolved through `gzkit.arb.paths.receipts_root()` | direct |
| Decisions changed | OBPI-05 primary-output hash before the critic ran vs. after | direct |
| False blocks | `refuted` verdicts (OBPI-07 resolution events) whose decision then proceeded with an unchanged primary-output hash | **proxy** |
| Operator reading time | operator-supplied only | **unmeasurable by this code** |

The last two carry the risk this brief exists to contain. A pilot that quietly
defaults operator reading time to zero, or presents its false-block proxy as a
direct count, produces a number that lights a permanent door on a fabrication —
which is the exact failure class the ADR was written against, executed by the
instrument built to prevent it. So: the proxy is labeled a proxy in the emitted
report, and an unsupplied reading time reports `unmeasured`, never a default.

Latency has a prior measurement to reconcile against, and a prior *error* to
avoid repeating. § Mechanics records 11.62–15.50s bare (mean 13.9s) and 19.62s
carrying a 50KB transcript slice; § Boundary records the casualty of assuming
instead — *"a 7-to-8-minute latency figure imported from OBPI-pipeline mechanism
was ~20x high and had to be withdrawn after direct measurement."* Read the
receipt.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/second_opinion_pilot.py` — the four measurements and the report renderer. Verified convention: flat modules under `src/gzkit/`; siblings in this ADR are `second_opinion.py`, `second_opinion_transport.py`, `second_opinion_door.py`, `second_opinion_envelope.py`, `second_opinion_tiering.py`, `second_opinion_resolution.py`.
- `docs/governance/second-opinion-pilot.md` — the pilot protocol and the home for its result. Verified convention: `docs/governance/` holds governance doctrine `.md` files (`advisory-rules-audit.md`, `arb-middleware.md`, `state-doctrine.md`). Verified: `mkdocs.yml` sets `omitted_files: info`, so a page absent from `nav:` does not fail `mkdocs build --strict` — no `mkdocs.yml` edit is in scope.
- `tests/governance/test_second_opinion_pilot.py` — covering tests. Verified convention: `tests/governance/test_*.py`.
- `tests/governance/fixtures/second_opinion_receipts/` — recorded adversary step receipts the latency reader is exercised against via `GZKIT_ARB_RECEIPTS_ROOT`. Verified convention: `tests/governance/fixtures/` exists and holds `.json` fixtures (`foundation_grandfather_golden.json`). Copy real receipts out of the live tree; do not hand-compose one, and never write a receipt into `artifacts/receipts/`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `data/flags.json` — **Boundary Invariant #3.** OBPI-09's dark-door switch. This brief measures; it never flips. An edit here is the self-referential shape § Why nine split these two units to prevent.
- `.claude/hooks/**`, `.claude/settings.json`, `src/gzkit/hooks/**` — OBPI-09 owns both sides of the adapter, wired and off.
- `src/gzkit/arb/**` — read-only. A registered security surface (`data/security_surfaces.json`, category `arb_receipt_chain`): *"receipts are the attestation evidence chain and fabrication anywhere in the chain breaks every claim that cites a receipt."* This brief **reads** receipts through the public `gzkit.arb.paths.receipts_root()` and writes none.
- `artifacts/receipts/**` — never written, never hand-edited. Reading a receipt is evidence; authoring one is fabrication.
- `src/gzkit/second_opinion_envelope.py`, `src/gzkit/second_opinion_resolution.py` — OBPI-05 and OBPI-07 own those surfaces. If a measurement needs a field they do not expose, raise it against the owning brief rather than adding it here.
- `src/gzkit/cli/**` — no new `gz` verb.
- `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, any Step-4b gate — Boundary Invariant #1.
- Paths not listed in Allowed Paths
- New dependencies — STDLIB-FIRST: `json` and `statistics` cover receipt reading and latency aggregation.
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. NEVER: Set, default, flip, or recommend-in-code any value that would enable OBPI-09's `AskUserQuestion` adapter. Boundary Invariant #3: *"Neither brief may light it on its own evidence."* The report is read by an operator; the report is not an actuator.
2. ALWAYS: Resolve the receipts directory through `gzkit.arb.paths.receipts_root()`. NEVER hardcode `artifacts/receipts` — that path is the *default*, overridable by `GZKIT_ARB_RECEIPTS_ROOT` and by `config.arb.receipts_root`, and a hardcoded reader silently measures an empty directory in any project that moved it.
3. ALWAYS: Take latency from the receipt's `duration_ms` field. NEVER wall-clock the measurement inside this module — the receipt is the attested record and the module is not in the dispatch path.
4. ALWAYS: Report operator reading time as `unmeasured` when it has not been supplied by a human. NEVER default it to zero, infer it from token counts, or estimate it. A fabricated fourth measurement lighting a permanent door is this ADR's worst outcome, executed by its own instrument.
5. ALWAYS: Label the false-block figure as a **proxy** in every rendering, and state the proxy's rule inline (a `refuted` verdict whose decision then proceeded unchanged). NEVER present it as a direct count.
6. ALWAYS: Refuse to declare the pilot complete while any of the four is `unmeasured`. A three-of-four pilot is not the precondition § Target Scope names.
7. ALWAYS: Derive *decisions changed* from OBPI-05's primary-output hash pre- and post-verdict. Identical hashes are never counted as changed, whatever the verdict said.
8. NEVER: Add a `gz` verb, write an ARB receipt, wire a hook, or edit Step 4b.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Target Scope — the `pilot-instrumentation` one-line definition and the staging paragraph, including the sentence that must survive every status report: *"Until that door lights, this ADR does not deliver a second opinion at every structured choice."*
- [ ] Parent ADR § Why nine — the **Testability Ceiling** bullet, which is this brief's charter and its fence in one paragraph.
- [ ] Parent ADR § Boundary Invariants #3 — this brief is one of the two units it fences; it is the proof channel for REQ-0.36.0-08-06.
- [ ] Parent ADR § Mechanics (measured, not assumed) — the Latency row (11.62–15.50s bare, mean 13.9s; 19.62s with a 50KB transcript slice). The pilot's latency figure should be reconciled against this, and a large divergence is a finding, not a rounding error.
- [ ] Parent ADR § What the critics themselves could not verify — *"Neither measured the recommendation-classifier's precision, nor the operator's actual reading burden."* Reading burden is still unmeasured; requirement #4 is why this brief does not pretend otherwise.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `docs/governance/advisory-rules-audit.md` § Self-referential scope domains — the named shape this brief's separation from OBPI-09 avoids. Read it before deciding what the report is allowed to do.
- [ ] `docs/governance/arb-middleware.md` — the receipt model, what a step receipt attests, and why a receipt is evidence while a narrated number is not.
- [ ] `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT — operative claim 3, *"Doctrine drift is invariant drift. Silent rule/threshold changes without a witness are the root failure."* The pilot's four numbers become a threshold; the report is their witness.
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — this brief carries BEHAVIOR, SUPPORT and STRUCTURAL-FENCE REQs; read the proof-channel matrix before writing tests, and do NOT author a `@covers` test for the fence.

**Context:**

- [ ] OBPI-0.36.0-02 — the transport whose ARB receipts carry `duration_ms` and the `step.command` argv. Read REQ-0.36.0-02-01: the cross-vendor property is proven *from the argv*, which is also how this module selects second-opinion receipts from every other receipt in the tree.
- [ ] OBPI-0.36.0-05 — the envelope. The primary-output hash is the sole input to *decisions changed*, and it is also half the false-block proxy.
- [ ] OBPI-0.36.0-06 — tier outcomes and their reason strings. Aggregating them is how the pilot reports what the sampler actually selected versus what the enumerated set forced.
- [ ] OBPI-0.36.0-07 — the resolution events. `refuted` verdicts come from here; a resolution shape that cannot be aggregated is a measurement this ADR cannot take.
- [ ] OBPI-0.36.0-09 — the door this pilot may inform and may not open. Read its Denied Paths for the mirror image of requirement #1.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/arb/paths.py::receipts_root` exists and honors `GZKIT_ARB_RECEIPTS_ROOT` — verified; requirement #2 and REQ-0.36.0-08-01 both depend on that override existing.
- [ ] `artifacts/receipts/` exists and holds `arb-step-*.json` receipts — verified; note `artifacts/` is git-ignored, so this is runtime state and tests must point the env override at a fixture directory rather than at the live tree.
- [ ] `data/schemas/arb_step_receipt.schema.json` exists and lists `duration_ms` and `step.command` as required fields — verified.
- [ ] `docs/governance/` exists and holds `.md` doctrine files — verified.
- [ ] `src/gzkit/second_opinion_envelope.py` (OBPI-05) and `src/gzkit/second_opinion_resolution.py` (OBPI-07) exist — STOP if missing: three of the four measurements have no source without them, and a pilot reporting one of four is not the precondition the dark door needs.
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_pilot.py`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/governance/second-opinion-pilot.md`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_pilot.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/fixtures/second_opinion_receipts/`

**Existing Code (understand current state):**

- [ ] `src/gzkit/arb/paths.py` — read the whole file. The three-step resolution order (env override, config, default) is requirement #2 in code, and the module is 50 lines.
- [ ] `data/schemas/arb_step_receipt.schema.json` — read the required-field list. `duration_ms` is `integer, minimum 0` and `step.command` is a non-empty argv array; both are guaranteed present on any valid receipt, so the reader needs no defaulting branch.
- [ ] `artifacts/receipts/` — open one real `arb-step-*.json` and confirm the field shape against the schema before writing the parser. Observed, not assumed.
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py:97-135` — `_receipt_proves_cross_vendor` and `_load_adversary_receipt`, **read-only**. They already select an adversary receipt from a run id and prove the vendor property from argv; borrow the reading technique, never the file. Boundary Invariant #1.
- [ ] `docs/governance/state-doctrine.md` — the Layer-1/2/3 model. The pilot report is a **Layer-3 derived view**: it is regenerated from receipts and ledger events and is never source-of-truth for its own numbers.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_second_opinion_pilot -v
uv run gz validate --req-kind-discipline
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Produce a real adversary receipt to measure, through the shipped transport.
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute: operator reading time can be estimated from token counts."

# The pilot report over the live receipts tree and ledger. Latency comes from
# the receipts' duration_ms; operator reading time reports `unmeasured`.
uv run python -m gzkit.second_opinion_pilot report

# The machine-readable form the operator's ruling will cite.
uv run python -m gzkit.second_opinion_pilot report --json

# The receipts root is resolved, never hardcoded: point it elsewhere and the
# report follows (REQ-08-01).
GZKIT_ARB_RECEIPTS_ROOT=/tmp/second-opinion-pilot-fixture uv run python -m gzkit.second_opinion_pilot report

# Supply the one measurement no code can take, then re-render.
uv run python -m gzkit.second_opinion_pilot record-reading-time --seconds 42 --decisions 6 --attestor g0
uv run python -m gzkit.second_opinion_pilot report

# The report refuses to declare the pilot complete while a measurement is
# missing — the dark door's precondition is four of four (REQ-08-05).
uv run python -m gzkit.second_opinion_pilot status

# The door is untouched by its own instrument: still at its registry default.
uv run gz flags
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.36.0-08-01 [BEHAVIOR]: Given `GZKIT_ARB_RECEIPTS_ROOT` pointed at a fixture directory of adversary step receipts, when the latency measurement runs, then it aggregates the `duration_ms` values found there — a reader that measures the default `artifacts/receipts` regardless of the override fails.
- [ ] REQ-0.36.0-08-02 [BEHAVIOR]: Given no operator-supplied reading time, when the report renders, then that measurement reads `unmeasured` — never `0`, never an estimate — and given a supplied value, then that value is reported unchanged.
- [ ] REQ-0.36.0-08-03 [BEHAVIOR]: Given envelope pairs whose primary-output hash differs before and after the critic ran, when *decisions changed* is computed, then only the differing pairs are counted; identical hashes are never counted as changed regardless of the verdict recorded against them.
- [ ] REQ-0.36.0-08-04 [BEHAVIOR]: Given a set of `refuted` verdicts, when the false-block figure is rendered in either the text or the `--json` form, then it is labeled a proxy and its rule is stated alongside the number — a rendering that emits the count without the label fails.
- [ ] REQ-0.36.0-08-05 [BEHAVIOR]: Given any one of the four measurements unmeasured, when pilot status is requested, then it reports incomplete and names the missing measurement; only a four-of-four set reports complete.
- [ ] REQ-0.36.0-08-06 [SUPPORT]: `docs/governance/second-opinion-pilot.md` records the pilot protocol — the four measurements, the source each is read from, and the explicit statement that the report informs an operator ruling and never enables the door itself. Witnessed by `artifact_edited` citing `docs/governance/second-opinion-pilot.md` + `gz validate --documents`.
- [ ] REQ-0.36.0-08-07 [STRUCTURAL-FENCE]: Across the delivered set, no artifact of this unit sets, defaults, or flips the `AskUserQuestion` adapter's registry entry — the pilot reports and an operator rules, so the door's state is never changed by its own instrumentation — parent ADR § Boundary Invariants #3 (OBPI-08, OBPI-09).

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
