# AUDIT — ADR-0.28.0-focused-context-loader

**Lane:** Lite · **Lifecycle (entry):** Completed · **Target:** Completed → Validated
**Auditor persona:** pipeline-orchestrator · **Date:** 2026-06-01
**Ledger proof:** `gz adr audit-check ADR-0.28.0` → PASS, 13/13 REQs covered (live recompute).
Ledger `obpi-audit.jsonl` markers dated 2026-05-24 (8 days → exceeds 7-day staleness
threshold); fresh verification + value demonstration run per skill Step 2.

---

## Feature Demonstration (Step 3 — MANDATORY)

The ADR delivers `gz context <ADR-ID>`: a single Markdown payload bundling the target
ADR body, every OBPI brief, covering-test paths (via `@covers`), and a governance-rules
section — for verbatim piping into an agent harness. `--slim` omits governance.

| Capability | Command | Observed output | Value |
|---|---|---|---|
| Focused payload | `gz context ADR-0.28.0` | 38,577-byte Markdown doc; ADR body + 2 OBPI briefs + covering tests + governance section | One-shot ADR context, replaces "reload the encyclopedia every turn" |
| Harness-safe rendering | `… \| grep -c $'\x1b'` | `0` ANSI sequences | Pipeable verbatim (REQ-01-08 core) |
| Slim variant | `gz context --slim ADR-0.28.0` | 839 lines vs. 848 default; governance section omitted | Non-governance harness mode (REQ-02-02/03) |
| Fail-closed lookup | `gz context ADR-9.9.9-bogus` | `BLOCKERS: gz context: error: ADR not found: ADR-9.9.9-bogus`, exit 1 | Names the missing ADR; clean non-zero (REQ-01-07) |

**Verdict:** The capability is real, integrated, and demonstrably working. The two OBPIs
cohere at a clean subtractive renderer seam (`build_context_payload(..., *, slim)`,
single `if not slim:` branch at `context_cmd.py:137`) — no duplicated renderer path.

---

## Execution Log

| Check | Result | Evidence |
|---|---|---|
| `gz adr audit-check ADR-0.28.0` | ✓ PASS (13/13) | live recompute 2026-06-01 |
| Value demonstration (4 capabilities) | ✓ all observed | table above |
| `gz context --help` surface | ✓ documents `<ADR-ID>` + `--slim` | help output |
| Verb shape / Lite-lane boundary | ✓ top-level verb, no schema/ledger write | `cli/parser_artifacts.py:103-143` |

---

## Shortfalls (Step 5)

Independent persona dispatch: `spec-reviewer` (REQ-tracing) + `quality-reviewer`
(structural coherence). Both converged on REQ-01-06. All findings verified by the
driver against primary sources (`context_cmd.py`, `test_context_cmd.py`, OBPI-01 brief).

### Blocker

| ID | Severity | REQ | Finding |
|---|---|---|---|
| **F1** | **Blocker** | REQ-0.28.0-01-06 | **Fork-independent test-semantics gap.** The covering test (`test_context_cmd.py:146-158`) asserts *only* string-presence of "lane"/"lifecycle"/"governance rules". It asserts **nothing** about the current-gate *value* or its *source* — so it is structurally blind regardless of which surface is right (Invariant 6f). Separately, an impl/REQ tension exists: REQ-01-06 names *ledger state (current gate)* as the input, while `_render_governance_rules` (`context_cmd.py:97`) derives the gate from frontmatter `status:` only (no ledger read; cf. Never-rule #7). The gate is currently **correct by coincidence** (Completed→Gate 5 matches the ledger today), so no operator is shown wrong data now — but that latent state is exactly what Never-rule #7 names. **Which surface is wrong is the operator's call** (see fork below); the test must be re-derived under *either* fork, which is why this blocks. |

### Test-quality cleanup (non-blocking)

| ID | REQ | Finding |
|---|---|---|
| F2 | REQ-0.28.0-01-08 | **CORRECTED on remediation.** Initially read (by spec-reviewer and driver) as `assertNotIn("[", result.output)` — a bracket bug. A byte dump (`od -c`) showed the line actually embeds a **raw ESC control byte** (`\033[`), invisibly rendered by the file reader. It is *not* a bracket check; it is a **redundant** ANSI-CSI assertion duplicating the readable `\x1b[` check on the prior line. No bracket bug exists; the real (tiny) issue is a duplicate assertion carrying a raw control char in source. Collapsed to one readable `\x1b` check. |
| F3 | REQ-0.28.0-01-05 | "grouped by REQ" clause untested — single-REQ fixture cannot exercise the `### {req_id}` grouping (`context_cmd.py:76`). |
| F4 | REQ-0.28.0-01-07 | Test asserts exit≠0 + "BLOCKERS" but not the "naming the missing ADR path" clause (impl *does* name it — value demo confirms — test does not pin it). |
| F5 | REQ-0.28.0-02-04 | "delta IS governance" weakened to line-membership; brief Evidence overclaims "mechanically verified". |
| F6 | Decision item 3 | Naming-convention fallback tier unimplemented (`scan_test_tree` is `@covers`-only). Unexercised-by-design; amend Decision text or implement. |

---

## Audit Outcome

**Value demonstration: PASS.** The feature works and is shown working.
**Evidence verification: ONE BLOCKER (F1) — NOT cleared to VALIDATED.**

Per skill Step 6 + "Audit fails → no receipt," the `validated` receipt is **withheld**.
The ceremony requires operator attestation before emit regardless, so withholding is not
an over-reach. F1 routes to the operator for a fork decision before any GHI is authored
(the fork determines what the GHI says):

- **Fork (a) — impl is wrong:** wire ledger-derived gate state + re-derive the REQ-01-06
  test to assert the gate *value* and *source*. Treats the frontmatter read as a
  Never-rule #7 defect.
- **Fork (b) — REQ over-specified:** amend REQ-01-06 to drop the "ledger state" clause
  (a frontmatter-derived advisory gate is acceptable for a Lite-lane *informational*
  context payload, not a Gate-5 decision surface) + fix the test to assert the actual
  frontmatter-derived value.

F2–F5 are test-quality cleanup that can ride the same remediation OBPI. Code-touching →
fresh OBPI per skill ("never spawn an implementer inside the audit").

### Operator ruling (2026-06-01)

**Fork (a) selected — impl is wrong.** Operator (g0) ruled the frontmatter-
derived gate a Never-rule #7 defect. Remediation scope:
1. Wire ledger-derived current-gate state into `_render_governance_rules`
   (`context_cmd.py:82-108`) — replace the frontmatter `status:` heuristic at line 97.
2. Re-derive the REQ-01-06 test (`test_context_cmd.py:146-158`) to assert the gate
   *value* and its *ledger source*, not string-presence.
3. Ride-along test cleanup: F2 (drop `assertNotIn("[")` line 180), F3, F4, F5.

Filed as **GHI #576** (`defect`, `runtime`).

---

## Remediation Applied (direct fix — 2026-06-01)

After the operator noted that OBPIs descend from ADRs (not GHIs) and asked whether a
direct fix applied, the routing was re-computed against AGENTS.md § Defect-fix routing:
precedent 308 `fix(` commits/60d (≥3 ✓), single module + its test (≤2 files ✓), in-flight
defect ✓, unit-test coverage no new BDD ✓, no CLI/schema/exit-code/contract change → **all
direct-fix criteria hold, no OBPI-required trigger fires.** Routed as a TDD direct fix.

**F1 (the blocker) — fixed.** New `_ledger_current_gate` (`context_cmd.py`) derives the
current gate from `Ledger.get_effective_gate_statuses(adr_id)` (Layer-2 truth) as the
highest gate cleared — lane/lifecycle still from frontmatter per REQ wording. REQ-01-06
test re-derived to pin the gate **value and ledger source**: fixture forces frontmatter
(`status: Completed` → old heuristic Gate 5) to disagree with ledger (gate 2 cleared) and
asserts the payload shows "Gate 2", not "Gate 5". RED confirmed (old impl rendered Gate 5),
GREEN after fix. Live: `gz context ADR-0.28.0` → `Current gate: Gate 2 (latest cleared per
ledger)`.

**Cleanup F2–F5 — done (F2 corrected, see table).** F3 grouping now exercised with two
REQs; F4 asserts the missing ADR is named; F5 strengthened to a byte-prefix proof that the
slim↔default delta *is* the governance section.

**Verification:** 13/13 `test_context_cmd` GREEN; 85 command tests no regression; ruff +
ty clean on touched files; `gz adr audit-check` 13/13 coverage intact.

ADR-0.28.0 remains **Completed** this ceremony — no `validated` receipt emitted (re-audit
to Validated is a separate operator-attested ceremony). GHI #576 closes `fixed` citing the
remediation commit.

_Attestation withheld — see Audit Outcome. No `validated` receipt emitted._
