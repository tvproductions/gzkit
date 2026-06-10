# Plan — OBPI-0.0.69-02-structural-fence-channel-boundary-invariants-anchor

**OBPI:** OBPI-0.0.69-02 (`OBPI-0.0.69-02-structural-fence-channel-boundary-invariants-anchor`)
**Parent ADR:** ADR-0.0.69-channels-first-closeout-proof (foundation / heavy)
**Closes:** GHI #538
**Authored:** 2026-06-10 (pipeline Stage 1, post plan-audit-gate)

## Context

The STRUCTURAL-FENCE proof arm is fake today: `compute_three_channel_coverage`
(`src/gzkit/req_kind.py:371`) hardcodes `proof_status = "grandfathered"` for every
STRUCTURAL-FENCE REQ — no anchor lookup, no ADR read, no real assertion. The channel
constant is `PARENT_ADR_INVARIANT` (`req_kind.py:41`); the name promises an ADR anchor
check, the code delivers none (#538).

**Parent ADR § Decision item (2) verbatim (brief Discovery Checklist, order pinned):**
> "STRUCTURAL-FENCE channel made load-bearing (OBPI-0.0.69-02, Heavy). The FENCE arm
> (today reporting `"grandfathered"`) asserts that a parent-ADR `## Boundary Invariants`
> anchor is present for the FENCE REQ; a missing anchor reports unproven. ADR-0.0.59
> itself gains a `## Boundary Invariants` heading anchoring its own FENCE REQs so it stays
> provable. Closes #538."

**ADR-0.0.59 coupled-surface note:** ADR-0.0.59 currently has NO `## Boundary Invariants`
section. Its own STRUCTURAL-FENCE REQs (REQ-0.0.59-02-04, REQ-0.0.59-03-03) will resolve
`"unproven-fence"` under the new arm until the heading is added. Adding it in this OBPI is
the coupled-surface fix (brief Allowed Paths bullet 3).

**`project_root` parameter already present:** `compute_three_channel_coverage` already
accepts `project_root: Path | None = None` (signature added for OBPI-01 SUPPORT wiring).
The FENCE arm uses the same parameter — no signature change needed.

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

Before authoring this plan I had formed: "add a `resolve_fence_proof(req_id, project_root)`
function that parses the ADR semver from the req_id, finds the parent ADR file, checks for
`## Boundary Invariants`; wire it into the STRUCTURAL_FENCE branch replacing the
`"grandfathered"` literal." Rejected alternatives:

1. **Return `"advisory-fence"` when `project_root` is None** (mirror SUPPORT's precedent).
   Rejected: the brief is explicit — "never `grandfathered` or advisory." Unlike SUPPORT's
   lenient legacy path, the FENCE channel must be fail-close even for callers that cannot
   supply a `project_root`: no anchor verification = unproven, not advisory. This is a
   stricter failure posture than SUPPORT and the brief requires it.
2. **Check REQ text for the anchor rather than the parent ADR file** (look for "Boundary
   Invariants" in the REQ description string). Rejected: the proof channel is defined as a
   parent-ADR file assertion, not a string mention in the REQ body. Checking the REQ text
   would make any REQ that mentions "Boundary Invariants" pass — the exact cosmetic-backfill
   anti-pattern this ADR exists to eliminate.
3. **Add a new parameter `parent_adr_path: Path | None` and require callers to supply it.**
   Rejected: the ADR semver is derivable from the req_id at runtime; requiring callers to
   supply it leaks lookup concerns upward and adds coupling. The in-function derivation is
   the local precedent (SUPPORT's `parse_support_citation` derives all citation info from the
   req text alone).

## Files (brief allowlist)

- `src/gzkit/req_kind.py` — FENCE resolver + coverage wiring (allowlisted)
- `tests/test_req_kind_fence_channel.py` (new) — fail-close regression tests
- `tests/governance/test_req_coverage_record.py` — update existing FENCE tests to expect
  new proof_status values (coupled-surface coherence; same allowlisted tests/ path)
- `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine.md` — add `## Boundary Invariants` heading (allowlisted)
- `docs/user/manpages/validate.md` — document STRUCTURAL-FENCE proof semantics (allowlisted)
- Brief + parent ADR — read-only reference / evidence updates (allowlisted)

Denied (untouched): SUPPORT branch (`_check_support_req`), `--closeout-proof` view
(OBPI-03), `ln:` surface (OBPI-04), deps/lockfiles/CI.

## Steps

1. **Discovery (read-only).** Quote parent ADR § Decision item (2) verbatim above (done).
   Verify prerequisites: `src/gzkit/req_kind.py` STRUCTURAL_FENCE arm exists at line 371
   with `"grandfathered"` literal; ADR-0.0.59 package exists at
   `docs/design/adr/foundation/ADR-0.0.59-*/`; `docs/user/manpages/validate.md` exists.
   Review ADR-0.0.68's `## Boundary Invariants` section as anchor-shape precedent. Review
   existing `test_structural_fence_req_is_grandfathered` for the fixture shape to update.
   (Discovery complete — findings above in Context.)

2. **RED.** New `tests/test_req_kind_fence_channel.py` deriving from brief REQs (semantics,
   not strings):
   - `TestFenceNoAnchor.test_fence_no_anchor_is_unproven` — @covers REQ-0.0.69-02-01:
     FENCE REQ + temp ADR with NO `## Boundary Invariants` heading + `project_root` →
     `proof_status != "grandfathered"` AND `proof_status.startswith("unproven")`.
   - `TestFenceWithAnchor.test_fence_with_anchor_is_proven` — @covers REQ-0.0.69-02-02:
     FENCE REQ + temp ADR WITH `## Boundary Invariants` heading + `project_root` →
     `proof_status == "pass"`.
   - `TestFenceNoProjectRoot.test_fence_no_project_root_is_unproven` — @covers
     REQ-0.0.69-02-01 (second scenario): FENCE REQ with `project_root=None` →
     `proof_status != "grandfathered"` (fail-close when root unavailable).
   Run, observe RED for all three.

3. **GREEN — resolver.** In `src/gzkit/req_kind.py`:
   - Add `_REQ_SEMVER_RE: re.Pattern[str] = re.compile(r"REQ-(\d+\.\d+\.\d+)-")` (module
     level).
   - Add `_find_parent_adr_file(semver: str, project_root: Path) -> Path | None`: search
     `project_root / "docs" / "design" / "adr"` via `rglob(f"ADR-{semver}-*.md")`; return
     the first match where the file's parent dir name starts with `f"ADR-{semver}-"` (the
     package dir, not a brief subdir).
   - Add `_adr_has_boundary_invariants(adr_path: Path) -> bool`: return
     `"## Boundary Invariants" in adr_path.read_text(encoding="utf-8")`.
   - Add `resolve_fence_proof(req_id: str, project_root: Path) -> str`: parse semver from
     req_id via `_REQ_SEMVER_RE`; call `_find_parent_adr_file`; call
     `_adr_has_boundary_invariants`; return `"pass"` if anchor found, else `"unproven-fence"`.

4. **GREEN — wiring.** In `src/gzkit/req_kind.py`:
   - Replace `else:  # STRUCTURAL_FENCE\n    proof_status = "grandfathered"` with:
     ```python
     else:  # STRUCTURAL_FENCE
         if project_root is not None:
             proof_status = resolve_fence_proof(entry.req_id, project_root)
         else:
             proof_status = "unproven-fence"
     ```
   - Update the `proof_status` docstring at line 331 from `"grandfathered"` to:
     `"pass" / "unproven-fence"` (with project_root) or `"unproven-fence"` (without).
   - Update `_recompute_rollup`: remove `"grandfathered"` from the advisory set (lines
     396-401). The `"unproven-fence"` status is fail-closed — NOT in the grandfathered set.
   - Update `ReqCoverageRecord.proof_status` Field description to replace `grandfathered`
     with `unproven-fence`.
   - Update `ReqCoverageSummary.grandfathered_reqs` Field description: remove
     "STRUCTURAL-FENCE" from the advisory-only enumeration.

5. **Update affected tests.** In `tests/governance/test_req_coverage_record.py`:
   - `test_structural_fence_req_is_grandfathered` → rename to
     `test_structural_fence_req_no_project_root_is_unproven_fence`; update
     `assertEqual(entry.proof_status, "grandfathered")` to
     `assertEqual(entry.proof_status, "unproven-fence")`; update
     `assertGreater(summary.grandfathered_reqs, 0)` to
     `assertEqual(summary.grandfathered_reqs, 0)` (unproven-fence is fail-closed,
     not advisory).
   - `test_grandfathering_cache_overrides_inference` (cache STRUCTURAL-FENCE, no
     project_root) → update `assertEqual(entry.proof_status, "grandfathered")` to
     `assertEqual(entry.proof_status, "unproven-fence")`.

6. **ADR-0.0.59 coupled-surface fix.** In
   `docs/design/adr/foundation/ADR-0.0.59-.../ADR-0.0.59-*.md`: add a `## Boundary
   Invariants` section after `## Evidence` (or before `## Attestation Block`) anchoring
   ADR-0.0.59's own STRUCTURAL-FENCE REQs. The heading text and one-line invariant
   statement for the STRUCTURAL-FENCE REQs in ADR-0.0.59 (REQ-0.0.59-02-04 and
   REQ-0.0.59-03-03) makes the ADR self-provable under the new arm.

7. **Docs.** `docs/user/manpages/validate.md`: document STRUCTURAL-FENCE proof semantics
   — parent-ADR `## Boundary Invariants` anchor required; absent anchor reports unproven;
   never grandfathered/advisory. Mirror the SUPPORT-channel docs shape added by OBPI-01.

8. **Verify** (brief Verification section + Heavy lane): `uv run gz arb ruff`,
   `uv run gz arb typecheck`, `uv run gz arb step --name unittest -- uv run -m unittest -q`,
   `uv run gz validate --documents`, `uv run mkdocs build --strict`, `uv run gz cli audit`,
   covers parity `uv run gz covers OBPI-0.0.69-02-structural-fence-channel-boundary-invariants-anchor --json`.

## Verification commands (from the brief)

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
```

## Notes

- `compute_three_channel_coverage` signature is unchanged — `project_root: Path | None`
  is already present from OBPI-01's wiring.
- The `grandfathered` bool field on `ReqCoverageRecord` (advisory-only flag) must remain
  False for proven FENCE REQs and True only for inferred/advisory-support cases. No change
  to the `grandfathered` field assignment logic in `_enrich` (it is derived from
  `proof_status` via `_recompute_rollup`, not set on the `CoverageEntry` model directly).
- REQ-0.0.69-02-03 [support] proves via `artifact_edited` ledger event + `gz validate
  --documents` + `mkdocs build --strict` — no @covers test. Covered by Step 6 (ADR-0.0.59
  edit) + Step 7 (manpage edit).
- REQ-0.0.69-02-04 [structural-fence] is verified at ADR-0.0.69 closeout via the parent
  ADR `## Boundary Invariants` (Invariant 1) — no per-OBPI test needed.
- TASK subdivision call happens at Stage 2 per REQ; coarse `seq=01` default unless labor
  genuinely subdivides below REQ granularity.
