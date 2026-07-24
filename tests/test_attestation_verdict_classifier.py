"""Semantics + single-source guard for the ceremony attestation-verdict classifier.

GHI #573 (BI-2 DRY fork, ADR-0.0.63 Gate-5 audit): ``closeout.py``'s
``_parse_ceremony_attestation_text`` was a byte-identical fork of
``ceremony_state.py``'s ``_classify_attestation_verdict``. A future edit to one
body could silently diverge the ``attested`` ledger event ``status`` from the
``lifecycle_transition`` ``to_state`` (state-doctrine Layer-1/Layer-2
incoherence). This test pins the classifier's verdict semantics and guards
against the fork's return: both attestation-emitting paths (``closeout`` and
``closeout_ceremony``) route through the single ``ceremony_state`` classifier.
"""

import unittest

from gzkit.commands import closeout
from gzkit.commands.ceremony_state import _classify_attestation_verdict


class TestAttestationVerdictClassifier(unittest.TestCase):
    def test_verdict_classification_table(self) -> None:
        cases = [
            # (attestation text, expected status, expected reason)
            ("Completed - all gates green", "completed", None),
            ("attest completed — enriched", "completed", None),
            ("Dropped - scope pulled", "dropped", "Dropped - scope pulled"),
            (
                "Completed - Partial: docs deferred",
                "partial",
                "Completed - Partial: docs deferred",
            ),
            ("DROPPED loudly", "dropped", "DROPPED loudly"),
            ("Partial coverage only", "partial", "Partial coverage only"),
        ]
        for text, exp_status, exp_reason in cases:
            with self.subTest(text=text):
                status, reason = _classify_attestation_verdict(text)
                self.assertEqual(status, exp_status)
                self.assertEqual(reason, exp_reason)

    def test_dropped_precedence_over_partial(self) -> None:
        # "dropped" is checked before "partial"; a text carrying both classifies dropped.
        status, _reason = _classify_attestation_verdict("Dropped - was going to be partial")
        self.assertEqual(status, "dropped")

    def test_keyword_only_matches_within_120_char_window(self) -> None:
        # The classifier scans only the leading 120 chars; a keyword past it is not seen.
        text = "Completed " + ("x" * 130) + " dropped"
        status, reason = _classify_attestation_verdict(text)
        self.assertEqual(status, "completed")
        self.assertIsNone(reason)

    def test_reason_is_whitespace_stripped(self) -> None:
        status, reason = _classify_attestation_verdict("   Dropped - trailing   ")
        self.assertEqual(status, "dropped")
        self.assertEqual(reason, "Dropped - trailing")

    def test_single_source_no_closeout_duplicate(self) -> None:
        # BI-2 guard: closeout must NOT reintroduce a private classifier; both
        # attestation paths route through ceremony_state._classify_attestation_verdict.
        self.assertFalse(
            hasattr(closeout, "_parse_ceremony_attestation_text"),
            "closeout must route through ceremony_state._classify_attestation_verdict "
            "(GHI #573 BI-2 DRY fork); no private duplicate.",
        )


if __name__ == "__main__":
    unittest.main()
