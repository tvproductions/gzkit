# Plan — OBPI-0.26.0-03: ADR Reconciliation comparison and decision

- **OBPI:** OBPI-0.26.0-03-adr-recon
- **Parent ADR:** ADR-0.26.0-governance-library-module-absorption (Heavy)
- **Brief:** `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md`
- **Sibling precedent:** OBPI-0.26.0-02-references (Decision: Exclude) and OBPI-0.26.0-01-adr-management (Completed)
- **ADR execution warning:** OBPI-0.26.0-01..03 are decision units first. If
  comparison shows Absorb requires substantial implementation, split the
  Absorb path into a follow-on execution unit rather than bundling it here.

## Context

The opsdev module `../airlineops/src/opsdev/lib/adr_recon.py` (607 lines) is
"Layer 2 ledger consumption" — reads ADR audit ledger entries and reconciles
ADR OBPI table status against ledger proof. The brief's Cross-Reference Matrix
row asserts gzkit has "no equivalent module," but a `rg` sweep of `src/gzkit/`
returns 22 files mentioning reconcile/reconciliation, including dedicated
modules:

- `src/gzkit/governance/trust_audits/reconcile.py`
- `src/gzkit/governance/adr_status_index.py`
- `src/gzkit/governance/frontmatter_coherence.py`
- `src/gzkit/commands/frontmatter_reconcile.py`
- `src/gzkit/commands/obpi_precomplete.py`
- `src/gzkit/commands/obpi_stages.py`
- `src/gzkit/ledger_semantics.py`

The "no equivalent" claim in the cross-reference matrix is potentially stale.
The OBPI is therefore a comparison + decision unit per the ADR's stated frame.
Three outcomes are nominally available (Absorb / Confirm / Exclude) per the
parent ADR's Decision section, but the OBPI brief's Assumptions narrow this
to Absorb / Exclude only ("No existing gzkit equivalent means either Absorb
or Exclude — there is no Confirm path"). If the audit finds gzkit already
owns substantively-equivalent reconciliation, that maps to Exclude with
rationale citing the gzkit surface that already covers the capability —
the same pattern OBPI-0.26.0-02 used for Exclude.

## Files

- **Read (audit, no edits):**
  - `../airlineops/src/opsdev/lib/adr_recon.py` (607 lines)
  - `../airlineops/src/opsdev/lib/ledger_schema.py` (only the imports adr_recon
    relies on — `BriefStatus`, `ObpiAuditEntry`, `parse_ledger_entry`)
  - `src/gzkit/governance/trust_audits/reconcile.py`
  - `src/gzkit/governance/adr_status_index.py`
  - `src/gzkit/governance/frontmatter_coherence.py`
  - `src/gzkit/commands/frontmatter_reconcile.py`
  - `src/gzkit/commands/obpi_precomplete.py`
  - `src/gzkit/commands/obpi_stages.py`
  - `src/gzkit/ledger_semantics.py`
- **Edit (brief only on Exclude/Confirm path):**
  - `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md`
- **Edit (Absorb path only — ADR warning says split into follow-on unit):**
  - `src/gzkit/` — adapted module (deferred)
  - `tests/` — coverage (deferred)

All edits stay inside the brief's Allowed Paths. No `pyproject.toml` edits,
no CI files, no opsdev edits (one-way absorption only).

## Steps

1. **Stage 1 lock + markers.** Claim the OBPI lock; write the per-OBPI
   pipeline marker so subsequent src/ or tests/ writes are unblocked.

   ```bash
   uv run gz obpi lock claim OBPI-0.26.0-03-adr-recon
   ```

2. **Stage 1→2 Confidence Gate.** Self-report confidence after reading the
   brief and sibling precedent. Initial confidence is ~85% (procedure mirrors
   OBPI-02; the unknown is the depth-and-quality of opsdev vs gzkit). If
   confidence remains <90% after reading both surfaces, run
   `uv run -m gzkit justify OBPI-0.26.0-03 --save` and validate before
   composing the comparison.

3. **Read opsdev source end-to-end.** Read all 607 lines of
   `../airlineops/src/opsdev/lib/adr_recon.py`. Catalog: dataclasses
   (`ObpiTableRow`, `DriftReport`, `ReconResult`, …); regex constants;
   reconcile-loop entry points; ledger-entry consumption pattern; filesystem
   contract (which `docs/design/adr/...` paths it walks); error handling
   semantics; cross-platform assumptions.

4. **Audit gzkit reconciliation surface.** For each gzkit module listed under
   Files (Read), record: scope (what it reconciles), ledger-consumption
   pattern, fail-closed posture (warn vs fail vs auto-rebuild), test coverage
   under `tests/governance/` and `tests/commands/`. Note overlap with opsdev
   surface and identify deltas.

5. **Build dimension-by-dimension comparison table** in the brief mirroring
   the OBPI-0.26.0-02 pattern: feature completeness, error handling,
   cross-platform robustness, test coverage, fit-with-gzkit-conventions.
   Each cell must cite concrete line ranges or `tests/` paths — no vague
   adjectives.

6. **Record final decision.** Decision is one of:
   - **Absorb:** opsdev provides materially stronger capability gzkit lacks.
     Per the ADR execution warning, do not bundle absorb implementation in
     this brief — record decision + scoped follow-on plan, file follow-on
     OBPI/GHI, close this brief on the decision artifact.
   - **Exclude:** opsdev module is ops-specific (e.g., depends on
     `airlineops.paths.subpaths`, hardcoded ops surfaces) and fails the
     subtraction test, OR gzkit's existing reconciliation surface already
     covers the capability with comparable or stronger fidelity. Cite
     concrete line anchors and gzkit-side equivalents.

7. **Update brief with REQ-01..REQ-05 evidence.** Each acceptance criterion
   gets a concrete observation (line anchors, dimension table cites, Gate 4
   N/A rationale or behave artifact name).

8. **Fix `briefs/` → `obpis/` path drift in Verification section.** The brief
   Verification commands reference `briefs/OBPI-0.26.0-03-adr-recon.md` (3
   occurrences) but the canonical path is `obpis/`. Same fix the sibling
   OBPI-0.26.0-02 brief recorded.

9. **Stage 3 verification.**

   ```bash
   uv run gz arb ruff
   uv run gz arb typecheck
   uv run gz arb step --name unittest -- uv run gz test --obpi OBPI-0.26.0-03-adr-recon
   uv run gz covers OBPI-0.26.0-03-adr-recon --json
   uv run gz validate --documents --surfaces --brief-headings
   ```

10. **Stage 4 ceremony.** Render the canonical Stage 4 template — Value
    Narrative, Key Proof, Evidence table with ARB receipt IDs, REQ coverage
    table with `@covers` locations, files modified. Wait for human
    attestation (Heavy lane).

11. **Stage 5 sync.**

    ```bash
    uv run gz obpi precomplete OBPI-0.26.0-03-adr-recon
    uv run gz obpi complete OBPI-0.26.0-03-adr-recon \
      --attestor 'Jeffry Babb' \
      --attestation-text "$(cat /tmp/obpi-attestation.txt)" \
      --implementation-summary "$(cat /tmp/obpi-summary.md)" \
      --key-proof "$(cat /tmp/obpi-keyproof.md)" \
      --attestor-present
    uv run gz obpi lock release OBPI-0.26.0-03-adr-recon
    rm -f .claude/plans/.pipeline-active-OBPI-0.26.0-03.json
    uv run gz git-sync --apply
    uv run gz obpi reconcile OBPI-0.26.0-03-adr-recon
    uv run gz adr status ADR-0.26.0 --json > /dev/null
    uv run gz git-sync --apply
    ```

## Verification

Brief-specific verification commands (also embedded in the brief itself):

```bash
test -f ../airlineops/src/opsdev/lib/adr_recon.py
# Expected: opsdev source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test --obpi OBPI-0.26.0-03-adr-recon
# Expected: comparison or absorbed implementation remains green

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

Lane-required heavy commands:

```bash
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# Heavy lane: docs build clean (only meaningful if brief edits affect mkdocs build)

# uv run -m behave features/heavy_lane_gate4.feature
# Only required when operator-visible behavior changes; record N/A otherwise.
```

## Notes

- **Decision-unit framing.** Per the ADR execution warning, this brief is a
  decision unit. If decision is Absorb, scope of THIS brief is the decision
  artifact; absorb implementation goes to a follow-on OBPI or GHI.
- **Possible Confirm-shaped Exclude.** If gzkit's existing reconciliation
  surface already covers the capability, the brief's "Absorb or Exclude"
  rule pushes the outcome toward Exclude with rationale citing the gzkit
  modules that already own the capability. This is the same shape
  OBPI-0.26.0-02 used (Exclude with five-point ops-specific rationale).
- **Path-drift fix.** The brief's Verification commands reference `briefs/`
  but the canonical path is `obpis/`; fix in-flight as part of brief authoring.
- **No `pypdf`-style new dependency.** opsdev `adr_recon` imports
  `airlineops.paths.subpaths` and `opsdev.lib.ledger_schema` — both
  ops-internal. Adapting either to gzkit would require both upstream
  ledger-schema absorption (OBPI-0.26.0-05) and `airlineops.paths`
  removal — both out of scope for this brief.
- **PII rule.** Operator name only in attestor field (`Jeffry Babb`); no
  personal email anywhere in brief, ledger, attestation text, or commits.
- **Pre-mortem (operator-economy framing).** The most likely failure mode
  is reading opsdev source while skimming gzkit's reconciliation surface —
  reaching a premature Absorb conclusion that ignores already-shipped gzkit
  capability. Mitigation: audit gzkit modules first (Step 4) before
  composing the dimension table, so each opsdev capability is evaluated
  against an explicit gzkit baseline rather than against absence.
