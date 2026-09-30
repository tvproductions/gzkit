"""ARB RED reporter — emits the base-tree falsifiability receipt (GHI #642).

Sibling of ``step_reporter``, inverted: a step receipt records whatever exit status
a command produced, while a RED receipt records that a test *failed* against the
base tree, and how. ``exit_status == 0`` here is not success — it is the finding
that the test cannot fail, and the caller is expected to treat it as blocking.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.arb.paths import receipts_root
from gzkit.arb.ruff_reporter import _git_context
from gzkit.commit_witness import CommitWitness
from gzkit.red_witness import RedWitness, run_red_witness

SCHEMA_ID = "gzkit.arb.red_receipt.v1"
COMMIT_SCHEMA_ID = "gzkit.arb.red_commit_receipt.v1"
DEFAULT_MAX_OUTPUT_CHARS = 4000


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def build_red_receipt(
    witness: RedWitness,
    *,
    duration_ms: int,
    obpi_id: str | None = None,
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
) -> dict[str, object]:
    """Render a ``RedWitness`` as a schema-conformant receipt payload."""
    tail = witness.output_tail
    truncated = len(tail) > max_output_chars
    return {
        "schema": SCHEMA_ID,
        "red": {
            "req_id": witness.req_id,
            "test_names": list(witness.test_names),
            "obpi_id": obpi_id,
        },
        "run_id": f"arb-red-{witness.req_id}-{uuid.uuid4().hex}",
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git": _git_context(),
        "base_commit": witness.base_commit,
        "base_provenance": witness.base_provenance,
        "exit_status": witness.exit_status,
        "failure_class": witness.failure_class,
        "duration_ms": duration_ms,
        "output_tail": tail[-max_output_chars:] if truncated else tail,
        "output_truncated": truncated,
    }


def build_red_commit_receipt(
    witness: CommitWitness, *, exit_status: int, duration_ms: int
) -> dict[str, object]:
    """Render a commit-mode witness as a receipt (GHI #1152).

    ``ghi-close`` cites this verdict when it closes a direct fix, so the run must
    leave a record a reader can resolve, not only terminal output.
    """
    return {
        "schema": COMMIT_SCHEMA_ID,
        "run_id": f"arb-red-commit-{witness.commit[:12]}-{uuid.uuid4().hex}",
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git": _git_context(),
        "commit": witness.commit,
        "verdict": witness.verdict,
        "detail": witness.detail,
        "test_modules": list(witness.test_modules),
        "hunks": [hunk.model_dump() for hunk in witness.hunks],
        "exit_status": exit_status,
        "duration_ms": duration_ms,
    }


def write_red_commit_receipt(receipt: dict[str, object], project_root: Path) -> Path:
    """Write a commit-mode receipt under ``project_root``'s receipts root."""
    return _write_receipt(receipt, receipts_root(project_root=project_root))


def _write_receipt(receipt: dict[str, object], root: Path | None = None) -> Path:
    path = (root or receipts_root()) / f"{receipt['run_id']}.json"
    # Trailing newline keeps end-of-file-fixer from rewriting receipts every commit.
    path.write_text(_canonical(receipt) + "\n", encoding="utf-8")
    return path


def run_red_via_arb(
    *,
    project_root: Path,
    req_id: str,
    test_names: list[str],
    base_commit: str | None = None,
    obpi_id: str | None = None,
) -> tuple[RedWitness, Path]:
    """Run the base-tree witness for ``req_id`` and emit its ARB receipt."""
    started = time.perf_counter()
    witness = run_red_witness(
        project_root=project_root,
        req_id=req_id,
        test_names=test_names,
        base_commit=base_commit,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    receipt = build_red_receipt(witness, duration_ms=duration_ms, obpi_id=obpi_id)
    return witness, _write_receipt(receipt)


__all__ = [
    "COMMIT_SCHEMA_ID",
    "SCHEMA_ID",
    "build_red_commit_receipt",
    "build_red_receipt",
    "run_red_via_arb",
    "write_red_commit_receipt",
]
