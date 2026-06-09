---
id: ADR-0.0.67-tool-skill-invariant1-enforcement
status: Draft
kind: foundation
semver: 0.0.67
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-07
---

# ADR-0.0.67-tool-skill-invariant1-enforcement: Complete tool-skill Invariant 1 enforcement and reclaim orphaned CLI verbs

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
Treats governance not as overhead but as the discipline that keeps work honest.
The operative stance for this ADR: **compliance by coverage, not exemption** — a
waiver that silences a defect signal is the anti-vibe failure this ADR exists to
remove.

## Why foundation tier?

Without mechanically-complete enforcement of tool→skill Invariant 1, gzkit's
control surface rots silently — live CLI verbs accumulate with no skill wielding
them, and the "orphan tool = dead code or hidden drift = defect signal" guarantee
becomes a guarantee in name only. gzkit's identity **is** governance integrity /
anti-vibe enforcement; a binding invariant whose enforcement under-covers its own
stated scope is an integrity hole at the core. Yes — without this, the project is
not the project.

Port-vs-adapter: this ADR is a **port**. "Every registered CLI verb is wielded by
a skill or it is a defect" is an abstract contract every CLI surface must honor;
the specific verb→skill wirings are adapters behind it. The enforcement mechanism
(recursive enumeration + fail-close) is the port; this ADR closes the port that
GHI #202 left half-open (top-level verbs only).

## Intent

`audit_skill_alignment` (the mechanical enforcer of tool-skill-runbook-alignment
Invariant 1, landed under GHI #202) enumerated **only top-level subparser
choices** — `_known_cli_verbs()` never recursed into nested subparsers
(`src/gzkit/governance/trust_audits/cli.py:125-136`). Consequence: **32 multi-word
subcommands** (`gz obpi complete`, `gz adr status`, `gz task block`, …) were
structurally invisible to the orphan check and passed `gz validate
--skill-alignment` green **by invisibility, not by a wielding skill or an attested
waiver.** The binding invariant says "Every CLI verb"; the enforcement covered a
strict subset. Rule-as-enforced ⊊ rule-as-written.

A fresh audit of the 107-command surface found **36 orphans**: 4 top-level (all
legitimately waived in `_NO_SKILL_VERBS`) + 32 multi-word (structurally
unscanned). Of the 32, most are wielded under group waivers; **13** had no skill
and a non-waived group. Two of those 13 — `obpi audit` and `obpi withdraw` —
turned out to be **capable, fully-integrated tools left unwired**: power on the
floor.

## Decision

1. **Recursive enumeration (the port).** Add `_known_cli_verb_paths()` that walks
   the full argparse tree and returns space-joined leaf paths
   (`"adr status"`, `"obpi lock claim"`). `audit_skill_alignment` enforces against
   this full surface. `_NO_SKILL_VERBS` gains group-prefix cascade + multi-word
   key support; the stale-waiver check is rewritten to match leaf paths/prefixes.
   `_known_cli_verbs()` (top-level) is left untouched so `audit_cli_alignment`'s
   behavior is unchanged (coupled-surface coherence). **Status: already
   implemented** in the working tree (`cli.py` + regression test
   `tests/governance/test_promoted_advisory_audits.py::test_skill_alignment_enumerates_multiword_subcommands`).

2. **MAXX full compliance — wire, do not waive.** The 10 live orphan verbs are
   genuinely wielded by skills, with zero new `_NO_SKILL_VERBS` entries:

   | Verb | Home skill | Handler (receipt) | Note |
   |------|-----------|-------------------|------|
   | `obpi audit` | gz-obpi-reconcile (Phase 1) | `obpi_audit_cmd` (`obpi_audit_cmd.py:13`) | **headline** — deterministic engine replaces ad-hoc agent audit |
   | `obpi withdraw` | gz-obpi-reconcile (phantom remediation) | `obpi_withdraw_cmd` (`obpi_cmd.py:59`) | ledger-integrated (`ledger.py:670`, `state.py:86`); serves GHI #584 |
   | `obpi emit-receipt` | gz-obpi-reconcile (receipt step) | `obpi_emit_receipt_cmd` (`parser_artifacts.py:1024`) | distinct `--event validated` path |
   | `obpi status` | gz-status | `obpi_status_cmd` (`parser_artifacts.py:1048`) | focused single-OBPI runtime view |
   | `adr demote` | gz-adr-promote (bidirectional) | `adr_demote_cmd` (`parser_artifacts.py:812`) | inverse of promote |
   | `adr covers-check` | gz-adr-sync | `adr_covers_check` (`parser_artifacts.py:915`) | sync already discovers @covers |
   | `arb ty` | gz-arb | `arb_ty_cmd` (`parser_arb.py:142`) | raw `uvx ty` passthrough; **not** an alias of `arb typecheck` |
   | `chores propose-ghi` | gz-chore-runner | `chores_propose_ghi` (`parser_maintenance.py:1086`) | chore→GHI output step |
   | `skill list` | gz-skill-router | `skill_list` (`skills_cmd`) | catalog discovery |
   | `skill new` | gz-skill-router | `skill_new` (`skills_cmd`) | skill scaffolding |

   Wiring MUST be genuine procedural use (the verb invoked in the skill's body /
   `gz_command`), not a name-drop. Each target skill is read before edit; each
   edit bumps `skill-version` + `last_reviewed` and is followed by
   `gz agent sync control-surfaces`.

3. **Delete the 3 deprecated aliases.** `obpi lock-claim`, `obpi lock-release`,
   `obpi lock-status` are author-declared deprecated flat aliases
   (`parser_artifacts.py:1454`: "OBPI-03 will remove these after skill
   migration") dispatching to the **same handlers** as the canonical space forms
   (`lock claim/release/list`). The skill migration is complete (gz-obpi-lock
   wields the space forms). Execute the unlanded cleanup: remove the parser
   registrations + 3 manpages + `doc-coverage.json` entries + `mkdocs.yml` nav +
   the behave scenario `features/obpi_lock.feature:65` ("Deprecated lock-claim
   alias works"), keeping `gz cli audit` and `mkdocs build --strict` green.

## Consequences

### Positive

- Invariant 1 is enforced across the **full** CLI surface; no escape hatch by
  invisibility. New multi-word verbs without a skill now fail `gz validate
  --skill-alignment` (and `gz check`).
- **Determinism reclaimed:** gz-obpi-reconcile Phase 1 stops hand-rolling tests/
  coverage/@covers/ledger via ad-hoc agent steps and calls the deterministic
  `gz obpi audit` verb whose ledger schema the skill already documents
  (`gz-obpi-reconcile/SKILL.md:375-399`). Anti-vibe at the surface that needed it.
- **Reclaimed capability:** `gz obpi withdraw` (already wired end-to-end into the
  ledger graph + state counts) gains a skill home, giving reconcile teeth to
  remediate the 233 phantom `obpi_created` events of GHI #584.
- The deprecated lock aliases — dead weight the source itself marked for removal —
  are gone; the CLI surface stops lying about what it supports.

### Negative

- Heavy-lane **CLI-contract change** (verb removal): `obpi lock-claim/-release/
  -status` cease to exist. Re-adding is cheap, but it is a contract change and a
  ~one-way door — the deletions warrant the most evidence.
- Touches **6 sync'd skills** (canonical + 3 mirrors each via
  `gz agent sync control-surfaces`); each carries version-bump discipline.
- Risk: if `obpi audit`'s output subtly diverges from what reconcile Phase 1
  needs, wiring it silently degrades audits. **Mitigated** — schema match verified
  field-by-field (`obpi_audit_cmd._build_entry` ↔ skill Ledger Schema v1).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.67-01: Recursive verb-path enumeration + group-cascade waivers so `audit_skill_alignment` enforces Invariant 1 across multi-word subcommands (foundation port) — **implemented in working tree; brief ratifies it**
- [ ] OBPI-0.0.67-02: Wire the 10 live orphan verbs into 6 skills (no waivers) and add test coverage for `obpi audit` / `obpi withdraw`
- [ ] OBPI-0.0.67-03: Delete the 3 deprecated `obpi lock-*` hyphen aliases and their doc cascade (parser, manpages, doc-coverage, mkdocs nav, behave scenario)

## Q&A Transcript

<!-- Interview transcript preserved for context. Design dialogue conducted in session 2026-06-07; answers ratified by operator (kind: foundation). -->

**Problem:** see § Intent. Top-level-only enumeration left 32 multi-word verbs unenforced; 13 true orphans, 2 of them capable-but-unwired tools.

**Decision:** see § Decision. Recurse → wire-not-waive (MAXX) → delete deprecated.

**Alternatives:** see § Alternatives Considered.

**Forcing functions (load-bearing):**
- *Pre-mortem (how this fails):* "wiring" degrades into box-ticking — a skill names a verb without using it → orphan-in-disguise. Guard: each wiring is genuine procedural use, verified, not a name-drop.
- *Reversibility:* alias deletion is ~one-way (contract change) → most evidence; wirings are two-way (cheap revert).
- *Scope-min (half the time):* recursion + `obpi audit→reconcile` + deletions are the essential core; the other 8 wirings are completeness.
- *2am operator:* `gz obpi audit OBPI-x` must remain runnable standalone for diagnosis when reconcile is broken (it is).
- *Closing — downstream decisions forced:* Phase 2 — sweep the existing 24 single-token `_NO_SKILL_VERBS` waivers (some look stale, e.g. `init` vs gz-init's `gz_command: init`); possibly a dedicated skill-authoring skill for `skill new`.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_promoted_advisory_audits.py` (Invariant-1 enumeration + clean), new coverage for `obpi audit`/`obpi withdraw`
- [ ] Docs: manpage deletions; `gz-obpi-reconcile`, `gz-status`, `gz-adr-promote`, `gz-adr-sync`, `gz-arb`, `gz-chore-runner`, `gz-skill-router` SKILL.md edits
- [ ] `uv run gz validate --skill-alignment` green with zero new waivers for the 13
- [ ] `uv run gz cli audit` + `uv run mkdocs build --strict` green after deletions
- [ ] GHI #588 (anchor)

## Alternatives Considered

1. **Waive the orphans** (extend `_NO_SKILL_VERBS`). **Rejected** — uses the
   exemption mechanism to silence the exact signal the invariant raises; the
   anti-vibe / "graceful-degradation exit" failure. This was the agent's first
   pass; the operator correctly flagged it as vibe.
2. **Top-level-only enforcement (status quo).** **Rejected** — leaves every
   multi-word subcommand permanently blind; the defect persists and grows.
3. **Delete all orphans.** **Rejected** — most of the 13 are live and integrated
   (`obpi status`, `adr demote`, `chores propose-ghi`, `skill list/new` are tested
   and used); only the 3 self-declared deprecated aliases are deletion candidates.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.67 | Completed | Jeffry | 2026-06-09 | Completed |
