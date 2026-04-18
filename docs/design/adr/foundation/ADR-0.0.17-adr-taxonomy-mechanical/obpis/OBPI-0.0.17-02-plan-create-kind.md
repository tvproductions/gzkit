---
id: OBPI-0.0.17-02-plan-create-kind
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.17-02-plan-create-kind: --kind flag on gz plan create

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #2 — "`gz plan create --kind` CLI flag + scaffolder"

**Status:** Draft

## Objective

Add a required `--kind {pool, foundation, feature}` flag to `gz plan create`. No default — operator must choose explicitly. Scaffolder emits matching `kind:` frontmatter (or omits it for pool) and refuses to write a mismatched kind/semver combination.

## Lane

**Heavy** — CLI contract addition.

## Allowed Paths

- `src/gzkit/cli/parser_artifacts.py` (argparse registration)
- `src/gzkit/commands/plan.py` (scaffolder logic)
- `src/gzkit/templates/adr.md` (emit `kind:` field)
- `tests/commands/test_plan.py` (behavior)
- `docs/user/commands/plan.md` or `docs/user/commands/plan-create.md` (help-text update)

## Denied Paths

- Schema/model surfaces (OBPI-01)
- `gz adr promote` surface (OBPI-03)
- `gz validate` surface (OBPI-04)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz plan create --help` shows `--kind {pool, foundation, feature}` as a required flag. Omitting `--kind` exits with code 1 and names both foundation/feature criteria.
2. REQUIREMENT: `--kind foundation` requires `--semver` to match `^0\.0\.\d+$`. Mismatch → exit 1 with a recovery message naming the next available `0.0.x` value (by scanning existing foundation ADRs).
3. REQUIREMENT: `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch → exit 1 with a recovery message explaining feature ADRs carry release-carrying semver (`0.y.z` and up).
4. REQUIREMENT: `--kind pool` writes to `docs/design/adr/pool/ADR-pool.<slug>.md` (no directory-per-ADR, matching existing pool convention). No `kind:` field in frontmatter; no `semver:` required. Pool ADRs are out-of-scope for foundation/feature frontmatter entirely.
5. REQUIREMENT: The rendered ADR frontmatter for foundation/feature includes `kind: <value>` directly after `status:` per the schema ordering. Template variable substitution must not silently drop the field.
6. REQUIREMENT: Scaffolder validates kind/semver BEFORE writing any file. A rejected invocation writes nothing, appends no ledger event, and prints the recovery message to stderr with exit 1.
7. REQUIREMENT: `gz plan create … --kind foundation` routes to `docs/design/adr/foundation/<id>/<id>.md` (create directory if missing); `--kind feature` routes to `docs/design/adr/pre-release/<id>/<id>.md` by default (matching the existing convention for non-foundation ADRs). An explicit `--output <path>` override is out of scope for this OBPI.
8. REQUIREMENT: All prior `gz plan create` behavior (scorecard scoring, parent OBPI, etc.) remains unchanged when `--kind` is supplied. The flag is additive, not replacing any existing argument.

## Verification

```bash
uv run gz plan create --help | grep -- --kind
uv run gz plan create scratch-foundation --kind foundation --semver 0.0.99 --lane lite --dry-run
uv run gz plan create scratch-feature --kind feature --semver 0.99.0 --lane heavy --dry-run
uv run gz plan create scratch-bad --kind feature --semver 0.0.99 --dry-run  # must exit 1
uv run gz plan create scratch-pool --kind pool --dry-run
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_plan -v
```

## Evidence

- Help output showing `--kind` registered
- Dry-run scaffolder output for each kind
- Rejection transcript for mismatched kind/semver
- ARB receipts

## REQ Coverage

- REQ-0.0.17-02-01 through REQ-0.0.17-02-08
