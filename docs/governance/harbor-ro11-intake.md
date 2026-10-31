<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-11 specification — intake

**2026-10-30. Status: agent's draft, not reviewed by the operator; not specified until the operator rules on it (§ Not ruled).** Operator: **g0**. Repair order RO-11 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving the catalog. Sequenced after RO-12 and before RO-4 (operator: *"A"*), because RO-4's release and feature packages reference outcome codes this order settles. The rulings are quoted in full in the contract's § Rulings of 2026-10-29 and § Rulings of 2026-10-30.

## Scope

Intake is one act. Operator, verbatim: *"yes, it is just admitting/registering a new requirement into the requirements catalog, nothing more."* Admission is on the operator's word (*"yes, admission is on my word"*) and is separate from work selection, which is the Release Package's rule. What happens to an outcome after it enters, editing before the freeze, moves, reopening and withdrawal, is RO-5's by the change order of 2026-10-30.

The pool stays a store of intentions, and draining it stays on demand (*"A + B. A for design, B for execution"*). One entry is brought down by admitting its outcomes, each naming the entry as its `source`, and then writing the feature package that carries its story, in RO-4's store. No separate mark records the pull: an entry counts as brought down once an outcome names it.

## Rulings

<!-- gz-validate-skip: command-shape -->
1. **The entry verb is `gz catalog admit`** (operator: *"A"*). It creates a queued outcome with its `source`, `modules` and REQs and books `outcome_transitioned` for `queued`, the intake edge's witness. `gz catalog` is also the home of RO-5's verbs after entry and of the capability records.
2. **The five doors are the allowed values of `source`:** a pool entry, an R&D disposition, a deferred finding, the operator's word, an accepted ADR. `gz validate --catalog` refuses an outcome that names none (operator: *"yes, require the source"*).
3. **Exactly three levels, enforced** (operator: *"A"*, 2026-10-29): family, capability, outcome. An outcome's code has one dotted part, `SES1.4`; a bare capability code is not an outcome, and a fourth level is refused.
4. **Family codes are a fixed three letters** (operator: *"three"*), and the eleven are `AIR`, `SES`, `CTL`, `MNT`, `PKG`, `DEC`, `RQW`, `GAT`, `ATT`, `LED` and `QUA` (operator: *"yes, those eleven"*). The pattern is `^[A-Z]{3}[1-9][0-9]*\.[1-9][0-9]*$`.
5. **RO-11 lands the capability records, the tightened pattern and the re-coded legend** (operator: *"a"*). A capability is a named grouping with a scope and never carries work (§ Rulings of 2026-10-29).
6. **Capability records live in `data/catalog/capabilities.json`** (operator: *"A"*), one file for the kind, extending RO-3's layout.
<!-- gz-validate-skip: command-shape -->
7. **A capability is written by `gz catalog capability`** on the operator's word, taking a name and a scope (operator: *"A"*, twice), so a mistyped code at admission cannot create one; the entry verb refuses an outcome under a capability that has no record.

## Not ruled

Drafted by the agent and open, none of it to be built until the operator rules:

- this page itself, and the tranches below; the operator asked for the row's rewrite, not a specification page;
- whether the capability store lands empty;
- whether `gz validate --catalog` refuses an outcome whose capability has no record;
- dropping the old row's *"marked as pulled"* step: put in the draft, not objected to, not ruled.

## Tranches (for the contractor)

The contractor stops and waits on every structural question; the names of new verbs and events are among them.

1. **The code.** `OUTCOME_CODE_PATTERN` and `Family.code` in `src/gzkit/models/catalog.py`, with the schemas regenerated from them; the family lookup at `src/gzkit/governance/trust_audits/catalog.py:114`, which reads `o.code[0]`; `data/catalog/families.json` re-coded; the tests in `tests/governance/test_catalog.py` and the sample codes in `tests/test_id_resolver.py`.
2. **The records.** `capabilities.json`, its model and schema; `gz validate --catalog` refusing an outcome whose capability has no record; the outcome's `source` and `modules` fields.
<!-- gz-validate-skip: command-shape -->
3. **The verbs.** `gz catalog admit` and `gz catalog capability`, their manpages, and the `queued` writer in `src/gzkit/catalog_ledger.py`.

## Restoration (RO-11's list-of-discrepancies lines)

The lines are in the contract's § List of discrepancies under RO-11. Open lines elsewhere that name a family by its letter read through the mapping in § Rulings of 2026-10-30 once tranche 1 lands.

## Witness

The entry verb's unit tests, run against a temporary catalog with a real pool entry as input; `gz validate --catalog`.
