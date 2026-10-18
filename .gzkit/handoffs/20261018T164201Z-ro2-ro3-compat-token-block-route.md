---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T16:42:01Z'
agent: claude-code
session_id: e6800367-eb28-4b68-9624-65d94f7cdf17
continues_from: .gzkit/handoffs/20261018T154734Z-requirements-model-identity-open-ghi-1257-landed.md
---

## Current State Summary

The requirements model is fully ruled and written into canon. On 2026-10-18 the operator ruled decisions 2 to 10 one at a time (identity, authority, lifecycle with Backplane three-valued revision-bound REQ proof, readiness by explicit edges, one work package per outcome, no version in any id, the Q-19 open points, ADR links, BDD on user-facing outcomes) and the family legend on MIL-STD-881's model (decision 8.3: Scheme A banded into product elements X H C M P D and common elements R G A L Q). Landed: docs/governance/ieee/requirements-model.md (dd075ebe5, 5654caac2) with three schemes and FDAU's paper migration test (verdict: pass on paper); the PRD reconciled (755369437: FR-004 retired, FR-005/005a/005b split, FR-013 to FR-031 and AC-013 to AC-031 added, FR-001 layout and FR-005b Gate 5 corrected). Each ruling is an insight record, scope harbor-pilotage-wp4. Tree clean, origin/main level.

## Important Context

Safe mode is active (harbor pilotage drydock, docs/governance/harbor-pilotage-candidate-2026-10-15.md); the MX session 696ca9a4 is past its lease and carries advisory debt: expiry is booked and announced, never evicted, and only gz mx exit through the gz-mx skill closes it. RO-3 as written in the harbor contract predates the model: it names data/requirements_catalog.json, a feature-area registry, and 'a feature file declares one area'; the ruled model says data/catalog/ holding families, outcomes and REQs, and a feature file belongs to one outcome. RO-3 must be re-scoped to requirements-model.md before anyone specifies it. RO-2 (the id-resolution seam, phase 1 of ADR-pool.identifier-ladder-migration) is consistent with the model: member_of is the explicit parent field it calls for, and the paper test adds one constraint, that the resolver must disambiguate a reused numeric prefix (OBPI-0.28.0-01 names both chores-cli and context-core) by slug or rename event. The token-block expiry ruling ('expiry is never an eviction', applied to the token block by the operator's 'yes, of course, didn't I draw their equivalence') conflicts with OBPI-0.35.0-19 Requirement 8, which keeps TTL reaping; that brief is at its size ceiling and ADR-0.35.0 is frozen by RO-8, so the amend-the-brief route the operator first chose is blocked.

## Decisions Made

- [operator-ruled] Requirements-model decisions 2 to 10 and 8.3, each selection booked verbatim as an insight (scope harbor-pilotage-wp4); the family legend follows MIL-STD-881: 'so, perhaps MIL-STD-881 had the best compromise?' then '881: product + common (Rec.)'.
- [operator-ruled] BDD stays the standing user-facing rationale, only re-anchored to the outcome: 'gzkit has EXTENSIVE use of BDD already and it has always used that rationale (the user-facing surfaces and interfaces)'.
- [operator-ruled] The PRD amendment, verbatim: 'Amend the PRD to the dispositions in requirements-model.md: retire FR-004, split FR-005/005a/005b, and add the new FRs for the behaviour it doesn't name.'
- [agent-chose] Kept the 2026-10-17 text of design-candidates.md § The joined requirements model as a record under a replacement notice instead of deleting it.
- [agent-chose] Marked split PRD lines legacy rather than striking them, because gz specify and gz closeout still behave that way until migration.

## Immediate Next Steps

1. Get the operator's ruling on the token-block expiry route: a GHI direct fix in maintenance mode (recommended; ADR-0.35.0 is frozen by RO-8 and the brief is at its ceiling) or hold for civil rule. Then tell the idle child session local_43a33688 to proceed or stop.
2. Re-scope RO-3 in the harbor contract to requirements-model.md (data/catalog/, families, outcomes, REQs with member_of, proof results, depends_on, user_facing, the outcome-scoped BDD alignment check) and put the amended row to the operator.
3. Start the RO-2 specification: the card task_9c394f63 awaits the operator. The spec names every reader of version-shaped ids (requirements-model.md § Step 2 measured 371 Python files and 358 @covers test files), the one resolver, the reused-prefix constraint, and the validator proving every reader resolves through the seam.
4. Have the operator approve the RO-2/RO-3 compatibility path, which is FDAU migration step 5, still half reached.

## Pending Work / Open Loops

The lane language in PRD FR-006 and FR-008 and AGENTS.md § Gate Covenant moves to the outcome's user_facing flag only when the catalog lands. The gz-design, gz-obpi-pipeline and gz-adr-create skills still assume an ADR parents its work. docs/governance/GovZero/adr-lifecycle.md carries its own identifier scheme. Two model-surfaced gaps are booked as insights: gz mx and gz context have no tagged scenarios, and ADR-0.28.0 took the lite lane for a human-facing CLI verb. The semver-order work ruling still binds legacy ADR work until the operator retires it explicitly. The MX hangar session remains open.

## Verification Checklist

uv run gz handoff rulings --search harbor-pilotage; git log --oneline -6 (expect 755369437, 5654caac2, dd075ebe5); read docs/governance/ieee/requirements-model.md § The decisions, as ruled and § 8.3; read docs/design/prd/PRD-GZKIT-1.0.0.md § 19 entry of 2026-10-18; sed -n 181,182p docs/governance/harbor-pilotage-candidate-2026-10-15.md to see RO-2 and RO-3 as written; git rev-list --left-right --count origin/main...HEAD reads 0 0.

## Evidence / Artifacts

- `docs/governance/ieee/requirements-model.md`
- `docs/design/prd/PRD-GZKIT-1.0.0.md`
- `docs/governance/ieee/design-candidates.md`
- `docs/governance/ieee/OPEN-QUESTIONS.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/rnd/renewing-vows/identifier-migration-program.md`
- `.gzkit/insights/agent-insights.jsonl`
- `artifacts/receipts/arb-step-mkdocs-058138a431b649308356452c6ce50276.json`

## Settled Rulings

1600 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
