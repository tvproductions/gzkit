---
id: cli
paths:
  - "src/gzkit/commands/**"
description: CLI contract doctrine and design principles
---

# CLI Contract Doctrine

<!-- rule-version: 0.6.0 -->

> **Rule version:** `0.6.0` — operator ruling 2026-09-06 carves the GHI direct-repair exception into § Adding CLI Features, which had read as though every contract-bearing CLI change requires OBPI ceremony and so contradicted `AGENTS.md` § Operator Doctrine; `0.5.1` and the superseded `0.5.0`–`0.3.1` chain are lifted to [Rule Version History](../../docs/governance/rule-version-history.md#climd). Scoped `src/gzkit/commands/**`, this rule loads on every CLI-command edit, so narrative is the most expensive thing it can carry.
>
> _Prior `0.5.1`:_ diet pass under GHI #921 (operator ruling 2026-08-30, *"do 3, 4, and 5"*): the superseded `0.5.0`–`0.3.1` version chain is lifted to [Rule Version History](../../docs/governance/rule-version-history.md#climd), restoring the one-sentence shape `skill-surface-sync.md` § Non-negotiable rules #2 requires. Binding rules unchanged; scoped `src/gzkit/commands/**`, this rule loads on every CLI-command edit, so narrative is the most expensive thing it can carry.

**Baseline:** [clig.dev](https://clig.dev/) — Human-first CLI design principles.
**Canonical specification:** [`docs/design/cli-standards-v3.md`](../../docs/design/cli-standards-v3.md) — named canonical by [`ADR-0.0.4`](../../docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md). **Read its § Document status before citing any section:** parts are live-and-met, parts are live-but-UNMET, parts are RETIRED or superseded.
**Mechanical check:** `uv run gz cli audit` (see § Core Principles — Consistency).
**Heavy Lane Trigger:** Any CLI contract change (subcommands, flags, exit codes, output schemas).

---

## Command shape (binding)

Mirrored from the canonical specification's § Command Structure and § Output Rules so the per-turn contract carries them. Scored at `docs/governance/advisory-rules-audit.md` § CLI Contract Doctrine; measurements and per-rule justification in [`docs/design/cli-architecture-analysis.md`](../../docs/design/cli-architecture-analysis.md).

- The count of depth-1 leaf commands may not increase — the specification prescribes `<group> <command>`; 35 of 136 leaves are bare root verbs, so the existing set is waived shrink-only and new commands take a noun.
- No subcommand may share its verb with a bare root command — 13 shadow today (`gz adr status` vs `gz status`, `gz cli audit` vs `gz audit`). Repetition itself is correct: `list` recurs 7× under different nouns and collides with nothing.
- A noun may not be registered in both singular and plural form — exactly one pair today (`gz flag` group vs `gz flags` leaf).
- New root commands may not hyphenate a noun-verb pair — 6 exist (`register-adrs`, `check-config-paths`, `permitted-entry`, `migrate-semver`, `test-shape`, `git-sync`); subcommands are the mechanism the hyphen is standing in for.
- Every leaf command declares --json or carries a waiver with rationale — 63 of 136 lack it, and nine groups disagree with themselves: `gz adr emit-receipt` has none while `gz obpi audit` does, though both emit structured governance evidence.
- A parser node is a leaf or a group, never both — exactly one node violates this (`gz mx` carries a handler and subcommands), so the state is either a deliberate default-subcommand or an accident, and nothing records which.
- Building the gz parser tree may not import handler-only dependencies — every `gz --help` pays what the parser tree imports (GHI #180). Guarded by `tests/cli/test_help_path_imports.py`.
- A new subcommand satisfies all seven coupled obligations in the authoring patch — the set is enumerated at § Adding CLI Features — New Subcommand, and the validators named there win any disagreement with the list. Measured 2026-08-22: three surfaces described the set as 3, 4 and 1 obligations against 7 that fail closed (GHI #854).
- User-facing output passes through the formatter, never console.print directly — 1,230 sites bypass it against one `OutputFormatter`. This is the precondition for the `--json` rule above, not a sibling of it: a `--json` flag on a command whose body prints human text is green while blind.

Two further specification rules are scored **Judgment** and are deliberately absent from this list — mandatory-target-as-positional (no surface models "target"; the available proxy grades by shape) and one-verb noun groups (no surface models intent-to-extend). They live in the canonical specification; see the scorecard for why neither is mechanizable.

---

## Core Principles

| Principle | Rule |
|-----------|------|
| Human-first | Optimize for humans; add `--json`/`--plain` for machines |
| Consistency | Before landing a new flag or subcommand, run `uv run gz cli audit`; it must exit 0, **and the new flag's usage line must agree with its parser** (required-ness and value-taking; GHI #693). For a new subcommand the full obligation set is § Adding CLI Features — New Subcommand; this row does not restate it, because a second partial list is how the two fell out of agreement (GHI #787's class). If coverage is missing, author the missing artifacts in the same patch — the audit is the mechanical check, not operator taste. |
| Discovery | Comprehensive help with examples; no web docs needed |
| Robustness | Validate early; fail fast; provide progress indicators |

---

## Exit Codes (Standard 4-Code Map)

| Code | Meaning | Recovery |
|------|---------|----------|
| **0** | Success | N/A |
| **1** | User/Config Error | Fix invocation or config |
| **2** | System/IO Error | Check network/disk; retry |
| **3** | Policy Breach | Review logs; partial success needs review |

Use `sys.exit(code)`. Document codes 2/3 in help text.

---

## Flag Conventions

| Flag | Behavior |
|------|----------|
| `--quiet` | Errors only |
| `--verbose` | Debug output |
| `--dry-run` | Show plan, don't execute |
| `--json` | Machine-readable to stdout |
| `--help` / `-h` | Always works |

---

## Output Contracts

| Mode | Output |
|------|--------|
| Default | Human-readable (tables, colors, progress) |
| `--json` | Valid JSON to stdout; logs to stderr |
| `--plain` | One record per line (grep-friendly) |

---

## Help Text Requirements

Every command must:

1. Respond to `-h`/`--help` (exit 0)
2. Include description (1-2 sentences)
3. Include usage line
4. List all options
5. Include at least one example
6. Keep lines <=80 chars

---

## Adding CLI Features

**Lane authority is `AGENTS.md` § Gate Covenant — Lane Rules, not this file.** Both a new flag and a new subcommand are CLI-contract changes used by humans, so both are **Heavy**, consistent with this rule's own § Heavy Lane Trigger above (*"Any CLI contract change (subcommands, flags, exit codes, output schemas)"*). `AGENTS.md` § Defect-fix routing adds: *"Adds/changes CLI surface … OBPI ceremony is required"* — so **planned** contract-bearing CLI work runs `gz obpi pipeline`, not a freeform direct fix.

**Lane is not route. A GHI-tracked defect repair routes DIRECT even when it adds a CLI surface** — `AGENTS.md` § Operator Doctrine, verbatim: *"GHIs are AUTHORIZED for direct repair, always… A GHI-tracked defect repair routes to direct fix (`fix(<scope>): <summary> (GHI #N)`, close citing the commit SHA) regardless of the 'OBPI ceremony required when ANY hold' criteria below; those criteria gate planned ADR work, not defect repair. Never spin up an ADR or OBPI merely to discharge a GHI."* Reaffirmed 2026-09-06: *"'may add a CLI surface' alone does not require new ADR/OBPI ceremony: GHI-tracked corrections are authorized for direct repair."* The IRON LAW makes this more than a preference — only the operator initiates OBPI work, so an agent that read the un-carved sentence literally could not proceed by either route. Heavy lane still binds the **gates** the repair must clear (§ New Subcommand's seven obligations, `gz cli audit` exit 0); it never converts the repair into OBPI ceremony.

> `gz cli audit` does **not** adjudicate this. It audits a flag's *documentation* — that the flag is named in its manpage (GHI #350) and that the usage line's required/value-taking claims match the parser (GHI #693) — and exits 0 with full cross-coverage regardless of a new flag's **lane**. Its green is evidence about docs, never about lane assignment. Its green is not evidence of correct lane assignment.

### New Flag (Heavy Lane)

1. Follow naming conventions
2. Check for equivalent in other CLI
3. Update help text with example
4. Manpage flag row in `docs/user/manpages/`

### New Subcommand (Heavy Lane)

**Seven obligations fire for a new verb, and every one is already mechanically checked.** Satisfy them in the authoring patch — they are knowable up front, so discovering them reactively across repeated full-suite runs is a self-inflicted cost, not a property of the gates.

**The authority is the code, never this list.** The enumeration lives in `_SURFACE_NAMES` and `check_surfaces` (`src/gzkit/doc_coverage/scanner.py`), `find_undeclared_commands` (`src/gzkit/doc_coverage/manifest.py`), and `audit_skill_alignment` (`src/gzkit/governance/trust_audits/cli.py`). If this list and those disagree, they are right.

1. **Manifest entry** — `config/doc-coverage.json`. An undeclared command has no declared obligation, so it fails before any surface is examined.
2. **Manpage** — `docs/user/manpages/<slug>.md`, `<slug>` being the command with spaces hyphenated (`gz adr audit-check` → `adr-audit-check.md`). **Never a `gz-` prefix** (`governance-core.md` § Manpage filename references, GHI #532).
3. **Index entry** — the `<slug>.md` filename must appear in `docs/user/manpages/index.md`.
4. **Operator runbook** — a reference in `docs/user/runbook.md`.
5. **Governance runbook** — a reference in `docs/governance/governance_runbook.md`.
6. **Handler docstring** — the resolved handler needs a non-empty docstring. Most often missed, because it is the one obligation that is code rather than a doc file.
7. **Wielding skill** — a `.gzkit/skills/**/SKILL.md` naming the full verb path, or an `_NO_SKILL_VERBS` waiver carrying rationale (tool-skill-runbook Invariant 1).

Alongside these, unchanged: an ADR or brief documenting purpose, help text with examples, a behave smoke test, and the GHI cited in the commit — **do not hand-write release notes.** `RELEASE_NOTES.md` and `CHANGELOG.md` are authored at release time by the `gz-patch-release` ceremony, never by hand (`.gzkit/rules/changelog-release-notes.md` § Release-notes rules).

**A deprecated verb INVERTS obligations 4, 5 and 7:** absence is the passing state, because a runbook that prescribes a retired verb — or a skill that wraps one — routes agents back onto it (GHI #705).

**What this list cannot cover.** These seven are enumerable because they are fixed per verb. They are not the coupled surface of a change that also alters a *format* — a consumer reading a document body, a test asserting against prose, a fixture keyed on a schema shape. `8d9e09a4` is the worked example: relocating the settled-ruling corpus updated every per-verb surface in one commit and still left `test_settled_ruling_integrity` reading a section that had become a pointer, caught by the suite at push time. Front-loading this checklist collapses the reactive loop for **verb registration**; it does not make a **format** change safe, and treating it as though it does would build a false floor.
