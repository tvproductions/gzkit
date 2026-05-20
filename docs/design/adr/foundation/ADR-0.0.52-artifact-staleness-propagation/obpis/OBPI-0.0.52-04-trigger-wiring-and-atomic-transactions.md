---
id: OBPI-0.0.52-04-trigger-wiring-and-atomic-transactions
parent: ADR-0.0.52-artifact-staleness-propagation
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.52-04-trigger-wiring-and-atomic-transactions: Trigger wiring and atomic transactions

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #4 — "Trigger wiring — `gz closeout` and `gz obpi complete` hooks into `gzkit.governance.propagation.propagate`; atomic-transaction semantics (frontmatter write + ledger emit paired by `tx_id`)"

**Status:** Draft

## Objective

Wire the propagation pipeline into the existing `gz closeout` and `gz obpi complete` ceremonies as an unconditional side-effect, and implement the `tx_id` atomic-transaction semantics that pair ledger event emit with frontmatter write. OBPI-03 owns the algorithm; this OBPI owns when it fires and how its writes pair.

## Lane

**Heavy** — Modifies existing CLI verbs' side effects.

## Allowed Paths

- `src/gzkit/commands/closeout.py` — **PRIMARY:** hook propagation into closeout
- `src/gzkit/commands/obpi_complete.py` — **PRIMARY:** hook Tier 1-only propagation
- `src/gzkit/governance/propagation/trigger.py` — **PRIMARY:** `propagate(trigger_event)` entry point with `tx_id` semantics
- `src/gzkit/governance/propagation/transaction.py` — `tx_id` minting, frontmatter+ledger pairing, crash-recovery hooks
- `src/gzkit/governance/propagation/frontmatter.py` — atomic write of `evaluation_stale` entries
- `tests/governance/test_propagation_trigger.py` — trigger-wiring tests
- `tests/governance/test_propagation_transaction.py` — atomicity tests
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Validator scopes (OBPI-05)
- Resolution verb (OBPI-06)
- Tier 2 (OBPI-07)
- Status surfaces (OBPI-08)

## Creates These Files

- `src/gzkit/governance/propagation/trigger.py` — **CREATE** `propagate(trigger_event)` entry point with `tx_id` semantics
- `src/gzkit/governance/propagation/transaction.py` — **CREATE** `tx_id` minting, frontmatter+ledger pairing, crash-recovery hooks
- `src/gzkit/governance/propagation/frontmatter.py` — **CREATE** atomic write of `evaluation_stale` entries
- `tests/governance/test_propagation_trigger.py` — **CREATE** trigger-wiring tests
- `tests/governance/test_propagation_transaction.py` — **CREATE** atomicity tests

Existing files modified: `src/gzkit/commands/closeout.py`, `src/gzkit/commands/obpi_complete.py`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz closeout <ADR-X.Y.Z>` MUST invoke `propagate(trigger_event)` with `trigger_kind: adr_closeout` after closeout-attestation succeeds; propagation failure surfaces a prescriptive error and exits 3.
2. REQUIREMENT: `gz obpi complete <OBPI-X.Y.Z-NN>` MUST invoke `propagate(trigger_event)` with `trigger_kind: obpi_completion`, scoped to Tier 1 only.
3. REQUIREMENT: The propagation hook MUST be unconditional — no `--no-propagate` / `--skip-propagation` opt-out flag (no out-of-band trigger surface, per parent ADR negative scope).
4. REQUIREMENT: Every `artifact_staleness_flagged` event MUST pair with the corresponding frontmatter `evaluation_stale` entry via a shared `tx_id` (ULID minted per invocation).
5. REQUIREMENT: Transaction sequence MUST be: (a) emit ledger event with `tx_id` and fsync; (b) write frontmatter entry with same `tx_id`; (c) emit `propagation_evaluated` summary referencing same `tx_id`.
6. REQUIREMENT: On crash between (a) and (b), the next invocation of any propagation-aware command MUST detect the orphan via OBPI-05's `--staleness-coherence` and produce a prescriptive recovery message.
7. REQUIREMENT: `propagate(trigger_event)` MUST always emit at least one event (`propagation_evaluated`) — empty affected-set + fast-path-fired still produces it. Silent return is forbidden.
8. REQUIREMENT: For ADR closeout, `propagate()` MUST also schedule Tier 2 (OBPI-07 surface); when ADR-0.0.39 is not yet Proposed, OBPI-07's graceful-degradation path fires and the trigger wiring still emits the canonical `propagation_candidates_reviewed` event.

> STOP-on-BLOCKERS: read `gz closeout` and `gz obpi complete` source before authoring the hook insertion points.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"Trigger wiring — `gz closeout` and `gz obpi complete` hooks into `gzkit.governance.propagation.propagate`; atomic-transaction semantics"*.
- [ ] Parent ADR § Decision / "Trigger surface (binding)".
- [ ] Parent ADR § Decision / "2am operational discipline" — `tx_id` atomicity, crash recovery.

**Governance:**

- [ ] `AGENTS.md` § Behavior Rules / Never #2 — propagation uses canonical ledger APIs, never raw `.gzkit/ledger.jsonl` writes.

**Prerequisites:**

- [ ] OBPI-0.0.52-02 (Pydantic models, `tx_id`) has landed.
- [ ] OBPI-0.0.52-03 (Tier 1 algorithm + fast-path) has landed.

**Existing Code:**

- [ ] `src/gzkit/commands/closeout_cmd.py` reviewed for hook insertion point.
- [ ] `src/gzkit/commands/obpi_complete_cmd.py` reviewed for hook insertion point.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from brief acceptance criteria
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] BDD scenarios pass (full coverage in OBPI-09)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_propagation_trigger tests.governance.test_propagation_transaction -v
```

## Demo

```bash
uv run gz closeout ADR-0.0.X --dry-run --json > /tmp/closeout.json
python -c "import json; e=json.load(open('/tmp/closeout.json')); print('events:', [v['event'] for v in e.get('emitted_events', [])])"

uv run gz obpi complete OBPI-0.0.X-NN --dry-run --json > /tmp/obpi-complete.json
python -c "import json; e=json.load(open('/tmp/obpi-complete.json')); print('tier2_fired:', e.get('tier2_fired', False))"

# tx_id pairing check
tail -5 .gzkit/ledger.jsonl \
  | python -c "import json,sys; [print(json.loads(l).get('tx_id','-'),'|',json.loads(l).get('event','-')) for l in sys.stdin]"
```

## Acceptance Criteria

- [ ] REQ-0.0.52-04-01: Given a successful `gz closeout`, when the post-attestation hook runs, then `propagate(trigger_event)` is invoked with `trigger_kind: adr_closeout` and the full pipeline executes.
- [ ] REQ-0.0.52-04-02: Given a successful `gz obpi complete`, when the post-completion hook runs, then propagate is invoked with `trigger_kind: obpi_completion` and Tier 2 is NOT scheduled.
- [ ] REQ-0.0.52-04-03: Given the CLI parser, when invoked with `--no-propagate` or `--skip-propagation`, then the flag is rejected as unknown.
- [ ] REQ-0.0.52-04-04: Given a flagging event, when emitted, then both the ledger event and the frontmatter entry carry the same `tx_id` (ULID).
- [ ] REQ-0.0.52-04-05: Given a simulated crash between ledger emit (fsynced) and frontmatter write, when the next command runs, then `--staleness-coherence` flags the orphan with recovery message.
- [ ] REQ-0.0.52-04-06: Given any trigger event (including fast-path), when `propagate()` returns, then at least one ledger event (`propagation_evaluated`) has been emitted.
- [ ] REQ-0.0.52-04-07: Given an ADR closeout while ADR-0.0.39 is still Pending, when Tier 2 is scheduled, then OBPI-07's degradation path fires and `propagation_candidates_reviewed` is emitted with `judge_unreachable_reason: adr_039_not_proposed`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included

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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: closeout and OBPI completion were terminal — no downstream propagation, no atomic Layer-1/Layer-2 pairing. Now: every closeout fires the full pipeline, every OBPI completion fires Tier 1, every emission is paired by `tx_id`, and crash recovery is in-protocol via the coherence validator.

### Key Proof

```bash
$ uv run gz closeout ADR-0.0.X
[OK] ADR-0.0.X closeout complete.
Tier 1 propagation: 2 flagged. tx_id: 01HXXX...
Ledger: 1 propagation_evaluated + 2 artifact_staleness_flagged (all tx_id 01HXXX...)
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
