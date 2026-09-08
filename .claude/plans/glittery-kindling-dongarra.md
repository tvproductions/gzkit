# OBPI-0.35.0-05-corpus-candidate-generator — Implementation Plan

## Context

`docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md`
is Draft with a **FAIL** plan-audit verdict (`OBPI-0.35.0-05-PLAN-AUDIT-RECEIPT.json`,
archived in `OBPI-0.35.0-05-PLAN-REVIEW.md`): no implementation plan for OBPI-05 has ever
existed — the only plan discovery found was OBPI-04's plan, which explicitly disclaims
materialization ("This OBPI ships the declaration and the ratchet. It does NOT ship
materialization (OBPI-0.35.0-05)"). This plan is that missing artifact.

**Why now.** OBPI-0.35.0-05's prerequisites are landed: OBPI-01 (effective-corpus fold),
OBPI-03 (duplicate invariant entries retired, corpus 79→95 today after later captures),
OBPI-04 (section-ownership declaration + decrease-only ratchet, `.gzkit/ownership/AGENTS.md.json`),
and OBPI-09 (root-only AgentContract routing) are all `completed`/attested per
`gz adr status ADR-0.35.0-canon-entry-corpus-landing --json`.

**The gap this closes** (ADR § Intent gap 1, § Decision items 3/5): `composer.py:24-31`
takes `candidate_text` from the agent and validates it — nothing derives AGENTS.md from
the corpus. `composer.py:63-65` computes `compressible_bytes_after = total_bytes -
invariant_bytes`, a 63x inflation (354 B → 22,378 B) mislabeled as compression. This OBPI
makes the corpus materialize a real candidate (owned sections generated, unowned carried
forward byte-verbatim), emits a `<consumer>.lineage.json` provenance map, and fixes the
byte accounting to attribute bytes to actual emitted entries rather than subtracting totals.

**Boundary the ADR draws for this OBPI** (Decision 5, Alternatives O, BI-03): the lineage
map is a separate generate-time artifact, never bolted onto the frozen/`extra="forbid"`
`RenditionProvenance` (commit-time). "05 exposes a pure candidate-plus-lineage result; 07
owns final publication" — this OBPI produces staged candidate + lineage artifacts only; it
never writes a rendered surface and never commits.

## Design decisions (stated explicitly — surfacing per AGENTS.md § Behavior Rules #8)

1. **Shared fence-aware byte-boundary iterator lives in `ownership.py`, not a new module.**
   The brief's Allowed Paths list no new module except `lineage.py`; `ownership.py`'s own
   Allowed-Paths annotation says "shared byte-boundary iterator only; preserve declaration
   and ratchet policy." I will extract a new `SectionBoundary` NamedTuple + fence-aware
   `iter_section_boundaries(text: str) -> list[SectionBoundary]` (start/end are the
   half-open UTF-8 byte offsets of each H1/H2 span; a line inside a ```` ``` ```` fence never
   opens a heading) and refactor `measure_section_spans` to build on it — same signature,
   same collision-detection behavior, tests unchanged. `composer.py`'s new generator imports
   `iter_section_boundaries` from `ownership.py`. `section_body_lines`/`section_coverage`
   (a different, non-fence-aware walker) are **left untouched** — the brief names exactly
   two consumers of the shared iterator ("ownership measurement and generation"), and
   touching a third, unnamed walker would violate AGENTS.md Rule 11 (surgical changes).

2. **Candidate lineage is staged at a `.candidate.lineage.json` path, distinct from the
   eventual committed `.lineage.json`.** The brief's Generation and Accounting Contract
   states "Candidate lineage is staged with the candidate; it must never overwrite the
   committed lineage for the prior rendition before landing," which only makes sense if the
   two are different paths (mirroring the existing `.candidate.md` / `.md` split in
   `rendition.py` / `rendition_store.py`). `lineage.py` exposes both `lineage_path()` (the
   REQ-04 name, for 07's future committed write) and `candidate_lineage_path()` (what this
   OBPI's compose CLI actually writes). No prior committed lineage exists yet in this repo,
   so this is forward-compatible groundwork, not a live collision today.

3. **ByteEvidence fix applies to `compose()` uniformly, not only the new generated path.**
   BI-01 names `composer.py` as a consumer that must join the effective-view audit roster
   with no carve-out for "only when generating," and ADR § Consequences Positive #4 ("stops
   reporting a 63x inflation… as a compression accounting") carries no such qualifier
   either — today's measured 354→22,378 bug is reproducible via the **existing
   explicit-candidate path**, since the generator does not exist yet. Fix: both
   `invariant_entries` (already routed through `effective_corpus` via `tier_policy`, no
   change needed) and the compressible-entries computation move onto `effective_corpus`;
   `compressible_bytes_after` becomes **emission-attribution** — sum of byte-lengths of
   entries actually contributing to the candidate — never `total - invariant`.
   - **Generated path**: attribution comes directly from the lineage `entry_ids` computed
     during generation (exact, matches the brief's explicit instruction: "accounting must
     use emission attribution, never substring subtraction").
   - **Explicit-candidate path** (agent-authored `candidate_text`, unchanged CLI contract):
     no emission tracking is possible for freehand text, so attribution falls back to
     presence — sum of bytes of effective compressible entries whose text is a verbatim
     substring of `candidate_text`. This is strictly a subset-sum of the same population as
     `compressible_bytes_before` (each entry counted at most once), so it can never exceed
     it, and it eliminates the 63x-inflation formula on this path too.
   - REQ-07's "fails rather than emits an inflated figure" guard is implemented as an
     explicit `if after > before: raise` check kept for defense-in-depth (both computations
     are subset-sums by construction, so the branch is not reachable through the public
     API); it is unit-tested by calling the internal accounting helper directly with an
     inconsistent pair, proving the guard fires.

4. **Generation is a new function `generate_candidate(root, surface, consumer)` in
   `composer.py`**, not an overload of `compose()`'s positional signature (which requires
   `candidate_text: str`). The CLI (`commands/content/compose.py`) chooses between
   `compose()` (explicit path) and `generate_candidate()` (generated path) based on whether
   `--candidate` was given and, when absent, whether stdin is interactive
   (`sys.stdin.isatty()`) — this satisfies "must not block reading stdin" for the true
   generated case (no `--candidate`, no piped input) while leaving today's piped-stdin
   scripts (`echo "$text" | gz content compose ...`) on the unchanged explicit path.

5. **Off-route consumers are refused (REQ-05).** `generate_candidate` resolves the
   surface's content type via `content_type_for_surface`, then checks `consumer in
   routes_for(content_type, project_root=root)`; a consumer not on that route list raises
   `ValueError` naming the surface and the declared routes. For `AGENTS.md` today that means
   only `root` is accepted — `claude`/`codex` are refused, consistent with BI-07 (this ADR
   makes no change to Codex's own surfaces) and OBPI-09's root-only routing.

6. **Prior committed rendition is the carry-forward + boundary source.**
   `generate_candidate` loads `rendition_store.load_rendition(root, surface, consumer)`
   (fail-closed `FileNotFoundError` today if absent — refused with a clear message: no
   prior committed rendition to carry unowned sections forward from), decodes to UTF-8 text,
   and runs `iter_section_boundaries` over it to get the ordered section skeleton (id,
   title, level, byte start/end) that both defines the candidate's section order/heading
   text AND is the operand `load_declaration`'s existing measured-vs-declared cross-check
   runs against (reusing `load_declaration(ownership_path, prior_text, root)` gets the
   REQ-04 "unknown/duplicate section ids fail before writing" and the existing
   coverage-drift refusals for free, with zero duplicated logic).

7. **Duplicate live invariant text (REQ-09) is checked once, up front**, over
   `effective_corpus(corpus)` entries with `tier == "invariant"`, grouped by exact `.text`;
   any group of size > 1 raises `ValueError` naming both entry ids and sections, before any
   candidate bytes are emitted.

8. **REQ-10 needs no new test.** It is tagged `[structural-fence]` (ADR-0.0.59): its sole
   proof channel is the parent ADR's `## Boundary Invariants` BI-03 entry, audited at ADR
   closeout. This OBPI satisfies it structurally by never touching `rendition_store.py`
   (already a Denied Path) — no test-writing obligation.

## Files

- **`src/gzkit/content/ownership.py`** — add `SectionBoundary`, `iter_section_boundaries`;
  refactor `measure_section_spans` to use it (identical behavior/signature).
- **`src/gzkit/content/lineage.py`** (CREATE) — `SectionLineage`, `ConsumerLineage` Pydantic
  models (`frozen=True, extra="forbid"`, per `.claude/rules/models.md`); `lineage_path`,
  `candidate_lineage_path`, `save_candidate_lineage`/`load_candidate_lineage` helpers.
- **`src/gzkit/content/composer.py`** — fix `compose()`'s byte accounting (effective corpus
  + emission/presence attribution, decision 3); add `generate_candidate()` (decisions 4-7).
- **`src/gzkit/content/rendition.py`** — no field changes anticipated; touched only if a
  small helper (e.g. a byte-evidence assembly function shared by both compose paths) is
  more natural to live here than duplicated in `composer.py`.
- **`src/gzkit/commands/content/compose.py`** — branch on `--candidate`/stdin-isatty
  (decision 4); write both the candidate text and the candidate lineage JSON; unchanged
  ledger event (`composition_candidate_emitted_event`, not modified — out of allowlist).
- **`src/gzkit/commands/content/__init__.py`** — help/examples for the generated vs
  explicit-candidate mode.
- **`docs/user/manpages/content.md`** — document the generated path and the lineage
  artifact.
- **Tests** — `tests/content/test_ownership.py` (fence-aware boundary regression cases,
  additive), `tests/content/test_composer.py` (extend), `tests/content/test_lineage.py`
  (CREATE), `tests/commands/test_content_compose.py` (extend).
- **`features/content_compose.feature`** + **`features/steps/content_compose_steps.py`** —
  new `@REQ-0.35.0-05-*` scenarios for the generated path.
- **The brief itself** — evidence sections at completion (Stage 5, not this plan).

## REQ → implementation mapping

| REQ | Kind | Where |
|---|---|---|
| 05-01 (owned from effective corpus) | behavior | `generate_candidate`, owned-section branch |
| 05-02 (unowned byte-verbatim carry-forward) | behavior | `generate_candidate`, unowned-section branch (raw byte slice of prior rendition) |
| 05-03 (retired entries never contribute) | behavior | free from routing through `effective_corpus` |
| 05-04 (`<consumer>.lineage.json` shape) | behavior | `lineage.py` models + `generate_candidate` building `ConsumerLineage` |
| 05-05 (per-consumer spans) | behavior | span computed against the generated candidate's own byte layout; test with two consumers on a fixture manifest (root is the only real route today, so the second "consumer" in the test is a fixture-declared route, not a live one) |
| 05-06/07 (ByteEvidence correction + fail on inflation) | behavior | decision 3 |
| 05-08 (determinism) | behavior | no LLM/network/clock in either path; test double-run byte-identity |
| 05-09 (duplicate live invariant fails) | behavior | decision 7 |
| 05-10 (lineage never in `RenditionProvenance`) | structural-fence | no test; BI-03 audited at closeout |

## Verification

```bash
uv run -m unittest tests.content.test_composer tests.content.test_lineage tests.commands.test_content_compose tests.content.test_ownership
uv run -m behave features/content_compose.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --invariant-coherence
uv run gz validate --rendition-floor-coherence
uv run mkdocs build --strict
```

Manual demo once implemented: `uv run gz content compose AGENTS.md --consumer root` with no
`--candidate` and stdin attached to a TTY (or `< /dev/null` in CI) should generate a
candidate + `.candidate.lineage.json` from the real corpus and ownership declaration,
printing corrected byte evidence (no 63x-style inflation).

## Rejected within this plan's scope

- Extending `iter_section_boundaries` fence-awareness into `section_body_lines`/
  `section_coverage` — out of the brief's two named consumers; left as a separate,
  unmodified walker (decision 1).
- Wiring a new ledger event for lineage emission — `ledger_events.py` is not in the brief's
  Allowed Paths; the existing `composition_candidate_emitted_event` is reused unchanged.
- Any render-order policy — explicitly out of scope (OBPI-13), and this plan never reorders
  sections relative to the prior committed rendition's own order.
