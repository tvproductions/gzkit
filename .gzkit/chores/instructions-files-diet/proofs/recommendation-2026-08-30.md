# instructions-files-diet — recommendation, 2026-08-30

Chore steps 1–3a. **Nothing has been written to any contract surface.** This
document is the § 3 ranked recommendation; § 4 is a binding consult gate and the
operator rules per item or per rank-band before any edit.

Scope: the **rules arm** of GHI #921 (`.gzkit/rules/**` → `.claude/rules/**`).
The `AGENTS.md` corpus arm is operator-initiated under
`ADR-0.35.0-canon-entry-corpus-landing` and is out of scope here.

## § 1–2 measurements

**§ 1 Render — not runnable for this arm, and that is the finding.**
`gz content compose` fails closed on every rule surface: `surface_content_types`
in `data/vendor-manifest.json` declares only `AGENTS.md`, so no rule has a corpus
to compose from. Baseline is therefore measured directly from disk, which is the
honest substitute and is recorded as such.

**§ 2(a) delivery cap — no cap binds this arm.** The surface-delivery witness
(`gz validate --instructions-files-budget`, exit 0) declares caps for
`AgentContract` only. `.claude/rules/**` has no vendor cap, so **the required
delta for this arm is zero.** This is discretionary trimming under § Posture
("exceedance is permitted; this chore is the management valve"), not a gap-closing
run. Ranking is therefore by per-turn co-load cost, not by a delta to clear.

**§ 2(b) delivery routing — clean.** The `.claude/rules/` mirror is the delivered
surface and differs from canonical only by the designed transform (drops `id:` and
`description:` frontmatter, adds the generated marker); e.g. `pythonic.md`
10,334 B canonical vs 10,313 B mirrored. No routing defect.

**§ 2(c) available budget.** 25 canonical rules, 175,979 B. Current-version
rationale blockquotes total **16,994 B**, but the distribution is skewed: after the
`bb85e660` lift most rules sit at ~300–550 B, and **five outliers carry 9,194 B**.

### Per-turn co-load (what a single edit actually loads)

| Edited path | Rules loaded | Bytes loaded | Version blockquote | 5-outlier share |
|---|---|---|---|---|
| `src/gzkit/commands/foo.py` | 9 | 67,913 | 10,236 (15%) | 8,146 (11%) |
| `src/gzkit/governance/x.py` | 8 | 54,617 | 7,917 (14%) | 5,831 (10%) |
| `tests/test_foo.py` | 5 | 48,473 | 4,461 (9%) | 2,850 (5%) |
| `.gzkit/rules/tests.md` | 4 | 37,298 | 3,416 (9%) | 2,096 (5%) |
| `docs/governance/note.md` | 3 | 16,056 | 1,899 (11%) | 885 (5%) |

## § 3a scoring — all five candidates clear the retention gate

`gz validate --advisory-scorecard` exit 0. Of 221 scorecard rows, **94 score
Mechanical or Promotable** and are retained verbatim. Checked by substring against
each candidate blockquote: **zero retained fragments live inside any of the five.**
No `tier: invariant` corpus entry is implicated — this arm has no corpus at all.

The blockquote is preamble narrative, not a scored bullet. Class: **not scored /
narrative**, which is the only class this chore may touch.

## § 3 ranked recommendation

Recommended action is **`compress`, not `lift`** — retain the current-version
first sentence in place, relocate the remaining rationale to
`docs/governance/rule-version-history.md` (the destination `bb85e660` already
established for prior versions), leaving the established one-line pointer.

| # | Item | Scope (how often it loads) | Full | Keep | **Saving** | Cost to a reader |
|---|---|---|---|---|---|---|
| 1 | `pythonic.md` | `**/*.py` — every Python edit | 2,850 | 228 | **2,622** | Loses the worked detail on the two `ty` suppression forms; the binding syntax rule itself is in § Type-check suppression, unaffected |
| 2 | `task-discovery.md` | `src/gzkit/**` — every src edit | 2,096 | 124 | **1,972** | Loses the GHI #753 deferral-retirement narrative; the retained sentence still states the live fact ("enforcement is LIVE") |
| 3 | `cli.md` | `src/gzkit/commands/**` | 2,315 | 196 | **2,119** | Loses the 21-failure measured instance motivating the seven-obligation list; the list itself is binding content and stays |
| 4 | `chores.md` | `src/gzkit/chores/**` — narrow | 1,048 | 203 | **845** | Loses the `deprecated-verb-ok` precedent citation; retained sentence names the marker |
| 5 | `gate5-runbook-code-covenant.md` | `docs/**` + `src/gzkit/**` | 885 | 194 | **691** | Loses the Movement C closure context; retained sentence names the advisory posture |
|   | **Total** | | **9,194** | **945** | **8,249** | |

Cumulative saving clears no required delta because there is none; it removes
**8,249 B from every turn that loads these rules** — 11% of a `commands/` edit.

## The honest counter-argument

This is **not** the same transform as `bb85e660`, and should not be waved through
on that precedent. That lift moved *prior* version entries — archive material whose
only reader is someone auditing history. This moves the *current* entry, which is
the one a resuming agent is most likely to want in-turn, because it explains why
the rule reads the way it now does. The `compress` shape is proposed precisely to
split that difference: the live claim stays, the archaeology goes.

A defensible operator ruling is to take rank-band 1–2 only (4,594 B, the two
broadest scopes) and leave 3–5, or to decline entirely on the grounds that a rule's
current rationale is load-bearing context rather than narrative.

## Not recommended

- Any `tests.md` / `token-block-discipline.md` / `skill-surface-sync.md` block.
  Their large blocks are binding sub-invariants, tables, and proof-channel
  definitions — not narrative. Measured, not assumed.
- `governance-core.md`'s 3,645 B ILLUSTRATIVE-values bullet. It is `**/*`-scoped
  and therefore the single most expensive bullet in the repo, but it is binding
  rule text with a scorecard row. Out of bounds for this chore.

## Status

**Awaiting the § 4 operator ruling.** No contract surface has been edited. Record
the ruling verbatim in `CHORE-LOG.md` before any § 5 action; carry declined items
forward as declined.
