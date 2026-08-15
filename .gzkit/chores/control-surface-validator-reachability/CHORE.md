# CHORE: Control Surface — Validator Reachability & Ungated Ratchet (Pass D)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `control-surface-validator-reachability`

---

## Overview

Audit-plus-ratchet pass. Tier every runnable `gz validate --<scope>` by **what
invokes it**, sweep each scope individually to record its own exit code, and hold
the ungated set to a shrink-only baseline.

Passes A, B and C of this family all ask about **content relationships** — rule
vs rule (A), skill vs rule (B), rule prose vs check semantics (C). None asks
whether a check *runs*. A validator can cover its rule's prose exactly (Pass C
green) and be cited by the right skill (Pass B green) and still execute on no
commit path, in which case it protects nothing while reading as coverage.

## Background

Surfaced 2026-08-15 by a health-and-integrity audit run against the operator's
report that gzkit felt "wobbly and misaligned". Sweeping all 92 runnable scopes
individually found **89 pass, 3 fail** — and all three failures sat outside the
gated tier, so `uv run gz check` was green while they failed:

| Scope | Exit | Finding |
|---|---|---|
| `--audits` | 1 | Set two solo-only scopes alongside six aggregate ones, so the umbrella refused itself and ran nothing |
| `--deprecated-verb-prescription` | 3 | A rule's version-history line *documenting* a repoint tripped the checker shipped with that repoint |
| `--evaluation-justify-binding` | 3 | Two ADRs below threshold, missing `gz-justify` artifacts |

The load-bearing observation is not the count. **Two of the three were
regressions introduced by the fix for the previous defect** (GHI #704 hardened
scopes to solo-only and bricked the umbrella that fanned into them; GHI #705
shipped a checker that then failed the file describing the fix it shipped).
Neither could be caught, because neither scope runs in `gz check`.

> A fix that closes a false green by creating a never-run gate has not closed the
> false green; it has relocated it.

**Tier B is an upper bound, not a coverage figure.** All three failures were
Tier B — nominally "covered by tests." That the live repo violated them anyway
means those tests exercise their validator against *fixtures* rather than against
this repository. The test passes, the repo is dirty, and nobody is told.

## Policy and Guardrails

- **Lane:** Lite — audit-only on the validator surface; this chore never edits
  `src/gzkit/commands/validate*` or any check implementation.
- **Scope enumeration is from the live parser, never a roster.** `runnable_scopes()`
  reads `_build_parser()`, so a scope registered tomorrow is covered with no edit
  here. Value-taking flags are derived from the parser's action classes;
  `--evaluation-justify-binding` survives that filter because its argument is
  optional (`nargs="?"`) and it runs bare like any other scope. Only six flags are
  named by hand — `--json/--quiet/--verbose/--debug` (presentation) and
  `--regenerate/--recalibrate` (mutate state; running them is not an audit) — because
  they are `store_true` like every real scope and cannot be told apart structurally.
- **Gating is a property of the caller, not the citation.** A scope is gated only
  when it is in the `gz check` step registry (`src/gzkit/commands/quality.py`) or
  invoked from `.claude/hooks/`, `.github/workflows/`, or `.pre-commit-config.yaml`.
  Being named in a doc, a skill, or a test is not gating.
- **One invocation may gate several scopes.** `.pre-commit-config.yaml` runs
  `gz validate --bullet-retention --surface-weight --pointer-anchors` on one line.
  The scanner consumes the whole run of flags; capturing only the leading flag
  understated the gated set by two and would have frozen two gated scopes into the
  ratchet as ungated.
- **The ratchet may only shrink.** `--report --write` refuses to re-baseline when
  the set grew. A ratchet that rewrites itself upward is not a ratchet.

## Workflow

### 1. Tier census

```bash
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --report
```

Record the tier table and the orphan list in `proofs/reachability-matrix.md`.

| Tier | Meaning | Disposition |
|---|---|---|
| **A** | Gated — `gz check` registry, hook, CI, or pre-commit | none; this is the target state |
| **B** | Referenced only from `tests/**` or `features/**` | verify the test runs against the **live repo**, not a fixture; if fixture-only, the scope is effectively ungated |
| **C** | Named in docs or skills, invoked by nothing | wire into a gate **or retire** |
| **D** | No caller anywhere | delete — an orphan validator is dead code wearing a gate's clothes |

### 2. Conformance sweep (absorbed Axis 0)

Run every scope **individually** and read its own exit code. Individually
matters: solo-only scopes refuse combination outright (GHI #704), and `--audits`
was found broken precisely because it was run alone.

```bash
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --sweep
```

The sweep is Python, not shell, for two reasons both observed while building
this chore:

- **Shell word-splitting is not portable and bit once already.** A hand-rolled
  `for f in $FLAGS` loop silently passed all 105 flags as ONE argument under
  `zsh`, which does not word-split unquoted expansions, producing a single bogus
  failure that read like a real finding. A `.sh` sweep would also violate
  `.claude/rules/cross-platform.md` — gzkit targets Windows, macOS and Linux
  co-equally.
- **Never pipe the verifier.** `.gzkit/rules/tests.md` § Verification exit-code
  integrity is mechanically enforced by the `verifier-pipe-gate.py` hook — the
  shell reports the filter's exit, not the validator's. `--sweep` captures each
  process's own `returncode`, so there is no pipeline to mask it.

Record the exit-code table in `proofs/conformance-sweep.md`. **A non-zero exit on
a Tier B/C/D scope is the headline finding**, not the failure itself: it is a
gate that was already broken and had no way to tell anyone.

### 3. Ratchet enforcement

```bash
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py
```

Exit 3 when a scope entered the ungated set. Recovery is to wire it into a gate
or retire it — never to re-baseline upward.

### 4. Route findings

Findings route as **retirement or promotion, per scope**. This chore's output is
a disposition list, not a report. Where a scope's routing needs a decision the
chore cannot make, file it per `AGENTS.md` § Behavior Rules — Always #13.

## Acceptance Criteria

- `check_reachability.py --self-test` exits 0 (tiering assertions, deterministic)
- `check_reachability.py` exits 0 (the ungated set has not grown)
- Proof artifacts postdate the surfaces they audit

## Cadence

Run when the validator surface changes shape — a new `gz validate` scope, a new
`gz check` step, or a hook/CI edit — and at minimum before each release. The
ratchet makes the between-runs case safe: a new ungated scope fails the chore
whenever it next runs, rather than waiting for someone to notice.

## Related

- `control-surface-rule-conflicts` (Pass A) — rule-pair contradiction matrix
- `control-surface-skill-rule-reachability` (Pass B) — skill ↔ rule reachability
- `control-surface-rule-vs-check-drift` (Pass C) — rule prose vs check semantics
- `data/waiver_ratchet_registry.json` — where this chore's baseline is registered
  (ADR-0.0.73 Boundary Invariant #8; an unregistered `*_grandfather*.json` fails closed)
- `docs/governance/state-doctrine.md` — Layer-3 views are never source-of-truth
