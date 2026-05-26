# OBPI-0.0.59-01: Author REQ Scope Discipline Doctrine + Supersession

## Context

ADR-0.0.59 establishes a three-kind REQ taxonomy (BEHAVIOR / SUPPORT / STRUCTURAL-FENCE)
to fix the categorical category error where gzkit's @covers parity machinery applied a
single proof channel (test decorator) uniformly to all REQ kinds, producing ~3,404
tautological filesystem-grep tests (32% project-wide / 42% governance). OBPI-0.0.59-01
is the doctrine-only precondition: it ships zero code, zero schema, and is the contract
the downstream OBPIs (02-05) consume.

This is pure content work: 4 file edits + 1 new file + 2 GHI actions.

## Files to modify

| File | Action | What changes |
|------|--------|--------------|
| `.gzkit/rules/tests.md` | Edit | Bump rule-version 0.4.0→0.5.0 (comment + blockquote); add GHI #270 reconciliation note inline in Output-form carve-out; append `## REQ Scope Discipline` subsection at end |
| `docs/governance/req-scope-discipline.md` | **CREATE** | New canonical doctrine expansion (mirrors `agents-md-doctrine.md` shape) |
| `docs/governance/advisory-rules-audit.md` | Edit | Append row 59 (REQ Scope Discipline, Mechanical) to scorecard table; update Summary Mechanical 42→43; update narrative paragraph |
| `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` | Edit | Append `## Disposition` section after existing Promotion guidance (line 139) |

## GHI actions

- **GHI #165** — already CLOSED (state: CLOSED confirmed). Add retroactive comment via `gh issue comment 165 --body "..."` citing supersession by ADR-0.0.59, naming ledger_event + parent_adr_invariant as the non-code proof channels the issue requested. Do NOT re-close.
- **GHI #531** — OPEN. Close via `gh issue close 531 --comment "..."` citing ADR-0.0.59 and the doctrinal correction.

## Step-by-step implementation

### Step 1 — Edit `.gzkit/rules/tests.md`

Three changes in one Edit call (import + usage rule):

**a) Bump rule-version comment** (line 8):
- Old: `<!-- rule-version: 0.4.0 -->`
- New: `<!-- rule-version: 0.5.0 -->`

**b) Bump rule-version blockquote** (line 12):
- Old: `> **Rule version:** \`0.4.0\` — diet pass under GHI #327; ...`
- New: `> **Rule version:** \`0.5.0\` — added REQ Scope Discipline subsection (three-kind taxonomy + GHI #270 reconciliation); GHI #327 diet pass preserved.`

**c) Extend Output-form fixture carve-out sentence** to add GHI #270 note:
- Old: `**Output-form fixture carve-out.** Output-form assertions are permitted in dedicated fixture tests per \`.gzkit/rules/tool-skill-runbook-alignment.md\` § Invariant 3. Keep them in separate test classes from REQ-derived unit tests.`
- New: `**Output-form fixture carve-out.** Output-form assertions are permitted in dedicated fixture tests per \`.gzkit/rules/tool-skill-runbook-alignment.md\` § Invariant 3. Keep them in separate test classes from REQ-derived unit tests. *(GHI #270 reconciliation: output-form fixture tests are **BEHAVIOR** REQ proofs under the REQ Scope Discipline taxonomy — they test CLI render-code behavior, not file content. The apparent contradiction between § 6f's prose-content prohibition and Invariant 3's render-form requirement dissolves once REQ kind is named.)*`

**d) Append `## REQ Scope Discipline` subsection** at end of file (before closing `> See ...` pointer):

```markdown
## REQ Scope Discipline (binding)

Every REQ in an OBPI brief's `## Acceptance Criteria` carries exactly one of three kinds,
declared as a bracketed inline tag: `REQ-X.Y.Z-NN-NN [kind]: claim text`.

### Three-kind taxonomy

| Kind | What it covers | Proof channel |
|------|---------------|---------------|
| **BEHAVIOR** | Code behavior — functions, commands, CLI outputs, state transitions | `@covers`-decorated test in `tests/**` (existing pattern, unchanged) |
| **SUPPORT** | Governance artifacts, doctrine docs, rule files, data files that *support* behavior but are not behavior themselves | Ledger `artifact_edited` event citing the artifact path **AND** structural validator scope (e.g. `gz validate --documents`) admitting the artifact's shape |
| **STRUCTURAL-FENCE** | Integration-state properties scoped to the parent ADR's boundary — cross-OBPI invariants that audit at ADR closeout, not per-OBPI | Parent-ADR `## Boundary Invariants` entry, audited at ADR closeout layer |

### Brief-authoring tag syntax

```
REQ-X.Y.Z-NN-01 [behavior]: the system does X when Y
REQ-X.Y.Z-NN-02 [support]: the rule file carries subsection Z
REQ-X.Y.Z-NN-03 [structural-fence]: cross-OBPI boundary invariant P holds
```

### Proof-channel matrix

| Kind | Test `@covers`? | Ledger event? | Structural validator? | Parent-ADR invariant? |
|------|:--------------:|:------------:|:--------------------:|:--------------------:|
| BEHAVIOR | **required** | — | — | — |
| SUPPORT | — | **required** | **required** | — |
| STRUCTURAL-FENCE | — | — | — | **required** |

### What this replaces

Before ADR-0.0.59: every REQ used the BEHAVIOR proof channel uniformly, producing
tautological filesystem-grep tests for content REQs (32% project-wide / 42% governance).
SUPPORT-kind REQs are now witnessed by the ledger + structural validator; no `@covers`
test is required or appropriate for them — authoring one is the anti-pattern this rule
names.

> See [`docs/governance/req-scope-discipline.md`](../../docs/governance/req-scope-discipline.md)
> for canonical expansion: problem framing, proof-channel detail, GHI #270 reconciliation,
> quantification, and consequences.
```

### Step 2 — Create `docs/governance/req-scope-discipline.md`

New file mirroring `agents-md-doctrine.md` shape. Sections:

1. **Header block** — Source ADR, rule file, authoring date
2. **The failure pattern** — operator's "staggering find" framing + quantification (32%/42%)
3. **The invariant** — three-kind taxonomy as binding MUST/MUST NOT
4. **Three-kind proof-channel detail** — per-kind examples and anti-patterns
5. **GHI #270 reconciliation** — output-form fixture tests are BEHAVIOR proofs
6. **Lift targets matrix** — what moves from @covers to ledger+validator
7. **Consequences** — positive (from ADR § Consequences positive 1-3) + negative (negative 1-2)
8. **Related artifacts** — ADR-0.0.59, .gzkit/rules/tests.md, GHI #517 connection

### Step 3 — Edit `docs/governance/advisory-rules-audit.md`

**a) Append row 59** to the scorecard table (after current last row 58):
```
| 59 | REQ Scope Discipline | **Mechanical** | `gz validate --req-kind-discipline` (OBPI-0.0.59-02 scope) fail-closes brief-time on missing [kind] tags and per-kind proof-citation gaps. Mechanical for shape: the three-kind taxonomy (BEHAVIOR/SUPPORT/STRUCTURAL-FENCE) is a closed StrEnum; brief-authoring scaffold prompts for kind; parity gate consumes per-kind proof channels. Added by OBPI-0.0.59-01 (2026-05-26). ADR-0.0.59. |
```

**b) Update Summary table** Mechanical count: 42→43 (percentage recalculates to ~64%)

**c) Update narrative paragraph** — add sentence naming ADR-0.0.59 as the addition source.

### Step 4 — Append `## Disposition` to pool ADR

After line 139 (end of Promotion guidance section), append:

```markdown

## Disposition

**Superseded** by `ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine` (2026-05-26).

This pool ADR's prior-art analysis is preserved by inclusion in the parent ADR's
§ Alternatives Considered with full credit:

- **Path A** (schema-level REQ kind marker) → subsummed into ADR-0.0.59's `[kind]` inline tag syntax
- **Path B** (doctrine-only guidance) → rejected standalone; doctrine without mechanism violates operative claim 3
- **Path C** (phased A+B) → moot once the categorical fix ships as one cycle
- **Path D** (promote scope-fence REQs to parent-ADR invariants) → **adopted** as the STRUCTURAL-FENCE proof channel

The pool ADR retires having served its design-conversation purpose.
```

### Step 5 — GHI #165 retroactive comment

```bash
gh issue comment 165 --body "Superseded by ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine (2026-05-26).

The ledger_event + parent_adr_invariant proof channels this issue requested are now named in the canonical three-kind REQ taxonomy shipped by ADR-0.0.59:
- SUPPORT-kind REQs: witnessed by ledger artifact_edited event + structural validator scope
- STRUCTURAL-FENCE-kind REQs: witnessed by parent-ADR § Boundary Invariants entry at closeout

The @covers-as-sole-channel limitation is the categorical error ADR-0.0.59 names and fixes. GHI was already closed; this comment records the destination per ghi-close doctrine (a registered destination: ADR-0.0.59 visible in gz adr report)."
```

### Step 6 — Close GHI #531

```bash
gh issue close 531 --comment "Superseded by ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine (2026-05-26).

The categorical category error this GHI names (REQ→@covers parity machinery mass-producing tautological filesystem-grep tests for content REQs) is addressed by the three-kind REQ taxonomy (BEHAVIOR/SUPPORT/STRUCTURAL-FENCE) in ADR-0.0.59. The 32%/42% quantification from this GHI is preserved in the ADR's intent section and doctrine doc. Decommissioning chore (OBPI-0.0.59-04/05) handles the existing rot. Registered destination: ADR-0.0.59 visible in gz adr report."
```

## Verification

Run in order after all edits:

```bash
# REQ-01/04: tests.md updated + GHI #270 note
grep -q "## REQ Scope Discipline" .gzkit/rules/tests.md
grep -q "rule-version: 0.5.0" .gzkit/rules/tests.md
grep -q "GHI #270" .gzkit/rules/tests.md

# REQ-02: doctrine doc exists
test -f docs/governance/req-scope-discipline.md

# REQ-03: scorecard entry present
grep -q "REQ Scope Discipline" docs/governance/advisory-rules-audit.md

# REQ-05: pool ADR disposition
grep -q "Disposition" docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md
grep -q "ADR-0.0.59" docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md

# REQ-08: no PII
git diff --staged | grep -v "^---\|^+++" | grep -v "noreply" | grep -i "ahuimanu@\|gmail\|personal" || echo "no PII found"

# Structural validators (Gate 2 + Gate 3)
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest -q

# REQ-06/07: GHI states
gh issue view 165 --json state | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['state'])"
gh issue view 531 --json state | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['state'])"
```

## Notes

- `docs/governance/req-scope-discipline.md` is a CREATE path — the CLI plan audit's
  "path does not exist" gap is expected (false positive). The path is new.
- All 8 REQs are [support] kind — per the doctrine being shipped, NONE require
  @covers-decorated tests. Gate 2 is structural-validator clean run only.
- GHI #165 is already CLOSED — add retroactive comment only, do not close again.
- Scope is strictly within Allowed Paths; no src/, no tests/, no schemas/.
