# Changelog

All notable changes to gzkit are recorded here. This is the *exhaustive,
developer-facing* record of every user-visible change; the curated
*why-it-matters* narrative for each release lives in
[`RELEASE_NOTES.md`](RELEASE_NOTES.md). The two are distinct artifacts and never
collapse into each other.

Format adapted from the [Good Docs Project changelog
template](https://www.thegooddocsproject.dev/template/changelog). Versions follow
Semantic Versioning; dates use the ISO `YYYY-MM-DD` format. Because gzkit commits
to `main` and tracks work by GitHub Issue (GHI), **every entry cites its
`GHI #N`** in place of the upstream template's pull-request link. Each version's
entries are the derived projection of the GHIs closed since the previous tag.

Canonical shape: `.gzkit/templates/changelog.md`. Discipline: `.gzkit/rules/changelog-release-notes.md`.

## [Unreleased]

## v0.34.8 (2026-10-01)

### Release highlights

- Gates that reported green without holding now fail when their condition fails: receipt and verdict checks at OBPI completion, `gz validate --json`, `gz tidy`, plan-audit containment, the docs dead-link gate and the `Task:` trailer at push (GHI #889, GHI #960, GHI #995, GHI #1124, GHI #1057, GHI #803, GHI #1017)
- Ledger writes are serialized with crash-safe recovery, merged by a ts-ordered driver, and correctable append-only through `gz ledger correct` (GHI #953, GHI #1074, GHI #1075, GHI #611)
- `gz init` repair and `--update` stop writing what they did not report and detect local edits; skills ship with their references; plain `gz check` is the per-change gate and `--full` adds Behave (GHI #1098, GHI #1123, GHI #1122, GHI #1108, GHI #1088)

### Added

- `gz ledger correct` appends a corrective action against any prior ledger row, addressed by its `(event, id, ts)` triple, with three dispositions: `void` (the row was never true), `discharged` (true when written, its condition has ended) and `reinstated` (clears a prior correction); `gz ledger corrections` lists the rows currently voided or discharged. Netting happens at the reader boundary, so the artifact graph, replay, `gz validate --ledger` and `red_parity` read one correction contract and original rows stay byte-intact. `gz validate --producer-fields` scans every `LedgerEvent(` construction site against both ledger contracts. Partial: the primitive landed and has been applied to live rows; moving `gz obpi repudiate` and the park/unpark and block/unblock verb pairs onto it remains open (GHI #611)
- `gz arb red --commit <sha>` witnesses a direct-fix commit: each production hunk it added is reverted to the parent's text in turn and the commit's own test modules are run through `gzkit.mutation_witness`, reporting driven, undriven (exit 1), no-tests (exit 1), inconclusive or no-production-hunks; `ghi-close` step 7c runs it on the fix commit (GHI #927)
- `gz obpi verify-packet` re-executes every `$` transcript in a Step-4a attestation packet and blocks on any pasted line the command did not produce, on a non-zero exit, on a printed non-zero exit status the packet leaves out, and on a trailing no-op suffix (`; true`, `:`, `exit 0`) that hides a failure; abridging and `...` elision of output that cannot reproduce remain allowed (GHI #942)
- `gz-how` replaces `gz-skill-router` as the catalog-wide flow guide, answering "how do I …?" and "what can I …?" across 18 flows with look-alikes, operator-only steps and next steps; `gz validate --how-coverage` (default tier) fails when a live skill is neither catalogued nor excluded with a reason, and `AGENTS.md` § SKILLS FIRST routes unclear skill selection to it (GHI #1106)
- `gz chores status [--json]` reports each registered chore's currency band (overdue / due / unmeasured / paused / current) from its class declaration and CHORE-LOG PASS blocks, exiting 0 in every band; session orientation announces due and overdue chores; `staleness.surfaces` is declared for all 30 content-delta chores and `scripts/check_proof_freshness.py` reads that declaration instead of its own five-chore map (GHI #936)
- `gz obpi adversary-workspace` materializes a throwaway copy of the reviewed source (tracked HEAD plus uncommitted changes), and Step 4b dispatches the Codex adversary through `task --write --cwd <checkout> --prompt-file <file>`, so the reviewer can execute, write and run mutation sweeps while writes to the active repository are refused by the sandbox; the Step 4b pass condition stays "positive behavior demonstrated" (GHI #961)
- A shared mutation-witness harness runs every mutant under its own `PYTHONPYCACHEPREFIX`, since two same-size mutations made within the same second could reuse a stale `.pyc` and a sweep could report a verdict about code it never tested. It grades each mutant as `killed`, `survived`, `invalid` or `inconclusive`, so an import error or harness failure no longer counts as a kill (GHI #963)
- `gz content own <surface> --section <id> --attestor <n> --reason <t>` moves a section from `unowned` to `corpus-owned` once every content line is carried verbatim by a live corpus entry, re-measuring the unowned-byte floor from the successor map. Before this, the only exit was a hand-edited declaration with an unattested ratchet row, which the loader accepted (GHI #974)
- `@enforces(population=...)` plants a claim's negative control at every declared member and requires each finding to name its member, so a witness that checks only a subset can no longer pass its own control. The new `gz validate --population-controls` step in `gz check` inventories undeclared populations against a shrink-only grandfather list of 83 (GHI #1007)
- `.gzkit.json` `authorship.attestor_handle` supplies the default for an omitted `--attestor` on 11 verbs (the seven human-act verbs are untouched, and an explicit value is never replaced); `gz init --attestor-handle` records it, content retire/unown retry remedies print it instead of a fill-in token, and gzkit's own config carries `g0` (GHI #1036)
- `decommission-tautological-tests` gates outstanding tautological-test debt against a declining target (232 ops on 2026-09-28, -20/month, `data/tautological_test_debt_target.json`) rather than only its drift ratchet, which was green at any debt level and logged four PASS receipts across a seven-week stall; `gz check` gains a `Tautological debt` step that exits 3 on breach (GHI #808)
- `gz validate --config-registry` and `data/config_registry.json` give the 17 threshold, budget, roster and policy registries that had no owner a declared owner, verified to actually reference the registry; together with `data/waiver_ratchet_registry.json` the two are exhaustive over `data/*.json`, so an undeclared registry fails closed (exit 3), and a symmetric `relates_to` links registries encoding one concept (GHI #929)
- `codex_delivery_witness.py` measures what Codex actually assembles (`codex debug prompt-input`) and reports it in `gz validate --instructions-files-budget` beside the two authored-number checks, advisory, with an unavailable probe reported as unobserved; the issue's premise that Codex ignores `.codex/config.toml` was false (a trusted directory loads it), and the in-range lowering of `project_doc_max_bytes` to 32768 it licensed is reverted to 65536, under which Codex was measured delivering the whole root contract (GHI #962)
- All 40 registered chores declare class, rung, idempotence, staleness, remediation, non-authority and governing rule in `registry.json`; `gz chores run` refuses an undeclared chore (exit 1), `audit_chore_rung_conformance` fails a workflow step whose stage ranks above the declared rung, `audit_chore_suppression` fails a chore that discharges findings through suppression markers or exit-forcing flags (`chores.md` 0.4.0), and the chores README states what a chore is, its five classes and four rungs (GHI #999)
- `gzkit.settings_vault` reads the `.claude/settings.local.json` backup vault and reports current, drifted, absent or recoverable, and `gz tidy` surfaces the three actionable states; the stdlib-only backup hook stays independent of gzkit, held in agreement by a coherence test (GHI #1072)
- `gz validate --config-registry` also fences derivation and module constants: a new registry recording no authority for its values, either in its own provenance field or as a `derivation` on its `config_registry.json` entry, or a new module-level policy constant, fails closed (exit 3); the 19 registries that record no authority today and the 56 existing constants are frozen as shrink-only baselines; provenance must cite a doc, ADR, GHI or operator ruling, and `$schema` does not count (GHI #1066)
- `gz validate --doc-code-citations` (default tier) fails when prose under `docs/governance/**` cites a `src/gzkit/` module that does not exist, with a single-item skip marker for dated records, superseded-path quotes and prospective specs; of the six unresolved citations it found, the three pointing at moved modules (`cli.py`, `governance/trust_audits.py`, `personas.py`) are repaired to their real homes and the rest are marked as dated, superseded or prospective (GHI #1083)

### Changed

- Plain `gz check` is the per-change gate (scope `change`, formerly `prepush`) and skips `Behave` and `Preflight`; new `gz check --full` runs the full sweep and is exclusive with `--fast`; CI runs `--full`; verification receipts carry their scope, so a change-scope pass satisfies the pre-push gate but never a `--full` request (GHI #1088)
- Instruction-surface diet, partial (rules corpus onboarding remains open under OBPI-0.35.0-12): root `AGENTS.md` is corpus-sourced and generated, with `governance-core.md` folded in and deleted, and measures 25,603 B against 46,876 B in v0.34.7; gzkit's own tree drops its Copilot surface (154 files, 1,015,407 B) and renders Claude and Codex only, and the vendor gate now reads the `vendors` a project declares in `.gzkit.json`, so a declared-disabled vendor is no longer rewritten on every sync (adopter behavior unchanged); `compose()` resolves the content type from the surface registry and fails closed on an unmapped surface instead of grading everything as `AgentContract`; rule version chains are lifted out of the canonical rules into `docs/governance/rule-version-history.md` and the advisory-scorecard grandfather roster is drained to 0; 21 skill-correction commits are followed by a new `skill-authoring.md` rule stating the standard skill bodies are written and reviewed against; chore criteria name the parallel `gz test` runner (GHI #921)
- The canonical coverage step runs `unittest-parallel --coverage --coverage-source src/gzkit` instead of serial `coverage run -m unittest discover`: 493 s to 307 s over 10,467 tests with identical totals in one measured run; `gz arb coverage` with no arguments runs the canonical argv, and serial-form receipts recorded before the switch stay valid (GHI #1027)
- `gz agent sync` no longer generates a nested `CLAUDE.md` importer beside each subtree `AGENTS.md`; Claude already received those rules through `.claude/rules/*.md`, so each loaded twice (307,139 B duplicated), and the stale sweep reaps the 24 existing importers while nested `AGENTS.md` stays Codex's channel. Reverses the remedy ruled under #923 (GHI #1021)
- `gz-obpi-pipeline` 6.59.0 gathers Stage 4's seven pass-condition statements under one heading that defers to `gz obpi acceptance ... status --stage stage4`, adds a review window freezing the subject between 4a and 4b, bounds the loop at two follow-up rounds before `gz obpi block`, and dispatches Step 4b through the plugin's `task --write` path instead of `adversarial-review` (GHI #1028)
- Handoff resume resolves an ADR cited by its full id from its recorded closeout lifecycle (`Ledger.derive_adr_semantics`) rather than reporting UNKNOWN, so an ADR whose children are all attested but whose closeout was never recorded stays live; a citation by version prefix alone still reads unknown (GHI #1078)
- `Ledger.read_all`, `read_evidence` and the rename map are cached per instance and invalidated on append, so `canonicalize_id` no longer re-derives them on every call (20.35 ms per call across 2691 calls in one `gz validate --frontmatter` run, 55.44s and 97.9% of `Validate default scopes`; in-gate the step fell from 65.29s to 2.80s) (GHI #1080)
- `gz arb red --commit` falls back to statement-level mutants when a whole-hunk revert cannot be graded: each guard statement in the hunk is replaced with `pass` and graded as a `unit: statement` row, and a hunk with no guard becomes an ungraded `declaration` row, so helper-plus-caller and signature changes grade instead of reading inconclusive; the witness also sweeps the committed blob text, so CRLF checkouts on Windows no longer make every mutation target absent (GHI #1153)
- The ascending-semver ADR order exempts corrections re-homed from a Validated ADR, which previously had no permitted home; the exception is carried verbatim at all five skills holding the ruling (`gz-obpi-pipeline`, `gz-adr-create`, `gz-design`, `gz-plan`, `gz-status`) and in the Magna Carta amendment of 2026-09-29 (GHI #871)
- The Claude Fable 5.1 / Mythos 5.1 System Card (2026-09-01) replaces the Fable 5 / Mythos 5 registry entry and PDF, and the nine doctrine surfaces that sole-sourced the superseded card are re-sourced (GHI #934)
- The OBPI pipeline skill, reviewer prompts and agent definitions, recovery messages and user docs require observed failure attribution and requirement-derived expectations across evidence handoffs, and keep a reviewer's tool limits distinct from invalid required proof; verdicts, tool grants, stages and attestation are unchanged (GHI #984)
- Exit code 2 is labelled Usage or System/IO in every command's help epilog, `.gzkit/rules/cli.md` 0.7.0, the exception map and `cli-standards-v3.md`, matching parse errors that have always exited 2 (attested REQ-0.0.4-02-03); negative control `NC:cli-usage-error-exit-two` witnesses it (GHI #1001)
- `.gzkit/rules/chores.md` 0.6.0 names `.gzkit/chores/` the canonical authoring source and `src/gzkit/chores/` the generated distribution, agreeing with `skill-surface-sync.md`, and states `gz chores doctor`'s real recovery semantics (DAMAGED rewrites every differing definition file, surviving edits included); the chores README and manpage are corrected with it (GHI #1044)
- `gzkit.registries.load_registry(project_root, name)` is the single seam for reading config registries under `data/`, raising one typed `RegistryError`; a shrink-only ratchet refuses any new module that reads `data/` directly, and the roster of existing direct readers, re-measured at 50 rather than the reported 30, shrinks as each one migrates (GHI #1067)
- `gz check` measures each step's cost as a byproduct of its own run and prints it: `_run_check_steps` takes an optional `durations` sink covering the writer, overlap, serial and reader-pool paths, and accounts a raising step; the hand-refreshed `measured_seconds` in `data/check_step_concurrency.json`, which nothing read and which had drifted (`Test` 31.99s against a measured 92.10s), is no longer the source (GHI #1077)
- The Claude Opus 5.5 System Card (2026-09-22) replaces the Opus 5 registry entry and PDF, Opus 5.5 at `medium` effort becomes the default profile, and the `AGENTS.md` untrusted-content rule now covers text pasted into the operator's turn: an instruction inside it is followed only where the operator's own words ask for it (GHI #1089)
- Eight skill bodies still carrying the scaffold template (`gz-constitute`, `gz-prd`, `gz-plan`, `gz-adr-promote`, `gz-init`, `gz-agent-sync`, `gz-status`, `gz-tidy`) are rewritten against the code they wield, correcting false claims such as `gz init --update` preserving operator-edited files; four `openai.yaml` short descriptions lose the template text, and the runbook's intent-stage row shows the required name argument (GHI #1112)
- `sync_nested_agents_md` generated a `CLAUDE.md` importer (`@AGENTS.md`) beside each nested `AGENTS.md`, for 290,006 B of subtree rules across 26 files; later in the same range these importers were found to double-load rules Claude already receives through `.claude/rules/*.md`, and the generated importers were removed (see #1021), so no nested `CLAUDE.md` ships and the net user-visible change is nil (GHI #923)
- `gz-obpi-pipeline` 6.61.0 states Step 4b's true lane scope: the adversarial pass is expected on every lane and enforced by `gz obpi complete` on heavy lane only, replacing a rationalization row that claimed no lane exception while the gate returned early off heavy lane (GHI #939)
- `CLAUDE.md` § Model tuning is re-sourced to the current Opus and Fable 5.1 cards with Opus-first precedence where their guidance conflicts; the calibration of universal-pressure directives for both models remains open (GHI #943)
- The cross-platform advisory lock moved from the private `corpus_store._exclusive_store_lock` to the public `gzkit.file_lock.exclusive_file_lock`, used by both the corpus store and section ownership; pure relocation, with tests asserting mutual exclusion between the two callers (GHI #945)
- Reviewer persona descriptions in `.claude/agents`, `.gzkit/agents/roles.json` and `.codex/agents/*.toml` state the enforced grant (no execution) instead of 'read-only', and `gz-obpi-pipeline` assigns proving a test can fail to the orchestrator via `gzkit.mutation_witness` (GHI #968)
- `gz-session-handoff` 7.4.0 § CREATE directs authors never to restate an inherited ruling in `Decisions Made`, to seat a ruling that arrived after the predecessor with `--settled`, and to check `gz handoff rulings --search` before writing an `[operator-ruled]` entry; advisory guidance only, since ruling identity is not yet modelled (GHI #1003)

### Fixed

- The generated `.codex/config.toml` sets `project_doc_max_bytes = 65536`; at Codex's 32768-byte default, 14,108 B of `AGENTS.md` (30% of the contract, the operator's verbatim canon included) was silently truncated. `CodexDocCapCoherenceTest` holds the generated value and `data/vendor-manifest.json` to one number; the render-order residual moves to ADR-0.35.0 item 13, with its permutation ruled to require operator attestation. Closed as premise withdrawn once the cap and the `AGENTS.md` rewrite left 45,664 B of headroom (GHI #815)
- `gz arb red` resolves its base from the covering test's own history (`git log -S '@covers("REQ")'`, taking the parent of the introducing commit), so the falsifiability witness runs on `--from=verify` instead of returning `not-applicable` on every landed REQ. Each witness records `base_provenance`, and an `error` on a reconstructed base reads INCONCLUSIVE rather than a weak RED, closing the fail-open path; reconstruction is tried before HEAD, so unrelated dirty files no longer yield a false `none` (GHI #849)
- `gz obpi precomplete` reported its receipt precondition met on the existence of any `arb-*.json` in the tree (ok over 3718 receipts, 577 of them failed runs); it now requires the newest lint, typecheck and unittest receipt written since the OBPI's lock claim to record `exit_status` 0, names each missing or red step, refuses without a readable claim, and prescribes the canonical invocations (GHI #889)
- The negative-control runner `rmtree`'d whatever `Path` a fixture returned, and a fixture returning the repository root deleted the working clone; each claim now runs in a runner-created private temp workspace, sanctioned fixture builders allocate beneath it, and only the runner-owned handle controls cleanup, so a fixture-returned path is never a deletion target (GHI #920)
- `Ledger.append` had no transaction boundary: a failed append truncated back to its own size probe and erased a concurrent writer's committed row, and a truncated final row made every ledger read fail while the next append concatenated onto it; append now runs under an exclusive file lock across writers, an unfinished fragment is discarded, and a complete row missing only its newline is terminated in place (GHI #953)
- `gz obpi complete` required `--adversary-resolution` for a `refuted` verdict only, so `refuted-with-caveats` could clear the completion gate with no resolution recorded. The completion command now requires a resolution for both verdicts, as `precomplete` already did (GHI #959)
- `gz obpi complete` accepted `refuted` and `refuted-with-caveats` as completing verdicts whenever `--adversary-resolution` was supplied; both are now refused outright and the OBPI loops to Stage 2, with a block message naming the loop rather than an invalid verdict. Both verdicts stay in the ledger vocabulary for 13 historical rows, and draft OBPI-0.36.0-07 and its parent ADR text are reconciled to the same rule (GHI #960)
- OBPI acceptance derived readiness from narrative state, so re-edited prose or a fresh execution could manufacture or drop obligations; readiness now comes from canonical obligations, executed mutation controls and receipt-bound independent closure, findings survive replacement proof, runtime errors and unexecuted selectors are rejected as behavioral proof, approval is reused only across consecutive successful executions with equal proof claims, and Step 4a packet preparation is separated from Step 4b approval (GHI #985)
- `gz validate --json` returned before exit classification, so every `VALIDATOR_REGISTRY` scope and `--audits` exited 0 on failure while the payload read `"valid": false`; one `_exit_for_errors` helper now serves both renderers, and a parity table fences the solo early-return scopes (GHI #995)
- `gz validate --evaluation-justify-binding` accepted any file whose name matched the evaluated id, so an empty file satisfied required reasoning. A walkthrough now qualifies only if it parses, fills every section, names its subject in frontmatter and postdates the evaluation; refusals name each rejected candidate and a producer step that works (GHI #996)
- The mandatory `Task:` trailer had no automated witness: `gz validate --commit-trailers` was registered explicit-only and read HEAD alone. It now runs in the default `gz check` scope and reads every commit in `@{upstream}..HEAD`, so a trailer-less `src`/`tests` commit beneath a git-sync chore commit is caught; the eval-feedback trailer check reads the same range. The pre-push `--reuse-verified` skip, which matched on tree content and so never read a commit made after the verifying run, now consults the trailer checks and the task-envelope trailer channel before skipping (GHI #1017)
- `gz plan audit` containment returned True after every failed comparison, so a plan path outside the brief allowlist always passed; out-of-allowlist paths now produce a scope gap, a FAIL receipt and a non-zero exit, absolute paths and project escapes fail, and `CREATE` cannot grant scope (GHI #1057)
- The ledger merge driver read an addition inserted between ancestor rows, the ordinary output of a ts-ordered merge on another clone, as rewritten history and refused it, leaving a conflict only a hand-edit could resolve; ancestry is now tested by membership and additions are placed at their timestamp, while an edited, removed, unsortable or out-of-order ancestor still refuses. `gz validate --ledger` now fails on duplicate rows, compared by content regardless of key order, with the one live duplicate waived by content hash (GHI #1075)
- `gz init --dry-run` printed "no files written" while it rewrote canonical skills and chore files (the scaffolders ran with `skip_existing=False`), and the real repair changed 12 tracked files it never reported; a dry run no longer calls either scaffolder, repair plans its sync with `plan_sync_changes` and reports each file as `Would sync` or `Synced`, and skips `sync_all` when nothing would change (GHI #1098)
- Only `SKILL.md` reached the wheel and `gz init` scaffolds, so shipped skills' `references/` and `assets/` files were missing and links in `ghi-author`, `gz-obpi-pipeline`, `gz-adr-create` and others were dead; sync now packages every `*.md` under a shipped slug and `scaffold_core_skills` writes them (17 newly shipped files) (GHI #1108)
- `gz init --update` byte-copied every wheel file on five surfaces: it overwrote `chores/registry.json` (dropping every `projectLocal` entry), wrote package-only templates into `.gzkit/templates/`, and in an adopter misclassified newly shipped chore slugs and scripts as package-only so they were never delivered; each surface now routes through its delivery classifier and the registry is merged (GHI #1123)
- `gz tidy` exited 0 with 456 findings, printed "Project is tidy" over an actionable notice, and never read `--check`. Validation issues, orphaned OBPIs and an actionable settings vault now exit 3, ADRs pending attestation are listed without gating, `--fix` is judged on the tree it leaves, and `--check` and `--fix` are mutually exclusive (GHI #1124)
- `mkdocs build --strict` passed with dead links because `mkdocs.yml` set `validation.links.not_found: ignore`; the level is now `warn`, the docs gate refuses to build when `nav.not_found` or `links.not_found` is set below its floor, and the 226 dead-link warnings that surfaced were cleared to 0 by repairing, repointing or unlinking the links and excluding generated agent files and a template from the docs build (GHI #803)
- The session-green gate's delivery witness checked `pre-push` alone while `.pre-commit-config.yaml` declares four hook types, and its only negative control never reached the delivery arm; it now checks every declared hook type plus `pre-push` (a missing recording hook is advisory, any other fails closed), and `gz init` installs the same declared list (GHI #851)
- 373 of 15,922 committed ledger rows could not be read by `parse_typed_event`; two authored event models are wired into `TypedLedgerEvent` and producer-written fields are declared, taking the count to 0, and new `gz validate --producer-fields` AST-scans every `LedgerEvent(` construction site against both contracts, catching two undeclared `airlock_out` fields no committed row could have exposed (GHI #877)
- A SUPPORT REQ's proof channel came from a substring scan of its whole body, so a REQ stating that an event was absent read as citing it; the channel is now one explicit clause, ``Witnessed by `<event_type>` [citing `<path>`] + `gz validate --<scope>` ``, and an ambiguous or missing declaration is rejected as `undeclared-support`. The population was measured first: all 13 live SUPPORT REQs were migrated, and sealed briefs were left unchanged as historical records (GHI #888)
- The verifier pipe gate refused `verifier | tail` but allowed `verifier > log; tail log`, which also discards the verifier's exit status. `masked_verifier` now refuses a trailing statement that hides the status, in both the Bash hook and the Step-4a packet verifier, and still allows one that reports it (`; echo "REAL EXIT: $?"`) (GHI #940)
- Rich parsed bracketed text in operator output as markup and deleted it, so every failing `gz validate` line lost its `[error_type]`, and `gz check`'s CI relay re-parsed child output and ate the same tokens; `escape()` is applied at 15 data brackets across 8 modules, 59 free-text render sites across 33 modules and 12 further sites a widened roster surfaced, captured subprocess output prints with `markup=False`, and three ratchets fence the class (GHI #944)
- Session-exit bookmarks recorded the harness's absolute transcript path, carrying the operator's home directory, username and project slug into a repo-bound artifact; `_portable_transcript_reference` now records only the transcript's file name (`<session_id>.jsonl`), for POSIX and Windows paths alike (GHI #951)
- The verifier-pipe gate read the separator ending the verifier's own statement, so `gz check && echo ok; ls` and `gz check && echo ok || echo x`, which both exit 0 on failure, were admitted; it now reads the separator ending the AND-OR list, stops honoring `$?` after `&` as an escape, gives the `&` arm its own `background` recovery, and reads every stage once `pipefail` is set (GHI #971)
- `load_declaration` accepted an ownership declaration whose `floor_event_id` named any earlier event in its attested chain, silently reverting every later attested transition in either direction; the witness must now be the chain tip, and the four-field journal exemption added alongside it is removed, since a pending recovery journal proves the declaration is not current (GHI #979)
- The `windows-latest` CI leg had been red on every push with 14 failures. Stage-4 transcript replay now runs Git for Windows' bash (refusing the WSL launcher) through an argv, where `cmd.exe` had swallowed `;` and `$?` and let the verifier report a fabricated transcript; ledger-durability tests observe the directory barrier rather than POSIX `fsync`; the kill test falls back to `os._exit(137)`; and every fixture git spawn pins `core.autocrlf=false` (GHI #982)
- The mutation-witness parser expected unittest's status on the test-id line, but a docstring moves `... ok` to the next line, so a green baseline read as red and `gz obpi acceptance prove` returned `valid: false` for any REQ whose covering test had a docstring (4,443 of 10,069 methods, 44.1%) (GHI #986)
- `gz obpi pipeline` recorded `pipeline_launched` but left the brief's frontmatter at `Draft`, so every in-flight OBPI failed `gz validate --frontmatter` and blocked every push; launch now advances that one brief through `guarded_obpi_status_write`, and the frontmatter failure names its recovery command (GHI #992)
- A non-executing Stage-2 reviewer could record a confirmation of evidence that did not exist; `gzkit.acceptance.review.v1` gains `grounds` citations (`proof_id`, path, verbatim excerpt), and `record_review` refuses a citation whose excerpt is under 20 characters or absent from the cited file or evidence, and an uncited approval from a reviewer that cannot execute, appending nothing (GHI #994)
- The verifier pipe gate admitted `(uv run gz check); ls` and `{ uv run gz check; }; ls`, each of which exits 0 over a failing verifier; a subshell or brace group is now read as one command whose status is the verifier its own list carries, with an `errexit-suppressed` arm for a group that is not last in its AND-OR list (`tests.md` 0.25.0) (GHI #1008)
- `configure_logging` was never called, so structlog wrote to stdout and corrupted `--json` output such as `gz chores status --json`, and 13 `--json` sites rendered through the Rich console, which wrapped, colored and stripped `[...]` spans; `main()` now configures logging to stderr and every `--json` site prints the raw document; verbosity follows the CLI spec (default WARNING, `--verbose` INFO, `--debug` DEBUG) and the shared CLI error handler writes to stderr (GHI #1010)
- `gz closeout` hardcoded `from_state="Proposed"` and appended `Proposed -> Completed` (a pair `ADR_TRANSITIONS` forbids) straight to the ledger, 62 of 62 times, and nothing recorded `Accepted`; the pipeline now records the parent ADR `Accepted` through `LifecycleStateMachine` at launch, closeout plans from the actual state and exits 1 on an illegal pair, a Proposed ADR with launched children catches up with cited evidence, and a dropped ADR ends `Deprecated` (GHI #1014)
- Settings sync replaced the whole `enabledPlugins` value with gzkit's single declared entry, so a project-enabled plugin vanished at the next control-surface sync with no signal; keys named in `_PER_KEY_MERGED_SETTINGS` now merge entry by entry, gzkit still winning on the entries it declares (GHI #1070)
- Ledger `ts` was stamped when an event was built, outside `append`'s write lock, so concurrent writers could commit rows in descending order, which `gz validate --ledger` refuses. `append` now stamps an unstated `ts` under the lock, and a new fence test forbids production constructors from stating `ts` outside an explicit allowlist; on its first run it found `gz content unown` replaying a journal's stale stamp (GHI #1074)
- The commit-locus recorder printed 'recorded 1' and then lost its row when pre-commit's post-commit stash restore conflicted with unstaged ledger rows; it now installs as `post-commit.legacy`, which runs before the stash, via `gz init` or `uv run -m gzkit.hooks.commit_ledger --install`, and the session-green gate counts post-commit as delivered only when that recorder is installed and executable (GHI #1092)
- `gz obpi present-evidence` and the `gz obpi complete` re-run executed `## Demo` commands in the live repository, so a writing Demo overwrote a recorded operator attestation with `demo` and appended an irremovable ledger row; Demos now run in a temporary copy of the working tree and are refused, never run live, when no copy can be made (GHI #1093)
- `gz validate --red-parity` could never pass a BEHAVIOR REQ whose code landed before `gz arb red` ran, and refused an attested OBPI at push; a valid executed acceptance proof with at least one killed mutation control now counts as the falsifiability witness, while a `none` RED finding is never erased and void witnesses stay excluded (GHI #1094)
- The unit suite went red on 2026-09-26 with no code change, and `gz agent sync` refused wheel content more than 90 days after its author reviewed it, because three readers measured `last_reviewed` against the machine clock. Review age is now judged only by `gz skill audit` and Gate 3, `audit_skills` takes a `today` date, and the duplicate 90-day constant is gone (GHI #1099)
- `gz tidy --fix`, `gz init` repair and `gz init --force` reached `sync_all` without the canonical preflight, copying corrupted canonical skills into every vendor mirror and exiting 0; every propagating command now routes through `sync_guard`, and a refused `gz init` repair still lists the writes it made before exiting 1 (GHI #1100)
- `gz obpi brief-drift --apply` appended allowlist paths and `## Tracked Defects` notes into terminal-status briefs; it now exits 3 before any write or ledger event on all eight terminal statuses, with `--dry-run` refused too so the preview predicts the refusal (GHI #1115)
- 87 ledger rows sat under 21 bare ids that nothing migrated; airlock enter/exit, `gz obpi lock` and `gz adr evaluate` now record the slug id (which also stops a second agent claiming a brief under its slug while another holds it), the justify-binding reader folds renames, and `gz validate --pending-renames` (default tier) fails on any unmigrated pair; the 21 pairs are migrated (GHI #1118)
- `gz init --update` keyed operator-edit detection on a `<!-- gzkit-canonical-version -->` marker nothing wrote, so an edited scaffold read STALE and could be overwritten; detection now uses a content-hash history shipped with the wheel, scoped skill routers are recorded in their delivered form, and `gz upgrade` shares the path (fresh adopter: `IDENTICAL: 252 STALE: 0 EDITED: 0`; an edited rule exits 3 as a conflict) (GHI #1122)
- A hung unit tier blocked the pre-push gate indefinitely; `run_command` now bounds every quality-gate command by `src/gzkit/quality_command_timeout.json` (900s, shipped in the package, fail-closed if missing or malformed), kills the whole process tree on expiry, and fails with exit 124 naming the command and keeping its captured stderr (GHI #1143)
- `gz task envelope diagnose` reported layer-drift whenever one discovery channel was a strict subset of another, while `gz validate --task-envelope-coherence` reported none; both now read one shared drift predicate, and `task-discovery.md` 0.9.0 states that a channel merely behind is not drift (GHI #820)
- `gz handoff resume` walked a handoff's `continues_from` lineage and then discarded it, dropping 19 ancestors and 104 authored next steps on the live anchor; resume now renders ancestors oldest-first, the SessionStart advisement names the predecessor a CHECKPOINT chains from, and `ResumeResult.chain_truncated` qualifies a depth-bounded walk instead of presenting it as complete (GHI #870)
- Superseding an amendment republished the original corpus wording beside the newest: `[X, S1(supersedes=X), S2(supersedes=S1)]` folded to `[X, S2]`. A `supersedes` row now retires its target permanently and un-retirement is scoped to pure `retires` tombstones, so a chain of any length folds to its newest row (ADR-0.35.0 fold algebra amended) (GHI #873)
- Two corpus rows could share an `id`, and the id-keyed readers silently collapsed them, so a content row could leave canon unseen; entry-id uniqueness is enforced at the single corpus validation seam, and a duplicate never reaches disk (GHI #874)
- `gz validate --ledger`'s conditional `attestor` rule on `corpus_entry_retired` asserted non-empty while `gz content retire` requires a named attestor, so a row with `attestor: "."` validated clean; both now share one `is_named` predicate (GHI #894)
- `gz init` kept scaffolding a Copilot template into new projects after the Copilot drop; the Copilot vendor config, path keys, manifest-schema keys, hook adapter, templates, persona renderer, `SURFACE_ROOTS` entries and sync functions are removed, `ADR-pool.vendor-alignment-copilot` is Superseded, and `.github` now takes its sibling `CLAUDE.md` redirect like any other rule-scoped subtree (GHI #924)
- ADR Feature Checklist ticks were parsed away and read by nothing, so a row could claim a completion that contradicted the ledger. The box stays as a row marker with `[ ]` as its only legal value: `[x]`/`[X]` fail `gz validate --documents`, including on grandfathered Validated ADRs, and the 58 ticked rows across 11 ADRs were cleared (GHI #928)
- The pointer-integrity back-pointer check was a bare substring test, so one `<!-- lifted-from: -->` comment anywhere in a destination satisfied every pointer into that file; each comment is now parsed and one must name the `<source-path>#<anchor>` of the pointer under validation (GHI #932)
- The `frontier-model-card-currency` chore checked registry shape, never currency, and passed while a tracked card had been superseded; an elapsed-time arm now gates it on a 30-day interval dated from a declared scan record (`staleness.artifacts`), which an overdue chore clears only by performing its scan and which a hand-written heading or an in-period bare run cannot reset; `gz chores status` reads the same record (GHI #935)
- `gz check-config-paths`, a proof command, had exited 1 for an unknown period on unmapped `.github/` path literals; the scanner now credits `PathConfig` defaults as config coverage (exactly, so an undeclared sibling stays flagged) and credits literals a module declares as audit subjects in `_AUDIT_SUBJECT_LITERALS`, taking it to 0 findings, exit 0 (GHI #938)
- A reviewer granted `Read, Glob, Grep` returned CONCERNS for checks it had no tools to run; `ReviewResult` gains `verification_gaps`, so coverage gaps stay out of `findings` and the verdict, and both review composers disclose the reviewer's tool grant as read from its agent definition, failing safe to no-execution when the definition is unreadable (GHI #941)
- `gz task envelope diagnose` rendered the frontmatter `tasks:` channel empty for every OBPI whose brief carries a full-slug `id:`, and silently dropped that channel from the drift comparison; it now resolves on either spelling of the OBPI id, and promoting `extract_bare_obpi_id` to public shrank the private-import roster by two (GHI #946)
- `gz validate --task-envelope-coherence` required a `task_id` on `artifact_edited` rows, whose producers take no `task_id`, so one such row blocked every push with no repair path; `artifact_edited` leaves the worklog roster, and an `attested` row without a `task_id` under a live TASK still fails (GHI #947)
- `gz obpi precomplete` failed any Step 4b section recording a refuted round, even one later discharged, leaving a converged review no exit; a brief now declares `**Standing verdict:** <verdict>` on its own line, believed in both directions: a declared refutation still blocks, conflicting declarations are refused, and an undeclared section keeps the fail-closed behaviour (GHI #964)
- `gz obpi present-evidence` split a multi-line `## Demo` command into one command per line, so a quoted `uv run python -c '...'` probe ran as fragments (exit 2, then exit 127s) and the packet read NOT-ATTESTABLE; continuation lines are now joined before execution (GHI #965)
- `gz adr status` annotated closeout blockers with tracked defects read from the brief's authored token, so a GHI closed 33 days earlier rendered as live; state now resolves through the `ReferenceChecker` port as `(open)`, `(closed)` or `(unresolved)` when `gh` is unreachable, with the authored token kept as `authored_state` (GHI #966)
- `gz preflight` treated any mention of an OBPI in a plan as ownership during discovery but required the full slug when detecting orphans, so a FAIL receipt orphaned itself. Ownership is now declared (filename, H1 or `**OBPI:**` label), and `--apply` archives an orphan receipt with a sha256 and provenance sidecar, verified before the original is removed and failing closed, instead of unlinking it; the verdict is left unresolved (GHI #967)
- A `||` suffix let a Step-4a packet present a failing verifier as green with zero blockers; `||` joins the shared `_MASKING_SEPARATORS` predicate, so the Bash hook and the packet verifier both refuse a command whose exit status a `||` branch replaces (GHI #970)
- Eight declaration-damage refusals in `load_declaration` prescribed either `gz content unown`, which re-raises the same refusal, or a hand-edit. They now state a conditional recovery and name the blocker where none exists, and the section-coverage refusals direct the repair to whichever artifact drifted, surface or declaration. A pending journal must also continue the ownership chain's current tip, so recovery can no longer mint a second ownership row over a rolled-back declaration and exit 0 (GHI #978)
- Stage-4 packet replay ran under `/bin/sh`, which is dash on Debian/Ubuntu and rejects `set -o pipefail`, so on every Linux runner a packet using the gate's own sanctioned escape was refused as a fabricated transcript; replay now chooses a shell that runs it. This was `main`'s only ubuntu-latest CI failure across 9,891 tests (GHI #981)
- `gz arb step` rejected the `--max-output-chars` flag its documentation mandated; the flag is wired through to the reporter (default 8000-character tail, a negative limit retains everything, zero retains nothing), and the acceptance CLI tests launch real `gz` commands (GHI #987)
- The acceptance `input_digest` hashed `os.environ`, `sys.version` and `platform.platform()`, so the same tree produced a different digest whenever an unrelated variable such as `CI` changed and an independent review could never import; it now hashes only the audited file roster and the contract (GHI #989)
- A handoff's own `[operator-ruled]` decisions reached `.gzkit/handoffs/rulings.jsonl` only when a linked successor was written, so `gz handoff rulings --search` missed the newest rulings (20 of 20 absent in the measured handoff); they are booked when the handoff is written, and a refused create still books nothing (GHI #1000)
- A file directly under `.gzkit/chores/` was read as its own slug, so the orphan guard withheld the shipped `registry.json` from sync and it fell out of step with the shipped chores; surface-level files now belong to no slug and ship through the filtered export, and the generated nested `AGENTS.md` / `CLAUDE.md` are no longer scaffolded into adopters' `.gzkit/chores/` (GHI #1005)
- `gz validate --cli-alignment` read docs, features and skills only, so 8 `gz` chains in 4 chore docs (for example `gz complexity-advise`) resolved to nothing unnoticed; the scope now includes `.gzkit/chores/**/*.md` (minus `proofs/`), `.gzkit/rules/**/*.md` and root `AGENTS.md`, and manpage alignment reads the same enumeration (GHI #1006)
- `gz arb validate` rejected 38 receipts written by gzkit itself: 30 red receipts carrying `base_provenance`, 6 advisor-QC verdicts under an unregistered schema, and 2 step receipts with a negative signal exit status. The schemas now accept all three, and a lockstep test validates a receipt from every writer (GHI #1026)
- `gz content retire` / `unown` remedy strings, the content manpage, quickstart and user runbook, `docs/governance/governance_runbook.md` and the `gz-obpi-specify` OBPI brief template prompted for `--attestor "<your name>"`, `"<Human Name>"` or `[human name/handle]`; those tokens now read `<attestor-handle>` (GHI #1031)
- A brief allowed path written with a leading `./` escaped the generated-vendor-mirror refusal that the bare spelling triggered; the prefix is normalized before mirror classification (GHI #1049)
- The validator-reachability and ledger-inertness ratchets ran only as pre-commit hooks, so `gz check` and CI never ran them; both are now `gz check` steps with refuse and admit controls. A wheel install, which withholds the project-local chores, lists neither step (GHI #1063)
- `gz handoff resume` resolved every OBPI citation as `unknown`; `live_reference_checker` now resolves OBPI citations from the ledger via `obpi_ledger_state`, reading withdrawn and completed OBPIs as settled and repudiated ones as live (GHI #1076)
- Handoff citation resolution looked identifiers up as exact graph keys, but handoffs cite short forms such as `OBPI-0.35.0-08`, so none of 867 OBPI citations resolved; citations now route through `Ledger.resolve_artifact_id` with unique-prefix resolution and an ambiguous prefix refused, raising ADR answers from 288 to 1651 and OBPI from 0 to 397 (GHI #1079)
- `gz git-sync` emitted `Governance anchors touched:` trailers for any identifier-shaped string in a diff (in the measured commit, 6 of 24 named nothing in the graph), and truncated `ADR-0.6.0-pool.gz-chores-system` to a prefix that resolved to an unrelated ADR; anchors now resolve by rename-map collapse, exact membership and a unique prefix, an ambiguous prefix is refused, and the ADR-semver pattern matches whole identifiers only (GHI #1081)
- Handoff resume extracted zero next steps from a section with an inline enumeration after a preamble ("In order: 1. ... 2. ..."), a shape `gz handoff create --next-steps` invites by taking the section as one string; only marked items become steps, so the preamble never does (GHI #1082)
- The `AGENTS.md` REQ-coverage bullet, compressed in the 2026-09-17 diet, read as a universal fail-close that ADR-0.0.25 does not attest; its lane scope is restored through the corpus (heavy lane and foundation kind stop completion, lite warns, `--accept-uncovered` never waives a BEHAVIOR REQ). ADR-0.35.0 gains checklist item 14 and its OBPI brief, which plan a retention map before a promotion drops prior-rendition content (GHI #1090)
- The Stage-2 review prompt asked for both a legacy `ReviewResult` and a `gzkit.acceptance.review.v1` object with conflicting vocabularies, so replies kept failing import and each refusal cost a repair dispatch. The reply is now the acceptance envelope alone, from which `parse_review_result` derives the legacy result, and the frame states the import rules; `verification_gaps` is optional and non-governing (GHI #1095)
- Acceptance review prompts embedded the whole `ReviewContext`, carrying every repair round's proofs forward, so one OBPI's prompts grew from 63 KB to 1.7 MB over nine rounds; they now embed a `ReviewSubject` projection of current proofs and open in-scope findings (the measured spec prompt fell from 1,734,771 to 203,414 bytes), while `status --json` keeps the full history (GHI #1096)
- Neither `@intrinsic_complexity` nor the `--attest-intrinsic` ledger event suppressed a diagnosis: the decorator registry fills only on import and the ledger event was never read back, while the covering tests wrote `_REGISTRY` by hand; `gz complexity advise` and the auto-chain hook now read the decorator from the parsed function node and the attestation from the ledger, and print the attestation instead of a diagnosis (GHI #1102)
- The complexity advisor labelled every crossing no rule matched as `long_parameter_list`, one-parameter functions included, covering all 1,151 guide hints and 1,178 of 2,193 diagnoses over `src/gzkit`. Unmatched crossings now get the new `UNCLASSIFIED` archetype in both schemas (GHI #1103)
- Eight chores shipped to adopters ran acceptance criteria against `src/gzkit/...` or gzkit's `scripts/...` paths absent from an adopter tree; seven gzkit-specific chores are marked `projectLocal`, `pythonic-design-pattern-detection` ships with runnable criteria, and a test refuses any shipped criterion naming `src/gzkit/` or `scripts/` (GHI #1114)
- `gz obpi brief-drift --apply --dry-run` printed only per-dimension counts, so the operator attested amendments they could not see. The preview now lists each line that `--apply` would add or remove, diffed from the same text the write produces, and `--json` gains `planned_amendments` (GHI #1116)
- The whole-repo `--evaluation-justify-binding` scan graded Validated and Abandoned ADRs, so a Validated ADR held the gate red indefinitely, and it graded a renamed ADR under both ids. It now folds ids through the ledger's rename map, grades each live ADR once, and matches a walkthrough filed under any id that folds onto the subject (GHI #1150)
- Reusing a freed feature ADR slot whose previous holder had migrated to a slugged id before demotion made `fold_renames` repoint the demoted pool ADR's whole history onto the new feature; a rename of an id already renamed away now re-binds that id alone, and all 187 live `artifact_renamed` events resolve identically (GHI #1151)
- `gz arb red --commit` printed a verdict and recorded nothing, so GHI closes cited verdicts no reader could resolve; every run now writes an `arb-red-commit-<sha12>-<uuid>` receipt (schema `gzkit.arb.red_commit_receipt.v1`), appends a `red_commit_receipt_emitted` ledger event, and prints the receipt id on the verdict line (GHI #1152)
- `data/release_tag_reachability_grandfather.json` waived 22 releases whose tags were already reachable from `origin/main`; the waiver shrinks 34 to 12 with its ratchet baseline, and `gz validate --version-release` now refuses a grandfathered version whose tag is reachable (GHI #832)
- A handoff's `Settled Rulings` pointer counted only the rulings it inherited, running short by exactly the number of `[operator-ruled]` decisions the document itself booked (1015 stated against 1018 stored); the count is now read from the `Decisions Made` section before rendering, so the stated count and the store agree by construction (GHI #838)
- The OBPI pipeline's Stage 3 baseline still ran the serial `uv run -m unittest -q` under the `unittest` receipt label, emitting receipts `gz arb validate` rejects as non-canonical; it and the `gz arb` / `gz arb step` help examples now derive from `CANONICAL_STEP_COMMANDS`, and implementer and verifier prompts name `uv run gz test` (GHI #856)
- `gz agent sync` copied the generated Claude `CLAUDE.md` redirect into Codex's `.agents/skills/` surface root; the skill mirror no longer carries a redirect into another vendor's root, and a stale one there is reported (GHI #925)
- `gz validate --pointer-anchors` resolved relative links against the project root rather than the source file's directory, so a correct `../../docs/...` link from `.claude/rules/` failed; resolution is now relative to the source file (GHI #931)
- The pointer-integrity witness checked only forward `> See [...]` pointers, reaching 4 of 17 lift pointers. It now also walks every `<!-- lifted-from: -->` declaration under `docs/governance/**`, requiring the origin file, the anchor and the back-link to exist; the three orphaned back-pointers were repaired through the corpus, moving two sections to `corpus-owned` (unowned-byte floor 8637 to 6005) (GHI #933)
- `gz validate --tautological-test-audit` flagged behavior tests as content echoes when production code was reached through a same-module helper, loaded as a value, or asserted only through `assertRaises`; all three shapes are now recognized, clearing 7 false findings with no waiver added (GHI #948)
- `attested`, `gate_checked`, `audit_receipt_emitted` and `obpi_completion_uncovered_accept` rows now carry `task_id`: the new `in_scope_task_id` supplies the single in-progress TASK in the ADR's or OBPI's scope, and leaves it unset when there are several. All nine producers pass it, and `composition_rendered` and intrinsic-complexity attestation gain the field (GHI #950)
- Two `test_corpus_model` pins asserted 'no capture since re-pin' rather than their REQs, so every governed `gz content remember` turned the suite red; the fingerprint pin now covers the fixed 51-row set REQ-0.35.0-01-01 names, and the floor test asserts the folded invariant set instead of a count of 54 (GHI #975)
- The section-ownership growth refusal prescribed `gz content unown`, which the same check refuses, and `gz content unown --help` attributed the floor-lowering path to `gz content remember`, which never touches the declaration; the refusal now names both states behind it with a recovery for each (restore the declaration with `git checkout -- <path>` then `gz content unown`, or shrink the section, or capture it with `gz content remember` then `gz content own`), and the help names `gz content own` (GHI #976)
- On `windows-latest`, the ARB step fixture's child printed CJK in cp1252 and died with an empty assertion message; the helper now reconfigures stdout to UTF-8 and runs under the project interpreter. Receipt import also treats `python.exe` as the `python` runtime wrapper, since Windows argv had failed the independent-invocation check (GHI #991)
- Every `CHORE.md` restated criteria and versions that `gz chores` actually reads from JSON, and 17 of 40 criteria sets and 7 versions had drifted. All 40 now cite `acceptance.json` and `registry.json` instead, and the new `audit_chore_metadata_authority`, run in `gz check`, fails on a restated table, version or mismatched metadata (76 findings before the change) (GHI #1002)
- `gz handoff decide` still printed '(gate lifted)' and '(gate stays armed)', and its help, refusals and manpage described the resume gate retired 2026-08-15; every decision now reports only that it was recorded, and the retired-gate prose witness scans `docs/user` as well as `src/` (GHI #1004)
- 25 runtime sites in `src/gzkit` (refusal messages, docstrings and comments) cited `AGENTS.md` rule numbers ("Never #N", "Always #N") that no longer exist; they now name the section and quote the current wording, apart from two handoff comments that describe text the handoff corpus still holds, and the stop-turn lint refusal cites its real authorities, ADR-0.0.70 and the guardrail-feedback-prose rule (GHI #1035)
- Smoke documentation, `gz` help and the `run_smoke_tier` docstring said an empty tier fails; it is advisory unless `smoke.required` is true. Budget guidance now states that the full unit tier has no fixed ceiling and that a permanent smoke-budget change must update both `SMOKE_BUDGET_SECONDS` and policy (GHI #1047)
- Ontology source indexing, orphan detection and unified projection scanned `src/` even when `paths.source_root` named another directory, reporting 0 anchors and false orphans; both defaults load the discovered project's configuration, and the last-sweep cache uses the same project identity so a nested sweep cannot shift the next scan (GHI #1054)
- `audit_line_endings` named the `write_text`/`open(..., "w")`-without-`newline` hazard but read only committed bytes, so it could never catch runtime-written fixtures, and it stayed green through five instances. A third, static arm now flags byte-exact assertions on text-mode fixtures by reusing `_writes_text_without_newline` (GHI #1069)
- On Windows `scripts/settings_local_backup.py` built its vault slug from a path with a drive colon and backslashes, so backups landed inside the repository they were meant to survive; `_slug` normalizes through `as_posix()` to a safe segment and the vault resolves under `~/.claude/backups/` (GHI #1071)
- `gz git-sync` labelled artifacts a commit only mentions as touched, and every artifact anchor on the measured commit was false; the section now reads `Governance anchors referenced:` and the extractor docstring no longer claims touched artifacts (GHI #1084)
- `--help` examples for `gz obpi emit-receipt`, `brief-drift`, `withdraw`, `supersede` and `gz adr emit-receipt`, and the `brief-drift`, `supersede` and `withdraw` manpages, showed `--attestor "Jane Doe"`; they now show `g0`, and `obpi-emit-receipt.md`'s `human:g0` becomes `g0` to match its parser (GHI #1101)
- The complexity advisor's proof sorted a one-line signature's `arg` node ahead of the `FunctionDef`, so 870 of 1151 authoring hints over `src/gzkit` pointed at the def line alone; the diagnosed node's range now leads the proof, and the hint projection, `gz complexity guide`, `gz justify` hint injection and the auto-chain Proof line all span the function (GHI #1104)
- The complexity auto-chain ignored the `advisor_timeout_seconds` config key and its pre-commit hook ran unpinned `uvx xenon`; `run_with_timeout` takes the configured value when no explicit timeout is passed, the 30s default is single-sourced, the hook runs the pinned xenon, and `install_complexity_advisor` installs by default (GHI #1105)
- The Constitution type disagreed across registry, transitions, model and schema (two allowed `Amended`, two `Review`), and the registry path named a location `gz constitute` never writes; all four now carry Draft/Review/Ratified/Amended/Superseded with Draft to Review to Ratified transitions, and the registry path derives from `PathConfig.constitutions` (GHI #1134)
- The `commit_trailers` refusal prescribed `Task: TASK-<slug>-#<ghi>` for direct-fix work, prompting a GHI to be filed just to satisfy it; the message, three docstrings and `docs/user/manpages/validate.md` now give `TASK-<slug>` with `-#<ghi>` only when a GHI already exists (GHI #1142)
- 23 tests in `tests/commands/test_content_unown.py` failed on Windows because the ownership fixture wrote through `write_text` newline translation while floors were derived from the LF string; all seven surface writes go through one `write_bytes` helper (GHI #958)
- `ExecutionFixture.write` and 11 mutation-witness fixture writes translated `\n` to CRLF on Windows, breaking a `source_sha256` digest test and a multi-line `Mutation.find` in the acceptance-recovery scenario; all write with `newline="\n"` (GHI #990)
- 13 `src/` files still cited the deleted `governance-core.md` as a rule home, including the `manpage_alignment` validation error an operator reads, which now cites `AGENTS.md § Governance doctrine surfaces` (GHI #1024)
- The `ghi-triage` chat-silence hook matched `triage.py --format rank` with `[^\n]*`, so the same call wrapped across a backslash-newline was never inspected; the pattern now follows line continuations and still stops at a bare newline (GHI #1033)
- `.gzkit/rules/model-selection.md` § Skill frontmatter prescribed a top-level `skill-version`, which the metadata validator rejects as `SKA-METADATA-SKILL-VERSION-MISSING`; the example now uses quoted `metadata.skill-version`, delivered to every mirror (GHI #1040)
- `test_report_publication`'s retry test built its fixture with `write_text`, producing CRLF on Windows against an LF assertion; it writes bytes (GHI #1068)
- `docs/governance/opus-tuning.md` named one fallback model for all Opus 5.5 safety classifiers and kept two per-turn thinking nudges its own adaptive-regulation section contradicts; it now states each classifier's fallback per card § 1.5, prohibits asking an agent to reproduce hidden reasoning, and replaces the nudges with effort as the control; `.gzkit/rules/model-selection.md` 0.6.3 drops "extended thinking" from the `effort: max` row (GHI #1097)
- `gz content commit` wrote the `.retention.json` sidecar with no trailing newline, so the end-of-file-fixer hook rewrote it and refused the first commit carrying it; the sidecar now ends with a newline (GHI #1109)

### Breaking changes

- `gemini` is removed from `VendorsConfig` and the manifest schema, left behind when Gemini support and its surfaces were withdrawn 2026-09-16. A project that hand-authored a `vendors` block listing `gemini` now fails with `extra_forbidden`; delete the entry. `gz init` never writes one (GHI #1016)

## v0.34.7 (2026-08-29)

### Release highlights

- A feature file nested below `features/` was planned into no Behave shard and run by no process, reported as a pass; discovery is now recursive and the conservation test no longer asks the planner's own question to decide what the planner should have found (GHI #917)

### Fixed

- The Behave shard planner enumerates feature files recursively, so a feature nested below `features/` is sharded rather than dropped into no process; the conservation test now builds its expected set from what the fixture authored instead of re-asking the planner's own glob, and the `dist/` write-race guard discovers builders recursively on the same grounds (GHI #917)
- Two private step-module helpers that were defined and never called are removed — a patcher teardown that read as a discharged obligation while `after_scenario` actually owned it, and a 46-line duplicate seeder that lost its caller; a new fence fails on any uncalled private helper under `features/steps/` (GHI #918)

## v0.34.6 (2026-08-29)

### Release highlights

- A `gz init` tree is usable on its first command: it builds under `uv`, passes `gz validate --surfaces` with no follow-up sync, carries rules scoped to paths an adopter can have, and no longer ships the maintainer's personal name or machine-local paths (GHI #908, GHI #910, GHI #911, GHI #899, GHI #900)
- Gate wall-clock falls across the board — a one-file commit drops from 59.0s to 8.2s, BDD shards four ways, `gz validate` stops rewriting 102 files per invocation, and the canonical attestation invocation stops resolving a test runner from the network (GHI #902, GHI #906, GHI #890, GHI #891, GHI #856)
- Three gates that reported green without holding are bound to observed state: `precomplete` no longer reports READY on a refuted verdict, the tier-1 adversary proof is satisfiable by the mandated dispatch, and an interrupted corpus write can no longer destroy canon (GHI #879, GHI #884, GHI #881)

### Added

- `gz obpi block` and `gz obpi unblock` record that a brief awaits a named operator decision; the pipeline refuses to launch while a block stands (exit 3), and `precomplete` reports it as an eleventh precondition (GHI #887)
- `gz check` shards BDD execution across four parallel processes, conserving all 408 scenarios and reporting failing shards first; 65.1s to 48.5s at that fix (GHI #906)
- Ledger schema rules accept a conditional `when`/`then`/`because` form, so `gz validate --ledger` can assert a runtime gate's own condition; the first consumer requires an `attestor` on any `corpus_entry_retired` whose `floor_direction` moves invariant-tier liveness, and an unreadable rule is reported rather than skipped (GHI #882)
- `gz validate --corpus-retirement-witness` runs in the default `gz check` scope, and `gz content reconcile-retirements` emits `corpus_retirement_reconciled` for legacy hand-written tombstones (GHI #885)
- `gz validate` fails on any home- or drive-rooted literal in shipped instruction text (GHI #900)

### Changed

- The canonical `unittest` attestation invocation runs `unittest-parallel` 1.8.6, hash-locked in `uv.lock`, rather than resolving a runner from the network: 144.23s to 41.34s (GHI #856)
- `gz check` runs the Test step alongside the writer lane instead of idling behind it; 72.1s to 60.8s at that fix (GHI #904)
- `gz validate`'s default scope is classified read-only, so four gate steps run alongside it instead of queueing behind it (GHI #891)
- Session-start and resume advisement warns when the clone is behind origin, qualifying the named handoff with a commit count and a `git pull --ff-only` instruction (GHI #872)
- The wheel withholds skills whose subject only gzkit can have (`airlineops-parity-scan`, `gz-competitor-radar`) and every router row pointing at them: 68 of 70 delivered, no dangling references; `audit_router_tables` also widened to see `gz-skill-router`'s table header, previously structurally invisible to the router gate (GHI #915)
- The Pythonic-pattern design-patterns archive is an unset-by-default environment variable whose absence makes a disposition explicitly provisional (GHI #900)
- `gz obpi complete --help` and the manpages record the operator as `g0`; 92 occurrences across 19 files repaired (GHI #899)
- `data/check_step_concurrency.json` re-measured 2026-08-28 at `d3cf81b0`, all 58 steps run alone and reporting success; one entry had drifted 7x (28.67s to 4.05s) and was routing attention as the third most expensive step in the gate. `class` deliberately not re-derived — a different protocol, and re-deriving it casually would put a guess where a measurement is (GHI #903)

### Fixed

- `gz init` scaffolded a `pyproject.toml` naming a `README.md` it never created, so `uv run` failed on the first command init recommends (GHI #910)
- `gz init` left a tree that failed `gz validate --surfaces` with 58 missing generated surfaces (GHI #908)
- Rules delivered to adopters carried gzkit's own paths; unreachable `applyTo` patterns on a fresh tree fell from 33 to 14, with every gzkit-internal pattern removed (GHI #911)
- The reachability audit could not distinguish an unsatisfiable glob from one a young project had not yet populated, so a new project failed readiness on findings describing its age (GHI #912)
- `gz cli audit` raised an unhandled `FileNotFoundError` on a project with no doc-coverage manifest, and required adopters to document gzkit's own CLI to pass the readiness eval (GHI #913)
- Four wheel-shipped chore and skill files instructed readers to open a path resolvable only on the maintainer's machine (GHI #900)
- `sync_all` wrote relative to the process working directory rather than the `project_root` it was given; 5 of 591 files differed between in-tree and out-of-tree syncs, now 0 (GHI #909)
- `gz obpi precomplete` reported `adversarial_validation` READY whenever the evidence heading existed, including on `refuted` and `refuted-with-caveats` verdicts (GHI #879)
- The Step-4b tier-1 adversarial proof read `command[0]` instead of walking the runtime-wrapper set, so the operator-mandated Codex plugin dispatch could never satisfy the gate; the skill, its wheel twin, the vendor mirrors, and the function docstring now describe the walk (GHI #884)
- A conforming tier-1 dispatch fronted by `bun` was refused at OBPI completion; the runtime allowlist is held in agreement with the directive mandating dispatch surfaces (GHI #895)
- Stage-2 dispatch credit and single-driver declarations lived only in the Layer-3 pipeline marker, so `clear-stale` destroyed them and `precomplete` reported 0-of-3 against a review that had happened (GHI #886)
- `gz check`'s brief-reconcile scope compared allowlist globs literally, reporting drift against files a glob such as `src/gzkit/cli/**` legitimately covers; matching is subtree-bounded, so a sibling outside the pattern is still flagged (GHI #876)
- A `gz check` step gating a validator scope was invisible to the validator-reachability ratchet; the disagreement now fails a coherence test, and registering the one live instance (`--obpi-lifecycle-coherence`) drained the ungated baseline 52 to 51 (GHI #787)
- 22 generated surfaces — 21 vendor persona mirrors and the Copilot ledger-writer hook — were absent from `SURFACE_ROOTS`, so hand-edits passed `gz validate --surfaces` silently (GHI #893)
- A hook formatter that could not run swallowed its failure, making it indistinguishable from a clean format and surfacing only as unexplained sync drift; the full diagnostic now reaches stderr and the status is returned (GHI #914)
- `gz validate --ledger` fell through on nullable declarations (`{"type": ["string","null"]}`) and array item types, checking those fields for nothing; the two canonical ledger readers now agree (GHI #883)
- Hand-written corpus tombstones retired canon with no ledger witness; a retirement now requires a witness whose `retired_entry_id` equals the tombstone target, and seven previously unwitnessed retirements were reconciled to 12/12 (GHI #885)
- A failed corpus append could destroy canon; writes stage to a same-directory temp file, fsync, then atomically replace, so any failure leaves the prior corpus byte-identical (GHI #881)
- Concurrent corpus appends silently dropped rows from canon; writers serialize under an exclusive store lock with uniquely-named staging files, verified across 20 barrier-synchronized trials with zero losses (GHI #880)
- `append_entry` persisted before validating, so an unresolvable tombstone reached disk and left the corpus unreadable (GHI #875)
- The full `gz check` gate failed on `windows-latest`; three probes assumed POSIX permission bits and a moving ctime, and one leg had been asserting nothing at all (GHI #901)
- Pre-commit repo scanners walked 367k paths against 7,241 tracked files, and the reachability ratchet accepted gitignored caches, candidate renditions, and ARB receipts as evidence that a validator scope was reachable; a one-file commit fell from 59.0s to 8.2s (GHI #902)
- `gz validate` rewrote 102 canonical files on every invocation — `AGENTS.md`, every vendor rules mirror, 17 hook scripts — and six governance surfaces briefly vanished mid-sync (GHI #890)
- `gz validate` wrote canonical surfaces even on a drifted tree, blocking its classification as read-only (GHI #891)
- Seven stale `src/gzkit/` pointers in skill prose named modules that no longer existed; `gz validate --cli-alignment` now fails on a skill citing a missing module and names the package that replaced it (GHI #896)
- The `gz check` scheduler documented and tested a wheel-consumption dependency that nothing implemented; delivery verification was confirmed intact and only the false justification was retired (GHI #905)

## v0.34.5 (2026-08-23)

### Release highlights

- Six governance hooks bound to editor tool matchers were bypassed by any file write made through Bash; the write-side fences move to the commit locus, where `git diff --cached` sees the change regardless of which tool made it (GHI #844, GHI #847)
- The repository's own release history is reconciled in both directions — a tag is judged by reachability rather than local presence, every documented release is swept rather than only the current one, and a published release documented nowhere in the repo is now reachable by the audit (GHI #828, GHI #829, GHI #830)
- Two ceremony deadlocks that left an unpushable tree are cleared: completion ledger rows stamp at write time rather than ahead of the event written above them, and reconcile asks reachability instead of single-hop membership (GHI #842, GHI #867)

### Added

- `gz validate --module-size` reports a ratchet entry looser than the module it governs; the shrink-only ratchet had no arm for that direction and 861 lines went unrecorded (GHI #853)
- The OBPI pipeline makes an undispatched Stage 2 visible and refuses it; `record_subagent_dispatch` had a model, a reader, and an aggregator but zero callers, so the dispatch record could never be written (GHI #845)
- `ghi-author` Step 0 gains a third pre-flight query against `docs/design/adr/**/obpis/`, so an authored OBPI brief owning the same work is no longer invisible to the duplicate check by construction (GHI #864)
- The release audit sweeps the inverse direction, so a tagged and published release carrying no `RELEASE_NOTES.md`, `CHANGELOG.md`, or manifest entry is detected; three such releases existed (GHI #830)

### Changed

- `gz check` runs its read-only gate steps concurrently behind a measured declaration, fingerprints the staged tree so the pre-push skip actually fires, and skips a tree it has already verified (GHI #835)
- Handoff-document validation batches its tracked-path lookup; the `Handoff documents` step fell from 29.8s to 4.3s, having been 19% of the whole gate (GHI #858)
- A handoff carries the settled-ruling corpus by reference to the append-only store instead of copied prose, and the settled-ruling integrity audit reads the store rather than the rendered document (GHI #838)
- Stage-2 implementer prompts carry the persona and the Why, and cite the threshold authority rather than restating its values (GHI #861)
- All seven new-verb CLI obligations are named in one authority; they had been described across three surfaces with no two agreeing, and registering one verb produced 21 first-run failures (GHI #854)
- `.gzkit/rules/mx-mode.md` names both floor opt-in mechanisms — survival by guard name and survival by emitted level — and when each applies (GHI #855)
- The release audit sweeps every documented release rather than point-checking `[project].version`, so a historical release that loses its tag is reachable (GHI #829)
- The brief-ownership precondition is seated in `AGENTS.md` § Defect-fix routing: a live OBPI brief owning a finding makes routing operator-level, and a terminal brief does not block (GHI #864)

### Fixed

- Completion ledger rows are stamped at write time, so `gz obpi complete` no longer emits a receipt timestamped ahead of the adversarial-validation event written above it and leaves the ledger failing the append-only ts-order gate at push (GHI #842)
- `gz obpi reconcile` asks reachability rather than single-hop membership, so an OBPI that launched the pipeline without completing is no longer permanently stuck with an unpushable tree (GHI #867)
- Commit-locus `artifact_edited` rows are excused from task-envelope signature (a), which they have no attribution channel to satisfy (GHI #869)
- Governance edits and OBPI completion are gated at the commit locus rather than on tool identity, closing the four sibling hooks still keyed on `file_path` after the first member of the family was repaired (GHI #847)
- The MX checkpoint seam extends to the whole pre-commit surface, so a repair sanctioned by an open hangar is not refused at commit time by a guard the hangar never reached (GHI #843)
- `gz mx exit` releases its session lock and `gz mx enter` reaps orphans, so the hangar is no longer single-use per repository (GHI #848)
- `gz arb red` reports a void RED experiment instead of accusing the covering test, so a run over already-landed work no longer returns `failure_class=none` for every BEHAVIOR REQ and reads as a hollow-test finding (GHI #839)
- SessionStart scans the advised handoff at the consumption moment, so a handoff authored and left uncommitted no longer reaches the next session unvalidated (GHI #850)
- `gz handoff create` books rulings after validation rather than before, so a refused create no longer leaves rulings in the append-only store naming a document that was never written (GHI #859)
- `gz content retire` warns on rendition drift and its help text no longer promises that no recomposition is implied while the pre-push gate blocks on exactly that (GHI #863)
- `gz content remember` refuses a corpus append whose text is already live, and the root rendition is re-linked to the post-retirement corpus; seven invariant texts had been stored twice, so an amendment could not be clean (GHI #862)
- Rendition grading routes by the consumer's own content type instead of the union of all routes, so a rendition is no longer graded for a consumer its content type never routes to (GHI #840)
- The release audit judges a tag by reachability rather than local presence, so an unpushed tag no longer passes every gate; `v0.7.0` had sat local-only against an orphaned commit (GHI #828)
- Four skills no longer cite a Superseded pool ADR as "awaiting promotion", and the lifecycle-pointer arm is re-homed onto `--cli-alignment` to fence the class (GHI #846)
- `gz-adr-create`'s Trust Model states the pool carve-out: `gz plan create --kind pool` does not book an `adr_created` event (GHI #831)
- The generated resume-gate hook and its source docstring no longer document a `Bash` arm removed 2026-08-14 (GHI #805)
- Layered test patchers unwind LIFO so no mock outlives its test; four tests passed only in the default discovery order and failed under shuffle (GHI #857)
- The test-tier boundary is enforced on feature tags, so `@slow` is read rather than declared and ignored (GHI #860)

### Security

- Write-side governance hooks fence production writes at the commit locus rather than on the `Write|Edit|NotebookEdit` tool matcher, closing a bypass in which any file write issued through Bash matched none of the six gates (GHI #844)
- The authorship guard is pinned so an open MX hangar cannot demote it; hangar demotion had silenced the operator-PII check, which exists to prevent a leak whose recovery costs a history rewrite and a force-push (GHI #852)

## v0.34.4 (2026-08-18)

### Release highlights

- Enforcement gains its missing half: negative controls tested whether a gate's rule fires, never whether its exemption admits only what it should — 28 exemption surfaces, 55 negative controls, 0 exercising an exemption. The exemption axis is now declared, inventoried, and controlled on two gates, draining the undeclared backlog 71 -> 55 (GHI #797, GHI #798)
- The content surface's attestation is inverted and renamed: corpus additions and removals now carry operator attestation while a re-render of unchanged canon does not, and the build step stops claiming the name "Gate 5" that ADR-0.0.36 fixes to OBPI/ADR completion attestation (GHI #821, GHI #822)

### Added

- `gz validate` inventories the exemption half of every registered enforcement claim, and two gates receive working exemption controls; eight exemption-free gates are declared as such (GHI #797)
- `EnforcementClaimRecord` records the gate its entrypoint delegates to, so a claim resolves to the gate it enforces without reading the delegation chain by hand; `source_file` had pointed only at the negative-control shim in `_qc_nc_entrypoints.py` (GHI #798)
- `gz validate --ledger` compares each row's `ts` against its predecessor and rejects a ledger whose timestamps run backwards; the property held across all 15,037 live rows with no witness (GHI #812)
- `gz patch release` discovery reports an `unclassified_reference` bucket for a GHI cited in range only by a commit whose Conventional-Commits type is not a closure type; such a GHI previously appeared in no bucket at all (GHI #794)
- A merge driver for runtime-appended tracked JSONL, so two concurrent `gz git-sync` runs that both appended to `.gzkit/ledger.jsonl` merge by tail-union instead of halting the rebase for a hand-edit (GHI #811)

### Changed

- `gz content remember` and `gz content retire` accept and record an attestor; `gz content commit` no longer fail-closes on a re-render whose corpus fingerprint is unchanged, and the fingerprint witness is exposed rather than assumed (GHI #821)
- The content-surface attestation is named "corpus attestation" across help text, source, and docs; twelve naming sites across three sweeps previously called it "Gate 5" (GHI #822)
- `gz git-sync` retains a refusing hook's stdout in its blocker output, so a pre-push gate refusal reports the failing check, file, and line rather than only `failed to push some refs` (GHI #816)
- The handoff resume gate declares command separators explicitly instead of deriving compound shape, admits a compound whose every segment is individually admitted, reads `2>&1` as descriptor duplication rather than a file redirect, and admits writes targeting the null device; the ruling that compound breadth is correct is recorded in the gate and in `gz-session-handoff`'s Trust Model (GHI #800)
- The `instructions-files-diet` chore routes edits through `.gzkit/corpus/` and the canonical `.gzkit/rules/` sources rather than the rendered `AGENTS.md` and the generated vendor mirrors; the sibling memory-hygiene migrations are routed the same way (GHI #817)
- `docs/governance/attested-req-subject-retirement.md` records the disposition for an attested REQ whose subject a later doctrine ruling retired on a terminal, unamendable ADR, with the binding bullet added to `governance-core.md` in all four surface copies; the transition had been resolved correctly twice from first principles and written down nowhere an agent would find it (GHI #823)
- `--req-kind-discipline` tolerates markdown emphasis around a REQ kind tag in both readers, matching `triangle.py`'s existing tolerance; the two immune tag readers are pinned into the guard by test (GHI #809)
- Task-envelope Signature (c) fires on contradiction between discovery channels rather than on incompleteness, so a channel naming a strict subset of the union is no longer reported as layer-drift (GHI #820)

### Fixed

- `gz task start` resolves an OBPI id to its brief by anchoring on canon rather than substring-matching an `rglob` of the working tree, so TASK declarations no longer land in a `.claude/plans/` file; the 11 declarations misrouted on OBPI-0.35.0-09 were restored to the brief (GHI #824)
- The pipeline auto-start path stamps the `tasks:` frontmatter discovery channel, which had produced zero keys repo-wide and left Signature (c) comparing 7 of 534 OBPIs (GHI #752)
- `gz obpi brief-drift --apply` amends the frontmatter allowlist for a structured brief, where the reconciler actually reads; it had written into the prose `## Allowed Paths` section and reported success while the drift persisted byte-identically (GHI #825)
- `gz obpi precomplete` matches the supplied OBPI id instead of a derived prefix, so parked OBPI ids retaining a semver that a later ADR reused no longer collide under one `OBPI-<semver>-<index>` prefix (GHI #826)
- The verifier-pipe gate honors `pipefail` and `PIPESTATUS` when they are used rather than when they are named; any token mentioning either — including `grep -rn "pipefail" docs/` — previously disarmed the gate (GHI #796)
- A handoff resume ruling is coupled to the `handoff_path` it was booked against, so a ruling on one document no longer lifts a gate armed on another (GHI #795)
- The handoff settled-citation annotator matches only genuine GHI references, so an `AGENTS.md` behavior-rule number such as "Always #13" is no longer resolved against live issue state and stamped `[settled]` (GHI #827)
- Gate-5 template assets in the `gz-obpi-specify` and `gz-adr-audit` skills invoke commands that exist, replacing airlineops-era invocations of a module absent from this package; ADR-sync/audit Layer 1 routes through `gz covers` rather than a raw ADR grep (GHI #806)
- Four `REQ-0.0.37-15-*` covering tests and the AgentContract BDD scenarios are repointed at the root consumer, unstranding them from the retired per-vendor AgentContract doctrine while preserving their `@covers` bindings and attested REQs (GHI #819)

## v0.34.3 (2026-08-12)

### Release highlights

- Six of the thirteen fixes are gates that reported success while structurally unable to see their own subject: an advisory verb whose verdict never reached its exit status, a mandatory ledger ceremony no registered command could emit, and a negative control that reported working enforcement as theater (GHI #781, GHI #785, GHI #791, GHI #792, GHI #793, GHI #794)
- Windows returns to co-equal support: a Windows clone could not complete `gz git-sync` because the typecheck gate's exclusion never matched and generated surfaces were written with translated line endings (GHI #788, GHI #681)

### Added

- `gz validate --gate-callers` inventories gates with no automatic caller — 44 candidates surveyed, 40 disclosed as uncalled with a stated reason each, shrink-only via the waiver ratchet; wired as `gz check` step 45/54 (GHI #785)
- `gz validate --surface-weight --recalibrate` emits the `surface_weight_recalibrated` ledger event and rewrites `data/surface_weight_floor.json` in one transaction; the event was mandatory under ADR-0.0.33 and had no producer in any registered verb (GHI #791)

### Changed

- Surface-weight band constants are compared against the bands recorded on the most recent recalibration event and fail closed on disagreement, replacing enforcement by agent goodwill (GHI #792)
- `HandoffFrontmatter.continues_from` accepts multiple ancestors, so a forked handoff chain that re-merges inherits booked operator rulings from every parent instead of one (GHI #790)
- Toolchain and dependencies move to current upstream; the `ty` pin at 0.0.55 is lifted and the 88 latent diagnostics it was hiding are resolved (GHI #789)
- Surface sync prunes `runtime_state` from the package tree rather than only declining to propagate it, removing 71 chore proof files that shipped in the wheel against their own declared classification (GHI #783)
- `_build_check_steps`' coupling checklist splits STEP obligations from SCOPE obligations and names all eight, where it had named four (GHI #787)

### Fixed

- `ty check --exclude` uses a spelling that matches on Windows, so the 25 `features/` diagnostics no longer reach the gate and block `gz git-sync` on a Windows clone (GHI #788)
- Generated surfaces are written with pinned LF at all eight write sites in `sync_surfaces.py`, so raw-byte parity and distribution checks no longer report drift on a freshly synced Windows tree (GHI #681)
- `gz chores advise` exits 3 when a criterion fails, instead of printing `FAIL` and returning 0 — 7 of 39 registered chores were failing invisibly to any programmatic caller (GHI #781)
- Negative-control subprocesses pin colour off, so an `expect_output` substring assertion no longer flips its verdict on the invoking shell's `FORCE_COLOR` and report a false FACADE against working enforcement (GHI #793)
- The `hardcoded-root-eradication` chore criterion no longer counts a comment documenting compliance as a violation of the rule it documents (GHI #782)
- `_GHI_SUBJECT_CLOSURE_PATTERN` matches the `(GHI #N, GHI #M)` multi-issue subject spelling alongside `(GHI #N, #M)`; the unmatched spelling dropped both cited GHIs from release discovery with no warning bucket (GHI #794)

## v0.34.2 (2026-08-08)

### Release highlights

- Ten of the thirty closed GHIs move session continuity off agent recall and into the runtime: an exit-time bookmark with a producer, a recorded resume decision, and one single-sourced answer to "what changed since the last handoff" (GHI #756)
- Cross-vendor adversarial review claims must resolve to a receipt proving a different vendor ran, closing the tier-1 self-assertion path at both the pipeline and the completion gate (GHI #780)

### Added

- Exit-time handoff bookmark written by the session-exit path, giving the handoff write surface a trigger instead of depending on agent recall (GHI #756)
- Mechanical audit that every OBPI-status writer consults the terminal-status rule, which was convention-only with no witness (GHI #669)
- `gz arb archive` relocates aged, uncited receipts into `artifacts/receipts/archive/` as a move-not-delete retention half; the `purge` half and the unified retention doctrine covering handoffs remain unbuilt, so GHI #594 stays open (GHI #594)
- Resume decisions are recorded — including declines and per-step set-asides — and SessionStart seeds handoff review as a real first turn rather than a passive listing (GHI #757)
- Schema validation for pool ADR interview JSON, which was unschema'd while the non-pool path was validated, plus capture and rendering of forcing-function answers into the ADR (GHI #719)

### Changed

- The advisory scorecard scores each rule by version rather than by filename, so a new binding clause cannot land inside an already-scored file without being scored itself (GHI #754)
- Step-4b tier-1 must resolve to a receipt rather than being asserted by the caller (GHI #765)
- `gz obpi complete` refuses a tier-1 cross-vendor claim carrying no receipt, closing the class GHI #765 named but left open (GHI #780)
- The Step-4b adversary tier must be declared, and unsupported cross-vendor claims are rejected instead of accepted on preference (GHI #678)
- Dispatch attestation audits whether the mandated independent reviewer personas actually ran, rather than checking an absorption marker that dispatch does not imply (GHI #770)
- `ghi-close` re-derives every cited issue, receipt, and failure cause at close time instead of restating claims made earlier in the session (GHI #771)
- Verifier commands piped into another process are refused, since the shell reports the filter's exit status and can mask a failing suite as green; `set -o pipefail` and `${PIPESTATUS[0]}` are the explicit opt-ins (GHI #589)
- The handoff delta computation is single-sourced, so exit, orientation, and account surfaces cannot disagree about what changed since the last handoff (GHI #762)
- Token-block register entries are named and stored as exchange records, distinct from session handoffs, per the transit/exchange/handoff separation (GHI #763)
- Exchange records carry the brief's value narrative and its tracked defects instead of four boilerplate sections out of seven (GHI #764)
- Governance docs cite `gz adr status` for OBPI counts, and `gz check` fails closed on transcribed counts that no surface reconciles (GHI #768)
- The failure-class index ranks families by authored diagnoses rather than bare citations, so depth reflects real analysis (GHI #772)
- Brief reconciliation records that its checks are existence-only and detect neither dead surfaces nor code couplings (GHI #581)
- `gz adr demote` applies a non-lossy collision policy, preserving the promoted ADR's current content instead of failing or restoring the stale pool intake it diverged from (GHI #775)

### Fixed

- `gz git-sync` no longer absorbs staged `src/` and `tests/` work into a generated ceremony chore commit (GHI #708)
- The handoff resume gate's read allowlist uses a membership predicate, closing the fourth narrow miss in which file-writing verbs were admitted while harmless reads were refused (GHI #732)
- The memory-hygiene chore no longer passes regardless of actual drift, and its acceptance check runs on machines other than the maintainer's (GHI #743)
- A session that authored a handoff is no longer challenged to attest its own document (GHI #755)
- Machine-floor auto-bookmarks no longer shadow an authored handoff in session orientation (GHI #758)
- The session-exit skip predicate accounts for the handoff's own landing commit, so a redundant exit bookmark is not written when an authored handoff already accounts for the work (GHI #760)
- `gz adr evaluate` no longer overwrites the reviewer's scorecard, which silenced recorded NO-GO verdicts and blocked the next commit (GHI #769)
- ADR-0.44.0 is returned to pool, restoring one-feature-at-a-time, and demotion no longer silently breaks tests (GHI #773)
- OBPIs parked under an active parent are unparked, closing the path where a parked brief could be deleted with no ledger trace (GHI #774)
- Demoted pool ADRs no longer keep their pre-demotion id in the H1, which resolved to a different live ADR for 8 of them (GHI #776)
- Demoted pool ADRs no longer carry runnable attestation commands aimed at a different, now-live ADR (GHI #777)
- Governance docs and skills no longer point readers at a retired attestation-enrichment rules file that does not exist; the guidance is rehomed to a live surface (GHI #778)

## v0.34.1 (2026-08-04)

### Release highlights

- Nine of the twenty-three fixes are validators, audits, or discovery channels that passed while measuring a fraction of their declared surface, or none of it (GHI #744)
- The three frontmatter-ingress bypasses recorded as known limitations in v0.34.0 are closed (GHI #736)

### Added

- `gz validate --invariant-witness` registered as a CLI scope and enrolled in the gate; the validator function previously had no caller outside its own test (GHI #746)
- Refusal and negative demo discovery in closeout walkthroughs, so ceremony queues surface commands that must fail rather than only positive assertions that exit 0 (GHI #738)
- Schema enforcement for the `tasks:` discovery channel on both readers — `BriefStructure._validate_tasks` on the model path and signature (e) of `gz validate --task-envelope-coherence` on the corpus path — rejecting malformed TASK IDs and unknown parent REQs (GHI #753)
- `project_local` content class for chores, declared in `registry.json` and honored by sync, `gz init`, and `gz chores doctor`, keeping gzkit-internal chores out of the wheel and out of adopter scaffolding (GHI #728)

### Changed

- OBPI briefs parse through their `BriefStructure` Pydantic schema fail-closed; the regex-scraping `LegacyBriefShape` fallback that 597 of 600 briefs used no longer gates governance (GHI #615)
- Chore acceptance criteria gate the chore's own subject instead of standing in with the unit suite (GHI #743)
- The `tasks:` channel is producer-stamped by `gz task start`, and `@advances` is demoted to advisory with its emptiness asserted rather than assumed (GHI #752)
- Foundation closure is scoped project-local rather than framework-wide, so an adopter is no longer refused their own `kind: foundation` packages (GHI #740)
- MX agent-facing surfaces name the marker path the code writes, `.gzkit/mx.json`, instead of `.gzkit/mx-active` (GHI #650)
- `gz validate --cli-alignment` verb detection widened to fenced code blocks, which previously escaped all three detectors (GHI #745)
- `gz validate --cli-alignment` adopts the stronger shared verb extractor already shipped in `hooks/obpi.py` instead of its own weaker reimplementation (GHI #748)

### Fixed

- Text-mode `subprocess` reads across 41 call sites pass `errors=`, so commands no longer crash when a tool emits non-UTF-8 output (GHI #582)
- The tautological-test audit no longer walks the decorator list when applying its production-code exemption, so a `@covers` decorator stops hiding the test; 217 of 290 previously-masked findings are visible (GHI #730)
- The task-envelope layer-drift gate keys all channels on a canonical OBPI id, so signature (c) compares more than the 6 of 776 OBPIs that survived the key mismatch (GHI #731)
- The handoff resume gate admits `git rev-list`, closing the third narrow miss in a read allowlist its own refusal prose describes as permitting git reads (GHI #732)
- The shared `register_adr_in_ledger` helper enforces the foundation membrane, closing the third `adr_created` ingress that booked prohibited `kind: foundation` ADRs (GHI #734)
- A leading UTF-8 byte-order mark no longer hides an entire frontmatter block, which previously read as "this file has no frontmatter" for every key (GHI #735)
- Frontmatter ingress decodes through one shared tri-state reader, closing the unicode-line-separator and BOM-less UTF-16/32 bypasses that three disagreeing ad-hoc decoders admitted (GHI #736)
- The minor-release closeout ceremony no longer deadlocks on the rule-11 tag audit after bumping the version; `gz closeout` writes an in-flight manifest and the audit accepts `RELEASE-v{version}.md` (GHI #739)
- The ADR template's `{persona}` placeholder is substituted rather than rendered as literal text, with a validator enforcing the `## Persona` section (GHI #741)
- `gz validate --documents` validates ADR packages authored before the frontmatter mandate instead of silently exempting them (GHI #742)
- Registering a `gz validate` scope enrolls it in `gz check`, closing the gap that let a failing scope pass the commit gate for eight days (GHI #744)
- The GovZero OBPI-pipeline runbook no longer documents a `gz superbook` bridge that has never been registered (GHI #749)

## v0.34.0 (2026-07-31)

### Release highlights

- The `foundation` ADR kind is sealed at every authoring door (ADR-0.34.0 Foundation Sunset): 51 historical foundations are grandfathered from ledger truth, 23 genuinely-unstarted ones demote to pool, and `gz validate --taxonomy` is wired as the permanent final step of `gz check`. The kind is sealed, not deleted — the enum stays valid for the grandfathered set on disk
- Fifteen GHIs closed alongside it, seven of them surfaces that returned a clean or confident result while measuring the wrong thing — a reconciliation verdict that varied by machine, 1876 of 2020 REQs miscounted as drift, and a witnessless grandfather event accepted as attested

### Added

- `gz smoke` tier and its `gz check` gate, giving the 60-second smoke budget a tier to measure and a gate to enforce it after the budget had been declared with neither (GHI #724)
- `test-consolidation-subtest-sweep` chore registered project-local — deliberately not shipped in the wheel — as the landing site for the consolidation scope that survived the at-scale test-management tracker, which closes `superseded` (GHI #644)

### Changed

- `gz brief reconcile` becomes `gz obpi brief-drift` and `gz obpi reconcile` becomes `gz obpi sync`, retiring the single-verb `brief` namespace; the two verbs previously operated on the same artifact, so reaching for the wrong one exited clean on the wrong axis with no error signal (GHI #641)
- `audit_code_contract_mismatches` is scoped to `src/gzkit`, so gzkit's internal Pydantic-over-dataclass constraint is structurally inert outside this repository and no longer fails `gz validate` on an adopter's own `@dataclass` value objects; the rule text is unchanged, since the defect was the export rather than the doctrine (GHI #607)
- ADR-0.0.33 Invariant 4 (scenario reachability) and its validator scope are retired, ending a two-month advisory that three `gz check` steps emitted for a registry that was never delivered (GHI #716)

### Fixed

- `gz handoff create` reports when it cannot resolve a predecessor instead of silently dropping the settled-ruling chain, which had made an ADR-less create without `--continues-from` discard every carried ruling (GHI #717)
- The pool-ADR authoring path names the interview verb that actually accepts a pool ADR, rather than one that rejects it (GHI #718)
- `gz git-sync` reads pull state after the auto-commit that changes it, so a branch that is both behind and dirty no longer self-diverges (GHI #720)
- Brief reconciliation stops existence-checking paths outside the repository root, so its verdict no longer varies by machine (GHI #721)
- Handoff authoring refuses a `## Decisions Made` section whose marker-less shape parses to zero entries, the defect that silently dropped ten operator rulings across two handoffs (GHI #722)
- Test output is buffered so only failures speak, ending CI logs in which passing negative-path prose was indistinguishable from a real failure (GHI #723)
- Commit-authorship enforcement is bound to a gate rather than to a single clone's git config, closing a path that left operator PII one `git config` away (GHI #725)
- Negative-control warnings emitted by passing `behave` runs no longer persist into Gate-5 audit proofs (GHI #726)
- Drift reporting scopes unlinked specs to the `@covers` proof channel, so SUPPORT, STRUCTURAL-FENCE, doc-channel, and terminal REQs are no longer counted as drift — 1876 of 2020 reported entries were not drift (GHI #729)
- The `gz validate --taxonomy` terminal-partition reader inspects the `attestor` on a `foundation_grandfathered` event instead of accepting any event that carries a non-empty id, closing a path by which a generic attestorless event read as witnessed (GHI #733)

## v0.33.3 (2026-07-25)

### Changed

- Unstarted-brief Discovery findings in brief reconciliation scoped by computed predicate — own-deliverable, pending-upstream product, or dead citation — rather than exempting unstarted briefs wholesale (GHI #615)
- Pre-commit hook entries repointed from `uvx` to `uv run` so ruff, ty, xenon, and interrogate resolve at or above their `pyproject.toml` floors instead of from an ambient cache below them (GHI #715)
- `gz validate --cli-alignment` excludes `docs/releases/` from the manpage-prefix audit, exempting generated release manifests as sealed historical records (GHI #715)

### Fixed

- `gz init` installs and verifies the pre-commit and pre-push hooks it scaffolds instead of writing `.pre-commit-config.yaml` and leaving activation to the operator; `gz validate --session-green-gate` gains a delivery arm that inspects the effective hooks directory, honoring `core.hooksPath`, and reports recovery prose when installation is blocked (GHI #715)
- `gz patch release` discovery downgrades a still-open GHI carrying qualifying commits to an `open_upstream` bucket for operator adjudication instead of reporting it `qualified`, so manifests and stats no longer assert closures that did not happen (GHI #714)

## v0.33.2 (2026-07-25)

### Added

- Codex project-doc truncation-headroom warning reporting remaining bytes before the vendor cap silently truncates the rendered agent contract (GHI #712)
- Structured OBPI brief frontmatter emission (`allowlist`, `reqs`, `verification`) from `gz specify`, so newly minted briefs parse under the brief schema instead of being regex-scraped (GHI #615)
- Run telemetry for correction mining: per-run transcript-scanned and correction-matched counts written to a run log, distinguishing a zero-result run from a broken miner (GHI #614)
- `--settled` option on `gz handoff` for recording an operator ruling that arrives after the handoff was authored (GHI #696)
- Settled-rulings section, operator-vs-agent decision attribution, and stale-next-step flagging in the handoff format (GHI #696)
- `draft (scaffold)` lifecycle label in `gz adr status` distinguishing unauthored skeleton briefs from authored drafts (GHI #665)
- Manpage filename reference binding under `gz validate --cli-alignment`, fail-closing on the non-existent `gz-<verb>.md` convention (GHI #532)
- Negative-control fixture proving the handoff populated-sections check actually refuses an empty required section (GHI #698)

### Changed

- `gz check` renders advisory output from passing steps in a dedicated end-of-run section rather than discarding it (GHI #713)
- `gz adr audit-check` separates coverage-exempt REQs onto an informational line naming their proof channel, and splits the two groups in `--json` output (GHI #701)
- `gz validate --sensitivity` adopts the shared terminal-status predicate in both the audit and CLI paths, exempting sealed historical briefs from the auto-detect floor (GHI #682)
- Brief-reconcile drift gating scoped by lifecycle dimension: an unstarted brief no longer gates on its own deliverables but still gates on prerequisites (GHI #615)
- Brief status vocabulary matched to the corpus, admitting `attested_completed`, `Abandoned`, `Withdrawn`, and `in_progress` (GHI #615)
- `req_kind` module split to satisfy the 600-line module limit, with behavior verified identical (GHI #652)
- Attestation-verdict classifier fork consolidated into a single governed implementation (GHI #573)
- Removed `ReqCoverageRecord` and its paired model, declared and tested but never instantiated by any command (GHI #545)

### Fixed

- `gz check` no longer discards advisory notices emitted by steps that passed, which had made them reachable only by running each validation scope individually (GHI #713)
- An agent holding an OBPI lock with no active pipeline can no longer write implementation files unblocked within the locked OBPI's allowed paths (GHI #606)
- Fidelity assertion rows can no longer assert the fidelity gate that evaluates them; the tautological row shape is rejected and was swept from 102 ADRs (GHI #702)
- `gz adr audit-check` no longer reports REQs as missing test coverage when their kind owes no `@covers` test (GHI #701)
- `gz context` and `gz status` no longer project divergent current gates for the same ADR; both report the furthest gate applicable to the ADR's lane (GHI #577)
- `gz validate --sensitivity` no longer exits 3 on terminal-status briefs, and two active Draft briefs governing subprocess/hook execution now declare `sensitivity: security` (GHI #682)
- Drained 174 references to the non-existent `docs/user/manpages/gz-<verb>.md` convention across 60 briefs, skills, and docs (GHI #532)
- MX maintenance-hangar documentation and rules no longer name `.gzkit/mx-active`, a marker path the tool never creates (GHI #650)
- Corrected 13 OBPI briefs declaring their parent ADR by bare semver instead of full ID (GHI #615)
- Removed `@covers` decorations from two SUPPORT REQs that inflated the coverage census (GHI #703)
- Guarded `@covers` to BEHAVIOR REQs only and removed 47 inverted decorations repo-wide, closing the inverted-proof-channel gap (GHI #711)

## v0.33.1 (2026-07-23)

### Added

- Good Docs Project changelog and release-notes template discipline: canonical templates (`.gzkit/templates/changelog.md`, `.gzkit/templates/release_notes.md`), a `paths:`-scoped rule binding both files, and this changelog surface (GHI #685)
- Validator firing when a child OBPI declares a `[STRUCTURAL-FENCE]` REQ but the parent ADR lacks the `## Boundary Invariants` section that kind's proof channel requires (GHI #538)
- Mechanical resume authorization gate: a resuming agent must book explicit operator authorization before its first mutating action, replacing the prose-only banner (GHI #574)
- Enrollment-completeness enumeration wiring the gate5-floor and grader-gaming enforcement-claim sources into the single production-discovery seam (GHI #648)
- `gz cli audit` check that manpage flag descriptions agree with the parser (required vs optional, defaults, choices, env fallbacks), not merely that a flag is mentioned (GHI #693)
- `rendition_fingerprint` provenance field and fail-closed gate detecting committed-rendition byte drift past its Gate-5 attestation (GHI #694)
- Manifest-aware `kind` guard at the `register-adrs`/`init` ledger ingress refusing a hand-placed `kind: foundation` ADR absent from the grandfather roster (GHI #706)
- `gz git-sync` pre-staging guard refusing `git add -A` when the index already holds `src/**`/`tests/**` paths (GHI #708)

### Fixed

- `gz handoff` documents no longer emit a trailing blank line that tripped the end-of-file-fixer hook (GHI #684)
- Stage-4 present-evidence no longer counts proven SUPPORT REQs as attestability blockers, so coverage accounting reflects only genuinely uncovered BEHAVIOR requirements (GHI #683)
- Airlock exit-side ledger booking is now failure-atomic, so a partial transit can no longer leave an inconsistent L2 record (GHI #679)
- Reconciled 233 orphaned `obpi_created` ledger events across 24 feature ADRs (0.27.0–0.51.0) that asserted OBPI briefs never authored on disk (GHI #584)
- `Ledger.append` is now failure-atomic (serialize-then-single-write, truncate-on-failure) with pinned UTF-8, so an interrupted write can no longer corrupt the JSONL ledger (GHI #687)
- Bound the two `continues_from` pointer resolvers so they can no longer silently desync and wrongly archive or skip a live chain link (GHI #689)
- Handoff validator now requires section population, not mere heading presence, rejecting hollow handoffs (GHI #692)
- Handoff format preserves every authored next step, operator ruling, and decision attribution across the session boundary (GHI #696)
- Handoff `adr_id` is now optional, so handoffs carry continuity for any unit of work, not only ADR-scoped work (GHI #709)
- Documented the brief-reconcile existence-vs-liveness blind spot and routed its cure to the event-registry collapse rather than entrenching a new validator dimension (GHI #581)
- brief-reconcile `req_count` dimension recognizes the REQ taxonomy and checked acceptance-criteria boxes, ending the false-positive drift that blocked pipeline Stage 1→2 entry (GHI #664)
- `gz brief reconcile --apply` re-measures drift after writing amendments and fails closed on residual drift instead of certifying the pre-mutation state (GHI #677)
- `reconcile_brief` no longer existence-checks terminal (completed/attested) briefs against the current tree (GHI #707)
- CLI color decision honors `FORCE_COLOR=0`/`NO_COLOR`, so `gz test` and `gz git-sync --test` pass regardless of ambient `FORCE_COLOR` (GHI #663)
- Acceptance-criteria REQ parser tolerates bold kind tags (`**[BEHAVIOR]**`), so decorated REQs are no longer dropped from coverage (GHI #700)
- `gz validate` no longer silently drops the six solo-only scopes when combined with another scope under a false all-passed (GHI #704)
- Repointed the `governance-core` workflow order off the deprecated `gz gates` verb onto `gz closeout`, and stopped false completion-block reports for unrelated complete OBPIs (GHI #705)
- `gz adr audit-check` covers-backfill scan excludes withdrawn OBPIs' REQs, unblocking closeout of ADRs that withdraw OBPIs whose `@covers` tests remain in the tree (GHI #695)
- Hardened enforcement-floor negative controls: expected exit codes, banned empty-directory fixtures, decomposed composite claims, subprocess NCs pointed at the working tree (GHI #699)
- `gz plan audit` honors the brief's `**CREATE**` markers and `gz brief reconcile` skips glob prerequisites, so first-implementation OBPIs no longer deadlock (GHI #626)
- Resolved duplicate invariant-tier corpus entries for the "Correction vs enhancement" directive that made AGENTS.md recomposition unsatisfiable (GHI #635)
- Closed the `gz content remember` footgun with a guarded, orchestrated capture→compose→commit canon-landing flow across all consumers (GHI #654)
- Replaced the ADR-0.0.37 canon→AGENTS.md derivation facade with a content-coherence gate that fails closed unless the committed rendition contains every corpus invariant-tier entry verbatim (GHI #623)
