---
id: ADR-pool.feature-adr-semver-discipline
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.feature-adr-semver-discipline: Feature-ADR Semver Discipline: authoring, validation, and rendering mechanics

## Status

Pool

## Intent

Feature-ADR semver discipline is doctrine-only. AGENTS.md § Local Agent Rules
declares feature ADR IDs are *sequence positions* (semantic, contiguous), and
ADR-0.0.57 § Decision item 3 sharpens this by carving out the foundation
counter-rule (foundations are nominal/sparse). No mechanism was ever designed
to enforce the rule at any of the three surfaces where drift can enter:

1. **Authoring surface** — `gz adr promote --semver` takes an operator-supplied
   minor with no next-free-feature-minor guard. The symmetric foundation
   path enforces next-free-integer; the feature path is silent.
2. **Validator surface** — no `gz validate --feature-semver-contiguity` scope
   exists. `gz check` cannot fail-close on a gap. The rule sits in
   `docs/governance/advisory-rules-audit.md` as Promotable but was never
   promoted to mechanical.
3. **Rendering surface** — `gz adr report` enumerates from earlier
   `artifact_renamed`/`adr_created` events without applying the most-recent
   rename chain, emitting `pool_demotion`-renamed feature IDs as Pending
   feature rows. This violates a Layer-3 invariant from
   `docs/governance/state-doctrine.md` that predates the missing-feature
   surface — it is a genuine defect, not a missing-design symptom, but it
   compounds the missing-design problem by masking the gap visibly.

**Concrete drift instance.** On 2026-05-18 (commit `f311feac`), three pool
ADRs were promoted with explicit semvers `0.48.0`, `0.49.0`, `0.50.0` against
a baseline whose maximum feature semver was `0.28.0`, opening a 19-id gap
(`0.29.0`–`0.47.0`). The semvers were chosen to mirror parallel foundation
IDs (`0.0.48`–`0.0.51`) — exactly the cross-axis confusion the foundation
counter-rule warns against. The three promoted artifacts were demoted back
to pool on 2026-05-23 (commit `a95bba15`, GHI #520) but the gap remains and
the renderer continues to emit the demoted IDs as Pending feature rows.

This is the canonical shape Anti-vibing operative claim 3 warns about:

> Doctrine drift is invariant drift. Silent rule/threshold changes without
> a witness are the root failure.

The rule landed in AGENTS.md without a witness; the witness surfaces were
never designed.

## Decision

Design and implement feature-ADR semver discipline as **one coordinated set
of mechanics across three surfaces**, plus a migration ceremony for the
present gap. The discipline lives in a single foundation ADR (promoted from
this pool) so the three surfaces share the same authoring pass, the same
override-semantics design, the same ledger-event shape, and the same
operator documentation — not three independent fixes that drift relative
to each other.

### Mechanic 1 — Authoring guard (`gz adr promote`)

- Default `--semver` for `--kind feature` to `next-free-feature-minor`
  (max-on-disk feature semver-minor + 0.1.0) when not supplied. Empty-state
  baseline is `0.1.0`.
- When `--semver` is explicit and non-contiguous, fail-close with remediation
  pointer to the override flag.
- Override path: `--allow-non-contiguous --reason <text>`. Both flags
  required together; bare `--allow-non-contiguous` fail-closes with a "name
  the reason" pointer (mirrors the `--accept-uncovered-reason` discipline
  from ADR-0.0.25).
- Override emits an extended `artifact_renamed` event with
  `semver_skip_reason: <text>` and `operator: <name>` fields. Reason text
  is mechanically required so the override cannot be a one-token escape
  hatch (parallel to the GHI #466 Component-A inline-marker design).

### Mechanic 2 — Validator (`gz validate --feature-semver-contiguity`)

- Walks on-disk feature ADR packages from canonical directories.
- Sorts by semver-minor semantically (per AGENTS.md § Local Agent Rules
  ordering rule).
- Fail-close (exit 3) on any gap (missing minor between observed min and
  max) unless the gap is covered by a ledger `artifact_renamed` event with
  `semver_skip_reason` carrying the operator-attested reason.
- Included in default `gz check` pipeline.
- Catalogued under AGENTS.md § Mechanical scopes that bind here.

### Mechanic 3 — Renderer chain-resolution (`gz adr report`)

This mechanic is genuinely defect-shaped (#557) and would be needed even
absent the semver-discipline design — Layer-3 derived views must honor
canon and ledger truth per `docs/governance/state-doctrine.md`. It is
included here so the three surfaces ship as one coordinated patch, not
because chain-resolution depends on semver discipline.

- Locate the `gz adr report` enumeration source; identify whether it walks
  on-disk canon, the ledger, or both.
- Apply rename-chain resolution before rendering: for each candidate ADR
  ID, walk the latest `artifact_renamed` chain; drop entries whose latest
  rename routes to a `pool_*` ID or whose on-disk package is absent.
- Audit sibling enumeration surfaces (`gz state`, `gz adr status`,
  `gz register-adrs`) for the same defect shape; share one chain-resolution
  helper rather than reimplementing.

### Migration — the present 0.29.0–0.47.0 gap

The 19-id gap created on 2026-05-18 is not retroactively a defect under
the new mechanics — the override path explicitly accommodates intentional
skips. But the gap was not attested with a reason at the time; the
mechanism for that didn't exist. Three options:

| Option | Effect | Tradeoff |
|---|---|---|
| **A. Backfill attestation** | Emit a single ledger `artifact_renamed`-style event with `semver_skip_reason: "Pre-mechanism gap; see commit f311feac and GHI #520 demote ceremony"` covering 0.29.0–0.47.0. Validator accepts. | Honest about the gap; preserves the historical record; one ledger event closes the audit chain. |
| **B. Renumber affected feature ADRs** | Migrate `ADR-0.48.0+` IDs down to `0.29.0+`. Requires `gz adr migrate-semver` or equivalent; affects ledger events, commit history references, OBPI parent links. | Restores contiguity but propagates renames through the audit chain; collision risk if other parties have cited the IDs externally. |
| **C. Accept the gap as historical** | No mechanism change; validator special-cases the historical range. | Embeds historical accident in the validator surface — exactly the "silent rule/threshold change" anti-pattern. Rejected. |

Recommended option **A** (backfill attestation). It is the only option that
honors the new override-semantics design rather than embedding a one-off
exemption. Promotion of this pool ADR should book Option A unless the
operator names a specific reason to renumber.

### Surface scope

| Surface | Mechanic | Source-of-truth |
|---|---|---|
| `gz adr promote` | Authoring guard + override | `src/gzkit/cli.py` (promote handler), `src/gzkit/events.py` (ledger event schema) |
| `gz validate --feature-semver-contiguity` | Validator scope | `src/gzkit/trust_audits.py` (or wherever validator scopes live), `src/gzkit/cli.py` (flag plumbing) |
| `gz adr report` (+ siblings) | Renderer chain-resolution | `src/gzkit/cli.py` (report handler), shared helper in `src/gzkit/governance/` |
| Manpages | Documentation | `docs/user/manpages/adr.md`, `docs/user/manpages/validate.md` |
| Scorecard | Doctrine ledger | `docs/governance/advisory-rules-audit.md` (Promotable → Mechanical transition) |
| Mechanical scopes list | AGENTS.md anchor | AGENTS.md § Mechanical scopes that bind here |

## Alternatives Considered

### Alt 1 — Three independent defect fixes (rejected)

Treat #555, #556, #557 as independent GHIs and route each through
defect-fix routing or its own OBPI ceremony. Rejected because:

- The three surfaces share authoring-time design decisions (override flag
  shape, ledger event schema, error message wording) that drift if
  designed independently — exactly the failure shape AGENTS.md § DO IT
  RIGHT 1a (coupled-surface coherence) warns against.
- Two of the three are missing-design, not defects. Routing missing-design
  through the defect queue is the laundering anti-pattern the operator
  flagged when reviewing the original three-GHI cut.

### Alt 2 — Foundation ADR with no migration plan (rejected)

Author the ADR covering only the three mechanics, leaving the present
0.29.0–0.47.0 gap unresolved. Rejected because the gap is the concrete
evidence that drove the design — leaving it unresolved would land the
mechanism without the historical artifact graph being consistent with it.
The validator would then either (a) special-case the historical range
(silent rule/threshold change) or (b) fail-close immediately on default
`gz check` (broken-windows starting state). Neither is acceptable.

### Alt 3 — Per-surface OBPIs under an existing active ADR (rejected)

Decompose into three OBPIs and attach them to an existing active ADR
(candidates: ADR-0.0.21 chores, ADR-0.0.57 foundation-ADR-doctrine).
Rejected because:

- ADR-0.0.21 is about the chores system surface, not ADR semver semantics —
  parent mismatch.
- ADR-0.0.57 sharpened the *rule scope* (foundations nominal, features
  semantic). It did not design the *mechanism*. Attaching mechanics to it
  as OBPIs would expand its closed scope and corrupt its decision record.
- The three mechanics span CLI authoring, validator scope, and renderer
  internals — too cross-cutting to live under any existing foundation
  cleanly. They warrant their own foundation ADR after promotion.

### Alt 4 — Renderer fix only, defer authoring + validator (rejected)

Fix #557 as a direct defect (the Layer-3 invariant violation), leave
#555/#556 as long-running GHIs until enough drift evidence accumulates to
justify the design. Rejected because:

- The renderer fix alone makes the gap *invisible* (orphan rows disappear)
  without preventing future gaps. The next operator running `gz adr
  promote --semver 0.99.0` reproduces the drift, now silently because the
  renderer hides it.
- "Wait for more evidence" is the long-lived shadow-tracker anti-pattern
  the ghi-author skill § Doctrine item 4 names.

## Promotion Plan (Feature Checklist)

When promoted to foundation kind (next-free foundation integer per
ADR-0.0.57 § Decision item 1), the ADR scaffolds the following OBPIs:

1. **OBPI-01** — `gz adr promote` authoring guard: default allocation +
   override flags + ledger event extension (`semver_skip_reason`,
   `operator`).
2. **OBPI-02** — `gz validate --feature-semver-contiguity` validator scope
   + `gz check` inclusion + AGENTS.md mechanical-scopes catalogue entry.
3. **OBPI-03** — `gz adr report` chain-resolution helper + sibling-surface
   audit (`gz state`, `gz adr status`, `gz register-adrs`) + regression
   test against the present orphan rows.
4. **OBPI-04** — Migration ceremony for the 0.29.0–0.47.0 gap (Option A
   backfill attestation unless operator overrides).
5. **OBPI-05** — Documentation update across manpages, runbooks, advisory
   scorecard (Promotable → Mechanical transition).

## Source GHIs (routing complete)

- **#555** — `gz adr promote: --semver accepts non-contiguous feature
  minors with no next-free guard` → closes `superseded` against this pool
  ADR.
- **#556** — `validate: no --feature-semver-contiguity check; feature-ADR
  sequence doctrine unenforced` → closes `superseded` against this pool
  ADR.
- **#557** — `gz adr report: renders pool_demotion-renamed IDs as Pending
  feature ADRs (Layer-3 drift)` → remains open as a defect; will be closed
  `fixed` when OBPI-03 lands (the genuine defect surface within this ADR's
  scope, but routed as a defect rather than `superseded` because the
  underlying Layer-3 invariant violation existed independent of the
  missing-design scope).

## Related ADRs and rules

- ADR-0.0.57 — Foundation ADR ID doctrine (counter-rule; this ADR is the
  feature-side sibling).
- AGENTS.md § Local Agent Rules — ordering rule for feature semvers.
- AGENTS.md § Anti-vibing operative claim 3 — doctrine drift = invariant
  drift.
- AGENTS.md § Architectural Boundaries item 6 — derived views never
  source-of-truth (#557's anchor).
- `docs/governance/state-doctrine.md` — Layer-3 invariants.
- `docs/governance/advisory-rules-audit.md` — Promotable scorecard entry.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
