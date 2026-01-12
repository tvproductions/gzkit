# Source Documents

These documents are the original sources from AirlineOps that gzkit was extracted from. They are preserved here for reference and lineage tracking.

## Files

| File | Original Location | Description |
|------|-------------------|-------------|
| [RFC-GZKIT-FOUNDATION-airlineops.md](RFC-GZKIT-FOUNDATION-airlineops.md) | `docs/governance/gzkit/RFC-GZKIT-FOUNDATION.md` | Original RFC defining gzkit |
| [govzero-charter-v6-airlineops.md](govzero-charter-v6-airlineops.md) | `docs/governance/GovZero/charter.md` | GovZero Charter v6 |
| [govzero-adr-lifecycle-airlineops.md](govzero-adr-lifecycle-airlineops.md) | `docs/governance/GovZero/adr-lifecycle.md` | ADR lifecycle states |
| [govzero-release-doctrine-airlineops.md](govzero-release-doctrine-airlineops.md) | `docs/governance/GovZero/releases/README.md` | SemVer release doctrine |

## Purpose

These files document the evolution from AirlineOps-specific governance to a generalized toolkit. Key learnings captured:

1. **ADR-0.1.9 anti-pattern** — Don't accumulate 100 OBPIs under one minor version
2. **Gate 3-5 linkage** — Documentation IS the attestation proof
3. **Five Gates model** — Progressive verification catches drift early
4. **Lane doctrine** — Not everything needs Heavy lane ceremony
5. **Human attestation** — Gate 5 cannot be automated

## Status

These are historical reference documents. The authoritative gzkit documentation lives in the parent `docs/` directory:

- [charter.md](../charter.md) — The gzkit covenant (evolved from GovZero Charter)
- [lineage.md](../lineage.md) — Heritage documentation
- [concepts/](../concepts/) — The three concerns explained
