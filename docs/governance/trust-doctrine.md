<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Trust Doctrine — Layer Boundaries and Independent Verification

**Source session:** 2026-04-18 ADR-0.0.16 closeout retrospective
**Companion doctrine:** [state-doctrine.md](./state-doctrine.md) — names storage tiers (L1/L2/L3); this doctrine names *trust* across those tiers
**Enforcement hooks:** `gz validate --event-handlers --validator-fields --type-ignores --cli-alignment`

---

## Why this doctrine exists

The state doctrine defines *where* governance state lives — Layer 1 (canon files), Layer 2 (ledger events), Layer 3 (derived state). It answers "which layer wins?" when layers disagree.

The state doctrine does **not** answer a different question: *how does each layer verify the layer below it produced what this layer assumes?* That question is about trust boundaries, not storage tiers, and its absence as an explicit doctrine cost gzkit a full-session outage on 2026-04-18.

This document names the pattern that failure exposed, records the instance taxonomy, and establishes the invariants that prevent recurrence at the pattern level rather than the instance level.

---

## The pattern: trust-chain poisoning

**Definition.** When Layer A's output feeds Layer B's decision, and A is silently wrong, B's decision looks correct. If this continues up the chain, every downstream consumer is rendered unreliable by a defect none of them can see from their own vantage point.

The shape is always the same:

```
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│  Layer A       │ ──▶  │  Layer B       │ ──▶  │  Layer C       │
│  (produces X)  │      │  (trusts X)    │      │  (trusts B's   │
│                │      │  (emits Y)     │      │   green check) │
└────────────────┘      └────────────────┘      └────────────────┘
    ↑ silent bug          ↑ correct logic          ↑ correct logic
      here                  given wrong X            given wrong Y
```

Each layer is individually correct. The composition is wrong because no layer independently tests that its inputs are what it assumes. The rule *"derived views are never source-of-truth"* from the state doctrine says the right thing about storage; it says nothing about verification.

**Trust-chain poisoning is not a bug. It is a class of bug.** Every instance looks different at the surface — a graph field, a validator comparison, a receipt scope, a stale assertion — but the mechanics are the same: missing independent verification of inputs at a trust boundary.

---

## The 2026-04-18 outage taxonomy

| # | Layer broken | Instance | How it poisoned the chain |
|---|--------------|----------|---------------------------|
| A | Graph builder | `_apply_attestation_metadata` didn't recognize `obpi_receipt_emitted` events (GHI #193) | Every attested OBPI's graph node said `attested=False` |
| B | Validator input | `_derive_obpi_runtime_state` took `attestation_state="not_required"` from the poisoned `attested` field | Runtime state derived to `in_progress` for every attested OBPI |
| C | Validator comparison | Raw string compare `fm.lower() != ledger.lower()` without STATUS_VOCAB_MAPPING (GHI #200) | `Completed` vs `attested_completed` counted as drift |
| D | Validator vocabulary | `STATUS_VOCAB_MAPPING` lacked `in_progress`, `attested_completed`, variants | Chore ran BLOCKER on unmapped terms |
| E | Schema enum | OBPI brief schema enum `[Draft,Active,Completed,Abandoned]` didn't match canonical ledger vocab | `gz validate --briefs` rejected frontmatter the chore had just written |
| F | Attestation receipts | ARB `ty check . --exclude 'features/**'` diverged from governance gate `ty check src` (GHI #199) | Receipts reported exit 0 against scopes different from what `gz typecheck` measured |
| G | Type-check suppressions | `# type: ignore[<mypy-code>]` silently unrecognized by ty (GHI #197) | 12 diagnostics accumulated; each "suppressed" line suppressed nothing |
| H | BDD / doc assertions | `features/gates.feature` and command docs cited `gz chore run` after GHI #189 renamed it to `gz chores run` (GHI #198) | Behave scenario passed for weeks until its assertion string met reality |
| I | Commit-trailer rule | `Task:` trailer required, `gz git-sync` emitted none (GHI #201) | Every sync commit tripped `--commit-trailers`; rule was advisory in practice |

Nine separate instances, one underlying pattern. Every one of them shipped green in prior closeouts because the trust chain's downstream consumer accepted the upstream's exit-0 without independent verification.

---

## The three invariants

These invariants formalize the lessons as mechanical rules. Each has a regression test or fail-closed audit in the repo.

### Invariant T1 — Every produced value has a read-path assertion

**Statement.** If a producer writes a value, at least one test must assert the producer writes *that specific value* under *that specific trigger*, not merely that the field exists.

**Instance:** GHI #193's fix added `graph[id]["attested"] = True` for `obpi_receipt_emitted` events. A regression test (`tests/test_ledger.py::TestLedger::test_get_artifact_graph_marks_obpi_attested_from_receipt_event`) asserts the exact path: synthetic `obpi_receipt_emitted` event in, `attested=True` out. Field presence wasn't enough — the validator was reading `False`, not a missing key.

**Anti-pattern caught:** "We wrote to this field; a test that asserts the field exists is sufficient." No — the bug was that the field was populated with `False` on the only attestation code path. Tests must assert the value produced by the triggering event, not merely that the schema includes the field.

### Invariant T2 — Every consumed value has a write-path audit

**Statement.** For every `info.get("<field>")` or equivalent read in a consumer, an enumeration audit must verify the field is written by at least one producer handler.

**Instance:** `tests/governance/test_validator_graph_field_coverage.py` walks every `info.get("...")` in the validator and asserts the key appears either in the artifact creation entry or in a `graph[id]["<field>"] = ...` statement in `src/gzkit/ledger.py`. Any "read without writer" fails fast at test time.

**Anti-pattern caught:** Adding a new validator read against a field the graph never populates. The write-path audit refuses to let a trust-chain blind spot ship.

### Invariant T3 — Canonical claims bind canonical provenance

**Statement.** Any claim that names a canonical label (e.g. a receipt's `step.name == "typecheck"`) must carry the canonical invocation that corresponds to the label. Labels without bound provenance are not claims — they are assertions dressed as claims.

**Instance:** `src/gzkit/arb/validator.py::CANONICAL_STEP_COMMANDS` maps canonical step names to their exact `step.command`. `gz arb validate` fails on provenance drift. Rule documented in `.gzkit/rules/attestation-enrichment.md` receipt-canonicalization table.

**Anti-pattern caught:** An ARB receipt whose step name says "typecheck" but whose command runs `ty check .` instead of `ty check src`. The claim and the evidence disagree; the label is wrong.

---

## Mechanical enforcement surface

The following tests and validator scopes are the current implementation of this doctrine:

| Trust boundary | Audit mechanism | Failure mode caught |
|----------------|-----------------|---------------------|
| Ledger event → graph | `gz validate --event-handlers` (from `tests/governance/test_ledger_event_handler_coverage.py`) | Event type added without dispatch |
| Graph → validator | `gz validate --validator-fields` (from `tests/governance/test_validator_graph_field_coverage.py`) | Validator reads field graph never writes |
| Ty migration → suppressions | `gz validate --type-ignores` (from `tests/governance/test_type_ignore_syntax.py`) | mypy-style codes silently unrecognized |
| CLI verb → documentation | `gz validate --cli-alignment` (from `tests/governance/test_behave_cli_alignment.py`) | Stale `gz <verb>` in features, runbook, manpages |
| ARB step → command provenance | `gz arb validate` (from `src/gzkit/arb/validator.py::CANONICAL_STEP_COMMANDS`) | Heavy-lane receipt measures the wrong scope |
| Commit → governance intent | `gz validate --commit-trailers` (accepts `Task:` or `Ceremony:` trailer) | Code-touching commits with no governance anchor |

Each audit is fail-closed. Each one catches a specific trust-boundary violation. The pattern they collectively close is trust-chain poisoning.

---

## Doctrine for new layers

When introducing a new layer that consumes from or produces for an existing layer, the authoring contract is:

1. **Name the trust boundary.** Write it as `<producer> → <consumer>` with the specific field or signal that crosses.
2. **Author a producer test (T1).** Assert the producer emits the expected value under the expected trigger.
3. **Author a consumer audit (T2).** Enumerate every field the consumer reads; prove every one has a producer.
4. **If a canonical label is involved, author a provenance binding (T3).** The label and the evidence must travel together.
5. **Surface the audit.** Add it to the pattern-audit suite (`gz validate` scope or standalone test under `tests/governance/`) so it runs on every validation, not only when someone thinks to invoke it.

Skipping any of these steps means the new layer is advisory rather than mechanical — and advisory rules accumulate drift until one operation stresses all the cracks at once.

---

## Related

- `.gzkit/rules/tool-skill-runbook-alignment.md` — an early form of the same pattern applied to skill/CLI/doc alignment; Invariants 1–3 are exactly the skill-layer analog of T1–T3
- `CLAUDE.md` § Architectural Boundaries — memo rule 6 ("derived views silently become source-of-truth") is this doctrine's storage-tier complement
- `.gzkit/rules/arb.md` — ARB receipt middleware; the provenance enforcement from Invariant T3 lives here
- [2026-04-18 ADR-0.0.16 session transcript] — original forensic record; GHIs #193, #197, #198, #199, #200, #201 close the instance taxonomy above
