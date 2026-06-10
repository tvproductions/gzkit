# Plan — OBPI-0.0.69-01-support-channel-ledger-and-validator-dispatch

**OBPI:** OBPI-0.0.69-01 (`OBPI-0.0.69-01-support-channel-ledger-and-validator-dispatch`)
**Parent ADR:** ADR-0.0.69-channels-first-closeout-proof (foundation / heavy)
**Closes:** GHI #543
**Authored:** 2026-06-10 (pipeline Stage 1, post plan-audit-gate)

## Context

The SUPPORT proof channel is fake today: `compute_three_channel_coverage`
(`src/gzkit/req_kind.py:218`) hardcodes `proof_status = "advisory-support"` for
every SUPPORT REQ — the docstring at line 182 declares "ledger query deferred" —
and `_check_support_req` (`src/gzkit/commands/validate_req_kind.py:70-92`) does
keyword-presence checks (`"gz validate --"` substring + a ledger keyword) with no
ledger query and no validator dispatch. The channel constant is named
`LEDGER_PLUS_VALIDATOR` (`req_kind.py:35`); the name promises both, the code
delivers neither (#543).

**Module-home divergence (brief caveat clause invoked):** the brief's Allowed
Paths bullet locates `_check_support_req` inside `src/gzkit/req_kind.py`; its
real home is `src/gzkit/commands/validate_req_kind.py` (A3 module split). The
brief's own caveat — "if a refactor has moved it, locate the real home before
editing and note the divergence" — authorizes editing the real home. Noted here
and to be repeated in Stage 4 evidence.

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

Before authoring this plan I had formed: "add a real SUPPORT resolver in
req_kind.py; thread project_root into the coverage computation; keep
authoring-time `--req-kind-discipline` citation-shaped." Rejected alternatives:

1. **Hard-verify inside `_check_support_req` (authoring-time fail-close on
   missing evidence).** Rejected: `--req-kind-discipline` runs inside `gz check`
   over ALL briefs, including freshly authored Draft briefs whose cited
   `artifact_edited` events legitimately do not exist yet. Authoring-time
   fail-close would turn `main` red repo-wide on every new brief — the exact
   class of red the parent ADR exists to subtract, and it would bypass the
   operator's 19-brief pre-audit ruling (which protects the *closeout* gate,
   OBPI-03). The ADR's Decision scopes fail-close to *in-closeout* ADRs via
   `--closeout-proof`.
2. **Subprocess dispatch (`uv run gz validate --<scope>` via subprocess).**
   Rejected: in-process scope dispatch through the existing validate-scope
   registry is the local precedent, avoids ~2s interpreter spawn per REQ, and
   is what ruling 6.1-A's per-run memoization (OBPI-03) can wrap.
3. **Resolve SUPPORT proof lazily in OBPI-03 only (leave req_kind.py
   untouched).** Rejected: the ADR's Decision item (1) and this brief's
   Requirement 1 place the real resolver in the SUPPORT branch itself; OBPI-03
   consumes the computed `proof_status`, it does not compute it.

## Files (brief allowlist + caveat-resolved real home)

- `src/gzkit/req_kind.py` — SUPPORT resolver + coverage wiring (allowlisted)
- `src/gzkit/commands/validate_req_kind.py` — `_check_support_req` upgrade
  (real home of the allowlisted symbol, per brief caveat clause)
- `tests/test_req_kind_support_channel.py` (new) — fail-close regression tests
- `docs/user/manpages/validate.md` — SUPPORT-channel proof semantics (allowlisted)
- Brief + parent ADR — read-only reference / evidence updates (allowlisted)

Denied (untouched): STRUCTURAL-FENCE arm, `--closeout-proof` view
(`trust_audits/closeout_proof.py` does not exist yet — OBPI-03), `ln:` surface,
deps/lockfiles/CI.

## Steps

1. **Discovery (read-only).** Quote parent ADR § Decision item (1) verbatim
   (brief Discovery Checklist, order pinned). Read `req_kind.py` whole,
   `_check_support_req`, the validate-scope dispatch registry in
   `src/gzkit/commands/validate_cmd.py` (how a `--<scope>` string maps to a
   scope function, for in-process dispatch), and the ledger read pattern
   (`gzkit.events` / existing ledger-query helpers). Read existing req_kind
   tests for fixture shape.
2. **RED.** New `tests/test_req_kind_support_channel.py` deriving from the
   brief's REQs (semantics, not strings):
   - REQ-0.0.69-01-01: cited ledger event present in a fixture ledger AND cited
     validator scope dispatches exit 0 → `proof_status == "pass"` (and NOT
     `advisory-support`). `@covers("REQ-0.0.69-01-01")`
   - REQ-0.0.69-01-02: cited event absent → unproven/fail status (fail-close),
     never `advisory-support`. `@covers("REQ-0.0.69-01-02")`
   - REQ-0.0.69-01-03: cited validator dispatch non-zero → unproven/fail
     (fail-close). `@covers("REQ-0.0.69-01-03")`
   - Citation missing/unparseable on a SUPPORT REQ → violation (ValidationError
     from `_check_support_req`), never a pass (brief Requirement 2, second
     sentence).
   Run, observe RED.
3. **GREEN — resolver.** In `src/gzkit/req_kind.py`: add a SUPPORT citation
   parser (extract cited ledger-event type(s) and cited `--<scope>` from the
   REQ text) and `resolve_support_proof(...)`: query the project ledger for a
   matching event AND dispatch the cited validator scope in-process; both hold
   → `"pass"`; either fails → unproven status (fail-close). Guard: a scope that
   would re-enter req-kind/closeout-proof resolution is not dispatched
   (recursion fence) and resolves unproven with a named reason.
4. **GREEN — wiring.** `compute_three_channel_coverage` gains an optional
   `project_root: Path | None = None` parameter: when provided, the SUPPORT
   branch resolves via `resolve_support_proof` (real status); when omitted
   (legacy callers, no ledger access), behavior is unchanged. Update the
   docstring at lines 179-184 — "ledger query deferred" is no longer true.
   `_check_support_req` upgrades from keyword-presence to parse-based citation
   validation using the same parser (unparseable citation → violation), keeping
   `--req-kind-discipline` authoring-time citation-shaped (see disclosure #1).
5. **Docs.** `docs/user/manpages/validate.md`: document SUPPORT-channel proof
   semantics — cited ledger event found AND cited validator exit 0; fail-close
   on either miss; authoring-time vs closeout-time split.
6. **Verify** (brief Verification section + Heavy lane): `uv run gz lint`,
   `uv run gz typecheck`, `uv run gz test`, `uv run gz validate --documents`,
   `uv run mkdocs build --strict`, `uv run gz cli audit`, covers parity
   `uv run gz covers OBPI-0.0.69-01-support-channel-ledger-and-validator-dispatch --json`.

## Verification commands (from the brief)

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
```

## Notes

- REQ-0.0.69-01-04 [support] (manpage) proves via `artifact_edited` ledger
  event + `gz validate --documents` + `mkdocs build --strict` — no @covers test.
- No new runtime dependencies (stdlib + existing surfaces only).
- TASK subdivision call happens at Stage 2 per REQ; coarse `seq=01` default
  unless labor genuinely subdivides.
