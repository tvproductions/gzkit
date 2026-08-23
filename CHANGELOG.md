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
