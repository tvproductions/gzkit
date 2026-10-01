# Evidence — gate witness audit, 2026-09-30

One-shot audit artifacts: historical by construction, and outside the served docs and the live-path scans (`tests/governance/_fold_guard.py` `NON_LIVE_ROOTS`).

Raw evidence behind [`docs/governance/gate-witness-audit-2026-09-30.md`](../../../docs/governance/gate-witness-audit-2026-09-30.md).
Read that record first: it says which findings were re-checked in the main session, and it
lists errata for claims in these files that did not survive checking.

**These files are model-authored reports and their inputs. They are data, not rulings.**
The four `audit*.md` reports and `pretest-shape.md` were written by delegated read-only
agents. Where the record and a report disagree, the record governs.

| File | Measurement | Produced by |
|---|---|---|
| `auditA.md` | Completion-evidence gaps: GHI #889, #942, #994, #1093 | delegated agent |
| `o889.json`, `c1093b.txt`, `evhist.txt` | auditA's raw output; its scripts `a889.py`, `c1093b.py` are in `scripts.md` | delegated agent |
| `auditB.md` | Verdict gates: GHI #959, #960, #985, #996 | delegated agent |
| `auditC.md` | Falsifiability and scope: GHI #849, #927, #1057 | delegated agent |
| `audit1057.json`, `touch3.json`, `tier.json`, `red849.json`, `obpi849.json` | auditC's raw output; its scripts `audit1057.py`, `touch3.py`, `tier.py`, `red849.py` are in `scripts.md` | delegated agent |
| `auditD.md` | Exit codes, docs and trailers: GHI #995, #1124, #803, #1017 | delegated agent |
| `dead.json` | auditD's dead-link output; its rebuild script `build.py` is in `scripts.md` | delegated agent |
| `scripts.md` | Transcript of the delegated agents' throwaway scripts, exact source, not runnable in-tree | delegated agents |
| `pretest-shape.md` | Pre-fix test inputs for 9 of the 12 hollow gates | delegated agent |
| `gatemap.py`, `gatemap-final.json` | Mutation sweep of the 98 registered enforcement claims | main session |
| `registered_at_parent.py`, `registered_at_parent.json` | Whether each hollow gate was a registered claim at its fix's parent | main session |

## Re-run

Only the two main-session scripts are runnable (`gatemap.py`, `registered_at_parent.py`). They were made lint-clean before landing, then re-run and reproduced their committed results: the `adr-status-freshness` gate-map row, and all 12 rows of `registered_at_parent.json`. They are read-only with respect to the main checkout. Where they need historical code, they create detached local worktrees and remove them afterwards. The delegated scripts in `scripts.md` are a record of what ran, not a re-run path.

```bash
# Gate map, one shard of four, in a detached worktree (never pushed); run from the repo root
REPO="$(git rev-parse --show-toplevel)"
git worktree add --detach /tmp/gm0 HEAD
(cd /tmp/gm0 && "$REPO/.venv/bin/python" \
  artifacts/audits/gate-witness-audit-2026-09-30/gatemap.py /tmp/gm0 0 4 /tmp/gm0.json)
git worktree remove --force /tmp/gm0

# Registered-at-parent, for the 12 hollow gates (writes registered_at_parent.json into OUT_DIR)
.venv/bin/python artifacts/audits/gate-witness-audit-2026-09-30/registered_at_parent.py OUT_DIR
```

`gatemap.py` reads `GATEMAP_ONLY=<claim,claim>` to re-run selected claims. Population-declared
claims run through the runner's per-member path. That probe fix was applied after the first
pass, and `gatemap-final.json` merges the first pass with that re-run.
