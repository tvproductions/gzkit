# Plan — OBPI-0.26.0-04: ADR Governance comparison and decision

- **OBPI:** OBPI-0.26.0-04-adr-governance
- **Parent ADR:** ADR-0.26.0-governance-library-module-absorption (Heavy)
- **Brief:** `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md`
- **Sibling precedent:** OBPI-0.26.0-02-references (Decision: Exclude),
  OBPI-0.26.0-03-adr-recon (in-flight comparison), OBPI-0.26.0-01-adr-management
  (Completed)
- **ADR execution warning:** OBPI-0.26.0-01..04 are decision units first. If
  comparison shows Absorb requires substantial implementation, split the
  Absorb path into a follow-on execution unit (OBPI or GHI) rather than
  bundling it here.

## Context

The opsdev module `../airlineops/src/opsdev/lib/adr_governance.py` (535 lines)
is "ADR governance tooling: evidence audit, autolink, verification reports"
internalized from three opsdev scripts:

- `scripts/adr_evidence_audit.py` — scans ADRs for `## Evidence` section presence
- `scripts/adr_autolink.py` — auto-rewrites ADR `## Verification` sections from
  `@covers` decorators discovered in `tests/`
- `scripts/adr_verification_report.py` — emits ADR coverage report

It imports `airlineops.paths.subpaths` and `opsdev.lib.ledger_schema` — both
ops-internal — and hardcodes `docs_path("design", "adr")` and `Path("tests")`.

The brief frames gzkit's equivalent as "Partial in `src/gzkit/ledger.py`," but
ledger.py (728 lines) is the ledger-event authoring surface, not ADR governance
policy enforcement. The actual gzkit surfaces that own ADR governance are:

- `src/gzkit/commands/adr_audit.py` (790+ lines) — `gz adr audit-check`,
  `gz adr emit-receipt`, audit-begin/end ceremony, full attestation
  authenticity gating, kind/lane/sensitivity matrix enforcement.
- `src/gzkit/commands/adr_coverage.py` — `gz adr covers-check` and
  REQ/`@covers` traceability mechanics.
- `src/gzkit/commands/covers.py` — `gz covers` REQ-coverage report.
- `.gzkit/skills/gz-adr-autolink/SKILL.md` — explicitly documents that "there
  is no dedicated `gz adr autolink` command in this repository"; the canonical
  workflow is manual rg-of-`@covers` followed by `gz adr audit-check`.

The OBPI is therefore a comparison + decision unit per the ADR's stated frame.
Three outcomes are nominally available (Absorb / Confirm / Exclude). The brief
does NOT narrow the option space the way OBPI-0.26.0-03 did (which restricted
to Absorb/Exclude under "no equivalent" framing); here the brief's Assumptions
explicitly note "gzkit's ledger.py may embed some governance enforcement but
likely lacks the breadth of a dedicated 535-line governance module" — leaving
all three outcomes open.

The substantive question is per-subcommand:

1. **evidence_audit** vs `gz adr audit-check` — gzkit's audit-check is far
   richer (REQ coverage, evidence-section presence, attestation linkage). The
   opsdev surface is shallower and harder-coded to ops paths.
2. **adr_autolink** vs `.gzkit/skills/gz-adr-autolink` (manual workflow) — this
   is the one functional gap. opsdev mechanically rewrites the `## Verification`
   section of an ADR file from discovered `@covers` annotations; gzkit does
   the same work as a manually-curated step. Whether to absorb depends on
   whether the rewrite is a velocity bottleneck or a doctrine choice.
3. **verification_report** vs `gz covers` / `gz adr covers-check` — gzkit's
   surfaces emit the same report shape with stronger REQ-level fidelity.

## Files

- **Read (audit, no edits):**
  - `../airlineops/src/opsdev/lib/adr_governance.py` (535 lines)
  - `../airlineops/src/opsdev/lib/ledger_schema.py` (only the imports
    `adr_governance.py` uses — `CoversMapEntry`, `create_timestamp`)
  - `src/gzkit/commands/adr_audit.py` (790+ lines)
  - `src/gzkit/commands/adr_coverage.py`
  - `src/gzkit/commands/covers.py`
  - `src/gzkit/commands/adr_promote.py` (sibling structural reference)
  - `src/gzkit/ledger.py` (the brief's stated comparison target — confirm it is
    not the right comparison; the ADR governance modules above are)
  - `.gzkit/skills/gz-adr-autolink/SKILL.md` (canonical "no autolink command"
    doctrine source)
  - `tests/commands/test_adr_audit*.py`, `tests/commands/test_covers*.py`
    (gzkit-side test coverage signal)
- **Edit (brief only on Exclude/Confirm path):**
  - `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md`
- **Edit (Absorb path only — ADR warning says split into follow-on unit):**
  - `src/gzkit/` — adapted module (deferred)
  - `tests/` — coverage (deferred)

All edits stay inside the brief's Allowed Paths. No `pyproject.toml` edits,
no CI files, no opsdev edits (one-way absorption only).

## Steps

1. **Stage 1 lock + markers.** Claim the OBPI lock; write the per-OBPI
   pipeline marker so subsequent src/ or tests/ writes are unblocked.

   ```bash
   uv run gz obpi lock claim OBPI-0.26.0-04-adr-governance
   ```

2. **Stage 1→2 Confidence Gate.** Self-report confidence after reading the
   brief and sibling precedent. Initial confidence is ~85% (procedure mirrors
   OBPI-02 and OBPI-03; the unknown is the per-subcommand depth comparison
   between opsdev's three internalized scripts and gzkit's three surfaces).
   If confidence remains <90% after reading both surfaces, run
   `uv run -m gzkit justify OBPI-0.26.0-04 --save` and validate before
   composing the comparison.

3. **Read opsdev source end-to-end.** Read all 535 lines of
   `../airlineops/src/opsdev/lib/adr_governance.py`. Catalog by internalized
   script:
   - **evidence_audit:** `AdrRecord`, `scan_file_for_evidence`,
     `evidence_audit`, file-pattern regex, status regex. ~150 lines.
   - **adr_autolink:** `parse_test_file`, `collect_test_map`,
     `render_verification`, `write_into_adr`, `adr_autolink`,
     `extract_test_paths`, `discover_covers`, `extract_verification_block`,
     `render_verification_section`, `_normalize_adr_id`,
     `_write_covers_ledger`. ~250 lines.
   - **verification_report:** `verification_report`. ~80 lines.
   - Catalog: filesystem contract (`docs_path("design", "adr")`,
     `Path("tests")` hardcoded), error handling, cross-platform assumptions
     (UTF-8 explicit), regex semantics.

4. **Audit gzkit ADR-governance surface.** For each gzkit module listed under
   Files (Read), record: scope (what it audits/reports/links), ledger or
   `@covers` consumption pattern, fail-closed posture (warn vs fail vs
   policy-breach exit 3), test coverage under `tests/commands/`. Map
   per-subcommand:
   - opsdev `evidence_audit` → gzkit `gz adr audit-check` + `_collect_obpi_findings`
     in `adr_audit.py:62`.
   - opsdev `adr_autolink` → `.gzkit/skills/gz-adr-autolink/SKILL.md` (manual)
     + `gz covers` discovery, but **no automated `## Verification` rewrite**.
   - opsdev `verification_report` → `gz covers` / `gz adr covers-check` /
     `gz adr coverage` (commands defined in `adr_coverage.py`).

5. **Confirm or correct the brief's "Partial in `src/gzkit/ledger.py`" claim.**
   Read the relevant sections of `src/gzkit/ledger.py` and verify whether it
   contains ADR governance policy enforcement or only ledger-event authoring.
   If the latter, record this as a brief-side observation (the comparison
   target named in the brief is the wrong file) without editing the brief
   frontmatter or scope — the right comparison is the gzkit modules listed in
   Step 4.

6. **Build dimension-by-dimension comparison table** in the brief mirroring
   the OBPI-0.26.0-02 pattern: rows = the three opsdev internalized scripts;
   columns = feature completeness, error handling, cross-platform robustness,
   test coverage, fit-with-gzkit-conventions, gzkit equivalent. Each cell
   must cite concrete line ranges or `tests/` paths — no vague adjectives.

7. **Record final decision (one of):**
   - **Absorb:** opsdev provides materially stronger capability gzkit lacks
     across multiple subcommands, OR a single subcommand (most likely
     `adr_autolink`) is worth absorbing with a documented adapter path. Per
     the ADR execution warning, do not bundle absorb implementation in this
     brief — record decision + scoped follow-on plan, file follow-on
     OBPI/GHI, close this brief on the decision artifact.
   - **Confirm:** opsdev module is broadly equivalent to gzkit's combined
     surface (`adr_audit.py` + `adr_coverage.py` + `covers.py` + the
     gz-adr-autolink skill), with no material capability gap. Cite concrete
     line anchors and gzkit-side equivalents per subcommand.
   - **Exclude:** opsdev module is ops-specific (depends on
     `airlineops.paths.subpaths`, hardcoded `docs_path("design", "adr")`
     surface), AND/OR gzkit's existing surfaces already cover the capability
     with comparable or stronger fidelity, AND/OR the autolink-rewrite
     subcommand is a doctrine choice (manual workflow per `.gzkit/skills/
     gz-adr-autolink/SKILL.md`) rather than a capability gap. Cite concrete
     line anchors and gzkit-side equivalents.

   Pre-mortem hypothesis (do not pre-decide): the most likely landing is
   **Exclude** with three-line rationale citing (a) ops-specific imports,
   (b) gzkit's stronger audit-check + coverage surfaces, (c) the autolink
   rewrite being a documented doctrine choice — but Step 6's dimension table
   must drive the decision, not this hypothesis.

8. **Update brief with REQ-01..REQ-05 evidence.** Each acceptance criterion
   gets a concrete observation:
   - REQ-01: brief frontmatter or body records exactly one final decision
   - REQ-02: rationale cites concrete capability/robustness/ergonomics
     differences with line anchors
   - REQ-03: Absorb path only — adapted module/tests in gzkit, or follow-on
     OBPI/GHI link recorded
   - REQ-04: Confirm/Exclude path — explanation of why no upstream absorption
     is warranted
   - REQ-05: Gate 4 N/A rationale (no operator-visible behavior change for
     decision-only briefs) or behave artifact name

9. **Heading sweep.** Verify brief evidence sections will use H3
   (`### Implementation Summary`, `### Key Proof`, `### Closing Argument`)
   per `.claude/rules/brief-heading-conventions.md`. The current brief uses
   `### Closing Argument` correctly; no other H3 evidence sections present yet
   (they are added at Stage 5).

10. **Stage 3 verification.**

    ```bash
    uv run gz arb ruff
    uv run gz arb typecheck
    uv run gz arb step --name unittest -- uv run gz test --obpi OBPI-0.26.0-04-adr-governance
    uv run gz covers OBPI-0.26.0-04-adr-governance --json
    uv run gz validate --documents --surfaces --brief-headings
    ```

    Heavy lane addition (only meaningful if brief edits affect mkdocs build):

    ```bash
    uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
    ```

11. **Stage 4 ceremony.** Render the canonical Stage 4 template — Value
    Narrative, Key Proof, Evidence table with ARB receipt IDs, REQ coverage
    table with `@covers` locations (parity-gated by Stage 3 Phase 1b), files
    modified. Wait for human attestation (Heavy lane).

12. **Stage 5 sync.**

    ```bash
    uv run gz obpi precomplete OBPI-0.26.0-04-adr-governance
    uv run gz obpi complete OBPI-0.26.0-04-adr-governance \
      --attestor 'Jeffry Babb' \
      --attestation-text "$(cat /tmp/obpi-attestation.txt)" \
      --implementation-summary "$(cat /tmp/obpi-summary.md)" \
      --key-proof "$(cat /tmp/obpi-keyproof.md)" \
      --attestor-present
    uv run gz obpi lock release OBPI-0.26.0-04-adr-governance
    rm -f .claude/plans/.pipeline-active-OBPI-0.26.0-04.json
    rm -f .claude/plans/.pipeline-active.json   # only if it points to this OBPI
    uv run gz git-sync --apply
    uv run gz obpi reconcile OBPI-0.26.0-04-adr-governance
    uv run gz adr status ADR-0.26.0 --json > /dev/null
    uv run gz git-sync --apply
    ```

## Verification

Brief-specific verification commands (also embedded in the brief itself):

```bash
test -f ../airlineops/src/opsdev/lib/adr_governance.py
# Expected: opsdev source under review exists

test -f src/gzkit/ledger.py
# Expected: gzkit comparison target exists (brief-stated; actual comparison
# is the adr_audit/adr_coverage/covers triad, captured in the brief body).

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-04-adr-governance
# Expected: comparison or absorbed implementation remains green

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md
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
- **Brief comparison-target correction (Step 5).** The brief names
  `src/gzkit/ledger.py` as the comparison target, but ledger.py is the
  ledger-event authoring surface, not ADR governance policy enforcement. The
  actual comparison is the gzkit `adr_audit.py` + `adr_coverage.py` +
  `covers.py` triad plus the `gz-adr-autolink` skill. Record this observation
  in the brief body (Comparison section); do not edit the brief's
  Source Material header — that is parent-ADR-authored framing.
- **All three outcomes open.** Unlike OBPI-0.26.0-03 (which narrowed to
  Absorb/Exclude), this brief leaves Confirm on the table. If gzkit's three
  surfaces collectively cover the opsdev module's three internalized scripts
  with comparable fidelity, Confirm is structurally available — but the
  ops-specific imports (`airlineops.paths.subpaths`) make Exclude the more
  likely landing under the subtraction test.
- **No `pypdf`-style new dependency.** opsdev `adr_governance` imports
  `airlineops.paths.subpaths` and `opsdev.lib.ledger_schema` — both
  ops-internal. Adapting either to gzkit would require both upstream
  ledger-schema absorption (OBPI-0.26.0-05) and `airlineops.paths` removal —
  both out of scope for this brief.
- **Autolink path is the most interesting Absorb candidate.** The other two
  subcommands map cleanly to gzkit equivalents; only `adr_autolink`'s
  automated `## Verification` rewrite has no gzkit equivalent (the
  `gz-adr-autolink` skill explicitly documents the manual workflow as
  canonical). If the comparison surfaces a velocity argument for absorbing
  the rewrite, route it as a follow-on OBPI/GHI per the ADR execution
  warning, not as in-flight implementation here.
- **PII rule.** Operator name only in attestor field (`Jeffry Babb`); no
  personal email anywhere in brief, ledger, attestation text, or commits.
- **Pre-mortem (operator-economy framing).** The most likely failure mode
  is reading opsdev source while skimming gzkit's ADR governance surface —
  reaching a premature Absorb conclusion that ignores already-shipped gzkit
  capability (mirror failure mode of OBPI-0.26.0-03). Mitigation: audit
  gzkit modules first (Step 4) before composing the dimension table, so
  each opsdev capability is evaluated against an explicit gzkit baseline
  rather than against absence.
