# Check Behaviors — Pass C

> Chore: `control-surface-rule-vs-check-drift` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 extraction.
> **Read from the implementation, never from the rule's claim about itself** —
> that asymmetry is the whole point of Step 3.
> Scope this run: the **13 validator files changed since `0551bbbd3`** (+1951 lines).

The single highest-value field per validator is **EXEMPTS**. A check with a broad
waiver enforces far less than its prose implies, and that gap is what this chore
exists to find.

---

## New validators

### `status_writer_coverage.py` — `--status-writer-coverage` (GHI #669)

- **ENUMERATES:** `(project_root/"src"/"gzkit").rglob("*.py")` (`:232`). Files that fail `ast.parse` or raise `OSError` are skipped **silently** (`:236-237`).
- **ASSERTS:** AST, not regex. Every `ast.Call` whose callee is in `_STATUS_WRITE_PRIMITIVES = {"_upsert_frontmatter_value", "rewrite_governed_keys_in_place"}` (`:30-32`) and that `_touches_status_key` (`:115-138`) must sit inside a function textually referencing one of `_SANCTIONED_MONITORS` (`:42-44`). Enclosing function resolved by **qualified** name (`Class.method`, `:79-100`).
- **EXEMPTS:** `_REGISTERED_WRITERS` (`:53-76`) — four hardcoded `path::function` keys, each carrying a prose reason; an **empty reason is itself a finding** (`:189-200`). Counter-waiver: a register entry no live call site needs is reported as inert (`:247-259`), so **the register cannot rot.**
- **POSTURE:** fail-closed **exit 3** — `"status_writer_coverage"` is in `_POLICY_BREACH_ERROR_TYPES` (`validate_cmd.py:1152`); ERROR-level step in `gz check` (`quality.py:482`).
- **Assessment:** the best-shaped waiver in this batch. It is bounded, justified per entry, and self-cleaning in both directions.

### `transcribed_counts.py` — `--transcribed-adr-counts` (GHI #768)

- **ENUMERATES:** **opt-in registry only** — `data/transcribed_count_surfaces.json` (`:42, :90-100, :157-161`). Live registry holds **2 files**. No glob; anything unlisted is never scanned. Deliberate, per the module docstring: *"a blanket sweep would falsify the archive"* (`:24-30`).
- **ASSERTS:** per line, an ADR-id regex (`:48`) co-occurring with an `N/M` count (`:55`) whose ±24-char window contains a `_PROGRESS_CUES` token (`:63-74, :108-115`). A dangling registry path is its own finding (`:162-175`).
- **EXEMPTS:** three layers — (1) everything outside the registry; (2) per-surface `historical_sections` by heading-substring, shallowest level, subsections inheriting (`:103-105, :118-150`); (3) inline `<!-- historical-count -->` (`:45, :145`).
- **POSTURE — DRIFT:** advertises **exit 3**, actually **exit 1**. Flag help says *"Exit 3 on any (#768)"* (`parser_maintenance.py:984`) and `"transcribed_adr_counts"` **is** registered in `_POLICY_BREACH_ERROR_TYPES` (`validate_cmd.py:1153`) — but the validator emits `ValidationError(type="surface", …)` (`:165, :182`), and `"surface"` is not in that set, so the run routes to `SystemExit(1)`. **The policy-breach registration matches nothing and is inert.** Verified first-party this run.

### `taxonomy.py::audit_pool_interview_schema` — `--pool-interview` (GHI #719)

- **ENUMERATES:** `docs/design/adr/pool/*-interview.json` (`:97, :207`); `[]` if the pool dir is absent (`:203-204`).
- **ASSERTS:** grammar delegated to the CLI's own `answer_payload_problems("adr", payload)` (`:195, :224`) **so reader and validator cannot diverge** — the right shape. Plus pool-only identity checks (`:103-141`) and completeness (`:233-239`). An unreadable record is a **finding, not a skip** (`:209-221`).
- **EXEMPTS:** **none.** No waiver constant, no allowlist.
- **POSTURE:** fail-closed exit 1 (`type="pool_interview_schema"`, not a policy-breach type); runs in `gz check` (`quality.py:473`).

---

## Changed validators

### `taxonomy.py::audit_adr_taxonomy` — `--taxonomy`

- **ASSERTS — real narrowing of a silent fail-open (GHI #736):** frontmatter now read through the shared tri-state `read_frontmatter_bytes` (`:581-593`). Previously a malformed/BOM'd ADR returned `None` and was **skipped**; now `state == "malformed"` produces a finding (`:288-304`) and only `absent` returns `[]` (`:305-306`).
- **EXEMPTS:** `_parse_adr_frontmatter` survives as a permissive shim **for `sensitivity.py` only** (`:595-604`), still collapsing absent+malformed to `None`. **The old fail-open persists on that one consumer path.**
- **POSTURE:** fail-closed exit 1; default tier, so it runs on a bare `gz validate`.

### `taxonomy.py::audit_obpi_lifecycle_coherence` — `--obpi-lifecycle-coherence`

- **ASSERTS:** two arms now. The existing orphan census (`:695-706`), plus a **new park-coherence arm (GHI #774)** — an OBPI parked while its parent is a live non-pool ADR (`:707-731`). Input is `non_pool_brief_owners` (`:633-666`), reading Layer-1 placement off disk. The docstring explicitly rejects two easier inputs (`_live_adr_ids` flagged all 371 parked OBPIs; `rename_chain_target` resolves demote/promote cycles back to the pool id) — **a validator that documents the wrong answers it rejected.**
- **EXEMPTS:** briefs under a `pool` path segment (`:661`).
- **POSTURE:** fail-closed exit 1.

### `release.py::audit_advisory_scorecard` — `--advisory-scorecard`

- **ASSERTS — five arms, four new:** (1) coverage-ledger version **equality** (`:121-124, :699-754`), replacing a filename-stem proxy *"no edit to an existing rule file could ever falsify"* (`:665-670`); (2) `_summary_drift_errors` recounts the Score column (`:210-242`); (3) `_unreachable_ruff_claim_errors` — a Mechanical row citing a ruff code `select`/`ignore` would not run (`:318-419`); (4) `_missing_witness_path_errors` — a Mechanical row citing a non-existent witness path (`:463-552`); (5) `_prose_promotable_errors` — prose outside a scored row assigning **Promotable** (`:562-630`).
- **EXEMPTS — the widest waiver in this batch:** `data/advisory_scorecard_grandfather.json` (`:128, :633-655`) freezes **16 canonical rules** at pinned versions; while pinned, the version-equality arm is **skipped entirely** (`:706-709`). Shrink-ratchet, version-pinned — editing the rule breaks the pin (`:710-726`). Secondary: arms 3–5 gate to **Mechanical** rows only (`:379, :521`), so a Judgment-scored disclosure is never punished; `_is_executable_witness` (`:437-460`) waives anything containing a glob char and counts only hook scripts, `src`/`tests` `.py`, and `.feature` files; a missing Summary table is **clean by construction** (`:217-219`).
- **POSTURE:** fail-closed exit 1.
- **Note:** arm 4 is the direct mechanical answer to the false-Mechanical-claim class (rows 18/19/20) — but it checks only that a cited *path exists*, never that the cited *behavior* is what the code does. This run produced a live instance it cannot catch: see § Cross-cutting drift 1.

### `cli.py::audit_cli_alignment` / `audit_manpage_alignment` — `--cli-alignment`

- **ENUMERATES — materially widened (GHI #745):** `docs/**/*.md` (minus `docs/releases/`) + `features/**/*.feature` + `.gzkit/skills/**/SKILL.md` (`:114-152`). The docstring states outright *"the enumeration WAS the blind spot"*.
- **ASSERTS:** extraction delegated to shared `extract_verb_references`; resolution via `verify_gz_chain` walking the live parser tree at **every** level (`:200-231`), so `gz adr bogus` now fails where a first-token-only check passed (GHI #588/#748). Three local regexes were deleted.
- **EXEMPTS:** `_is_exempt_source` (`:155-186`) — **any path containing `design/adr/pool/`**, self-quantified in the docstring as *"530 sites across 79 files"*; sealed records (`/audit/` paths, `_SEALED_ADR_ARTIFACTS`, terminal briefs); per-reference `<!-- gz-validate-skip: command-shape -->`; and `_DOC_PROSE_VERBS = frozenset()` (`:20`) — an **empty, inert waiver hook** still consulted at `:206`.
- **POSTURE — DRIFT:** `.gzkit/rules/governance-core.md:53` says *"Exit 3 on any unresolvable reference."* Neither `type="cli_alignment"` (`:224`) nor `type="manpage_alignment"` (`:298`) is in `_POLICY_BREACH_ERROR_TYPES` → `SystemExit(1)`. Verified first-party this run.
- **Known scope gap:** `.gzkit/rules/**` is not in `_manpage_alignment_sources` (`:237`), so the rule surface sits outside its own binding. Also carried as Pass A row R03.

### `lock_exchange_coupling.py` — `--lock-exchange-coupling` (renamed from `--lock-handoff-coupling`)

- **ASSERTS:** five arms per `obpi_lock_released` event — `handoff_path` present (`:66-77`); file exists (`:79-92`); **NEW** path is in `git ls-files` (`:93-110`, GHI #759 — *"memory is not evidence"*); timestamp ordering; minimum-information fields plus a `## Decisions Made` section; **NEW** `_check_mode` rejects a cited record whose `mode:` is `CHECKPOINT` (`:277-310`, GHI #756).
- **EXEMPTS:** **dated-cutover waiver** — every event older than the cutover is skipped (`:61`), the cutover derived from the ledger's latest `OBPI-0.0.41-02/03` receipt (`:164-175`). **If no cutover receipt exists the entire audit returns `[]`** (`:51-52`). The new git-index arm waives itself when git is unavailable (`:93, :152-160`).
- **POSTURE:** fail-closed **exit 3** (`validate_cmd.py:1162`); solo scope.
- **Note:** the `type=` string was renamed in lockstep with the module, so any consumer keyed on `"lock_handoff_coupling"` silently stops matching.

### `events.py::audit_event_handlers` — `--event-handlers`

- **ASSERTS:** every emitted event type is claimed by a graph handler unless waived (`:214`); **and** every waiver corresponds to a still-emitted type — a stale waiver is its own finding (`:227`).
- **EXEMPTS:** `_NO_GRAPH_IMPACT` (`:21`), **widened by two entries this window**: `session_exit_bookmark_skipped` (`:22-31`) and `handoff_resume_decided` (`:40-48`), both on "session-scoped, not artifact lineage" grounds. Self-cleaning, but **prose-gated**: nothing checks a rationale is *true*, only that it exists.

### `distribution.py` — `--distribution`

- **EXEMPTS — widened:** `_is_package_only` now returns True for `("package_only", "runtime_state", "project_local")` (`:84`); `project_local` is new (GHI #728). Breadth depends on a per-surface classifier, so **the constant names no files** and the waiver's actual reach is not readable from the waiver.
- **POSTURE:** fail-closed exit 3.

### `brief_reconcile.py` / `waiver_ratchet.py`

- **Changed comments only.** `brief_reconcile.py`'s two `except Exception` blocks gained `# noqa: BLE001` with rationale after ruff `BLE` was enabled; `waiver_ratchet.py` updated a docstring reference. **No assertion changed in either.** Recorded so a diff-size reader does not mistake them for behavior changes.

### `_qc_negative_controls.py` — `gz qc` harness (no `gz validate` flag)

- **Seven new negative controls** this window: `pool-interview-schema`, `advisory-scorecard-coverage`, `advisory-scorecard-summary-drift`, `advisory-scorecard-ruff-reachability`, `validate-default-scopes`, `status-writer-coverage`, `transcribed-adr-counts`.
- Several plant **both poles** — a violation the audit must catch *and* a legitimate case it must leave alone — so a control cannot pass against an over-broad audit. That is the strongest pattern in this batch.
- **EXEMPTS (in effect):** entrypoint-side filters — `_ep_status_writer_coverage` keeps only findings whose artifact contains `"rogue_writer.py"`; `_ep_transcribed_adr_counts` keeps only findings containing `"Draft"`. Documented as necessary so a control cannot pass on the wrong evidence.

---

## Cross-cutting drift found by reading the code

1. **Two scopes advertise exit 3 and deliver exit 1.** `--transcribed-adr-counts`
   (registered as a policy-breach type but emitting `type="surface"`, so the
   registration is inert) and `--cli-alignment` (whose *rule* claims exit 3 while
   neither of its error types is registered). Both still fail `gz check`; only the
   policy-breach classification is wrong. **Neither is catchable by
   `_missing_witness_path_errors`, because the cited paths all exist** — the arm
   checks that a witness is *present*, never that it *behaves as claimed*.
2. **Widest waivers by reach**, for whoever tightens: the 16-rule advisory-scorecard
   grandfather (version-equality skipped entirely while pinned); the whole-file
   `design/adr/pool/` exemption in `audit_cli_alignment` (self-described 530 sites
   across 79 files); and `--transcribed-adr-counts`' opt-in registry (2 files
   scanned by design).
3. **One waiver that cannot rot, as the counter-example:**
   `status_writer_coverage.py`'s `_REGISTERED_WRITERS` reports its own stale
   entries (`:247-259`) and rejects an empty justification (`:189-200`). It is the
   shape the other three should be measured against.
