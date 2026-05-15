# AUDIT — ADR-0.0.32 (canonical-surface-packaging)

**Date:** 2026-05-15 (resumed; prior pass 2026-05-13)
**Auditor:** main-session agent (subagent invocation, Opus 4.7)
**Operator of record:** Jeffry Babb
**Lane / Kind / Sensitivity:** heavy / foundation / (none)
**Audit verdict:** PASS — `gz adr audit-check ADR-0.0.32` exits 0 after the GHI #466 detector extension landed at commit `a4cca07d`. All 15 OBPIs PASS at ledger level; 130/138 REQs covered (94.2%); 8 advisory REQs remain non-blocking per CLI labeling. S1+S2 RESOLVED by OBPI-15 (`gz validate --distribution` exits 0); S5 RESOLVED by GHI #466. Pending: operator verbal `accept audit` to authorize the validated receipt emission and advance lifecycle Completed → Validated.

## Layer-2 ledger verdict (2026-05-15 post-fix re-run)

```
$ uv run gz adr audit-check ADR-0.0.32
ADR audit-check: ADR-0.0.32-canonical-surface-packaging
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.0.32-01 .. OBPI-0.0.32-15 (all 15 attested_completed)
Advisory 8 REQ(s) without @covers traceability (non-blocking):
  - REQ-0.0.32-01-07, 02-03, 03-04, 03-05, 09-03, 09-04, 11-06, 11-08
Coverage: 130/138 REQs covered (94.2%)
exit=0
```

(Full transcript: `proofs/audit-check-2026-05-15.txt`.)

The PASS line: every linked OBPI (including OBPI-15) has a recorded Gate-5 attestation receipt in the ledger. The 8 advisory REQs from OBPIs 01/02/03/09/11 remain non-blocking per CLI labeling.

The prior FAIL block (32 covers-backfill findings across `tests/test_rules.py`, `tests/test_personas.py`, `tests/test_skills.py`, `tests/test_templates.py`, `tests/test_chores.py`, `tests/governance/test_distribution_audit.py` — all `REQ-0.0.32-15-*`) cleared after GHI #466 (commit `a4cca07d`) extended `_is_legitimate_authoring` with two new exemption shapes — see § Shortfall S5 (RESOLVED) for the detector-extension narrative.

## Feature Demonstration (Step 3 — MANDATORY)

The ADR delivered five operator-visible capabilities. Each is exercised below with the live `gz` CLI command and representative output captured under `proofs/`.

### Capability 1 — Module-to-package API preservation

**Claim (C7):** `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` and `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserve all public-symbol re-exports.

```
$ uv run python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills; \
                    from gzkit.rules import CORE_RULES, scaffold_core_rules; \
                    print('skills:', len(CORE_SKILLS), 'rules:', len(CORE_RULES))"
skills: 11 rules: 19
```

(Proof: `proofs/module-package-imports.txt`.)

**Value:** Existing call sites (`from gzkit.skills import X`, `from gzkit.rules import X`) continue resolving after the module-to-package conversion. The dual-surface refactor did not break the public Python API.

### Capability 2 — `gz init --update` three-state refresh

**Claim (C3):** `gz init --update` provides version-aware refresh with IDENTICAL/STALE/EDITED three-state detection.

```
$ uv run gz init --update --dry-run
Refreshing canonical surfaces from installed wheel...
Dry run: no files will be written.
  IDENTICAL: 218 STALE: 3 EDITED: 0
```

(Proof: `proofs/init-update-dry-run.txt`.)

**Value:** Adopters can refresh canonical surfaces from a newer gzkit wheel without losing local edits. The three-state report makes the diff visible before any write; `--dry-run` gates mutation.

### Capability 3 — `gz upgrade` adopter-side surface-only refresh

**Claim (C4):** `gz upgrade` is the adopter-side surface-only refresh subcommand, distinct from `gz init --update`.

```
$ uv run gz upgrade --help
usage: gz upgrade [-h] [--surface SURFACES] [--force] [--dry-run] ...

Surface-only refresh of .gzkit/<surface>/ from the installed wheel's package data.
```

(Proof: `proofs/upgrade-help.txt`.)

**Value:** Adopters who only want to pull, say, the latest skill catalogue without re-running the whole `gz init --update` ceremony can scope the refresh with `--surface skills`.

### Capability 4 — Unified `gz agent sync control-surfaces`

**Claim (C2):** A single `gz agent sync control-surfaces` invocation propagates `.gzkit/<surface>/` to BOTH `src/gzkit/<surface>/` AND `.[vendor]/<surface>/`.

(Proof: `proofs/agent-sync.txt`.)

**Value:** Before this ADR, the `.gzkit/ → src/gzkit/` arrow was manual and the `.gzkit/ → .[vendor]/` arrow ran separately. Now one invocation closes both arrows from the canonical source-of-truth.

### Capability 5 — T0 distribution-invariant fail-closed enforcement (post-OBPI-15)

**Claim (C5):** `gz validate --distribution` enforces wheel-shipping discipline fail-closed (exit 3 on any drift). **After OBPI-15** the validator now consults per-surface classifiers and the baseline regenerator keeps the manifest current.

```
$ uv run gz validate --distribution
Validated: distribution

✓ All validations passed (1 scopes).
exit=0
```

(Proof: `proofs/validate-distribution-2026-05-15.txt`; supersedes the 2026-05-13 `validate-distribution.txt` which captured the pre-OBPI-15 exit-3 state with 21 errors.)

**Value (resolution of prior-pass shortfalls):** Both S1 (stale baseline manifest) and S2 (package-only files in canonical surface roots) from the 2026-05-13 audit are now closed. OBPI-15 shipped the `--regenerate` flag (S1) and the per-surface class-classifier (S2); current `main` HEAD exits 0.

## Execution log

| Check | Result | Notes |
|---|---|---|
| `gz adr audit-check ADR-0.0.32` | ✓ PASS (exit 0) | All 15 OBPIs PASS; 130/138 REQs covered (94.2%); 8 advisory REQs non-blocking. Post-fix transcript at `proofs/audit-check-2026-05-15.txt`. |
| `gz validate --distribution` | ✓ PASS (exit 0) | T0 enforcement surface now passes on current `main`. S1+S2 from 2026-05-13 RESOLVED. |
| `gz adr report ADR-0.0.32` | ✓ PASS | Lifecycle = `Completed`, Closeout Phase = `attested`, OBPI 15/15, Closeout READY, QC READY. |
| `gz init --update --dry-run` | ✓ PASS | Three-state report works; 218 IDENTICAL / 3 STALE / 0 EDITED. |
| `gz upgrade --help` | ✓ PASS | Manpage surface present with `--surface`, `--force`, `--dry-run`. |
| `gz agent sync control-surfaces` | ✓ PASS | Single invocation propagates to all derived surfaces; idempotent. |
| `uv run -m unittest` | ✓ PASS (carried from 2026-05-13) | 4994/4994 pass per fc83df7 commit body. |
| Module-to-package imports | ✓ PASS | `from gzkit.skills import …` and `from gzkit.rules import …` both resolve. |
| T0 smoke test exists | ✓ PASS | `features/distribution_invariant.feature` present. |

## Evidence index

| Artifact | Path |
|---|---|
| Audit plan | `audit/AUDIT_PLAN.md` |
| Audit-check transcript (2026-05-15, current) | `audit/proofs/audit-check-2026-05-15.txt` |
| Distribution validation transcript (2026-05-15, exit 0) | `audit/proofs/validate-distribution-2026-05-15.txt` |
| ADR report transcript (2026-05-15) | `audit/proofs/adr-report-2026-05-15.txt` |
| Distribution validation transcript (2026-05-13, exit 3 — historical) | `audit/proofs/validate-distribution.txt` |
| Init-update dry-run transcript | `audit/proofs/init-update-dry-run.txt` |
| Upgrade help surface | `audit/proofs/upgrade-help.txt` |
| Agent sync transcript | `audit/proofs/agent-sync.txt` |
| Module-package imports proof | `audit/proofs/module-package-imports.txt` |
| ADR prose | `ADR-0.0.32-canonical-surface-packaging.md` |
| OBPI briefs | `obpis/OBPI-0.0.32-01..15-*.md` |
| Ledger | `.gzkit/ledger.jsonl` |

## Shortfalls identified

### S1 — Distribution baseline manifest staleness — RESOLVED 2026-05-14 by OBPI-15

OBPI-15 shipped `regenerate_distribution_baseline()` and the `--regenerate` flag on `gz validate --distribution` (commit fc83df7). The baseline manifest was regenerated; `gz validate --distribution` now exits 0 against `main` head. The 2026-05-13 audit's recommended fix landed as designed.

### S2 — Package-only files inside canonical surface roots — RESOLVED 2026-05-14 by OBPI-15

OBPI-15 added `_classify_rule_file`, `_classify_skill_file`, `_classify_persona_file`, `_classify_template_file` helpers in each surface's `__init__.py`, signature-compatible with `_classify_chore_file`. The distribution validator's `_collect_errors` now consults the classifiers and exempts `package_only` files (e.g. `_scaffolder.py`, `__init__.py`) from `ON_DISK_NOT_INCLUDED`. The doctrine extension landed at `.gzkit/rules/skill-surface-sync.md` v0.6.0 § Canonical surface class-classifier (one unified section covering chores + rules + skills + personas + templates).

### S3 — Advisory REQ-coverage gaps — UNCHANGED (NON-BLOCKING, documented)

`audit-check` continues to flag 8 REQs without `@covers` traceability across OBPI-01/02/03/09/11:
`REQ-0.0.32-01-07`, `REQ-0.0.32-02-03`, `REQ-0.0.32-03-04`, `REQ-0.0.32-03-05`, `REQ-0.0.32-09-03`, `REQ-0.0.32-09-04`, `REQ-0.0.32-11-06`, `REQ-0.0.32-11-08`.

- **Severity:** Non-blocking (CLI explicitly labels advisory).
- **Routing per skill § Step 2 diagnosis rule:** No cosmetic `@covers` backfill applied. Each REQ should be re-derived from its OBPI brief and either backed by a semantically-grounded test (case a) or removed if the assertion drifted from REQ semantics (case b). Diagnosis deferred to a follow-on under each REQ's parent.

### S4 — Doc-drift fixed in flight on 2026-05-13 — UNCHANGED

ADR frontmatter previously updated `Draft` → `Completed`; OBPI-15 expansion reverted to `Draft` then back to `Completed`. 15 of 15 OBPI checklist items are now `[x]` in the canonical ADR prose. No additional drift surfaced this pass.

### S5 — Covers-backfill detector false-positive on REQ-0.0.32-15-* decorators — RESOLVED 2026-05-15 by GHI #466 (commit a4cca07d)

**Resolution.** GHI #466 landed at commit `a4cca07d` ("fix(adr-audit): exempt same-commit block-creation + regression-overlay marker (GHI #466)"). The detector extension adds two new legitimate-authoring exemption shapes to `_is_legitimate_authoring` in `src/gzkit/commands/adr_audit_covers_backfill.py`:

1. **Same-commit BLOCK creation (Component B).** When a `@covers(REQ-X)` decorator's introducing SHA matches the introducing SHA of the function `def` line it decorates (via `git blame` on the decorated block, not the whole file), the decorator is exempted. This catches the OBPI-15 pattern where new test classes (`TestClassifyPersonaFile`, `TestRegenerateDistributionBaseline`, etc.) were authored in the same implementation commit as their decorators, even though the host test files pre-existed.
2. **Inline regression-invariant overlay marker (Component A).** When the line carrying the decorator also carries `# audit-exempt: regression-invariant-overlay <reason>`, the decorator is exempted (reason text mechanically required so the marker cannot be a one-token escape hatch). This handles the REQ-15-10 "no regression" piggyback shape — adding `@covers("REQ-0.0.32-15-10")` to pre-existing byte-parity tests where the assertion structurally IS the regression-invariant being claimed.

Both exemptions preserve the GHI #272/#309 guard: if the receipt is anchored to the same commit as the decorator AND the file/block was created in the same commit, the suppression triple still fires. The marker exemption is NOT suppressed by the receipt-coupled flag — it is the operator's explicit attestation that the overlay is legitimate.

`.claude/rules/adr-audit.md` § "Legitimate-authoring exemptions" now documents all five exemption shapes (same-commit FILE creation, same-commit BLOCK creation, inline marker, `Ceremony:` trailer, subject-suffix marker) with source GHIs, source-side annotations, and receipt-coupled-flag suppression semantics.

**Post-fix verification.** `uv run gz adr audit-check ADR-0.0.32` exits 0; the prior 32 covers-backfill findings cleared (proof: `proofs/audit-check-2026-05-15.txt`). The 8 advisory non-blocking REQs remain.

**Historical diagnosis (retained for audit trail).** All 32 prior findings were `@covers(REQ-0.0.32-15-*)` decorators introduced at commit fc83df7, 2 commits / 1 day before the OBPI-15 receipt at `obpi_receipt_emitted:OBPI-0.0.32-15-t0-maintenance-surfaces:2026-05-14T11:03:25Z`. Spread: `tests/test_rules.py` (12), `tests/test_personas.py` (5), `tests/test_skills.py` (5), `tests/test_templates.py` (5), `tests/governance/test_distribution_audit.py` (6), `tests/test_chores.py` (1).

**Diagnosis (per skill § Step 2 / `.gzkit/rules/adr-audit.md` / `.gzkit/rules/tests.md` § Invariant 6f).** Two cases must be distinguished before remediation:

- **Case (a) Genuinely missing coverage** — REJECTED. Inspection of the flagged tests shows each decorated test asserts semantics derived from the REQ it covers, not from a run of the code.
- **Case (b) Coverage-shape drift / cosmetic backfill** — REJECTED. The decorators are NOT cosmetic.

Two structurally distinct sub-shapes are present, both legitimate authoring:

1. **REQ-15-10 "no regression" piggyback on pre-existing byte-parity tests.** REQ-0.0.32-15-10 reads: *"no test that passed for OBPIs 01–14 newly fails (no regression of byte-parity, `gz init --update` three-state, `gz upgrade` filter, or T0 smoke-test invariants)."* This is a meta-REQ — its semantics ARE "the pre-existing tests still pass." Adding `@covers("REQ-0.0.32-15-10")` to pre-existing tests like `tests/test_personas.py:63 test_dual_surface_byte_parity` (which already covered `REQ-0.0.32-09-01`/`-02`) is the canonical authoring shape for a no-regression REQ. Re-deriving the assertion is structurally impossible (the assertion IS the byte-parity check; that's what "no regression" means). Removing the decorator silences the meta-REQ. The decorator is correct.

2. **REQ-15-04/-05/-06/-07/-08/-09 newly-authored test classes.** REQ-0.0.32-15-04 (classifier exists), -05 (`_scaffolder.py` classifies `package_only`), -06 (validator exempts `package_only`), etc. are covered by *new* test classes added at fc83df7: `TestClassifyPersonaFile` (test_personas.py:255+), `TestClassifyRuleFile` (test_rules.py:944+), `TestRegenerateDistributionBaseline` (test_distribution_audit.py:421+), `TestPackageOnlyExemption` (test_distribution_audit.py:508+). Each test asserts the REQ's named semantics (classifier callable, exit-0 after regenerate, `package_only` not flagged). These are the GHI #382/#386 legitimate-authoring shape: tests + implementation landed in the same commit; receipt deferred to the next pipeline ceremony.

**Why the legitimacy guard didn't fire.** `_is_legitimate_authoring` at `src/gzkit/commands/adr_audit_covers_backfill.py:505` exempts only two shapes:
1. Same-commit file creation (file went 0→N lines in the introducing commit), AND
2. Ceremony-bundled commits (commit subject/trailer carries `Ceremony: gz-git-sync` etc.).

fc83df7 is a `feat(obpi-0.0.32-15)` commit (implementation), not a ceremony commit, and the test files pre-existed (test_personas.py was created at 0cded87d, test_rules.py at 74ddf067, test_distribution_audit.py at f1fbe923 — all months before fc83df7). The decorator-added-to-existing-test-in-implementation-commit pattern is genuinely a gap in the guard.

**Severity.** Blocking on the audit ceremony only (skill § Step 8 "audit fails → no receipt"). Not semantic drift. The ADR's claimed capabilities all work; the validator passes; the lifecycle is `Completed` and READY; the only obstruction is the detector heuristic firing on what is in fact legitimate same-commit authoring.

**Remediation filed:** [GHI #466](https://github.com/tvproductions/gzkit/issues/466) — *"covers-backfill detector: same-commit block-creation flagged as backfill (blocks ADR-0.0.32 audit)"*. Sibling-cut clean against the closed #272/#309/#382/#385/#386/#388/#390 family. Reproducer: any of the 32 findings on ADR-0.0.32 (cleanest is REQ-0.0.32-15-10 piggyback at `tests/test_personas.py:63`). The fix shape is a third exemption in `_is_legitimate_authoring`: recognize same-commit block-creation (decorator + method/class body authored in same SHA, regardless of file-creation SHA), keyed off `git blame -L <decorator-line-range>` rather than `_file_creation_short_sha`. Tests must assert the new exemption catches the OBPI-15 reproducer without admitting GHI #272 cosmetic-backfill examples.

**Routing per AGENTS.md § Defect-fix routing.** Exceeds direct-fix thresholds (touches detector logic in `adr_audit_covers_backfill.py`, requires new exemption + tests, may require receipt-anchoring logic). OBPI ceremony required.

**Do NOT remediate by:** (i) removing the decorators (would silence the meta-REQ + remove legitimate per-REQ coverage); (ii) re-deriving the assertions (the assertions are already REQ-derived); (iii) backdating the receipt; (iv) declaring audit VALIDATED in spite of the FAIL.

## Attestation status

**Operator verbal attestation received: `accept audit` (Jeffry Babb, 2026-05-15).** All shortfalls resolved (S1/S2 by OBPI-15; S5 by GHI #466 / commit `a4cca07d`); S3/S4 unchanged (S3 non-blocking advisory; S4 already remediated in flight). Per skill § Step 8, the operator's verbal ack IS the Gate-5 attestation for the audit ceremony.

**Validated-receipt emission COMPLETE.** Ceremony executed in order: `gz adr audit-begin ADR-0.0.32` (marker written) → `gz adr emit-receipt ADR-0.0.32 --event validated --attestor "Jeffry Babb" --evidence-json <prepared payload>` (event `audit_receipt_emitted` written to `.gzkit/ledger.jsonl` at `ts=2026-05-15T08:26:38.682435+00:00`) → `gz adr audit-end ADR-0.0.32` (marker removed) → `gz adr report ADR-0.0.32` confirms `Lifecycle = Validated`, `Closeout = READY`, `QC = READY`, `OBPI = 15/15`.

**Attestation text seated (operator verbatim + enrichment):** `accept audit — ADR-0.0.32 canonical-surface-packaging validated: 15/15 OBPIs PASS at ledger level; gz adr audit-check exits 0 (proofs/audit-check-2026-05-15.txt); 130/138 REQs covered (94.2%); 8 advisory REQs non-blocking; S1+S2 resolved by OBPI-0.0.32-15 (fc83df7); S5 resolved by GHI #466 (a4cca07d); gz validate --distribution exits 0 (proofs/validate-distribution-2026-05-15.txt); receipts arb-ruff-3f9161d254d74dcd9887b3a732359723, arb-step-typecheck-8de160cbb5ce453384706b583f76de8b, arb-step-unittest-ac4376a39a98424cb53f64d459d344bb (5005 tests OK); five capabilities demonstrated under § Feature Demonstration.`

**Agent signature:** `main-session agent (Opus 4.7) — audit complete, lifecycle Completed → Validated confirmed via gz adr report`. Attestor of record: `Jeffry Babb` (operator name only per repo PII rule).

**Operator ratification scope (what the verbal ack attests to):**

1. All 15 OBPIs PASS at ledger level; `audit-check` exits 0.
2. 130/138 REQs covered (94.2%); 8 advisory REQs documented as non-blocking under S3.
3. S1 + S2 resolved by OBPI-15 (`gz validate --distribution` exits 0).
4. S5 resolved by GHI #466 (commit `a4cca07d`) — two new exemption shapes added; full detector-extension narrative under § Shortfall S5.
5. Feature demonstration captured (five capabilities exercised under § Feature Demonstration; proofs under `audit/proofs/`).
6. Lifecycle is ready to move `Completed` → `Validated` on receipt emission.

## Prior-pass artifacts (2026-05-13)

The 2026-05-13 pass blocked on S1+S2. Both are now RESOLVED by OBPI-15 as documented above. The historical `validate-distribution.txt` (21 errors) is retained under `proofs/` as evidence of the prior block; supersession by the new `validate-distribution-2026-05-15.txt` (exit 0) is the audit trail.
