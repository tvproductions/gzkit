---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T09:09:56Z'
agent: claude-code
session_id: eb9c59a4-16bc-412f-af6b-5fcd124c0a9a
continues_from: .gzkit/handoffs/20260913T075615Z-session-89fe194c-chores-rulings-exit-codes.md
---

## Current State Summary

Session eb9c59a4 resumed `20260913T075615Z-session-89fe194c-chores-rulings-exit-codes.md` (Fresh, verified: main level with origin, no locks, #999/#1002/#936 open, #1000/#1001 closed, named tests green). Operator ruling booked with `gz handoff decide`: proceed on #1002 then #999 step 3; #936 and the R&D skill design set aside.

Landed and pushed to main (HEAD `6615d0a18`, level with origin, clean tree):
- `c9c16de7c` — gz-session-handoff 7.4.0: never restate an inherited ruling in Decisions Made (GHI #1003, left open for Movement D).
- `e2d31cbac` — GHI #1002 CLOSED: every CHORE.md cites acceptance.json and registry.json instead of copying them; `audit_chore_metadata_authority` runs in gz check; 7 registry versions reconciled; required-artifact `fileExists` criteria restored on four control-surface chores.
- `84d3e23c8` — GHI #1005 CLOSED: files directly under the chores/skills surface no longer resolve as slugs, so the filtered registry and README ship; baseline manifest regenerated.
- `6615d0a18` — GHI #999 step 3: `audit_chore_rung_conformance`, declared workflow step stages checked against the declared rung. #999 stays open for steps 4–6.

Filed this session: #1003, #1004, #1005 (fixed), #1006. Every commit set passed `gz check` with a real exit 0, read from the verifier's own status rather than the harness notification.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system** — #1003 filed and its advisory arm landed (skill guidance); the identity arm belongs to Movement D's "Rulings become first-class" box. #1004 filed: `gz handoff decide` output, `--decision` help, two manpages and the operator runbook still describe the retired resume gate. #870 untouched.
- **ghi triage** — filed #1003–#1006; closed #1002 and #1005. No `ghi-triage` pass run; queue totals unverified.
- **adr/obpi campaign** — no OBPI work (IRON LAW), no locks. ADR-0.35.0 remains TOPMOST, untouched. Chore class work advances the Movement C `doctrine-declared-without-mechanism` box's agent-side arm only.
- **new R&D** — not worked; set aside at the resume ruling.

### Chore surface authority (settled by #1002)
- Criteria live only in `acceptance.json`; version/lane/slug/vendor/timeout and the class declaration live in `registry.json`. A CHORE.md criteria section cites the JSON, carries no table, and quotes only commands the JSON runs; there is no `**Version:**` field; the newest change note `**X.Y.Z (…)**` equals the registry version; Lane/Slug/Vendor/Timeout may stay but must equal the registry; runner-uncheckable obligations go under `## Manual completion checks`.
- Step 3 syntax: each `###` step under `## Workflow` ends ` — <stage>` from `observe · propose · repair · operator-only-repair`. The check binds a chore only once it is declared (step 5).

### Gotchas learned
- Background-task notifications reported exit 0 twice over a real `gz check` exit 1 (lint, then typecheck). Only the echoed `REAL EXIT` is evidence.
- `_classify_chore_file` had silently withheld every surface-level chores file from sync since `921728abb`; `gz validate --distribution` checks glob and manifest membership, not byte parity, so it never saw the stale shipped registry.
- A mutation that removes a guard whose absence crashes (`AttributeError`/`ValueError`) scores `inconclusive`, not killed. Disclose it; never reshape production code to make the sweep score.
- The independent spec review caught the package-surface gap and four audit holes on the first pass. Run it before closing, not after.

## Decisions Made

- [operator-ruled] Resume ruling on `20260913T075615Z`: "#1002 then #999 step 3 (Recommended)" — #936 and the R&D skill design set aside for this session.
- [operator-ruled] Duplicate rulings re-put with GHI #838's no-widening ruling and Movement D disclosed: "GHI + skill guidance (Recommended)" — file the evidence as #1003, land skill guidance now, leave the identity arm to Movement D. The earlier "File GHI, fix at authoring" selection is withdrawn as made on a framing that omitted the store's own docstring.
- [operator-ruled] #999 step 3 mechanism: "Declared step stages (Recommended)" — workflow step headings declare a stage from the rung vocabulary and no stage may exceed the declared rung; keyword heuristic and run-diff-alone rejected.
- [agent-chose] Fixed #1005 in-session before closing #1002, because #1002's closure boundary named the `src/gzkit/chores/` surface and its registry/README edits could not ship otherwise.
- [agent-chose] Held Lane/Slug/Vendor/Timeout equal to the registry instead of deleting them: zero measured drift, and they sit beside rationale prose.
- [agent-chose] Restored `fileExists` criteria on four control-surface chores rather than reconciling them toward the JSON, because the freshness gate that superseded `test -f` never checks a named artifact exists.
- [agent-chose] Did not adopt complexity-reduction-xenon's post-cluster criteria: that would move the gate to the threshold table's block band, the conflict `.gzkit/rules/pythonic.md` routes to the operator.

## Immediate Next Steps

1. GHI #999 step 4: `src/gzkit/chores/README.md` gains the class definitions, the rung ladder, the admission criterion and the declaration requirement, per `docs/governance/chore-class-system.md` §§ The five classes, The four rungs, The admission criterion.
2. GHI #1004: `gz handoff decide` output, `--decision` help, `handoff-decide.md`, `handoff-authorize.md` and the operator runbook stop reporting the retired resume gate, with a test pinning the output.
3. GHI #1006: widen `_cli_alignment_sources` to chore docs and resolve the 8 unresolvable `gz` chains in 4 chores (rename, register, or mark speculative after reading each).
4. Set-aside items awaiting operator initiation: GHI #936 (`gz chores status`) and the R&D skill design from the prior handoff.

## Pending Work / Open Loops

- GHI #999 steps 5–6: per-chore declarations (now including a stage on every workflow step) with the absence→refusal flip; the suppression rule with its witness. Read GHI #997 and GHI #808 before declaring those chores.
- GHI #1003 stays open until Movement D's typed ruling event gives rulings identity.
- Stale proofs: `control-surface-permission-consent-drift` and `control-surface-skill-rule-reachability` fail their freshness criterion (the latter because `c9c16de7c` moved `.gzkit/skills`); their audits need re-running before `gz chores run` goes green.
- complexity-reduction-xenon still names the pre-landing verb `gz complexity-advise` in its workflow and checklist (tracked by #1006), and its post-cluster mode waits on the pythonic.md threshold ruling.
- Mutation evidence gaps, disclosed: the stageless and unknown-stage guards in `audit_chore_rung_conformance` are observed only as crashes when removed.
- GHI #870 and GHI #810 untouched. No ghi-triage pass this session.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
gh issue view 1002 --json state,title
gh issue view 1005 --json state,title
gh issue view 999 --json state,title
gh issue view 1003 --json state,title
gh issue view 1004 --json state,title
gh issue view 1006 --json state,title
uv run -m unittest tests.governance.test_chore_metadata_authority tests.governance.test_chore_rung_conformance tests.test_chores_surface_level_files
uv run gz validate --distribution
uv run gz handoff rulings --search "Declared step stages"
```

Expected at authoring: 0 0; no active locks; #1002 and #1005 CLOSED; #999, #1003, #1004, #1006 OPEN; tests green; distribution exit 0; the stages ruling found. Re-run rather than trust these.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/chores.py` — `audit_chore_metadata_authority` (GHI #1002) and `audit_chore_rung_conformance` (GHI #999 step 3).
- `tests/governance/test_chore_metadata_authority.py`, `tests/governance/test_chore_rung_conformance.py`.
- `src/gzkit/chores/__init__.py`, `src/gzkit/skills/__init__.py`, `tests/test_chores_surface_level_files.py` — slug resolution and nested-instructions class (GHI #1005).
- `data/distribution_baseline_manifest.json` — regenerated.
- `.gzkit/chores/registry.json`, `.gzkit/chores/README.md` and all `.gzkit/chores/*/CHORE.md` — reconciled.
- `docs/governance/chore-class-system.md` — step 3 as landed.
- `.gzkit/skills/gz-session-handoff/SKILL.md` — restated-ruling guidance (GHI #1003).
- Commits `c9c16de7c`, `e2d31cbac`, `84d3e23c8`, `6615d0a18`.
- ARB receipts `arb-ruff-bd9a204327e240439a237b1cb520c033`, `arb-step-typecheck-25b023505ddf4750be9a1c73c7f55c09`, `arb-step-unittest-24be0b7671c244808e99f1c14aedcee1`.
- GitHub issues #999, #1002, #1003, #1004, #1005, #1006.

## Settled Rulings

833 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
