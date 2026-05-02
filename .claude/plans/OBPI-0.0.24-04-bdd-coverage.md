# Plan: OBPI-0.0.24-04-bdd-coverage

OBPI: `OBPI-0.0.24-04-bdd-coverage`
Parent ADR: `ADR-0.0.24-attestation-receipt-binding` (foundation, heavy)

## Context

OBPI-01 (`gz validate --attestation-receipts` worker + scope) and OBPI-02
(receipt-binding gate wired into `gz obpi complete`, `gz adr emit-receipt`,
`gz obpi emit-receipt` with `arb-meta-receipt-bind-…` self-attesting receipt
family) are both `attested_completed`. OBPI-03 landed the AGENTS.md / arb-
middleware / validate-manpage doc updates that align prose with the now-
mechanical contract.

This OBPI is the BDD tier that exercises the receipt-binding gate end-to-end
through the registered CLI surfaces — no subprocess mocking, real `gz validate
--attestation-receipts`, real `gz obpi complete`, real `gz adr emit-receipt`.
The 11 REQs from OBPI-01/02 (REQ-0.0.24-01-01..06 + REQ-0.0.24-02-01..05) each
need at least one `@REQ-0.0.24-NN-MM`-tagged passing scenario so
`uv run gz validate --behave-req-tags` exits 0 without a waiver entry for
ADR-0.0.24.

The current `data/behave_coverage_waivers.json` carries an
`adr-0.0.24-0.0.25-uncommitted-draft` waiver covering this ADR; landing this
OBPI means **removing** the OBPI-04 waiver entry (per brief REQ-5) so the
gate stops accepting "deferred coverage" for this work.

Inherits foundation-kind brief-level attestation (Heavy + Foundation = TTY +
`ATTEST` per § Lane & Kind & Sensitivity Attestation Matrix).

## Files

| Path | Change |
|------|--------|
| `features/attestation_receipt_binding.feature` | NEW — file-level `# @covers REQ-0.0.24-01-01` through `REQ-0.0.24-02-05` (11 lines), Feature header, then ≥11 `@REQ-0.0.24-NN-MM`-tagged scenarios (one per REQ minimum) exercising validator + gate behavior. |
| `features/steps/attestation_receipt_binding_steps.py` | NEW — step module with: receipt-fixture builders (`_write_arb_step_receipt`, `_write_arb_lint_receipt`), `GZKIT_ARB_RECEIPTS_ROOT` env juggling, attestation-string composers, ADR/OBPI brief seeders matching the lane × kind matrix, ledger inspectors (`@then` for `arb-meta-receipt-bind` event presence/absence), and a `pexpect`-shaped subprocess driver for the TTY+ATTEST scenario that feeds `ATTEST\n` to a real `gz obpi complete` child. |
| `data/behave_coverage_waivers.json` | EDIT — remove the `OBPI-0.0.24-04-bdd-coverage` waiver entry (and any sibling OBPI-0.0.24-NN entries that were under the `adr-0.0.24-0.0.25-uncommitted-draft` rationale and are now covered by this feature file). Verify with `uv run gz validate --behave-req-tags`. |

> **No source changes.** OBPI-04 is BDD-only; `src/**` and unit `tests/**`
> are explicitly denied by the brief. The waivers JSON edit is the single
> data-file mutation and is in the brief allowlist.

## Steps

1. **Read the canonical step conventions and existing PTY-fed test pattern.**
   Re-read `features/steps/gz_steps.py:209` (`_invoke` in-process driver,
   used for non-TTY scenarios) and existing PTY-fed unit tests (search
   `tests/commands/test_obpi_complete.py` for `pty.fork`/`pexpect` patterns
   from OBPI-02's wiring tests). The BDD tier uses real subprocess for the
   TTY scenario per brief REQ-9 — DO NOT in-process the attestation gate.

2. **Build the receipt-fixture toolkit in the step module
   (`features/steps/attestation_receipt_binding_steps.py`).** Helpers:
   - `_write_arb_lint_receipt(root: Path, run_id: str, exit_status: int = 0)` → writes
     `arb-ruff-<run_id>.json` matching the `gzkit.arb.lint_receipt.v1` schema
     used by `gzkit.arb.ruff_reporter._write_lint_receipt` (sample one from
     `artifacts/receipts/` to capture the exact field shape).
   - `_write_arb_step_receipt(root: Path, name: str, run_id: str, exit_status: int = 0)`
     → writes `arb-step-<name>-<run_id>.json` matching
     `gzkit.arb.step_receipt.v1` (mirror `_write_step_receipt`).
   - `_set_receipts_root(context, root: Path)` → assigns
     `os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(root)` and stashes the
     prior value on `context` for `environment.py` `after_scenario` cleanup.
   - `_compose_attestation(*, claim: str, receipt_id: str)` → returns the
     canonical AGENTS.md § Attestation form `"<claim> (lint: receipt
     <receipt_id>)"` for the test.
   Place these as module-private helpers above the `@given`/`@when`/`@then`
   blocks. NO live `artifacts/receipts/` reads; NO live `.gzkit/ledger.jsonl`
   reads (per brief REQ-3, REQ-4).

3. **Author the validator-scope scenarios — REQ-0.0.24-01-01 .. -06
   (6 scenarios).** Each scenario uses the fixture toolkit from Step 2,
   then runs `gz validate --attestation-receipts <text> --lane heavy --kind
   feature` (or the matching lane/kind axes per the REQ) via the in-process
   `_invoke` from `gz_steps.py`. Assertions:
   - REQ-01: resolved-receipt happy path → exit 0, output contains `resolved`.
   - REQ-02: missing receipt ID → exit 3, output contains `missing`.
   - REQ-03: receipt with `exit_status=1` → exit 3, output contains
     `status_mismatch`.
   - REQ-04: claim-category mismatch (cite `lint:` but receipt is a
     `step-typecheck-…`) → exit 3, output contains `claim_mismatch`.
   - REQ-05: malformed receipt ID (e.g. `arb-ruff-zzz`) → exit non-zero,
     output reports the malformed entry (not silently skipped).
   - REQ-06: zero receipts in attestation. Two sub-scenarios — heavy/foundation
     yields exit 3 (fail-closed), lite/feature yields exit 0 (warn-only).
     One file-level `@REQ-0.0.24-01-06` tag suffices; both scenarios carry
     the same tag.

4. **Author the gate-wiring scenarios — REQ-0.0.24-02-01 .. -05 (5
   scenarios).** Each scenario seeds a temp workspace with
   `_init_with_agent_surfaces(mode="heavy")` (or `mode="lite"` per REQ),
   creates a real ADR + OBPI brief whose lane/kind matches the REQ-under-
   test, builds receipt fixtures via Step 2 helpers, then invokes the
   appropriate end-to-end CLI:
   - REQ-01: heavy-lane brief + valid receipt → `gz obpi complete` exits 0,
     **and** the ledger contains both an `obpi_receipt_emitted` event and
     an `audit_receipt_emitted` event with `extra.receipt_event ==
     "meta-receipt-bind"`.
   - REQ-02: heavy-lane + missing receipt → `gz obpi complete` exits 3,
     ledger is unchanged (no `obpi_receipt_emitted`).
   - REQ-03: lite-non-foundation + missing receipt → `gz obpi complete`
     exits 0 (warn-only), warning in stdout, completion event still recorded.
   - REQ-04: foundation-kind lite-lane + missing receipt → exits 3
     (foundation overrides lite).
   - REQ-05: ADR closeout mirror — `gz adr emit-receipt --event closed`
     (or `validated`/`attested`/`accepted` per the wiring's
     `_HUMAN_ATTESTATION_RECEIPT_EVENTS`) on heavy lineage with missing
     receipt exits 3.

   For REQs 02-01 / 02-04 the brief explicitly requires the TTY + `ATTEST`
   path be exercised via a `pexpect`-shaped subprocess driver. Use the
   POSIX-only `pty.fork` pattern from `gz-obpi-pipeline` SKILL Stage 5
   Step 2 (the same pattern OBPI-02 uses in unit tests). On Windows the
   scenario is skipped via behave's `@skipif`-style tag (see
   `environment.py` for the existing skip mechanism); document the skip
   in the scenario docstring. The PTY driver:
   - spawns `uv run gz obpi complete <id> --attestor "BDD User"
     --attestation-text <text>` under `pty.fork`,
   - reads child output until both `ATTEST` and `confirm` appear in the
     buffer,
   - writes `ATTEST\n` once,
   - waits for the child to exit, captures status.
   This is the *real* PTY-enforcement traversal mandated by brief REQ-9.

5. **Wire scenario-level `@REQ-0.0.24-NN-MM` tags + file-level `# @covers`
   header.** At the very top of `attestation_receipt_binding.feature`:
   ```
   # @covers REQ-0.0.24-01-01
   # @covers REQ-0.0.24-01-02
   ...
   # @covers REQ-0.0.24-02-05
   Feature: Attestation receipt-binding gate
     ...
   ```
   The `audit_behave_req_tags` check (`src/gzkit/governance/trust_audits.py:782`)
   asserts every file-level `# @covers REQ-…` has at least one matching
   `@REQ-…`-tagged scenario in the same file (feature → feature direction
   per the parity-diff analysis). Both surfaces must agree or the check
   fail-closes.

6. **Remove the waiver entry.** Edit `data/behave_coverage_waivers.json`:
   delete the `OBPI-0.0.24-04-bdd-coverage` key under `waivers`. Do NOT
   touch other ADR-0.0.24 OBPI waivers if their REQs are not covered by
   this feature file (verify by grep before deletion). The brief targets
   OBPI-04 specifically; sibling cleanup belongs to its own brief.

7. **Verify (REQ-5, REQ-6).** Run the brief verification block in order
   and capture output for the Stage 4 evidence table:
   - `uv run gz arb ruff` → lint receipt
   - `uv run gz arb step --name unittest -- uv run -m unittest -q` → unittest receipt
   - `uv run gz arb step --name behave -- uv run -m behave features/attestation_receipt_binding.feature` → BDD receipt
   - `uv run gz validate --behave-req-tags` → exit 0 expected
   - `uv run gz validate --documents` → exit 0 expected (waiver edit
     is JSON, not docs, but heavy-lane sweep includes this)
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` → docs receipt
   ARB-wrapped per `AGENTS.md` § Attestation Canonical invocations so the
   Stage 4 receipts table cites concrete `arb-step-…` IDs.

8. **PII guard (REQ-8).** Before committing, grep the new feature file,
   the new step module, and the waivers edit for the operator's personal
   email substring (`ahuimanu@gmail.com`). The fixture user identity in
   step-module subprocess setup MUST use `BDD User` /
   `bdd@example.com` (the existing convention in `gz_steps.py:147-156`),
   never the operator's address. If any hit lands, abort and fix.

## Verification

```bash
uv run gz lint
uv run -m behave features/attestation_receipt_binding.feature
uv run gz validate --behave-req-tags
```

ARB-wrapped (heavy-lane evidence — required for Stage 4 receipt-binding
gate per OBPI-02):

```bash
uv run gz arb ruff
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name behave -- uv run -m behave features/attestation_receipt_binding.feature
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Notes

- **Lane:** Heavy (per brief). Foundation-kind brief-level attestation
  fires at OBPI completion; TTY + `ATTEST` required.
- **No source / no unit tests:** Brief denies `src/**` and unit `tests/**`.
  Gate 2 (TDD) for this OBPI is satisfied by behave passing — the brief
  Gate 2 prose explicitly notes "the implementation is upstream; scenarios
  are the end-to-end check".
- **Scope-collision warnings from `gz plan audit`:** All `tests/fixtures/
  ledger/` and `docs/design/adr/foundation/ADR-0.0.24-attestation-
  receipt-binding/**` collisions are shared-fixture / parent-package
  patterns common to every OBPI in those ADRs — not real conflicts.
  This OBPI does not write to `tests/fixtures/ledger/` (fixtures are
  built in tempdirs per-scenario) and only reads from the parent ADR
  package.
- **`pexpect` is not in `pyproject.toml`.** Use `pty.fork` from stdlib
  per the AGENTS.md § STDLIB-FIRST DOCTRINE — `pty` is a stdlib module
  on POSIX. Adding `pexpect` would require ADR justification and is out
  of scope for this OBPI. The brief's "pexpect-shaped" language is a
  shape descriptor, not a dependency mandate.
- **Windows skip:** `pty` is POSIX-only. The TTY + `ATTEST` scenario
  carries a tag that skips on Windows via `before_scenario` in
  `features/environment.py`. Document the skip in the scenario doc-
  string so audit shows the limitation transparently. Non-TTY scenarios
  (validator-scope REQs 01-01..01-06, gate-wiring REQs 02-02/02-03/02-05
  via the in-process `_invoke`) run on every platform.
- **Destination-in-mind disclosure (Step 6a):** I had already concluded
  the structure (one feature file with 11+ scenarios + one step module,
  PTY-fed for the TTY scenarios, in-process `_invoke` for the rest)
  before drafting this plan, driven by direct reads of the brief
  Requirements list and the existing `gz_steps.py` / `arb.feature`
  conventions. **Rejected alternatives:** (a) splitting into two feature
  files (validator-scope vs gate-wiring) — rejected because
  `audit_behave_req_tags` is per-file and split files complicate the
  file-level `# @covers` header; one file keeps the REQ → scenario
  audit trail mechanical. (b) reusing existing `obpi_complete.feature`
  by appending scenarios — rejected because the brief allowlist names a
  *new* feature file (`features/attestation_receipt_binding.feature`)
  and modifying an unrelated heavy-lane feature would expand scope.
  (c) mocking the PTY check via patching
  `_enforce_human_attestation_authenticity` — explicitly rejected by
  brief REQ-9 ("DO NOT patch the PTY check internally; the BDD tier is
  end-to-end and must traverse the real PTY enforcement path"). (d)
  using `pexpect` for the PTY driver — rejected per Stdlib-First
  doctrine; `pty.fork` from stdlib is the canonical equivalent.
