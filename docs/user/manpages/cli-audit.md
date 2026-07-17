# gz cli audit

Audit CLI command documentation coverage and headings.

---

## Usage

```bash
gz cli audit [--json]
```

---

## What It Checks

- Required command manpages exist under `docs/user/manpages/`
- Each page heading matches the command surface (`# gz ...`)
- `docs/user/manpages/index.md` links to each required page
- `README.md` Quick Start command examples parse against the live CLI

### Cross-Coverage (AST-driven)

Discovers all CLI commands by parsing `cli/main.py` and verifies five documentation
surfaces per command:

| Surface | Verification |
|---------|-------------|
| Manpage | `docs/user/manpages/<slug>.md` exists |
| Index entry | Listed in `docs/user/manpages/index.md` |
| Operator runbook | Referenced in `docs/user/runbook.md` |
| Governance runbook | Referenced in `docs/governance/governance_runbook.md` |
| Docstring | Handler function has non-empty docstring |

Also detects orphaned documentation referencing removed commands.

### Per-flag coverage: presence AND truth

Command-grained checks never see a flag, so the audit also walks every
`add_argument` call and checks its manpage two ways:

| Check | Assertion | Origin |
|-------|-----------|--------|
| Presence | The long flag is named somewhere in its command's manpage | GHI #350 |
| Truth | The manpage's **usage line** agrees with the parser: a `required=True` flag is not bracketed `[--flag]`, and an `action="store_true"` flag is not shown taking a value | GHI #693 |

Presence alone is not enough: a doc that *mentions* every flag while *lying*
about one passes the presence half and is believed. A missing row fails loudly;
a wrong row ships green — `gz handoff authorize` documented a required
`--session-id` as optional under a fully green `gz check` (2026-07-16).

The truth check reads only the fenced block under `## Usage` / `## Synopsis` —
the region that *declares* the contract. Prose elsewhere may discuss or quote a
bracket form without claiming it. It checks only what argparse can adjudicate
without inference (required-ness, value-taking); stated defaults and env
fallbacks are prose (`"defaults to the current branch"` is true with an argparse
default of `None`), and grading prose produces the false positives that keep a
check from being trusted.

---

## Example

```bash
uv run gz cli audit
```

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
