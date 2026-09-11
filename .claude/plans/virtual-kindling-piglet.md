# OBPI-0.35.0-06 — `gz validate --rendition-lineage`

## Context

ADR-0.35.0 Decision item 4 requires a fail-closed gate over OWNED sections only:
a committed rendition's owned-section text must be derivable from the effective
corpus, unowned bytes are measured debt (never a failure), and the coverage
percentage is surfaced rather than implied. This is checklist item #6, depends
on OBPI-04 (ownership declaration, landed) and OBPI-05 (candidate generator +
lineage model, landed this session). It does **not** depend on OBPI-07 (the
`gz content land` publication orchestrator, not yet built) — the brief says so
explicitly, and Requirement 1's framing ("a gate whose scope is partial and
undeclared is the theater ADR-0.35.0 exists to remove") is the reason this gate
ships now, ahead of publication, rather than waiting.

**Allowlist was amended pre-implementation** (operator-approved) to add
`data/check_scope_membership.json` and
`src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — both mechanically
or brief-textually required coupled surfaces the original brief omitted. Logged
in the brief's Change Log under 2026-09-11.

## Design decisions (stated explicitly — the brief's prose left these as forks)

1. **Missing committed lineage = fail closed, not bootstrap-skip.** A surface
   with an ownership declaration but no `<consumer>.lineage.json` sidecar is a
   genuine gap in enforcement, not a bootstrap state to paper over — that is
   the ADR's own anti-theater thesis. On the live repo today, `AGENTS.md`/`root`
   has a declaration (OBPI-04) but no committed lineage (OBPI-07 hasn't
   published one), so `gz validate --rendition-lineage` legitimately reports
   FAIL right now. That's honest and expected: this scope is `"explicit"` tier
   and `out_of_check` in `check_scope_membership.json`, so it never runs inside
   `gz check` and blocks nothing.
2. **Core semantic check = regenerate and compare, not trust self-reported
   flags.** `generate_candidate(root, surface, consumer)` (OBPI-05, already
   deterministic and adversarially corroborated) reads the CURRENT effective
   corpus and CURRENT ownership declaration and regenerates a candidate using
   the COMMITTED rendition as its carry-forward/boundary skeleton. Slicing both
   the regenerated candidate and the committed rendition into
   `{section_id: text}` maps (via `iter_section_boundaries`, matched by id) and
   comparing OWNED sections' text is the independent derivation the Audit
   Contract demands — it never trusts the committed rendition's or lineage
   file's own owned/span claims as evidence.
3. **When a committed lineage sidecar exists, additionally validate its own
   internal integrity**: section-id set matches the committed text's own
   boundaries (no duplicate/unknown ids), `ConsumerLineage.assert_complete_partition`
   holds, each section's `owned` flag agrees with the ownership declaration,
   and every `entry_ids` referenced by an owned section is LIVE in
   `effective_corpus(corpus)` (a retired id left in a committed lineage is
   drift). This is the Audit Contract's artifact-integrity list.
4. **Coverage reporting via `emit_advisory` (stderr), not a new CLI subsystem.**
   `rendition_floor_coherence.py`'s sibling gate already proves this pattern
   works for `--json` (stderr advisory + stdout JSON error array coexist
   cleanly). Surfacing coverage this way avoids growing `validate()`'s already
   very large solo-scope dispatch table — surgical, minimal touch to
   `validate_cmd.py`/`parser_maintenance.py`.
5. **MX checkpoint + registration mirror `rendition_floor_coherence.py:47-51`
   exactly**: `_checkpoint.resolve("rendition-lineage", _levels.ERROR, root)`,
   `"explicit"` tier `_ScopeEntry`, `out_of_check` membership.
6. **A pure verification function is exposed for OBPI-07's future use**
   (Audit Contract: "expose a pure verification function for an explicitly
   supplied candidate/lineage pair") — no I/O, takes an in-memory candidate
   text + `ConsumerLineage` + `Corpus` + `OwnershipDeclaration`, returns
   `list[str]` problems. The main scope function calls it after regenerating;
   07 will call it before ever writing a candidate to disk.

## Files

### 1. `src/gzkit/governance/trust_audits/rendition_lineage.py` (CREATE)

Module docstring mirrors `rendition_floor_coherence.py`'s shape (what/why/
registration/severity). Key functions:

- `_section_text_by_id(text: str) -> dict[str, str]` — walk
  `iter_section_boundaries(text)` (from `gzkit.content.ownership`, read-only
  import), slice UTF-8 bytes per boundary, decode, key by `section_id`.
- `_load_committed_lineage(root, surface, consumer) -> ConsumerLineage | None`
  — read `lineage_path(root, surface, consumer)` (from `gzkit.content.lineage`,
  read-only import), parse into `ConsumerLineage.model_validate` per section;
  `None` when the file doesn't exist.
- `verify_candidate_against_declaration(candidate_text: str, lineage: ConsumerLineage | None, corpus: Corpus, declaration: OwnershipDeclaration) -> list[str]`
  — the PURE function (Audit Contract requirement). No disk I/O. Runs the
  integrity checks from design decision 3 (when `lineage` is not `None`) and
  returns plain-English problem strings; empty list means clean.
- `validate_rendition_lineage(root: Path, *, fail_closed: bool | None = None) -> list[ValidationError]`
  — the scope entry. Mirrors the sibling's enumeration exactly:
  `renditions_dir.iterdir()` → skip non-dirs → skip surfaces with no
  `declaration_path(root, surface).exists()` (bootstrap-safe, matches
  `codex.md` today) → for each `*.md` under the surface dir where
  `is_graded_rendition` is true:
  1. Load `declaration = load_declaration(declaration_path(root, surface), committed_text, root)`.
  2. `consumer = rendition_file.stem`; load committed lineage via `_load_committed_lineage`.
  3. If ownership declares ANY `corpus-owned` section and the committed lineage
     is `None` → fail-closed `ValidationError` (three-part recovery prose:
     what/why per Decision item 4/why forbidden, next step = `gz content land
     <surface>` once available — never "mark unowned", per Requirement 6).
  4. Regenerate: `regenerated = generate_candidate(root, surface, consumer)`.
  5. Build `committed_by_id = _section_text_by_id(committed_text)`,
     `regenerated_by_id = _section_text_by_id(regenerated.rendition.candidate_text)`.
  6. For each section id declared `corpus-owned`: if
     `committed_by_id[id] != regenerated_by_id[id]` → fail-closed
     `ValidationError` naming the section id, citing ADR-0.35.0 § Decision item
     4, and the corpus round-trip next step (Requirement 5/6 — this is what
     catches a retired entry left behind, since regeneration excludes it).
  7. Run `verify_candidate_against_declaration` against the current
     (committed_text, committed lineage, corpus, declaration) tuple; append any
     problems as `ValidationError`s.
  8. Accumulate coverage: sum owned/unowned byte spans (via
     `measure_section_spans`), section counts; after the surface loop,
     `emit_advisory` one line per surface: sections owned/total, bytes
     owned/total, percentage — always, pass or fail (Requirement 4).
  9. Severity resolution: `closed = _disposition.grounds(_checkpoint.resolve("rendition-lineage", _levels.ERROR, root)) if fail_closed is None else fail_closed` — staged-warn emits `emit_advisory` WARNING and is dropped from the returned list, exactly like the sibling.

### 2. `src/gzkit/governance/trust_audits/__init__.py`

Add `validate_rendition_lineage` to the module's exposed names, mirroring
exactly how `validate_rendition_floor_coherence` is exposed today (same import
statement shape, same place in the file).

### 3. `src/gzkit/cli/parser_maintenance.py`

Add `--rendition-lineage` (`dest="check_rendition_lineage"`, help text) as a
sibling argument to the existing `--rendition-floor-coherence` registration;
pass `check_rendition_lineage=a.check_rendition_lineage` through to the
`validate()` call at the existing forwarding site.

### 4. `src/gzkit/commands/validate_cmd.py`

- `_ScopeEntry("rendition_lineage", "explicit", True, lambda r, _f: _rendition_lineage_runner(r))`
  placed next to the `rendition_floor_coherence` entry.
- `_rendition_lineage_runner(project_root: Path) -> list[ValidationError]` —
  mirrors `_rendition_floor_coherence_runner` exactly (lazy import + call).
- Add `check_rendition_lineage: bool = False` to `validate()`'s signature,
  wired into `default_scopes`/`explicit_scopes` construction the same way
  `check_rendition_floor_coherence` already is.

### 5. `data/check_scope_membership.json`

Add `"rendition_lineage"` to the `out_of_check` array (alphabetical, matching
the file's existing sort order); bump `_counts.registry_scopes` 95→96 and
`_counts.out_of_check` 41→42.

### 6. `src/gzkit/governance/trust_audits/_qc_negative_controls.py`

Add `_build_rendition_lineage() -> Path`, mirroring `_write_declaration`'s
pattern from `tests/content/test_composer.py` (via `emit_section_ownership_genesis`
+ hand-written declaration JSON — the only way to construct a
`load_declaration`-passing fixture, since `floor_event_id` must resolve to a
real ledger event). Plant: a corpus jsonl with one `corpus-owned`-declared
section's entry; a vendor-manifest route for the consumer; an ownership
declaration marking that section owned; a committed rendition whose "owned"
section carries hand-authored prose that does NOT match the corpus entry (the
violation this gate must catch); and a valid committed lineage sidecar
(`root.lineage.json`) so the fixture exercises the semantic drift check, not
merely the missing-lineage path. Register
`("rendition-lineage", _build_rendition_lineage, _ep._ep_rendition_lineage)`
in `_build_enforcement_floor()`'s tuple list, next to `rendition-floor-coherence`.

### 7. `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`

Add `_ep_rendition_lineage(root: Path) -> list[ValidationError]`, mirroring
`_ep_rendition_floor_coherence` exactly (lazy import + call
`validate_rendition_lineage(root)`).

### 8. `tests/governance/test_rendition_lineage.py` (CREATE)

One test class per REQ (mirroring OBPI-05's `test_composer.py` fixture shape:
an isolated tmp root, `_write_declaration`/`_write_prior_rendition`-style
helpers reused/adapted). RGR discipline: each test written and watched RED on
its own assertion before the corresponding piece of `rendition_lineage.py` is
written.

- **REQ-01**: committed rendition's owned section matches deterministic
  materialization → `validate_rendition_lineage` returns `[]`.
- **REQ-02**: owned section carries non-derivable prose → returns one
  `ValidationError` naming the section id.
- **REQ-03**: unowned section carries arbitrary hand-authored prose → returns
  `[]` (never fails on unowned bytes) and the coverage advisory reports it as
  debt.
- **REQ-04**: changing the ownership declaration (flip a section between
  owned/unowned) changes the reported coverage figure — assert on the
  `emit_advisory`-captured line or a small coverage-computing helper's return
  value directly (whichever the implementation exposes; prefer asserting the
  helper's return value directly since that's a hand-independent oracle, not a
  string-match on advisory prose).
- **REQ-05**: an invariant entry retired by a tombstone, whose text still sits
  inside a committed owned section → exits with a `ValidationError` (regenerate
  excludes the retired entry, so text mismatch fires — mutation-witness proof
  spec should nominate the liveness-fold line in `effective_corpus`, mirroring
  OBPI-05's REQ-03 proof).
- **REQ-06**: the `ValidationError.message` on the exit-3 path carries all
  three recovery parts (drifted section id; cites ADR-0.35.0 § Decision item
  4; names the corpus-round-trip command) and does NOT suggest un-owning.
- **REQ-07** [support]: registration ledger event
  (`artifact_edited` citing `docs/user/manpages/validate.md`) +
  `gz validate --cli-alignment` passes.
- **REQ-08** [structural-fence]: no test — proof channel is
  `ADR-0.35.0` § Boundary Invariants BI-05 (already present), audited at ADR
  closeout.

Falsifiability negative control mirrors `_build_rendition_lineage` above but as
a focused unit fixture (mutation-witness proof spec for `gz obpi acceptance
prove` at Stage 2: mutate the owned/unowned comparison to always pass, watch
REQ-02's test fail on its assertion).

### 9. `features/rendition_lineage.feature` + `features/steps/rendition_lineage_steps.py` (CREATE)

Gate-4 scenarios covering the exit-0 and exit-3 paths end-to-end via the CLI
(`gz validate --rendition-lineage`), reusing the step-definition conventions
from a sibling `.feature`/steps pair already in `features/` (e.g. the
`content_compose` pair from OBPI-05) for corpus/ownership/rendition fixture
setup.

### 10. `docs/user/manpages/validate.md`, `docs/governance/governance_runbook.md`

Document the new `--rendition-lineage` scope: what it checks, the coverage
figure it surfaces, the exit-0/exit-3 contract, and that it is `out_of_check`
(not part of `gz check`) pending OBPI-07. Follow the existing
`--rendition-floor-coherence` entries' shape in both docs as the template.

## Verification

```bash
uv run -m unittest tests.governance.test_rendition_lineage
uv run -m behave features/rendition_lineage.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --rendition-lineage
uv run gz validate --rendition-lineage --json
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --gate-callers
uv run gz cli audit
uv run mkdocs build --strict
```

`gz validate --gate-callers` is the load-bearing regression check for the
`check_scope_membership.json` edit — it must stay green once `rendition_lineage`
is registered. Confirm `uv run gz validate --rendition-lineage` on the live
repo reports FAIL (missing committed lineage for `AGENTS.md`/`root`) and that
this is the EXPECTED state, not a regression — cite it plainly in Stage 4
evidence rather than treating it as something to silently fix.
