---
id: ADR-pool.validator-scope-registration-seam
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.validator-scope-registration-seam: Validator Scope Registration Seam

## Status

Pool

## Persona

`quality-reviewer` — architectural-rigor, solid-principles, maintainability-assessment.
The subject is duplication across module boundaries and which duplications encode a
decision versus restate a fact. That is a design-review judgment, not an
implementation one, and the wrong persona here would optimise the copies rather
than remove them.

## Intent

**Adding one `gz validate` scope currently costs seventeen registrations across
sixteen files. Eleven of them are mechanical restatements of one fact.**

Measured 2026-08-26 while landing a single new validator scope
(`--corpus-retirement-witness`, GHI #885):

| Surface | Entries |
|---|---|
| `VALIDATOR_REGISTRY` `_ScopeEntry` rows | 93 |
| `validate()` explicit `check_*` kwargs | 94 |
| argparse `dest="check_*"` flags | 95 |
| argparse forwarding lines (`check_x=a.check_x`) | 94 |

Four parallel lists of ~94 items, roughly 376 lines whose entire content is
"these scopes exist". **The counts do not agree** — 93/94/95/94 — and three test
modules exist solely to check that the copies match:
`tests/cli/test_validate_dispatch_consistency.py`,
`tests/cli/test_validate_registry_parity.py`,
`tests/governance/test_check_scope_parity.py`. A fifth copy lives in
`data/check_scope_membership.json`.

`VALIDATOR_REGISTRY`'s own docstring already states the correct design —
*"the single source from which every validate dispatch surface derives"* — and
it is accurate **inside `validate_cmd.py`**. The pattern stops at the module
boundary. Everything beyond it re-declares.

### The seventeen, split by kind

**Mechanically derivable from `(name, tier, level, runner)` — eleven:**

1. `VALIDATOR_REGISTRY` `_ScopeEntry` row
2. `validate()` `check_<scope>` kwarg
3. `validate()` scope→flag mapping entry
4. argparse `--<scope>` flag
5. argparse forwarding line
6. `data/check_scope_membership.json` in_check/out_of_check placement
7. `_POST_SNAPSHOT_DEFAULT_ADDITIONS` snapshot entry
8. `quality.py` `run_<scope>_audit` wrapper
9. `commands/quality.py` import
10. `commands/quality.py` step tuple
11. `commands/quality.py` `_mx_levels` registry row
12. `trust_audits/__init__.py` import + `__all__`

**Genuine authorship that must stay hand-written — six:**

- QC step classification (`qc_binding._STEP_CLASSIFICATION`) — a real taxonomy call
- QC negative control fixture + entrypoint — must be authored, and earned its
  keep on 2026-08-26 by forcing proof the new gate could fail at all
- Concurrency class + `measured_seconds` — requires actually measuring
- Exemption posture (`EXEMPTS_NONE` or a claim id) — a real judgment
- Manpage section and per-flag doc — prose only a human should write

The target is therefore **eleven collapse to one; six remain**. This is not a
reduction in governance. Every gate that caught something on 2026-08-26 is in
the six.

### Why this is worth an ADR rather than a fix

The cost compounds against every future gate, and the parity tests are the
tell: gzkit has built fences to detect drift between four copies of a list
instead of holding one list. Those tests are not coverage, they are scar
tissue, and collapsing the copies makes three test modules unnecessary — a rare
case where deleting tests increases safety.

Measured cost of the status quo on one four-file defect fix (GHI #885): the fix
itself took ~25 minutes; the registrations took ~35; nine full 8870-test suite
runs added ~21 minutes of waiting because each missing registration surfaces
only as a failing test.

## Decision

**Option C — derive the derivable, checklist the rest.**

1. `VALIDATOR_REGISTRY` becomes the single source across the module boundary,
   not just within it. The eleven mechanical sites are generated or read from it.
2. `validate()`'s ~94 explicit kwargs collapse to a scope collection; argparse
   flags and `quality.py` steps are generated from the registry.
3. The six authored surfaces stay hand-written. A `gz validate scope-doctor
   <name>` reports which of the six a new scope is missing, so the checklist is
   mechanical even though the content is not.
4. `test_validate_dispatch_consistency`, `test_validate_registry_parity`, and
   `test_check_scope_parity` retire as their subject ceases to exist. Their
   retirement is part of the deliverable, not a side effect — a parity test over
   a single source is tautological.

Option C is chosen over full derivation (Option A) as the first increment
because it captures most of the win at a fraction of the blast radius, and
because it draws the line exactly where the distinction is real: derive what
restates a fact, keep what records a decision. A is what C converges toward.

## Alternatives Considered

**A — Full registry-driven generation, in one step.** Replace every dependent
surface at once. Rejected as the first increment, not on merit: it is the
correct end state, but it rewrites the dispatch path for ~94 live scopes in a
single change, and the parity tests that would catch a mistake are themselves
part of what it deletes. C reaches the same place with a checkable intermediate.

**B — Scaffold command (`gz validate scaffold-scope <name>`).** Generate all
seventeen sites from a template. Rejected: it automates the symptom and
entrenches the cause. The copies still exist, can still drift, and the parity
tests must stay forever. It would make the next scope cheap while making the
duplication permanent.

**D — Do nothing; absorb the cost per scope.** Rejected on measurement. The
2026-08-26 instance is not an outlier — it is what adding any scope costs, and
the cost is paid by every future gate. Doing nothing also leaves the four lists
disagreeing (93/94/95/94), which is a live drift the parity tests currently
paper over rather than resolve.

## Notes

**Sequencing (binding).** `AGENTS.md` § Operator Doctrine forbids out-of-sequence
ADR work: feature ADRs are worked in ascending semver order, and ADR-0.35.0 is in
flight at 3/10 as of 2026-08-26. This item stays Pool and waits its turn.
Promotion is an operator decision, and the campaign does not override the
ascending-semver rule.

**Origin.** Surfaced 2026-08-26 during `/ghi-close 885`, from direct measurement
rather than review — the session performed all seventeen registrations before the
pattern was named. Operator ruling, verbatim: *"this sounds like absolute
insanity, yes to pool"*.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
