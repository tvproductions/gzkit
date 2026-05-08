# gz-validate

Validate governance artifacts and trust-doctrine surfaces against schema rules
and audit invariants.

## NAME

gz-validate — fail-closed structural validation across manifests, ledger,
documents, briefs, personas, and promoted advisory audits. Each scope
returns ``ValidationError`` lists; the CLI exits per the four-code map
(`.gzkit/rules/cli.md`).

## SYNOPSIS

```text
gz validate [--manifest] [--documents] [--surfaces] [--ledger]
            [--instructions] [--briefs] [--personas]
            [--frontmatter [--adr <ID>] [--explain <ADR-ID>]]
            [--taxonomy] [--brief-headings] [--chores-layout]
            [--unscoped-rules [--allowlist-only]]
            [--sensitivity [--explain ALLOWED_PATHS_LIST]]
            [--complexity-doctrine-links] [--complexity-thresholds]
            [--intrinsic-attestation] [--advisor-proof-binding]
            [--evaluation-justify-binding [ARTIFACT_ID]]
            [--attestation-receipts <text|@file>
                [--lane heavy|lite] [--kind foundation|feature]]
            [--audits] [--all] [--json]
```

## DESCRIPTION

`gz validate` is the gate-time fail-closed validator umbrella for governance
artifacts, agent control surfaces, and promoted-advisory audits. With no flag,
it runs the default scopes — `manifest`, `documents`, `surfaces`, `ledger`,
`instructions`, `briefs`, `personas`, `frontmatter`, `version`, and
`taxonomy`. Each opt-in flag activates one additional audit; multiple flags
compose, and `--audits` and `--all` are aggregate roll-ups.

The verb is wired into `gz check` (the pre-merge / Stage-3 verification
runner) so that every promoted scope fires automatically. New flags must
mirror the `gz check` integration; this is enforced by the audit-promotion
discipline at `docs/governance/advisory-rules-audit.md`.

## OPTIONS

The flags below partition into **default** (run when no flag is set), **opt-in**
(run only when explicitly requested), and **scoped attestation** (the
`--attestation-receipts` family).

### Default scopes

- `--manifest` — Validate `.gzkit/manifest.json` against
  `src/gzkit/schemas/manifest.json`.
- `--documents` — Validate every artifact declared in the manifest against
  its schema (ADRs, OBPIs, PRDs, constitutions, personas, etc.).
- `--surfaces` — Enforce canonical/mirror parity for generated control
  surfaces (`.gzkit/skills/` ↔ `.claude/skills/` etc.).
- `--ledger` — Validate `.gzkit/ledger.jsonl` event-by-event against
  `src/gzkit/schemas/ledger.json`.
- `--instructions` — Validate agent rule files under `.gzkit/rules/` and
  vendor mirrors.
- `--briefs` — Validate every OBPI brief against the canonical brief schema.
- `--personas` — Validate every persona file under `.gzkit/personas/`.
- `--frontmatter [--adr <ID>] [--explain <ADR-ID>]` — Reconcile ADR
  frontmatter against ledger truth; `--explain` renders a per-field drift
  diff for one ADR.
- `--taxonomy` — Enforce ADR taxonomy invariants (kind ⇔ semver, no `kind`
  on pool ADRs).

### Opt-in audits (selected — see also the `commands/validate.md` reference)

- `--brief-headings` — Brief evidence sections must use H3 (not H2);
  enforces the canonical heading shape that `gz obpi complete` extracts.
- `--chores-layout` — Validate chore directory layout (`CHORE.md`,
  `INTENT.md`, `proofs/`).
- `--unscoped-rules` — Detect rule files with `paths: "**"` under vendor
  rule dirs (ADR-0.0.20). `--allowlist-only` lists the current allow-list.
- `--sensitivity` — Auto-detect security-sensitivity floor for every brief
  against `data/security_surfaces.json`; escalate-not-escape (ADR-0.0.22).
- `--complexity-doctrine-links` — Link-integrity audit for every cluster
  ADR citation against the current `distilled-characteristics-*.md`
  document (OBPI-0.0.27-07).
- `--complexity-thresholds` — Per-metric threshold table shape audit
  (OBPI-0.0.28-03).
- `--intrinsic-attestation` — `intrinsic-complexity-attestation` ledger
  event shape audit (OBPI-0.0.29-07).
- `--advisor-proof-binding` — Verdict ↔ proof binding audit
  across fixtures, ledger-cited diagnoses, and the JSON Schema; defense-in-depth
  backstop for the model and engine layers (OBPI-0.0.29-08).
- `--evaluation-justify-binding [ARTIFACT_ID]` — Fail-closed gate that
  requires a `gz-justify` artifact for low-scored evaluations (ADR-0.0.26).
- `--attestation-receipts <text|@file> [--lane heavy|lite] [--kind foundation|feature]` —
  Validate ARB receipt citations in an attestation string (ADR-0.0.24).
- `--audits` — Run all four trust-doctrine pattern audits in one pass.
- `--all` — Run every default plus opt-in scope.
- `--json` — Emit results as JSON to stdout; logs to stderr.
- `--help`, `-h` — Show usage and exit 0.

## EXIT CODES

Per `.gzkit/rules/cli.md` four-code map:

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | All scopes clean | — |
| 1 | One or more validation errors outside the policy-breach taxonomy | Inspect the error list and re-author the failing artifact |
| 2 | System / IO error (manifest unreadable, ledger missing, etc.) | Restore the missing surface or fix permissions |
| 3 | Policy breach (frontmatter drift, chores layout, escape attempt) | Fix the policy violation and re-run |

## EXAMPLES

```bash
# Default sweep — no flags
gz validate

# Single scope
gz validate --briefs

# Verdict <-> proof binding audit (OBPI-0.0.29-08)
gz validate --advisor-proof-binding

# Full sweep including all opt-in scopes
gz validate --all

# Reconcile a specific ADR's frontmatter against ledger truth
gz validate --frontmatter --adr ADR-0.0.29

# Validate ARB receipts cited in an attestation string
gz validate --attestation-receipts @path/to/attestation.txt --lane heavy
```

## RELATED

- [`docs/user/commands/validate.md`](../commands/validate.md) — full per-flag
  reference with recovery tables.
- [`docs/governance/advisory-rules-audit.md`](../../governance/advisory-rules-audit.md) —
  promotion-discipline scorecard for every audit fronted by this verb.
- [`docs/user/runbook.md`](../runbook.md) — operator workflow entries that
  cite this verb under their respective doctrine surfaces.
