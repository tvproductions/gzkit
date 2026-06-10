---
id: OBPI-0.0.69-01-support-channel-ledger-and-validator-dispatch
parent: ADR-0.0.69-channels-first-closeout-proof
item: 1
lane: Heavy
status: Completed
req_atomic:
  - REQ-0.0.69-01-01  # one resolver pass-branch (event found + dispatch 0 → pass) + its tests — single indivisible TDD unit
  - REQ-0.0.69-01-02  # one fail-close branch (event absent / citation unparseable) + tests — single indivisible TDD unit
  - REQ-0.0.69-01-03  # one fail-close branch (validator non-zero) + test — single indivisible TDD unit
  - REQ-0.0.69-01-04  # one manpage section edit — single indivisible doc unit
ln:
  - req_id: REQ-0.0.69-01-01
    receipt_ids:
      - arb-step-unitscoped-c6a26fbeacb84b0eb4cd8d5ebf42aaca
      - arb-step-unittest-60ef1652a5c946a5ae8ede9071560d6f
      - arb-ruff-d027bedd2567474c8a2158308fedbd64
      - arb-step-typecheck-c6002951f3c24665ba9d838f46fc8921
      - arb-step-mkdocs-3c7ff0490a7e4bf6b64a84c42fe25672
      - arb-step-coverage-6426cf06db9749e58c1e9ff844fbbab9
  - req_id: REQ-0.0.69-01-02
    receipt_ids:
      - arb-step-unitscoped-c6a26fbeacb84b0eb4cd8d5ebf42aaca
      - arb-step-unittest-60ef1652a5c946a5ae8ede9071560d6f
      - arb-ruff-d027bedd2567474c8a2158308fedbd64
      - arb-step-typecheck-c6002951f3c24665ba9d838f46fc8921
      - arb-step-mkdocs-3c7ff0490a7e4bf6b64a84c42fe25672
      - arb-step-coverage-6426cf06db9749e58c1e9ff844fbbab9
  - req_id: REQ-0.0.69-01-03
    receipt_ids:
      - arb-step-unitscoped-c6a26fbeacb84b0eb4cd8d5ebf42aaca
      - arb-step-unittest-60ef1652a5c946a5ae8ede9071560d6f
      - arb-ruff-d027bedd2567474c8a2158308fedbd64
      - arb-step-typecheck-c6002951f3c24665ba9d838f46fc8921
      - arb-step-mkdocs-3c7ff0490a7e4bf6b64a84c42fe25672
      - arb-step-coverage-6426cf06db9749e58c1e9ff844fbbab9
  - req_id: REQ-0.0.69-01-04
    receipt_ids:
      - arb-step-unitscoped-c6a26fbeacb84b0eb4cd8d5ebf42aaca
      - arb-step-unittest-60ef1652a5c946a5ae8ede9071560d6f
      - arb-ruff-d027bedd2567474c8a2158308fedbd64
      - arb-step-typecheck-c6002951f3c24665ba9d838f46fc8921
      - arb-step-mkdocs-3c7ff0490a7e4bf6b64a84c42fe25672
      - arb-step-coverage-6426cf06db9749e58c1e9ff844fbbab9
---

# OBPI-0.0.69-01-support-channel-ledger-and-validator-dispatch: SUPPORT Channel Ledger And Validator Dispatch

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`
- **Checklist Item:** #1 - "OBPI-0.0.69-01: SUPPORT channel — real ledger query + validator dispatch in `req_kind.py` SUPPORT branch and `_check_support_req`, propagating real `proof_status` (closes #543) (Heavy)"

**Status:** Completed

## Objective

The SUPPORT proof channel stops hardcoding `"advisory-support"` at `req_kind.py:182`: the
SUPPORT branch and `_check_support_req` query the ledger for the cited event AND dispatch
the cited validator scope, propagating the real `proof_status` so a missing event or a
non-zero validator exit reports unproven (fail-close). Closes #543.

## Lane

**Heavy** - Changes the runtime semantics of the `gz validate --req-kind-discipline`
SUPPORT proof channel (a runtime-contract surface) from advisory-always to a real
ledger-query + validator-dispatch result.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/traceability.py` (added by brief reconcile, attestor g0)
- `src/gzkit/triangle.py` (added by brief reconcile, attestor g0)
- `src/gzkit/events.py` (added by brief reconcile, attestor g0)

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/req_kind.py` — the SUPPORT branch (today hardcoding `"advisory-support"` near line 182) and `_check_support_req`: query the ledger for the cited event AND dispatch the cited validator scope, propagating the real `proof_status`
- `tests/` — fail-close regression tests (cited event found + validator exit 0 → pass; event missing → unproven; validator non-zero → unproven)
- `docs/user/manpages/validate.md` — document the SUPPORT-channel proof semantics (ledger-event-found AND cited-validator-exit-0)
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md` — parent ADR (read-only reference)
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/obpis/OBPI-0.0.69-01-support-channel-ledger-and-validator-dispatch.md` — this brief

> The exact module home above is the current location of the SUPPORT-channel logic; if a
> refactor has moved it, locate the real home before editing and note the divergence.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/governance/trust_audits/closeout_proof.py` and the `--closeout-proof` view — OBPI-03's scope
- The `ln:` closeout-proof-binding surface (`closeout_proof_binding.py`, schema `ln`, producer) — OBPI-04's scope
- The STRUCTURAL-FENCE arm and ADR-0.0.59's `## Boundary Invariants` heading — OBPI-02's scope
- New runtime dependencies; lockfiles; CI files

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language. -->

1. REQUIREMENT: The SUPPORT branch MUST resolve `proof_status` from a real ledger query for the cited event AND a real dispatch of the cited validator scope — never the hardcoded `"advisory-support"` constant.
1. REQUIREMENT: A SUPPORT REQ whose cited ledger event is NOT found MUST report unproven (fail-close). A missing or unparseable citation is treated as a violation, never a pass.
1. REQUIREMENT: A SUPPORT REQ whose cited validator scope exits non-zero MUST report unproven (fail-close).
1. REQUIREMENT: `docs/user/manpages/validate.md` MUST document the SUPPORT-channel proof semantics; `mkdocs build --strict` and `gz validate --documents` MUST stay green.
1. NEVER: touch the STRUCTURAL-FENCE arm, the derived `--closeout-proof` view, or the `ln:` surface — those are OBPI-02/03/04 scopes.
1. ALWAYS: reconcile this brief against the parent ADR § Decision item (1) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- Read structured input (parent ADR § Decision) before unstructured. -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (1)** — quote it verbatim into this brief's Implementation Summary. The Decision item is the contract.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`

> **STOP:** If you cannot quote the parent ADR § Decision item (1) that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR (OBPI-02 FENCE arm, OBPI-03 derived view)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/req_kind.py` exists and the `"advisory-support"` hardcode near line 182 is present
- [ ] The ledger query and validator-dispatch helpers the SUPPORT branch will call are located
- [ ] `docs/user/manpages/validate.md` exists

**Existing Code (understand current state):**

- [ ] `req_kind.py` SUPPORT branch and `_check_support_req` read whole; the proof-channel mapping (`_KIND_TO_CHANNEL`) understood
- [ ] Existing validator-dispatch and ledger-read patterns reviewed for the dispatch shape
- [ ] Existing `req_kind` tests reviewed for the fail-close test fixture shape

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- Single-program, shell-less invocations only (GHI #415). -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
```

## Demo

<!-- The yielded product. -->

```bash
# A SUPPORT REQ whose cited ledger event exists and whose cited validator exits 0
# now resolves to a real "pass" rather than the advisory-support placeholder:
uv run gz validate --req-kind-discipline
```

## Acceptance Criteria

<!-- Each REQ carries exactly one inline [kind] tag (ADR-0.0.59). -->

- [ ] REQ-0.0.69-01-01 [behavior]: Given a SUPPORT REQ whose cited ledger event is found AND whose cited validator scope dispatches exit 0, when the SUPPORT branch resolves proof, then `proof_status` is `pass` — not the hardcoded `advisory-support`. (@covers test)
- [ ] REQ-0.0.69-01-02 [behavior]: Given a SUPPORT REQ whose cited ledger event is NOT found, when the SUPPORT branch resolves proof, then `proof_status` is unproven/fail (fail-close), never `advisory-support`. (@covers test)
- [ ] REQ-0.0.69-01-03 [behavior]: Given a SUPPORT REQ whose cited validator scope dispatches a non-zero exit, when the SUPPORT branch resolves proof, then `proof_status` is unproven/fail (fail-close). (@covers test)
- [ ] REQ-0.0.69-01-04 [support]: `docs/user/manpages/validate.md` documents the SUPPORT-channel proof semantics (cited ledger event found AND cited validator exit 0). Proof: `artifact_edited` ledger event + `gz validate --documents` (doc-tree structural validator) + `mkdocs build --strict` green.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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

Before: the SUPPORT proof channel hardcoded `"advisory-support"` (req_kind.py:182) and
never queried the ledger or dispatched the cited validator, so any SUPPORT REQ passed
closeout regardless of whether its evidence existed (#543). Now: the SUPPORT branch
computes a real `proof_status` from a live ledger query plus a validator dispatch, and
fail-closes when either is missing.

### Key Proof


Live resolver demonstration against this repository's real ledger:

    $ uv run python -c "from pathlib import Path; from gzkit.req_kind import resolve_support_proof; ..."
    pass case (artifact_edited in real ledger + --documents exit 0)
      -> proof_status = 'pass'
    recursion fence (cites --req-kind-discipline)
      -> proof_status = 'unproven-recursion-fence'
    unparseable citation (no scope, no event type)
      -> proof_status = 'unproven-support'

OBPI-scoped tests:

    $ uv run -m unittest tests.test_req_kind_support_channel -v
    Ran 16 tests in 0.034s
    OK

Authoring-time compatibility held — the 8 pre-existing SUPPORT briefs stay green:

    $ uv run gz validate --req-kind-discipline
    ✓ All validations passed (1 scopes).

ARB receipts (canonical invocations per AGENTS.md § Attestation):
arb-step-unittest-60ef1652a5c946a5ae8ede9071560d6f (6013 pass),
arb-ruff-d027bedd2567474c8a2158308fedbd64,
arb-step-typecheck-c6002951f3c24665ba9d838f46fc8921,
arb-step-mkdocs-3c7ff0490a7e4bf6b64a84c42fe25672,
arb-step-coverage-6426cf06db9749e58c1e9ff844fbbab9 (6013 pass),
arb-step-unitscoped-c6a26fbeacb84b0eb4cd8d5ebf42aaca (16 pass, scoped).
gz covers behavior_uncovered_reqs=0. (A mis-named scoped receipt
arb-step-unittest-8a594f88d00b4612acf8d05a9ce03ae6 is superseded by the
unitscoped receipt; flagged non-canonical by `gz arb validate` by design.)

### Implementation Summary


- Parent ADR § Decision item (1), verbatim: "**SUPPORT channel made load-bearing (OBPI-0.0.69-01, Heavy).** The SUPPORT branch in `req_kind.py` (today hardcoding `"advisory-support"` at line 182) and `_check_support_req` actually query the ledger for the cited event AND dispatch the cited validator scope, propagating the real `proof_status`. A SUPPORT REQ whose cited ledger event is not found OR whose cited validator exits non-zero reports unproven (fail-close). Closes #543."
- Resolver: src/gzkit/req_kind.py — `SupportCitation` (frozen, `min_length=1`), `parse_support_citation`, `_KNOWN_LEDGER_EVENT_TYPES` derived from the `TypedLedgerEvent` union via import-time introspection (plus explicitly-commented, currently-empty `_UNTYPED_LEDGER_EVENT_EXTRAS`), `_ledger_has_event`, `_dispatch_validator_scope` (in-process via validate_cmd scope runners; lazy import is cycle-avoidance), `resolve_support_proof` with recursion fence (`req_kind_discipline`, `closeout_proof` never dispatched)
- Coverage wiring: `compute_three_channel_coverage` gains optional `project_root` — provided → real SUPPORT proof; omitted → legacy `advisory-support` unchanged for existing callers
- Authoring-time validator: src/gzkit/commands/validate_req_kind.py `_check_support_req` — strict parse first, legacy keyword fallback so the 8 pre-existing SUPPORT briefs (ADR-0.0.37/0.0.59) stay green; strictness is consumed fail-closed at closeout (OBPI-03's derived view)
- Docs: docs/user/manpages/validate.md — SUPPORT-channel proof semantics section + sharpened citation bullet
- Coupled-surface fixes: data/behave_coverage_waivers.json waiver entry; brief `req_atomic` frontmatter; operator-attested allowlist amendment (3 read-only test-import paths)
- Tests added: tests/test_req_kind_support_channel.py — 16 tests (2 pass-path with mocked dispatch isolation, 6 fail-close, 1 validator-non-zero, 4 derived-registry coherence that ran RED on the ghost first, 1 legacy-citation regression pin, 2 recursion fence)
- Two-stage review: quality-reviewer FAIL → fix-cycle-1 (derived registry, pass-case isolation, min_length=1) → PASS; spec-reviewer PASS (all 4 REQs traced)
- Date completed: 2026-06-10
- Attestation status: pending operator attestation
- Defects noted: brief-reconcile neighborhood-filter false positive tracked in agent-insights (2026-06-10); mis-named scoped receipt superseded (see Key Proof)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI. -->

- Closes #543 — SUPPORT channel hardcoded `advisory-support` without querying the ledger.

## Human Attestation

- Attestor: `g0`
- Attestation: ATTEST COMPLETED — operator-verbatim Stage 4 attestation for OBPI-0.0.69-01 SUPPORT-channel ledger-and-validator dispatch (closes #543); operator confirmed the Stage 4 ceremony rendering as correct ('this was correct, this is what worked'). Evidence: 16 OBPI-scoped tests green (arb-step-unitscoped-c6a26fbeacb84b0eb4cd8d5ebf42aaca), full suite 6013 pass (arb-step-unittest-60ef1652a5c946a5ae8ede9071560d6f), ruff clean (arb-ruff-d027bedd2567474c8a2158308fedbd64), typecheck clean (arb-step-typecheck-c6002951f3c24665ba9d838f46fc8921), mkdocs strict clean (arb-step-mkdocs-3c7ff0490a7e4bf6b64a84c42fe25672), coverage 6013 pass (arb-step-coverage-6426cf06db9749e58c1e9ff844fbbab9); gz covers uncovered_reqs=0; precomplete READY 8/8.
- Date: 2026-06-10

---

**Date Completed:** 2026-06-10

**Evidence Hash:** -
