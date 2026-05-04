---
id: ADR-pool.attestation-quality-measurement
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-0.0.27
inspired_by: ADR-0.0.27
---

# ADR-pool.attestation-quality-measurement: Attestation Quality Measurement

## Status

Pool

## Date

2026-05-04

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Codify how gzkit measures whether its Gate 5 attestation ceremony is producing high-signal operator witness or degenerating into rubber-stamping. ADR-0.0.27 named foundation-kind brief-level attestation as the structural defense against agent-only-authored doctrine, but every ceremony repetition is a chance for attestation fatigue to erode the signal. This ADR-pool entry holds the forward-reference for the empirical measurement of that signal — operator decision-time distributions per ceremony, attestation-text richness over time, rejection rates per OBPI bucket — and the trigger conditions that would activate the work (WWHTBT-rejected condition #4 from the ADR-0.0.27 design dialogue: attestation fatigue empirically materializing across the four-ADR complexity-doctrine cluster).

Booked at OBPI-0.0.27-02 as a forward-reference in the citation graph. Activates if attestation-quality erosion is observed in ledger metrics across recurring foundation-kind ceremonies.
