<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Advisory Rules Audit — Mechanical Enforcement Scorecard

**Session date:** 2026-04-18
**Companion doctrine:** [trust-doctrine.md](./trust-doctrine.md)
**Purpose:** Catalog every rule currently stated as agent-facing doctrine in `CLAUDE.md` and `.gzkit/rules/`, score its mechanical-enforceability, and name the highest-leverage candidates for promotion from advisory to fail-closed.

---

## Why this audit exists

The ADR-0.0.16 closeout cascade (trust-doctrine.md § *The 2026-04-18 outage taxonomy*) proved that **advisory rules without mechanical enforcement accumulate invisible drift until one operation stresses all the cracks at once**. Nine concurrent silent failures had been sitting in production for weeks, each individually an honest doctrine violation, collectively a full-session outage.

The lesson: rules that depend on agent discipline are unreliable over long runs, especially under agent rotation and multi-session work. Every rule that *could* be a test *should* be a test.

This audit scores every rule by:

| Score | Meaning |
|---|---|
| **Mechanical** | Already has a fail-closed check (unit test, validator scope, pre-commit hook). No agent discipline required. |
| **Promotable** | Could become mechanical; naming the specific check is tractable. |
| **Judgment** | Requires human or agent judgment by its nature. Mechanical enforcement would overconstrain. |
| **Ambiguous** | Scope is unclear enough that the first step is rule clarification, not mechanization. |

---

## Scorecard

### Architectural Boundaries (`CLAUDE.md` § Architectural Boundaries)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | Do not promote post-1.0 pool ADRs into active work | **Promotable** | Pool ADR IDs are deterministic (`ADR-pool.*` or under `docs/design/adr/pool/`); check that no Gate 1+ events fire against them |
| 2 | Do not add more pool ADRs to the runtime track | **Promotable** | Same detection as #1; an ADR whose directory is `pool/` receiving lifecycle events is the violation |
| 3 | Do not build the graph engine without locking state doctrine first | **Judgment** | "Locking" is a human decision; can't mechanize ordering of conceptual work |
| 4 | Do not let reconciliation remain a maintenance chore | **Mechanical** (partial) | `gz state` and `gz frontmatter reconcile` are in the pipeline; `gz chores list` shows them. Full enforcement would require a test that fails if reconcile hasn't run against HEAD |
| 5 | Do not let AirlineOps parity become perpetual catch-up | **Judgment** | Requires a metric ("perpetual") that depends on external repo state |
| 6 | Do not let derived views silently become source-of-truth | **Mechanical** | Enforced by `gz validate --frontmatter`, `--event-handlers`, `--validator-fields`. Trust doctrine operationalizes this rule |

### Local Agent Rules (`CLAUDE.md` § Local Agent Rules)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 7 | Order versioned identifiers semantically, never lexicographically | **Mechanical** | `gz adr report`/`gz state` sort via `semver` library; tests in `tests/test_adr_status.py` lock the order |
| 8 | Add imports with usage in same Edit | **Judgment** | Meta-rule about agent tool use; the ruff hook removing unused imports IS the enforcement |
| 9 | Never prefix `uv run gz` with `PYTHONUTF8=1` | **Promotable** | Could scan skills/runbook for the anti-pattern |
| 10 | Attestation enrichment (pass user words + enrichment + receipt IDs) | **Mechanical** | ARB receipt-ID requirement enforced by `gz arb validate`; heavy-lane fail-closed per `.gzkit/rules/attestation-enrichment.md` |
| 11 | Every version bump → GitHub release | **Promotable** | Could scan `pyproject.toml` version against `gh release list` latest tag; mismatch = error |
| 12 | Use GitHub gitignore template for `.gitignore` scaffolding | **Judgment** | Only applies to `gz init` / scaffolding skills; hard to mechanize retrospectively |

### Governance Core (`.gzkit/rules/governance-core.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 13 | Read AGENTS.md before implementation work | **Judgment** | Pre-work discipline; no compile-time signal |
| 14 | Use `uv run` for Python command execution | **Mechanical** | Ruff + tests run via `uv run`; CI enforces. Runbook + docs scanned by `gz validate --cli-alignment` for `uv run gz ...` form |
| 15 | Do not bypass Gate 5 for Heavy/Foundation | **Mechanical** | `gz closeout` pipeline enforces attestation before `Completed` lifecycle event |
| 16 | Do not edit `.gzkit/ledger.jsonl` manually | **Promotable** | Could add a git pre-commit check scanning staged diff for manual ledger edits |
| 17 | Every defect must be trackable (GHI or agent-insights.jsonl) | **Judgment** | Enforcement is cultural; no reliable mechanical signal for "defect noticed but not tracked" |

### Pythonic Standards (`.gzkit/rules/pythonic.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 18 | No bare `except:` / `except Exception:` | **Mechanical** | ruff BLE001 enforces |
| 19 | Functions ≤50 lines | **Mechanical** | xenon complexity + pre-commit hooks |
| 20 | Modules ≤600 lines | **Mechanical** | Pre-commit check under `.pre-commit-config.yaml` |
| 21 | Classes ≤300 lines | **Promotable** | Not enforced today; could add AST check in `gz validate` |
| 22 | No `Optional`/`List` (use `\| None` / `list[]`) | **Mechanical** | ruff UP007, UP006 |
| 23 | Top-level imports only (no lazy imports) | **Promotable** | Partially enforced by ruff PLC0415; inventory of exceptions documented |
| 24 | Suppress ty diagnostics via `# ty: ignore[<code>]` or bare `# type: ignore` | **Mechanical** | Enforced by `gz validate --type-ignores` (this audit's direct outcome, GHI #197) |

### Data Models (`.gzkit/rules/models.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 25 | All data models use Pydantic `BaseModel` (no stdlib `dataclass`) | **Promotable** | AST scan for `@dataclass` usage in `src/gzkit/**` with a waiver list for test fixtures |
| 26 | Immutable models use `ConfigDict(frozen=True, extra="forbid")` | **Promotable** | AST scan for `class X(BaseModel)` without `model_config = ConfigDict(...)` |
| 27 | Use `str \| None` not `Optional[str]` | **Mechanical** | ruff UP007 |

### Tool / Skill / Runbook Alignment (`.gzkit/rules/tool-skill-runbook-alignment.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 28 | **Invariant 1** — Every CLI tool has a wielding skill | **Promotable** | Explicitly stated in rule as advisory, long-term home is `gz validate --surfaces` |
| 29 | **Invariant 2** — Every skill's `gz_command` matches a runbook-prescribed tool | **Promotable** | Same; testable via skill frontmatter scan + runbook cross-reference |
| 30 | **Invariant 3** — Destination verb's default output matches routing skill's Output Contract | **Promotable** | Harder but tractable; run each skill's `gz_command` against a fixture and assert form markers |

### Skill & Surface Sync (`.gzkit/rules/skill-surface-sync.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 31 | Edit `.gzkit/` first; never edit vendor mirrors | **Mechanical** | `gz agent sync control-surfaces` detects drift; version + commit hash resolution documented |
| 32 | Bump `skill-version` on every skill edit | **Mechanical** | Skill version discipline enforced by sync command; higher version wins |
| 33 | Run sync after every skill/rule edit | **Promotable** | Could fail pre-commit if canonical source edited without follow-up sync |

### Tests Policy (`.gzkit/rules/tests.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 34 | Red-Green-Refactor TDD discipline | **Judgment** | Cannot mechanically verify "test failed before implementation" after the fact |
| 35 | Every commit touching src/tests carries Task: or Ceremony: trailer | **Mechanical** | `gz validate --commit-trailers` — landed under GHI #201 |
| 36 | Use stdlib `unittest` (no pytest) | **Mechanical** | `forbid pytest` pre-commit hook |
| 37 | Two runners: unittest + behave (no tier under unittest) | **Promotable** | Could scan `tests/integration/` et al. and fail if they reappear |
| 38 | Coverage floor ≥40% | **Mechanical** | Pre-commit hook |
| 39 | Behave scenarios covering a REQ carry `@REQ-X.Y.Z-NN-MM` tag | **Promotable** | AST/regex scan of feature files; assert REQ-tagged scenarios exist for each OBPI |

### Constraints (`.gzkit/rules/constraints.md`)

This file is a cross-reference aggregator; every entry maps to one of the rules scored above. Its meta-rule ("these prohibitions are addressed to you — the executing agent") is itself **judgment** — the document's purpose is behavioral guidance for Claude Code sessions, not a mechanical gate.

### Behavioral Invariants (`.gzkit/rules/behavioral-invariants.md`)

Invariants #1–17 in the behavioral invariants doc are primarily **judgment** rules aimed at agent tool use and session behavior:

- "Own the work completely" / "Complete all work fully" / "Never say out of scope" — judgment
- "Fix class of failure, not instance" — judgment (but this audit itself is an instance of applying it)
- "Read AGENTS.md before starting work" — judgment
- "If <90% sure, ask the human" — judgment
- "On inconsistencies, STOP, name confusion, present tradeoff, wait" — judgment

**Invariant #10a** ("When a skill step names a tool, invoke it in the same turn") is **promotable** — could be detected via hook analysis, but the signal-to-noise ratio is probably poor.

---

## Summary

| Score | Count | % |
|-------|-------|---|
| **Mechanical** | 12 | 30% |
| **Promotable** | 14 | 36% |
| **Judgment** | 13 | 33% |
| **Ambiguous** | 0 | 0% |

**The 30% mechanical floor is the actual safety surface.** Everything else depends on agent discipline, and the 2026-04-18 outage demonstrated that a 36%-promotable band is the attack surface — rules that look binding but have no enforcement ride right up to the first composition stress.

---

## Recommended promotion order (highest leverage first)

Each promotion candidate has a tracking GHI. Close the GHI when the promotion lands per the discipline in § Promotion discipline below.

| # | Rule(s) | GHI | Summary |
|---|---------|-----|---------|
| 1 | 28 / 29 / 30 | [#202](https://github.com/tvproductions/gzkit/issues/202) | Skill ↔ CLI ↔ runbook alignment (Invariants 1–3) |
| 2 | 25 / 26 | [#203](https://github.com/tvproductions/gzkit/issues/203) | Pydantic `BaseModel` + `ConfigDict` discipline |
| 3 | 21 | [#204](https://github.com/tvproductions/gzkit/issues/204) | Class size limit (300 lines) |
| 4 | 11 | [#205](https://github.com/tvproductions/gzkit/issues/205) | Version bump → GitHub release alignment |
| 5 | 9 | [#206](https://github.com/tvproductions/gzkit/issues/206) | No `PYTHONUTF8=1` prefix on `uv run gz` |
| 6 | 16 | [#207](https://github.com/tvproductions/gzkit/issues/207) | No manual ledger edits (pre-commit guard) |
| 7 | 1 / 2 | [#208](https://github.com/tvproductions/gzkit/issues/208) | Pool ADRs never touch the runtime track |
| 8 | 37 | [#209](https://github.com/tvproductions/gzkit/issues/209) | No third test tier under `unittest` |
| 9 | 33 | [#210](https://github.com/tvproductions/gzkit/issues/210) | Sync after every skill/rule edit |
| 10 | 39 | [#211](https://github.com/tvproductions/gzkit/issues/211) | Behave scenarios tagged `@REQ-X.Y.Z-NN-MM` |
| 11 | meta | [#212](https://github.com/tvproductions/gzkit/issues/212) | Scorecard self-test (catch new rules added without score) |
| 12 | 4 | [#213](https://github.com/tvproductions/gzkit/issues/213) | Reconcile freshness audit |
| 13 | 6 (extension) | [#214](https://github.com/tvproductions/gzkit/issues/214) | L3 derived-view audits beyond frontmatter/graph |
| 14 | discoverability | [#215](https://github.com/tvproductions/gzkit/issues/215) | Wire trust-doctrine + scorecard into agent control surfaces |

---

## Promotion discipline

When promoting an advisory rule to mechanical:

1. **Write the audit first.** It fails. You observe real current violations (or none). Don't write the audit against a clean state you assumed — you'll miss drift that's already in.
2. **Fix or waive the current violations.** Waivers are explicit dict entries with rationale; silent pass-lists are anti-pattern (trust doctrine T2).
3. **Promote the audit into `gz validate` as a named scope.** Discoverable via `--help`, runnable at pre-commit.
4. **Delete or narrow the advisory rule text.** The rule is now mechanical; the doctrine file can drop the admonition and point at the audit. Doctrine that's mechanical is doctrine that survives agent rotation.

This audit is itself a candidate for promotion: the catalog above could be a test that fails when a new rule is added without a score. That would make the audit self-sustaining. Left as a follow-up — the scorecard shape is still stabilizing.

---

## Related

- `docs/governance/trust-doctrine.md` — the pattern this scorecard supports
- `docs/governance/state-doctrine.md` — storage-layer doctrine; complement to trust doctrine
- `.gzkit/rules/constraints.md` — the cross-reference index of these rules
- `CLAUDE.md` — architectural-boundaries memo (rules 1–6 in scorecard)
