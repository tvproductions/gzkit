# ADR Folder Structure

The ADR root is `paths.adrs` in `.gzkit.json`, which the ADR writers read: `docs/design/adr` in gzkit, `design/adr` by default where `gz init` scaffolded it. gzkit's layout record is `docs/design/adr/meta/README.md` § Canonical Layout. The tree is illustrative; the comment on each line names the producer that writes it.

```text
<adr-root>/
  foundation/ADR-0.0.z-{slug}/     # gz plan create --kind foundation
  pre-release/ADR-0.y.z-{slug}/    # gz plan create --kind feature
    ADR-0.y.z-{slug}.md            # gz plan create (intent document)
    ADR-CLOSEOUT-FORM.md           # _closeout_form_path (closeout workspace)
    obpis/                         # gz specify
      OBPI-0.y.z-01-{slug}.md      # gz specify (atomic implementation units)
    audit/                         # gz audit
      AUDIT_PLAN.md                # gz audit (audit plan)
      AUDIT.md                     # gz audit (post-attestation reconciliation)
      proofs/                      # gz audit (captured verification output)
  pool/                            # gz plan create --kind pool
    ADR-pool.{slug}.md             # gz plan create --kind pool (proposal only)
```
