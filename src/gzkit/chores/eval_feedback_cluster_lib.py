"""eval-feedback-cluster chore library — OBPI-0.0.26-03.

Reads ``adr-evaluation`` ledger events and ``gz-justify`` artifacts, groups
by recurring weak-dimension or confusion-shape patterns, and emits structured
proposal records when a pattern recurs >= ``cluster_min_recurrence`` times
across distinct artifacts.

Design:
- Pure library: no CLI surface, no ledger writes, no subprocess.
- Only writes to its own ``proofs_dir``; all other surfaces are read-only.
- Idempotent: deduplicates by content hash of ``(cluster_key, sorted artifact IDs)``.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONFUSION_VOCABULARY: frozenset[str] = frozenset(
    {
        "unclear",
        "ambiguous",
        "confusing",
        "scope drift",
        "boundary unclear",
        "not sure",
        "uncertain",
        "vague",
        "unresolved",
        "conflicting",
    }
)

_DEFAULT_CLUSTER_MIN_RECURRENCE = 3
_DEFAULT_SCORE_THRESHOLD = 3.0

# ---------------------------------------------------------------------------
# Public model
# ---------------------------------------------------------------------------


class ProposalRecord(BaseModel):
    """A single clustering proposal record emitted when a bucket exceeds threshold."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cluster_key: str = Field(..., description="Cluster identifier, e.g. dim:clarity:low")
    recurrence_count: int = Field(..., description="Number of distinct artifacts in the cluster")
    source_artifact_ids: list[str] = Field(..., description="Artifact IDs contributing to cluster")
    source_artifact_paths: list[str] = Field(
        ..., description="Artifact paths contributing to cluster"
    )  # noqa: E501
    summary: str = Field(..., description="Human-readable summary of the cluster")
    proposed_rule_target: str = Field(..., description="Suggested rule or doctrine target")
    content_hash: str = Field(..., description="SHA-256 content dedup fingerprint (first 16 chars)")
    filed: bool = Field(default=False, description="Whether a GHI has been filed for this proposal")
    ghi_url: str | None = Field(default=None, description="GitHub issue URL if filed")
    advisory: bool = Field(default=False, description="Marked advisory-only in headless run")


# ---------------------------------------------------------------------------
# Score band mapping
# ---------------------------------------------------------------------------


def _score_band(score: float) -> str:
    """Map a raw dimension score to a band label.

    Thresholds:
        < 1.5 -> critical
        < 2.5 -> very_low
        < 3.0 -> low
    """
    if score < 1.5:
        return "critical"
    if score < 2.5:
        return "very_low"
    return "low"


# ---------------------------------------------------------------------------
# Ledger reader
# ---------------------------------------------------------------------------


def _read_adr_evaluation_events(ledger_path: Path) -> list[dict]:
    """Read adr-evaluation events from ledger.jsonl.

    Returns a list of raw dicts for lines where event == "adr-evaluation".
    Non-existent ledger returns empty list.
    """
    if not ledger_path.exists():
        return []

    events: list[dict] = []
    with ledger_path.open(encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSON at %s line %d", ledger_path, line_num)
                continue
            if record.get("event") == "adr-evaluation":
                events.append(record)
    return events


# ---------------------------------------------------------------------------
# Justify artifact walker
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML-like frontmatter between first two ``---`` delimiters.

    Returns a dict of ``key: value`` pairs parsed from simple ``key: value``
    lines in the frontmatter block. Does not require a YAML parser.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}

    fm: dict[str, str] = {}
    for line in lines[1:end_idx]:
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def _walk_justify_artifacts(justify_root: Path) -> list[dict]:
    """Walk justify_root recursively for *.md files and parse frontmatter.

    Returns list of dicts: ``{"path": Path, "anchor_id": str, "raw": str}``.
    Non-existent root returns empty list.
    """
    if not justify_root.exists():
        return []

    artifacts: list[dict] = []
    for md_file in sorted(justify_root.rglob("*.md")):
        try:
            raw = md_file.read_text(encoding="utf-8")
        except OSError:
            logger.warning("Skipping unreadable file: %s", md_file)
            continue
        fm = _parse_frontmatter(raw)
        anchor_id = fm.get("anchor_id", md_file.stem)
        artifacts.append({"path": md_file, "anchor_id": anchor_id, "raw": raw})
    return artifacts


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------


def _extract_confusion_keywords(text: str) -> list[str]:
    """Scan text for confusion-shape vocabulary keywords.

    Returns sorted list of matched keywords (case-insensitive substring match).
    """
    lower = text.lower()
    matched = sorted(kw for kw in _CONFUSION_VOCABULARY if kw in lower)
    return matched


# ---------------------------------------------------------------------------
# Bucket builder
# ---------------------------------------------------------------------------


def _build_buckets(
    events: list[dict],
    justify_artifacts: list[dict],
    score_threshold: float,
) -> dict[str, list[dict]]:
    """Build cluster buckets from events and justify artifacts.

    Cluster key families:
        ``dim:<dimension_name>:<score_band>`` — adr-evaluation weak dimensions
        ``rt:<challenge_id>`` — fired red-team challenges
        ``jk:<keyword>`` — confusion keywords in justify artifacts

    Each bucket value is a list of ``{"artifact_id": str, "artifact_path": str}``.
    """
    buckets: dict[str, list[dict]] = {}

    for event in events:
        artifact_id = event.get("artifact_id", "")
        artifact_path = event.get("artifact_id", "")  # use id as path fallback

        dimensions: dict[str, float] = event.get("dimensions", {})
        for dim_name, score in dimensions.items():
            if score < score_threshold:
                band = _score_band(score)
                key = f"dim:{dim_name}:{band}"
                buckets.setdefault(key, []).append(
                    {"artifact_id": artifact_id, "artifact_path": artifact_path}
                )

        for challenge_id in event.get("red_team_challenges_fired", []):
            key = f"rt:{challenge_id}"
            buckets.setdefault(key, []).append(
                {"artifact_id": artifact_id, "artifact_path": artifact_path}
            )

    for artifact in justify_artifacts:
        anchor_id = artifact["anchor_id"]
        artifact_path = str(artifact["path"])
        keywords = _extract_confusion_keywords(artifact["raw"])
        for kw in keywords:
            key = f"jk:{kw}"
            buckets.setdefault(key, []).append(
                {"artifact_id": anchor_id, "artifact_path": artifact_path}
            )

    return buckets


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def _content_hash(cluster_key: str, artifact_ids: list[str]) -> str:
    """Compute a content-dedup fingerprint from cluster_key and sorted artifact IDs."""
    payload = json.dumps([cluster_key, sorted(artifact_ids)]).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _load_existing_hashes(proofs_dir: Path) -> set[str]:
    """Read all proposal-*.json files in proofs_dir and return their content_hash values."""
    if not proofs_dir.exists():
        return set()

    hashes: set[str] = set()
    for json_file in proofs_dir.glob("proposal-*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            ch = data.get("content_hash")
            if ch:
                hashes.add(ch)
        except (json.JSONDecodeError, OSError):
            logger.warning("Skipping unreadable proposal file: %s", json_file)
    return hashes


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------


def _build_summary(cluster_key: str, artifact_ids: list[str]) -> str:
    """Build a human-readable summary for a proposal record."""
    if cluster_key.startswith("dim:"):
        _, dim_name, band = cluster_key.split(":", 2)
        return (
            f"Dimension '{dim_name}' scored in the '{band}' band "
            f"across {len(artifact_ids)} distinct artifacts: " + ", ".join(sorted(artifact_ids))
        )
    if cluster_key.startswith("rt:"):
        challenge_id = cluster_key[3:]
        return (
            f"Red-team challenge '{challenge_id}' fired "
            f"across {len(artifact_ids)} distinct artifacts: " + ", ".join(sorted(artifact_ids))
        )
    if cluster_key.startswith("jk:"):
        keyword = cluster_key[3:]
        return (
            f"Confusion keyword '{keyword}' found "
            f"across {len(artifact_ids)} justify artifacts: " + ", ".join(sorted(artifact_ids))
        )
    return f"Cluster '{cluster_key}' across {len(artifact_ids)} artifacts."


def _build_proposed_rule_target(cluster_key: str) -> str:
    """Build a proposed rule target string from cluster_key."""
    if cluster_key.startswith("dim:"):
        _, dim_name, band = cluster_key.split(":", 2)
        return f"docs/governance/{dim_name}-{band}-improvement.md"
    if cluster_key.startswith("rt:"):
        challenge_id = cluster_key[3:]
        return f".gzkit/rules/red-team-{challenge_id}.md"
    if cluster_key.startswith("jk:"):
        keyword = cluster_key[3:].replace(" ", "-")
        return f".gzkit/rules/clarity-{keyword}.md"
    return ".gzkit/rules/general-improvement.md"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_cluster(
    project_root: Path,
    *,
    ledger_path: Path | None = None,
    justify_root: Path | None = None,
    proofs_dir: Path | None = None,
    cluster_min_recurrence: int = _DEFAULT_CLUSTER_MIN_RECURRENCE,
    score_threshold: float = _DEFAULT_SCORE_THRESHOLD,
) -> list[ProposalRecord]:
    """Run the eval-feedback-cluster chore.

    Reads adr-evaluation events from ledger, walks justify artifacts, builds
    cluster buckets, and emits proposal records for buckets that meet the
    recurrence threshold.

    Args:
        project_root: Project root directory (used to resolve defaults).
        ledger_path: Path to ledger.jsonl; defaults to
            ``project_root/.gzkit/ledger.jsonl``.
        justify_root: Root to walk for justify artifacts; defaults to
            ``project_root/artifacts/justify``.
        proofs_dir: Directory to write proposal JSON files; defaults to
            ``project_root/.gzkit/chores/eval-feedback-cluster/proofs``.
        cluster_min_recurrence: Minimum distinct artifacts for a cluster to
            produce a proposal (default 3).
        score_threshold: Score below which a dimension is considered weak
            (default 3.0).

    Returns:
        List of newly-written ProposalRecord objects. Empty if no new clusters
        exceed threshold or all matching clusters were already written.
    """
    if ledger_path is None:
        ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if justify_root is None:
        justify_root = project_root / "artifacts" / "justify"
    if proofs_dir is None:
        proofs_dir = project_root / ".gzkit" / "chores" / "eval-feedback-cluster" / "proofs"

    events = _read_adr_evaluation_events(ledger_path)
    justify_artifacts = _walk_justify_artifacts(justify_root)
    buckets = _build_buckets(events, justify_artifacts, score_threshold)
    existing_hashes = _load_existing_hashes(proofs_dir)

    proposals: list[ProposalRecord] = []

    for cluster_key, members in buckets.items():
        # Deduplicate members by artifact_id within this bucket
        seen_ids: set[str] = set()
        unique_members: list[dict] = []
        for member in members:
            aid = member["artifact_id"]
            if aid not in seen_ids:
                seen_ids.add(aid)
                unique_members.append(member)

        if len(unique_members) < cluster_min_recurrence:
            continue

        artifact_ids = [m["artifact_id"] for m in unique_members]
        artifact_paths = [m["artifact_path"] for m in unique_members]
        ch = _content_hash(cluster_key, artifact_ids)

        if ch in existing_hashes:
            continue

        proposal = ProposalRecord(
            cluster_key=cluster_key,
            recurrence_count=len(unique_members),
            source_artifact_ids=artifact_ids,
            source_artifact_paths=artifact_paths,
            summary=_build_summary(cluster_key, artifact_ids),
            proposed_rule_target=_build_proposed_rule_target(cluster_key),
            content_hash=ch,
        )

        proofs_dir.mkdir(parents=True, exist_ok=True)
        ts_ms = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S%f")
        proposal_path = proofs_dir / f"proposal-{ts_ms}.json"
        proposal_path.write_text(
            proposal.model_dump_json(indent=2),
            encoding="utf-8",
        )

        existing_hashes.add(ch)
        proposals.append(proposal)

    return proposals


__all__ = [
    "ProposalRecord",
    "run_cluster",
]
