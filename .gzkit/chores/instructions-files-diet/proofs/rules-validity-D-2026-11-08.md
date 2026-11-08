# Rule validity review — batch D

Read-only review, 2026-11-08, gzkit HEAD `532a071b9`. The rules are `chores` 0.6.4, `mx-mode` 1.16.0, `model-selection` 0.8.0, `skill-authoring` 0.2.1, `skill-surface-sync` 0.14.0 and `agents-md-map-doctrine` 0.13.1.

Key: V = validity (T TRUE / S STALE / U UNVERIFIABLE). U = usefulness (N NEEDED / R REDUNDANT / O NO-OP). Line numbers refer to `.gzkit/rules/<rule>.md`.

Background fact for every rule. Each rule is delivered twice. Claude gets the path-scoped `.claude/rules/<rule>.md`. The same body is also rendered into a nested `AGENTS.md` (`.gzkit/chores/AGENTS.md` 10,228 B, `src/gzkit/mx/AGENTS.md` 11,923 B, `.gzkit/skills/AGENTS.md` 26,306 B). Every rule in this batch is over the 4,000-char per-file budget (`data/instructions_files_budget.json`). For example, `gz validate --instructions-files-budget --verbose` reports: "`.claude/rules/chores.md is 8325 chars, exceeds 4000-char budget by 4325`".

---

## 1. chores.md (8,413 B) — KEEP-PARTIAL

| # | Clause (line) | V | Evidence | U | Why |
|---|---|---|---|---|---|
| C1 | Edit `.gzkit/chores/` only; the package copy is generated (21-22) | T | `sync_pkg_surfaces` copies `.gzkit/chores` → `src/gzkit/chores` for canonical-class files only (`src/gzkit/sync_surfaces.py:933-964`) | N | Root AGENTS.md § Skills names `.gzkit/skills` only. Nothing in always-on context tells an agent that edits under `src/gzkit/chores/**` that its edit will be overwritten. |
| C2 | Surface table: canonical vs distribution, runtime fallback via `importlib.resources("gzkit.chores")`, doctor source (24-27) | T | `_package_chores_root` `commands/chores.py:146-148`; `_repair_damaged_doctor_slug` reads `importlib.resources.files("gzkit.chores")` (:523) | R | Duplicates `.gzkit/skills/skill-surface-sync.md` § Surface layout row 5 and `.gzkit/chores/README.md` § Two-Surface Layout. |
| C3 | A correction in `src/gzkit/chores/` is overwritten by the next sync; the registry is authored at `.gzkit/chores/registry.json` and ships filtered (29-31) | T | `sync_surfaces.py:951-957` writes `exportable_registry(src_file)` (GHI #728) | N | Same reason as C1. **Coupled defect:** `.gzkit/chores/README.md:57` says the opposite: "The registry at `src/gzkit/chores/registry.json` (canonical)". |
| C4 | Resolution order project-first → package-fallback, registry the same; `list --explain` labels `project`/`package`/`missing` (33-38) | T | `_resolve_chore_dir` and `_resolve_registry` (`chores.py:169-220`); `_explain_source` returns `"package (fallback; scaffolder may need re-run)"` / `"project"` / `"missing"` (:292-298) | R | `gz chores list --help` says "Show which resolution path (project\|package) won per chore". The README carries the same text. |
| C5 | `proofs/` is always project-local, never canonical (40-42) | T | `_classify_chore_file` puts `proofs/**` in `runtime_state` (`chores/__init__.py:111-127`); all 41 chore dirs have `proofs/`; none under `src/gzkit/chores/*/proofs` | R | The classifier enforces it at sync, and README:29-31 says the same. |
| C6 | Doctor table MISSING / DAMAGED / HEALTHY / PROJECT-LOCAL and actions (44-52) | T | `_classify_doctor_slug` (`chores.py:498-513`); `_repair_damaged_doctor_slug` rewrites every differing file (:516-535) | R | `gz chores doctor --help`: "restore them from the package source. Project-local slugs and proofs/ content are never modified." |
| C7 | DAMAGED replaces surviving edited files, so run `--dry-run` first and sync unsynced edits (54-56) | T | :531-535 overwrites when `existing != canonical_bytes` | N | This is a data-loss gotcha that `--help` does not state. |
| C8 | Plan-first (62) | U | Scorecard row 54: "no queryable witness" | R | `gz-chore-runner` steps 2-3 (plan, advise) run at that moment. |
| C9 | Lite by default: `uv run gz test` (unit tier only), no behave (63) | T | `gz test --help`: "Default = full unittest suite … --bdd adds behave scenarios" | R | `gz-chore-runner` reads the lane from `gz chores show`. AGENTS.md § Gate Covenant: "`behave` belongs to heavy-lane OBPI work and to CI". |
| C10 | Small diffs (64) | U | — | O | AGENTS.md DO IT RIGHT 11 already says "Surgical changes". |
| C11 | CLI evidence / never raw SQL; Prohibited Evidence list (65, 143-147) | U | gzkit has no SQL database. Evidence is the JSONL ledger, written only through `gz` (AGENTS.md § Behavior Rules). | O | Carried over from AirlineOps. No path in gzkit can produce SQL attestation. |
| C12 | Layout discipline: `gz validate --chores-layout` (66) | T | Ran it: `Validated: chores_layout ✓ All validations passed (1 scopes).` | R | The witness fails closed on violation. |
| C13 | Suppression is not a repair (70) | T | Doctrine; `docs/governance/chore-class-system.md` § Suppression | N | Unwitnessed at run time. Nothing else in context says that `# noqa` is manufactured evidence. (`gz-chore-runner`:130 repeats it, but only as a pointer back to this rule.) |
| C14 | Mechanical arm: `SHELL_OPERATORS_RE`, `audit_chore_suppression` (72) | T | `commands/chores.py:26` `SHELL_OPERATORS_RE = re.compile(r"&&\|\|\||[\|<>]")`; `governance/trust_audits/chores.py:507` | R | The witness fails the registry. |
| C15 | Advisory arm: a marker hand-written during a run is not detected; review the diff (73) | T | Scorecard 56b | N | Same as C13. |
| C16 | Command sequences §1-§5 (79-126) | T | All verbs resolve: `gz chores {list,show,plan,advise,run,status,audit,doctor,…}`; `audit (--all \| --slug)`; `doctor [--dry-run] [--json]`; `gz lint [--fix]` | R | `gz-chore-runner` SKILL.md steps 1-9 and `gz chores --help`. |
| C17 | Apply Advice steps 1-5 (97-101) | U | — | O | Generic TDD/todo procedure. |
| C18 | "Lite default does not waive the full per-change gate the pre-push hook runs" (133-134) | T (normally) | `.pre-commit-config.yaml:183` `gz-check-pre-push` runs **through `gzkit.mx.alarms`**, so it is off under the open drydock marker | R | Hook-enforced. |
| C19 | Heavy evidence: `uv run behave features/<feature>.feature --tags=@schema` (140) | **S** | No feature file in `features/` carries an `@schema` tag. Tag census: `@dispatch 31, @covers 23, @review 12, @stage 6, @parse 4, @slow 2, …`. | — | Dead example. |
| C20 | Authoring a new chore: author in `.gzkit/chores/<slug>/`, sync, never edit the package copy; file table (151-161) | T | Same as C1. All 41 slugs carry CHORE.md, acceptance.json, README.md and proofs/. | R (except the edit-site sentence, already counted under C1) | `.gzkit/chores/README.md` § Chore Directory Structure. |
| C21 | Related links (168-171) | T | All four paths exist | R | — |

Totals: 21 clauses. V: T 17 / S 1 / U 3 (C8, C10, C11; C17 is also policy). U: N 5 (C1, C3, C7, C13, C15) / R 12 / O 3, with C19 not scored.

**Survives (about 1,700 B):** C1+C3 (edit site, overwrite, authored registry; about 450 B), C7 (about 200 B), C13+C15 (§ Suppression without the mechanical arm; about 1,000 B).

---

## 2. mx-mode.md (12,033 B) — KEEP-PARTIAL

| # | Clause (line) | V | Evidence | U | Why |
|---|---|---|---|---|---|
| M1 | Honor the marker: when the condition is on, most guards drop to advisory (23) | T | `checkpoint.resolve` (`mx/checkpoint.py:17-37`) | R | The awareness banner fires every turn. Ran it: "SAFE MODE ACTIVE — … most guards advisory; slow alarms off, lint and fast static checks on; gate5_invariants, the ledger through gz verbs and operator PII still bind …". |
| M2 | Condition is on only when present, parses, bound to an open `mx_session_opened`, not `exiting`; a hand-made marker lowers nothing; recovery `gz mx repair` (25-30) | T | `marker.condition` (`mx/marker.py`): `absent`/`unreadable`/`unbound`/`exiting` causes; `gz mx --help` lists `repair` | N | For an agent editing `src/gzkit/mx/**` or `guards.py`, this is the contract every reader must honour (GHI #1273: "each reader interprets the marker its own way"). |
| M3 | Readers that raise protection keep the file's presence (30-31) | T | `marker.is_active` is presence only; docstring of `condition`: "A reader that raises protection on the file itself keeps :func:`is_active`" | N | Non-obvious design choice for code in the glob. |
| M4 | The marker is committed; condition belongs to the repo/CI (31) | T | `.gzkit/mx.json` tracked; `gz-mx` skill: "Commit the repaired marker" | R | gz-mx skill § Repairing the marker. |
| M5 | CI `full-strength-report` sets `GZKIT_MX_FULL_STRENGTH`, reports without failing (32-33) | T | `.github/workflows/ci.yml:122-126` (`continue-on-error: true`, `GZKIT_MX_FULL_STRENGTH: "1"`); `checkpoint.full_strength_requested` | N | Needed by anyone editing `hangar_demotes`. |
| M6 | Before every action where `mx.json` exists, confirm the hangar is open (35-36) | T | — | R | The banner is injected every turn (`.claude/hooks/mx-awareness.py`, UserPromptSubmit). |
| M7 | `gate5_invariants` remain fail-closed (38) | T | `resolve`: `if guard_name in GATE5_INVARIANTS: return route(CRITICAL)` | R | The banner says "gate5_invariants … still bind", and the floor is pinned by tests (scorecard 62a). |
| M8 | Both enforcement surfaces honor the marker; a demoted pre-commit finding prints `[MX advisory]` (39-42) | T | `hooks/guards.py` `run_guards` → `checkpoint.demote_notice`; `validate_cmd._route` prints the same to stderr | N | A new guard in `guards.py` or a new validate scope must route through the checkpoint. That is the defect GHI #843 recorded. |
| M9 | Demotion never reaches an integrity guard; `ledger` and `gate5-attestation` are members; the route out is an append-only corrective-action primitive (GHI #611) (43-47) | T | `GATE5_INVARIANTS = {gate5-attestation, secrets, operator-pii, ledger, grader-gaming}` (`mx/invariants.py`). The primitive now exists as `gz ledger correct` (`gz ledger --help`); #611 is still OPEN for the general case. | N | Partial: the clause could name `gz ledger correct`. |
| M10 | The MX awareness hook fires every turn (48) | T | Hook wired in `.claude/settings.json:197` | O | Self-evident: the banner itself shows it. |
| M11 | Two opt-in mechanisms, NAME vs LEVEL; `resolve` is the whole decision (52) | T | `checkpoint.resolve` | N | Core guidance for editing guards (GHI #855). |
| M12 | NAME is a one-way door, forbidden for a narrower proxy (54) | T | `invariants.py` "`_GATE5_NAMED_NOT_ENFORCED`… binding a NARROWER PROXY entrypoint … is FORBIDDEN" | N | Judgment (scorecard 62e). |
| M13 | LEVEL: emit CRITICAL (55) | T | `_GUARD_META` (`guards.py:592-599`); `_STEP_GUARD_META` (`commands/quality.py:61-`) | N | — |
| M14 | Default to LEVEL; precedent `84519da5` (57) | T | `git show 84519da5`: "Repaired by LEVEL, not by NAME" | N | — |
| M15 | Floor-pinned by LEVEL today: `post-authoring-src-commits`, `enforcement-floor`, `forbid-pytest`, the `Lint` and `Complexity ceiling` steps, and the `complexity_ceiling`, `bullet_retention`, `surface_weight`, `pointer_anchors` scopes; the alarm switch never wraps their hooks (59) | T, but incomplete | Confirmed in `guards.py:593-598`, `quality.py:63,100,148`, `validate_cmd.py:418-505`. The list omits `authorship` (`validate_cmd.py:231` and `quality.py:143` "Authorship policy", both CRITICAL), although M14 names it as the precedent. `.pre-commit-config.yaml` wraps none of these hooks in `gzkit.mx.alarms`. | R | Tests pin it (scorecard 62h/62i: `tests/mx/test_alarms.py::TestFastStaticStaysArmed`). An enumerated inventory in prose drifts. |
| M16 | Stage-2 fence pin is permanent (GHI #855) (59) | T | `guards.py:596` CRITICAL | N | It is an operator ruling, and the code comment still calls it "PRESERVE today's behaviour rather than to rule on it" (`guards.py:582-584`). The code comment is the stale side. |
| M17 | An unregistered guard name resolves CRITICAL (61) | T on the validate surface only | `validate_cmd.py:988-989` `scope_levels.get(scope, _mx_levels.CRITICAL)`. `checkpoint.resolve` itself has no registry and demotes any unknown name at ERROR. On the pre-commit surface a guard missing from `_GUARD_META` simply never runs. | N | Partly misleading, because line 52 says "`resolve` is the whole decision". |
| M18 | Mechanical-witness paragraph; tests listed (63-71) | T | All 5 test files exist (`tests/mx/test_checkpoint.py`, `test_disposition.py`, `test_gate5_invariants.py`, `test_check_step_checkpoint_seam.py`, `test_gate5_invariants_live_nc.py`) | R | The witnesses fail with their own messages. Keep only "a new guard inherits demotion by default". |
| M19 | Out of service is one state; hangar and drydock are synonyms; alarm test; return to service package; governors-off care; advisory until GHI #1303/#1304 (75-82) | T | `docs/governance/safe-mode-doctrine.md` § Out of service and the four levels; `gz mx enter --help` still has `--level {hangar,drydock}` (#1303 and #1304 both OPEN) | R | `gz-mx` SKILL.md § Overview carries the same paragraph almost word for word. The skill runs at entry and exit. |
| M20 | Safe mode entry `gz mx enter --level drydock --contract`; marker `level`/`contract`; old `mode` aliases (86-88) | T | `Marker.level` with `AliasChoices("level","mode")`; the live marker carries `"mode": "safe"` | R | gz-mx skill § Workflow — safe mode step 2. |
| M21 | What safe mode suspends: OBPI initiation + brief ceremony (90-91) | T | Doctrine: "the contract suspends the initiation clause for repair orders and the brief ceremony" | R | The banner: "OBPI initiation and brief ceremony are suspended". |
| M22 | What still binds: gate5, ledger via verbs, PII, secret scan, no control removed, PD trackability, lint + fast static; every other guard advisory and slow alarms off; `hangar_demotes` true under either mode; exit re-runs all (92-97) | T | `checkpoint.hangar_demotes`; `alarms.alarms_off` is true only at `level == "drydock"`; `.pre-commit-config.yaml:92,99,183,215` route through `gzkit.mx.alarms`; gitleaks and authorship are not wrapped | R (prose); N (one point) | The banner and gz-mx carry the list. Code editors need one point: `hangar_demotes` covers both levels, while `alarms_off` covers drydock only. The rule does not state that split, and safe-mode-doctrine does. |
| M23 | What it records: one commit per act with `Task:` trailer; no long check per act; list of discrepancies; passage log (98-101) | T | Doctrine § The instruments item 5 | R | gz-mx skill step 3, the banner, and the contract itself. |
| M24 | Contract pinned: SHA-256 + § What is suspended + § Exit at entry; `mx_contract_amended` per committing edit (102-106) | T | `mx/contract.py:24-48,71-93` | R | gz-mx skill step 2 says the same. |
| M25 | Who restores: each repair order reattaches every safeguard it disconnected (107-109) | T | Doctrine | R | It belongs to the contract and the skill handback. |
| M26 | How it ends; doctrine and template pointers (110-113) | T | Paths exist | R | — |
| M27 | Witness list for safe mode (115-116) | T | `TestSafeMode` (`tests/mx/test_checkpoint.py:157`), `TestMxEnterSafeMode` (`tests/commands/test_mx_enter.py:227`), `tests/hooks/test_mx_awareness.py`, `tests/mx/test_contract_pin.py` all exist | R | — |
| M28 | Lease = `mx-session` lock TTL `DEFAULT_LOCK_TTL_MINUTES` (120-121) | T | `lock_manager.py:29` `= 24 * 60`; `marker.SESSION_LOCK_KEY = "mx-session"` | N | Code fact for `lease.py`/`hardening.py`. |
| M29 | Past the lease nothing is evicted; one `mx_session_lease_expired` booked; reaper leaves the lock (122-124) | T | `mx/lease.py` `book_lease_expiries` | N | Code contract. |
| M30 | Advisory debt ages per contract (125-128) | T | `gz validate --mx-hardening`: "MX session 57346836… has carried advisory debt for 532.7h at WARNING" | N | — |
| M31 | `gz mx renew` lease-only (129-132) | T | `gz mx --help`: "renew  Renew the open session's lease; runs no guard" | R | gz-mx skill step 3. |
| M32 | Lease and debt never block exit; exit holds the marker `exiting` (133-134) | T | `Marker.exiting`; `condition` cause `exiting` | N | — |
| M33 | What grounds: a dangling session; more than one open session (135-136) | T | `gz validate --mx-hardening` witness (`NC:mx-hardening`) | R | The witness fails with its message. |
| M34 | Safe mode differs: fix-immediately waits for exit; trackability via punch list; lint swept per act (143-146) | T | Doctrine § The instruments 5 | R | The banner says "what it breaks goes on the punch list". |
| M35 | In the hangar: fix what you know and what you find; "out of scope" forbidden; advisory guards are no license to defer (148-154) | T | — | R | AGENTS.md § PRIME DIRECTIVE 1-5, always in context. |
| M36 | Operate the skill, not the shell (158-159; Do Not 163) | T | — | R | `gz-mx` SKILL.md: "nobody shells out to `gz mx enter` or `gz mx exit` directly." `gz mx enter --help` also requires an operator `--attestor`. |
| M37 | Do not treat advisory guards as license to defer / do not conflate advisory with PD suspended (164-165) | T | — | R | AGENTS.md PRIME DIRECTIVE; M35 |
| M38 | **Do not exit the hangar while any detectable defect remains unfixed** (166) | **S** | Contradicted by the doctrine for the open (drydock) session and by the 2026-11-03 single-state ruling. `safe-mode-doctrine.md` § The instruments 5: "The exit clears every line that blocks return to service, and the handback transfers the rest". The 2026-11-03 ruling also says hangar and drydock are synonyms, so the rule's own split (M34 "The hangar below is unchanged") no longer gives the clause a separate scope. | — | — |

Totals: 38 clauses. V: T 37 / S 1 / U 0. Three clauses are TRUE but incomplete or misleading (M9, M15, M17). U: N 16 (M2, M3, M5, M8, M9, M11-M14, M16, M17, M28-M30, M32, plus the one point from M22) / R 20 / O 1, with M38 not scored.

**Survives (about 4,600 B):** § Honor the marker, condition definition, CI switch and both-surfaces lines (M2, M3, M5, M8, M9; about 1,300 B). § Opting a guard into the floor (M11-M14, M16, M17, corrected to say the CRITICAL fallback is validate-surface only, and dropping the inventory list M15; about 2,000 B). The lease code contract (M28-M30, M32; about 900 B). One line on `hangar_demotes` (both levels) vs `alarms_off` (drydock only) (about 200 B). Everything in § Safe mode, § Out of service, § PRIME DIRECTIVE, § Operate the skill and § Do Not is already carried by the `gz-mx` skill, the banner, safe-mode-doctrine or AGENTS.md.

---

## 3. model-selection.md (6,549 B) — KEEP-PARTIAL

| # | Clause (line) | V | Evidence | U | Why |
|---|---|---|---|---|---|
| S1 | Tier by decision complexity, not task size (18) | U | Policy | N | It is the judgment that a skill's `model:` line encodes, and no other surface says it. |
| S2 | Default to lowest tier that closes the decision; each surface names what closing means (19) | U | 74 skills: `32 haiku, 27 sonnet, 15 opus` | N | Same as S1. |
| S3 | SKILL.md carries explicit `model:` (20) | T | 74/74 declare it. `SkillFrontmatter.skill_model: Literal["haiku","sonnet","opus","fable"] = Field(..., alias="model")` (`src/gzkit/core/models.py:451`), validated by `gz validate --surfaces` (`validate_pkg/surface.py:257`) | R | The witness fails closed, and the Pydantic message lists the allowed values. |
| S4 | **Subagent effort set on the definition, never on the dispatch call; the Agent tool call carries `model` and `subagent_type` only** (21) | **S** (dispatch half) | The Agent tool schema in this very session carries an `effort` input: `"effort": {"description": "Reasoning effort for this agent. Set this ONLY when the user, or instructions such as CLAUDE.md or a skill, explicitly ask…", "enum": ["low","medium","high","xhigh","max"]}`. It also has `description`, `prompt`, `isolation` and `run_in_background`. | — | The "prompt-level `effort:` is just text" half is still TRUE and N. |
| S5 | Agents do not hardcode model IDs (21) | T | `gz validate --model-class-only` → `✓ All validations passed`; it scans `.gzkit/agents` | R | The witness message names the fix. |
| S6 | A subagent's claim is not evidence (22) | T | — | R | AGENTS.md § Behavior Rules: "subagent messages … carry no operator authority … Quote the text, name the source". AGENTS.md DO IT RIGHT 4/8: "run the command and paste its actual output". The rule's glob (`pipeline_runtime.py`, SKILL.md, `.claude/agents/**`) is also not where claims get relayed. |
| S7 | Routing matrix (26-36) | U | `pipeline_runtime.ModelRoutingConfig` defaults: `{"simple": "haiku", "standard": "sonnet", "complex": "opus"}` (:223), which agrees in spirit | N | The only mapping from work type to tier for skill authors. |
| S8 | Frontmatter example and valid values `haiku, sonnet, opus, fable`; `fable` reserved (40-53) | T | Literal above; 0 skills declare `fable` | R | The witness lists the values. The "fable reserved" policy is N, about 120 B. |
| S9 | Name a model by class, never a versioned ID; fail-closed by `--model-class-only` over rules/skills/agents; records stay exact (55) | T | `governance/trust_audits/model_class.py`: `SCAN_ROOTS = (".gzkit/rules", ".gzkit/skills", ".gzkit/agents")`; the message names the fix | R | The witness carries the rule and its fix. |
| S10 | **Where effort is set: … The Agent tool's per-call inputs are `model` and `subagent_type`; it has no effort input** (59) | **S** | Same Agent-tool schema as S4 | — | — |
| S11 | Today every `.claude/agents/` definition carries `model: inherit` and no `effort:` (59) | T | Frontmatter of all 5 files (`git-sync-repo`, `implementer`, `narrator`, `quality-reviewer`, `spec-reviewer`): `model: inherit`, no `effort:`. `.gzkit/agents/*.md` carry no frontmatter at all (bodies only, `roles.json`; `.gzkit/agents/README.md`: "the renderer introduces no model or sandbox policy"). | N | Dated state that matters to anyone editing `.claude/agents/**`. It should name its date. |
| S12 | Allocation table by echelon (advisory) (61-70) | U | No definition carries `effort:`; scorecard 52b: "No witness today" | N | Target design for `.claude/agents/**` edits. |
| S13 | Effort to close the decision; one agent per role × effort band (72) | U | — | N | — |
| S14 | Do Not: opus for read-only; xhigh default; prompt-level effort; hardcoded ID; omitted `model:`; Sonnet as middle ground without naming why (76-81) | T | Each restates S1-S10 | R | Restates the clauses above. The hardcoded-ID and omitted-`model:` bullets are witnessed. |

Totals: 14 clauses. V: T 7 / S 2 (S4, S10) / U 5. U: N 6 (S1, S2, S7, S11, S12, S13, plus the fable-reserved half of S8) / R 6 / O 0.

**Survives (about 2,600 B):** S1, S2, the routing matrix S7, the fable-reserved sentence, and § Subagent effort levels (S11-S13) rewritten. The rewrite must remove "the Agent tool … has no effort input" and S4's "the Agent tool call carries `model` and `subagent_type` only". Keep the observation that a prompt-level `effort:` line is inert.

---

## 4. skill-authoring.md (5,658 B) — KEEP

| # | Clause (line) | V | Evidence | U | Why |
|---|---|---|---|---|---|
| A1 | Skills are canonical files, not corpus; review is their control; three chores read this rule (14) | T | `agent-control-surface-rendering-substrate.md:7` § Binding claim; chores `skill-authoring-quality`, `instructions-files-diet`, `frontier-model-card-currency` exist | R | Orientation prose. |
| A2 | Procedure plus judgment; a one-command alias is user-invoked or removed (18) | T | — | N | Not witnessed anywhere. |
| A3 | One-line description says when and what; it is the only part loaded every turn (19) | T | `SkillFrontmatter.description` max length; budget file "skill descriptions … max_chars 6000" | N | — |
| A4 | Every skill states its terminal state and what it does not do (20) | U | — | N | Supports AGENTS.md SKILLS FIRST ("When a skill's scope is narrow…"). |
| A5 | Parsimony 1: procedure stays, history leaves (24) | T | Scorecard 94 | N | Judgment, unwitnessed. |
| A6 | Parsimony 2: one home per meaning; AGENTS.md quoted from the current file or not at all (25) | T | Scorecard 95 | N | Top defect class (GHI #921, #1035). |
| A7 | Parsimony 3: name the verb, not its work (26) | T | — | N | — |
| A8 | Parsimony 4: branch test → `references/` (27) | T | `sync_pkg_surfaces` ships every `*.md` under the skill (GHI #1108) | N | — |
| A9 | Parsimony 5: red-flag rows must name an observed failure (28) | T | — | N | — |
| A10 | Parsimony 6: size is a finding; compress before lifting; commit says what was compressed (29) | T | `gz skill audit`: `SKA-BODY-OVERSIZED … above SKILL_BODY_MAX_LINES=300 … decompose before adding lines` | N (compress-first half) / R (threshold half) | AGENTS.md § Behavior Rules carries "A size limit triggers a compress-and-merge pass … say what was compressed". So the compress-first half is also R. |
| A11 | Model alignment preamble: follow `opus-tuning.md`/`gpt-tuning.md`, cite the doc, never a card (33) | T | Both docs exist | N | — |
| A12 | MA1 state scope and stop conditions (35) | T | `opus-tuning.md` § Recalibration: "both current Anthropic models expand task scope at higher effort by default" | N | — |
| A13 | MA2 no re-check step where a witness exists; no anti-laziness pressure (36) | T | Same section | R | CLAUDE.md § Model tuning: "add no verification or re-check steps the model already performs". |
| A14 | MA3 reserve MUST/NEVER for owned constraints (37) | U | — | N | — |
| A15 | MA4 keep written constraints; quote (38) | T | `opus-tuning.md:280-281` "Capability gains are not evidence that a written constraint has become less necessary." | N | — |
| A16 | MA5 state the behavior wanted (39) | T | — | N | It also duplicates map-doctrine § Writing levers "Positive target". |
| A17 | Authority lines (43-49) | T | AGENTS.md § OBPI Acceptance Protocol, § Behavior Rules (ghi-author), § Execution Rules ("never the operator's real name"), § Gate Covenant ("Gate 5 is universal") | R | Each line cites AGENTS.md, which is always in context. The last line ("run it and resolve it") is witnessed by `--cli-alignment`. |
| A18 | Enforcement posture: `gz skill audit` checks frontmatter, lifecycle, review age, mirror parity, body size, unfinished markers; `skill_contract.py`, `skill_body_grandfather.json` may only shrink; `--cli-alignment`, `--skill-alignment` (53) | T | `skills_audit.py` codes `SKA-BODY-OVERSIZED` (:666), `SKA-BODY-UNFINISHED` (:677), `SKA-MIRROR-DIR-MISSING` (:763), `SKA-LAST-REVIEWED-STALE` (:312); both files exist; `gz validate --help` lists both scopes | R (mechanics) / N (the sentence "qualitative parsimony … judged at authoring … repair that touches a skill is operator-only") | — |

Totals: 18 clauses. V: T 16 / S 0 / U 2 (A4, A14). U: N 13 / R 5 (A1, A13, A17, A18-mechanics; A10's threshold half is also R) / O 0.

**Survives (about 3,700 B):** § What a skill carries, § Parsimony, § Model alignment (minus MA2), and the last sentence of § Enforcement posture. § Authority lines (about 570 B) and the countable-check inventory (about 800 B) can go.

---

## 5. skill-surface-sync.md (6,959 B) — KEEP-PARTIAL

| # | Clause (line) | V | Evidence | U | Why |
|---|---|---|---|---|---|
| Y1 | R1 Edit `.gzkit/` first; every other copy is generated (19) | T | `sync_pkg_surfaces` reads only `.gzkit/` (REQ-0.0.32-08-01) | R | AGENTS.md § Skills: "Edit skills in `.gzkit/skills`; `uv run gz agent sync control-surfaces` regenerates every vendor mirror". AGENTS.md § Control Surfaces: "generated surfaces are not edited directly". The `forbid_skill_sync_drift` guard also enforces it. |
| Y2 | R2 Bump the version on every edit; skill `metadata.skill-version` quoted under `metadata:`; rule marker + block quote; `RuleFrontmatter` `extra="forbid"`; minor vs patch (20) | T | `SKA-METADATA-SKILL-VERSION-MISSING` (`skills_audit.py:511`); `RuleFrontmatter` `ConfigDict(frozen=True, extra="forbid")` (`rules/__init__.py:801`); `gz validate --rule-version-markers` passes | N | Presence is witnessed, but the *bump* on edit is not, and neither is the minor/patch convention. |
| Y3 | "do not skip sync because two files look the same (it also updates manifests and registrations)" (20) | U | — | R | Y4 covers it. |
| Y4 | R3 Run sync after every edit; one invocation writes the wheel copy and every enabled mirror (21) | T | `sync_all` → `render_rules_to_dir` + `sync_pkg_surfaces` (`sync_surfaces.py:1090-1140`) | R | AGENTS.md § Skills; guard `forbid_skill_sync_drift` (scorecard 33). |
| Y5 | R4 Never edit vendor mirrors; read roster from `.gzkit.json § vendors` (22) | T | `.gzkit.json` vendors: `{'claude': True, 'codex': True, 'opencode': False}` | R | AGENTS.md § Control Surfaces. The roster pointer is N, about 100 B. |
| Y6 | R5 Never edit `src/gzkit/<surface>/`; only `sync_pkg_surfaces` writes them (23) | T | `sync_surfaces.py:851` | N | AGENTS.md does not name the package copy. |
| Y7 | R6 `skill-version` bump requires `last_reviewed` bump (skills); 90-day audit (24) | T | `DEFAULT_MAX_REVIEW_AGE_DAYS = 90` (`skills_audit.py:27`); scorecard 33c: "Unenforced today" | N | Unwitnessed coupling. |
| Y8 | Surface layout table (28-34) | T | Rows check out: `.claude/personas`, `.agents/personas` exist; templates have no mirror; rules go to `.claude/rules` (Codex gets nested AGENTS.md, so there is no `.agents/rules`) | R | It describes the directory layout. map-doctrine's "Single source, and the environment counts" lever says not to cache that. |
| Y9 | **"If sync reports a mirror ahead of canonical, an agent edited the mirror … Same version with differing content means an unbumped edit — use the git timestamp"** (36) | **S** | No code reports a mirror "ahead". `render_rules_to_dir` and the skill mirror sync overwrite the mirror from canon. The only drift report is `validate_pkg/sync_parity.py:334`: "Generated surface is out of sync with canonical state. Run `uv run gz agent sync control-surfaces` to repair." That message tells the agent to run sync, which overwrites the mirror edit. It never says to promote the edit. `audit_generated_surface_drift` returns early whenever `.gzkit/rules/` exists (`instruction_audit.py:207-208`). | — | The recovery it describes cannot occur as written. |
| Y10 | Bootstrap: after `gz init` the adopter's `.gzkit/` is canonical; repair-mode idempotent `skip_existing=True`; `--force` wipes and re-copies (40) | T (partly U) | `gz init --help`: "Re-running on an initialized project repairs missing artifacts"; `--force  Override safety checks` (help does not say "wipes") | R | Adopter-side; not reached by a gzkit edit. |
| Y11 | Retirement: superseded skill dir deleted from every surface root in the same commit; no retired stub (44) | T | No `lifecycle_state: retired` SKILL.md remains in `.gzkit/skills` or `src/gzkit/skills` | N | — |
| Y12 | A retired rule leaves the same way; doctrine moves first to a named home (46) | T (policy, landed 6e6d35134) | — | N | Needed for this very review. |
| Y13 | Delete `.gzkit/rules/<name>.md`, sync removes vendor mirrors; sync never removes the package copy, so delete `src/gzkit/rules/<name>.md` by hand (GHI #1316) (48) | T | `render_rules_to_dir` removes a stale mirror bearing "Generated by gz agent sync" (`rules/__init__.py:1083-1091`). `_sync_classified_flat` only copies and never prunes (`sync_surfaces.py:827-848`). GHI #1316 is OPEN. | N | — |
| Y14 | Remove `data/distribution_baseline_manifest.json` entry, Coverage Ledger row, re-point scorecard rows (49) | T | File exists; scorecard 33d | N | — |
| Y15 | Re-point tests, validator messages, doc links, chore registry targets (50) | T | E.g. `tests/governance/test_agents_md_map_doctrine.py:53` `_RULE_PATH = … "agents-md-map-doctrine.md"` | N | — |
| Y16 | Attested-REQ test repaired at surface; a REQ asserting existence goes to the operator first; advisory in part (52) | T | GHI #1316, #1317 OPEN (`gh issue view`) | N | — |
| Y17 | Class-classifier table: canonical / package_only / runtime_state / **project_local *(chores only)*** (58-63) | **S** (the project_local row) | `_classify_skill_file` returns `Literal["canonical","package_only","runtime_state","project_local"]`, and its docstring says "project_local: every file under a slug whose `SKILL.md` declares `project_local: true` … (GHI #915)" (`skills/__init__.py:78-121`). Two skills declare it. `sync_surfaces.py:794` `_UNSHIPPABLE_SKILL_CLASSES = frozenset({"runtime_state", "project_local"})`. The `package_only` row also omits retired skills, which `_classify_skill_file` classifies `package_only`. | — | — |
| Y18 | Declare a project-local chore with `"projectLocal": true`; shipped registry filtered (GHI #728); both validators read `_classify_<surface>_file` (65) | T | `exportable_registry` (`sync_surfaces.py:951-957`); classifiers in `chores/rules/skills/personas/templates/__init__.py` | N | The project-local declaration is N. The skill side (`project_local: true` in SKILL.md frontmatter) is missing and is N. |

Totals: 18 clauses. V: T 15 (Y10 partly U) / S 2 (Y9, Y17) / U 1 (Y3). U: N 11 / R 5 (Y1, Y3, Y4, Y8, Y10; most of Y5 is also R) / O 0.

**Survives (about 4,300 B):** R2, R5 and R6 plus the roster pointer (about 1,100 B). § Retirement policy in full (about 1,800 B). The classifier table corrected to give `project_local` to skills and chores, plus the declaration paragraph (about 1,400 B). Y9 should be dropped or rewritten to describe the real `sync_parity` message.

---

## 6. agents-md-map-doctrine.md (6,903 B) — RETIRE (operator first: an attested REQ asserts the file exists)

Glob: `AGENTS.md`, `CLAUDE.md` and `.claude/rules/*.md`. All three are generated surfaces. AGENTS.md § Control Surfaces says root `AGENTS.md` "is playback of the committed `root` rendition … generated surfaces are not edited directly". `CLAUDE.md` and `.claude/rules/*.md` are also written by `gz agent sync control-surfaces`. So the rule loads when an agent *reads* a generated file, and never when it edits the canon the rule governs (`.gzkit/corpus/AGENTS.md.jsonl`, `.gzkit/rules/*.md`, skill descriptions). That trigger mismatch alone makes every clause below unreachable at its point of use.

| # | Clause (line) | V | Evidence | U | Why |
|---|---|---|---|---|---|
| D1 | Invariant: AGENTS.md MUST contain only (a) binding bullets ≤ 3 lines, (b) tables, (c) canonical links; MUST NOT contain (i)-(v) (18) | T (witnessed arm) / S-adjacent (the absolute "only") | `gz validate --agents-md-map-conformance` → `✓ All validations passed`. Root AGENTS.md still holds non-bullet, non-table prose, e.g. § STDLIB-FIRST ("Use stdlib by default. A runtime dependency, … needs ADR or OBPI rationale …") and § Governance doctrine surfaces' first paragraph. Its only table is the Gate Covenant; there is no Persona or defect-fix-routing table. The witness checks only the 5-line paragraph rule, so these pass. | R | The witness fails closed with `recovery: /gz-context-diet`. `docs/governance/agents-md-doctrine.md` is the canonical expansion. |
| D2 | CLAUDE.md and `.claude/rules/*.md` inherit the shape with their per-file budget (18) | U | — | R | `gz-context-diet` skill. |
| D3 | Enforced budgets are the values in `data/instructions_files_budget.json`; this rule never restates them (22) | T | The file holds `"AGENTS.md": 25000, "CLAUDE.md": 15000`, `.claude/rules/*.md` 4000 | R | The validator message carries the value and the pointer. |
| D4 | **"The destination for AGENTS.md is the tightened `15000`-char ceiling; reaching it lands under `ADR-0.35.0` § Decision 3"** (22) | **S** | `docs/governance/agents-md-doctrine.md:51`: "a range: 15,000 chars ideal, 20,000 chars ceiling | … Operator rulings 2026-09-19, verbatim: "make target 20k", then "state a range: 15K is ideal, 20K a ceiling"". `instructions-files-budget-history.md:57`: "the doctrine DESTINATION for root AGENTS.md moves 15,000 → 20,000 chars … OBPI-0.35.0-10 … is no longer owed for size". The clause also breaks its own "never restates them" sentence. | — | — |
| D5 | Cite ADR-0.35.0 directly; predecessors ADR-0.0.37 and GHI #533 terminal (22) | T | GHI #533 CLOSED; ADR-0.35.0 `status: Accepted` | R | Doc citation hygiene, carried by agents-md-doctrine.md. |
| D6 | Budgets advisory until 1.0; overrun reported with distance and `/gz-context-diet` pointer (24) | T | Validator output: "exceeds 4000-char budget by 4325. Run /gz-context-diet …" | R | AGENTS.md § Governance doctrine surfaces: "budgets in `data/instructions_files_budget.json` (advisory until 1.0)". The witness message also names it. |
| D7 | Codex delivery cap is set by gzkit through `.codex/config.toml`; changes verified by observed delivery (GHI #962, #815) (24) | T | `vendor-manifest.json` `"codex": 65536`; validator: "[codex-delivery-witness] AGENTS.md: 24906 B of 24906 B delivered by Codex" | R | The witness. |
| D8 | Shape enforcement description (28) | T | `trust_audits/agents_md_map_conformance.py` | R | Describes the witness. |
| D9 | Over-budget trim is `instructions-files-diet`'s job; ordinary sessions add to sources and never resize a render surface (30) | T | — | R | AGENTS.md § Control Surfaces ("Change canon with the content skills"); AGENTS.md § Behavior Rules size-limit line; `gz-context-diet` skill. |
| D10 | Attestation granularity: the discriminator is whether canon changed (34) | T | `gz content commit --help`: "a re-render of UNCHANGED canon needs none and carries the standing attestation forward (GHI #821)" | R | AGENTS.md § Attestation: "Content attestation records canon provenance: additions and removals are attested; capture must not be blocked. Re-rendering unchanged canon needs no attestation; use the corpus fingerprint … Trims or compression invite operator review. A rendition is Layer 3 …" |
| D11 | Table: re-render none; remember attested; retire attested; trim invites review (36-41) | T (mostly) | `gz content remember` has `--witness` ("recorded provenance, never a gate"), not `--attestor`. `retire` requires `--attestor` only when invariant liveness moves. | R | AGENTS.md § Attestation |
| D12 | A GHI needs no attestation (43) | T | — | R | AGENTS.md § Attestation: "a GHI needs no completion attestation" |
| D13 | Do not call a build step "Gate 5"; name it CORPUS ATTESTATION (44) | T | `gz content commit --help`: "Operator-attested (corpus attestation, NOT Gate 5)" | R | AGENTS.md § Attestation: "Gate 5 names completed OBPI/ADR work only". The `gz content` help also says it. |
| D14 | Attestation on add/remove is provenance, never blocking (45) | T | ADR-0.35.0 § Decision 7 | R | AGENTS.md § Attestation: "capture must not be blocked" |
| D15 | Transport never gates attestation (46) | T | — | R | AGENTS.md § Attestation: "no TTY, PTY, or transport condition may prevent recording human attestation" |
| D16 | **"(Advisory — the implementation is inverted and no witness holds it: `gz content remember` and `retire` accept no `--attestor`, while `gz content commit` requires one …)"** (48) | **S** | `gz content retire --help`: "`--attestor ATTESTOR  Operator retiring; required when retirement moves` invariant-tier liveness". `gz content commit --help`: "`--attestor` and `--attestation-text` fail closed when empty IF the corpus moved since this consumer's last committed rendition; a re-render of UNCHANGED canon needs none". `retire` accepts `--attestor`, and `commit` no longer always requires one. Only `remember` still lacks it, and it has `--witness`. | — | — |
| D17 | Writing levers (9 bullets) (52-62) | U (self-declared advisory) | — | N (content) / unreachable (glob) | No other home exists: there are no matches for "Two loads", "No-op hunt" or "Writing levers" in `docs/governance/agents-md-doctrine.md`, `gz-context-diet/SKILL.md` or `agent-contract-rationale.md`. `skill-authoring.md:19` points here ("`agents-md-map-doctrine.md` § Writing levers"). The levers apply when writing corpus entries, rules and skill descriptions, which are canon files this glob never matches. |
| D18 | Related links (66-68) | T | All paths exist | R | — |

Totals: 18 clauses. V: T 14 / S 2 (D4, D16) / U 2 (D2, D17). U: N 1 (D17, content only) / R 15 / O 0, with D4 and D16 not scored.

**Retire path:** move § Writing levers (about 1,700 B) into `docs/governance/agents-md-doctrine.md`, `skill-authoring.md`, or a new rule scoped to the canon (`.gzkit/corpus/**`, `.gzkit/rules/**`), then re-point `skill-authoring.md:19`. Everything else already lives in AGENTS.md § Attestation, `docs/governance/agents-md-doctrine.md`, the `gz-context-diet` skill, and the `--agents-md-map-conformance` / `--instructions-files-budget` failure messages. **Blocker:** `tests/governance/test_agents_md_map_doctrine.py:103-104` `@covers("REQ-0.0.54-01-01") test_rule_file_exists_with_v010_and_required_shape` asserts that the rule file exists. Under skill-surface-sync § Retirement policy, that REQ goes to the operator first. `test_agents_md_map_conformance.py:104` and `agents_md_map_conformance.py:263` also cite the rule's § Invariant.

---

## Scorecard rows in `docs/governance/advisory-rules-audit.md`

Rows that score a STALE clause:

- **Row 52b** (model-selection: "Subagent effort is set on the agent definition, never on the dispatch call") scores S4/S10, whose dispatch half is now false.
- **Row 62** and the general MX rows do not score M38 directly. **Row 63** ("PRIME DIRECTIVE binds the entire hangar session") is the closest; M38 is in its § Do Not and is not scored separately.
- **Row 58** (map-doctrine invariant) scores D1. **Row 58a** scores D10-D15 and D11; it does not score D16's advisory parenthetical. D4 is unscored.
- **Row 31 / 33a** (skill-surface-sync) does not score Y9 or Y17. However, **row 33a** cites `audit_generated_surface_drift` as reporting "a mirror that diverges from canon". That audit returns early whenever `.gzkit/rules/` exists (`instruction_audit.py:207-208`), so the row names a witness that does not run here. Its effective witness is `validate_pkg/sync_parity.py`.

Other scorecard drift found:

- **Row 52** cites `src/gzkit/core/models.py:127`; the field is at `:451`. It also says "All 70 canonical skills declare a tier (33 haiku, 24 sonnet, 13 opus …)"; today it is 74 skills, with 32 haiku, 27 sonnet and 15 opus.
- **Row 55** cites `src/gzkit/commands/chores.py:25` for `ALLOWED_LANES`; line 26 now holds `SHELL_OPERATORS_RE`. Not re-verified beyond that.

## Coupled defects found (outside the six rules)

1. `.gzkit/chores/README.md:57` says "The registry at `src/gzkit/chores/registry.json` (canonical)". That contradicts chores.md C3 and skill-surface-sync R1.
2. `src/gzkit/hooks/guards.py:582-584` says the `post-authoring-src-commits` pin is "to PRESERVE today's behaviour rather than to rule on it". The operator has since ruled it permanent (mx-mode M16; GHI #855).
3. `docs/governance/opus-tuning.md` § Model Selection says "Every skill declares `model: haiku|sonnet|opus`", omitting `fable`, which the `SkillFrontmatter` Literal allows.
4. `.pre-commit-config.yaml:15` comment says the alarm switch skips "while .gzkit/mx.json carries `mode: safe`". The code tests `level == "drydock"` (`mx/alarms.py`). The two agree through the alias, but the comment uses the retired field name.
