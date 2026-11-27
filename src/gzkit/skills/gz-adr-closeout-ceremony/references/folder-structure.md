# ADR Folder Structure

The ADR root is `artifacts.adr.path` in `.gzkit/manifest.json`: `docs/design/adr` in gzkit, `design/adr` where `gz init` scaffolded it. gzkit's layout record is `docs/design/adr/meta/README.md` § Canonical Layout. The tree is illustrative; the comment on each line names the producer that writes it.

```text
<adr-root>/
  foundation/ADR-0.0.z-{slug}/     # foundation kind
  pre-release/ADR-0.y.z-{slug}/    # feature kind, before 1.0
    ADR-0.y.z-{slug}.md            # Intent document (gz plan create)
    ADR-CLOSEOUT-FORM.md           # Closeout workspace (_closeout_form_path)
    obpis/
      OBPI-0.y.z-01-{slug}.md      # Atomic implementation units (gz specify)
    audit/
      AUDIT_PLAN.md                # Audit plan (gz audit)
      AUDIT.md                     # Post-attestation reconciliation (gz audit)
      proofs/                      # Captured verification output (gz audit)
  pool/
    ADR-pool.{slug}.md             # Proposal only; no OBPIs
```
