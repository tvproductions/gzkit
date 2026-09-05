"""Behavior tests for the observed-delivery witness (GHI #962).

Every other check on this surface compares one authored number to another
authored number. ``CodexDocCapCoherenceTest`` fail-closes when the generated
``.codex/config.toml`` and ``data/vendor-manifest.json`` disagree; the
surface-delivery witness compares rendered bytes against the cap the manifest
*declares*. Both are green while delivery is zero — the presence-check shape
``AGENTS.md`` names: *"A PRESENCE CHECK ANSWERS 'is something armed', NEVER
'did the governed procedure run'."*

This witness asks the other question: **how many bytes did Codex actually
hand the model?** ``codex debug prompt-input`` renders the model-visible prompt
list as JSON, so the answer is observable rather than inferred.

The measured cost of not asking it (GHI #962, 2026-09-04 → 2026-09-05):
``codex doctor`` names only the global config source and does not enumerate the
project-local overlay. Read as proof of absence, that silence produced the
conclusion *"Codex never reads it"*, which licensed lowering the cap from 65536
to Codex's own 32768 default — re-introducing the truncation GHI #815 had
already fixed, and propagating *"gzkit has no route to set it"* into five
surfaces. Trust is what loads the project-local file; the cap had been working.

Severity is deliberately advisory, never fail-closed. A vendor's byte cap must
not gate the core contract (operator ruling 2026-07-06), and the observation
depends on local state — whether Codex is installed, whether the operator has
trusted this directory — which is environment, not repository truth. A missing
observation is reported as *unobserved*, never as a pass: an absent witness that
renders green is the exact defect this module exists to close.
"""

from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.codex_delivery_witness import (
    _PREFIX,
    DeliveryProbe,
    audit_codex_delivery_witness,
    delivered_contract_bytes,
    diagnose_delivery,
)


def _prompt_input(delivered: str, *, project_root: str = "/repo") -> list[dict[str, object]]:
    """Build a prompt-input payload shaped like `codex debug prompt-input` output.

    The framing is reproduced from observed output rather than invented: Codex
    wraps the project doc in a `# AGENTS.md instructions for <root>` header and
    an `<INSTRUCTIONS>` element, and the bytes between the element's tags are
    exactly the bytes it loaded from the file (measured 2026-09-05: a 32768-byte
    cap yields a 32768-byte inner block inside a 32862-byte payload).
    """
    return [
        {"role": "developer", "content": [{"text": "<permissions instructions>…"}]},
        {
            "role": "user",
            "content": [
                {"text": "<recommended_plugins>…</recommended_plugins>"},
                {
                    "text": (
                        f"# AGENTS.md instructions for {project_root}\n\n"
                        f"<INSTRUCTIONS>\n{delivered}\n</INSTRUCTIONS>"
                    )
                },
                {"text": "<environment_context>…</environment_context>"},
            ],
        },
    ]


def _advisories(fn) -> list[str]:
    """Run *fn*, returning the advisory lines it emitted to stderr."""
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        fn()
    return [line for line in stderr.getvalue().splitlines() if _PREFIX in line]


class DeliveredContractBytesTest(unittest.TestCase):
    """The witness must read the doc bytes, not the bytes of Codex's wrapper."""

    def test_returns_the_inner_block_size_not_the_payload_size(self) -> None:
        """Wrapper bytes are Codex's framing and are not part of the contract.

        Counting them would overstate delivery by a constant (~94 B observed)
        and would make a fully-truncated surface look like it still arrived.
        """
        contract = "x" * 5000

        self.assertEqual(delivered_contract_bytes(_prompt_input(contract)), 5000)

    def test_measures_utf8_bytes_rather_than_characters(self) -> None:
        """The cap Codex applies is a byte cap; characters would undercount it."""
        contract = "—" * 100  # 3 bytes each in UTF-8

        self.assertEqual(delivered_contract_bytes(_prompt_input(contract)), 300)

    def test_returns_none_when_no_contract_block_is_present(self) -> None:
        """No AGENTS.md block means the contract reached the model not at all.

        That is a distinct state from a truncated delivery and must not be
        reported as a byte count of zero, which would read as a measurement.
        """
        payload = [{"role": "user", "content": [{"text": "<environment_context/>"}]}]

        self.assertIsNone(delivered_contract_bytes(payload))

    def test_ignores_prose_that_merely_mentions_the_contract(self) -> None:
        """Other prompt sections reference AGENTS.md; only the loaded doc counts."""
        payload = [
            {
                "role": "developer",
                "content": [{"text": "Do not spawn sub-agents unless AGENTS.md asks for it."}],
            }
        ]

        self.assertIsNone(delivered_contract_bytes(payload))


class DiagnoseDeliveryTest(unittest.TestCase):
    """Verdict semantics: what the observation means for the declared cap."""

    def test_whole_surface_delivered_raises_no_warning(self) -> None:
        findings = diagnose_delivery(
            relpath="AGENTS.md", surface_bytes=46876, delivered_bytes=46876, declared_cap=65536
        )

        self.assertEqual([severity for severity, _ in findings], ["NOTE"])

    def test_truncated_delivery_warns_and_names_the_undelivered_bytes(self) -> None:
        """The deficit is the actionable number — canon past it is not in force."""
        findings = diagnose_delivery(
            relpath="AGENTS.md", surface_bytes=46876, delivered_bytes=32768, declared_cap=65536
        )
        warnings = [message for severity, message in findings if severity == "WARNING"]

        self.assertTrue(warnings, "a truncated delivery must warn")
        self.assertTrue(
            any("14108" in message for message in warnings),
            f"the undelivered byte count must be stated; got {warnings}",
        )

    def test_delivery_below_the_declared_cap_disputes_the_declaration(self) -> None:
        """The GHI #962 semantic, and the reason this module exists.

        gzkit declaring a cap of 65536 while Codex delivers 32768 means the
        declared number is not the number in force. Every same-surface check
        stays green in that state, because each compares authored numbers to
        each other. Only an observation can dispute the declaration.
        """
        findings = diagnose_delivery(
            relpath="AGENTS.md", surface_bytes=46876, delivered_bytes=32768, declared_cap=65536
        )
        warnings = [message for severity, message in findings if severity == "WARNING"]

        self.assertTrue(
            any("65536" in message and "32768" in message for message in warnings),
            f"the declared cap and the delivered size must be contrasted; got {warnings}",
        )

    def test_delivery_at_the_declared_cap_does_not_dispute_it(self) -> None:
        """A surface larger than a correctly-applied cap is a content problem.

        That is the surface-delivery witness's finding (and GHI #815's scope),
        not evidence that the declaration is wrong. Reporting it here as a
        disputed declaration would send the reader to the wrong remedy.
        """
        findings = diagnose_delivery(
            relpath="AGENTS.md", surface_bytes=90000, delivered_bytes=65536, declared_cap=65536
        )
        disputes = [
            message
            for severity, message in findings
            if severity == "WARNING" and "declares" in message
        ]

        self.assertEqual(disputes, [])

    def test_absent_contract_block_warns_rather_than_reporting_zero(self) -> None:
        findings = diagnose_delivery(
            relpath="AGENTS.md", surface_bytes=46876, delivered_bytes=None, declared_cap=65536
        )

        self.assertEqual([severity for severity, _ in findings], ["WARNING"])


class AuditCodexDeliveryWitnessTest(unittest.TestCase):
    """Audit-level posture: advisory always, and never green on no evidence."""

    def _root(self, stack: contextlib.ExitStack, contract: str) -> Path:
        root = Path(stack.enter_context(TemporaryDirectory()))
        (root / "AGENTS.md").write_text(contract, encoding="utf-8")
        return root

    def test_unobserved_delivery_is_reported_as_unobserved_not_as_a_pass(self) -> None:
        """An absent witness must never render green.

        `AGENTS.md`: *"Do not build or trust a gate whose only witness is that
        an artifact exists."* A witness that stays silent when it could not run
        is the same defect wearing a different hat — the reader concludes the
        surface was checked.
        """
        with contextlib.ExitStack() as stack:
            root = self._root(stack, "contract")
            probe = DeliveryProbe(payload=None, unavailable_reason="codex CLI not on PATH")

            lines = _advisories(lambda: audit_codex_delivery_witness(root, probe=lambda _r: probe))

        self.assertTrue(lines, "an unavailable witness must still say so")
        self.assertTrue(
            any("unobserved" in line for line in lines),
            f"the advisory must name the state as unobserved; got {lines}",
        )

    def test_unobserved_delivery_returns_no_findings(self) -> None:
        """Environment absence is not a repository defect and must not gate."""
        with contextlib.ExitStack() as stack:
            root = self._root(stack, "contract")
            probe = DeliveryProbe(payload=None, unavailable_reason="codex CLI not on PATH")

            with contextlib.redirect_stderr(io.StringIO()):
                findings = audit_codex_delivery_witness(root, probe=lambda _r: probe)

        self.assertEqual(findings, [])

    def test_truncated_delivery_is_advisory_never_fail_closed(self) -> None:
        """Operator ruling 2026-07-06: an adapter limit must not gate the core."""
        with contextlib.ExitStack() as stack:
            root = self._root(stack, "x" * 5000)
            probe = DeliveryProbe(payload=_prompt_input("x" * 1000))

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                findings = audit_codex_delivery_witness(root, probe=lambda _r: probe)

        self.assertEqual(findings, [])
        self.assertTrue(
            any("WARNING" in line and _PREFIX in line for line in stderr.getvalue().splitlines()),
            "a truncated delivery must surface on the advisory channel",
        )

    def test_whole_delivery_reports_the_observation(self) -> None:
        """The green path must still speak: silence cannot distinguish itself
        from a witness that never ran."""
        with contextlib.ExitStack() as stack:
            root = self._root(stack, "x" * 5000)
            probe = DeliveryProbe(payload=_prompt_input("x" * 5000))

            lines = _advisories(lambda: audit_codex_delivery_witness(root, probe=lambda _r: probe))

        self.assertTrue(any("5000" in line for line in lines), f"got {lines}")

    def test_missing_surface_is_not_an_error(self) -> None:
        """A project without a root AGENTS.md has nothing to observe."""
        with contextlib.ExitStack() as stack:
            root = Path(stack.enter_context(TemporaryDirectory()))

            with contextlib.redirect_stderr(io.StringIO()):
                findings = audit_codex_delivery_witness(
                    root, probe=lambda _r: DeliveryProbe(payload=None, unavailable_reason="n/a")
                )

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
