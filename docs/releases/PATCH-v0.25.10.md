# Patch Release: v0.25.10

**Date:** 2026-04-18
**Previous Version:** 0.25.9
**Tag:** v0.25.9

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 215 | Discoverability: wire trust-doctrine and advisory-rules-audit into agent control surfaces | diff_only | GHI #215 has commits touching src/gzkit/ but no 'runtime' label |
| 214 | Enumerate and audit remaining Layer 3 derived views beyond frontmatter/graph | diff_only | GHI #214 has commits touching src/gzkit/ but no 'runtime' label |
| 213 | Promote advisory rule: reconciliation is a core operation, not maintenance chore | diff_only | GHI #213 has commits touching src/gzkit/ but no 'runtime' label |
| 212 | Meta: advisory-rules-audit scorecard needs self-test | diff_only | GHI #212 has commits touching src/gzkit/ but no 'runtime' label |
| 211 | Promote advisory rule: behave REQ scenario-tag coverage → mechanical audit | diff_only | GHI #211 has commits touching src/gzkit/ but no 'runtime' label |
| 210 | Promote advisory rule: sync-after-skill-edit → mechanical pre-commit drift detection | diff_only | GHI #210 has commits touching src/gzkit/ but no 'runtime' label |
| 209 | Promote advisory rule: no third test tier under unittest → mechanical scan | diff_only | GHI #209 has commits touching src/gzkit/ but no 'runtime' label |
| 208 | Promote advisory rule: pool ADRs in runtime track → mechanical detection | diff_only | GHI #208 has commits touching src/gzkit/ but no 'runtime' label |
| 207 | Promote advisory rule: no manual ledger edits → pre-commit guard | diff_only | GHI #207 has commits touching src/gzkit/ but no 'runtime' label |
| 206 | Promote advisory rule: no PYTHONUTF8=1 prefix on uv run gz → mechanical scan | diff_only | GHI #206 has commits touching src/gzkit/ but no 'runtime' label |
| 205 | Promote advisory rule: version bump → GitHub release → mechanical alignment audit | diff_only | GHI #205 has commits touching src/gzkit/ but no 'runtime' label |
| 204 | Promote advisory rule: class size limit (300 lines) → mechanical AST audit | diff_only | GHI #204 has commits touching src/gzkit/ but no 'runtime' label |
| 203 | Promote advisory rule: Pydantic BaseModel + ConfigDict discipline → mechanical AST audit | diff_only | GHI #203 has commits touching src/gzkit/ but no 'runtime' label |
| 202 | Promote advisory rule: tool-skill-runbook alignment Invariants 1-3 → mechanical gz validate scope | diff_only | GHI #202 has commits touching src/gzkit/ but no 'runtime' label |
| 201 | Defect (Class G): gz git-sync auto-commits lack Task trailer, always trip gz validate --commit-trailers | excluded |  |
| 200 | Defect (Class F / regression): GHI #193 fix has no regression test — graph builder attestation invariant is advisory | excluded |  |
| 199 | Defect (Class E): ARB ty-check scope diverges from gz typecheck — receipts can green-light closeouts that gz typecheck rejects | excluded |  |
| 198 | Defect (Class C): BDD scenarios silently drift from CLI output when recovery strings change | excluded |  |
| 197 | Defect (Class B): ty migration residue — mypy-style # type: ignore[code] comments silently unrecognized by ty | excluded |  |
| 196 | Defect-fix routing: agents author full OBPI ceremony for trivial in-flight fixes when direct commit is the established precedent | diff_only | GHI #196 has commits touching src/gzkit/ but no 'runtime' label |
| 195 | gz obpi precomplete: pre-Stage-5 checklist not mechanically enforced; reactive triage burns context | excluded |  |
| 194 | gz obpi validate: brief-prescribed commands not verified against registered CLI surface | diff_only | GHI #194 has commits touching src/gzkit/ but no 'runtime' label |
| 193 | gz obpi complete writes brief status='Completed' but canonical-ledger form is 'in_progress' | diff_only | GHI #193 has commits touching src/gzkit/ but no 'runtime' label |
| 192 | validate_frontmatter omits pool-ADR skip filter that frontmatter_coherence library applies | diff_only | GHI #192 has commits touching src/gzkit/ but no 'runtime' label |
| 191 | plan-audit-gate ↔ plan-mode deadlock: ExitPlanMode requires a write that plan mode forbids | diff_only | GHI #191 has commits touching src/gzkit/ but no 'runtime' label |
| 190 | gz-obpi-specify (brief authoring) must ground-truth Allowed Paths before saving | excluded |  |
| 189 | validator recovery hint uses singular 'gz chore run' — should be 'gz chores run' | diff_only | GHI #189 has commits touching src/gzkit/ but no 'runtime' label |
| 188 | plan-audit hook: short-form vs canonical-slug receipt mismatch (class-of-failure fix) | diff_only | GHI #188 has commits touching src/gzkit/ but no 'runtime' label |
| 186 | gz prd scaffolder emits id that its own validator rejects | diff_only | GHI #186 has commits touching src/gzkit/ but no 'runtime' label |
| 185 | gz test --obpi: extend to covered behave scenarios via @REQ-X.Y.Z-NN-MM scenario tags | excluded |  |
| 184 | ty: unresolved-attribute in scripts/backfill_req_ids.py:246 (pre-existing) | excluded |  |
| 183 | Unit-tier test perf hot spots (test_init/test_skills/test_sync_cmds/test_audit > 800ms/test) | excluded |  |
| 182 | Integration-grade tests should mock subprocess or port to behave — tests/integration/ is a symptom patch (follow-up to #181) | diff_only | GHI #182 has commits touching src/gzkit/ but no 'runtime' label |
| 181 | Unit test suite contaminated with integration tests — 89s for 3019 tests | diff_only | GHI #181 has commits touching src/gzkit/ but no 'runtime' label |
| 180 | gz --help exceeds 1.0s startup budget (test_help_renders_fast fails) | diff_only | GHI #180 has commits touching src/gzkit/ but no 'runtime' label |
| 170 | Frontmatter-ledger coherence: lineage derivation path unguarded against stale frontmatter | excluded |  |
| 169 | Frontmatter-ledger coherence: identity resolution path unguarded against stale frontmatter | excluded |  |
| 168 | Frontmatter-ledger coherence: registration path unguarded against stale frontmatter | excluded |  |
| 167 | Frontmatter-ledger coherence: no guard gate or chore audit validates derived frontmatter against ledger truth | excluded |  |
| 162 | ADR frontmatter status: field systemically stale — 94.7% drift rate vs ledger | excluded |  |

## Operator Approval

Approved by gz patch release
