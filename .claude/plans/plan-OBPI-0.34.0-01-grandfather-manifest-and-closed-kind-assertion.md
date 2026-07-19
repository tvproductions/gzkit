# Plan — OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion

**Parent ADR:** ADR-0.34.0-foundation-sunset (feature, heavy)
**Brief:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/obpis/OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion.md`

## Context

Land the committed closed grandfather manifest, its frozen identity-only Pydantic
model, and two fail-closed `gz validate --taxonomy` assertions, guarded by a
golden-file tamper test — so foundation-kind membership becomes a committed,
machine-checked, two-way-door set instead of "whatever `kind: foundation` files
happen to sit on disk".

Decision quote this OBPI implements (parent ADR § Decision, DATA MODEL):

> data/foundation_grandfather.json with a frozen Pydantic
> FoundationGrandfatherManifest (extra=forbid) holding IDENTITY-ONLY entries
> (id, title, semver, frozen_at) and NO lifecycle field - storing lifecycle
> would bake a Layer-2 fact into a committed Layer-1 file, the exact
> state-doctrine drift the 0.0.37 frontmatter-lie demonstrated.

and (§ Decision, INTERFACE):

> extend 'gz validate --taxonomy' (ADR-0.0.17) with two fail-closed assertions -
> closed-kind (every on-disk kind:foundation ADR must appear in a committed
> grandfather manifest) ...

and Review Refinement (a):

> the grandfather manifest is protected by a golden-file test pinning it to the
> sunset roster, so reopening the kind surfaces as a deliberate reviewable diff.

## Load-bearing design decision: the interim red is deliberate

This OBPI lands the **assertion**; OBPI-04 lands the **population** (brief
§ Denied Paths names roster population as OBPI-04's, explicitly). Consequently,
once this OBPI ships, `gz validate --taxonomy` fails closed with one
`foundation_kind_closed` finding per on-disk foundation ADR, and stays red until
OBPI-04 populates the roster.

That interim red is correct, not a defect, and must NOT be papered over:

- The parent ADR's anti-staging-flag doctrine forbids a hand-set flag to hold the
  gate green over a non-terminal tree (§ Decision, SEQUENCING; § Consequences
  Negative #2).
- It does not break `gz check`: `taxonomy` is absent from the check step list
  (`src/gzkit/commands/quality.py:424-448` — verified, the list runs Lint /
  Format / Typecheck / Test / Behave / … / Invariant coherence, with no taxonomy
  entry). Wiring `--taxonomy` into `gz check` is OBPI-05's last act, by design.
- The parent ADR's Fidelity Assertions row 2 (`gz validate --taxonomy` -> 0) is
  therefore expected to go RED after this OBPI and GREEN after OBPI-04. The
  fidelity block is the sunset's scoreboard; a row that flips red here is the
  scoreboard working.

**Do not** populate the roster to make the gate green. **Do not** add a staging
flag. Both are the failure this ADR exists to prevent.

## Golden-file pinning under a deliberately-unpopulated manifest

REQ-04 requires the golden test to fail when the manifest "diverges from the
pinned sunset roster", but the roster does not exist until OBPI-04. Resolution:
the golden test pins the manifest to a committed fixture by exact content. This
OBPI lands manifest + fixture together in their seed state; OBPI-04 updates
**both** in the same reviewable commit. Any edit to one without the other fails
the test — which is precisely the tamper-guard semantics Review Refinement (a)
asks for, and it holds at every stage rather than only after population.

## Files

Per brief § Allowed Paths — nothing outside this list.

| Path | Action |
|---|---|
| `data/foundation_grandfather.json` | CREATE — manifest instance, seed state |
| `src/gzkit/models/foundation_grandfather.py` | CREATE — frozen model + TypeAdapter loader |
| `src/gzkit/governance/trust_audits/taxonomy.py` | MODIFY — additive only; two new assertions |
| `tests/governance/test_foundation_grandfather_manifest.py` | CREATE — model + golden-file tests |
| `tests/governance/test_taxonomy_closed_kind.py` | CREATE — two-finding validator tests |
| `tests/governance/fixtures/foundation_grandfather_golden.json` | CREATE — golden fixture |

Denied (untouched): `src/gzkit/cli/**`, `src/gzkit/schemas/adr.json` (kind enum
stays intact), `.gzkit/ledger.jsonl`, `gz check` wiring, the `foundation_limbo`
terminal-partition gate (OBPI-03), roster population (OBPI-04).

## Steps

Red-Green-Refactor per behavior. Each RED must be an **assertion-level** failure,
not an ImportError — so step 1 creates importable skeletons first.

1. **Skeleton** — create `src/gzkit/models/foundation_grandfather.py` with
   `FoundationGrandfatherEntry`, `FoundationGrandfatherManifest`, and
   `load_manifest` as no-op stubs, so subsequent tests fail on their own
   assertions rather than on a missing symbol.

2. **REQ-03 (model discipline)** — RED: tests asserting `ValidationError` for
   (a) an entry carrying `lifecycle`, (b) an entry with any extra key, (c) each
   of `id`/`title`/`semver`/`frozen_at` missing. GREEN: implement the frozen
   model mirroring `src/gzkit/models/security_surfaces.py` —
   `ConfigDict(frozen=True, extra="forbid")`, `Field(..., description=...)`,
   module-level `TypeAdapter`, `load_manifest(path)`, `__all__`.

3. **Manifest instance** — create `data/foundation_grandfather.json` in seed
   state (valid against the model, roster unpopulated — OBPI-04 populates).

4. **REQ-01 (`foundation_kind_closed`)** — RED: a test building a temp project
   root with a `kind: foundation` ADR absent from the manifest, asserting the
   audit returns a `foundation_kind_closed` finding. GREEN: extend
   `audit_adr_taxonomy` additively, reusing the existing `_parse_adr_frontmatter`
   and `_is_nested_adr_artifact` conventions already in the module. Finding prose
   is three-part per `.gzkit/rules/guardrail-feedback-prose.md`: what failed /
   why forbidden (kind closed, ADR-0.34.0) / next step (`--kind feature` or
   `gz adr demote`).

5. **REQ-02 (`grandfather_dangling`)** — RED: a manifest entry naming a
   nonexistent package asserts a `grandfather_dangling` finding. GREEN: implement
   the inverse subset check, same prose bar.

6. **REQ-04 (golden-file guard)** — RED: a test asserting the manifest matches
   the committed fixture byte-for-byte, verified to fail under a mutated
   manifest. GREEN: land the fixture.

7. **Exit-3 wiring** — confirm both findings propagate to `gz validate --taxonomy`
   exit 3 through the existing `ValidationError` path (no new exit plumbing —
   the scope already exits 3 on non-empty errors).

## Verification

Per brief § Verification — single-program invocations, no compound shells.

```bash
uv run gz validate --taxonomy
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
```

`gz validate --taxonomy` is expected to exit **3** after this OBPI (see § the
interim red above). All other commands must be clean. Note `--taxonomy` must be
run **alone**: GHI #704 documents that six solo-only scopes are silently dropped
when combined with another scope.

## Notes — destination-in-mind disclosure (plan-audit Step 6a)

**Conclusion formed before authoring:** that this OBPI is a near-mechanical
mirror of the `security_surfaces.py` data-registry precedent (frozen model +
`TypeAdapter` + `data/*.json`), which the brief names explicitly. Reading
`security_surfaces.py` confirmed the shape rather than discovering it.

**Alternatives considered and rejected during exploration:**

1. *Populate the roster here so `--taxonomy` lands green.* Rejected — the brief's
   Denied Paths assigns population to OBPI-04, and green-by-population would
   destroy the staged evidence the fidelity scoreboard is meant to show.
2. *A separate JSON Schema under `src/gzkit/schemas/` alongside the model.*
   Rejected — `security_surfaces.py` is the named precedent and deliberately
   carries no separate schema; a second validation authority is the drift shape
   `.gzkit/rules/models.md` exists to prevent.
3. *A new dedicated validator scope (`--foundation-closure`) instead of extending
   `--taxonomy`.* Rejected — the ADR says extend ADR-0.0.17's existing scope; a
   new scope would also inherit the GHI #704 solo-only-drop defect.
4. *Storing `lifecycle_at_sunset` in the manifest for convenience.* Rejected by
   the ADR itself (Alternative 3) — bakes a Layer-2 fact into Layer-1.
