# ADR-0.0.74-mx-mode-maintenance-hangar — Audit

**Date:** 2026-06-27
**Driver persona:** pipeline-orchestrator
**Phase:** COMPLETED → VALIDATED (audit)
**Verdict:** ⚠️ **CONCERNS — NOT VALIDATED.** Three MAJOR coherence findings require disposition before the `validated` receipt may be emitted.

---

## 1. Mechanical checks (Layer 1/2)

| Check | Command | Result | Proof |
|-------|---------|--------|-------|
| Ledger completeness | `gz adr audit-check ADR-0.0.74-mx-mode-maintenance-hangar` | ✅ PASS — all 19 linked OBPIs completed with evidence; 21 REQs without `@covers` are **advisory/non-blocking** (SUPPORT + STRUCTURAL-FENCE) | `proofs/audit-check.txt` |
| Governance CLI | `gz cli audit` | ✅ PASS — 112/112 commands fully covered | `proofs/cli-audit.txt` |
| OBPI-10 (cut) | ledger + frontmatter | ✅ Properly withdrawn (`obpi_withdrawn` event, `status: withdrawn`, reason cites Magna Carta cut) — not a shortfall | — |

## 2. Fidelity Gate (Step 3 — bound, mandatory)

`gz adr fidelity ADR-0.0.74-mx-mode-maintenance-hangar` → **10 pass, 0 fail** (proof: `proofs/fidelity.txt`). The ADR's 10 `## Fidelity Assertions` rows each ran their real test against the running system and matched expected exit 0. The ADR's thesis holds at the test layer.

## 3. Independent review dispatch (anti-optimistic-bias)

Per the skill, two independent subagents re-verified rather than the driver scoring itself:

- **spec-reviewer** (REQ-coverage): BEHAVIOR coverage honestly holds — all 51 BEHAVIOR REQs carry `@covers`, no orphan `@covers`, no mislabeled kinds, no tautologies in the deep-read scope. 4/5 meta-property fences honestly deferred. **One MAJOR:** 17-05/BI#9 enumeration facade (see Findings).
- **quality-reviewer** (structural coherence): hangar pieces compose cleanly; enforcement floor genuinely binds into `gz check` and fails closed; §3 meta-property-fence deferral is architecturally sound and does **not** reopen the §5 facade; single-claim fences keep their teeth. **Two MAJOR + minors** (see Findings).

## 4. Findings

### MAJOR

| ID | Finding | Evidence | Tracked | Disposition |
|----|---------|----------|---------|-------------|
| F1 | **Marker-path drift (BI#1 violation, agent surface).** Code marker is `.gzkit/mx.json` (`src/gzkit/mx/marker.py:29,76`, `awareness.py:19`); agent-facing surfaces tell agents to read `.gzkit/mx-active` (`.gzkit/rules/mx-mode.md:23,25`, `.gzkit/skills/gz-mx/SKILL.md:46,57`, `src/gzkit/mx/AGENTS.md:19,21` + `.claude`/`.agents`/`.github` mirrors). `gz-mx` skill falsely claims `gz mx enter` creates `.gzkit/mx-active`. Mitigated (awareness hook reads `mx.json`, so the banner fires) but the documented manual-check contract is wrong. | independently verified | ❌ untracked | Correction — direct-fix GHI (replace `mx-active` → `mx.json` across canonical surfaces, re-sync mirrors). Lite lane. |
| F2 | **Enforcement floor demotes in hangar (BI#3/§5 tension).** The `Enforcement floor` `gz check` step is absent from `_STEP_GUARD_META` (`src/gzkit/commands/quality.py:41-79`), so it falls back to `guard_name='enforcement-floor'` / `ERROR`. `checkpoint.resolve` (`src/gzkit/mx/checkpoint.py:29-33`): `'enforcement-floor'` ∉ `GATE5_INVARIANTS`, marker active + `ERROR != CRITICAL` → `Route.ADVISORY`; `_apply_mx_seam` (`quality.py:98-111`) converts the floor's `returncode=3` (a FACADE — e.g. grader-gaming) into `success=True` inside the hangar. Realizes ADR Decision item-3's own warning ("a grader-gaming that could go advisory in the hangar would make MX the safe place to vibe undetected"). Backstopped only by `gz mx exit` full-strength re-run. | independently verified | ❌ untracked | Correction — needs **operator/designer ruling**: is the exit backstop sufficient, or must the floor step pin (emit CRITICAL / be named a floor member) so it never demotes in the hangar? Then GHI. |
| F3 | **17-05 / BI#9 enrollment-completeness enumeration is a facade for its asserted property.** BI#9 / REQ-0.0.74-17-05 assert the meta-validator "enumerates `GATE5_INVARIANTS` membership" and "a member with no entry fails the floor." No code enumerates `GATE5_INVARIANTS` for enrollment: `run_meta_validator` (`enforcement.py:337`) iterates only the registry; `_enforcement_floor_green` (`closeout_proof.py:140`) checks only PASS counts; `_GATE5_NAMED_NOT_ENFORCED` (`mx/invariants.py:54`) is never consumed. A future 6th floor member with no NC would ride green. 17-05's floor-green deferral does not exercise the property it asserts. All five *current* members are honestly handled. | spec-reviewer (code-cited) | ✅ **GHI #648** (remaining work, routed to AIRLOCK / campaign Movement III) | Correction — already tracked; operator adjudicates whether tracked-but-unbuilt forward-protection blocks VALIDATED. |

### Minor / Info

| ID | Finding | Disposition |
|----|---------|-------------|
| m1 | ADR BI#9 prose overstates an enumeration property not built; contradicts Consequences/Negative #7 (which is honest). | Fold into F3's GHI (#648). |
| m2 | `src/gzkit/req_kind.py` is 765 lines (> 600-line limit, `.claude/rules/pythonic.md`). Pre-existing, exacerbated by OBPI-18 + the closeout-proof fix. | GHI (tech-debt). |
| m3 | `_STEP_GUARD_META` maps build steps (Lint/Format/Typecheck/Test/Behave) as ERROR-demotable, but the `returncode==3` gate makes those entries inert (they exit 1). Documented-vs-actual mismatch, not a facade. | Note; low priority. |
| m4 | `check_hook_liveness` verifies only the Claude vendor surface; ADR claims per-vendor (`.claude`/`.agents`/`.github`) adaptation. | Note. |
| m5 | OBPI-10 (withdrawn) brief body has a stale `**Status:** Draft` line vs `status: withdrawn` frontmatter; audit-check advisory counts withdrawn-OBPI REQs. | Cosmetic; low priority. |

## 5. Verdict & gate checklist

**VALIDATED checklist:**
- [x] Audit plan / mechanical checks executed with proofs
- [x] Fidelity gate run (10/10 pass) — ADR thesis holds at test layer
- [x] Independent spec + quality review dispatched
- [ ] **No unresolved MAJOR shortfalls** — ❌ F1, F2, F3 open
- [ ] Validation receipt emitted — **withheld** (Red Flag: never emit with unresolved shortfalls)
- [ ] Lifecycle = Validated

**The audit does not pass to VALIDATED.** The ADR remains COMPLETED. F1/F2/F3 are facade/coherence corrections — natural campaign **Movement II ("Drain the facade", patch line 0.29.1+)** work. F2 needs an operator/designer ruling; F1 is a clean direct-fix; F3 is tracked (#648).

**Attestation:** *unsigned* — audit verdict is CONCERNS; no agent sign-off and no `validated` receipt until shortfalls are dispositioned and (where chosen) repaired, then re-audited.
