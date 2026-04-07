# AUDIT (Gate-5) — ADR-0.0.14

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.14 |
| ADR Title | Deterministic OBPI Commands |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands |
| Audit Date | 2026-04-06 |
| Auditor(s) | agent:claude-opus-4-6 |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?**

- Deterministic `gz obpi lock` CLI commands (claim/release/check/list) as the sole lock write path
- Atomic `gz obpi complete` transaction — validates, writes evidence, flips status, records attestation, emits receipt in one all-or-nothing operation
- TTL-based lock expiration with automatic stale-lock reaping
- Skill migration: `gz-obpi-pipeline` and `gz-obpi-lock` skills delegate entirely to CLI commands (zero direct Write tool calls to governance paths)

### Capability 1: Lock claim/check/release lifecycle

```bash
$ uv run gz obpi lock claim OBPI-0.0.14-01 --agent audit-agent --ttl 300
Claimed: OBPI-0.0.14-01 (agent=audit-agent, ttl=300m)

$ uv run gz obpi lock check OBPI-0.0.14-01
HELD: OBPI-0.0.14-01  agent=audit-agent  elapsed=0m  remaining=300m

$ uv run gz obpi lock release OBPI-0.0.14-01 --agent audit-agent
Released: OBPI-0.0.14-01
```

**Why it matters:** Multi-agent coordination requires deterministic, CLI-driven lock semantics. Before this ADR, skills wrote lock files directly — now all lock mutations go through a single command with ownership validation, TTL enforcement, and ledger accounting.

### Capability 2: Lock listing with stale-reaping

```bash
$ uv run gz obpi lock list
  OBPI-0.0.14-01  ACTIVE  agent=audit-agent  elapsed=0m  ttl=300m
```

**Why it matters:** Operators can audit active locks at a glance. Expired locks are automatically reaped before listing, preventing stale coordination state.

### Capability 3: Atomic OBPI completion

```bash
$ uv run gz obpi complete -h
usage: gz obpi complete [-h] --attestor ATTESTOR
                        --attestation-text ATTESTATION_TEXT
                        [--implementation-summary IMPLEMENTATION_SUMMARY]
                        [--key-proof KEY_PROOF] [--json] [--dry-run]
                        [--quiet | --verbose] [--debug]
                        obpi

All-or-nothing OBPI completion: validates the brief, writes evidence sections,
flips status to Completed, records attestation in the audit ledger, and emits
a completion receipt. If any step fails, no files or ledger entries are modified.
```

**Why it matters:** Before this ADR, OBPI completion involved 5+ separate file writes from skill prose — any failure mid-sequence left partial artifacts. Now a single atomic command handles the entire transaction with rollback on failure.

### Capability 4: Skill migration — zero direct writes

```bash
$ grep -ciE 'Write.*locks|Write.*obpi-audit|Write.*attestation' \
    .claude/skills/gz-obpi-lock/SKILL.md \
    .claude/skills/gz-obpi-pipeline/SKILL.md \
    .claude/skills/gz-obpi-pipeline/DISPATCH.md
.claude/skills/gz-obpi-lock/SKILL.md:0
.claude/skills/gz-obpi-pipeline/SKILL.md:2  # Documentation prose only, not tool instructions
.claude/skills/gz-obpi-pipeline/DISPATCH.md:0
```

The 2 matches in SKILL.md are documentation prose describing what `gz obpi complete` does internally ("atomically writes the attestation"), not Write tool instructions to agents.

**Why it matters:** Skills no longer perform direct file mutations against governance artifacts. All state transitions route through deterministic CLI commands, making the pipeline auditable and reproducible.

### Value Summary

Operators and agents now have a deterministic, atomic command surface for the two most critical OBPI lifecycle operations (locking and completion). Direct file writes from skill prose are eliminated. Lock coordination is TTL-enforced with automatic stale-reaping. Completion transactions are all-or-nothing with rollback, eliminating the class of partial-write bugs that plagued the previous skill-driven approach.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.14` | ✓ | PASS — all 3 OBPIs completed with evidence |
| Lock claim/release cycle | `gz obpi lock claim/check/release` | ✓ | Full lifecycle demonstrated (see Feature Demonstration) |
| Lock list with stale-reaping | `gz obpi lock list` | ✓ | Lists active locks, reaps expired |
| Complete command interface | `gz obpi complete -h` | ✓ | Full help with examples, exit codes |
| Skill migration — no direct writes | `grep` for Write tool in skills | ✓ | 0 Write tool instructions (2 matches are documentation prose) |
| Unit tests | `uv run -m unittest -q` | ✓ | 2616 tests pass in 19.4s — `proofs/unittest.txt` |
| Docs build | `uv run mkdocs build -q` | ✓ | Build clean — `proofs/mkdocs.txt` |
| Gates 1-4 | `uv run gz gates --adr ADR-0.0.14` | ✓ | All pass — `proofs/gates.txt` |

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 3 OBPIs delivered: lock commands, complete command, skill migration |
| Data Integrity | ✓ Atomic transactions with rollback; ledger events emitted |
| Performance Stability | ✓ 2616 tests in 19.4s; 107 BDD scenarios in 2.2s |
| Documentation Alignment | ✓ 5 command docs delivered; runbook updated; mkdocs builds clean |
| Risk Items Resolved | ✓ No blocking issues found |

## Evidence Index

- `audit/proofs/unittest.txt` — Unit test output (2616 tests)
- `audit/proofs/mkdocs.txt` — Docs build output
- `audit/proofs/gates.txt` — Full gate verification output (Gates 1-4)
- `audit/AUDIT_PLAN.md` — Audit plan with scope and checks

## Recommendations

- **Resolved: REQ-level @covers coverage raised from 0/29 to 27/29 (93.1%).** Added REQ-level decorators to all existing unit tests in `test_obpi_lock_cmd.py`, `test_obpi_complete_cmd.py`, and `test_lock_manager.py`. Created `test_obpi_skill_migration.py` with 16 static verification tests for OBPI-03 skill migration REQs.
- **Advisory: 2 REQs remain uncovered (REQ-0.0.14-03-11, REQ-0.0.14-03-12).** These are integration-level requirements (pipeline dry-run tool-use log inspection and ledger event parity) that require end-to-end pipeline execution, not unit tests.
- No blocking issues found.

## Attestation

I attest that ADR-0.0.14 (Deterministic OBPI Commands) is implemented as intended, evidence is reproducible, and no blocking discrepancies remain. All 3 OBPIs are delivered, all gates pass, and the skill migration eliminates direct file writes from governance skill prose.

Signed: agent:claude-opus-4-6, 2026-04-06
