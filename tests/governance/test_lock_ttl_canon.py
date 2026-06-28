"""The lock TTL default must equal the token-block canon, with no drift across sites.

Derived from GHI #604 ("token-block TTL default contradiction: canon 24h vs CLI
--ttl 120m") and token-block-discipline.md § Sub-Invariant 4 (Default TTL: 24 hours).

The canon is 24 hours. There must be a single source of truth (`DEFAULT_LOCK_TTL_MINUTES`)
that the CLI claim default, the preflight expiry fallback, and the MX session lock all
reference — so the value cannot drift between sites (the defect this fixes).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.commands.mx_cmd import _DEFAULT_TTL_MINUTES
from gzkit.commands.preflight import _find_expired_locks
from gzkit.lock_manager import DEFAULT_LOCK_TTL_MINUTES


class TestLockTtlCanon(unittest.TestCase):
    def test_default_equals_canon_24_hours(self) -> None:
        # token-block-discipline.md § Sub-Invariant 4: Default TTL is 24 hours.
        self.assertEqual(DEFAULT_LOCK_TTL_MINUTES, 24 * 60)

    def test_cli_claim_default_is_canon(self) -> None:
        # The `gz obpi lock claim` --ttl default must be the canon, not the old 120.
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        args = parser.parse_args(["obpi", "lock", "claim", "OBPI-0.0.1-01"])
        self.assertEqual(args.ttl_minutes, DEFAULT_LOCK_TTL_MINUTES)

    def test_preflight_fallback_is_canon(self) -> None:
        # A lock file missing ttl_minutes falls back to the canon. Aged ~2h10m, it is
        # NOT expired under the 24h canon (it WOULD be under the old 120m default).
        with tempfile.TemporaryDirectory() as tmp:
            locks_dir = Path(tmp)
            claimed = (datetime.now(UTC) - timedelta(minutes=130)).isoformat()
            (locks_dir / "OBPI-0.0.1-01.lock.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.0.1-01", "claimed_at": claimed}),
                encoding="utf-8",
            )
            expired = _find_expired_locks(locks_dir)
            self.assertEqual(expired, [])

    def test_mx_session_lock_ttl_tracks_canon(self) -> None:
        # mx_cmd's session-lock TTL declares it matches the OBPI lock TTL; it must
        # reference the same canon constant so the two cannot drift apart.
        self.assertEqual(_DEFAULT_TTL_MINUTES, DEFAULT_LOCK_TTL_MINUTES)


if __name__ == "__main__":
    unittest.main()
