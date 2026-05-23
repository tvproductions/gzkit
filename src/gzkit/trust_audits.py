"""Public facade for taxonomy trust audits.

Audit record (ADR-0.0.57 OBPI-01, 2026-05-23):
  Line-by-line audit of the taxonomy validator for sequence-position assumptions.
  Finding: ZERO sequence-position assumptions. The validator enforces format and
  kind coherence (0.0.x pattern, kind: foundation/feature, pool id-prefix) only.
  No max-N computation, consecutive-integer check, or gap-detection logic exists.
  Foundation trees with sparse IDs (e.g. 0.0.54, 0.0.56) return no taxonomy errors.
  The canonical implementation is at gzkit.governance.trust_audits.taxonomy.

Re-exports the public audit API for stable import path.
"""

from gzkit.governance.trust_audits.taxonomy import (
    audit_adr_status_fresh,
    audit_adr_taxonomy,
    audit_pool_adr_isolation,
)

__all__ = [
    "audit_adr_taxonomy",
    "audit_adr_status_fresh",
    "audit_pool_adr_isolation",
]
