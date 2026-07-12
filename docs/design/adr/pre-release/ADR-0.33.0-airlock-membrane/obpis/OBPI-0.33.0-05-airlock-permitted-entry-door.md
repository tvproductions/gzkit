---
id: OBPI-0.33.0-05-airlock-permitted-entry-door
parent: ADR-0.33.0-airlock-membrane
item: 5
lane: Heavy
status: Completed
req_atomic:
  # REQ-01..06 are BEHAVIOR — each one indivisible unit of labor with no sub-step
  # below it, implemented as a single Red-Green-Refactor cycle: 01 the permissive
  # gate that ALWAYS fires, 02 reconnaissance-first default, 03 the light-repair
  # ceiling, 04 the trip-to-fresh-transit tripwire, 05 no-private-fork (consume
  # the shared primitive), 06 the silent-bypass closure. REQ-07 is STRUCTURAL-FENCE
  # (no code labor — proven by parent-ADR BI-3, audited at ADR closeout). No labor
  # subdivided below any REQ.
  - REQ-0.33.0-05-01
  - REQ-0.33.0-05-02
  - REQ-0.33.0-05-03
  - REQ-0.33.0-05-04
  - REQ-0.33.0-05-05
  - REQ-0.33.0-05-06
  - REQ-0.33.0-05-07
---

# OBPI-0.33.0-05-airlock-permitted-entry-door: Airlock Permitted Entry Door

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`
- **Checklist Item:** #5 - "permitted-entry door (new surface): the ad-hoc/spurious entry -- reconnaissance-first, light-repair-at-most, permissive ceremony; closes the silent-bypass hole; a discovered need beyond light repair trips a fresh transit through pipeline/mx. [BEHAVIOR; gated-breadth]"

**Status:** Completed

## Objective

Build the third airlock door — a new `permitted-entry` verb for the ad-hoc/spurious
entry (reconnaissance for comprehension, light repair at most, bracketing action both
upstream of planning and downstream of action) — that CONSUMES the shared airlock primitive
(`gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit`) at the lightest,
PERMISSIVE intent, so that the acknowledge-and-decide gate STILL fires on every ad-hoc entry
(parent ADR BI-2), the silent-bypass hole finally closes, no private airlock is ever forked,
and any discovered need beyond light repair TRIPS a fresh transit through the pipeline or mx
door rather than being smuggled inline. NOTE (reconciled to the hull, option c): the delivered
primitive exposes NO ceremony-profile parameter and is diagnostic-only at the door — per-door
ceremony calibration (permissive vs. tight) and the brief-less DECLARE input are the attested
deferred WWHTBT-(a) frontier (OBPI-02/03). This door wires the diagnostic-only tracer at
permissive intent, with the calibration distinction a NAMED RESIDUAL, never a parameter
asserted as already-built. The "gate always fires" property is realized now (the door always
CALLS the primitive); the ceremony-weight distinction matures with the frontier.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a net-new operator CLI verb (`permitted-entry`) — a runtime
contract surface humans invoke — plus its argparse wiring under `src/gzkit/cli/` and its
command manpage. It is the door that closes the silent-bypass hole named in the parent ADR's
Consequences #2, so its ceremony (permissive but never skipped) is itself an external
covenant, not internal plumbing.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). Disjoint from every sibling OBPI. -->

- `src/gzkit/commands/permitted_entry.py` — **CREATE**: the `permitted-entry` command handler; DECLAREs the ad-hoc entry (target + recon/light-repair intent), CALLS `gzkit.airlock.enter.airlock_enter` on the way in and `gzkit.airlock.exit.airlock_exit` on the way out at permissive intent (the delivered primitive has no ceremony-profile parameter — calibration deferred to the frontier), and TRIPS a fresh-transit recommendation when the declared work exceeds the light-repair ceiling
- `src/gzkit/cli/parser_governance.py` — register the additive `permitted-entry` verb ONLY: one `commands.add_parser("permitted-entry", ...)`, its `--target` / `--recon` / `--repair` / `--dry-run` arguments, and a `_permitted_entry_dispatch` that lazy-imports the handler (mirrors the `gz mx` registration in this same file)
- `tests/test_permitted_entry.py` — **CREATE**: `@covers`-decorated REQ tests for the door (permissive gate always fires, recon-first default, light-repair ceiling, trip-to-fresh-transit, no-private-fork, silent-bypass closure)
- `src/gzkit/cli/main.py` — read-only reference: the CLI-parser tests import `_build_parser` from here to exercise the assembled `permitted-entry` subparser (argparse mutual-exclusion + single-`--repair` smuggling fences, GHI #678). NOT edited by this OBPI
- `docs/user/manpages/permitted-entry.md` — **CREATE**: the `permitted-entry` command manpage (Gate 3 docs coherence; contract + EXAMPLES with real CLI output)
<!-- Coupled coherence surfaces a NET-NEW heavy-lane CLI verb mandates (AGENTS.md
     Rule 1a coupled-surface coherence + .claude/rules/cli.md § New Subcommand;
     operator-ratified allowlist amendment 2026-07-11). Each is a consumer that a
     new verb must satisfy in the same change or a coherence test fails closed. -->
- `docs/user/manpages/index.md` — add the `permitted-entry` index row (doc-coverage `index_entry` surface; `test_doc_coverage`)
- `docs/user/runbook.md` — add the operator-runbook `permitted-entry` block (`gz cli audit` operator_runbook cross-coverage)
- `docs/governance/governance_runbook.md` — add the `gz permitted-entry` reference (`gz cli audit` governance_runbook cross-coverage)
- `config/doc-coverage.json` — declare the `permitted-entry` command's documentation obligations (`test_real_manifest_covers_all_discovered_commands`)
- `src/gzkit/governance/trust_audits/cli.py` — add the `_NO_SKILL_VERBS` waiver for `permitted-entry` (operator-invoked ad-hoc door, not a recurring agent workflow; Invariant 1 skill-alignment, mirrors the `obpi repudiate` precedent)
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` — parent ADR `## Decision` + `## Boundary Invariants` (read-only reference; NOT edited by this OBPI)
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-05-airlock-permitted-entry-door.md` — this brief (evidence)

## Denied Paths

<!-- The shared primitive and the sibling doors are out of scope: this OBPI
     CONSUMES the airlock, it never modifies it, forks it, or touches a sibling
     door's surface. -->

- `src/gzkit/airlock/**` — the shared airlock primitive (`gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit`, the SeamMap/Preflight/DriftDiff models, the gate) is authored by OBPI-01/02/03; this OBPI CONSUMES it only and NEVER modifies or forks it (parent ADR BI-3 — one extracted primitive the doors CALL, never fork)
- `src/gzkit/pipeline_runtime.py`, `src/gzkit/commands/pipeline.py` — the pipeline door (OBPI-02/03) is the calibration reference, read-only here; the permitted-entry door adapts to the primitive, it does not re-open the pipeline wiring
- `src/gzkit/mx/**`, `src/gzkit/commands/mx_cmd.py` — the mx door is OBPI-04; permitted-entry only NAMES mx as a fresh-transit destination, it never wires the mx door
- `docs/governance/work-phases-and-airlock.md`, `docs/governance/four-phases-of-work.md` — the doctrine-lawful promotion is OBPI-06 (the one-way door); not touched here
- New runtime dependencies, CI files, lockfiles — the door stands on the already-attested airlock primitive + `gz ontology reach` floor; no new dependency
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. NEVER/ALWAYS language. -->

1. REQUIREMENT: Deliver ONLY the permitted-entry door — a net-new `permitted-entry` verb that CONSUMES the shared `gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit` primitive at permissive intent (the delivered primitive has NO ceremony-profile parameter; per-door calibration is the deferred frontier). No new airlock mechanism is authored here; the door is a thin adapter over the existing primitive.
2. ALWAYS: the acknowledge-and-decide gate FIRES on every `permitted-entry` transit — realized now by the door ALWAYS CALLING the shared primitive. "Permissive" is the door's INTENT (lightest ceremony); the delivered primitive has no ceremony-profile parameter, so the permissive-vs-tight WEIGHT distinction is the deferred calibration frontier — but the gate is NEVER set to "skip" regardless (parent ADR BI-2: the reason selects the door and its ceremony weight, never whether the gate fires; "a gate with a hole is not a gate").
3. NEVER: fork a private airlock. The door MUST call the shared primitive from `src/gzkit/airlock/**`; it MUST NOT define its own enter/exit/gate logic, its own SeamMap, or a parallel airlock variant (parent ADR BI-3 — door-drift is the failure this forbids).
4. ALWAYS: a permitted-entry that DISCOVERS a need beyond light repair TRIPS a fresh transit through the pipeline door (intentional change) or the mx door (defect repair). The door NEVER absorbs work beyond the light-repair ceiling inline (parent ADR BI-5 — discovered correction routes as a fresh transit; the four-phases cross-phase tripwire — never smuggle real work into a reconnaissance).
5. ALWAYS: the door DEFAULTS to reconnaissance (inspection for comprehension); action is bracketed, not assumed. Light repair is the CEILING, not the default, and the ad-hoc entry may carry no repair at all.
6. NEVER: leave the silent-bypass hole open. An ad-hoc/spurious entry that previously crossed NO membrane MUST now cross the airlock via this door — the door's existence is what makes the membrane total rather than mostly (parent ADR Consequences #2).
7. NEVER: emit or record the permitted-entry gate as a completion attestation. The acknowledge-and-decide gate is a DIFFERENT sort from Gate-5 completion attestation and never spends the sacred word (parent ADR BI-3 of the attestation canon; § Decision).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision + § Intent — quote the three-doors line this OBPI implements** verbatim into `### Implementation Summary`. The § Intent contract is: "Three entry-reasons, three doors: pipeline (design implementation -- intentional change), mx/ghi (defect repair -- correction to a desired state), and permitted-entry (ad-hoc/spurious -- reconnaissance for comprehension with light repair at most, bracketing action: upstream of planning and downstream of action)." The § Decision ceremony line is: "ceremony scales by door (pipeline tight; mx corrective; permitted-entry permissive), calibrated to the pipeline". These two clauses ARE this OBPI's contract.
- [ ] Parent ADR § Boundary Invariants #2 (the gate fires on every entry; the reason/door selects ceremony weight, never whether the gate fires) — the fail-closed anchor for REQ-01.
- [ ] Parent ADR § Boundary Invariants #3 (one extracted primitive; never fork) and #5 (discovered correction routes as a fresh transit) — the anchors for REQ-05 and REQ-04.
- [ ] Parent ADR § Consequences #2 (the silent-bypass hole closes) and #4 (ceremony-creep bypass) — the why-frame and the tension REQ-06 and REQ-02 hold.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`

> **STOP:** If you cannot quote the parent ADR § Decision line that names the three doors and the "permitted-entry permissive" ceremony calibration, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until that quote is in hand.

> **GATED-BREADTH PRECONDITION (STOP):** This OBPI is gated breadth. It does NOT begin until
> OBPI-0.33.0-02's section-5 live negative control BITES LIVE — i.e. `uv run gz validate
> --qc-binding` is green and the un-accounted-seam NC genuinely cannot be forced (un-forced
> production, meta-validated per ADR-0.0.74). If OBPI-02's landing keystone has not landed and
> its NC does not bite, STOP: this door has no proven primitive to consume. Confirm the NC is
> live before authoring any code.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — REQ-kind discipline the Acceptance Criteria below obey (REQ-01..06 BEHAVIOR → `@covers` test proof channel; REQ-07 STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` anchor, no `@covers` test)
- [ ] `.claude/rules/hexagonal-architecture.md` — the door is an adapter over the airlock port; it consumes domain-typed enter/exit, never a private mechanism

**Context:**

- [ ] Sibling OBPI-0.33.0-02 (airlock-in) + OBPI-0.33.0-03 (airlock-out) — the primitive this door CALLS; read their `gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit` signatures (brief-path-centric; NO ceremony-profile parameter — per-door calibration is the deferred frontier)
- [ ] Sibling OBPI-0.33.0-04 (mx door) — the corrective-scoped sibling that NAMES the same primitive; permitted-entry NAMES mx as a fresh-transit destination but never wires it
- [ ] `src/gzkit/commands/mx_cmd.py` + `src/gzkit/cli/parser_governance.py` (`gz mx enter/exit`) — the closest precedent for a door that calls a shared session primitive and registers a top-level verb with a lazy-import dispatch

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/airlock/**` present with `gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit` — the primitive this door consumes (OBPI-01/02/03 landed). NOTE: no ceremony-profile parameter; diagnostic-only at the door (real-entry accounting deferred); consume as-shipped
- [ ] `uv run gz validate --qc-binding` green (OBPI-02 section-5 live NC bites; the gated-breadth precondition above)
- [ ] `src/gzkit/cli/parser_governance.py` present with the top-level `commands` subparser registry — the `permitted-entry` verb registers here
- [ ] Parent ADR `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` present, registered in `gz state`, and carrying a `## Boundary Invariants` section (BI-2/BI-3/BI-5 anchors)

**Existing Code (read; do NOT modify — establishes the conventions this door mirrors):**

- [ ] `src/gzkit/airlock/**` — the enter/exit/gate primitive the door consumes (`airlock_enter` / `airlock_exit`; NO ceremony-profile parameter; diagnostic-only at the door; calibration deferred) (read-only; DENIED for edit)
- [ ] `src/gzkit/commands/mx_cmd.py` — how a door builds a session over a shared primitive and refuses to narrow its way out of the gate
- [ ] `src/gzkit/cli/parser_governance.py` (`gz mx` registration, lines ~758–825) — how a new top-level verb registers end-to-end (add_parser + arguments + lazy-import dispatch + `set_defaults(func=…)`)

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
- [ ] `docs/user/manpages/permitted-entry.md` authored with real CLI-output EXAMPLES

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- CONSTRUCTION HOUSEKEEPING (lint, type, test) proving the codebase is healthy.
     AUTHORING CONTRACT: single-program, shell-less invocations only — no &&, ||,
     |, ;, $(...), or redirects (GHI #415). One command per line. -->

```bash
uv run gz validate --documents
uv run gz obpi validate --adr ADR-0.33.0-airlock-membrane --authored
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --qc-binding
uv run -m unittest tests.test_permitted_entry -v
```

## Demo

<!-- THE YIELDED PRODUCT: the permitted-entry door with the permissive gate that
     STILL fires. Concrete, runnable invocations (not --help). Harvested by the
     closeout walkthrough. -->

> **Reconciled to the hull (option c, attested 2026-07-11):** the delivered
> primitive is diagnostic-only at the door, with per-door ceremony calibration
> and the brief-less DECLARE input deferred to the calibration frontier. The
> transits below are the TARGET behavior; this increment wires the diagnostic-
> only tracer at permissive intent — the gate always fires (the door always
> calls the primitive) and logs its decision; it does not yet block.

<!-- gz-validate-skip: command-shape -->
```bash
# Reconnaissance-first: enter the permitted-entry door to inspect a region for
# comprehension. The acknowledge-and-decide gate STILL fires — permissive
# ceremony (the lightest profile), but never skipped (BI-2).
uv run gz permitted-entry --target src/gzkit/quality.py --recon

# The permissive gate fires and reaches GO on a fully-accounted recon (dry-run).
uv run gz permitted-entry --target docs/governance/state-doctrine.md --recon --dry-run

# Light repair at most: a one-line typo fix under the light-repair ceiling still
# crosses the membrane — the gate fires, the transit is logged to L2.
uv run gz permitted-entry --target README.md --repair "fix typo in badge line" --dry-run

# A discovered need BEYOND light repair TRIPS a fresh transit: the door refuses to
# absorb real work inline and names the door to route through (pipeline | mx).
uv run gz permitted-entry --target src/gzkit/ledger.py --repair "refactor event schema" --dry-run
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test in tests/**; STRUCTURAL-FENCE proves via a parent-ADR Boundary
     Invariants anchor (audited at ADR closeout). The six door behaviors (items
     01 through 06) are BEHAVIOR; the attestation-distinction fence (item 07) is
     STRUCTURAL-FENCE. -->

- [ ] REQ-0.33.0-05-01 [BEHAVIOR]: `permitted-entry` ALWAYS fires the acknowledge-and-decide gate on every transit — realized by the door ALWAYS CALLING the shared primitive (diagnostic-only posture; the decision is surfaced, not yet fail-closing — the blocking calibration is the deferred frontier); a `@covers(REQ-0.33.0-05-01)` test in `tests/test_permitted_entry.py` drives the door and asserts the primitive is invoked (a gate event/decision is produced) on a bare recon entry, and asserts there is NO code path by which a permitted-entry transit reaches its exit without the gate firing (parent ADR BI-2 — the reason/door selects ceremony weight, never whether the gate fires).
- [ ] REQ-0.33.0-05-02 [BEHAVIOR]: the door DEFAULTS to reconnaissance (inspection for comprehension) — invoked with `--recon` (or no repair intent), it performs the airlock declare→ping→reconcile→gate beats and yields a comprehension report WITHOUT requiring or performing any change; a `@covers(REQ-0.33.0-05-02)` test asserts a recon-only invocation completes with no file mutation and a non-empty seam/comprehension report.
- [ ] REQ-0.33.0-05-03 [BEHAVIOR]: light repair is the CEILING — the door admits at most a light-repair intent; a `@covers(REQ-0.33.0-05-03)` test asserts a within-ceiling light-repair intent is admitted (crosses the gate, surfaced as admitted) while an intent exceeding the light-repair ceiling is NOT admitted for inline handling and instead SURFACES a fresh-transit recommendation. Consistent with the door's diagnostic-only posture (REQ-0.33.0-05-01, option-c reconcile): the door is a membrane, not an editor — it never performs the repair inline regardless, so the ceiling SURFACES its verdict diagnostically rather than fail-closing. The classifier is a best-effort heuristic tripwire, NOT a semantic guarantee; reliable free-text scope-classification (and any fail-closing on it) is the deferred calibration frontier.
- [ ] REQ-0.33.0-05-04 [BEHAVIOR]: a discovered need beyond light repair TRIPS a fresh transit — given an entry whose declared/discovered work exceeds the light-repair ceiling, the door PRESENTS BOTH fresh-transit doors with their selection criteria (pipeline = intentional change, mx = defect repair) and does NOT absorb the work inline. The door does NOT authoritatively guess which door: defect-vs-intentional cannot be reliably inferred from free text, and an open-ended keyword list always misroutes some corrective phrasing (Codex Step-4b refutation, GHI #678) — so the captain chooses. This satisfies the parent ADR's binding requirement (BI-5: discovered correction routes as a fresh transit, never smuggled inline), which is about ROUTING as a fresh transit, not auto-selecting the door. A `@covers(REQ-0.33.0-05-04)` test asserts that both doors are presented across intentional AND corrective phrasings, that no authoritative primary is emitted, and that no inline mutation occurred.
- [ ] REQ-0.33.0-05-05 [BEHAVIOR]: the door NEVER forks a private airlock — it consumes the shared `gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit` primitive; a `@covers(REQ-0.33.0-05-05)` test asserts the handler calls the shared primitive (e.g. patching `gzkit.airlock.enter.airlock_enter` / `gzkit.airlock.exit.airlock_exit` observes the door routing through them) and asserts `src/gzkit/commands/permitted_entry.py` defines no parallel enter/exit/gate/SeamMap of its own (parent ADR BI-3 — one extracted primitive the doors CALL, never fork).
- [ ] REQ-0.33.0-05-06 [BEHAVIOR]: the silent-bypass hole closes — an ad-hoc/spurious entry that formerly crossed no membrane now crosses the airlock via this door; a `@covers(REQ-0.33.0-05-06)` test asserts that the ad-hoc entry path produces an `airlock_in` (and, on exit, `airlock_out`) L2 ledger event, so the previously membrane-less surface now leaves an accountable transit record (parent ADR Consequences #2 — the membrane becomes total rather than mostly).
- [ ] REQ-0.33.0-05-07 [STRUCTURAL-FENCE]: the door NEVER emits or records the permitted-entry acknowledge-and-decide gate as a Gate-5 completion attestation — the airlock books `airlock_in`/`airlock_out` L2 encounter events only, never a completion-attestation event; proven by the parent ADR `## Boundary Invariants` #3 ("The airlock gate is acknowledge-and-decide, never completion attestation"), audited at ADR closeout (STRUCTURAL-FENCE proof channel, ADR-0.0.59 — no `@covers` test; the every-transit gate never spends the sacred word).

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

### Step 4b — Independent Adversarial Validation

**Adversary:** Codex (`codex` / codex-cli 0.144.1) — a different-vendor model (tier 1,
cross-vendor), so it shares none of this agent's blind spots. Dispatched via
`codex-companion adversarial-review`, prompted to REFUTE the completion claim.

**Final verdict:** NOT-REFUTED (Codex `approve`, "No material findings"). Reached after
NINE refute→fix cycles — the cross-vendor adversary drove out every concrete defect a
same-vendor (Claude) adversary had passed:

1. REQ-04 keyword misroute → removed authoritative routing; door presents BOTH doors, captain chooses
2. `airlock_exit` unpaired transit → tracked out-of-scope **GHI #679** (shared primitive `src/gzkit/airlock/exit.py`, DENIED path, affects all doors)
3. `--recon` silent-drops repair → `--recon`/`--repair` mutually exclusive, fail-fast
4. repeated `--repair` collapse → `_SingleValueAction` rejects duplicates
5. punctuation evades ceiling → `_intent_tokens` normalizes to alphanumeric core
6. Rich markup injection/crash → operator text escaped via `rich.markup.escape`
7. empty target → anonymous transit → rejected at argparse + handler
8. vague-prefix misbind + Markdown injection → exact-id-only resolution + intent sanitize
9. sanitize-as-identity collision → lossless target identity; unrepresentable targets rejected

**Claims broken and resolved:** the REQ-02 (footprint accuracy) and REQ-06 (transit
accountability) claims were broken repeatedly (misbinding, injection, identity collision)
and each was resolved in-scope; the REQ-04 routing claim was broken (keyword misroute) and
resolved by removing the heuristic pick entirely. Two items are accepted as tracked/deferred
per operator ruling: **GHI #679** (shared-primitive exit atomicity, out of this OBPI's scope)
and the ceiling classifier's **semantic precision** (the operator-attested deferred
calibration frontier — this door is diagnostic-only and never edits, so a misclassification
smuggles no work).

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


A beyond-ceiling intent presents both fresh-transit doors (no misroute), and a non-dry-run books a paired, lossless-identity L2 transit:

```
$ uv run gz permitted-entry --target src/gzkit/ledger.py --repair "rewrite the module to eliminate the deadlock" --dry-run
permitted-entry recon: permitted-entry:src/gzkit/ledger.py
  footprint (declared bodies): src/gzkit/ledger.py
permitted-entry: intent exceeds the light-repair ceiling — not admitted inline (the door never edits). Route a fresh transit and choose the door — pipeline (intentional change) or mx (defect repair): rewrite the module to eliminate the deadlock
```

Full suite 7013/7013 green (receipt `arb-step-unittest-f5002c6659c34c8bade14edeb1575610`); Step-4b independent adversarial validation via Codex (cross-vendor tier 1) returned NOT-REFUTED ("No material findings") after nine refute-fix cycles.

### Implementation Summary


- Files created: `src/gzkit/commands/permitted_entry.py` (door handler, thin adapter over the shared airlock primitive); `tests/test_permitted_entry.py` (21 tests); `docs/user/manpages/permitted-entry.md`
- Files modified: `src/gzkit/cli/parser_governance.py` (permitted-entry verb + `_SingleValueAction` + `_nonblank_target`); `src/gzkit/governance/trust_audits/cli.py` (`_NO_SKILL_VERBS` waiver); `config/doc-coverage.json`; `docs/user/manpages/index.md`; `docs/user/runbook.md`; `docs/governance/governance_runbook.md`
- Behavior: consumes the shared `airlock_enter`/`airlock_exit` primitive (never forks, BI-3); the acknowledge-and-decide gate fires on every transit (BI-2); a beyond-ceiling intent presents BOTH fresh-transit doors (no authoritative heuristic guess); blank/backtick/newline targets rejected; lossless-identity paired `airlock_in`/`airlock_out` L2 transits (REQ-06)
- Tests added: 21 (@covers for 6 BEHAVIOR REQs + CLI-parser smuggling fences + accountability regressions)
- Date completed: 2026-07-12
- Attestation status: operator-verbatim "attest completed" (g0)
- Defects noted: GHI #679 (shared-primitive airlock_exit atomicity, out of scope); ceiling semantic-precision = operator-attested deferred calibration frontier

## Tracked Defects

- RESOLVED (2026-07-11, attestor g0): REQ-count drift (7 declared vs 6 acceptance criteria) fixed by adding REQ-0.33.0-05-07 [STRUCTURAL-FENCE] — the attestation-distinction constraint, proven by parent-ADR BI-3, restoring the 1:1 requirements↔acceptance convention held by sibling OBPI-02/03/04.
- TRACKED → GHI #679 (2026-07-11): the SHARED airlock primitive (`src/gzkit/airlock/exit.py`) books its `airlock_out` L2 event after its reach/drift/brief work, so an exit-side I/O failure can leave an unpaired transit (`airlock_in` with no `airlock_out`). Surfaced by the Codex (tier-1) Step-4b adversary. Out of scope for THIS door (DENIED path `src/gzkit/airlock/**`; forking a private compensation violates BI-3) — the fix belongs to the airlock-primitive surface (OBPI-01/02/03) and affects all three doors. Mitigated here: `airlock_exit` is called from a nested `finally` so it is always attempted once `airlock_enter` fired. Operator-ratified route (GHI + complete, 2026-07-11).

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — permitted-entry airlock door (OBPI-0.33.0-05): 6 BEHAVIOR REQs covered (behavior_uncovered=0); full suite green — receipts arb-step-unittest-f5002c6659c34c8bade14edeb1575610, arb-ruff-f9cc5a1336d24dd6916472eba07acee3, arb-step-typecheck-9954ecb4a44e458e820f28c898416558, arb-step-mkdocs-b7332d22c81242f1a45a2d00a3270ece; Step-4b independent adversarial validation via Codex (cross-vendor tier 1) returned NOT-REFUTED after nine refute-fix cycles that drove out every concrete defect (routing misroute, flag-smuggling, markup injection, target accountability, identity collision); airlock_exit atomicity tracked out-of-scope GHI #679; ceiling semantic-precision the attested deferred calibration frontier.
- Date: 2026-07-12

---

**Date Completed:** 2026-07-12

**Evidence Hash:** -
</content>
</invoke>
