# Parity Diff — control-surface-rule-vs-check-drift (Pass C)

Side-by-side of prose assertions (from `prose-assertions.md`) vs check
assertions (from `check-behaviors.md`) for each promoted scope flag. The
verdict enum:

- **parity** — check enforces substantially the same set as the prose.
- **prose-wider** — rule prose says more than the check enforces; check
  behavior is a strict subset of prose.
- **check-wider** — check enforces more than the rule prose states
  (operator surprise risk — the check could flag something the operator
  has no rule to cite against).
- **divergent** — prose and check assert meaningfully different things.

| # | Rule + § | Prose assertions | Check assertions | Prose-only gaps | Check-only gaps | Verdict |
|---|---|---|---|---|---|---|
| 1 | `CLAUDE.md` § AB rules 1–2 — pool ADR runtime isolation (`--pool-adr-isolation`) | 4 | 6 | Prose #1 mentions "post-1.0" specifically; check fires on any pool ADR regardless of the 1.0 boundary. Prose #4 covers both `ADR-pool.` id-prefix AND `docs/design/adr/pool/` path — check only covers id-prefix (check #6). | Check #5 dedup semantics; check #6 path-ignore; check #7 Gate 1 generic-event behavior — all implementation details the prose does not state. | **prose-wider** |
| 2 | `CLAUDE.md` § AB rule 4 — reconciliation freshness (`--reconcile-freshness`) | 3 | 7 | Prose #2 asserts reconciliation must be "tested, gated, and part of the pipeline" — the check only verifies freshness of a single ledger event, not gating/testing coverage. | Check #6 fail-open when no reconcile events exist — the check silently passes on an entirely empty reconcile history, which the prose would arguably reject. Check #7 fail-open on git error. | **divergent** |
| 3 | `CLAUDE.md` § AB rule 6 — frontmatter coherence (`--frontmatter`) | 3 | 7 | (none) | Check #3 status supersetting (`attested_completed` for `completed`) is mechanical detail the prose does not explicitly bless — but it's derived from the status vocab contract, not drift. Check #7 recovery hints per field. | **parity** |
| 4 | `CLAUDE.md` § AB rule 6 — event handler coverage (`--event-handlers`) | 2 | 5 | (none) | Check #4 stale-waiver errors extends beyond the bare prose rule (prose says "must be claimed or waived"; check also enforces waivers be live). This is prose-aligned defense-in-depth, not drift. | **parity** |
| 5 | `CLAUDE.md` § AB rule 6 — validator field coverage (`--validator-fields`) | 1 | 5 | Prose asserts symmetric "write-path audit" (trust-doctrine T2); the check does NOT flag stale `_VALIDATOR_FIELD_WAIVERS` entries even though the sibling audit #4 does. Asymmetric enforcement vs. event-handlers pair (check #5 explicitly calls this out). | (none) | **prose-wider** |
| 6 | `CLAUDE.md` § AB rule 6a — ADR taxonomy (`--taxonomy`) | 6 | 6 | Prose #6 about pool ADRs omitting `semver:` is partially unchecked — the validator only asserts `kind:` is absent on pool ADRs, not that `semver:` is also absent (check #4). | Check #6 non-pool id-prefix ↔ semver coherence is NOT enforced — an ADR with filename `ADR-0.3.0-*.md` but `semver: 0.0.7` in frontmatter (or `id: ADR-0.0.7`) would pass the check when `kind: foundation`. | **prose-wider** |
| 7 | `CLAUDE.md` LR 9 + `cross-platform.md` — UTF-8 prefix (`--utf8-prefix`) | 4 | 7 | Prose #2 + #3 + #4 about fresh-interpreter helpers (`python -c`, `uv run python <script>`, `tools/**`) needing explicit `sys.stdout.reconfigure(encoding='utf-8')` is **entirely unenforced** (check #5, #6, #7). The runtime-guard scope boundary is prose-binding but check-invisible. Doc scope misses `.sh`, Makefiles, CI workflows. | Check #4 excludes `advisory-rules-audit.md` by filename exception. | **prose-wider** |
| 8 | `CLAUDE.md` LR 11 — version bump → release (`--version-release`) | 5 | 8 | Prose #2 names `pyproject.toml`, `__init__.py`, AND README badge — check only validates `pyproject.toml` (check #5, #6). Prose #3 about PyPI + binary builds is end-state, unenforceable. | Check #3 GHI-217 exemption (`docs/releases/PATCH-v{version}.md` treated as equivalent evidence) is an implementation escape hatch prose does not declare. Check #7 accepts tag existence without validating `--latest` / `--notes` / `--target main`. | **prose-wider** |
| 9 | `governance-core.md` via Invariant 2 rule text — CLI alignment (`--cli-alignment`) | 3 | 6 | (The rule text for this check is implicitly in the validator docstring since governance-core.md does not state the operator-doc-verb-alignment rule directly. Prose-wider in the sense that the rule surface does not match the check surface at the rule-file level.) | Check #6 excludes `.gzkit/skills/**/SKILL.md` from scanning — the skills surface can carry unresolvable `gz <verb>` strings and pass this audit. | **divergent** |
| 10 | `pythonic.md` § Size Limits — classes ≤300 (`--class-size`) | 4 | 8 | Prose #4 names functions ≤50 and modules ≤600 — check #6, #7 explicitly do not cover them (handled by ruff/xenon/pre-commit separately per scorecard rules 19/20). | Check #4 waiver format `path::ClassName` with POSIX forward-slash is an implementation spec not in prose. | **parity** (split enforcement is scorecard-acknowledged). |
| 11 | `pythonic.md` § Type-check suppression (`--type-ignores`) | 6 | 8 | Prose #2 + #4 + #7 about the positive form `# ty: ignore[<ty-code>]` with ty-code specificity is **entirely unenforced** (check #6, #7). A suppression that writes `# ty: ignore[totally-bogus-code]` passes the check but violates the prose. | Check #2 tokenize-only scope (COMMENT tokens) is a robustness feature not stated in prose. | **prose-wider** |
| 12 | `models.md` — Pydantic discipline (`--pydantic-models`) | 7 | 7 | Prose #2 + #7 about `frozen=True` AND prose #3 about `extra="forbid"` are **unenforced at the content level** (check #6): `model_config = {}` counts. Prose #6 about `Optional`/`List` is delegated elsewhere. | Check #3 accepts both `Assign` and `AnnAssign` forms for `model_config`. | **prose-wider** |
| 13 | `tool-skill-runbook-alignment.md` § Invariant 1 (`--skill-alignment`) | 3 | 8 | Invariant 1 only covers verb-referenced-by-at-least-one-skill. Invariants 2 and 3 are explicitly out-of-scope (rule-level and scorecard acknowledge this). **Prose scope matches check scope at rule-file level.** | Check #8 does NOT check multi-word subcommand coverage (`gz adr status`) — a skill mentioning only `gz adr` counts, and the `adr status` subpath is invisible. This is a subtle prose-wider: the rule talks about "every CLI verb" and the check treats only top-level subparser choices as "verbs." | **prose-wider** |
| 14 | `tests.md` § TASK-Driven Workflow — commit trailers (`--commit-trailers`) | 5 | 8 | Prose #3 about trailer positional discipline (Task: as final line) is **unenforced** (check #6). Prose implicitly covers historical commits via "every commit touching" — check scopes to HEAD only (check #7). | Check #7 HEAD-only scope is explicitly documented as "advisory and focused on preventing *new* trailer omissions," which the prose does not bless as a carve-out. | **prose-wider** |
| 15 | `tests.md` § Runner anti-patterns — test tiers (`--test-tiers`) | 4 | 5 | (none) | Check #3 naive `flag in text` substring can catch a flag name appearing inside a comment/docstring and flag it — minor false-positive risk the prose does not anticipate. Check #4 scope is parser source files; prose says "re-appearing in `parser_*.py`" matching the check. | **parity** |
| 16 | `tests.md` § Behave scenario tagging (`--behave-req-tags`) | 4 | 8 | Prose #3 (and scorecard row #39 Notes) declare scope as "heavy-lane and foundation-kind OBPIs" — check is **entirely scope-blind** (check #6). Prose asserts all heavy/foundation REQs must have scenario coverage; check asserts only that feature-level `# @covers` comments must have matching scenario tags in the same file (check #7, #8). Direction is reversed: prose is OBPI→feature, check is feature→feature. | (none) | **divergent** |
| 17 | Scorecard meta-rule (`--advisory-scorecard`) | 2 | 5 | Prose asserts "the catalog could be a test that fails when a new rule is added without a score" — score validity (prose assertion 1's stem-match satisfies "a row exists") is not checked. Check #3, #4, #5 all show prose-wider gaps. Stale-row handling is missing entirely. | Check stem-match is case-insensitive substring anywhere in text — a rule stem mentioned in a narrative paragraph but not in a scorecard row counts. Risk: a deleted rule mentioned in prose somewhere else makes the check pass. | **prose-wider** |
| 18 | `brief-heading-conventions.md` — H3 evidence (`--brief-headings`) | 6 | 8 | Prose #2 enumerates three canonical headings and check enforces exactly those three. Prose does not assert presence — check also does not (check #8 makes this explicit). **Prose and check agree at the negative-check level.** | Check #7 parenthetical-stripping behavior (`split("(")[0]`) is mechanical detail; an author using an em-dash suffix rather than a paren would silently drop out of the check. Minor but prose-wider if an author uses `## Key Proof — v2` instead of `## Key Proof (v2)`. | **parity** |

---

## Verdict summary

| Verdict | Count |
|---|---|
| parity | 5 |
| prose-wider | 10 |
| check-wider | 0 |
| divergent | 3 |

**Total audited**: 18 promoted scope flags.

---

## Prose-wider cases, ranked by risk

(Prose-wider means operators see rule text promising more than the check
actually enforces. The class of silent drift this chore exists to measure.)

1. **`--utf8-prefix`** (row 7) — rule `cross-platform.md:79-101` explicitly
   declares fresh-interpreter helpers (`python -c`,
   `uv run python <script>`, `tools/**`) need explicit `sys.stdout.reconfigure`;
   check covers **none of it**. GHI #234 observed this exact failure
   class; the rule-text fix landed, the mechanical fix did not.
2. **`--type-ignores`** (row 11) — the positive form assertion
   (`# ty: ignore[<ty-code>]` with ty-code specificity) is entirely
   unenforced. `# ty: ignore[totally-bogus-code]` passes.
3. **`--pydantic-models`** (row 12) — `model_config = {}` satisfies the
   check even though the prose demands `ConfigDict(frozen=True,
   extra="forbid")`. The frozen/forbid semantics — the actual point of
   the Pydantic discipline — is unchecked.
4. **`--version-release`** (row 8) — `pyproject.toml` / `__init__.py` /
   README-badge triple is named in prose; only pyproject is checked. A
   version drift between the three files lands silently.
5. **`--advisory-scorecard`** (row 17) — stem-as-substring-anywhere is
   weak: a rule stem referenced in a narrative paragraph of the scorecard
   (but without a scorecard-table row) passes the check. Score presence
   and stale-row detection both absent.

---

## Divergent cases, ranked by risk

(Divergent means the rule and the check tell the operator two different
stories about what "passes" means — highest drift risk.)

1. **`--behave-req-tags`** (row 16) — prose scopes to "Heavy-lane and
   foundation-kind OBPIs" (scorecard row #39 Notes) and the check is
   scope-blind, plus the check's direction is feature→feature while the
   prose's direction is OBPI→feature. A Heavy OBPI with zero feature
   coverage passes the check entirely — the check literally cannot see
   the violation the prose forbids.
2. **`--reconcile-freshness`** (row 2) — prose asserts reconciliation is
   "tested, gated, and part of the pipeline"; the check treats an empty
   reconcile-event history as a pass (fail-open at check #6). A
   reconciliation pathway that has never fired looks exactly like a
   green pathway.
3. **`--cli-alignment`** (row 9) — the rule-file source for this check is
   implicit: `governance-core.md` does not state the rule directly. The
   check excludes `.gzkit/skills/**/SKILL.md`, which is where the
   tool-skill-runbook-alignment rule asserts skills must wield real
   verbs. An unresolvable `gz <verb>` in a SKILL.md file passes this
   audit but violates the spirit of the tool-skill-runbook-alignment
   rule whose Invariant 1 was promoted alongside.
