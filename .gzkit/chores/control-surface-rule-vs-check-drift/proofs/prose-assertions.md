# Prose Assertions — Pass C

> Chore: `control-surface-rule-vs-check-drift` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 extraction.
> The prose side of the parity diff: what each promoted rule **claims** its check
> does. Paired against [`check-behaviors.md`](check-behaviors.md), which records
> what the code actually asserts. The diff between the two files is
> [`parity-diff.md`](parity-diff.md).

**Extraction rule:** an assertion is admitted only where the rule names a
mechanism — a flag, an exit code, a scope, or an enforcement claim. Prose that
states a discipline *without* claiming a mechanism is not an assertion here; it is
correctly-scoped advisory text and cannot drift from a check it never names.

That distinction is this run's central finding, so it is stated before the table
rather than after: **every `parity` verdict in the ledger belongs to a rule that
discloses its own posture, and every `prose-wider` verdict belongs to a rule that
asserts a mechanism.** Disclosure is stable; assertion rots.

---

## Assertions carrying a drift verdict

| Rule (file:line) | Asserted mechanism | Verdict |
|---|---|---|
| `governance-core.md:53` | *"Enforced by `gz validate --cli-alignment`. **Exit 3** on any unresolvable reference."* | M2 `prose-wider` — exits 1 |
| `governance-core.md:44` | scope is `docs/**/*.md`, `docs/**/*.feature`, `features/**/*.feature`, `.gzkit/skills/**/SKILL.md`, runbooks | M3 `prose-wider` — `docs/**/*.feature` never globbed; `docs/releases/` silently excluded |
| `cli.md:15` + `:38` | *"**Mechanical check:** `uv run gz cli audit`"* under a map where 3 = Policy Breach | M15 `divergent` — `cli_audit.py:243` is the only non-zero exit, and it is 1 |
| `changelog-release-notes.md` | `--changelog` *"fails closed"* | M5 `prose-wider` — not in the breach set, exits 1 |
| manpage `validate.md` (`--brief-headings`) | *"Exits 3"* | M4 `prose-wider` — exits 1 |
| `AGENTS.md:354` | authoring-guide protocol envelope *"schema-validated at runtime"* | P3 `prose-wider` — **zero** `authoring_guide_protocol` hits in any `.py` |
| `complexity-thresholds.md:97` | *"**Silent edits are forbidden** by the validator"* | P4 `prose-wider` — only existence, parse, and metric coverage are asserted |
| `AGENTS.md:356` | complexity calibration *"grounded in an empirically-measured exemplar corpus (seven selection criteria)"* | M9 `prose-wider` — four citation facts only |
| `AGENTS.md:358` | `.gzkit/rules/*.md` with `paths: "**"` *"may not live under any vendor-surface rules directory"* | M10 `prose-wider` — validator globs `.gzkit/rules` only |
| `AGENTS.md:212` | `--taxonomy` enforces *"`pool` ⇒ no `kind`/`semver` frontmatter"* | M11 `prose-wider` — `semver` read then short-circuited; a pool ADR carrying it passes |
| `task-discovery.md:130` | names eight worklog event types as the set signature (a) checks | M12 `divergent` — a **different** eight; overlap is two |
| `task-discovery.md:140` | *"fail Heavy lane closeouts on layer-drift; Lite lane warns"* | M13 `divergent` — zero `lane` reads in the module; exit 3 both lanes |
| `skill-surface-sync.md:28` | body-level marker **and** visible block quote, version *"the primary signal"* | M14 `divergent` — live path stamps `type="surface"` → exit 1; the exit-3 path has no caller in `src/` |
| `tests.md:18` | smoke gate *"exit 3 on breach **or on an empty tier**"* | M16 `prose-wider` — `_EXIT_OK` on empty unless `smoke.required`, default `False` |
| `AGENTS.md:266` | canonical-invocation table *"Locked by `CANONICAL_STEP_COMMANDS`"* | M17 `prose-wider` — no `"ruff"` key; the lock covers 4 of its own 5 rows |
| `AGENTS.md:353` | `Field(min_length=1)` on `AdvisorDiagnosis.proof` enforced by `--advisor-proof-binding` | M8 `prose-wider` — the check reads `properties.proof.minItems` from the JSON schema, not the Pydantic field |
| `AGENTS.md:360` | `--invariant-coherence` *"**re-renders the registry** and byte-compares"* | =4 `divergent` (**refuted prior parity**) — `render_agents_md` returns committed rendition bytes verbatim; no registry is read |
| `pythonic.md:50-51` | accuses the scorecard of miscoding size limits as Mechanical | D3 `divergent` — the scorecard now scores them **Judgment**; the accusation is stale |
| `task-discovery.md:107` | *"Witness status unruled — GHI #752"* | D6 — pointer dead for the second time; #752 is CLOSED |

## Assertions in parity

| Rule (file:line) | Asserted mechanism | Why it holds |
|---|---|---|
| `governance-core.md:18` | attestation universal; `_requires_human_obpi_attestation` returns `True` unconditionally | `adr_audit.py:462-475` body is `return True`; fenced by `mx/invariants.py:110-125` |
| `chores.md:47` + `:93` | `--chores-layout` enforces, exit 3 | `"chores_layout"` in the breach set (`validate_cmd.py:1122`) |
| `token-block-discipline.md:43` + `:53` | frontmatter keys vs `## Decisions Made` body section, exit 3 | `lock_exchange_coupling.py:37-38`; `"lock_exchange_coupling"` in the breach set |
| `tests.md:89` | `Ceremony:`/`Eval-feedback-source:` no longer substitute for `Task:` | `validate_commit_trailers.py:75` gates solely on `has_task_trailer` |
| `skill-surface-sync.md:131-133` | three content classes exempt from `ON_DISK_NOT_INCLUDED` | `distribution.py:66-84`; rule table and code gained `project_local` in the **same** change |
| `AGENTS.md:94` | `forbid-pytest` pre-commit hook | `.pre-commit-config.yaml:43-48` → `guards.py:26-32` |
| `changelog-release-notes.md:49` | hermetic structure here, networked coverage in `gz-patch-release` | `validate_pkg/changelog.py:9-12` carries the same split and cites back |
| `cross-platform.md:35` | `--utf8-prefix`, with a fresh-interpreter carve-out | `cross_platform.py:80-89, :138-141` maps one-to-one onto the prose |

## Disclosures — no mechanism asserted, so nothing can drift

These are the rules that say what they *cannot* enforce. All score `parity`, and
none has ever produced a drift row.

- `gh-cli.md:22` — *"the sanctioned and forbidden invocations are byte-identical commands. Nothing mechanical can tell them apart — the discipline is yours to keep."*
- `agent-failure-modes.md:16` — *"**Loading posture:** advisory vocabulary, not a mechanical gate."*
- `security-sensitivity.md:23` — *"a **discipline obligation, not a mechanical one**."*
- `changelog-release-notes.md:50` — *"no mechanical release-notes validator — the curated narrative is not machine-checkable."*
- `pythonic.md:44-45` — the size-limit table listing the enforcer as *"nothing / authoring-time guidance only"*.
- `tool-skill-runbook-alignment.md` § Enforcement posture — Invariants 2 and 3 *"advisory, and that is the settled disposition rather than a queue"*.

**The generalizable rule this run confirms:** a rule that *describes* a gate goes
stale silently, because nothing re-reads it when the gate moves. A rule that
*points at* a gate by flag name breaks loudly. A rule that *discloses* it has no
gate cannot break at all. Nineteen drift rows sit in the first category; zero sit
in the third.
