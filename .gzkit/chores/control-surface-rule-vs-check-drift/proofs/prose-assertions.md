# Prose Assertions (Rule-Stated Invariants)

**Generated:** 2026-05-10
**Sources:** `.gzkit/rules/*.md`, `AGENTS.md`, `CLAUDE.md`

One line per assertion. Captured statements that read as binding rules
("must", "MUST", "Do not", "shall", "fail-closed", "required"). Soft
advisory language ("prefer", "consider", "see also") is excluded.
Path renderings use POSIX form throughout.

## `.gzkit/rules/pythonic.md`

- `.gzkit/rules/pythonic.md:8` Clarity over cleverness — explicit, readable, consistent code (principle).
- `.gzkit/rules/pythonic.md:18` No bare `except:` / `except Exception:` outside CLI boundaries.
- `.gzkit/rules/pythonic.md:24` Functions <=50 lines, modules <=600 lines, classes <=300 lines.
- `.gzkit/rules/pythonic.md:28` Top-level imports only; no lazy imports unless required for optional dependencies or cycle avoidance.
- `.gzkit/rules/pythonic.md:33` Catch specific exceptions, translate to `core.errors`; no bare `except:` / `except Exception:` outside CLI.
- `.gzkit/rules/pythonic.md:47-58` `# type: ignore[<code>]` (bracketed) under `src/` is forbidden; use bare `# type: ignore` or `# ty: ignore[<ty-code>]`.

## `.gzkit/rules/models.md`

- `.gzkit/rules/models.md:7` Use Pydantic `BaseModel` for all data models; no stdlib `dataclasses`.
- `.gzkit/rules/models.md:8` Use `ConfigDict(frozen=True, extra="forbid")` for immutable models.
- `.gzkit/rules/models.md:9` Use `Field(...)` with descriptions for required fields; `Field(None, ...)` for optional.
- `.gzkit/rules/models.md:10` Use type hints (`str | None`, `list[str]`); not `Optional`, `List`.
- `.gzkit/rules/models.md:37-39` Anti-patterns: stdlib `dataclass` for governance, Pydantic without `ConfigDict`, `Optional`/`List` instead of `| None` / `list[]`.

## `.gzkit/rules/cli.md`

- `.gzkit/rules/cli.md:11` Optimize for humans; add `--json`/`--plain` for machines.
- `.gzkit/rules/cli.md:12` Before landing a new flag or subcommand, run `uv run gz cli audit`; must exit 0 with new verb covered across manpage + command doc + index.
- `.gzkit/rules/cli.md:27-34` Exit-code map: 0 success / 1 user-config / 2 system-IO / 3 policy breach.
- `.gzkit/rules/cli.md:42-48` Flag conventions: `--quiet`, `--verbose`, `--dry-run`, `--json`, `--help`/`-h`.
- `.gzkit/rules/cli.md:55-58` Default output human-readable; `--json` valid JSON to stdout, logs to stderr; `--plain` one record per line.
- `.gzkit/rules/cli.md:65-71` Every command must respond to `-h`/`--help`, include description, usage, options, example, lines <=80 chars.

## `.gzkit/rules/cross-platform.md`

- `.gzkit/rules/cross-platform.md:21` Paths via `Path("dir") / "file"`; never `"dir/file"` or `"dir\\file"`.
- `.gzkit/rules/cross-platform.md:22` Relative paths via `.relative_to(root).as_posix()`; never `str(.relative_to(root))`.
- `.gzkit/rules/cross-platform.md:23` File I/O specifies `encoding="utf-8"`.
- `.gzkit/rules/cross-platform.md:24` Temp files use context managers; not raw `shutil.rmtree()`.
- `.gzkit/rules/cross-platform.md:25` Subprocess in list form via `uv run`; no `shell=True`, no bare `python`.
- `.gzkit/rules/cross-platform.md:30` Always use `.as_posix()` when result is compared against forward-slash literals, embedded in JSON/YAML/ledger, or stored on identifier fields.
- `.gzkit/rules/cross-platform.md:34` The CLI entrypoint handles UTF-8 at startup; do NOT prefix `uv run gz` with `PYTHONUTF8=1`.
- `.gzkit/rules/cross-platform.md:34` Fresh `python -c` and helper scripts need explicit `sys.stdout.reconfigure(encoding='utf-8')`.

## `.gzkit/rules/tests.md`

- `.gzkit/rules/tests.md:16` Use stdlib `unittest`; no pytest.
- `.gzkit/rules/tests.md:17` Prefer table-driven tests with deterministic seeds; no network/external services.
- `.gzkit/rules/tests.md:18` Smoke/BVT <=60s; cover current-scope surfaces only.
- `.gzkit/rules/tests.md:20` Database isolation: unit tests MUST use `tempfile` temp DBs; NEVER use live/production databases.
- `.gzkit/rules/tests.md:21` NEVER use raw `shutil.rmtree()` in tearDown; use `tempfile.TemporaryDirectory()` context manager.
- `.gzkit/rules/tests.md:25` Minimum line coverage: 40.00%.
- `.gzkit/rules/tests.md:26` Before closing any brief, verify coverage has not regressed.
- `.gzkit/rules/tests.md:38-46` Red-Green-Refactor TDD discipline — Red, Green, Refactor cycle per behavior increment.
- `.gzkit/rules/tests.md:46` Test cases derive from OBPI brief acceptance criteria, not from the implementation.
- `.gzkit/rules/tests.md:48` Tests assert semantics, not strings (invariant 6f).
- `.gzkit/rules/tests.md:50` Audit-helper names MUST NOT pattern-match as audit-step names — name them by behavior.
- `.gzkit/rules/tests.md:56` Do not author ARB receipts with `exit_status=1` as "RED receipts".
- `.gzkit/rules/tests.md:60` Every src/tests commit carries a governance-intent trailer: `Task:`, `Ceremony:`, or `Eval-feedback-source:`.
- `.gzkit/rules/tests.md:74-77` Mock every subprocess boundary; complete in <200ms; deterministic; `tempfile` temp DBs only.
- `.gzkit/rules/tests.md:81` Behave scenarios covering a REQ carry `@REQ-X.Y.Z-NN-MM` as a scenario tag.

## `.gzkit/rules/governance-core.md`

- `.gzkit/rules/governance-core.md:11` Read `AGENTS.md` before implementation work.
- `.gzkit/rules/governance-core.md:12` Use `uv run` for Python command execution.
- `.gzkit/rules/governance-core.md:13` Do not bypass Gate 5 when lane requirements require human attestation.
- `.gzkit/rules/governance-core.md:14` Do not edit `.gzkit/ledger.jsonl` manually.
- `.gzkit/rules/governance-core.md:15` Every defect must be fixed now or tracked (GHI or insights jsonl).
- `.gzkit/rules/governance-core.md:23-28` Required OBPI workflow order: state → status → implement → gz implement → gates → audit-check.
- `.gzkit/rules/governance-core.md:42-44` Every `gz <verb>` reference in operator docs must resolve to a registered parser verb.
- `.gzkit/rules/governance-core.md:46` Multi-word subcommands count (`gz adr status`, `gz obpi complete`), not just top-level verbs.
- `.gzkit/rules/governance-core.md:48` `gz validate --cli-alignment` exits 3 on any unresolvable reference.
- `.gzkit/rules/governance-core.md:55-58` `docs/governance/GovZero/adr-status.md` is Layer 3 derived — never source-of-truth, never hand-maintained; regenerator is `uv run gz register-adrs`.
- `.gzkit/rules/governance-core.md:64` `uv run gz validate --adr-status-fresh` fail-closes drift between committed index and on-disk canon.

## `.gzkit/rules/adr-audit.md`

- `.gzkit/rules/adr-audit.md:13` Verify linked OBPI evidence via `gz adr audit-check ADR-<X.Y.Z>`.
- `.gzkit/rules/adr-audit.md:21-26` Run quality checks: `gz lint`, `gz test`, `gz typecheck`, `mkdocs build --strict`.
- `.gzkit/rules/adr-audit.md:31-34` Run closeout / attest / audit in order.
- `.gzkit/rules/adr-audit.md:45` Do not run `gz audit` before attestation.
- `.gzkit/rules/adr-audit.md:46` Never backfill a cosmetic `@covers` decorator to silence audit-check without re-deriving the assertion.
- `.gzkit/rules/adr-audit.md:47` Keep `docs/user/runbook.md` and `docs/governance/governance_runbook.md` aligned with runtime behavior.

## `.gzkit/rules/brief-heading-conventions.md`

- `.gzkit/rules/brief-heading-conventions.md:10` OBPI brief evidence sections MUST use H3 (`###`), not H2 (`##`).
- `.gzkit/rules/brief-heading-conventions.md:14-17` Canonical evidence sections: `### Implementation Summary`, `### Key Proof`, `### Closing Argument`.
- `.gzkit/rules/brief-heading-conventions.md:38-40` `uv run gz validate --brief-headings` exits 3 on drift.

## `.gzkit/rules/skill-surface-sync.md`

- `.gzkit/rules/skill-surface-sync.md:11` Edit `.gzkit/` first — canonical source is `.gzkit/skills/` and `.gzkit/rules/`.
- `.gzkit/rules/skill-surface-sync.md:12-15` Bump version on every edit: skills carry `skill-version:` in frontmatter; rules carry body-level `<!-- rule-version: X.Y.Z -->` + visible block quote.
- `.gzkit/rules/skill-surface-sync.md:16` Run `uv run gz agent sync control-surfaces` after every edit.
- `.gzkit/rules/skill-surface-sync.md:17` Never edit vendor mirrors directly (`.claude/`, `.github/`).
- `.gzkit/rules/skill-surface-sync.md:13` Rule frontmatter schema is `extra="forbid"` and rejects `skill-version:` on rule files.

## `.gzkit/rules/chores.md`

- `.gzkit/rules/chores.md:46` Lite by default: `uv run -m unittest -q` only; no behave, no network, no external services.
- `.gzkit/rules/chores.md:47` Small diffs — touch only files in scope.
- `.gzkit/rules/chores.md:48` CLI evidence only; never use raw SQL for attestation.
- `.gzkit/rules/chores.md:49` Stray `CHORE.md` / `acceptance.json` outside the two canonical roots is a defect — `gz validate --chores-layout` enforces it.
- `.gzkit/rules/chores.md:118-126` Each chore slug directory MUST contain `CHORE.md`, `acceptance.json`, `README.md`, and (project-local) `proofs/`.

## `.gzkit/rules/tool-skill-runbook-alignment.md`

- `.gzkit/rules/tool-skill-runbook-alignment.md:19` Invariant 1 — every CLI verb registered in `src/gzkit/cli/` must be invoked by at least one skill under `.gzkit/skills/`.
- `.gzkit/rules/tool-skill-runbook-alignment.md:23` Invariant 2 — every skill's `gz_command:` must resolve to the CLI verb the runbook prescribes for the same operator moment.
- `.gzkit/rules/tool-skill-runbook-alignment.md:27` Invariant 3 — destination verb's default output form must honor the routing skill's Output Contract.

## `.gzkit/rules/gh-cli.md`

- `.gzkit/rules/gh-cli.md:16` Use `gh` for defect tracking, ADR closeout, release ceremony, or active brief / explicit user request.
- `.gzkit/rules/gh-cli.md:28-33` Prohibited without explicit approval: settings mutations, secret management, force pushes, merging PRs without authorization.
- `.gzkit/rules/gh-cli.md:35` Defects against gzkit-owned surfaces filed from consuming repos MUST go to `tvproductions/gzkit` via `gz issue file`.
- `.gzkit/rules/gh-cli.md:37` Operator PII: the wrapper stamps only repo slug + gz version, never operator email.

## `.gzkit/rules/security-sensitivity.md`

- `.gzkit/rules/security-sensitivity.md:17` Security work needs heightened review regardless of lane or kind.
- `.gzkit/rules/security-sensitivity.md:17` A brief carrying `sensitivity: security` is never self-closeable.
- `.gzkit/rules/security-sensitivity.md:25` Briefs whose allowed-paths overlap a registered security surface MUST declare `sensitivity: security`.
- `.gzkit/rules/security-sensitivity.md:26` A brief MAY declare sensitivity without overlap (escalation); MAY NOT omit sensitivity while overlapping (escape is fail-closed).
- `.gzkit/rules/security-sensitivity.md:30` `gz obpi complete` on a `sensitivity: security` brief fires an extended Gate 5 walkthrough.
- `.gzkit/rules/security-sensitivity.md:31` Scanner-unavailable is fail-closed (no degradation).
- `.gzkit/rules/security-sensitivity.md:34-38` Anti-patterns: declaring `sensitivity: absent` while touching registered surface; editing `data/security_surfaces.json` without declaring `sensitivity: security`; narrative substitution for security-scan receipt; bundling security work into non-security parent OBPI.

## `.gzkit/rules/agent-failure-modes.md`

- `.gzkit/rules/agent-failure-modes.md:7-14` Six-pattern failure-mode vocabulary: Safeguard circumvention / Reckless action / Fabrication / Skipped cheap verification / Correction fails / Dishonest when caught.
- `.gzkit/rules/agent-failure-modes.md:16` Advisory vocabulary, not a mechanical gate.

## `.gzkit/rules/complexity-doctrine.md`

- `.gzkit/rules/complexity-doctrine.md:31-42` Selection criteria (all must hold): longevity >=5y, maintenance health, practitioner reputation, pure-Python >=80%, author craftsmanship, project doctrine fitness, pinned commit SHA.
- `.gzkit/rules/complexity-doctrine.md:44-53` Corpus anti-patterns: post-hoc fitting, GitHub-star count, only modern/only legacy, monoculture, agent-supplied list, doctrine-incompatible inclusion.
- `.gzkit/rules/complexity-doctrine.md:54-60` Distillation cadence: annual calendar OR drift >25% OR judgment trigger; 6-month minimum guard.
- `.gzkit/rules/complexity-doctrine.md:78-81` Downstream foundation ADRs MUST cite the distilled-characteristics document, NOT raw distributions, NOT the corpus directly.
- `.gzkit/rules/complexity-doctrine.md:84-92` Citation is a three-field tuple; codified by Pydantic `Citation`.
- `.gzkit/rules/complexity-doctrine.md:110-112` Percentile + absolute pairing: cited boundary MUST appear as both forms together.
- `.gzkit/rules/complexity-doctrine.md:116-121` Citation valid at corpus_revision N and N+1; out of date at N+2.

## `.gzkit/rules/complexity-thresholds.md`

- `.gzkit/rules/complexity-thresholds.md:35-43` One canonical threshold table; every entry is `(metric, percentile-band, absolute-number, trigger-semantic)`; trigger vocabulary fixed at `block`/`warn`/`advise`.
- `.gzkit/rules/complexity-thresholds.md:45-47` Every metric MUST carry a `block` band.
- `.gzkit/rules/complexity-thresholds.md:51-63` Trigger-semantic vocabulary is exactly three values; fourth value forbidden.
- `.gzkit/rules/complexity-thresholds.md:80-82` Loader fails closed when a canonical metric is missing a block-band row.
- `.gzkit/rules/complexity-thresholds.md:96-97` Amendments to `(metric, band, trigger)` mappings flow through ADR ceremony; silent edits forbidden by validator.

## `.gzkit/rules/gate5-runbook-code-covenant.md`

- `.gzkit/rules/gate5-runbook-code-covenant.md:7` Documentation is a first-class deliverable; tracks behavior changes in same patch set.
- `.gzkit/rules/gate5-runbook-code-covenant.md:17-19` Update command docs, runbook flows, attestation language when behavior changes.
- `.gzkit/rules/gate5-runbook-code-covenant.md:30` Do not leave placeholder output examples.
- `.gzkit/rules/gate5-runbook-code-covenant.md:31` Do not update code without docs when command output changes.
- `.gzkit/rules/gate5-runbook-code-covenant.md:32` Do not declare completion without explicit human attestation for heavy/foundation scope.

## `.gzkit/rules/token-block-discipline.md`

- `.gzkit/rules/token-block-discipline.md:25` `obpi_lock_release_cmd` and `lock_manager.release_lock()` MUST accept `--abandon <category>:<reason>` flag.
- `.gzkit/rules/token-block-discipline.md:40-50` Register entry MUST contain last lock-event timestamp, last commit SHA, named decision context, branch state.
- `.gzkit/rules/token-block-discipline.md:50` Entries lacking any of the four fields MUST fail `gz validate --lock-handoff-coupling`.
- `.gzkit/rules/token-block-discipline.md:96-107` Release fail-closed precondition: valid handoff OR `--abandon` flag; staged warning -> fail-closed.

## `.gzkit/rules/model-selection.md`

- `.gzkit/rules/model-selection.md:17` Model tier is determined by decision complexity, not task size.
- `.gzkit/rules/model-selection.md:18` Default to the lowest tier that closes the decision space.
- `.gzkit/rules/model-selection.md:19` Skill SKILL.md files carry explicit `model:` frontmatter; no inference.
- `.gzkit/rules/model-selection.md:20` Subagent prompts specify effort level, not model name.
- `.gzkit/rules/model-selection.md:50` Valid values: `haiku`, `sonnet`, `opus`; no inference, no runtime detection.

## `AGENTS.md`

- `AGENTS.md` Prime Directive 1-6 — own work completely, complete all work fully, never say "out of scope", scope expansion is not creep, flag defects never excuse them, every defect must be trackable.
- `AGENTS.md` DO IT RIGHT 1-9 — fix class of failure not instance, no vibe coding, prefer thorough fix, verify observed behavior, read code before changing, tests assert semantics not strings, choose fix scope per thresholds, verify runtime surface before recommending, quote rule and conflicting directive verbatim.
- `AGENTS.md` Anti-vibing operative claims 1-4 — 5:1 governance ratio is the product; smallest-vibing-surface framing; doctrine drift = invariant drift; stochastic LLM vibing is the named failure class.
- `AGENTS.md` Stdlib-first claims 1-5 — default is stdlib; departures are foundation-attested; "popularity"/"hot topic" not rationale; existing deps inherit rule.
- `AGENTS.md` Operator economy claims 1-6 — agent drafts/operator reviews; multiple-choice when possible; verbatim phrasing preserved; forcing functions agent-driven; decisions accumulate; never ask operator to type more than necessary.
- `AGENTS.md` Always 1-12 — read AGENTS.md, follow gate covenant, record ledger events, preserve human intent, offload to subagents when appropriate, include 'Why' in subagent prompts, <90% sure ask human, surface assumptions, stop on inconsistencies, push back on flawed plans, append improvement insight on course-correct, include Eval-feedback-source trailer on eval-feedback rule edits.
- `AGENTS.md` Never 1-7 — bypass Gate 5, modify ledger directly, create artifacts without linkage, violate invariants, summarize after Stage 2/3 and stop, work around hook blocks, read frontmatter status:Completed as proof.
- `AGENTS.md` § Attestation — pattern `<user words> — <concrete characterization>`; canonical receipt-prefix table is binding; heavy-lane missing receipt = fail-closed.
- `AGENTS.md` § Defect-fix routing — direct fix when ALL criteria hold (<=10 lines, <=2 files, single surface, >=3 precedent commits in 60d, unit-test coverage); OBPI required when any cross-boundary/CLI/schema/runtime trigger holds.
- `AGENTS.md` § Architectural boundaries 1-6 — do not promote post-1.0 pool ADRs, do not add more pool ADRs to runtime, do not build graph engine without state-doctrine lock, do not let reconciliation be maintenance chore, do not let AirlineOps parity be perpetual catch-up, do not let derived views silently become source-of-truth.
- `AGENTS.md` Local rule "Order versioned identifiers semantically" — semver, not lexicographic.
- `AGENTS.md` Local rule "Add imports in same Edit as usage".
- `AGENTS.md` Local rule "Never prefix `uv run gz` with `PYTHONUTF8=1`".
- `AGENTS.md` Local rule "Every version bump is a release — create GitHub release after bump".
- `AGENTS.md` Local rule "Use github/gitignore template for scaffolding".
- `AGENTS.md` Local rule "Operator PII — never include operator's personal email in any repo-bound artifact".

## `CLAUDE.md`

- `CLAUDE.md` Invariant 10a (Claude-only) — skill-tool-invoke-same-turn: invoke named tool in same turn the skill step names it.
- `CLAUDE.md` Compact instructions — preserve active pipeline ID, OBPI ID, gate state, attestation, GHIs, TASK ID on `/compact`.
