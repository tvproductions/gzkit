---
id: ADR-0.0.65-handoff-system-consolidation
status: Validated
kind: foundation
semver: 0.0.65
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-29
promoted_from: ADR-pool.handoff-system-consolidation
---

# ADR-0.0.65-handoff-system-consolidation: Handoff System Consolidation and CLI Surface

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

The session-handoff system is half-wired: the documented surface, the code
that backs it, and the runtime that reads it disagree. A 2026-05-29 audit
(GHI #529) surfaced three concrete defects plus an unresolved doctrine
conflict that no single direct fix can resolve because the canonical write
location is genuinely contested between two governance surfaces.

Observed defects:

1. **Read/write location split-brain.** The `gz-session-handoff` skill writes
   handoffs to `{ADR-package}/handoffs/` (`SKILL.md:32,83`), but the
   SessionStart orientation read only `.gzkit/handoffs/`
   (`scripts/session_orientation.py::collect_handoff`). ADR-package handoffs
   were therefore invisible to auto-orientation.
2. **Non-handoff `.md` false-positive.** `collect_handoff` picked the newest
   `*.md` by mtime with no content filter, so `.gzkit/handoffs/AGENTS.md`
   (a generated subtree-rules file) was surfaced as "the most-recent handoff."
3. **Vaporware programmatic API.** `SKILL.md` documents
   `create_handoff` / `scaffold_handoff` / `list_handoffs` / `resume_handoff` /
   `load_handoff_chain` importable from `tests.governance.test_session_handoff`
   — a module that does not exist. Only `src/gzkit/handoff_validation.py`
   (`validate_handoff_document`) is backed by code, so CREATE/RESUME flows
   cannot be executed as documented and handoffs end up hand-authored, which
   bypasses the validation gate.

A partial repair already landed for (1) and (2) (commit `2ab33914`,
`fix(orientation): … (GHI #529)`): `collect_handoff` now unions both
locations and filters to files carrying `adr_id` frontmatter. That fix is
forward-compatible with either resolution of the doctrine conflict below; it
does not resolve the conflict itself.

## Why foundation tier?

Without this ADR, the project would not be the project because handoff storage
is a governance source-of-truth boundary: agents cannot preserve intent across
sessions if the write surface, read surface, and executable authoring API
disagree about where audit-bearing recovery state lives.

## Decision

Consolidate the handoff system to a single source of truth across doctrine,
skill, code, and CLI:

1. **Resolve the canonical write location** by amending whichever surface
   loses. The two contestants:
   - `.claude/rules/token-block-discipline.md` (OBPI-0.0.41-03):
     *"the handoff document written to `.gzkit/handoffs/` (canonical storage
     per OBPI-0.0.41-03)"*
   - `gz-session-handoff/SKILL.md`: writes `{ADR-package}/handoffs/`

   This is the foundation-shaping decision and must be made by an operator at
   promotion time, not inferred. (Working hypothesis for the design pass: the
   token-block rule has ADR-anchored doctrinal weight, but ADR-package
   co-location keeps handoffs with the work they describe and is what the
   working manual resume already uses — the trade-off is real and unresolved.)

2. **Build the documented programmatic API** (`create_handoff`,
   `scaffold_handoff`, `list_handoffs`, `resume_handoff`, `load_handoff_chain`)
   as real importable code in `src/gzkit/` (not a `tests.` module), wrapping the
   existing `handoff_validation.py` so CREATE runs the validation gate
   mechanically — OR rewrite the skill to document only what exists. The former
   is preferred (the skill's RESUME chain-traversal and staleness gate are
   genuinely useful).

3. **Add a `gz handoff` CLI verb** (the original GHI #529 ask) exposing
   create/resume/list, so handoff authoring routes through the validation gate
   instead of hand-authored markdown.

4. **Align the orientation reader** with the resolved canonical location (the
   union scan from `2ab33914` becomes a single-location read once one wins, or
   stays a union if both remain supported).

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The `gz handoff` CLI verb ships and its read projection over `.gzkit/handoffs/` works (OBPI-02/-03). | uv run gz handoff list --json | 0 |
| The archive lock-handoff coupling guard the retention OBPI honors validates green (OBPI-05). | uv run gz validate --lock-handoff-coupling | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.65-handoff-system-consolidation --check | 0 |

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 7
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [x] OBPI-0.0.65-01: **canonical-location-migration** — Canonize `.gzkit/handoffs/` as the single handoff write location per ADR-0.0.41 / OBPI-0.0.41-03. Migrate the 24 per-ADR handoff files (across 10 ADR packages) into `.gzkit/handoffs/`, preserving `continues_from:` chains and frontmatter timestamps. Amend `gz-session-handoff/SKILL.md` output-path doctrine from `{ADR-package}/handoffs/` to `.gzkit/handoffs/`. Bump `skill-version` and `last_reviewed`; run `gz agent sync control-surfaces`.
- [x] OBPI-0.0.65-02: **programmatic-api-implementation** — Ship real `create_handoff`, `scaffold_handoff`, `list_handoffs`, `resume_handoff`, `load_handoff_chain` in `src/gzkit/handoff_api.py` (or equivalent runtime module) wrapping `handoff_validation.py`. Replace the `gz-session-handoff/SKILL.md` import references from `tests.governance.test_session_handoff` to the real runtime module. Remove the `NOT IMPLEMENTED` disclaimers.
- [x] OBPI-0.0.65-03: **gz-handoff-cli-verb** — Add `gz handoff` CLI verb with `create`, `resume`, `list` subcommands routing authoring through the validation gate. Add manpage under `docs/user/manpages/`. Add behave coverage for create/resume/list flows.
- [x] OBPI-0.0.65-04: **orientation-single-location-scan** — Collapse `_candidate_handoff_dirs()` in `scripts/session_orientation.py` to a single-surface scan of `.gzkit/handoffs/`. Delete the GHI #529 dual-scan workaround. Update orientation tests. (Depends on OBPI-01 completion: cannot collapse the scan until the per-ADR sources are empty.)
- [x] OBPI-0.0.65-05: **handoff-archive-retention** — Add a governed `gz handoff archive` subcommand that moves handoffs older than a threshold from `.gzkit/handoffs/` to `.gzkit/handoffs/archive/` (move-not-delete; audit trail preserved), honoring three mechanical guards: the migration-floor test (count canonical + archive ≥ floor), `continues_from:` chain integrity (chains may cross into the archive subdir), and lock-handoff coupling (never archive a handoff referenced by an `obpi_lock_released` ledger event). Extend `tests/governance/test_handoff_migration.py` to count the archive subdir. Add manpage + behave coverage. Surface-boundary split from OBPI-03 (distinct retention semantics + guard coupling). Depends on OBPI-03 (the `gz handoff` verb must exist). Closes GHI #585.

## Target Scope

- **canonical-location-migration** — Canonize `.gzkit/handoffs/` as the single handoff write location per ADR-0.0.41 / OBPI-0.0.41-03; migrate 24 per-ADR handoffs into the canonical store; amend `gz-session-handoff/SKILL.md` output-path doctrine and bump skill-version.
- **programmatic-api-implementation** — Ship real `create_handoff` / `scaffold_handoff` / `list_handoffs` / `resume_handoff` / `load_handoff_chain` in `src/gzkit/handoff_api.py` wrapping `handoff_validation.py`; remove the `NOT IMPLEMENTED` disclaimers and replace `tests.governance.test_session_handoff` import references with the real module.
- **gz-handoff-cli-verb** — Add `gz handoff` CLI verb with `create` / `resume` / `list` subcommands routing authoring through the validation gate; add manpage and behave coverage.
- **orientation-single-location-scan** — Collapse `_candidate_handoff_dirs()` in `scripts/session_orientation.py` to a single-surface scan; delete the GHI #529 dual-scan workaround. Depends on `canonical-location-migration` completing first.
- **handoff-archive-retention** — Governed `gz handoff archive` move-not-delete verb (`.gzkit/handoffs/` → `.gzkit/handoffs/archive/`) honoring the migration-floor, `continues_from`-chain, and lock-handoff-coupling guards; extends `tests/governance/test_handoff_migration.py` to count the archive subdir; manpage + behave coverage. Depends on `gz-handoff-cli-verb`. Closes GHI #585.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

**Kind at promotion:** `foundation` — the canonical-location decision shapes a
system invariant (where the audit-bearing register entries live) and the
token-block coupling is foundation doctrine. The CLI verb + API are the
adapter layer atop that invariant.

**Evidence base:** GHI #529 (this ADR's source); partial repair commit
`2ab33914`; sibling cleanup GHI #565 (brief Verification compound commands) is
unrelated to handoffs but was filed in the same audit session. Operator
decision 2026-05-29 on the canonical-location forcing function captured in
the OBPI Decomposition table above.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.handoff-system-consolidation` on 2026-05-29; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.65 | Completed | g0 | 2026-07-15 | Completed — attest completed (g0): 5/5 OBPIs attested; 6 live demos verified (archive dry-run/live parity, list --json/--adr, resume, gated create); ARB green — arb-ruff-d510f84, arb-step-typecheck-c615ea4, arb-step-unittest-ab54fac6, arb-step-mkdocs-5447c487; bound fidelity gate passed; validate --documents clean. |
| 0.0.65 | Validated | g0 | 2026-07-15 | Validated — accept audit (g0): L2 ledger proof 5/5 OBPIs PASS; bound fidelity gate 3/3 (rewritten to exercise the shipped gz handoff verb); spec-reviewer PASS-WITH-CONCERNS + quality-reviewer COHERENT-WITH-CONCERNS concur no blocking defect; split-brain closed; S1 doc drift remediated in-audit; S2/S3 filed GHI #688/#689. ARB green — arb-ruff-7d3c75c0, arb-step-typecheck-a8a076b2, arb-step-unittest-8db5e4cf, arb-step-mkdocs-a49646b0. |
