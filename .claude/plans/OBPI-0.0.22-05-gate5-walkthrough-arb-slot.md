# Plan — OBPI-0.0.22-05-gate5-walkthrough-arb-slot

**OBPI:** OBPI-0.0.22-05-gate5-walkthrough-arb-slot
**Parent ADR:** ADR-0.0.22-security-sensitivity-doctrine
**Lane:** Heavy
**Depends on:** OBPI-0.0.22-04 (Completed) — `_requires_security_review_attestation` ORed into `_requires_human_obpi_attestation`.

## Destination-in-mind (advisory)

Approach I came in with: extend `obpi_complete_cmd` in `src/gzkit/commands/obpi_complete.py` with a security-specific gate that runs before the existing `_enforce_human_attestation_authenticity` call when the brief carries `sensitivity: security`. Reserve a `"security"` slot with an empty placeholder list in `CANONICAL_STEP_COMMANDS`. Read the security checklist from `.gzkit/rules/security-sensitivity.md` at runtime (no hardcoded list).

## Rejected alternatives

1. **Hardcode the security checklist into `obpi_complete.py`.** Rejected: REQ-2 explicitly forbids hardcoding; the checklist must come from the rule file at runtime.
2. **Use a sentinel string (`"<UNSET>"`) instead of an empty list as the placeholder slot value.** Rejected: `CANONICAL_STEP_COMMANDS` types as `dict[str, list[str]]`; mixing sentinel strings would force a type widening. An empty list is a natural "no canonical command yet" state and `_provenance_error` already short-circuits when the observed command differs (a non-empty observed command vs. expected `[]` triggers the canonical mismatch).
3. **Compute receipt freshness with `os.path.getmtime`.** Rejected: receipts carry their own `created_at` timestamp; using mtime makes tests fragile under filesystem touch reordering. Read the timestamp from the receipt JSON.
4. **Run the security gate in `_enforce_human_attestation_authenticity` itself.** Rejected: that function is shared with `obpi_cmd.py` and `adr_audit.py`; bolting security-specific logic onto it leaks scope and breaks the single-responsibility shape.

## Context

REQ-1 — When `gz obpi complete` runs against a brief carrying `sensitivity: security`, the attestation walkthrough is extended with a security-specific checklist. The list is sourced from `.gzkit/rules/security-sensitivity.md` (authored by OBPI-06).

REQ-2 — The list MUST be read from the rule file at runtime. NOT hardcoded.

REQ-3 — `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` extends with one new entry: name `"security"` (so the receipt-name prefix becomes `arb-step-security-`); the canonical command list is left as a placeholder (empty list) for the toolchain feature ADR to fill.

REQ-4 — `sensitivity: security` brief + placeholder slot → `gz obpi complete` exits 3 with a finding naming the unfilled slot and the parent ADR.

REQ-5 — `sensitivity: security` brief + filled slot + no `arb-step-security-*` receipt → exit 3 with `receipt-missing` finding.

REQ-6 — `sensitivity: security` brief + filled slot + receipt older than 24 h → exit 3 with `receipt-stale` finding citing the receipt timestamp.

REQ-7 — Behavioral tests cover walkthrough-fires (sensitivity:security), walkthrough-suppressed (sensitivity:null), placeholder-slot, receipt-missing, receipt-stale.

REQ-8 / REQ-9 — Out of scope: schema/frontmatter, registry, validate scope, audit OR, rule file content, AGENTS.md matrix, the actual security-scan command string.

### Existing surface

- `src/gzkit/commands/obpi_complete.py:91-99` — already extracts `sensitivity` from the brief frontmatter and passes it through `_requires_human_obpi_attestation` (OBPI-04 work). The audit OR already fires; what is missing is the Gate-5 walkthrough extension and the canonical-slot/receipt-freshness pre-checks.
- `src/gzkit/commands/obpi_complete.py:188-205` — the GHI #290 authenticity gate (`_enforce_human_attestation_authenticity`) is invoked here. The new security gate must run BEFORE this call so the placeholder/missing/stale checks short-circuit cleanly with exit 3.
- `src/gzkit/arb/validator.py:52-57` — `CANONICAL_STEP_COMMANDS` table; the new `"security"` entry lands here.
- `src/gzkit/arb/paths.py:13-48` — `receipts_root()` resolves the ARB receipts directory; the receipt-search helper consumes it.
- `src/gzkit/commands/adr_audit.py:338-440` — `_enforce_human_attestation_authenticity` is unchanged by this OBPI; the security gate runs above it.

### Brief-vs-physical-path note

The brief lists `src/gzkit/commands/obpi.py` in Allowed Paths. The physical OBPI command surface has been split into `obpi_complete.py`, `obpi_cmd.py`, etc. Per `AGENTS.md` § DO IT RIGHT (read the surface, change the surface), the walkthrough extension lands in `obpi_complete.py` (the file that owns `obpi_complete_cmd`, where Gate 5 is enforced). Treating the brief's `obpi.py` label as canonical-shorthand for the OBPI command surface is consistent with the parent ADR's wording.

## Files

- `src/gzkit/arb/validator.py` — extend `CANONICAL_STEP_COMMANDS` with `"security": []` placeholder (one-line change + comment).
- `src/gzkit/commands/obpi_complete.py` — add four module-level helpers + integrate the security gate into `obpi_complete_cmd`.
- `tests/arb/test_validator_canonical_step_commands.py` (new) — REQ-3 coverage: presence of `"security"` slot, placeholder shape, receipt-name prefix derivation.
- `tests/commands/test_obpi_complete_security.py` (new) — REQ-1/2/4/5/6/7 coverage: table-driven walkthrough fires/suppresses, placeholder-slot exit 3, receipt-missing exit 3, receipt-stale exit 3, receipt-fresh-and-filled proceeds.

No edits to `data/behave_coverage_waivers.json` are anticipated — REQ-7 is unit-testable without BDD; foundation OBPIs in this ADR have been deferring BDD per the parent's pattern. If `gz validate --behave-req-tags` flags the brief at Stage 5, add the waiver entry then.

## Steps

1. **RED — REQ-3 — extend CANONICAL_STEP_COMMANDS placeholder.** Author `tests/arb/test_validator_canonical_step_commands.py` asserting:
   - `"security"` key is present in `CANONICAL_STEP_COMMANDS`.
   - The associated value is `[]` (placeholder shape).
   - A receipt with `step.name == "security"` and any non-empty `step.command` triggers `_provenance_error` (since expected `[]` ≠ observed).
   Decorate every test with `@covers("REQ-0.0.22-05-03")`. Run; expect failure.

2. **GREEN — REQ-3.** Add `"security": []` to `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` with a comment naming the parent ADR, the reserved receipt-name prefix `arb-step-security-`, and the deferral to the toolchain feature ADR (the one promoting `pool.agentic-security-review`). Run tests; expect pass.

3. **RED — REQ-1/2 (helper)** — Author tests in `tests/commands/test_obpi_complete_security.py` for a helper `_load_security_checklist(rule_path: Path) -> list[str]`:
   - Returns parsed bullet items when the rule file exists with a recognizable checklist section.
   - Raises `GzCliError` (or returns sentinel) when the rule file is absent.
   Decorate with `@covers("REQ-0.0.22-05-01")` and `@covers("REQ-0.0.22-05-02")`. Run; expect failure.

4. **GREEN — REQ-1/2.** Implement `_load_security_checklist` in `obpi_complete.py`. Contract:
   - Resolve rule path from `<project_root>/.gzkit/rules/security-sensitivity.md`.
   - When the file is absent → raise `GzCliError("Security checklist rule file missing: .gzkit/rules/security-sensitivity.md (authored by OBPI-0.0.22-06).")`.
   - When present → read UTF-8 text, locate a heading like `## Walkthrough Checklist` (case-insensitive, accept `### Walkthrough Checklist`), collect each `- ` bullet under it until the next heading. Return the list of stripped bullet strings.
   - The list is read at runtime per REQ-2 — no caching, no defaults baked in.

5. **RED — REQ-4 (placeholder-slot fail)** — Add a test that, given a brief with `sensitivity: security` and `CANONICAL_STEP_COMMANDS["security"] == []`, `obpi_complete_cmd` exits 3 with a message naming the unfilled slot and the parent ADR. Decorate `@covers("REQ-0.0.22-05-04")`. Run; expect failure.

6. **GREEN — REQ-4.** In `obpi_complete.py`, add `_security_canonical_slot_filled() -> bool` (returns `bool(CANONICAL_STEP_COMMANDS.get("security"))`). Add `_enforce_security_review_gate(...)` which is invoked from `obpi_complete_cmd` after step 4 (would-be-content validation) and before step 4b (authenticity gate), guarded by `sensitivity == "security"`. When the slot is unfilled, the gate calls `_fail("Security-scan canonical slot in CANONICAL_STEP_COMMANDS is unfilled for parent ADR <ADR-ID>; the toolchain feature ADR (promoting pool.agentic-security-review) must fill it before sensitivity:security briefs can be completed.", exit_code=3, ...)`.

7. **RED — REQ-5 (receipt-missing fail)** — Add a test where the slot is monkey-patched to a non-empty command, no `arb-step-security-*` files exist under the receipts root (use a `tmp_path`-like fixture with `GZKIT_ARB_RECEIPTS_ROOT` set), `gz obpi complete` exits 3 with a `receipt-missing` finding. Decorate `@covers("REQ-0.0.22-05-05")`. Run; expect failure.

8. **GREEN — REQ-5.** Add `_find_fresh_security_receipt(receipts_dir: Path, max_age_hours: int = 24) -> Path | None`:
   - Glob `arb-step-security-*.json` (or whatever the canonical name shape is — confirm against `arb/step_reporter.py`).
   - For each candidate, parse JSON and read `created_at`. Return the newest receipt whose age ≤ `max_age_hours`.
   - Return `None` when no candidate is fresh enough.
   In `_enforce_security_review_gate`, when the slot is filled and `_find_fresh_security_receipt` returns `None`, distinguish missing vs. stale by also computing the newest receipt regardless of freshness:
   - No receipts found at all → `_fail("Security-scan receipt missing under <receipts_dir> (sensitivity:security brief requires arb-step-security-* receipt within 24h).", exit_code=3, ...)`.
   - Newest receipt older than 24 h → `_fail("Security-scan receipt stale: newest arb-step-security-* receipt at <path> created <iso8601> (>24h old).", exit_code=3, ...)`.

9. **RED — REQ-6 (receipt-stale fail)** — Add a test that produces a fresh-named receipt with `created_at` 25 hours in the past; expect exit 3 with `receipt-stale` finding citing the timestamp. Decorate `@covers("REQ-0.0.22-05-06")`. Run; expect failure.

10. **GREEN — REQ-6.** The Step-8 implementation already covers both REQ-5 and REQ-6 by branching on "no receipts found" vs. "newest receipt is stale." Run REQ-6 test; expect pass.

11. **RED — REQ-1 walkthrough-fires** — Add a test that with `sensitivity: security`, slot filled, fresh receipt present, the walkthrough is invoked: assert that `_render_security_walkthrough` (or the console output) produces the rule-file-derived checklist before `_enforce_human_attestation_authenticity` is called. Patch `_enforce_human_attestation_authenticity` so the test does not require a real TTY. Decorate `@covers("REQ-0.0.22-05-01")`. Run; expect failure.

12. **GREEN — REQ-1 walkthrough-fires.** Add `_render_security_walkthrough(checklist_items: list[str]) -> None` that prints a Rich panel naming the OBPI, parent ADR, and each checklist item. Wire it into `_enforce_security_review_gate` as the final step before returning successfully. The walkthrough does NOT consume the `ATTEST` confirmation — that remains the responsibility of `_enforce_human_attestation_authenticity` immediately afterward.

13. **RED — REQ-2 walkthrough-suppressed** — Add a test that with `sensitivity` absent (or non-`security`), the walkthrough is NOT invoked and the slot/receipt checks are NOT run. Decorate `@covers("REQ-0.0.22-05-02")`. Run; expect failure.

14. **GREEN — REQ-2 walkthrough-suppressed.** The guard `if sensitivity == "security":` at the top of `_enforce_security_review_gate` already implements this; confirm the test passes after the previous green steps. The dispatch site in `obpi_complete_cmd` should read `sensitivity` once (line 94 already extracts it) and pass it into the gate so no duplicate parse is added.

15. **REFACTOR** — Once all REQs are green:
    - Confirm helper functions are size-cap compliant (≤50 lines each per `.claude/rules/pythonic.md`).
    - Confirm no `# type: ignore[<code>]` mypy-style suppression syntax landed (use bare `# type: ignore` or `# ty: ignore[<ty-code>]` per `pythonic.md`).
    - Confirm `obpi_complete.py` stays ≤600 lines; if the security gate plus helpers tip it over, extract them into a sibling module (e.g., `src/gzkit/commands/obpi_complete_security.py`) and import from `obpi_complete_cmd`. **Allowed-paths note:** the brief lists `src/gzkit/commands/obpi.py` as the walkthrough surface; a `obpi_complete_security.py` sibling under the same package path is consistent with the brief's intent (the OBPI command surface) but is a path expansion. If the size-cap is breached, surface the path expansion to the operator before extracting.
    - Confirm `validator.py` stays ≤600 lines.

16. **Stage 3 verification** — run the canonical bundle:
    - `uv run gz arb ruff` (lint).
    - `uv run gz arb typecheck`.
    - `uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_obpi_complete_security tests.arb.test_validator_canonical_step_commands -v` (scoped tests).
    - `uv run gz covers OBPI-0.0.22-05 --json` (REQ → @covers parity, REQ-7).
    - `uv run gz validate --documents`.
    - Heavy lane: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`.

## Verification (Stage 4 evidence template)

Each REQ row in the Stage 4 evidence table maps to a concrete fixture:

| REQ | Mechanism | `@covers` location | Test class | Result |
|-----|-----------|--------------------|------------|--------|
| REQ-0.0.22-05-01 | `_render_security_walkthrough` invoked when `sensitivity: security` | `tests/commands/test_obpi_complete_security.py` | `TestSecurityWalkthroughFires` | Pass |
| REQ-0.0.22-05-02 | walkthrough suppressed when `sensitivity` absent / non-security | `tests/commands/test_obpi_complete_security.py` | `TestSecurityWalkthroughSuppressed` | Pass |
| REQ-0.0.22-05-03 | `CANONICAL_STEP_COMMANDS["security"] == []` placeholder + receipt-name prefix | `tests/arb/test_validator_canonical_step_commands.py` | `TestSecurityCanonicalSlot` | Pass |
| REQ-0.0.22-05-04 | placeholder-slot exits 3 with parent-ADR finding | `tests/commands/test_obpi_complete_security.py` | `TestSecurityPlaceholderSlotFailsClosed` | Pass |
| REQ-0.0.22-05-05 | receipt-missing exits 3 with `receipt-missing` finding | `tests/commands/test_obpi_complete_security.py` | `TestSecurityReceiptMissingFailsClosed` | Pass |
| REQ-0.0.22-05-06 | receipt-stale (>24h) exits 3 citing timestamp | `tests/commands/test_obpi_complete_security.py` | `TestSecurityReceiptStaleFailsClosed` | Pass |

## Notes

- The security gate is **additive** to `_requires_human_obpi_attestation`'s OR; it does not replace any existing branch.
- The walkthrough output is informational — it does NOT take a separate confirmation. The single `ATTEST` confirmation already enforced at `_enforce_human_attestation_authenticity` covers human attestation; the walkthrough's job is to put the checklist in front of the operator before they type `ATTEST`.
- 24 h is read from the parent ADR Decision; not configurable in this OBPI (a future GHI may parameterize it). Hardcoding `24` in `_find_fresh_security_receipt`'s default is acceptable per the ADR.
- The helpers parse the rule file each time `obpi_complete_cmd` runs — no module-level caching. Per REQ-2, "the walkthrough reads the canonical list from the rule file at runtime."
- Cross-OBPI dependency: until OBPI-0.0.22-06 lands the rule file, every `sensitivity: security` brief will fail at `_load_security_checklist`. That is the intended fail-closed posture; OBPI-06 is a forward dependency, not a regression.
- Tests must NOT touch live receipts root — use the `GZKIT_ARB_RECEIPTS_ROOT` env override (already supported by `arb/paths.py`) and `tempfile.TemporaryDirectory()`.
