# Patch Release: v0.34.6

**Date:** 2026-08-29
**Previous Version:** 0.34.5
**Tag:** v0.34.5

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 787 | gz check: _build_check_steps' coupling checklist names 4 obligations, 8 are required | qualified |  |
| 856 | arb: canonical unittest invocation is serial while every gate runs it parallel (3.05x) | qualified |  |
| 872 | session-start: resume advisement omits the behind-origin caveat | qualified |  |
| 875 | corpus_store: append_entry persists before validating, so an invalid corpus reaches disk | qualified |  |
| 876 | brief-reconcile: allowlist globs compared literally, so declared scope reports as drift | qualified |  |
| 879 | obpi precomplete: adversarial_validation reports READY on a REFUTED verdict | qualified |  |
| 880 | corpus_store: concurrent appends silently drop rows from canon | qualified |  |
| 881 | corpus_store: append_entry truncates before writing, so a failed append can destroy canon | qualified |  |
| 882 | ledger validator: no conditional rules, so a gate's own condition cannot be asserted | qualified |  |
| 883 | ledger: the two canonical readers disagree on null and on array item types | qualified |  |
| 884 | obpi complete: tier-1 proof reads argv[0], so the mandated plugin dispatch can never satisfy it | qualified |  |
| 885 | corpus: hand-written tombstones retire canon with no ledger witness | qualified |  |
| 886 | pipeline: Stage-2 dispatch state lives only in the Layer-3 marker, so clear-stale destroys it | qualified |  |
| 887 | pipeline: no blocked-on-operator state, so a brief awaiting a ruling keeps buying adversary rounds | qualified |  |
| 890 | gz validate writes 102 canonical files, so 4 gate steps must wait on it | qualified |  |
| 891 | sync_all: still writes on drift, so validate cannot become read_only | qualified |  |
| 892 | sync_all: one pass does not converge, so skill mirrors are a generation stale | unclassified_reference | GHI #892 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 893 | sync parity: persona mirrors are generated but absent from SURFACE_ROOTS | qualified |  |
| 895 | obpi complete: wrapper allowlist is unwitnessed, so bun refuses tier 1 | qualified |  |
| 896 | cli-alignment: skill prose cites 3 src paths that no longer exist | qualified |  |
| 899 | authorship: operator's name ships in the wheel's --help examples | qualified |  |
| 900 | chores/skills: wheel ships defaults that resolve only on one machine | qualified |  |
| 901 | tests: three probes assume POSIX mode and ctime, so Windows CI is red | qualified |  |
| 902 | pre-commit hooks: repo scanners walk 367k paths against 7,241 tracked files | qualified |  |
| 903 | check step timings: attention-routing record is 7x stale on one step | unclassified_reference | GHI #903 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 904 | gz check: Test idles 33s behind a writer phase it has no edge to | qualified |  |
| 905 | gz check scheduler: the producer/consumer edge it preserves is not implemented | qualified |  |
| 906 | gz check: Behave is single-threaded, and shards 3.5x across processes | qualified |  |
| 908 | gz init: the tree it scaffolds fails gz validate --surfaces | qualified |  |
| 909 | sync_all: writes depend on process cwd, not the project_root it is given | qualified |  |
| 910 | gz init: scaffolded pyproject names a README it never creates, so uv cannot build the tree | qualified |  |
| 911 | gz init: scaffolded rules carry gzkit's own paths, so every adopter fails gz readiness audit | qualified |  |
| 912 | reachability audit: an unpopulated young project reads the same as an unsatisfiable glob | qualified |  |
| 913 | doc-coverage: gzkit's docs layout is asserted against adopter trees | qualified |  |
| 914 | hook formatter: a failed format is indistinguishable from a clean one | qualified |  |
| 915 | skills: the delivery boundary fences rules and chores, not skills | qualified |  |
| 916 | behave: a scenario's mock.patch leaks and arms the next scenario's preconditions | excluded |  |
| 917 | behave shards: non-recursive glob would drop nested feature files | unclassified_reference | GHI #917 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 918 | justify_steps: gh patcher teardown is defined but never called | unclassified_reference | GHI #918 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |

## Operator Approval

Approved by gz patch release
