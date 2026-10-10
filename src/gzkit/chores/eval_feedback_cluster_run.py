"""Run the eval-feedback-cluster chore over a project (GHI #997).

``python -m gzkit.chores.eval_feedback_cluster_run`` is the operational step the
chore's CHORE.md names: it reads the project's ``adr-evaluation`` ledger events and
``gz-justify`` artifacts, clusters them, and writes proposal records under the
chore's ``proofs/`` directory. Before GHI #997 the chore's "run clustering" step
invoked the library's unit tests, so the live ledger was never clustered.

Every run reports what it read, so a zero-proposal run is distinguishable from
an empty input (the GHI #614 negative-signal shape). ``--dry-run`` reports the
same counts and writes nothing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gzkit.chores.eval_feedback_cluster_lib import cluster_buckets, run_cluster
from gzkit.registries import RegistryError, load_registry

_THRESHOLDS_REGISTRY = "eval_feedback_thresholds"
_DEFAULTS = {"cluster_min_recurrence": 3, "low_score_threshold": 3.0}


def load_thresholds(project_root: Path) -> dict[str, float]:
    """Return the chore's thresholds from the ``eval_feedback_thresholds`` registry.

    Read through the single registry seam (GHI #1067). A project without the
    registry runs on the library's defaults.
    """
    try:
        raw = load_registry(project_root, _THRESHOLDS_REGISTRY)
    except RegistryError:
        return dict(_DEFAULTS)
    return {key: raw.get(key, default) for key, default in _DEFAULTS.items()}


def main(argv: list[str] | None = None) -> int:
    """Cluster the project's evaluation evidence; return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Report the clusters and write nothing."
    )
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--proofs-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    root = (args.project_root or Path.cwd()).resolve()
    thresholds = load_thresholds(root)
    min_recurrence = int(thresholds["cluster_min_recurrence"])
    score_threshold = float(thresholds["low_score_threshold"])

    summary = cluster_buckets(root, score_threshold=score_threshold)
    qualifying = {
        key: members
        for key, members in summary.buckets.items()
        if len({m["artifact_id"] for m in members}) >= min_recurrence
    }
    print(
        f"eval-feedback-cluster: read {summary.events_read} adr-evaluation event(s) and "
        f"{summary.artifacts_read} justify artifact(s) from {root}"
    )
    print(
        f"  {len(summary.buckets)} cluster(s); {len(qualifying)} at or above recurrence "
        f"{min_recurrence} (score threshold {score_threshold})"
    )
    for key in sorted(qualifying):
        distinct = len({m["artifact_id"] for m in qualifying[key]})
        print(f"  {key}: {distinct} distinct artifact(s)")

    if args.dry_run:
        print("  dry run: nothing written")
        return 0

    proposals = run_cluster(
        root,
        proofs_dir=args.proofs_dir,
        cluster_min_recurrence=min_recurrence,
        score_threshold=score_threshold,
    )
    print(f"  wrote {len(proposals)} new proposal record(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
