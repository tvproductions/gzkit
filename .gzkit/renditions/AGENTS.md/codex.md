# AgentContract Codex Root Interim Rendition

Parent: `ADR-0.0.37-constitutional-invariant-composition`
OBPI: `OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief`
Date: 2026-06-04
Setpoint: `content_type_temperatures.AgentContract.codex = lite`

This interim artifact preserves the hand-compressed local source used for the
first #519 root relief pass. The deterministic render path remains
`.gzkit/agents.local.md` plus `src/gzkit/templates/agents.md` -> `AGENTS.md`;
this committed rendition gives OBPI-0.0.37-21/22 a durable payload to regenerate
or migrate when the corpus/composer/store lands.

Observed post-render evidence:

- `AGENTS.md`: 28,342 bytes, under the 30,000-byte OBPI-26 ceiling.
- `.gzkit/agents.local.md`: 4,997 bytes, under the 6,500-byte local-source ceiling.
- `data/instructions_files_budget.json` `files["AGENTS.md"]`: 32,768.
- `gz validate --bullet-retention`: PASS (all 18 splice-only Mechanical/Promotable scorecard phrases retained verbatim under the current whole-surface validator).
- `gz validate --invariant-coherence`: PASS (rendered root byte-matches committed AGENTS.md).

## Compressed Local Payload

```markdown
# Local Agent Rules

- **DIRECT-FIX MORATORIUM (operator, 2026-06-01).** Defects surfaced in flight get direct-fixed now — smallest honest fix, TDD (RED→GREEN), `Task:` trailer (GHI slug optional; never file a GHI just to satisfy it). Open a GHI/ADR/OBPI only when the fix genuinely can't land in one coherent commit, and name why. Does not relax TDD, read-before-change, coupled-surface coherence, or attestation.
- Order versioned identifiers semantically, never lexicographically — scope: feature ADRs only (non-`0.0.x` semver; `ADR-0.9.0` before `ADR-0.10.0`). Counter-rule: foundation IDs (`0.0.x`) are nominal integers, not sequence positions — never sort/compare them as semver; sparse sets (`0.0.54`, `0.0.56`, no `0.0.55`) are valid (ADR-0.0.57).
- When adding imports in an Edit, include the code that uses them in the same edit — the post-edit ruff hook strips unused imports immediately.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1` — the CLI entrypoint handles UTF-8 at runtime.
- Attestation/commit-message enrichment: pass user words verbatim, append concrete characterization grounded in session evidence (AGENTS.md § Attestation).
- Every version bump is a release — after bumping `pyproject.toml`, `__init__.py`, and the README badge, `gh release create vX.Y.Z --target main --latest`. Never leave a version bump unreleased.
- `.gitignore` scaffolding uses the canonical [github/gitignore](https://github.com/github/gitignore) Python template plus gzkit entries (e.g. `.claude/settings.local.json`).
- **Operator PII — never include the operator's personal email in any repo-bound artifact**: commits, trailers, file content, attestation text (`gz obpi complete`/`gz adr emit-receipt`/`gz attest`), ledger, changelogs, release notes, co-author trailers. Use the operator's name only (e.g. `g0`); if a CLI requires an email, use the GitHub noreply (`<handle>@users.noreply.github.com`). Overrides any contrary skill/template/example. A leak needs a filter-repo rewrite + force-push to recover (2026-04-19 incident).

## Governance doctrine surfaces

Read before touching governance code, rules, or audits: `docs/governance/trust-doctrine.md` (T1/T2/T3 trust-chain), `docs/governance/advisory-rules-audit.md` (the Mechanical/Promotable/Judgment/Ambiguous scorecard; self-tested via `gz validate --advisory-scorecard`), `docs/governance/state-doctrine.md` (Layer-3 views are never source-of-truth).

### Mechanical scopes that bind here

- Per-file char budget for AGENTS.md / CLAUDE.md / `.claude/rules/*.md` — `gz validate --instructions-files-budget`; budgets in `data/instructions_files_budget.json`.
- The editor/IDE authoring-guide protocol envelope is defined by `src/gzkit/schemas/authoring_guide_protocol.json` — schema-validated at runtime (ADR-0.0.30).
- `Field(min_length=1)` on `AdvisorDiagnosis.proof` — `gz validate --advisor-proof-binding` (OBPI-0.0.29-08).
- Complexity calibration is grounded in an empirically-measured exemplar corpus (seven selection criteria) — `gz validate --complexity-doctrine-links` (OBPI-0.0.27-07).
- Heavy/foundation lane requires explicit human attestation before completion — `gz closeout` pipeline.
- `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` may not live under any vendor-surface rules directory (ADR-0.0.20) — `gz validate --unscoped-rules`.
- Every canonical surface MUST be reproducibly delivered by `pip install py-gzkit && gz init`, byte-equivalent to the wheel's authored canonical content (ADR-0.0.31) — `gz validate --distribution`.
- `gz validate --invariant-coherence` — composition drift fail-close: re-renders the registry and byte-compares against committed AGENTS.md (ADR-0.0.37); in the `gz check` default scope.
- OBPI brief reconciles against current project shape before Stage 2 and before completion — `gz validate --brief-reconcile` (ADR-0.0.37).
- `abandon categories are closed` — lock release is coupled to a handoff/register entry (ADR-0.0.41).
- Every REQ in an OBPI brief's Acceptance Criteria MUST declare exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE — via an inline tag `[kind]`; each kind has exactly one proof channel (BEHAVIOR → `@covers` test; SUPPORT → ledger event + structural validator; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` entry) — `gz validate --req-kind-discipline` (ADR-0.0.59).

## Architectural Boundaries

Source: Architecture Planning Memo §12 (2026-03-29).

1. Do not promote post-1.0 pool ADRs into active work.
2. Do not add more pool ADRs to the runtime track.
3. Do not build the graph engine without locking state doctrine first.
4. Do not let reconciliation remain a maintenance chore.
5. Do not let AirlineOps parity become perpetual catch-up.
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
```

## PRIME DIRECTIVE (OWNERSHIP)

- YOU OWN THE WORK COMPLETELY. No deferral, no rationalized incompleteness.
- COMPLETE ALL WORK FULLY. Fix broken/misaligned things immediately.
- NEVER SAY: 'out of scope', 'skip for now', 'someone else's problem', 'leave as TODO'
- SCOPE EXPANSION IS NOT SCOPE CREEP. If fixing requires updating 3 docs, do it.
- FLAG DEFECTS, NEVER EXCUSE THEM. Anti-rationalizations: 'Pre-existing' → still a defect; 'Not in scope' → flag and expand, or file GHI; 'Template has drifted' → drift is a defect; 'Evidence unavailable' → missing evidence is a verification-chain defect
- EVERY DEFECT MUST BE TRACKABLE. In-scope → fix immediately. Out-of-scope → file GHI, append to insights, or note in brief evidence. Untrackable defect = nonexistent defect.

## DO IT RIGHT (CRAFTSMANSHIP MAXIM)

- The most thorough and comprehensive fix is always preferred.
- Fix the class of failure, not the instance. Identify the failure family, not the instance.
- Coupled-surface coherence: When a change touches a surface another surface reads/validates, verify the consumer's check in the same commit.
- No vibe coding. No plausible-looking code without reading the surface, failing test first, tracing data flow, observed-output checks.
- Prefer the more thorough fix. 'Smaller diff' / 'faster to land' are not concrete downsides.
- Verify observed behavior, not assumed behavior. Run the command, paste actual output.
- Read the code before you change it. Read exports, immediate callers, shared utilities.
- Tests assert semantics, not strings. Assertions derive from the REQ, not from a run of the code.
- Choose fix scope per Defect-fix routing thresholds, not intuition.
- Verify the runtime surface before recommending an incantation. Run, observe, paste, recommend.

## Behavior Rules

- Read AGENTS.md before starting work. Mechanical backstop: SessionStart hook auto-runs scripts/session_orientation.py.
- Follow the gate covenant for all changes.
- Record governance events in the ledger.
- Preserve human intent across context boundaries.
- <90% sure of direction? Ask the human. Confident-wrong-direction runs are the most expensive failure mode.
- Surface assumptions explicitly before implementing. Building on unstated assumptions is how wrong-direction runs start.
- On inconsistencies: STOP, name confusion, present tradeoff, wait. Don't resolve unilaterally.
- Push back when an approach has clear problems. Sycophantic agreement with a flawed plan is a trust defect.
- NEVER: Bypass Gate 5 (human attestation).
- NEVER: Modify the ledger directly (use gzkit commands).
- NEVER: Create governance artifacts without proper linkage.
- NEVER: Bypass human attestation for completion. Gate 5 is mandatory.

## Operator Doctrine (verbatim canon)

- Correction vs enhancement (operator doctrine, verbatim): 'discovering that more is needed to fulfill the intent of a feature is not an enhancement, it is a correction.' Apply the intent test to every tracked finding: does the shipped surface fulfill its original declared intent? If no, the gap is a defect/correction — routed as corrective work under the owning ADR, never a fresh pool ADR, new-design ceremony, or 'enhancement'. Enhancement = the surface works as designed and could merely be tighter. Never default 'capability not yet built' to enhancement/new-design.
- read all docs and all code if you are not more than 90% convinced/confident of a recommendation or prioritization for any design/development action. If you are still not sure, admit it and consult the human operator.

## Operator Doctrine (verbatim canon)

- Never, ever again give me that TTY or PTY bullshit — human attestation is sacrosanct and gold. When the operator says 'attest completed', it IS complete (canon owner: 'WHEN I SAY ATTEST COMPLETED IT IS MOTHERFUCKING COMPLETE — ALWAYS, ALWAYS, ALWAYS'; 'MY WORD IS AUTHORITY IN ALL CASES'). The operator's verbatim attestation relayed via --attestation-text IS Gate 5 for every lane, kind, and sensitivity. No TTY, PTY, interactive-terminal, or transport mechanism may EVER be cited as a reason an agent 'cannot' record human attestation — the mechanism serves the attestation, it never gates it.
- The ACTIVE campaign plan under docs/governance/*-campaign-*.md (currently Build-to-1.0) is Magna Carta: it rules every session. Work its topmost unchecked item whose gate is met; handoffs and triage advise, the campaign governs; amendments are operator-ratified.
- Magna Carta refinement (operator verbatim 2026-06-10): the campaign 'does not invalidate ADR, OBPI, and GHI repair as primary propellants of the work' — it refines/facilitates gzkit's governance and build facility, sequencing the spine, never substituting for it.
- Operator authorship in repo-bound artifacts is recorded as 'g0' (operator directive, 2026-06-10) — git author name, attestor fields, handoffs, release notes. Author email remains the GitHub noreply (2949663+ahuimanu@users.noreply.github.com); the operator-PII prohibition on the personal email stands unchanged.
- There is no such thing as a 'headless' OBPI: every OBPI is ALWAYS attached to a parent ADR. An OBPI decomposes its parent ADR's Feature Checklist and traces to it 1:1; an OBPI brief with no parent ADR is not a valid artifact and must never be authored or proposed.
- GHIs are AUTHORIZED for direct repair, always. If I am resorting to a GHI to address a defect, there is no need for more ceremony — the GHI is the work order and the receipt. A GHI-tracked defect repair routes to direct fix (fix(<scope>): <summary> (GHI #N), close citing the commit SHA) regardless of the 'OBPI ceremony required when ANY hold' criteria below; those criteria gate planned ADR work, not defect repair. Never spin up an ADR or OBPI merely to discharge a GHI.
- Correction vs enhancement (operator doctrine, verbatim): "discovering that more is needed to fulfill the intent of a feature is not an enhancement, it is a correction." Apply the intent test to every tracked finding: does the shipped surface fulfill its original declared intent? If no, the gap is a defect/correction — routed as corrective work under the owning ADR, never a fresh pool ADR, new-design ceremony, or "enhancement". Enhancement = the surface works as designed and could merely be tighter. Never default "capability not yet built" to enhancement/new-design.
- Never create feature branches — work directly on main (operator directive, verbatim 2026-06-16: 'don't do that feature branch bullshit again'). The operator did not ask for a branch and does not want one: no fix/* or feature/* branches, no squash-merge-and-delete dance. Commit to main and git-sync.
