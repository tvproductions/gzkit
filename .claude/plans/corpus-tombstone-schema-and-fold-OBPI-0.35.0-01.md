# Plan — OBPI-0.35.0-01-corpus-tombstone-schema-and-fold

**OBPI:** `OBPI-0.35.0-01-corpus-tombstone-schema-and-fold`
**Parent ADR:** `ADR-0.35.0-canon-entry-corpus-landing` (Draft, kind=feature, lane=heavy)
**Lane:** Heavy
**Plan authored:** 2026-08-24

## Context

ADR-0.35.0 § Decision item 1 (verbatim contract this OBPI implements):

> RETIREMENT IS AN APPENDED TOMBSTONE, NEVER A DELETION. `CorpusEntry` gains
> optional `supersedes: str | None` and `retires: str | None`. `effective_corpus()`
> folds the append log; `tier_policy.invariant_entries()` reads the effective view;
> the raw log is never mutated. Direct analogue of `gz obpi withdraw`/`repudiate`
> (ADR-0.0.71). The fold's algebra is specified in this ADR, not deferred to
> implementation -- it is the one genuinely irreversible commitment.

### Measured state at HEAD (2026-08-24) — supersedes the brief's stale fixture figures

The brief's PARTIALLY PRE-LANDED table records "51 rows: 50 invariant, 1 compressible"
and marks it **stale — re-measure**. Re-measured:

| Fact | Brief (2026-08-07) | Measured HEAD (2026-08-24) |
|---|---|---|
| Raw rows in `.gzkit/corpus/AGENTS.md.jsonl` | 53 | **79** |
| Tier split (raw) | 51 inv / 2 compressible | **66 invariant / 13 compressible** |
| Tombstone rows (`retires` set) | 1 | **12 — all `compressible` tier** |
| Live invariant floor (`invariant_entries`) | 50 | **54** |
| `corpus_fingerprint` | not recorded | `8459d30b0fbacc8e5e33da8dd391f9355daef6ac1912d5c175f53888bd3f92de` |

Algebra preconditions verified against the live corpus **before** writing code:

- Algebra 2 (target strictly earlier): **0 violations**, 0 self-references, 0 unknown targets.
- Algebra 3 (exclusivity): no row can violate it — `supersedes` does not exist yet.
- Algebra 7 (at most one live tombstone per target): **0 duplicate targets**.
- Fold impact on the floor: **none**. All 12 tombstones are `compressible`, so
  `effective_corpus`'s `e.retires is None` clause drops zero invariant rows.
  Floor stays 54 → `gz validate --rendition-floor-coherence` cannot flip on this change.

Already landed (do NOT re-invent): `retires` field, `POST_BASELINE_IDENTITY_FIELDS`
+ `_inert_fields` omission mechanism (`corpus.py:66-115`), its fence
`TestDerivationIdentity::test_every_field_is_classified`, and `tier_policy`'s wiring
to a liveness notion (flat, `tier_policy.py:24`) — the latter needs a **repoint**, not
a new connection.

Open (the actual work): `supersedes` field, the nine-clause fold, load-time algebra
validation, and repointing every in-module liveness reader off the flat stand-in.

## Files

All inside the brief's Allowed Paths. No denied path is touched.

| File | Change |
|---|---|
| `src/gzkit/content/models/corpus.py` | `supersedes` field; `POST_BASELINE_IDENTITY_FIELDS` += `"supersedes"`; `_liveness()` reverse pass; `validate_tombstone_algebra()`; `effective_corpus()`; `Corpus.loads` calls the validator; `retired_ids()` + `live_entry_with_text()` repointed onto liveness |
| `src/gzkit/content/tier_policy.py` | `invariant_entries()` reads `effective_corpus()` |
| `src/gzkit/schemas/corpus_entry.json` | additive optional `supersedes` property |
| `tests/content/test_corpus_model.py` | fold-algebra + additive-load tests, `@covers` for REQ-01..08 |
| `docs/.../obpis/OBPI-0.35.0-01-....md` | evidence sections at Stage 4/5 |

## Design decisions (made here, not at implementation time)

**D1 — Algebra 2/3/7 validate in `Corpus.loads()`, NOT in a Pydantic `model_validator`.**
The brief says "a load-time `ValueError`" for each of Algebra 2, 3 and 7 — never
"construction-time". This is load-scoped for two concrete reasons:

1. **Idempotence (Algebra 9) would otherwise be unsatisfiable.** A surviving
   `supersedes` row in the folded output names a target the fold just removed. Under
   a `model_validator`, `effective_corpus(effective_corpus(c))` would raise
   "unknown target" instead of returning an equal corpus — Algebra 2 and Algebra 9
   would directly contradict each other.
2. **Blast radius.** A `model_validator` fires on every in-memory `Corpus(entries=...)`
   in the test tree, including fixtures outside this brief's allowlist. Load-scoping
   confines the new failure mode to the real store, which is where the REQs put it.

`effective_corpus()` therefore does not re-validate; it is a pure projection over an
already-validated log.

**D2 — `_liveness()` is one shared reverse pass, consumed by three readers.**
`live(e) = not any(live(t) for t in tombstones targeting e)`, evaluated last-to-first.
A single `dict[str, bool]` built in one backward loop — no fixpoint, no recursion
(ADR § Liveness by single reverse pass). Both `retires` and `supersedes` register a
tombstone edge; only `retires` suppresses the row's own text.

**D3 — repoint the in-module flat readers too (coupled-surface coherence, AGENTS.md
§ DO IT RIGHT 1a).** `Corpus.retired_ids()` (`corpus.py:129-131`) and
`Corpus.live_entry_with_text()` (`:133-155`) both compute liveness in the flat
`{e.retires for e in entries}` form that carries the exact Algebra-6 defect the fold
exists to fix. Both live in this brief's allowlist. Leaving either is the
"leftover flat reader" failure ADR § Consequences Negative #5 ranks worst.
Redefined on `_liveness`, both are **output-identical on the corpus as it stands
today** (verified: not-live == the 12 tombstone targets, exactly what the flat form
returns) and correct under un-retirement. This repoints `src/gzkit/commands/content/retire.py`'s
already-retired guard for free **without editing that denied path**.

**D4 — `retired_ids()` is kept, not deleted.** Its only non-repointed consumer is
`retire.py:50`, which is a DENIED path (OBPI-0.35.0-02). Deleting it would force an
out-of-scope edit.

**D5 — `effective_corpus` is not added to `content/models/__init__.py`.** That file is
outside the allowlist, and the brief's own Demo imports
`from gzkit.content.models.corpus import effective_corpus` — the direct-module path is
the declared contract.

**D6 — `supersedes` goes in `POST_BASELINE_IDENTITY_FIELDS`, never BASELINE.** The
existing `_inert_fields` mechanism generalizes: no row on disk uses `supersedes`, so
every row stays byte-identical and `corpus_fingerprint` is unchanged (REQ-01/REQ-2).
`test_every_field_is_classified` fails closed if this is forgotten.

## Steps

Red-Green-Refactor, one behavior per cycle. **Skeleton-first** to avoid the false
(import-error) red: define `effective_corpus`/`validate_tombstone_algebra` as no-op
stubs so every test fails on its own assertion, for the right reason.

1. **Skeleton.** Add `supersedes: str | None = None` to `CorpusEntry`; append
   `"supersedes"` to `POST_BASELINE_IDENTITY_FIELDS`; declare
   `effective_corpus(corpus) -> Corpus` returning `corpus` unchanged and
   `validate_tombstone_algebra(entries) -> None` as `pass`. Run the suite: the
   identity fence must stay green and the fingerprint must be unchanged.
2. **REQ-01 (RED→GREEN).** Test: a tombstone-free entry round-trips byte-identically
   through `dumps`/`loads` and `corpus_fingerprint(load_corpus(...))` still equals
   `8459d30b…f92de`. Expected red: assertion on the emitted JSON containing
   `"supersedes"`. Green by step 1's classification.
3. **REQ-02 (RED→GREEN).** Tests for forward reference, self reference, unknown id,
   and both-fields-populated → `ValueError` naming the offending entry id. Red:
   `ValueError not raised`. Green: implement Algebra 2 + 3 in
   `validate_tombstone_algebra`, called from `Corpus.loads`.
4. **REQ-03 (RED→GREEN).** `[X, T1(retires=X)]` folds to empty. Red: `1 != 0` /
   entries still present. Green: implement `_liveness` + `effective_corpus` projection.
5. **REQ-04 (RED→GREEN).** `[X, T1(retires=X), T2(retires=T1)]` folds to `[X]`, and
   `len(raw.entries) == 3` still. Red before the reverse pass lands.
6. **REQ-05 (RED→GREEN).** `[X, S1(supersedes=X)]` folds to `[S1]` — replacement row
   is a content row.
7. **REQ-06 (RED→GREEN).** Two live tombstones on one target → `ValueError`. Green:
   Algebra 7 check in `validate_tombstone_algebra`, computed over `_liveness`.
8. **REQ-07 (RED→GREEN).** Idempotence + append-order preservation, asserted over
   several shapes including one with a surviving `supersedes` row.
9. **REQ-08 (RED→GREEN).** A retired `invariant` entry is absent from
   `invariant_entries()` and `assert_invariant_verbatim()` no longer demands its text.
   Green: repoint `tier_policy.invariant_entries` onto `effective_corpus`.
10. **D3 repoint + schema.** Redefine `retired_ids` / `live_entry_with_text` on
    `_liveness`; add `supersedes` to `corpus_entry.json`; confirm the schema-mirror
    test still passes.
11. **Refactor + full verification.** Run the brief's Verification block.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --rendition-freshness
uv run gz validate --rendition-floor-coherence
```

Plus the brief's Demo block (raw vs effective counts, floor count, fingerprint).

## Notes / risks

- **R1 — out-of-allowlist test fallout.** `tests/content/test_tier_policy.py:168` and
  `tests/commands/test_content_retire.py:313` assert on `retired_ids()`. D3 is
  output-identical on their fixture shapes, so they should stay green; if either
  breaks, that is a Gate-Friction escalation (evaluator → operator → surgical
  allowlist amendment), never a silent edit.
- **R2 — REQ-09 is `[structural-fence]`.** Its proof channel is a parent-ADR
  `## Boundary Invariants` entry audited at ADR closeout, after OBPI-05 and OBPI-06
  land their consumers. **No unit test may be authored to make it look covered**
  (ADR-0.0.59; GHI #571).
- **R3 — `rendition_floor_coherence.py:96` and `composer.py:50` stay on the raw log.**
  Both are DENIED paths here (OBPI-0.35.0-06 and -05 respectively). Measured harmless
  today because the fold does not change the invariant floor (54 → 54).

## Step 6a — Plan-Before-Exploration disclosure

**Destination-in-mind.** Before writing this plan I had already formed a destination
during exploration: put Algebra 2/3/7 in a Pydantic `@model_validator(mode="after")`
on `Corpus`, because "no construction path can bypass it" is the reflexive
fix-the-class-of-failure answer. I was going to propose exactly that. It was wrong,
and reading REQ-12 against it is what broke it — the model-validator shape makes
Algebra 9 unsatisfiable, and the brief had already said "load-time" five times.
That conclusion was reversed by the requirements, not by further exploration.

**Rejected alternatives.**
1. *`model_validator` on `Corpus`* — rejected: contradicts Algebra 9 (idempotence),
   and fires on every out-of-allowlist in-memory fixture.
2. *`Corpus.model_construct()` inside `effective_corpus` to skip re-validation* —
   rejected: rescues the validator shape only by punching a hole in it; a reviewer
   would rightly read it as validation theatre.
3. *`effective_corpus` strips `supersedes` from surviving rows* — rejected: makes the
   fold non-pure (it would return altered copies), contradicting REQ-13.
4. *Recursive `live()` with memoization* — rejected: ADR pins "single reverse pass —
   never a fixpoint iteration and never unbounded recursion". The append-order
   guarantee makes recursion unnecessary.
5. *Delete `retired_ids()` and repoint `retire.py`* — rejected: `retire.py` is a
   denied path owned by OBPI-0.35.0-02.
6. *Leave `live_entry_with_text` on the flat form* — rejected: it carries the same
   Algebra-6 defect, sits in the allowlist, and is the leftover-flat-reader failure.
