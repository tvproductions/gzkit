## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**OBPI:** OBPI-0.35.0-06-validate-rendition-lineage (parent ADR-0.35.0-canon-entry-corpus-landing, item 6, Heavy lane)
**Current acceptance input_digest:** `90807b7ef6ec9ae9f6df25e05c08bcc723d984ed0f40d4d5feb7f21de3507931`

**1. Value Narrative**

Before this OBPI, `AGENTS.md`'s owned-vs-hand-authored split (OBPI-0.35.0-04) had no gate: a committed rendition could drift from the corpus it claims to derive from — hand-authored prose could sit inside a section marked `corpus-owned` — and nothing would ever exit non-zero over it. `gz validate --rendition-lineage` now exists: it fails closed (exit 3) the moment an owned section's committed text stops matching its deterministic materialization of the effective corpus, names the offending section, and prescribes the corpus round-trip as the only sanctioned recovery — while unowned bytes and never-yet-published lineages are disclosed as measured debt, never used to fail the gate. The coverage figure (owned sections/bytes vs. total) is computed at run time and surfaced on every run, so the gate's partial scope is declared rather than implied.

**2. Key Proof**

```
$ uv run gz obpi present-evidence OBPI-0.35.0-06-validate-rendition-lineage --json
{
  "obpi_id": "OBPI-0.35.0-06-validate-rendition-lineage",
...
  "demos": [
    {
      "command": "uv run gz validate --rendition-lineage",
      "ran": true,
      "exit_status": 0,
      "stdout_tail": "Validated: rendition_lineage\n\n✓ All validations passed (1 scopes).\n[advisory] rendition-lineage: What is ungraded: committed rendition 'AGENTS.md/root' declares 12 corpus-owned sections but carries no committed lineage artifact (/Users/jeff/Documents/Code/gzkit/.gzkit/renditions/AGENTS.md/root.lineage.json is absent), so those sections have no provenance baseline to grade against and are reported UNGRADED.\nWhy it matters: ADR-0.35.0 § Decision item 4 grades owned sections against a committed lineage artifact; counting these as owned coverage would claim proof this gate does not have. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.\nNext step: publish the rendition and its lineage together — `gz content compose AGENTS.md --consumer root`, then `gz content commit AGENTS.md --consumer root`.\n[advisory] rendition-lineage: 1 committed rendition(s) graded; 0/22 sections owned, 0/47851 bytes owned (0.0%); 12 section(s) / 41846 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4)."
    },
    {
      "command": "uv run gz validate --rendition-lineage --json",
      "ran": true,
      "exit_status": 0,
      "stdout_tail": "{\n  \"valid\": true,\n  \"errors\": []\n}\n[advisory] rendition-lineage: What is ungraded: committed rendition 'AGENTS.md/root' declares 12 corpus-owned sections but carries no committed lineage artifact (/Users/jeff/Documents/Code/gzkit/.gzkit/renditions/AGENTS.md/root.lineage.json is absent), so those sections have no provenance baseline to grade against and are reported UNGRADED.\nWhy it matters: ADR-0.35.0 § Decision item 4 grades owned sections against a committed lineage artifact; counting these as owned coverage would claim proof this gate does not have. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.\nNext step: publish the rendition and its lineage together — `gz content compose AGENTS.md --consumer root`, then `gz content commit AGENTS.md --consumer root`.\n[advisory] rendition-lineage: 1 committed rendition(s) graded; 0/22 sections owned, 0/47851 bytes owned (0.0%); 12 section(s) / 41846 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4)."
    }
  ],
  "receipts": [
    {
      "step": "ruff",
      "found": true,
      "receipt_id": "arb-ruff-ab86ee6b0199483b8eb85f82e0394ec0.json",
      "exit_status": 0
    },
    {
      "step": "typecheck",
      "found": true,
      "receipt_id": "arb-step-typecheck-1c706bdc42bf4db4bc86c02edaa1cbaf.json",
      "exit_status": 0
    },
    {
      "step": "unittest",
      "found": true,
      "receipt_id": "arb-step-unittest-b1a805a8b6b04d44abecba040eec88e0.json",
      "exit_status": 0
    }
  ],
  "covers_total": 8,
  "covers_uncovered": 0,
  "attestable": true,
  "blockers": [],
  "review_blockers": []
}
```

The gate itself, run live against the current repo, discloses (never fails) `AGENTS.md`'s 12 never-yet-published owned sections as UNGRADED and reports `0/22 sections owned, 0/47851 bytes owned (0.0%)` — the operator-ruled bootstrap-tolerant behavior for a lineage OBPI-0.35.0-07 has not yet published, proven live rather than only by fixture.

**3. Evidence**

**Stage-3 gates — all re-run fresh against the current digest (`90807b7e...`), cited by receipt, not older rounds:**

| Check | Command | Result |
|-------|---------|--------|
| Tests | `arb:unittest` (see below) | 10159/10159 pass, 4 skipped — receipt `arb-step-unittest-b1a805a8b6b04d44abecba040eec88e0` |
| Lint | `arb:ruff` (see below) | clean, 0 findings — receipt `arb-ruff-ab86ee6b0199483b8eb85f82e0394ec0` |
| Typecheck | `arb:typecheck` (see below) | `All checks passed!` — receipt `arb-step-typecheck-1c706bdc42bf4db4bc86c02edaa1cbaf` |
| Docs build | `arb:mkdocs` (see below) | `Documentation built in 3.92 seconds` — receipt `arb-step-mkdocs-acab19b488a343b48c4b934fa2451663` |
| BDD (scoped) | `arb:behave-scoped` (see below) | 3 scenarios, 20 steps, 0 failed — receipt `arb-step-behave-eaae5376ad8548c989eff61c9aed166e` |

```bash
# arb:unittest — full unittest sweep
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer

# arb:ruff — lint
uv run gz arb ruff

# arb:typecheck — static type check
uv run gz arb typecheck

# arb:mkdocs — docs build
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# arb:behave-scoped — Gate 4 scenarios for this OBPI
uv run gz arb step --name behave -- uv run -m behave features/rendition_lineage.feature
```

The digest was re-confirmed unchanged immediately after this gate run:

```
$ uv run gz obpi acceptance OBPI-0.35.0-06-validate-rendition-lineage status --stage stage4 --json
```
`input_digest: 90807b7ef6ec9ae9f6df25e05c08bcc723d984ed0f40d4d5feb7f21de3507931` · `ready: True` · `open_findings: []` · `blockers: []` — the gates above and this acceptance record describe the same tree.

**REQ coverage cross-check:** `gz covers` reports `total_reqs 8`, `behavior_uncovered_reqs 0`. REQ-07 (SUPPORT) and REQ-08 (STRUCTURAL-FENCE) correctly carry no `@covers` — proof-channel exemption, not a gap.

```
$ uv run gz covers OBPI-0.35.0-06-validate-rendition-lineage --json
```
`"summary": {"identifier": "OBPI-0.35.0-06-validate-rendition-lineage", "total_reqs": 8, "covered_reqs": 6, "uncovered_reqs": 2, "coverage_percent": 75.0, "behavior_uncovered_reqs": 0, "grandfathered_reqs": 0}`

**Acceptance proof:** 8/8 proofs `valid: true`, all bound to digest `90807b7e...`. **11 recorded mutation controls; 11 assertion-class kills.** All 11 were independently **replayed by the tier-1 cross-vendor adversary at the current digest** (enumerated by replay records bound to `90807b7e`):
- 8 controls replayed in `arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32`
- 2 controls replayed in `arb-step-codexadversary-61d07ad4157a45ff9cd20a672ac42a8e`
- `strip-recovery-from-the-missing-citation-finding` replayed in **both** `arb-step-codexadversary-61d07ad4...` and `arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b`

**Review set on the current digest (all five bound to `90807b7e`):**

| Stage | Tier | Verdict | Receipt |
|---|---|---|---|
| spec | 2 | accepted | `arb-step-specreview-42ad26da08b74a2bb78758680e976caf` |
| quality | 2 | accepted | `arb-step-qualityreview-b9fd1be9156b4e61b21c171c548cf499` |
| adversarial | 1 | accepted | `arb-step-codexadversary-61d07ad4157a45ff9cd20a672ac42a8e` |
| adversarial | 1 | **refuted** | `arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32` (record-correction round; raised the historical finding) |
| adversarial | 1 | accepted | `arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b` (closing round) |

20 acceptance reviews exist across this OBPI's whole history; the five above are the ones bound to the current digest.

**Files created:**
- `src/gzkit/governance/trust_audits/rendition_lineage.py` — the new `--rendition-lineage` scope: owned-section derivation, coverage computation, MX-checkpoint severity resolution (535 lines)
- `tests/governance/test_rendition_lineage.py` — 16 covering tests, one per REQ-derived behavior (636 lines)
- `features/rendition_lineage.feature` — Gate 4 BDD scenarios (3 scenarios, 20 steps)
- `features/steps/rendition_lineage_steps.py` — step definitions for the feature above

**Files modified:**
- `src/gzkit/governance/trust_audits/__init__.py` — scope registration
- `src/gzkit/cli/parser_maintenance.py` — `--rendition-lineage` argparse option and handler forwarding
- `src/gzkit/commands/validate_cmd.py` — handler/default-scope wiring
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — live-scope negative control (fixture builder + roster entry)
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — `_ep_rendition_lineage` runner
- `src/gzkit/governance/trust_audits/_qc_claim_exemptions.py` — newly authored enforcement claim's exemption-surface declaration
- `src/gzkit/quality.py`, `src/gzkit/commands/quality.py` — `gz check` step runner + `_STEP_GUARD_META` MX-severity entry (GHI #785 automatic-caller requirement)
- `src/gzkit/qc_binding.py` — `_STEP_CLASSIFICATION` entry
- `data/check_scope_membership.json` — `rendition_lineage` declared `in_check`
- `data/check_step_concurrency.json` — concurrency declaration (`read_only`, measured)
- `tests/cli/test_validate_registry_parity.py` — explicit-tier parity frozenset entry
- `docs/user/manpages/validate.md`, `docs/governance/governance_runbook.md` — the new scope documented
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-06-validate-rendition-lineage.md` — this brief's Evidence/Change Log sections and the REQ-07 amendment

**REQ coverage:**

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|-----|------|-----------|----------------|-------|--------|
| REQ-0.35.0-06-01 | BEHAVIOR | Owned-section match passes; omitted-citation liveness gap closed | `req-01:tests` (below) | 2 tests | Pass |
| REQ-0.35.0-06-02 | BEHAVIOR | Pure verifier now compares owned TEXT to its materialization | `req-02:tests` (below) | 2 tests | Pass |
| REQ-0.35.0-06-03 | BEHAVIOR | Unowned/ungraded bytes reported as debt, never fail | `req-03:tests` (below) | 4 tests | Pass |
| REQ-0.35.0-06-04 | BEHAVIOR | Coverage computed at run time from ownership + corpus; merge sums both operands | `req-04:tests` (below) | 4 tests | Pass |
| REQ-0.35.0-06-05 | BEHAVIOR | Effective corpus (not raw log) read; retired-but-committed text is drift | `req-05:tests` (below) | 1 test | Pass |
| REQ-0.35.0-06-06 | BEHAVIOR | Three-part recovery prose on stderr; never suggests un-owning | `req-06:tests` (below) | 3 tests | Pass |
| REQ-0.35.0-06-07 | SUPPORT | Scope registered + documented in both manpage/runbook | `req-07:support` (below) | arm-2 file-existence + `--cli-alignment` | Pass |
| REQ-0.35.0-06-08 | STRUCTURAL-FENCE | Fail-closed reach is owned-sections-only, decomposition-wide | Parent ADR `## Boundary Invariants` BI-05 | Audited at ADR closeout | Pass |

```text
# req-01:tests — REQ-0.35.0-06-01 (BEHAVIOR)
tests.governance.test_rendition_lineage.OwnedSectionMatchingCorpusPassesTest.test_owned_section_matching_its_materialization_yields_no_findings
tests.governance.test_rendition_lineage.OwnedSectionEntryIdCompletenessTest.test_owned_section_citing_no_entry_ids_fails_closed

# req-02:tests — REQ-0.35.0-06-02 (BEHAVIOR)
tests.governance.test_rendition_lineage.OwnedSectionDriftFailsClosedTest.test_owned_section_not_derivable_from_corpus_names_the_section
tests.governance.test_rendition_lineage.PureVerifierRejectsOwnedDriftTest.test_pure_verifier_rejects_an_owned_body_replaced_wholesale

# req-03:tests — REQ-0.35.0-06-03 (BEHAVIOR)
tests.governance.test_rendition_lineage.UnownedSectionNeverFailsTheGateTest.test_arbitrary_prose_in_an_unowned_section_yields_no_findings
tests.governance.test_rendition_lineage.UnownedSectionNeverFailsTheGateTest.test_fully_unowned_surface_without_a_lineage_yields_no_findings
tests.governance.test_rendition_lineage.UnownedSectionNeverFailsTheGateTest.test_unowned_section_citing_a_dead_entry_id_yields_no_findings
tests.governance.test_rendition_lineage.MissingCommittedLineageIsDisclosedTest.test_declared_ownership_without_a_lineage_is_ungraded_not_failed

# req-04:tests — REQ-0.35.0-06-04 (BEHAVIOR)
tests.governance.test_rendition_lineage.CoverageIsComputedAtRunTimeTest.test_flipping_a_section_to_owned_changes_the_computed_coverage
tests.governance.test_rendition_lineage.CoverageIsComputedAtRunTimeTest.test_coverage_counts_utf8_bytes_not_characters
tests.governance.test_rendition_lineage.CoverageIsComputedAtRunTimeTest.test_scope_surfaces_the_computed_figure_on_the_clean_path
tests.governance.test_rendition_lineage.CoverageIsComputedAtRunTimeTest.test_merge_accumulates_all_six_fields_across_two_non_zero_renditions

# req-05:tests — REQ-0.35.0-06-05 (BEHAVIOR)
tests.governance.test_rendition_lineage.RetiredEntryLeftInAnOwnedSectionIsDriftTest.test_retired_invariant_text_still_committed_fails_closed

# req-06:tests — REQ-0.35.0-06-06 (BEHAVIOR)
tests.governance.test_rendition_lineage.RecoveryProseCarriesThreePartsTest.test_drift_message_names_section_cites_the_adr_and_prescribes_the_round_trip
tests.governance.test_rendition_lineage.RecoveryProseReachesStderrTest.test_fail_closed_path_writes_the_three_parts_to_stderr
tests.governance.test_rendition_lineage.UncitedEntryFindingCarriesRecoveryTest.test_missing_citation_finding_carries_the_three_parts

# req-07:support — REQ-0.35.0-06-07 (SUPPORT)
src/gzkit/req_kind_support.py:255-258 (_support_path_arm_ok, arm 2 — cited artifact exists on disk, GHI #647)
uv run gz validate --cli-alignment   # resolves every gz-verb reference the new docs prescribe
```

**4. All eight findings and their dispositions** (account for every one)

1. **`req-03-unowned-content-mutation-gap`** (REQ-03) — raised by spec (tier 2). Operator-ruled an **accepted DISCLOSED residual**: its cross-module half is structurally unwitnessable from inside this OBPI (`composer.py` is a Denied Path, landed OBPI-0.35.0-05). **Disclosed, not proven.** Closed at the current proof by spec + quality + tier-1 adversarial.
2. **`rendition-lineage-merge-untested-multi-operand`** (REQ-04) — raised by quality (tier 2). Repaired with a twelve-distinct-value multi-operand merge test. Closed by spec + quality + tier-1 adversarial.
3. **`req-01-missing-owned-entry-ids-pass`** (REQ-01) — raised by the tier-1 adversary. Liveness was vacuous over omitted entry ids. Repaired via `_uncited_materialized_entries`. Closed by spec + quality + tier-1 adversarial.
4. **`req-02-pure-verifier-accepts-owned-drift`** (REQ-02) — raised by the tier-1 adversary. The pure verifier never compared owned-section TEXT to its materialization. Repaired by moving the derivation comparison into the pure core (`_owned_drift` removed). Closed by spec + quality + tier-1 adversarial.
5. **`req-06-recovery-emitted-to-stdout`** (REQ-06) — raised by the tier-1 adversary. Recovery prose went to stdout though the REQ names stderr. Repaired. Closed by spec + quality + tier-1 adversarial.
6. **`req-07-declared-artifact-edit-witness-missing`** (REQ-07) — raised by the tier-1 adversary and independently re-raised by a spec reviewer. The REQ text demanded an `artifact_edited` ledger row the emitter structurally cannot produce for this path. The implementing agent contested first and was overruled by independent review; the operator ruled the REQ TEXT the defect and directed an amendment naming the witness the channel actually produces (arm 2 of `_support_path_arm_ok`, GHI #647). Closed by spec + quality + tier-1 adversarial — the final adversary judged the amendment "honestly describes its proof channel."
7. **`req-02-json-cli-owned-drift-exits-zero`** — **null obligation (auxiliary)**. Raised by the tier-1 adversary, independently confirmed by both Stage-2 channels. `gz validate --json` exits 0 on a failing scope while its payload says `valid: false`. **Pre-existing and repo-wide** (branch dates to `b27f42c92`, 2026-05-02), so operator-ruled OUT of this OBPI and filed as **GHI #995**. Auxiliary observation, no closure required — correct treatment.
8. **`req-06-missing-citation-recovery-incomplete`** (REQ-06) — raised by the tier-1 adversary; **this OBPI's own regression** (finding #3's repair emitted a bare diagnostic on its exit-3 path, and REQ-06 scopes to "the exit-3 path" as a whole). Repaired via `_missing_citation_message`. Raised by `arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32`, closed by `arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b`.

**5. Caveats — each was open at the previous packet; each is now CLOSED**

- **"Reviewer did not rerun the suite/lint/typecheck/docs/BDD."** CLOSED: all five gates re-run against the current digest, ARB-receipted at `exit_status 0` (table above), digest reconfirmed unchanged afterward.
- **"Replayed 3 of 11 substitutions."** CLOSED BY EXECUTION: 11 of 11 controls are now independently replayed at the current digest (enumeration above), replacing the orchestrator's own unreplayed claim with the adversary's execution.
- **"A real finding is absent from the ledger's structured history."** CLOSED: it is finding #8 above — raised into Layer-2 and independently closed against the current proof by two separate tier-1 rounds.

**6. Raise → repair → closure sequence** (real history, not smoothed)

The tier-1 cross-vendor adversary **refuted this OBPI three times** before corroborating. Two Claude reviewers had passed the pre-repair state 8/8 twice; the cross-vendor tier caught what they missed:

1. Tier-1 round 1 (`arb-step-codexadversary-8eaeb01d5ff44b29bcd08416ec80f67b`) — **REFUTED**, 4 findings (#3, #4, #5, #6 above).
2. Repairs landed + operator-ruled REQ-07 amendment; Stage-2 re-reviews re-run.
3. Tier-1 round 2 (`arb-step-codexadversary-4329ae96fc6f45799e069e8d255f2567`) — **REFUTED**, confirmed all four prior dispositions and raised 2 new (#7, #8). **This review's record was refused at import** (it closed findings on obligations whose proofs it had not accepted), so it carries no acceptance-ledger entry; its ARB receipt is durable and both findings were recorded by other means. Disclosed here as history.
4. The design-escalation rule fired: rounds 1 and 2 named the same root at different surfaces, and finding #8 had been introduced by this OBPI's own prior repair. Dispatching stopped; the design question went to the operator, who ruled the scope boundary (repair #8, route #7 to GHI #995).
5. Tier-1 round 3 (`arb-step-codexadversary-61d07ad4157a45ff9cd20a672ac42a8e`) — **corroborated-with-caveats / not-refuted**.
6. Tier-1 round 4 (`arb-step-codexadversary-81439f474a3d4f39b375ed6e22eeef32`) — **REFUTED** by design: the record-correction round that replayed the 8 outstanding controls and raised finding #8 into the ledger.
7. Tier-1 round 5 (`arb-step-codexadversary-07dfb35f0aaf4af482c86feb724c750b`) — **corroborated / not-refuted**, closing finding #8 after verifying the repair by execution.

**7. Known limitations and tracked defects**

- `req-03-unowned-content-mutation-gap` is a **disclosed residual**, not a proven claim.
- Three GHIs filed this session, none blocking this OBPI: **#993** (`gz obpi acceptance human-review` has no obligation scope and hardcodes `stage="adversarial"`), **#994** (a non-executing reviewer recorded a confirmation it could not have made — a false "independently located" claim in an early spec review of this OBPI), **#995** (the JSON exit bypass, finding #7).
- Three acceptance reviews were refused at import this session on closure-scope rules; each was a legitimate reviewer judgment the record format could not express.
- `gz arb red` returns `failure_class=error` on a reconstructed base for all six BEHAVIOR REQs — **inconclusive per the skill's own provenance table, not an assertion RED, and not offered as falsifiability evidence.** The 11 replayed mutation kills are the falsifiability evidence.
- The REQ-06 stderr repair means the recovery message now appears on both stderr (satisfying the REQ) and stdout (via the shared CLI renderer) — an operator sees it twice. Non-blocking; a consequence of fixing the channel inside the gate rather than in the shared renderer (GHI #995's surface).

**8. Awaiting attestation.** Do NOT proceed to Stage 5 until human responds.
