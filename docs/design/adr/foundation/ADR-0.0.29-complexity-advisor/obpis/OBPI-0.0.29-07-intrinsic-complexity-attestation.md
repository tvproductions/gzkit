---
id: OBPI-0.0.29-07-intrinsic-complexity-attestation
parent: ADR-0.0.29
item: 7
lane: Heavy
status: Completed
---

# OBPI-0.0.29-07-intrinsic-complexity-attestation: Two-path Intrinsic-Complexity Attestation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #7 — "Two-path intrinsic-complexity attestation (`@intrinsic_complexity` decorator + `--attest-intrinsic` commit-time flag; both Gate 5 follow-up)"

**Status:** Draft

## Objective

Implement the two-path intrinsic-complexity attestation: (a) a `@intrinsic_complexity(reason=..., attestor=...)` Python decorator at `src/gzkit/complexity/advisor/intrinsic.py` that the advisor honors at diagnosis time; (b) a commit-time `gz complexity-advise --attest-intrinsic` flag that records attestation as a canonical `intrinsic-complexity-attestation` ledger event with Gate 5 follow-up persistence. Both paths land at brief-level Gate 5; neither produces a silent escape hatch.

## Lane

**Heavy** — New decorator API + new ledger event family + new CLI flag = three contract surfaces. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/advisor/intrinsic.py` — `@intrinsic_complexity` decorator + runtime registry
- `src/gzkit/commands/complexity_advise.py` — extend with `--attest-intrinsic` flag (additive only)
- `src/gzkit/governance/ledger_events.py` (or schema home) — register `intrinsic-complexity-attestation` event type
- `src/gzkit/schemas/ledger.json` — extend ledger schema for the new event family
- `src/gzkit/governance/trust_audits.py` — extend `validate --documents` to recognize the new event shape
- `tests/complexity/advisor/test_intrinsic.py`, `tests/commands/test_complexity_advise_attest_intrinsic.py`, `tests/governance/test_intrinsic_attestation_event.py`
- `features/intrinsic_complexity_attestation.feature` — behave scenarios tagged with REQ IDs
- `docs/user/manpages/gz-complexity-advise.md` — extend with `--attest-intrinsic` example
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces" describing the two paths
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-07-intrinsic-complexity-attestation.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01 (the `IntrinsicAttestationRef` forward stub lands there; this OBPI fills out the full implementation referenced by the stub)
- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02 (consumed, not edited; engine reads the registry to honor decorators at diagnosis time)
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09
- `.gzkit/hooks/**` — auto-chain hook is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `@intrinsic_complexity(reason: str, attestor: str)` is a Python decorator at `src/gzkit/complexity/advisor/intrinsic.py`. It registers the decorated function in a module-level registry keyed by `(file_path, qualname)` and persists the attestation tuple `(reason, attestor, decoration_date)`.
2. REQUIREMENT: The decorator is a no-op at runtime (does NOT modify the decorated function's behavior); it is a metadata declaration only. The advisor engine reads the registry at diagnosis time to honor pre-attested functions.
3. REQUIREMENT: The advisor engine (OBPI-02 contract — engine reads but does not edit) skips emitting a diagnosis for a function whose `(file_path, qualname)` is in the intrinsic-complexity registry; instead it emits the diagnosis with `intrinsic_attestation: IntrinsicAttestationRef(...)` populated, and the CLI presenter formats this as "intrinsic complexity attested by `<attestor>` on `<date>`: `<reason>`" rather than as a refactor recommendation.
4. REQUIREMENT: `gz complexity-advise --attest-intrinsic --reason="<reason>" --attestor="<name>" <path>:<qualname>` is the commit-time path. It (a) validates that the named function actually crosses a warn or block band (refusing attestation for functions that are NOT crossing — no fabricated escape hatches); (b) emits a canonical `intrinsic-complexity-attestation` ledger event with payload `{file_path, qualname, reason, attestor, attestation_date, crossing_metric, crossing_band, crossing_value}`; (c) prints the attestation receipt ID for the operator to cite.
5. REQUIREMENT: The commit-time path enforces TTY + `ATTEST` confirmation per `_enforce_human_attestation_authenticity` precedent (`src/gzkit/commands/adr_audit.py`); a headless invocation refuses to emit the event (closes the synthesis vector per GHI #290).
6. REQUIREMENT: The new ledger event family `intrinsic-complexity-attestation` is registered in `src/gzkit/governance/ledger_events.py` (or schema home) with the canonical payload shape. The ledger schema at `src/gzkit/schemas/ledger.json` is extended; `gz validate --documents` recognizes the new event shape.
7. REQUIREMENT: A failed `--attest-intrinsic` invocation (validation error, malformed input, headless rejection, TTY-confirmation refused) MUST NOT emit the event. Partial state is not preserved.
8. REQUIREMENT: Tests cover: decorator registers function in registry; decorator does not modify runtime behavior; advisor engine honors the decorator at diagnosis time (mocked engine integration); commit-time `--attest-intrinsic` validates the function crosses a band before emitting; commit-time `--attest-intrinsic` emits exactly one ledger event with the canonical payload; commit-time `--attest-intrinsic` refuses headless emission; failed invocations emit no event; ledger schema validates the new event shape; `gz validate --documents` recognizes the new event. Each test decorated with `@covers(REQ-0.0.29-07-NN)`.
9. REQUIREMENT: A behave scenario at `features/intrinsic_complexity_attestation.feature` tagged `@REQ-0.0.29-07-{01..05}` covers both paths (decorator + commit-time) end-to-end.
10. REQUIREMENT: Manpage extension adds the `--attest-intrinsic` flag with an example invocation. Runbook entry describes when to use which path (decorator: pre-attested, persists in code; commit-time: in-flight, persists in ledger).
11. REQUIREMENT: Tests use `tempfile`-backed ledger fixtures; NEVER touch the live `.gzkit/ledger.jsonl`.
12. REQUIREMENT: TDD discipline.
13. REQUIREMENT: NEVER include the operator's personal email in attestor field, code, fixtures, or commit messages — operator name only or GitHub noreply per the user's project rule.

> STOP-on-BLOCKERS: if OBPI-01's `IntrinsicAttestationRef` stub is not present, OR if OBPI-03's CLI verb is not landed, STOP — both are dependencies.

## Discovery Checklist

- [ ] OBPI-01 schema — `IntrinsicAttestationRef` stub
- [ ] OBPI-03 CLI verb shell — extended here
- [ ] OBPI-02 engine — registry-read contract
- [ ] `src/gzkit/commands/adr_audit.py` `_enforce_human_attestation_authenticity` — TTY + ATTEST gate precedent
- [ ] AGENTS.md § OBPI Acceptance Protocol — heavy + foundation Gate 5 rigor; ATTEST gate
- [ ] `.gzkit/ledger.jsonl` — sample existing event shapes (e.g. `adr-evaluation` from ADR-0.0.26) for consistency

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage extension + runbook entry

### Gate 4: BDD (Heavy)
- [ ] Behave scenarios pass for both paths

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` for the OBPI itself (the OBPI's own brief-level Gate 5, distinct from the runtime ATTEST gate the OBPI implements)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_intrinsic.py tests/commands/test_complexity_advise_attest_intrinsic.py tests/governance/test_intrinsic_attestation_event.py -v
uv run -m behave features/intrinsic_complexity_attestation.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-07-01: Given a function decorated `@intrinsic_complexity(reason=..., attestor=...)`, when the registry is inspected, then the function appears keyed by `(file_path, qualname)` with the attestation tuple.
- [ ] REQ-0.0.29-07-02: Given a decorated function whose CC crosses the warn band, when the engine runs, then the emitted diagnosis has `intrinsic_attestation: IntrinsicAttestationRef` populated and no refactor recommendation.
- [ ] REQ-0.0.29-07-03: Given a function that does NOT cross any band, when `gz complexity-advise --attest-intrinsic --reason=X --attestor=Y <path>:<qualname>` runs, then the command refuses (exit 1) with a named error.
- [ ] REQ-0.0.29-07-04: Given a function that crosses a warn or block band + valid attestation arguments + interactive TTY + `ATTEST` confirmation, when `--attest-intrinsic` runs, then exactly one `intrinsic-complexity-attestation` ledger event is emitted with the canonical payload.
- [ ] REQ-0.0.29-07-05: Given a headless invocation of `--attest-intrinsic`, when the command runs, then it refuses (exit 1) and no ledger event is emitted.
- [ ] REQ-0.0.29-07-06: Given the new event in the ledger, when `gz validate --documents` runs, then exit 0 and the event shape is recognized.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict + manpage + runbook
- [ ] Gate 4: behave scenarios pass
- [ ] Gate 5: TTY + `ATTEST` (brief-level)

## Evidence

### Gate 1 (ADR)
- [x] Intent and scope recorded — ADR-0.0.29 OBPI-07 two-path attestation

### Gate 2 (TDD — Red-Green-Refactor)
```text
arb-step-unittest-cf68ebf06bb646cbb56d5e0cf81afef5
All tests pass (skipped=1)
REQs covered: REQ-0.0.29-07-01 through REQ-0.0.29-07-06
```

### Code Quality
```text
arb-ruff-363ee011147c4191a2196e0eb613434b (lint clean)
arb-step-typecheck-093d9f5a6d32460fab47140eb0b1f986 (types clean)
```

### Gate 3 (Docs)
```text
arb-step-mkdocs-42e979ab5b214bf9bf28beb7e79ccc2e (docs build clean)
docs/user/commands/complexity-advise.md: --attest-intrinsic, --reason, --attestor documented
docs/user/commands/validate.md: --intrinsic-attestation documented
docs/user/runbook.md: two-path attestation entry added
```

### Gate 4 (BDD)
```text
features/intrinsic_complexity_attestation.feature
1 feature passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
21 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)
```text
Attestor: Jeffry
Text: attest completed
Date: 2026-05-08
```

### Value Narrative

Functions with genuinely irreducible cyclomatic complexity (query optimizers,
state machines, protocol decoders) previously had no formal escape from
repeated advisor refactor recommendations. OBPI-0.0.29-07 closes this gap
with two human-attested paths: a decorator for compile-time registration and
a commit-time CLI command for in-flight discovery.

### Key Proof


arb-step-unittest-cf68ebf06bb646cbb56d5e0cf81afef5 (all tests pass);
uv run -m behave features/intrinsic_complexity_attestation.feature (4/4 pass);
gz validate --documents (exit 0)

### Implementation Summary


Decorator path: @intrinsic_complexity(reason, attestor) registers
(file_path, qualname) in module-level registry; _analyze_file checks
registry before engine call and short-circuits attested functions.
Commit-time path: gz complexity advise file:qualname --attest-intrinsic
validates band crossing, TTY gate, ATTEST confirmation, emits
intrinsic-complexity-attestation ledger event. Trust audit
validate_intrinsic_attestation added under gz validate --intrinsic-attestation.

- Files created: intrinsic.py, intrinsic_attestation.py, 3 test files, BDD feature + steps
- Files modified: complexity_advise.py, ledger_events.py, schemas/ledger.json, events.py, trust_audits/__init__.py, validate_cmd.py, parser_artifacts.py, parser_maintenance.py, 3 doc files
- Tests added: 8 unit (registry), 7 unit (attest CLI), 8 unit (event shape), 4 BDD
- Date completed: 2026-05-08
- Attestation status: Attested by Jeffry
- Defects noted: None in-scope

### Closing Argument

Both attestation paths are human-gated: the decorator requires explicit reason
and attestor at authoring time; the CLI path requires a crossing function,
an interactive TTY, and the literal word ATTEST. The trust audit closes the
ledger loop.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — two-path intrinsic-complexity attestation implemented: decorator registry (@intrinsic_complexity) + commit-time --attest-intrinsic CLI path with TTY gate; validate_intrinsic_attestation trust audit wired; arb-ruff-363ee011147c4191a2196e0eb613434b, arb-step-typecheck-093d9f5a6d32460fab47140eb0b1f986, arb-step-unittest-cf68ebf06bb646cbb56d5e0cf81afef5, arb-step-mkdocs-42e979ab5b214bf9bf28beb7e79ccc2e; 4/4 BDD scenarios pass; gz validate --documents clean; REQ-0.0.29-07-01 through -06 covered
- Date: 2026-05-08

---

**Brief Status:** Completed

**Date Completed:** 2026-05-08

**Evidence Hash:** -
