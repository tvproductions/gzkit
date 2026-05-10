# AUDIT (Gate-5) — ADR-0.0.30 Complexity Authoring Guidance

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.30-complexity-authoring-guidance |
| ADR Title | Complexity Authoring Guidance |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ |
| Audit Date | 2026-05-10 |
| Auditor(s) | Agent (gz-adr-audit skill, opus-tier) under operator g0 |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?** The fourth and closing foundation in the
complexity-doctrine cluster — the upstream-prevention complement to
ADR-0.0.29's trigger-time advisor. Hints surface to the developer at
authoring time (before the metric crosses any band), so refactor decisions
land at design time rather than at gate time. The advise band of
ADR-0.0.28's threshold table finally has a consumer surface. Six concrete
capabilities ship; each is demonstrated below with live `gz` command
output.

### Capability 1: `gz complexity guide` CLI verb — help surface

```bash
$ uv run gz complexity guide --help
```

The verb is registered with the four-code exit map per `.claude/rules/cli.md`:
0 success, 1 user/config error, 2 system/IO error, exit 3 NEVER produced (the
authoring-guide surface never blocks; that is OBPI-0.0.29's trigger-time
advisor's responsibility). Help text documents this explicitly. Full output
captured at `audit/proofs/demo-01-cli-help.txt` (exit 0).

**Why it matters:** The verb's help surface is the operator's first
discovery point. Operators reaching for "preview complexity hints before
commit" land on a discoverable, well-documented entry point. The help
text's explicit "Exit 3 is NOT used" callout teaches the operator that
this surface is non-blocking by design — it is a conversation, not a gate.

### Capability 2: `gz complexity guide` CLI verb — prose form on real source

```bash
$ uv run gz complexity guide src/gzkit/commands/validate_cmd.py
── src/gzkit/commands/validate_cmd.py:82-82 ──
Archetype : long_parameter_list
Band      : approaching
Guidance  : cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
Move      : When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
... (7 hint blocks total) ...
```

Full 42-line output captured at `audit/proofs/demo-02-cli-prose.txt` (exit
0). Seven advise-band hint blocks were emitted against `validate_cmd.py`,
each with canonical fields: file:line range header, archetype, precedence
band, doctrinal-frame guidance headline, and recommended-move headline.

**Why it matters:** The operator sees the engine's verdict in human-readable
prose, in the operator's terminal, against real code. The "Archetype / Band /
Guidance / Move" structure is the cluster's distilled-characteristics
doctrine landing at the operator's editing moment — what kind of complexity
this is, how close to a real warning it is, what the cluster's doctrine says
about it, and what to do about it. This is the upstream-prevention surface
that ADR-0.0.28's advise band finally has a consumer for.

### Capability 3: `gz complexity guide --json` — canonical AuthoringHint serialization

```bash
$ uv run gz complexity guide src/gzkit/commands/validate_cmd.py --json
```

Emits a 7-element JSON array; each record carries the canonical
`AuthoringHint` fields: `archetype`, `crossing_value`, `doctrinal_frame_headline`,
`end_line`, `file_path`, `metric`, `precedence_band`, `recommended_move`,
`start_line`. Validates against `src/gzkit/schemas/authoring_hint.json`. Full
79-line output captured at `audit/proofs/demo-03-cli-json.txt`.

**Why it matters:** Editor authors, CI scripts, and downstream tools have a
machine-readable surface. The JSON shape is the canonical Pydantic
serialization (frozen + extra="forbid"), guaranteed stable by OBPI-03's
schema mirror. This is the contract that the editor protocol (Capability 5)
emits over stdio, and the same contract that the justify integration
(Capability 6) consumes in-process.

### Capability 4: Skill discovery + vendor-mirror parity

```bash
$ ls .gzkit/skills/complexity-guide/SKILL.md \
     .claude/skills/complexity-guide/SKILL.md \
     .agents/skills/complexity-guide/SKILL.md \
     .github/skills/complexity-guide/SKILL.md
$ diff -q .gzkit/skills/complexity-guide/SKILL.md .claude/skills/complexity-guide/SKILL.md
$ diff -q .gzkit/skills/complexity-guide/SKILL.md .agents/skills/complexity-guide/SKILL.md
$ diff -q .gzkit/skills/complexity-guide/SKILL.md .github/skills/complexity-guide/SKILL.md
```

All four mirror locations contain the canonical `SKILL.md`; the three
`diff -q` invocations produce no output (byte-identical). Captured at
`audit/proofs/demo-04-skill-mirrors.txt`.

**Why it matters:** Operators using Claude Code, the `.agents/` channel, or
GitHub-flavored agent surfaces all see the same skill body. The skill's
trigger phrases ("authoring-time complexity hint", "complexity guide
preview", "preview before commit", "advise-band hints") route the operator
to the CLI verb regardless of which agent surface they invoke from. Vendor
mirror parity is the mechanical guarantee that no surface drifts away from
the canonical contract.

### Capability 5: Editor/IDE protocol contract — live handshake

```bash
$ printf 'Content-Length: 80\r\n\r\n{"jsonrpc":"2.0","id":1,"method":"initialize",...}' \
     'Content-Length: 56\r\n\r\n{"jsonrpc":"2.0","id":2,"method":"shutdown",...}' \
  | uv run gz complexity guide --server
Content-Length: 94

{"id": 1, "result": {"version": "1.0", "capabilities": ["initialize", "analyze", "shutdown"]}}Content-Length: 55

{"id": 2, "result": {"status": "ok", "shutdown": true}}
```

Captured at `audit/proofs/demo-05-protocol-handshake.txt` (exit 0). The
server speaks the documented LSP-style envelope: Content-Length-framed
JSON, three methods (`initialize`, `analyze`, `shutdown`), version handshake
returning `1.0` plus the capability list. Specification document at
`docs/governance/complexity/authoring-guide-protocol.md`; envelope JSON
Schema at `src/gzkit/schemas/authoring_guide_protocol.json`.

**Why it matters:** Editor authors (VS Code, Neovim, JetBrains, future
agent-driven editors) have a stable, well-documented stdio contract to
bind against. JSON-over-stdio matches the existing CLI invocation pattern
and avoids introducing a network surface (which would expand the
security-scope this cluster does not address). LSP-style envelope is the
well-known precedent editors already implement; reusing it reduces
editor-author friction. No editor implementations land in this ADR — the
contract is what editor authors consume.

### Capability 6: `gz justify` integration — pre-execution reasoning walkthrough

```bash
$ uv run gz justify OBPI-0.0.30-05
... (8-section walkthrough renders) ...
### Authoring-time complexity hints

- **/Users/jeff/Documents/Code/gzkit/src/gzkit/justify/cli.py:183-183** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. ...
```

Full walkthrough captured at `audit/proofs/demo-06-justify-integration.txt`
(exit 0; section header `### Authoring-time complexity hints` confirmed
present). The integration is additive — the existing `gz justify` 8-section
reasoning structure is preserved verbatim; the complexity-hints sub-heading
appears only when the OBPI's allowed-paths include `.py` files with
advise-band crossings (silent-skip behavior verified at OBPI-05 BDD level).

**Why it matters:** ADR-0.0.19's pre-execution reasoning walkthrough is the
canonical home for authoring-time complexity reasoning. Without this
integration, `gz justify` and the authoring-guidance surface would be two
unconnected reasoning surfaces that the operator would have to stitch
together by hand. The integration closes the cluster's loop with the
reasoning-walkthrough doctrine — the operator's complexity-decision moment
is now bound from corpus measurement (ADR-0.0.27) through threshold
calibration (ADR-0.0.28) through trigger-time response (ADR-0.0.29) through
authoring-time hints inside pre-execution reasoning (ADR-0.0.30 + 0.0.19).

### Value Summary

Before this ADR, the operator who wanted to preview complexity hints during
authoring had no canonical surface — the advise band of ADR-0.0.28's
threshold table existed but did nothing. After this ADR, the operator has
three concrete pathways: ad-hoc CLI (`gz complexity guide <path>`), an
editor/IDE stdio protocol that any editor author can consume, and an
in-process integration with `gz justify` so authoring-time hints surface
inside the OBPI pre-execution reasoning walkthrough automatically. The
cluster's four-foundation loop (corpus → thresholds → trigger-time advisor
→ upstream-prevention authoring guidance) is now closed; the developer's
complexity-decision moment is bound at every layer of the cluster.

---

## Execution Log

| # | Check | Command / Method | Result | Notes |
|---|-------|------------------|--------|-------|
| C1 | Ledger proof complete | `uv run gz adr audit-check ADR-0.0.30` | ✓ | PASS; 5/5 OBPIs completed; 33/33 REQs covered. Proof: `audit/proofs/audit-check.txt`. |
| C2 | Demo: CLI help | `uv run gz complexity guide --help` | ✓ | exit 0; help documents flags + four-code exit map. Proof: `audit/proofs/demo-01-cli-help.txt`. |
| C3 | Demo: CLI prose form | `uv run gz complexity guide src/gzkit/commands/validate_cmd.py` | ✓ | exit 0; 7 advise-band hint blocks emitted with canonical fields. Proof: `audit/proofs/demo-02-cli-prose.txt`. |
| C4 | Demo: CLI `--json` | `uv run gz complexity guide src/gzkit/commands/validate_cmd.py --json` | ✓ | exit 0; valid JSON array, 7 records, all canonical AuthoringHint fields present. Proof: `audit/proofs/demo-03-cli-json.txt`. |
| C5 | Demo: Skill vendor-mirror parity | `ls` + `diff -q` across 4 surfaces | ✓ | All four mirror copies present; three `diff -q` invocations empty (byte-identical). Proof: `audit/proofs/demo-04-skill-mirrors.txt`. |
| C6 | Demo: Editor protocol handshake | `gz complexity guide --server` driven with Content-Length framing | ✓ | exit 0; initialize → `{"version":"1.0","capabilities":["initialize","analyze","shutdown"]}`; shutdown → `{"status":"ok","shutdown":true}`. Proof: `audit/proofs/demo-05-protocol-handshake.txt`. |
| C7 | Demo: `gz justify` integration | `uv run gz justify OBPI-0.0.30-05` | ✓ | exit 0; output contains `### Authoring-time complexity hints` section with at least one hint block for the OBPI's `.py` allowed-paths. Proof: `audit/proofs/demo-06-justify-integration.txt`. |
| C8 | Spec + schema artifacts present | `ls` of spec doc + 2 schemas + manpage | ✓ | All four files present at canonical paths. Proof: `audit/proofs/demo-07-artifacts-present.txt`. |

## Dataset Spot Examples

```text
# Capability 2 — CLI prose form on real source (head):
── src/gzkit/commands/validate_cmd.py:82-82 ──
Archetype : long_parameter_list
Band      : approaching
Guidance  : cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
Move      : When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. ...

# Capability 5 — Editor protocol initialize response:
{"id": 1, "result": {"version": "1.0", "capabilities": ["initialize", "analyze", "shutdown"]}}

# Capability 6 — Justify integration injected section:
### Authoring-time complexity hints

- **/Users/jeff/Documents/Code/gzkit/src/gzkit/justify/cli.py:183-183** — long_parameter_list (approaching)
  Guidance: ...
```

## Summary Table

| Aspect | Status | Notes |
|--------|--------|-------|
| Implementation Completeness | ✓ | All five OBPIs `attested_completed`; six product capabilities live and exercised. |
| Data Integrity | ✓ | 33/33 REQs covered (100%) per `gz adr audit-check`; ledger proof complete and fresh (<2 days). |
| Performance Stability | ✓ | OBPI-04 BDD scenarios + protocol handshake demo run sub-second; CLI guide on validate_cmd.py emits 7 hints with no observed delay. |
| Documentation Alignment | ✓ | Manpage at `docs/user/manpages/complexity-guide.md`, runbook entry under "Complexity doctrine surfaces", protocol spec at `docs/governance/complexity/authoring-guide-protocol.md`, all referenced from ADR-0.0.30 § Decision § Mechanical surfaces. |
| Risk Items Resolved | ✓ | All five risks from AUDIT_PLAN § Risk Focus mitigated by demo evidence; no shortfalls surfaced. |

## Evidence Index

All proof files committed under
`docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/audit/proofs/`:

- `audit-check.txt` — `gz adr audit-check ADR-0.0.30` (PASS, 33/33 REQs)
- `demo-01-cli-help.txt` — `gz complexity guide --help` (Capability 1)
- `demo-02-cli-prose.txt` — `gz complexity guide validate_cmd.py` (Capability 2; 7 hints)
- `demo-03-cli-json.txt` — `gz complexity guide validate_cmd.py --json` (Capability 3; canonical schema)
- `demo-04-skill-mirrors.txt` — vendor-mirror parity check (Capability 4)
- `demo-05-protocol-handshake.txt` — Content-Length-framed initialize + shutdown (Capability 5)
- `demo-06-justify-integration.txt` — `gz justify OBPI-0.0.30-05` with hints section (Capability 6)
- `demo-07-artifacts-present.txt` — spec doc + schemas + manpage existence

## Recommendations

- **No blocking issues found.** All eight planned checks pass; all six
  product capabilities demonstrated working with live command output and
  canonical schema; ledger proof complete and fresh.
- **Note on cluster forward-references (informational, not blocking).** The
  ADR's Negative #4 calls out that future amendments to `AdvisorDiagnosis`
  (ADR-0.0.29) would require re-deriving the `AuthoringHint` projection.
  The doctrine-amendment-protocol pool stub is the canonical home for that
  work — no action required here.
- **Note on advise-band calibration (informational).** ADR § Negative #8
  acknowledges the initial advise-band thresholds are conservative
  cold-start values; the next distillation pass per the cluster cadence
  will tighten them. Not a shortfall — explicitly anticipated by the ADR.

## Attestation

**Phase 1 (Layer 1 verification):** Skipped per Layer 2 trust model — ledger
proof from `gz adr audit-check ADR-0.0.30` shows all five OBPIs in the
`Completed` state with full REQ coverage; ledger entries are <2 days old
(briefs completed 2026-05-09 and 2026-05-10) and well within the 7-day
freshness threshold. The receipts named in each brief's evidence section
(arb-step-unittest-d98f3e4f724e4ba6b3846a3c7e3acfb0 across 4648 tests, plus
the OBPI-scoped receipts in the brief evidence sections) constitute the
Layer 1 proof.

**Phase 2 (agent's signature on audit completion):** I, the audit agent,
attest that ADR-0.0.30 is implemented as intended, all six product
capabilities demonstrate working with live command output, evidence is
reproducible, and no blocking discrepancies remain. Proof artifacts are
committed under `audit/proofs/` and referenced in the Evidence Index above.

**Phase 3 (operator's verbal attestation — pending):** The operator's
verbal `accept audit` / `verify audit` is required before the validated
receipt is emitted to the ledger. Audit-begin marker has been written via
`gz adr audit-begin ADR-0.0.30`; the agent waits for the operator's verbal
ack to compose the relayed `gz adr emit-receipt ... --event validated`
command, then audit-end + `gz adr report ADR-0.0.30` to confirm the
`Lifecycle: Validated` transition.

Signed: _Agent (gz-adr-audit skill, opus-tier) — 2026-05-10. Operator
verbal attestation pending._
