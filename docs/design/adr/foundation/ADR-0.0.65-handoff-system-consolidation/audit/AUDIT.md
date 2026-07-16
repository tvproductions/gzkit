# AUDIT — ADR-0.0.65-handoff-system-consolidation

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.65-handoff-system-consolidation |
| Title | Handoff System Consolidation and CLI Surface |
| SemVer / Kind / Lane | 0.0.65 / foundation / heavy |
| Audit Date | 2026-07-15 |
| Driver | pipeline-orchestrator |
| Independent reviewers | spec-reviewer, quality-reviewer (dispatched per skill Persona Dispatch) |
| Transition | COMPLETED → VALIDATED |
| Recommendation | **VALIDATED may proceed** — no blocking defects; concerns are minor and tracked |

## 1. Fidelity Gate (Step 3 — bound, `gz adr fidelity`)

`uv run gz adr fidelity ADR-0.0.65-handoff-system-consolidation` → **3 pass, 0 fail** (proof: `proofs/fidelity.txt`).

| Claim | Command | Expected | Observed | Result |
|-------|---------|----------|----------|--------|
| `gz handoff` verb ships; read projection over `.gzkit/handoffs/` works (OBPI-02/-03) | `gz handoff list --json` | 0 | 0 | ✓ |
| Archive lock-handoff coupling guard validates green (OBPI-05) | `gz validate --lock-handoff-coupling` | 0 | 0 | ✓ |
| Fidelity block is parseable | `gz adr fidelity …65… --check` | 0 | 0 | ✓ |

> **Remediation applied during audit:** the pre-audit row 1 was self-labeled
> `WEAK` and asserted "the gz handoff verb is unbuilt (Proposed)" — false since
> the verb shipped in OBPI-02/-03. It was replaced with a runnable probe that
> actually exercises the delivered CLI surface, so the gate now fails if the
> thesis regresses. (Both independent reviewers flagged the stale prose:
> spec-reviewer finding @ ADR:102, quality-reviewer DOC-1.)

## 2. Execution Log (mechanical checks)

| Check | Command | Signal | Result | Proof |
|-------|---------|--------|--------|-------|
| Ledger proof (L2) | `gz adr audit-check ADR-0.0.65` | 5/5 OBPIs PASS; 22/28 REQ covered (6 advisory SUPPORT) | ✓ | `proofs/audit-check.txt` |
| Gate status | `gz adr status ADR-0.0.65 --json` | Gates 1–5 pass; closeout attested (g0, 2026-07-15) | ✓ | — |
| Heavy gates | `gz gates --adr ADR-0.0.65` | pass | ✓ | `proofs/gates.txt` |
| Governance CLI audit | `gz cli audit` | pass; 129/129 commands covered | ✓ | — |
| Verb + API exist | `gz handoff --help`; `ls src/gzkit/handoff_api.py` | 4 subcommands; 13 KB module | ✓ | — |
| Documents (post-edit) | `gz validate --documents` | clean (1 scope) | ✓ | — |
| Live value demo | `gz handoff list` / `archive --dry-run` / lock-coupling | all working | ✓ | `proofs/value-demo.txt` |

**Ledger-proof staleness:** fresh — closeout attested 2026-07-15 (audit date),
well within the 7-day threshold. Layer-2 trust honored; no re-verification forced.

## 3. Thesis Verification (does the ADR's claimed capability hold?)

The ADR was born from a 2026-05-29 "half-wired" audit (GHI #529): write surface,
read surface, and executable API disagreed about where handoffs live. The audit
confirms all four surfaces now agree on `.gzkit/handoffs/`:

| Surface | Evidence | Agrees on `.gzkit/handoffs/`? |
|---------|----------|-------------------------------|
| Write (skill doctrine) | `.gzkit/skills/gz-session-handoff/SKILL.md:55,78,107` | ✓ |
| Write (CREATE API) | `src/gzkit/handoff_api.py:106-107,250-253` | ✓ |
| Read (orientation) | `scripts/session_orientation.py:151-158` — single-surface; GHI #529 dual-scan **deleted** | ✓ |
| Read (API / archive) | `handoff_api.py:300`; `handoff_archive.py:95-96` | ✓ |
| On-disk migration | `docs/design/adr/**/handoffs/*.md` → **no files** (24 relocated) | ✓ |

- **CREATE is fail-closed** through the validation gate: `handoff_api.py:244`
  validate → `:246` raise-on-violation → `:253` write-only-after-guard. Hand-
  authoring is no longer the only path (kills the vaporware-API defect).
- **Lock-handoff coupling guard is real and load-bearing** on both audit-time
  (`governance/trust_audits/lock_handoff_coupling.py:30-99`) and runtime archive
  (`handoff_archive.py:164-176,258-259`) paths.

## 4. REQ Coverage — spec-reviewer independent trace

Verdict: **PASS-WITH-CONCERNS.** Every BEHAVIOR REQ has a real `@covers` test
asserting REQ semantics (not string/shape pins); the fail-closed CREATE wiring
is genuine in code. Per-OBPI claimed coverage HOLDS for all five.

The 6 advisory-uncovered REQs are all `[SUPPORT]` (proof-channel exempt — ledger
event + structural validator), none a silently-uncovered BEHAVIOR:

| REQ | Kind | Legitimacy |
|-----|------|------------|
| REQ-0.0.65-01-05 | SUPPORT | legitimate (skill-version bump + surfaces sync) |
| REQ-0.0.65-02-06 | SUPPORT | legitimate (SKILL.md repoint) |
| REQ-0.0.65-02-09 | SUPPORT | legitimate (brief-reconcile + agent-sync events) |
| REQ-0.0.65-03-04 | SUPPORT | legitimate (manpages/index/doc-coverage) |
| REQ-0.0.65-03-05 | SUPPORT | legitimate (skill wields verb) |
| REQ-0.0.65-05-06 | SUPPORT | legitimate (handoff-archive manpage) |

## 5. Structural Coherence — quality-reviewer independent review

Verdict: **COHERENT-WITH-CONCERNS.** Split-brain genuinely closed (not merely
relocated); no architectural defect blocks VALIDATED. Pydantic conventions clean
(all models `frozen=True, extra='forbid'`); every function < 50 lines.

## 6. Shortfall Register

No **blocking** shortfalls. Minor findings, all tracked:

| # | Finding | Severity | Route | Status |
|---|---------|----------|-------|--------|
| S1 | Stale `WEAK`/"unbuilt (Proposed)" fidelity prose (ADR:102) + unchecked checklist boxes vs Completed status | minor (doc) | **Fixed in-audit** — fidelity block rewritten to a runnable thesis probe; 5 checklist boxes checked; `gz validate --documents` clean | ✅ resolved |
| S2 | `collect_handoff` (`session_orientation.py:169`, unguarded) **and** the campaign scanner (`:72`, `except OSError` misses `UnicodeDecodeError`) read strict-UTF-8 without the guard the API sibling `list_handoffs` has (`handoff_api.py:306-312`, GHI #582) — a non-UTF-8 file crashes the SessionStart hook, contradicting the module's "never crash the boot" contract | minor (robustness) | **GHI [#688](https://github.com/tvproductions/gzkit/issues/688)** — direct-fix work order; sibling-cut of #582, cross-linked | ✅ filed (open) |
| S3 | `continues_from` resolver duplicated across the OBPI-02/-05 brief boundary (`handoff_api.py:188-198` vs `handoff_archive.py:179-197`) with no coherence test forcing the mirror to stay consistent — Invariant-1a fragility | minor (maintainability) | **GHI [#689](https://github.com/tvproductions/gzkit/issues/689)** — direct-fix work order (shared helper or coherence test) | ✅ filed (open) |
| S4 | `handoff_validation.py` = 732 lines, over the 600-line module ceiling (`.claude/rules/pythonic.md §9`); largely pre-existing (ADR-0.0.25 base + GHI #619 + OBPI-0.0.72-02) | minor (size) | Existing **oversized-module census** (Build-to-1.0 campaign, Movement IV) | ⏳ tracked by census |
| S5 | REQ-0.0.65-01-02 text says "exactly 34 .md files" but covering test asserts `>= 34` (floor); documented + defensible (permits handoff accretion + archive subdir) — test looser than REQ, not the pin anti-pattern | trivial (wording) | Note; fold into S3 GHI if brief amendment is taken | 📝 noted |
| S6 | Two register-writers (`write_degenerate_handoff`, `write_completion_handoff` in `handoff_validation.py`) write without `validate_handoff_document` — by design (ADR-0.0.41 / GHI #619 mechanical token-block writers, post-hoc validated by `--lock-handoff-coupling`), NOT a CREATE bypass | info | Noted for future readers | 📝 noted |

## 7. Evidence Index

- `proofs/fidelity.txt` — bound fidelity gate (3 pass, 0 fail)
- `proofs/audit-check.txt` — L2 ledger proof (5/5 OBPIs PASS)
- `proofs/gates.txt` — heavy gate status
- `proofs/value-demo.txt` — live `gz handoff` list / archive-dry-run / lock-coupling output
- `AUDIT_PLAN.md` — extracted claims, planned checks, risk focus

## 8. Summary Table

| Dimension | Assessment |
|-----------|------------|
| Completeness | ✅ 5/5 OBPIs completed with evidence; all BEHAVIOR REQs covered |
| Integrity | ✅ Layer-2 ledger proof fresh; fidelity gate 3/3; two independent reviews concur |
| Alignment (code = docs = tests) | ✅ after S1 doc remediation; write/read/API/CLI agree on `.gzkit/handoffs/` |
| Value demonstrated | ✅ live CLI surface + guards shown working (`proofs/value-demo.txt`) |
| Blocking shortfalls | None |
| Follow-ups | S2, S3 → GHI; S4 → census; S5/S6 → noted |

## 9. Attestation

- **Agent (audit driver):** pipeline-orchestrator — audit executed per `gz-adr-audit`
  skill; mechanical checks green, bound fidelity gate 3/3, two independent persona
  reviews (spec-reviewer PASS-WITH-CONCERNS, quality-reviewer COHERENT-WITH-CONCERNS)
  concur that no defect blocks the VALIDATED transition. In-artifact doc drift (S1)
  remediated; S2/S3 routed to GHIs.
- **Human (Gate-5):** _pending operator verbal `accept audit` / `verify audit` — the
  audit-validation acceptance is a distinct operator moment from OBPI closeout._
