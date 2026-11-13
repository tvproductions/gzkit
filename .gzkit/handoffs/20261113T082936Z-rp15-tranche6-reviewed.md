---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-13T08:29:36Z'
agent: claude-code
session_id: 55f2e5b3-2d9b-4efd-9db1-c56f3ed6becc
continues_from:
- .gzkit/handoffs/20261112T105826Z-drawdown-caller-wired.md
- .gzkit/handoffs/20261113T013931Z-session-exit-bookmark.md
- .gzkit/handoffs/20261113T052550Z-session-exit-bookmark.md
---

## Current State Summary

RP-15 tranche 6 had its independent review and its findings are repaired, pushed (c7c933909..81f5a49bf). A spec reviewer and a quality reviewer that did not write tranche 6 returned FAIL and CONCERNS. Repaired in 607c663f2 with each new test observed failing on the old code: the dependency checker refuses a package not under its source root (it had passed as an empty tree) and reads a dotted package from its nested directory; a kernel base is followed through other classes and package re-exports; a malformed map, a non-UTF-8, non-JSON or non-object baseline fail with three-part prose; the buses refuse an uncallable handler and a non-class key at construction. 21 tests added, 9 tightened. Rule hexagonal-architecture 0.6.2, scorecard row 64f and the validate manpage now state what the checker does not witness. The contract's tranche 6 discrepancy line and a passage-log row record the review; 81f5a49bf booked the amendment pin. GHI 1267 is NOT fixed and stays open; the review was posted on it (issuecomment-6847423606). The previous handoff's line that GHI 1267's mechanism was addressed overstated it.

## Important Context

Safe mode is active; every act is one commit with the Task: TASK-ro6-classic-adr trailer. Why 1267 stays open: the draft package map in pyproject.toml [tool.py-gzkit.hexagon] names domain = gzkit.core.domain, which does not exist, so every live core/ module and gzkit.ontology is unmapped, and the checker never judges an unmapped module's imports; the edge req_kind_support.py:359 -> gzkit.commands.validate_cmd (function-local) is unwitnessed except as unmapped baseline keys. The older one-hop core/ allowlist in tests/policy/test_import_boundaries.py is still the only live fence on core/. The MX session lease expired (mx_session_lease_expired booked 2026-11-13); renewal is the operator's act (gz mx renew --attestor g0) and it gates nothing. Shift turnover: no tag-out log or work-package record exists yet (RO-12); I read the contract's List of discrepancies RP-15 lines and gz obpi lock list (mx-session held by claude-code-28be5a76, lease expired) in their place; this session hung no tag.

## Decisions Made

- [operator-ruled] Proceed on the drawdown-caller-wired handoff (verbatim: "Proceed").
- [operator-ruled] Independent review of tranche 6 moves next (verbatim: "Review tranche 6").
- [operator-ruled] Repair the review's checker defects now as one repair act (verbatim: "Yes, repair them").
- [operator-ruled] Push the repair commits (verbatim: "Push them").
- [operator-ruled] Post the drafted review on GHI 1267 (verbatim: "Post it").
- [agent-chose] Held the coarse unmapped key, the handler-module public-class rule and dynamic or past-root relative imports on the discrepancy line instead of changing them, since each changes the ruled baseline shape or the canon.
- [agent-chose] Kept row 64f Mechanical and narrowed its evidence to what is witnessed, with the unwitnessed limits named in the row.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's own id.
2. Ask whether the operator renews the expired MX lease (uv run gz mx renew --attestor g0).
3. Ask for the placement ruling that closes GHI 1267: which live core/ and ontology modules the package map puts in the domain region, and whether the req_kind_support -> validate_cmd edge is removed by an injected scope runner or held as a named finding.
4. Ask which work moves next among RP-7's hexagon test gates, RP-7's held rulings H1 to H14, the hexagonal run's row 7 follow-on runs, routing GHIs 1318 to 1324, and observing the ratchet-drawdown workflow's first run on GitHub.

## Pending Work / Open Loops

GHI 1267 open: core/ unmapped, the req_kind_support -> commands.validate_cmd edge unwitnessed, no planted-chain test through a mapped domain module. On the tranche 6 discrepancy line: the unmapped key names the highest unmapped ancestor so growth inside a held package adds no finding; every public class in a handlers module is held to the handler rule, which canon does not state; dynamic imports and relative imports past the package root are not judged. The tranche 6 line stays open until cleared with the alarms on. The ratchet-drawdown workflow has not yet run on GitHub. GHIs 1318 to 1324 open and unrouted. RP-7's hexagon test gates unbuilt and H1 to H14 held. MX lease expired.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD reads 0 0; uv run gz validate --hexagon-dependencies exits 0; uv run -m unittest tests.kernel.test_dependency_checker tests.kernel.test_buses tests.kernel.test_bases tests.governance.test_audit_hexagon_dependencies tests.policy.test_import_boundaries passes; gh issue view 1267 shows OPEN with the review comment; uv run gz obpi lock list shows the mx-session lease state.

## Evidence / Artifacts

- `src/gzkit/kernel/dependency_checker.py`
- `src/gzkit/kernel/buses.py`
- `src/gzkit/governance/trust_audits/hexagon_dependencies.py`
- `tests/kernel/test_dependency_checker.py`
- `tests/kernel/test_buses.py`
- `tests/kernel/test_bases.py`
- `tests/governance/test_audit_hexagon_dependencies.py`
- `.gzkit/rules/hexagonal-architecture.md`
- `docs/governance/advisory-rules-audit.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/user/manpages/validate.md`
- `data/hexagon_dependency_baseline.json`
- Commits 607c663f2 and 81f5a49bf; GHI 1267 review comment issuecomment-6847423606.

## Settled Rulings

2186 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
