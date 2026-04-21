# AUDIT PLAN — ADR-0.0.18 ADR Taxonomy Doctrine

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.18-adr-taxonomy-doctrine |
| ADR Title | ADR Taxonomy — Operator Doctrine (pool curation, PRD→ADR derivation, epic grouping) |
| SemVer | 0.0.18 |
| Kind / Lane | foundation / lite |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine |
| Audit Date | 2026-04-20 |
| Auditor(s) | agent:claude-opus-4-7 (Gate 5 human attestation recorded at OBPI completion, 2026-04-20 g0) |

## Purpose

Confirm ADR-0.0.18 implementation is complete by validating its claims with reproducible CLI evidence. The ADR lands operator doctrine: a one-page concepts reference, a PRD→ADR derivation runbook section, a pool curation policy, an epic grouping naming convention with `gz status --epic` filter, and skill prompt enrichment for `gz-plan` / `gz-adr-create`.

**Audit Trigger:** Post-implementation validation phase. All five OBPIs are `attested_completed` in the ledger with per-OBPI Gate-5 human attestation recorded 2026-04-20 (g0). Audit advances lifecycle from Completed → Validated.

## Scope & Inputs

**Primary contract surfaces delivered by the ADR:**

- `docs/user/concepts/adr-taxonomy.md` — canonical one-page taxonomy reference (OBPI-01)
- `docs/user/runbook.md` § PRD → ADR Derivation — 103-line insertion (OBPI-02)
- `docs/governance/pool-curation.md` — pool entry/promotion/retirement policy (OBPI-03)
- `gz status --epic <slug>` — filter flag on existing command; pool-ADR filename + frontmatter matching (OBPI-04)
- `.gzkit/skills/gz-plan/SKILL.md` and `.gzkit/skills/gz-adr-create/SKILL.md` — interview-prompt enrichment (OBPI-05)

**Operator assertion the ADR delivers:** An adopter reading the concepts page alone can answer *"what kind of ADR am I writing"* without source-spelunking through `AGENTS.md`; the CLI `--kind` no-default becomes an informed choice via skill prompts; pool curation has a named policy; epic grouping survives pool→active transitions.

## Planned Checks

| # | Check | Command / Method | Expected Signal | Result |
|---|-------|------------------|-----------------|--------|
| 1 | Ledger completeness | `uv run gz adr audit-check ADR-0.0.18` | Exit 0, PASS, 34/34 REQs covered | ✓ |
| 2 | ADR lifecycle / OBPI state | `uv run gz adr status ADR-0.0.18` | Lifecycle=Completed, 5/5 OBPIs attested_completed, no issues | ✓ |
| 3 | Gate covenant | `uv run gz gates --adr ADR-0.0.18` | Gate 1 PASS, Gate 2 PASS, Gate 3/4 n/a (lite), Gate 5 PASS | ✓ |
| 4 | Concepts page exists + strict mkdocs | `test -f docs/user/concepts/adr-taxonomy.md && uv run mkdocs build --strict` | File exists (187 lines); build clean | ✓ |
| 5 | Pool curation policy exists + strict mkdocs | `test -f docs/governance/pool-curation.md` | File exists (139 lines); build clean | ✓ |
| 6 | Runbook cross-links the concepts page | `grep -l "adr-taxonomy.md" docs/user/runbook.md` | Match present | ✓ |
| 7 | `gz status --epic` flag registered | `uv run gz status --help` | `--epic SLUG` flag and help text visible | ✓ |
| 8 | `gz status --epic` empty-match exit 0 | `uv run gz status --epic <no-match>` | Exit 0, informational empty message | ✓ |
| 9 | Skill prompt enrichment landed | `grep -l "adr-taxonomy" .gzkit/skills/gz-plan/SKILL.md .gzkit/skills/gz-adr-create/SKILL.md` | Both files cite the concepts page | ✓ |
| 10 | Taxonomy validator clean | `uv run gz validate --taxonomy` | All validations passed | ✓ |
| 11 | Lint clean (ARB) | `uv run gz arb ruff` | Exit 0 | ✓ |
| 12 | Typecheck clean (ARB) | `uv run gz arb typecheck` | Exit 0 | ✓ |
| 13 | Tests pass (ARB) | `uv run gz arb step --name unittest -- uv run -m unittest -q` | Exit 0, 3249 tests OK | ✓ |
| 14 | Docs build clean (ARB) | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | Exit 0 | ✓ |
| 15 | CLI audit clean | `uv run gz cli audit` | Exit 0 | ✓ |

## Risk Focus

- **Doctrine drift.** The ADR is Lite-lane foundation; its external contract surface is near-zero (only the new `--epic` filter). The real risk is doctrine drift: the concepts page, runbook section, pool policy, and skill prompts all describe the *same* taxonomy and must stay mutually consistent. Mitigation: `mkdocs --strict` resolves all cross-links; the taxonomy validator binds kind/semver mechanically; skills cite the concepts page so drift is surfaced at next operator pass.
- **Pre-existing reflection drift.** OBPI-01's Implementation Summary was prose (not bullet format), which the validator `_has_substantive_implementation_summary` rejects as a placeholder. Pure-doc OBPIs 01/03/05 were missing the `[doc]` REQ classification tag that OBPI-02 established — `gz covers` read them as 27 uncovered testable REQs. Both surfaced during audit and were fixed as adjacent in-flight defects per Behavioral Invariants 2/4.
- **Frontmatter / ledger drift.** The ADR file's `status:` was `Draft` while the ledger recorded `Completed` — Gate 1 flagged this before fix. Resolved via `gz frontmatter reconcile` (1 file rewritten).

## Findings Placeholder

Captured in `AUDIT.md`.

## Acceptance Criteria

- All planned checks executed; results recorded in `AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced from `AUDIT.md`.
- ADR lifecycle advances Completed → Validated via `gz adr emit-receipt --event validated`; `gz adr report` confirms the change.
- No blocking discrepancies remain; adjacent in-flight defects either fixed or filed with traceable disposition.

## Attestation Placeholder

Human will review and sign in `AUDIT.md` § Attestation if standalone; otherwise closeout ceremony Step 4 covers this.
