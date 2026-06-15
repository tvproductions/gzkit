# Plan: OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop — Advisor-Panel Info-Retention QC Loop

**OBPI:** OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop
**ADR:** ADR-0.0.37-constitutional-invariant-composition (Checklist item #24)
**Lane:** Heavy
**Status:** Ready for implementation (B.1, sequence 1 of 3 — produces the receipt OBPI-25 consumes)

## Booked decisions (operator, 2026-06-14)

- **Receipt schema: doctrine-aligned ARB receipt.** Emit the verdict as an existing-form
  ARB receipt aligned to ADR-0.0.39 doctrine fields (explanation-before-verdict, candidate
  provenance), **NOT** bound to the un-landed `judge_invocation.json`. (Resolves the brief's
  § Open Implementation Decision; re-confirm at Gate 5.)
- **Receipt id form: `arb-step-judge-<32hex>`.** The receipt-id regex is
  `arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}` — the step segment forbids a hyphen, so
  `advisor-qc` is INVALID as a step name. Use step name **`judge`** (matches the brief's
  `arb-step-judge-*` form). `<32hex>` via `uuid.uuid4().hex`.

## Context

Delivers the **advisor-QC** stage between compress (OBPI-21) and commit (OBPI-22): an agent,
wielding the `gz-advisor-qc` skill, judges the information-retained-per-byte of a candidate
rendition and records its verdict as an ARB receipt the operator cites at Gate 5. The tool is
**deterministic** (no in-code LLM/network) — it ingests the agent's verdict + explanation,
validates receipt shape (explanation-before-verdict), writes the receipt, and emits a ledger
event. It is **advisory-never-gating**: a low retention score is evidence, never a fail-closed
gate. The ONLY fail-closed path is a structurally malformed receipt (missing explanation).

**Cross-ADR dependency (surfaced, not blocking):** ADR-0.0.39 (llm-as-judge) is Proposed/Pending;
`judge_invocation.py`/`.json` do not exist. This OBPI binds to ADR-0.0.39's stable *doctrine*
and the existing ARB receipt infrastructure (`src/gzkit/arb/`), not the un-landed schema.

## Discovery-grounded patterns (mirror these)

- **Handler** ← `src/gzkit/commands/content/remember.py` (`content_remember_cmd(*, ...) -> None`;
  fail-closed-*before*-write; exit 0 success / 1 user-error / 2 IO; ledger via factory).
- **Subparser** ← `_register_remember` in `commands/content/__init__.py` (lazy
  `_content("advise_rendition", "content_advise_rendition_cmd")` dispatch); add
  `_register_advise_rendition(content_commands)` after `_register_compose` in the call list (~line 53).
- **Receipt write** ← `arb/step_reporter._write_receipt` + `arb/paths.receipts_root()`
  (env override `GZKIT_ARB_RECEIPTS_ROOT`; default `.gzkit.json` config / `artifacts/receipts/`).
  Build a **verdict-shaped** receipt (NOT `run_step_via_arb`, which is command-execution shaped).
- **Receipt validity** ← `governance/trust_audits/attestation_receipts.py`: file exists, parses
  as JSON, `exit_status == 0`, category match. Verdict receipt MUST carry `exit_status: 0` and
  `run_id: arb-step-judge-<32hex>`.
- **Typed event** ← `events.CompositionRenderedEvent` (`_EventBase` + `Literal[...]`); register
  `RenditionAdvisorVerdictEvent` in `TypedLedgerEvent` union.
- **Write factory** ← `ledger_events.composition_rendered_event` → `rendition_advisor_verdict_event`.
- **Schema** ← `schemas/ledger.json` `composition_rendered` block (required-fields shape).
- **No-graph waiver** ← `governance/trust_audits/events.py` `_NO_GRAPH_IMPACT` (substantive rationale).
- **Skill** ← `.gzkit/skills/gz-content-remember/SKILL.md` (tool+skill split).

## Files

### Creates These Files

- `src/gzkit/commands/content/advise_rendition.py` **CREATE** — `content_advise_rendition_cmd(*, ...)`
- `src/gzkit/content/advisor_qc.py` **CREATE** — deterministic verdict-record engine
- `.gzkit/skills/gz-advisor-qc/SKILL.md` **CREATE** — the LLM-as-judge skill (wields the tool)
- `tests/commands/test_content_advise_rendition.py` **CREATE** — command-level BEHAVIOR tests
- `tests/content/test_advisor_qc.py` **CREATE** — engine-level BEHAVIOR tests
- `docs/user/skills/gz-advisor-qc.md` **CREATE** — skill manpage
- `features/content_advise_rendition.feature` **CREATE** — `@REQ-0.0.37-24-*` BDD

### Edits

- `src/gzkit/commands/content/__init__.py` — register `_register_advise_rendition`
- `src/gzkit/events.py` — add `RenditionAdvisorVerdictEvent` + register in `TypedLedgerEvent`
- `src/gzkit/ledger_events.py` — add `rendition_advisor_verdict_event(...)`
- `src/gzkit/schemas/ledger.json` — register `rendition_advisor_verdict` event type
- `src/gzkit/governance/trust_audits/events.py` — `_NO_GRAPH_IMPACT` waiver entry
- `tests/test_schemas.py` — add `rendition_advisor_verdict` to `_EVENT_MODELS`
- `tests/content/test_tui_affordances.py` — admit `advise-rendition` in the content-subcommand fence
- `config/doc-coverage.json` — declare `content advise-rendition`
- `docs/user/manpages/content.md` — `### advise-rendition` subsection + real EXAMPLES
- `docs/user/runbook.md` — operator runbook entry
- `docs/user/skills/index.md` — link the new skill manpage
- `.gzkit/skills/gz-context/SKILL.md` — route `gz-advisor-qc` (skill-version bump + last_reviewed)
- `data/distribution_baseline_manifest.json` — regen for the new canonical skill (ADR-0.0.31)
- `data/behave_coverage_waivers.json` — OBPI-level waiver for SUPPORT REQs w/o Gherkin behavior
- (brief + parent ADR evidence/checklist as usual)

**Sync-generated mirrors** (written by `gz agent sync control-surfaces`, never hand-edited):
`src/gzkit/skills/gz-advisor-qc/SKILL.md`, `.claude/...`, `.github/...`, `.agents/...`.

## Steps (TDD-ordered)

### Step 0 — Brief reconcile
`uv run gz validate --brief-reconcile` (confirm allowlist + REQ count vs reality before any edit).

### Step 1 — `advisor_qc.py` engine (REQ-01, REQ-02, REQ-03) — RED→GREEN
Deterministic, stdlib + Pydantic only. Public surface (sketch):
```python
def record_verdict(*, root: Path, surface: str, consumer: str | None,
                   explanation: str, score: float) -> Path:
    """Assemble + write the advisor-QC ARB receipt; return its path.
    Fail-closed (ValueError, NO receipt written) when explanation is empty/absent.
    Receipt field order puts explanation BEFORE verdict/score (ADR-0.0.39).
    run_id = arb-step-judge-<uuid4().hex>; exit_status = 0; deterministic given inputs."""
```
Tests (`tests/content/test_advisor_qc.py`, `@covers`):
- `test_records_receipt_and_is_advisory` (REQ-01): any score → receipt written, no raise.
- `test_empty_explanation_fails_closed_no_receipt` (REQ-02): empty explanation → raise, no file.
- `test_deterministic_no_llm` (REQ-03): identical input → identical receipt payload (modulo the
  injected run_id/timestamp seam — inject these so the body is byte-stable); assert no network/LLM.

### Step 2 — `rendition_advisor_verdict` event (REQ-04)
Typed model + factory + `ledger.json` block (`required: surface, consumer, receipt_id, score`)
+ `_NO_GRAPH_IMPACT` waiver + `tests/test_schemas.py` `_EVENT_MODELS` entry. Emit on successful record.

### Step 3 — `advise_rendition.py` command handler (REQ-01/02 at the CLI seam)
`content_advise_rendition_cmd(*, surface, consumer, explanation, score)` → validate → call
`advisor_qc.record_verdict(...)` → emit ledger event → exit 0 (advisory). Empty explanation → exit
non-zero, no receipt. Register subparser; admit in `test_tui_affordances` fence. Tests in
`tests/commands/test_content_advise_rendition.py` (`@covers` REQ-01/02).

### Step 4 — Skill + surfaces (REQ-05)
`.gzkit/skills/gz-advisor-qc/SKILL.md` (frontmatter: name, description, category, lifecycle_state:
active, owner, last_reviewed: <today>, model, gz_command: `gz content advise-rendition`; body:
Overview / Workflow / Validation / Example). `gz agent sync control-surfaces` → mirrors byte-equal.
Skill manpage + index link + gz-context router (bump skill-version + last_reviewed together).
Regen `data/distribution_baseline_manifest.json`.

### Step 5 — Docs (REQ-06)
`content.md` `### advise-rendition` + EXAMPLES (real CLI output), runbook entry, `doc-coverage.json`.

### Step 6 — BDD (REQ-01/02/03)
`features/content_advise_rendition.feature` tagged `@REQ-0.0.37-24-0{1,2,3}`. SUPPORT REQs ride the
behave waiver.

## Verification (canonical, arb-wrapped)

```bash
uv run gz validate --brief-reconcile
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.content.test_advisor_qc tests.commands.test_content_advise_rendition -v
uv run gz covers OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop --json
uv run gz validate --ledger
uv run gz validate --surfaces
uv run gz validate --documents --cli-alignment
uv run mkdocs build --strict
uv run -m behave features/content_advise_rendition.feature
```

## Notes / risks

- **Verdict-receipt envelope** is the one design nuance: satisfy BOTH validators (`arb-step-judge-<32hex>`
  id regex + `exit_status == 0`) while carrying advisor fields (explanation-first, score, surface,
  consumer, provenance). Build via `_write_receipt`, not `run_step_via_arb`.
- **No in-code LLM/network** — the judgment is the skill's; the tool only records/validates. (STDLIB-FIRST.)
- **Advisory-never-gating** — a low score never blocks; only a malformed (explanation-less) receipt fails closed.
- **Gate 5 (Heavy/foundation, no self-close):** attest + re-confirm the receipt-schema decision.
- Produces the receipt **OBPI-25's** compressible-tier branch witnesses (surface-level).
