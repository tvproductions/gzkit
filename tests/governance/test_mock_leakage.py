"""No test may leave a ``Mock`` bolted onto a gzkit module (GHI #857).

A patch that outlives its test does not fail that test — it fails whichever test
runs next and happens to call the patched surface. Measured 2026-08-22: two
``resolve_adr_file`` patchers were unwound FIFO, which restored the INNER
patcher's mock instead of the original function, so
``gzkit.commands.adr_audit.resolve_adr_file`` stayed a ``MagicMock`` for the rest
of the process. Four tests in ``tests.commands.test_runtime`` then passed only in
the default alphabetical order — including one asserting that a pool ADR is
REFUSED, which instead audit-checked whichever ADR id the last layered patch had
been handed. The canonical ``uv run -m unittest -q`` that attests "Tests pass"
for Gate 5 was green in exactly one traversal order.

**What this test can and cannot do.** It cannot prove the suite is
order-independent; it observes one moment in one process. What it does is convert
a leak from SILENT into a failure: any module that leaks and runs before this one
is caught, and under a shuffled run — which is how GHI #857 surfaced — "before
this one" is most of the suite most of the time. That is a net, not a proof, and
it is named as a net here so nobody later reads a green run as the stronger claim.

The scoped sibling in ``tests/governance/test_audit_check_covers_backfill.py``
(``TestPatchLeakageIntoSiblingModules``) is the deterministic half: it runs the
one class that actually leaked and asserts restoration unconditionally. The two
are complementary — that one always fires for the known instance, this one
sometimes fires for an unknown one.

Costs nothing: a walk of the already-imported ``gzkit.*`` modules, which is why
it can sit in the default suite rather than behind a marker.

@covers GHI #857
"""

from __future__ import annotations

import sys
import unittest
from unittest.mock import NonCallableMock


class TestNoLeakedMocksOnGzkitModules(unittest.TestCase):
    """Every gzkit module attribute must be the real object, not a patch remnant."""

    def test_no_gzkit_module_attribute_is_a_mock(self) -> None:
        leaked: list[str] = []
        for module_name, module in list(sys.modules.items()):
            if not module_name.startswith("gzkit") or module is None:
                continue
            for attr in dir(module):
                try:
                    value = getattr(module, attr)
                except AttributeError:
                    continue
                # NonCallableMock is the base of Mock/MagicMock alike, so this
                # catches every patch remnant without enumerating the subclasses.
                if isinstance(value, NonCallableMock):
                    leaked.append(f"{module_name}.{attr}")

        self.assertEqual(
            sorted(leaked),
            [],
            "a test that ran earlier left a Mock installed on a gzkit module. It "
            "will answer for every test that follows, so those tests are green "
            "only in orderings that place them first. Find the patcher that was "
            "not stopped — a common cause is unwinding layered patchers FIFO, "
            "which restores the inner mock rather than the original (GHI #857).",
        )


if __name__ == "__main__":
    unittest.main()
