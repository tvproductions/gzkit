---
id: cli
paths:
  - "src/gzkit/commands/**"
description: CLI contract doctrine and design principles
---

# CLI Contract Doctrine

<!-- rule-version: 0.3.0 -->

> **Rule version:** `0.3.0` — reconciled § Core Principles — Consistency to the
> mechanism it names (GHI #693, operator ruling 2026-07-17: this is a
> *correction*, not an enhancement — the rule's promise WAS the audit's declared
> intent). "The audit is the mechanical check" read as a promise that the
> documented flag contract is verified; the audit mechanized *presence* only, so
> a manpage could contradict its parser and ship green — observed live on
> `gz handoff authorize --session-id`, which documented a required flag as
> optional under a fully green `gz check`. The audit now checks usage-line
> agreement (required-ness, value-taking) and the rule says so. The § Adding CLI
> Features caveat also claimed the audit "audits verbs, not flags", which stopped
> being true at GHI #350; scoped it to the lane claim it was actually making.
> Prior `0.2.0` — resolved a self-contradiction and a release-notes
> conflict (Pass A conflict-matrix rows 17 and 25, run 2026-07-16); adds the
> body-level version marker this file never carried. § Adding CLI Features
> declared "New Flag (Additive = Lite Lane)" while § Heavy Lane Trigger, 65
> lines above, named *flags* explicitly as Heavy — and `AGENTS.md` § Lane
> Rules agrees with the latter. Step 5 prescribed hand-authoring release
> notes, the one artifact `changelog-release-notes.md` forbids hand-editing.
> Prior: unversioned since authoring.

**Baseline:** [clig.dev](https://clig.dev/) — Human-first CLI design principles.
**Mechanical check:** `uv run gz cli audit` (see § Core Principles — Consistency).
**Heavy Lane Trigger:** Any CLI contract change (subcommands, flags, exit codes, output schemas).

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
