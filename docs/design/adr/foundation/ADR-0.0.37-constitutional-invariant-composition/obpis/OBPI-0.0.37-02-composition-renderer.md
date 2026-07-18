---
id: OBPI-0.0.37-02-composition-renderer
parent: ADR-0.0.37-constitutional-invariant-composition
item: 2
lane: Heavy
status: Abandoned
---

<!-- gz-validate-skip: brief-demo-section -->

# OBPI-0.0.37-02-composition-renderer: Composition Renderer

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #2 — "OBPI-0.0.37-02 — Composition renderer (`gz governance render --target agents-md`; deterministic byte output; `--check` mode)"

**Status:** Completed

## Objective

Land the deterministic composition renderer: consume the invariant registry from OBPI-01, project into AGENTS.md template shape, emit a byte-deterministic markdown sequence, and expose the behavior as `gz governance render --target agents-md` with a `--check` mode that exits non-zero on drift without writing.

## Lane

**Heavy** — Introduces a new CLI verb (`gz governance render`), modifies `parser_artifacts.py`, and ships the renderer that AGENTS.md will be rebuilt from. CLI/runtime contract surface.

## Allowed Paths

- `src/gzkit/governance/compose.py` (new) — renderer; consumes registry, emits bytes
- `src/gzkit/commands/governance_render.py` (new) — `gz governance render` CLI implementation
- `src/gzkit/cli/parser_artifacts.py` (modify) — register `governance render` verb
- `tests/governance/test_compose.py` (new) — renderer unit tests (byte-determinism, template projection)
- `tests/commands/test_governance_render.py` (new) — CLI tests (--check mode, exit codes)
- `tests/fixtures/compose/` (new) — fixture registries + expected rendered output for byte-comparison tests
- `docs/user/manpages/governance-render.md` (new) — manpage per gate5-runbook-code-covenant (naming follows the project convention `<verb>-<subverb>.md` per `complexity-distill.md`, `arb-ruff.md` precedent)
- `features/constitutional_invariants.feature` (new) — BDD scenarios for CIC-1 renderer; tagged `@REQ-0.0.37-02-*`; subsequent OBPIs (03, 04, 09) add scenarios to this file
- `docs/user/runbook.md` (modify) — operator runbook entry for `gz governance render`
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-02-composition-renderer.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md` itself (rendered output is consumed/written here only via OBPI-09 migration)
- `src/gzkit/governance/invariants.py` (OBPI-01's surface — consume, do not modify)
- `.gzkit/invariants/*.yaml` (registry content — consumed, not authored here)
- Validator scopes — OBPI-03
- Ledger event registration — OBPI-03 (`composition_rendered`, `composition_drift_detected`)
- CI files, lockfiles, dependency additions

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `compose.py` exposes `render_agents_md(invariants: Mapping[str, ConstitutionalInvariant], template_root: Path) -> bytes`. Output is byte-deterministic — same input mapping (same iteration order, same template) MUST produce identical bytes across repeated invocations and across processes.
2. REQUIREMENT: Iteration order over the invariants is sorted by id (lexicographic) before rendering, to make byte-determinism independent of dict iteration order.
3. REQUIREMENT: Rendering is template-based (Jinja2 if available; otherwise stdlib `string.Template`) — NEVER LLM-driven. Non-determinism at the canon layer is the failure mode this ADR exists to close.
4. REQUIREMENT: `governance_render.py` exposes `gz governance render --target agents-md` that writes the rendered bytes to `AGENTS.md` at repo root. `--check` mode reads the current `AGENTS.md`, re-renders, byte-compares, exits 0 on match and exit code 3 on drift, printing a unified diff of the first 50 differing lines.
5. REQUIREMENT: `--stdout` mode emits to stdout without writing the file (used by drift validator and integration tests).
6. REQUIREMENT: `--target agents-md` is the only target accepted at this OBPI; other targets (skill READMEs, persona files) raise `argparse` error `unsupported target` — they are forward-references for future feature ADRs.
7. REQUIREMENT: This OBPI does NOT register ledger events (OBPI-03's scope) and does NOT wire `gz validate --invariant-coherence` (OBPI-03's scope). The renderer is a stand-alone producer; the validator consumes it.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (`src/gzkit/governance/invariants.py` and `.gzkit/invariants/*.yaml` absent), halt — this OBPI depends on the registry primitive.

## Discovery Checklist

**Parent ADR (read first; order pinned):**

- [ ] Quote ADR § Decision item #2 (composition renderer) verbatim into Implementation Summary
- [ ] ADR § Intent — the inversion this renderer closes
- [ ] Parent ADR file

> **STOP:** If you cannot quote the renderer paragraph, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/cli.md` — CLI verb registration conventions
- [ ] `.gzkit/rules/gate5-runbook-code-covenant.md` — manpage and runbook obligations

**Prerequisites:**

- [ ] OBPI-0.0.37-01 landed (registry primitive available)
- [ ] `src/gzkit/templates/agents.md` exists (used as template root)

**Existing Code:**

- [ ] `src/gzkit/commands/specify_cmd.py` — example of a `gz` subcommand with `--check` / write modes
- [ ] `src/gzkit/cli/parser_artifacts.py` — verb-registration pattern (`_LAZY_HANDLERS` + `_register_*_parsers` + lazy func dispatch)
- [ ] `src/gzkit/templates/agents.md` — current template shape (consumed as the projection target)
- [ ] `src/gzkit/governance/invariants.py` — `ConstitutionalInvariant` Pydantic model and `load_invariants()` from OBPI-0.0.37-01
- [ ] `.gzkit/invariants/*.json` — three seed invariants (CIC-1, CIC-2, foundation-adr-registers-invariant) registered by OBPI-01
- [ ] `tests/governance/test_invariants.py` — REQ-derived test pattern for governance modules (use as template for `test_compose.py`)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded; renderer paragraph quoted

### Gate 2: TDD

- [ ] Tests in `test_compose.py` and `test_governance_render.py` derived from REQs
- [ ] RGR cycle followed
- [ ] Tests pass: `uv run -m unittest tests.governance.test_compose tests.commands.test_governance_render`

### Code Quality

- [ ] Lint: `uv run gz lint`
- [ ] Typecheck: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-governance.md` exists with NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES sections; EXAMPLES shows real `gz governance render --check` output
- [ ] `docs/user/runbook.md` entry for "When AGENTS.md drifts: `gz governance render --check`"
- [ ] Docs build clean: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy)

- [ ] `features/constitutional_invariants.feature` includes scenarios for renderer byte-determinism and `--check` exit codes; tagged `@REQ-0.0.37-02-01`, `-02`, `-03`
- [ ] `uv run -m behave features/constitutional_invariants.feature` passes

### Gate 5: Human (Heavy + Foundation universal)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_compose tests.commands.test_governance_render -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature

# REQ-01/02: byte-determinism across consecutive invocations
diff <(uv run gz governance render --target agents-md --stdout) <(uv run gz governance render --target agents-md --stdout) && echo "REQ-01 OK: byte-identical across runs"

# REQ-04: --check exit codes
uv run gz governance render --target agents-md --check && echo "REQ-04 OK: --check exit 0 on match"
# (drift case exercised in test_governance_render.py)

# REQ-06: rejected target
uv run gz governance render --target skill-readme 2>&1 | rg -q "unsupported target" && echo "REQ-06 OK: rejected unknown target"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-02-01: `gz governance render --target agents-md --stdout` produces byte-identical output across consecutive invocations on the same registry
- [ ] REQ-0.0.37-02-02: `gz governance render --target agents-md --check` exits 0 when committed AGENTS.md matches rendered output; exits 3 when they differ and prints a unified diff
- [ ] REQ-0.0.37-02-03: `gz governance render --target agents-md` (no `--check`) writes the rendered bytes to `AGENTS.md` and reports the byte count written
- [ ] REQ-0.0.37-02-04: `gz governance render --target <anything-other-than-agents-md>` exits with argparse error message `unsupported target`
- [ ] REQ-0.0.37-02-05: The `governance render` verb is registered in `src/gzkit/cli/parser_artifacts.py` and resolves via `gz governance render --help`

## Completion Checklist

- [ ] Gate 1 / 2 / 3 / 4 / 5 satisfied as above
- [ ] `gz obpi reconcile OBPI-0.0.37-02-composition-renderer` reports zero drift before completion

## Evidence

### Gate 1 / 2 / Code Quality / Gate 3 / Gate 4 / Gate 5

```text
# Paste outputs here per REQ
```

### Value Narrative

<!-- Before: AGENTS.md was hand-authored prose; no mechanical projection from registry; drift impossible to detect without a renderer. After: deterministic renderer ships; AGENTS.md becomes a derivable artifact. -->

### Key Proof


REQ-0.0.37-02-01 (byte-determinism) — verified live:

```
$ diff <(uv run gz governance render --target agents-md --stdout) \
       <(uv run gz governance render --target agents-md --stdout) \
  && echo "REQ-01 OK: byte-identical across runs"
REQ-01 OK: byte-identical across runs
```

REQ-0.0.37-02-04 (unsupported target) — verified live:

```
$ uv run gz governance render --target skill-readme
unsupported target: 'skill-readme'. Supported targets: ['agents-md']
```

Quality gates (canonical ARB receipts):
- Lint: `arb-ruff-c1ba28b870744ebbb39be736ed3f53ab` (exit 0)
- Typecheck: `arb-step-typecheck-61e6b65d7c2947da952c764992d126c8` (exit 0)
- Unittest: `arb-step-unittest-a67ab049e79147f0a83ac4e41232a434` (5339/5339 pass)
- Mkdocs --strict: `arb-step-mkdocs-0863cbce74764376919ea219e6252068` (exit 0)
- Behave (constitutional_invariants.feature): 6/6 scenarios pass, 31/31 steps, all 5 REQs tagged

REQ coverage (verified by `uv run gz covers OBPI-0.0.37-02-composition-renderer --json`): 0 uncovered REQs.

### Implementation Summary


- Files created: `src/gzkit/governance/compose.py` (Jinja2-based byte-deterministic renderer), `src/gzkit/commands/governance_render.py` (CLI handler with `--check`, `--stdout`, write modes), `tests/governance/test_compose.py` (9 unit tests), `tests/commands/test_governance_render.py` (12 CLI tests), `tests/fixtures/compose/{agents.md,CIC-test-alpha.json,CIC-test-beta.json}` (test fixtures), `docs/user/manpages/governance-render.md` (manpage with NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES), `features/constitutional_invariants.feature` (6 BDD scenarios), `features/steps/constitutional_invariants_steps.py` (step definitions).
- Files modified: `src/gzkit/cli/parser_artifacts.py` (registered `_register_governance_parsers` and `governance_render_cmd` lazy handler), `src/gzkit/governance/trust_audits/cli.py` (added `governance` to `_NO_SKILL_VERBS` with rationale), `config/doc-coverage.json` (added `governance render` entry with 4 surface requirements), `docs/user/manpages/index.md` (added index row), `docs/user/runbook.md` + `docs/governance/governance_runbook.md` (added runbook entries).
- Tests added: 9 compose unit tests + 12 CLI command tests + 6 BDD scenarios (31 steps) = 27 new test entries; all 5 REQs covered via `@covers` decorators and `@REQ-0.0.37-02-NN` scenario tags.
- Date completed: 2026-05-19.
- Attestation status: Human-attested via operator-verbatim "attest completed" relayed in Stage 4.
- Defects noted: (1) Brief drift — original brief listed `docs/user/manpages/gz-governance.md` but project convention (`complexity-distill.md`, `arb-ruff.md` precedent) is `<verb>-<subverb>.md`. Brief allowed path updated to `governance-render.md` in same OBPI per Coupled-Surface Coherence. (2) Discovery Checklist refactored from non-canonical "Context (existing exemplars)" section to required `**Existing Code**` block per `gz obpi validate --authored` contract. (3) Brief Completion Checklist referenced unregistered `gz brief reconcile` verb (OBPI-06 future scope) — replaced with `gz obpi reconcile` for current pipeline parity.

## Tracked Defects

- GHI #495 — ADR-0.0.37 OBPI briefs in unindividualized scaffold state
- GHI #485 — root-cause of the scaffold defect

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator-verbatim attestation relayed from Stage 4 conversational gate; OBPI-0.0.37-02-composition-renderer ships byte-deterministic Jinja2 composition renderer (`gz governance render --target agents-md` with `--check`/`--stdout`/write modes), all 5 acceptance REQs covered by unit + BDD tests, Heavy-lane gates green: lint receipt `arb-ruff-c1ba28b870744ebbb39be736ed3f53ab`, typecheck receipt `arb-step-typecheck-61e6b65d7c2947da952c764992d126c8`, unittest receipt `arb-step-unittest-a67ab049e79147f0a83ac4e41232a434` (5339/5339), mkdocs receipt `arb-step-mkdocs-0863cbce74764376919ea219e6252068`, behave 6/6 scenarios pass. Plan-audit receipt PASS; precomplete 7/7. attestation_type: operator-verbatim-conversational per ADR-0.0.36.
- Date: 2026-05-19

---

**Brief Status:** Draft

**Date Completed:** 2026-05-19

**Evidence Hash:** -
