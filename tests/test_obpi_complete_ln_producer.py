"""Tests for the ln: proof-binding producer at gz obpi complete (GHI #599).

`gz obpi complete` binds resolved ARB receipt-IDs into the ledger but
historically never wrote the brief's `ln:` frontmatter — forcing a manual
backfill at every post-ADR-0.0.63 closeout. The `_inject_ln_block` producer
auto-populates `ln:` from the receipts the attestation gate resolved, so the
closeout proof-binding gate has an automated upstream.
"""

import unittest

import yaml

_BRIEF = """\
---
id: OBPI-9.9.9-01-demo
parent: ADR-9.9.9-demo
lane: Heavy
status: Completed
req_atomic:
  - REQ-9.9.9-01-01  # a comment that must survive injection
  - REQ-9.9.9-01-02
---

# OBPI-9.9.9-01-demo: Demo

## Acceptance Criteria

- [ ] REQ-9.9.9-01-01 [behavior]: the system does X when Y.
- [ ] REQ-9.9.9-01-02 [support]: the rule file carries subsection Z.
"""

_RECEIPTS = [
    "arb-step-unittest-deadbeef",
    "arb-ruff-cafebabe",
]


def _frontmatter(text: str) -> dict:
    end = text.find("\n---\n", 4)
    return yaml.safe_load(text[4:end])


class TestInjectLnBlock(unittest.TestCase):
    """The producer binds every Acceptance-Criteria REQ to the resolved receipts."""

    def test_writes_ln_for_every_req(self) -> None:
        from gzkit.commands.obpi_complete import _inject_ln_block

        out = _inject_ln_block(_BRIEF, _BRIEF, "OBPI-9.9.9-01-demo", _RECEIPTS)
        fm = _frontmatter(out)
        ln = {entry["req_id"]: entry["receipt_ids"] for entry in fm["ln"]}
        self.assertEqual(
            set(ln),
            {"REQ-9.9.9-01-01", "REQ-9.9.9-01-02"},
            "every Acceptance-Criteria REQ must get an ln entry",
        )
        for receipts in ln.values():
            self.assertEqual(receipts, _RECEIPTS, "each REQ binds to all resolved receipt-IDs")

    def test_preserves_existing_frontmatter_and_comments(self) -> None:
        from gzkit.commands.obpi_complete import _inject_ln_block

        out = _inject_ln_block(_BRIEF, _BRIEF, "OBPI-9.9.9-01-demo", _RECEIPTS)
        # Existing keys and their inline comment survive.
        self.assertIn("a comment that must survive injection", out)
        fm = _frontmatter(out)
        self.assertEqual(fm["id"], "OBPI-9.9.9-01-demo")
        self.assertEqual(fm["status"], "Completed")

    def test_idempotent_on_reinjection(self) -> None:
        from gzkit.commands.obpi_complete import _inject_ln_block

        once = _inject_ln_block(_BRIEF, _BRIEF, "OBPI-9.9.9-01-demo", _RECEIPTS)
        twice = _inject_ln_block(once, _BRIEF, "OBPI-9.9.9-01-demo", _RECEIPTS)
        self.assertEqual(once, twice, "re-injection must not duplicate the ln block")

    def test_noop_without_resolved_receipts(self) -> None:
        from gzkit.commands.obpi_complete import _inject_ln_block

        out = _inject_ln_block(_BRIEF, _BRIEF, "OBPI-9.9.9-01-demo", [])
        self.assertEqual(out, _BRIEF, "no resolved receipts -> no ln, no regression")


if __name__ == "__main__":
    unittest.main()
