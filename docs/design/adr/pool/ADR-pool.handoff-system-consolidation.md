---
id: ADR-pool.handoff-system-consolidation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.handoff-system-consolidation: Handoff System Consolidation and CLI Surface

## Status

Pool

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

## Alternatives Considered

1. **Leave the union-scan partial fix as the terminal state.** Rejected: it
   masks the doctrine conflict (both locations keep accumulating handoffs) and
   leaves the vaporware API and missing CLI verb unaddressed — handoffs stay
   hand-authored and bypass validation.
2. **Delete the skill's programmatic-API documentation, keep hand-authoring.**
   Rejected: hand-authoring is exactly what shipped two invalid-frontmatter
   handoffs this session; removing the API removes the validation gate's only
   mechanical entry point.
3. **Make `{ADR-package}/handoffs/` canonical and deprecate `.gzkit/handoffs/`.**
   Viable but conflicts with token-block doctrine (OBPI-0.0.41-03) which couples
   lock-release register entries to `.gzkit/handoffs/`; would require amending
   that rule. A real candidate for the design pass, not a foregone conclusion.
4. **Make `.gzkit/handoffs/` canonical and change the skill to write there.**
   Viable but loses ADR-package co-location (handoffs no longer travel with the
   ADR they describe). Also a real candidate.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

**Kind at promotion:** likely `foundation` — the canonical-location decision
shapes a system invariant (where the audit-bearing register entries live) and
the token-block coupling is foundation doctrine. The CLI verb + API are the
adapter layer atop that invariant.

**Provisional OBPI promotion plan** (refine at promotion):

- OBPI-01 — resolve + canonize the single write location; amend the losing
  surface (token-block rule or skill) so doctrine is consistent.
- OBPI-02 — implement `create_handoff`/`scaffold_handoff`/`list_handoffs`/
  `resume_handoff`/`load_handoff_chain` in `src/gzkit/`, wrapping
  `handoff_validation.py`; migrate the skill's documented API references.
- OBPI-03 — `gz handoff` CLI verb (create/resume/list) with manpage + behave.
- OBPI-04 — align `scripts/session_orientation.py` with the canonical location;
  collapse or keep the union scan accordingly.

**Evidence base:** GHI #529 (this ADR's source); partial repair commit
`2ab33914`; sibling cleanup GHI #565 (brief Verification compound commands) is
unrelated to handoffs but was filed in the same audit session.
