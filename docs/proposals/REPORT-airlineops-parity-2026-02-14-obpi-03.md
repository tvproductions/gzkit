# REPORT: AirlineOps Parity Scan (OBPI-0.3.0-03 Closure)

## Metadata

- Date: 2026-02-14
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Scope: `OBPI-0.3.0-03-govzero-canonical-doc-surface`

---

## Executive Summary

- Overall status for OBPI-03 scope: **Closed**
- Finding F-003 (missing canonical GovZero doc-surface): **Resolved in gzkit**
- Remaining ADR-0.3.0 work: OBPI-0.3.0-04 and OBPI-0.3.0-05

---

## Canonical Coverage Matrix (GovZero Doc Surface)

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status | Severity | Evidence |
|---|---|---|---|---|
| `docs/governance/GovZero/**/*.md` (recursive) | `docs/governance/GovZero/**/*.md` | Parity | P1 -> Closed | Recursive path set diff = 0 |
| Canonical markdown file bodies | Mirrored markdown file bodies | Parity | P1 -> Closed | Byte compare mismatches = 0 |
| Canonical GovZero docs published in site nav | `mkdocs.yml` `Governance (Canonical)` section | Parity | P2 -> Closed | `uv run mkdocs build --strict` PASS |

---

## Evidence

### Path-Level Recursive Parity

```bash
(cd /Users/jeff/Documents/Code/airlineops/docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
(cd docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
comm -3 <(cd /Users/jeff/Documents/Code/airlineops/docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort) <(cd docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
```

Observed:
- Canonical count: 22 markdown files
- gzkit count: 22 markdown files
- `comm -3` output: empty

### Byte-Level Parity

```bash
while IFS= read -r rel; do
  cmp -s "/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/$rel" "docs/governance/GovZero/$rel" || echo "mismatch:$rel"
done < <(cd /Users/jeff/Documents/Code/airlineops/docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
```

Observed:
- Content mismatches: 0

### Build + Validation

```bash
uv run mkdocs build --strict
uv run gz validate --documents
```

Observed:
- Both commands pass in gzkit after docs surface/nav updates.

---

## Findings Status

### F-003 (from prior parity reports): Missing canonical GovZero docs surface

- Prior status: Missing (P1)
- Current status: **Resolved in gzkit**
- Closure evidence:
  - `docs/governance/GovZero/**` recursive markdown mirror present
  - Byte-for-byte parity verified
  - Canonical docs published in navigation and strict docs build passes

---

## Required Next Actions

1. Execute `OBPI-0.3.0-04-core-semantics-reconciliation` to align overlays and runtime-semantic presentation with canonical doctrine.
2. Execute `OBPI-0.3.0-05-parity-scan-path-hardening` to make parity scan canonical-root resolution deterministic across execution contexts.
3. Re-run `uv run gz adr audit-check ADR-0.3.0` after OBPI-04/05 close.
