---
id: cli
paths:
  - "src/gzkit/commands/**"
description: CLI contract doctrine and design principles
---

# CLI Contract Doctrine

<!-- rule-version: 0.4.0 -->

> **Rule version:** `0.4.0` — GHI #810: links the canonical specification, and adds § Command shape so this file can be scored for real. This rule declared clig.dev as its baseline while the 1,037-line specification elaborating it — `docs/design/cli-standards-v3.md`, named canonical by ADR-0.0.4 (Validated, foundation, heavy) — was cited by that ADR and by **no rule or governance surface**, so the per-turn contract never reached it. Meanwhile this file sat in `data/advisory_scorecard_grandfather.json` pinned at `0.3.1` — pre-ledger debt, never scored. The two facts compound: measured 2026-08-16, every CLI rule with a mechanical arm holds at or near 100% (exit codes, epilogs, manpage coverage, skill alignment) and every rule that is prose only sits at or near 0% (`--json` 73/136, formatter chokepoint 1,230 bypasses, structlog 1 `get_logger`, `--log-file` absent). This edit drops the pin by construction, which per `docs/governance/advisory-rules-audit.md` compels the scoring pass. Prior `0.3.1` — reconciled § Core Principles — Consistency to the mechanism it names, so the audit checks usage-line agreement (`0.3.0`, GHI #693); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#climd).

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
- User-facing output passes through the formatter, never console.print directly — 1,230 sites bypass it against one `OutputFormatter`. This is the precondition for the `--json` rule above, not a sibling of it: a `--json` flag on a command whose body prints human text is green while blind.

Two further specification rules are scored **Judgment** and are deliberately absent from this list — mandatory-target-as-positional (no surface models "target"; the available proxy grades by shape) and one-verb noun groups (no surface models intent-to-extend). They live in the canonical specification; see the scorecard for why neither is mechanizable.

---

## Core Principles

| Principle | Rule |
|-----------|------|
| Human-first | Optimize for humans; add `--json`/`--plain` for machines |
| Consistency | Before landing a new flag or subcommand, run `uv run gz cli audit`; it must exit 0 with the new verb covered across manpage, command doc, and index, **and the new flag's usage line agreeing with its parser** (required-ness and value-taking; GHI #693). If coverage is missing, author the missing artifacts in the same patch — the audit is the mechanical check, not operator taste. |
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

**Lane authority is `AGENTS.md` § Gate Covenant — Lane Rules, not this file.** Both a new flag and a new subcommand are CLI-contract changes used by humans, so both are **Heavy**, consistent with this rule's own § Heavy Lane Trigger above (*"Any CLI contract change (subcommands, flags, exit codes, output schemas)"*). `AGENTS.md` § Defect-fix routing adds: *"Adds/changes CLI surface … OBPI ceremony is required"* — so contract-bearing CLI work runs `gz obpi pipeline`, not a freeform direct fix.

> `gz cli audit` does **not** adjudicate this. It audits a flag's *documentation* — that the flag is named in its manpage (GHI #350) and that the usage line's required/value-taking claims match the parser (GHI #693) — and exits 0 with full cross-coverage regardless of a new flag's **lane**. Its green is evidence about docs, never about lane assignment. Its green is not evidence of correct lane assignment.

### New Flag (Heavy Lane)

1. Follow naming conventions
2. Check for equivalent in other CLI
3. Update help text with example
4. Manpage flag row in `docs/user/manpages/`

### New Subcommand (Heavy Lane)

1. ADR or brief documenting purpose
2. Help text with examples
3. Behave smoke test
4. Manpage in `docs/user/manpages/`
5. GHI cited in the commit — **do not hand-write release notes.** `RELEASE_NOTES.md` and `CHANGELOG.md` are authored at release time by the `gz-patch-release` ceremony, never by hand (`.gzkit/rules/changelog-release-notes.md` § Release-notes rules).
