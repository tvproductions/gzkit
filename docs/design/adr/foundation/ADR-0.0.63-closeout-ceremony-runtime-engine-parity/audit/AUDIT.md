# AUDIT — ADR-0.0.63-closeout-ceremony-runtime-engine-parity

**Lane:** heavy · **Kind:** foundation · **Audit date:** 2026-05-30
**Driver persona:** pipeline-orchestrator
**Independent reviewers dispatched:** spec-reviewer (REQ tracing), quality-reviewer (integration coherence), narrator (value demonstration)

---

## Verdict (pending operator audit-acceptance)

- **Ledger proof:** `gz adr audit-check ADR-0.0.63` → **PASS**. 7/7 OBPIs `attested_completed`; 21/29 REQs `@covers`-covered (72.4%); 8 advisory-uncovered REQs, **0 blocking**; `covers_backfill_unresolvable: []`.
- **Independent spec re-derivation (spec-reviewer):** PASS. All 8 advisory-uncovered REQs are legitimately non-BEHAVIOR (3 STRUCTURAL-FENCE + 5 SUPPORT) with their declared proof channels present on disk; 5 BEHAVIOR spot-checks all semantic (Invariant 6f satisfied); REQ arithmetic closes to 29.
- **Independent integration review (quality-reviewer):** CONCERNS — two latent DRY/SOLID seams + one cosmetic comment-drift. **None are proof-channel failures; none corrupt the ledger today.** See § Shortfalls.

The COMPLETED → VALIDATED transition is **held pending operator decision** on the
disposition of the BI-1 seam (block vs. track-and-proceed). The audit attestation
below is unsigned until that decision lands.

---

## 1. Audit Plan & Ledger Completeness

Layer-2 trust model: this audit consumes ledger proof rather than re-running Layer-1 verification.

| Check | Command | Result | Proof |
|---|---|---|---|
| Ledger completeness | `gz adr audit-check ADR-0.0.63` | ✓ PASS (7/7 OBPIs) | `proofs/` (verdict captured below) |
| Coverage shape | `gz adr audit-check --json` | ✓ 0 blocking, 8 advisory | inline |
| Proof-binding validator | `gz validate --closeout-proof-binding` | ✓ exit 0 | `proofs/closeout-proof-binding.txt` |
| Brief/verify shape gate | `gz validate --documents` | ✓ exit 0 | `proofs/verify-command-shape.txt` |
| Closeout CLI surface | `gz closeout --help` | ✓ state-machine surface | `proofs/closeout-help.txt` |

### Advisory-uncovered REQs (all legitimately non-BEHAVIOR — independently confirmed)

| REQ | Kind | Proof channel | Verified present |
|---|---|---|---|
| REQ-0.0.63-01-04 | STRUCTURAL-FENCE | ADR BI-3 (body L135-138) | ✓ |
| REQ-0.0.63-02-05 | STRUCTURAL-FENCE | ADR BI-1 (body L123-129) | ✓ (classifier shared — see seam below) |
| REQ-0.0.63-05-04 | STRUCTURAL-FENCE | ADR BI-2 (body L130-134) | ✓ (single emitter) |
| REQ-0.0.63-03-05 | SUPPORT | SKILL.md REQ column + `agent_sync_completed` | ✓ SKILL.md:317 |
| REQ-0.0.63-04-01 | SUPPORT | SKILL.md:80 rescope + `artifact_edited` | ✓ |
| REQ-0.0.63-04-02 | SUPPORT | SKILL.md:64 retained + `artifact_edited` | ✓ |
| REQ-0.0.63-04-03 | SUPPORT | skill-version 7.13.1 + `agent_sync_completed` | ✓ frontmatter:8,16 |
| REQ-0.0.63-07-03 | SUPPORT | template guidance + `artifact_edited` | ✓ `.gzkit/templates/obpi.md`:126-127 |

Per ADR-0.0.59 REQ-kind discipline, none of these eight should carry an `@covers`
test; the audit-check advisory is the expected shape, not a coverage gap.

---

## 2. Feature Demonstration

This ADR delivers **closeout-ceremony / OBPI-pipeline runtime-engine parity**: the human-attestation boundary, the evidence-binding gate, and the verify-stage command-shape gate are now enforced by a single runtime engine rather than by two divergent code paths. Each delivered capability is shown as a command an auditor can re-run, with the operator value it unlocks.

### Capability 1 — Gate-5 cannot be self-advanced (`PolicyBreachError` on the attestation edge)

The ATTESTATION → CLOSEOUT transition is the one edge an agent must not walk past with `--next`. The runtime now reads the ledger for a fresh `attested` receipt and fail-closes if absent (`src/gzkit/commands/closeout_ceremony.py:293-312`, `_gate_attestation_boundary`):

```python
if state.current_step != CeremonyStep.ATTESTATION:
    return
if _has_fresh_attestation_receipt(project_root, state):
    return
raise PolicyBreachError(
    f"Step {int(CeremonyStep.ATTESTATION)} (ATTESTATION) -> "
    f"{int(CeremonyStep.CLOSEOUT)} (CLOSEOUT) is the human-attestation "
    "boundary and cannot be self-advanced with --next: no `attested` ledger "
    "receipt was recorded for this ceremony run. ..."
)
```

The CLI surface exposes the boundary explicitly — `--attest` is the *only* way across, exit code 3 (Policy breach) is the documented failure:

```
$ gz closeout --help
  --next             Advance ceremony to next step (requires --ceremony)
  --attest TEXT      Record attestation at step 6 (e.g. --attest "Completed")
Exit codes
    3   Policy breach
```

**Operator value:** An agent can no longer tick a step counter past your sign-off. The ledger — not the agent's narration — decides whether attestation happened; without your verdict recorded, closeout halts hard at the boundary.

### Capability 2 — Demo-extraction re-execution preflight (receipts bind to observed output)

ARB receipts produced from a brief's demo content bind to the **observed** exit code plus stdout SHA, not the brief's prose claim. The receipt is the re-execution result, not a transcription of what the author said would happen.

**Operator value:** A brief that *claims* "exit 0, all green" but actually fails on re-run can no longer carry a passing receipt — the receipt fingerprints reality, so a stale or aspirational demo claim is caught at closeout instead of being trusted.

### Capability 3 — REQ↔receipt-ID proof-binding validator (`gz validate --closeout-proof-binding`)

Every REQ in the parent ADR's Acceptance Criteria must carry at least one binding receipt-ID in the closeout Evidence Summary; an unbound REQ produces exit 3:

```
$ gz validate --closeout-proof-binding
Validated: closeout_proof_binding

✓ All validations passed (1 scopes).
```

**Operator value:** "All REQs covered" is now a checkable fact, not a claim. Every requirement traces to a specific ledger-present receipt, so the audit reads proof IDs rather than trusting a summary that asserts coverage exists.

### Capability 4 — Verify-stage command-shape gate (closes GHI #550 at authoring time)

The OBPI-pipeline verify stage and `gz validate --documents` reject `## Verification` commands that aren't single-program, shell-less invocations — no `&&`, `||`, `|`, `;`, `$(...)`, or redirects. Brief shape is green:

```
$ gz validate --documents
Validated: documents

✓ All validations passed (1 scopes).
```

**Operator value:** A verification command is forced to be a single, deterministic, re-runnable invocation. Compound shell pipelines — where one segment can fail silently while the line as a whole reports success — are rejected when the brief is authored, not discovered as a false-green during the audit.

### Capability 5 — Single runtime engine (`--next`/`--attest` and Step 7 pipeline emit byte-identical ledger surfaces)

`gz closeout --ceremony --next`, `gz closeout --ceremony --attest`, and the Step 7 pipeline closeout all drive the same state machine. `--attest` is an orchestration shortcut into this engine, not a parallel emitter — re-emit is guarded at `closeout.py:504-512` (`if consumed is None`), so only the ceremony's `attested_event` fires.

```
$ gz closeout --help
  --ceremony         Run interactive ceremony with deterministic step sequencing
  --next             Advance ceremony to next step (requires --ceremony)
  --attest TEXT      Record attestation at step 6
  --restart          Restart ceremony (new attempt, fresh from Step 1)
```

**Operator value:** There is no second closeout path with subtly different rules. Whether you close out interactively or via the pipeline, the same gates fire and the same ledger receipts are written — eliminating the divergence class where one path enforced a boundary the other quietly skipped.

---

## 3. Shortfalls (integration review)

None are proof-channel failures; the audit-check PASS and all 29 REQ proof channels stand. These are forward-looking coherence findings surfaced by the independent quality review and confirmed against primary source.

### S-1 — BI-1 extraction fork → tracked as **GHI #569** (major, latent, likely pre-existing)

**Finding.** BI-1 states multi-line quoted constructs are "joined into one logical command, never split per physical line," spanning OBPI-02 (Demo extractor) and OBPI-07 (Verification extractor). The shared *classifier* `is_shell_less_executable` (`src/gzkit/brief_commands.py:101`) is genuinely consumed by both surfaces — the literal REQ-0.0.63-02-05 claim holds. **But** OBPI-07's verify-stage extractor (`src/gzkit/commands/obpi_stages.py:142-148`) does its own `re.findall(r"```bash\n(.*?)```")` then iterates `block.splitlines()`, classifying each *physical* line — it does **not** reuse the multi-line-joining `extract_fenced_commands` (`brief_commands.py:55`, GHI #539) that the demo path uses (`ceremony_data.py:365`).

**Consequence.** A multi-line `python -c "…"` (or backslash-continued) command in a `## Verification` block is split per physical line; the fragment with the unterminated quote fails `shlex.split` → `is_shell_less_executable` returns False → **BLOCKED** (`SystemExit(1)`). The demo path would *join* and accept the same command. Multi-line `## Verification` commands are a common corpus pattern (ADR-0.0.37, 0.0.43, 0.0.3, 0.0.48, …), so the next author of one would hit a confusing block — a residual flavor of the GHI #550 failure OBPI-07 set out to kill.

**Severity rationale.** Not a proof failure (no OBPI-07 REQ pins join behavior for the verify extractor — grep confirmed NONE). No active breakage in ADR-0.0.63's scope (all instances are in already-completed OBPIs where the verify stage is moot). The per-physical-line split predates OBPI-07; OBPI-07 made it fail-*closed* rather than introducing it. → **latent, forward-reachable.**

### S-2 — BI-2 verdict-classifier duplication → tracked in **agent-insights.jsonl** (major, latent)

**Finding.** The emitter is genuinely single-source (re-emit guarded at `closeout.py:504-512`), so REQ-0.0.63-05-04's byte-identical-ledger-*surfaces* claim holds. But the attestation-verdict classifier is duplicated: `_classify_attestation_verdict` (`ceremony_state.py:180-185`) feeds the `attested` event status, and `_parse_ceremony_attestation_text` (`closeout.py:205-210`) feeds the `lifecycle_transition` `to_state`. Byte-identical semantics today; in-code comments say this is deferred to OBPI-05, but OBPI-05 collapsed the *emitter*, not the classifier.

**Consequence.** Latent fork hazard: any future edit to one classifier silently diverges `attested(status)` from `lifecycle_transition(to_state)`. No active divergence.

### S-3 — Stale line-reference comment → tracked in **agent-insights.jsonl** (cosmetic)

`src/gzkit/commands/closeout.py:508` cites `closeout_ceremony.py:549` for the single-source receipt; the actual `attested_event` emit is at `closeout_ceremony.py:443`. Documentation drift only.

---

## 4. Disposition

Operator decision (2026-05-30): **Proceed to VALIDATED.** Track-and-proceed.

- S-1 (BI-1 extraction fork): GHI #569 filed (`defect`, `runtime`, `tech-debt`); Related: #565, #550.
- S-2 (BI-2 classifier DRY): logged to `.gzkit/insights/agent-insights.jsonl`.
- S-3 (stale comment): logged to `.gzkit/insights/agent-insights.jsonl`.

---

## 5. Attestation

**Signed 2026-05-30.** Operator audit-acceptance (verbatim): *"accept audit, with
contempt - gzkit is a living nightmare now."* Disposition: track-and-proceed (S-1 → GHI #569;
S-2/S-3 → agent-insights). Validated receipt emitted to the ledger (`gz adr emit-receipt
--event validated`, attestor g0), four QA receipts resolved (ruff / unittest /
typecheck / mkdocs). Lifecycle confirmed: `gz adr report ADR-0.0.63` → **Validated**.

Agent signature: pipeline-orchestrator (audit driver), with spec-reviewer + quality-reviewer
+ narrator independent dispatches. The human attested at each of the 7 OBPI completions
(`attested_completed`) and accepted this integrated-ADR audit above.
