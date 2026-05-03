# AUDIT — ADR-0.0.23-agent-failure-mode-taxonomy

**Phase:** Audit (Layer 2 — read ledger proof, then demonstrate value).
**Outcome:** **PASS — recommend VALIDATED.** All Layer-1 mechanical checks
green; Layer-2 ledger proof exits 0; five delivered capabilities
demonstrated working live; one in-flight defect (frontmatter drift) fixed
in scope per Prime Directive. Receipt ceremony pending operator verbal
attestation.

This file supersedes the prior FAIL audit captured 2026-05-02 earlier in
the day, which terminated at Step 2 with 79 covers-backfill heuristic
false-positives. Those findings were filed at GHI #382 (now closed) and
the heuristic was refined to distinguish same-commit-creation from
backfill-onto-existing-test. The refined heuristic returns exit 0 against
ADR-0.0.23.

## Summary

| Field | Value |
|---|---|
| ADR | ADR-0.0.23-agent-failure-mode-taxonomy |
| Kind / Lane | foundation / lite |
| OBPIs | 5/5 attested completed (g0, ledger Layer-2 proof) |
| Layer-2 verdict | **PASS** — `uv run gz adr audit-check ADR-0.0.23` exits 0 |
| Mechanical state | Unittest 3959/3959 PASS (2 skipped); mkdocs strict build clean; `gz gates --adr ADR-0.0.23` exits 0 after frontmatter reconcile |
| Coverage | 21/30 REQs covered (70.0%); 9 advisory uncovered REQs are doc-shaped surfaces in OBPI-01/02/03 (rule authoring, cross-link, mirror sync) — non-blocking |
| Gate 5 attestation | Pending operator verbal `accept audit` / `verify audit` |
| Lifecycle (pre-receipt) | Completed |

## Execution log

| Step | Check | Result | Proof |
|---|---|---|---|
| 1 | Plan scoped (claims, checks, risk focus) | ✓ | `audit/AUDIT_PLAN.md` |
| 2 | Layer-2 ledger proof (`gz adr audit-check`) | ✓ | `proofs/audit-check.txt` (exit 0) |
| 3 | Demonstrate Value | ✓ | § Feature Demonstration below |
| 4 | Document | ✓ | this file |
| 5 | Identify Shortfalls | ✓ | one in-flight defect (frontmatter drift); fixed in scope |
| 6 | Remediate | ✓ | `gz frontmatter reconcile` rewrote ADR-0.0.23 status `Draft` → `Completed` |
| 7 | Mark VALIDATED | pending receipt | — |
| 8 | Emit Validation Receipt | pending operator verbal ack | — |
| 9 | Verify Lifecycle Update | pending Step 8 | — |

## Layer-1 mechanical state

| Command | Exit | Proof |
|---|---|---|
| `uv run -m unittest -q` | 0 (3959 tests, 2 skipped) | `proofs/unittest.txt` |
| `uv run mkdocs build -q` | 0 (clean, strict) | `proofs/mkdocs.txt` |
| `uv run gz gates --adr ADR-0.0.23` | 0 (Gate 1 PASS, Gate 2 PASS) | `proofs/gates.txt` |

## Layer-2 ledger proof

`gz adr audit-check ADR-0.0.23` exits 0 with the structured output captured
at `proofs/audit-check.txt`:

- **OBPI completion:** PASS — all 5 OBPIs linked in the ledger with
  attested operator signatures.
- **Coverage:** 21/30 REQs covered (70.0%) — OBPI-04 = 10/10, OBPI-05 =
  11/11, OBPI-01/02/03 = 0/3 each.
- **Advisory (non-blocking):** 9 uncovered REQs in OBPI-01/02/03. These
  briefs deliver documentation-shaped surfaces (rule authoring,
  cross-link insertion, mirror sync) whose evidence shape is grep + diff
  + validator exit code, not unit-test coverage. The advisory floor is
  explicitly non-blocking under the refined heuristic.
- **Backfill findings:** none. The covers-backfill heuristic refinement
  shipped under GHI #382 distinguishes "decorator added to existing
  test" (cosmetic backfill, GHI #272 anti-pattern; should flag) from
  "decorator present at file creation" (legitimate same-commit
  authoring; should not flag) by checking whether the introducing commit
  is the file-creation commit.

## In-flight defect — frontmatter drift (fixed in scope)

`gz gates --adr ADR-0.0.23` initially exited 3 with Gate 1 FAIL flagging
frontmatter drift: ledger said `Completed`, ADR file said `Draft`. The
canonical remediation (`gz chores show frontmatter-ledger-coherence`)
prescribes `gz frontmatter reconcile`, which is the in-flight defect-fix
shape — single-file, ≤5 source-line edit, contained to a derived state
field per the chore's "frontmatter is derived state" doctrine. Applied:

```bash
$ uv run gz frontmatter reconcile --json
{
  "files_rewritten": [
    {
      "diffs": [{"after": "Completed", "before": "Draft", "field": "status"}],
      "path": "docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md"
    }
  ],
  ...
}
```

Re-running `gz gates --adr ADR-0.0.23` exits 0 (`proofs/gates.txt`).
No GHI filed — the chore is the prescribed routing for derived-state
drift, and reconcile is the sanctioned mechanism rather than a fix
to track.

## Feature Demonstration

ADR-0.0.23 delivers five capabilities; each is exercised live below.

### Capability 1 — Six-pattern failure-mode taxonomy canonized

Canonical rule at `.gzkit/rules/agent-failure-modes.md` (229 lines, two
YAML frontmatter delimiters) enumerates the six patterns in the
prescribed Opus 4.7 § 2.3.6 order, with `## ` H2 headings:

```bash
$ grep -n '^## ' .gzkit/rules/agent-failure-modes.md
33:## Safeguard circumvention
53:## Reckless action
71:## Fabrication
100:## Skipped cheap verification
124:## Correction fails
144:## Dishonest when caught
170:## When to invoke this vocabulary
197:## Loading posture
215:## Related
```

**Value:** reviewers, auditors, and rule-authors have a shared vocabulary
for the recurring agent failure shapes the AGENTS.md § DO IT RIGHT
invariants are engineered against. Without this, every new rule
re-invents its motivation; with this, `gz validate
--advisory-scorecard` can score new rules against a canonical catalogue.

### Capability 2 — Cross-links into AGENTS.md and the advisory scorecard

```bash
$ grep -n "agent-failure-modes" AGENTS.md docs/governance/advisory-rules-audit.md
AGENTS.md:75:See [`.gzkit/rules/agent-failure-modes.md`](.gzkit/rules/agent-failure-modes.md) for the canonical six-pattern failure-mode taxonomy these invariants backstop ([ADR-0.0.23](docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md)).
docs/governance/advisory-rules-audit.md:195:### Agent Failure-Mode Taxonomy (`.gzkit/rules/agent-failure-modes.md`)
```

**Value:** the always-loaded AGENTS.md DO IT RIGHT section now points at
the catalogue, and the advisory-rules-audit scorecard has a row for the
taxonomy. Discovery from the agent contract surface is one hop, not a
search.

### Capability 3 — Vendor mirrors stay in lockstep with canon

```bash
$ test -f .claude/rules/agent-failure-modes.md && echo "claude mirror: present"
claude mirror: present
$ test -f .github/instructions/agent_failure_modes.instructions.md && echo "copilot mirror: present"
copilot mirror: present
```

The `gz agent sync control-surfaces` PostToolUse hook keeps these mirrors
byte-equivalent to canon (modulo the `<!-- Generated by gz agent sync —
do not edit -->` header line). Per OBPI-03's attested evidence, the
template surface at `src/gzkit/templates/agents.md:78` carries the
cross-link so `gz agent sync` does not strip it on regeneration.

**Value:** Claude Code (`/.claude/rules/`) and GitHub Copilot
(`.github/instructions/`) sessions load the taxonomy without manual
copy. The vendor-mirror invariant is mechanical, not honor-system.

### Capability 4 — `gz issue file` cross-repo defect filing wrapper

The wrapper hard-rejects bodies that reference no gzkit-owned surface,
operationalizing the `Safeguard circumvention` failure shape (filing a
gzkit-surface defect at the consumer's tracker is the same class of
failure as bypassing a hook block):

```bash
$ uv run gz issue file --title "Test" --body "no markers here" --defect --dry-run
error: issue body references no gzkit-owned surface — expected at least one of:
`gz <verb>`, `.gzkit/`, `src/gzkit/`, `gzkit.<module>`. file at the consuming
repo's tracker if the defect is in consumer code; otherwise edit the body to
name the gzkit surface.
EXIT=1

$ uv run gz issue file --title "Test" --body "gz validate --documents miscounts X" \
                       --defect --dry-run
Target: tvproductions/gzkit
Label: defect
Title: Test
Body:
Filed from tvproductions/gzkit running gz v0.26.0

gz validate --documents miscounts X
EXIT=0
```

**Value:** misrouting a gzkit-surface defect to the consuming repo's
tracker is now structurally impossible — the wrapper hard-rejects it
before `gh issue create` runs. The provenance trailer
(`Filed from <consumer-slug> running gz vX.Y.Z`) auto-stamps without
leaking operator PII. Closes GHI #316.

### Capability 5 — `gz adr audit-check` covers-backfill heuristic

The same Layer-2 command that gates this audit demonstrates the heuristic
working correctly (and exit-0-clean against ADR-0.0.23 itself, the ADR
that delivered it):

```bash
$ uv run gz adr audit-check ADR-0.0.23
ADR audit-check: ADR-0.0.23-agent-failure-mode-taxonomy
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.0.23-01-author-failure-modes-rule
  - OBPI-0.0.23-02-cross-link-and-scorecard
  - OBPI-0.0.23-03-sync-mirrors
  - OBPI-0.0.23-04-cross-repo-defect-filing
  - OBPI-0.0.23-05-audit-check-covers-backfill-heuristic
Advisory 9 REQ(s) without @covers traceability (non-blocking):
  ...
Coverage: 21/30 REQs covered (70.0%)
EXIT=0
```

**Value:** the heuristic operationalizes the `Skipped cheap verification`
failure shape — flags decorators added to existing tests in the same
commit as the closing receipt without re-deriving the assertion from
REQ semantics. Refined under GHI #382 to skip same-commit-creation
(legitimate authoring), eliminating the 79 false-positives that blocked
the prior audit run. Closes GHI #309 (taxonomy entry) and GHI #382
(heuristic miscalibration).

## Shortfalls

- **None blocking.** The single in-flight defect (frontmatter drift) was
  the prescribed-chore-driven derived-state correction; fixed in scope.
- **Advisory only:** 9 uncovered REQs in OBPI-01/02/03. These are
  documentation-shape briefs whose evidence is grep + diff + validator
  exit, not unit-test coverage. Non-blocking by `gz adr audit-check`
  doctrine.

## What I explicitly did NOT do

- I did not file a new GHI for the frontmatter drift. The chore
  `frontmatter-ledger-coherence` (ADR-0.0.16, OBPI-03) is the canonical
  routing for derived-state drift; reconcile is the sanctioned
  mechanism, not a tracked defect. Filing a GHI would duplicate the
  chore's intent.
- I did not run `audit-begin` / emit the receipt yet. The skill's
  GHI #292 agent-relayed branch requires operator verbal `accept audit`
  / `verify audit` after `audit-begin` writes the co-presence marker.
  Awaiting that ack.
- I did not rewrite assertions for the 9 advisory uncovered REQs. They
  are structurally non-coverable (rule authoring text, cross-link
  insertions, mirror file existence). Adding `@covers` decorators to
  surface them would be the GHI #272 cosmetic-backfill anti-pattern the
  refined heuristic is designed to detect.

## Recommended next-action

Operator verbal ack `accept audit` or `verify audit` triggers the
ceremony pair:

1. `uv run gz adr audit-begin ADR-0.0.23` — co-presence marker.
2. `uv run gz adr emit-receipt ADR-0.0.23 --event validated --attestor "g0" --attestor-present --evidence-json '{"gate":5,"tests_passed":true,"tests_count":3959,"scope":"ADR-0.0.23","date":"2026-05-02","attestation_text":"<verbatim ack> — <agent enrichment>"}'`
3. `uv run gz adr audit-end ADR-0.0.23` — marker hygiene.
4. `uv run gz adr report ADR-0.0.23` — confirm `Lifecycle: Validated`.

## Attestation (audit signature; not Gate 5)

I (Claude Opus 4.7, model ID `claude-opus-4-7[1m]`) ran this audit on
behalf of g0 on 2026-05-02. My signature on this AUDIT.md
attests to:

- The Layer-1 mechanical state (unittest, mkdocs, gates after frontmatter
  reconcile) being PASS as captured in `proofs/`.
- The Layer-2 audit-check exit-0 verdict captured in
  `proofs/audit-check.txt`.
- Each of the five Feature Demonstration capabilities being exercised
  with live commands and observed output above.
- The frontmatter drift remediation being routed through the canonical
  chore mechanism (`gz frontmatter reconcile`) rather than a hand-edit
  or a tracked defect.

I do **not** attest the ADR as Validated; that requires operator-relayed
Gate 5 attestation via the `audit-begin` / `audit-end` ceremony pair
described above.
