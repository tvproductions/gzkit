---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-21T08:34:04Z'
agent: claude-code
session_id: 57346836-b4d2-414f-b5b1-04898f13456f
continues_from: .gzkit/handoffs/20261020T235101Z-mx-renew-landed-ci-switch-parked.md
---

## Current State Summary

Since `.gzkit/handoffs/20261020T235101Z-mx-renew-landed-ci-switch-parked.md`: RO-9 tranche 2 (lock discipline) landed in 16aa7c5f8 and was driven in d1e6f18ca; the Astral witness baseline went from 46 to 14 rows, the rest owned by tranches 3, 4 and 7. RO-3 is specified in `docs/governance/harbor-ro3-requirements-store.md` (3b80a255b), four tranches for a cheaper session. The witness now rejects a requirements*.txt at any depth (a520dc68a). GHI #1264 records the API reference. A full unit run found four tests the per-change gate never selected, repaired in d1e6f18ca. CI is green on d52bc65bd (the first full --locked run, Linux and Windows); origin/main reads 0 0.

## Important Context

- The drydock lease (session 57346836, opened 2026-10-20T22:59Z, 24h) expires about 2026-10-21T23:00Z. Renew with `gz mx renew --attestor g0` through the gz-mx skill when the orientation announces it; nothing else is needed.
- The per-change `gz check` does not select tests that scan a registry or the tree (attestor classification, schema/model parity, type-ignore audit, argv lockstep). Run `uv run gz test` (full unit tier, about 90s) before pushing a change that adds a CLI verb, an event field or a tool invocation (insight scope `gz-check-changed-tests`).
- Read the Docs now installs uv with asdf and syncs `--only-group docs`; that step runs only on a tag build and is unverified until the next release. The install-and-build path was rehearsed locally.
- The GHI #1263 CI switch stays parked in `git stash`; it and the renewal both bumped mx-mode to 1.10.0, so unparking needs a rule bump and a reconcile.
- The operator wants the drydock loop free of fuss: prefer the smallest step that keeps the session moving.

## Decisions Made

- [operator-ruled] Continue the drydock from the handoff (verbatim: "continue drydock"), taken as RO-9 tranche 2.
- [operator-ruled] Specify RO-3 (verbatim: "Next: specify RO-3 (the requirements store) per the handoff order."), with four selections: "One file per kind (Rec.)", "Seed the legend (Rec.)", "Library producer + probe (Rec.)", "Advisory until RO-5 (Rec.)".
- [operator-ruled] An API reference is wanted (verbatim: "Yes, I want an API reference; file a GHI for it through ghi-author.").
- [operator-ruled] No requirements files under strict Astral rules (verbatim: "with strict astral project rules, this should not be used: requirements*.txt" and "strict astral compliance would have zero `requirements.txt` files").
- [agent-chose] The witness gained registered `records` (a module-level table of data, not an invocation) for `RETIRED_STEP_COMMANDS` and `_REQUIRED_RECEIPT_STEPS`, rather than editing a dated history row or reordering a tuple to dodge the check.
- [agent-chose] Read the Docs reads the uv version from `[tool.uv] required-version` with sed, so the version is stated once.

## Immediate Next Steps

1. Renew the lease when the orientation announces it expired (`gz mx renew --attestor g0`, through the gz-mx skill, on the operator's word).
2. RO-3 tranche 1 in a cheaper session, from `docs/governance/harbor-ro3-requirements-store.md` § Tranches: the read seam admits `catalog/`, the three files with schemas and models, the legend seeded, `gz validate --catalog` with the structure checks.
3. Then the predecessor's order: GHI #1259; RO-9 tranches 3 to 7 follow in order.
4. When the operator chooses: GHI #1264 (the API reference; its scope question is the operator's), GHI #1262 (debt reading), GHI #1263 (parked).

## Pending Work / Open Loops

- GHI #1264: API reference, open; which modules count as the API is the operator's call.
- GHI #1262: debt reading names what the demoted checks would refuse, open.
- GHI #1263: CI full-strength switch, parked in git stash.
- RO-3 tranches 1 to 4 and their four known uncertainties (the freeze lock's event, `depends_on` non-outcome targets, § 7 attribute ids, the delivery-event list).
- RO-9 tranches 3 to 7; the Read the Docs asdf step at the next tag.
- The per-change test-selection gap (insight scope `gz-check-changed-tests`), a neighbour of GHI #1240.
- 30 overdue chores, carried.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads `0 0`; `gh run list --limit 1` shows CI success on d52bc65bd or later.
- `uv run gz validate --astral-discipline` exits 0; `data/astral_discipline_baseline.json` holds 14 rows.
- `uv run gz obpi lock list` shows the mx-session lock for 57346836.
- `git ls-files | grep -ic 'requirements.*\.txt'` prints 0.

## Evidence / Artifacts

- `docs/governance/harbor-ro3-requirements-store.md`
- `docs/governance/harbor-ro9-astral-toolchain.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `src/gzkit/governance/trust_audits/astral_discipline.py`
- `data/astral_exceptions.json`
- `data/astral_discipline_baseline.json`
- `.readthedocs.yaml`

## Settled Rulings

1641 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
