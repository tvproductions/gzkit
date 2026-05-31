"""Attestation-verdict classifier contract + single-source guard (BI-2).

The verdict ``(status, reason)`` derived from a ceremony attestation string is
the single input to BOTH:

* the ceremony's Step-6 ``attested`` ledger event status
  (``closeout_ceremony`` → ``attested_event(adr_id, status, ...)``), and
* the closeout pipeline's lifecycle ``to_state`` transition
  (``closeout._consume_ceremony_attestation``).

The ADR-0.0.63 Gate-5 audit (2026-05-30) flagged a latent DRY fork: the closeout
pipeline carried its own byte-identical copy of the classifier
(``closeout._parse_ceremony_attestation_text``) alongside the ceremony emitter's
``ceremony_state._classify_attestation_verdict``. Byte-identical then, but a
future edit to one body could silently diverge ``attested.status`` from
``lifecycle_transition.to_state`` — an incoherent ledger.

These tests lock (1) the verdict contract both surfaces depend on, and (2) the
single-source property: closeout routes through the one shared classifier rather
than a private duplicate.
"""

import unittest

from gzkit.commands.ceremony_state import _classify_attestation_verdict


class TestAttestationVerdictContract(unittest.TestCase):
    """The ``(status, reason)`` mapping both attestation surfaces depend on."""

    def test_completed_when_no_terminal_keyword(self) -> None:
        for text in (
            "Completed",
            "attest completed - all gates green",
            "LGTM, ship it",
        ):
            with self.subTest(text=text):
                self.assertEqual(_classify_attestation_verdict(text), ("completed", None))

    def test_dropped_keyword_yields_dropped_with_verbatim_reason(self) -> None:
        text = "Dropped - design pivot rendered ADR moot"
        self.assertEqual(_classify_attestation_verdict(text), ("dropped", text))

    def test_partial_keyword_yields_partial_with_verbatim_reason(self) -> None:
        text = "Completed - Partial: REQ-04 deferred to follow-up brief"
        self.assertEqual(_classify_attestation_verdict(text), ("partial", text))

    def test_keyword_matching_is_case_insensitive(self) -> None:
        self.assertEqual(_classify_attestation_verdict("DROPPED — moot")[0], "dropped")
        self.assertEqual(_classify_attestation_verdict("Partial coverage only")[0], "partial")

    def test_reason_is_stripped_but_otherwise_verbatim(self) -> None:
        status, reason = _classify_attestation_verdict("  Dropped - boundary spaces  ")
        self.assertEqual(status, "dropped")
        self.assertEqual(reason, "Dropped - boundary spaces")

    def test_dropped_takes_precedence_over_partial(self) -> None:
        # Both keywords in window: 'dropped' is checked first, so a dropped
        # ceremony whose reason mentions partial work still classifies dropped.
        text = "Dropped - superseded; partial work discarded"
        self.assertEqual(_classify_attestation_verdict(text)[0], "dropped")

    def test_keyword_beyond_leading_window_is_ignored(self) -> None:
        # Only the leading 120 chars are inspected; a terminal keyword buried
        # past that window must not flip an otherwise-completed verdict.
        text = "Completed. " + ("x" * 120) + " dropped"
        self.assertEqual(_classify_attestation_verdict(text), ("completed", None))


class TestAttestationClassifierSingleSource(unittest.TestCase):
    """Both attestation surfaces route through ONE classifier (BI-2 anti-fork)."""

    def test_closeout_pipeline_shares_the_ceremony_classifier(self) -> None:
        from gzkit.commands import ceremony_state, closeout

        self.assertIs(
            getattr(closeout, "_classify_attestation_verdict", None),
            ceremony_state._classify_attestation_verdict,
        )

    def test_ceremony_emitter_shares_the_classifier(self) -> None:
        from gzkit.commands import ceremony_state, closeout_ceremony

        self.assertIs(
            closeout_ceremony._classify_attestation_verdict,
            ceremony_state._classify_attestation_verdict,
        )

    def test_no_residual_duplicate_classifier_in_closeout(self) -> None:
        from gzkit.commands import closeout

        self.assertFalse(
            hasattr(closeout, "_parse_ceremony_attestation_text"),
            "closeout._parse_ceremony_attestation_text was collapsed into "
            "ceremony_state._classify_attestation_verdict; a re-introduced copy "
            "is the BI-2 fork hazard this guard exists to catch.",
        )


if __name__ == "__main__":
    unittest.main()
