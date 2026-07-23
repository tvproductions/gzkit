"""REQ-kind partition of the audit-check uncovered-REQ advisory (GHI #701).

`gz adr audit-check` reported every uncovered REQ under a heading naming
`@covers` traceability as the missing thing — but only BEHAVIOR REQs owe a
`@covers` test. SUPPORT (ledger + structural validator) and STRUCTURAL-FENCE
(parent-ADR boundary invariant) are proof-exempt, so reporting them as deficient
steers an agent straight into the rule-(c) anti-pattern (a filesystem-grep
`@covers` decorator that cannot fail when behavior changes).

The partition keys on declared ADR-0.0.59 kind, with untagged/legacy REQs
defaulting to BEHAVIOR — the conservative channel that owes proof.

Direct-fix work under GHI #701 — no covering REQ, so no `@covers`.
"""

from __future__ import annotations

import unittest
from typing import Any


def _adv(*ids: str) -> list[dict[str, Any]]:
    return [{"id": i, "issue": "REQ not covered.", "severity": "advisory"} for i in ids]


class TestPartitionAdvisoryByKind(unittest.TestCase):
    def test_behavior_and_untagged_land_in_behavior_bucket(self) -> None:
        from gzkit.commands.adr_audit import _partition_advisory_by_kind

        advisory = _adv("REQ-0.0.37-01-01", "REQ-0.0.37-02-01")
        kinds = {"REQ-0.0.37-01-01": "BEHAVIOR"}  # -02-01 is untagged → BEHAVIOR
        behavior, exempt = _partition_advisory_by_kind(advisory, kinds)
        self.assertEqual({c["id"] for c in behavior}, {"REQ-0.0.37-01-01", "REQ-0.0.37-02-01"})
        self.assertEqual(exempt, [])

    def test_support_and_fence_land_in_exempt_bucket(self) -> None:
        from gzkit.commands.adr_audit import _partition_advisory_by_kind

        advisory = _adv("REQ-a", "REQ-b", "REQ-c")
        kinds = {"REQ-a": "SUPPORT", "REQ-b": "STRUCTURAL-FENCE", "REQ-c": "BEHAVIOR"}
        behavior, exempt = _partition_advisory_by_kind(advisory, kinds)
        self.assertEqual({c["id"] for c in behavior}, {"REQ-c"})
        self.assertEqual({c["id"] for c in exempt}, {"REQ-a", "REQ-b"})

    def test_declared_kind_is_stamped_on_each_entry(self) -> None:
        from gzkit.commands.adr_audit import _partition_advisory_by_kind

        behavior, exempt = _partition_advisory_by_kind(_adv("REQ-a"), {"REQ-a": "SUPPORT"})
        self.assertEqual(behavior, [])
        self.assertEqual(exempt[0]["kind"], "SUPPORT")

    def test_ghi_701_population_all_exempt(self) -> None:
        """The GHI's exact case: 26 SUPPORT + 1 STRUCTURAL-FENCE, zero BEHAVIOR."""
        from gzkit.commands.adr_audit import _partition_advisory_by_kind

        support_ids = [f"REQ-0.0.37-{n:02d}-01" for n in range(1, 27)]
        fence_id = "REQ-0.0.37-99-01"
        advisory = _adv(*support_ids, fence_id)
        kinds = dict.fromkeys(support_ids, "SUPPORT") | {fence_id: "STRUCTURAL-FENCE"}
        behavior, exempt = _partition_advisory_by_kind(advisory, kinds)
        self.assertEqual(behavior, [])
        self.assertEqual(len(exempt), 27)


if __name__ == "__main__":
    unittest.main()
