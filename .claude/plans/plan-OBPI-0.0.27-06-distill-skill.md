# Plan: OBPI-0.0.27-06-distill-skill

**OBPI:** OBPI-0.0.27-06-distill-skill
**Parent ADR:** ADR-0.0.27-exemplar-corpus-doctrine (foundation, heavy)
**Date:** 2026-05-05

## Context

Author the `gz-complexity-distill` skill at `.gzkit/skills/gz-complexity-distill/`
and propagate to vendor mirrors via `gz agent sync control-surfaces`. The skill
carries the corpus list, per-project path filters, methodology rationale, and
the three distillation-cadence triggers from ADR-0.0.27 § Decision § Cadence.

Brief amended 2026-05-05 (this session) to (a) drop vendor-mirror entries from
Allowed Paths per `.gzkit/rules/skill-surface-sync.md` Rule #4 and (b) accept
a `gz_command_status: deferred` waiver path tracked by GHI #400 — the skill
ships against the waiver shape; the destination CLI verb (`gz complexity
distill` or equivalent) is authored under GHI #400.

### Destination-in-mind disclosure (Step 6a)

Approach already considered: ship a **declarative skill body** that documents
cadence triggers verbatim from parent ADR, references corpus + OBPI-04
contract by path, declares Output Contract for the deferred verb, carries
the waiver fields. **No `scripts/` directory** — the skill is operator-runnable
ad-hoc (operator invokes the verb when GHI #400 lands; until then the skill
documents what to run). OEE doctrine § "only if a script-backed surface is
materially better than direct CLI invocation" forbids speculative scripts.

### Rejected alternatives

1. **Author verb in this OBPI (Option A from operator decision).** Rejected
   2026-05-05 by operator — bundles two operator-surface deliveries. Tracked
   via GHI #400 waiver instead.
2. **Include shell scripts under `scripts/`.** Rejected — the destination
   verb will be the canonical surface; pre-authoring scripts that wrap a
   non-existent verb is speculative work. If scripts later prove useful
   they can be added at GHI #400 close time.
3. **Inline corpus content in SKILL.md (vs. cite by path).** Rejected by
   REQ-03/04 — single source of truth lives at `data/exemplar_corpus.json`.

## Files

### Create

- `.gzkit/skills/gz-complexity-distill/SKILL.md` — canonical skill body with:
  - Frontmatter: `name`, `description` (triggers on "run distillation",
    "refresh complexity corpus", "distill complexity"), `category`,
    `lifecycle_state: active`, `owner: gzkit-governance`, `last_reviewed`,
    `metadata.skill-version: "0.1.0"`, `gz_command_status: deferred`,
    `deferred_gh_issue: 400`
  - Body sections:
    - Overview / Purpose
    - Cadence triggers (verbatim from ADR-0.0.27 § Decision Cadence: annual
      calendar, drift > 25% with 6-month re-distillation guard, judgment for
      ground-breaking projects)
    - Corpus reference (cite `data/exemplar_corpus.json`; do not duplicate)
    - Per-project path filters (cite corpus entries; do not duplicate)
    - Methodology rationale (agent-driven, operator-attested per OEE; OBPI-04
      brief shape this skill is bound to produce)
    - Output Contract (form the deferred verb is required to produce on GHI
      #400 close: dated distilled-characteristics document under
      `docs/governance/complexity/`)
    - Workflow (when verb lands: `uv run gz complexity distill --corpus
      data/exemplar_corpus.json --baseline <latest>`; until then: operator
      direct-invokes `src/gzkit/complexity/distillation.py:render_document`
      against the latest baseline as documented in OBPI-04 brief)
    - Waiver disclosure (gz_command_status: deferred; tracking GHI #400)
    - References (parent ADR, OBPI-04 brief, related rules)

- `tests/skills/test_gz_complexity_distill.py` — REQ-derived tests, each
  decorated with `@covers("REQ-0.0.27-06-NN")`:
  - REQ-01: SKILL.md frontmatter validates against the canonical skill
    frontmatter rules (required fields present; description ≤ 1024 chars;
    `metadata.skill-version` is `"0.1.0"`; `name` matches directory)
  - REQ-02: Body declares all three cadence triggers (annual calendar,
    drift > 25% with 6-month guard, judgment trigger) — searched as
    substring matches against canonical phrasing
  - REQ-03: Body cites corpus by path `data/exemplar_corpus.json` and does
    not embed corpus entries inline (no `pinned_sha:` keys, no project
    URL list duplicating the corpus)
  - REQ-04 (waiver shape): Output Contract section names the form the
    deferred verb is required to produce on GHI #400 close
  - REQ-05 (waiver shape): Frontmatter carries `gz_command_status: deferred`
    and `deferred_gh_issue: 400`
  - REQ-06: Output Contract section is present and explicit per
    `tool-skill-runbook-alignment.md` Invariant 3
  - REQ-07: Vendor mirrors at `.claude/skills/`, `.agents/skills/`,
    `.github/skills/` are byte-equal to canonical after `gz agent sync
    control-surfaces` (test reads canonical and each mirror via
    `tempfile`-backed setup; no live sync invocation in test)
  - REQ-08 (waiver path): Test asserts the waiver shape rather than verb
    resolution; on GHI #400 close, the test is amended in tandem
  - REQ-11: NEVER include the operator's personal email — assert no `@`
    address pattern in SKILL.md or tests other than `@users.noreply.github.com`
    or `@covers(...)` decorator references

### Modify

- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-06-distill-skill.md`
  (already amended 2026-05-05 in this session — vendor mirrors removed,
  REQs 04/05/08 amended, GHI #400 added to Tracked Defects; further
  evidence-section updates land at Stage 4)

### Generated by sync (do not edit directly)

- `.claude/skills/gz-complexity-distill/SKILL.md`
- `.agents/skills/gz-complexity-distill/SKILL.md`
- `.github/skills/gz-complexity-distill/SKILL.md`

## Steps

1. **TDD red** — Author `tests/skills/test_gz_complexity_distill.py` with
   the eight REQ-derived tests above. Run `uv run -m unittest
   tests/skills/test_gz_complexity_distill.py -v` and capture all failures
   (file does not exist; tests cannot import target).
2. **TDD green** — Author `.gzkit/skills/gz-complexity-distill/SKILL.md`
   with all seven body sections + frontmatter satisfying the eight tests.
3. **Sync** — Run `uv run gz agent sync control-surfaces` to propagate to
   vendor mirrors. Capture diff (must be empty post-sync per REQ-07).
4. **Stage 3 baseline** — Run ARB-wrapped `gz arb ruff`, `gz arb typecheck`,
   `gz arb step --name unittest -- uv run -m unittest -q`,
   `gz arb step --name mkdocs -- uv run mkdocs build --strict`,
   `gz validate --documents --surfaces`, `uv run gz cli audit`.
5. **REQ→@covers parity gate** — Run `uv run gz covers
   OBPI-0.0.27-06-distill-skill --json`; uncovered_reqs must be 0.
6. **BDD coverage** — REQ-07 / REQ-09 alignment: register OBPI-06 BDD
   coverage in `data/behave_coverage_waivers.json` if appropriate (the
   parent ADR's per-OBPI BDD pattern); inherit OBPI-04's
   `adr-0.0.27-04-bdd-deferred-to-obpi-06` waiver close, or write a
   BDD scenario tagged `@REQ-0.0.27-06-NN` covering a fixture-mode
   skill invocation.
7. **Stage 4 evidence** — Author the skill brief evidence sections
   (Implementation Summary, Key Proof, Files created/modified, REQ
   coverage table) per AGENTS.md § Brief heading conventions.
8. **Stage 4 ceremony** — Present evidence; foundation+heavy → TTY+ATTEST.
9. **Stage 5 sync** — `gz obpi precomplete`, then PTY-allocated
   `gz obpi complete --attestor-present`, lock release, marker cleanup,
   `gz git-sync --apply`, `gz obpi reconcile`, `gz adr status`,
   second `gz git-sync --apply`.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_gz_complexity_distill.py -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents --surfaces
uv run gz cli audit
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz covers OBPI-0.0.27-06-distill-skill --json  # uncovered_reqs == 0
```

## Notes

- **Plan-audit known limitation.** The four "Allowed path does not exist"
  gaps are inherent — `gz plan audit` checks paths exist on disk and
  cannot distinguish stale paths from to-be-created paths. The pipeline
  runtime tolerates this state (warning, not block). The vendor-mirror
  gap class (the actual GHI #393 fail-close intent) is cleared by this
  amendment; the existence-check noise will resolve as Stage 2 lands
  the new files.
- **Lock state.** Pipeline marker at
  `.claude/plans/.pipeline-active-OBPI-0.0.27-06-distill-skill.json` was
  written by Stage 1 of the canonical runtime invocation (2026-05-05).
  Lock claimed; do not re-claim.
- **Scope discipline.** REQ-coverage gate (Stage 3 Phase 1b) requires
  every REQ in the brief to have a covering test. The eight tests above
  cover REQs 01-08 + 11; REQs 09 and 10 are doctrine assertions
  (waiver-path narrative + TDD/tempfile discipline) that the test author
  satisfies by the test design itself; verify parity gate counts them
  as covered before completion.
