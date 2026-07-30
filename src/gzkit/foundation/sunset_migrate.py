"""Foundation Sunset migration — one-shot executor (ADR-0.34.0, OBPI-04).

Partitions the foundation set by Layer-2 ledger truth, demotes the
genuinely-unstarted foundations to pool, populates
``data/foundation_grandfather.json``, and emits one attested
``foundation_grandfathered`` terminality witness per manifest entry
(backfill-at-populate, so the ledger is complete-by-construction).

Usage::

    uv run python -m gzkit.foundation.sunset_migrate --dry-run
    uv run python -m gzkit.foundation.sunset_migrate --apply \
        --attestor "g0" --attestation "<Gate-5 attestation>"

``--dry-run`` is the default; ``--apply`` is the only path that writes. The
Gate-5 human attestation is the legitimate terminality witness for pre-ledger
foundations (7 of 8 sampled carry no terminal ledger event), so ``--apply``
fail-closes without ``--attestor`` and ``--attestation``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from gzkit.config import GzkitConfig
from gzkit.foundation.triage import _extract_h1_title, _parse_simple_frontmatter
from gzkit.ledger import Ledger

_ADR_SHORT_ID_RE = re.compile(r"^(ADR-\d+\.\d+\.\d+)")

_DEMOTE_GHI = 520
_DEMOTE_OPERATOR = "g0"
_DEMOTE_NOTE = "Foundation Sunset demotion (ADR-0.34.0, OBPI-04)"

_MANIFEST_REL = Path("data") / "foundation_grandfather.json"
_GOLDEN_REL = Path("tests") / "governance" / "fixtures" / "foundation_grandfather_golden.json"

# Prerequisite foundations whose closeout makes the tree terminal (brief
# Requirement 1 / parent ADR SEQUENCING). Populating over a foundation still in
# Pending-with-attested-work limbo would make the terminal-partition gate
# false-red the instant OBPI-05 wires it into `gz check`.
_SUNSET_PREREQUISITES: tuple[str, ...] = (
    "ADR-0.0.37",
    "ADR-0.0.54",
    "ADR-0.0.64",
    "ADR-0.0.65",
    "ADR-0.0.72",
)


class FoundationRow(BaseModel):
    """One on-disk foundation ADR with its Layer-2 completion tally."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    title: str
    semver: str
    package: Path
    completed_obpis: int
    live_obpis: int
    brief_paths: tuple[Path, ...]


class Partition(BaseModel):
    """The sunset partition: what demotes to pool, what stays grandfathered."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    demote: tuple[FoundationRow, ...]
    grandfather: tuple[FoundationRow, ...]

    @property
    def total(self) -> int:
        """Total foundations accounted for — must equal the on-disk count."""
        return len(self.demote) + len(self.grandfather)


# The negation flags on a graph node, and WHY these three and not the
# ``TERMINAL_EVENTS`` name set:
#
# ``TERMINAL_EVENTS`` answers "did a terminal event EVER occur?"; this partition
# needs "is this child terminal NOW?". The two differ wherever a disposition is
# reversible, and ADR-0.0.71 makes repudiation exactly that: `gz obpi repudiate`
# is reverse-and-keep, and a genuine re-attestation CLEARS ``repudiated``
# (`_apply_obpi_receipt_metadata` sets ledger_completed=True and repudiated=False
# on a later receipt). Reading the ever-seen event set would therefore pool a
# foundation whose only work was legitimately re-completed — deleting real work
# to tidy the partition, the one thing the parent ADR forbids outright.
#
# ``get_artifact_graph`` IS the canonical last-event-wins projection of those
# events, so these flags are not a re-inlined negation set — they are the
# temporal resolution of it. ``withdrawn`` and ``superseded`` are one-way
# latches (their appliers never clear); ``repudiated`` is two-way.
# ``obpi_parked`` is deliberately absent: parking is reversible on re-promotion
# and is not a negation of completed work.
_NEGATION_FLAGS: tuple[str, ...] = ("withdrawn", "repudiated", "superseded")


def _obpi_tally(
    graph: dict[str, dict[str, Any]],
    adr_id: str,
    ledger: Ledger,
) -> tuple[int, int]:
    """Return ``(completed, live)`` OBPI counts for ``adr_id`` from Layer-2 only.

    See ``_NEGATION_FLAGS`` for why current graph flags — not the ever-seen
    ``TERMINAL_EVENTS`` set — are the correct read.
    """
    canonical = ledger.canonicalize_id(adr_id)
    info = graph.get(canonical) or graph.get(adr_id) or {}
    completed = 0
    live = 0
    for child in info.get("children", []):
        child_info = graph.get(child) or {}
        if child_info.get("type") != "obpi":
            continue
        if any(child_info.get(flag) for flag in _NEGATION_FLAGS):
            continue
        live += 1
        if child_info.get("ledger_completed"):
            completed += 1
    return completed, live


def foundation_rows(project_root: Path, ledger: Ledger) -> tuple[FoundationRow, ...]:
    """Read every on-disk foundation package and tally its Layer-2 completions.

    FAIL-CLOSED on Layer-1 identity incoherence. Frontmatter ``id`` is the
    load-bearing ledger join, so a package that cannot supply one would silently
    vanish from BOTH sides of the partition — never demoted, never grandfathered,
    still flagged by the closed-kind gate — while the migration reported success.
    A silent skip in front of an rmtree-capable loop is the defect; the missing
    key is only its trigger.
    """
    config = GzkitConfig.load(project_root / ".gzkit.json")
    foundation_dir = project_root / config.paths.adrs / "foundation"
    if not foundation_dir.is_dir():
        return ()
    graph = ledger.get_artifact_graph()
    rows: list[FoundationRow] = []
    problems: list[str] = []
    seen_ids: dict[str, str] = {}
    packages = sorted(p for p in foundation_dir.iterdir() if p.is_dir())
    for package in packages:
        rel = package.relative_to(project_root).as_posix()
        adr_files = [p for p in sorted(package.glob("ADR-*.md")) if "CLOSEOUT" not in p.name]
        if len(adr_files) != 1:
            problems.append(f"{rel}: expected exactly one ADR document, found {len(adr_files)}")
            continue
        text = adr_files[0].read_text(encoding="utf-8")
        frontmatter = _parse_simple_frontmatter(text)
        adr_id = frontmatter.get("id", "")
        semver = frontmatter.get("semver", "")
        if not adr_id:
            problems.append(f"{rel}: frontmatter has no `id` — the ledger join is unresolvable")
            continue
        if not semver:
            problems.append(f"{rel}: frontmatter has no `semver`")
            continue
        # IDENTITY BIJECTION (not merely a count). A frontmatter id that disagrees
        # with the package directory, the filename, or its own semver makes the
        # ledger join resolve to the WRONG node — which reads as zero completions
        # and destructively pools a foundation holding attested work. Counting
        # rows cannot catch that; only comparing identities can.
        if package.name != adr_id:
            problems.append(
                f"{rel}: frontmatter id `{adr_id}` does not match its package directory "
                f"`{package.name}` — the ledger join would resolve to the wrong node"
            )
            continue
        if adr_files[0].stem != adr_id:
            problems.append(
                f"{rel}: frontmatter id `{adr_id}` does not match its filename "
                f"`{adr_files[0].name}`"
            )
            continue
        if not adr_id.startswith(f"ADR-{semver}-"):
            problems.append(
                f"{rel}: frontmatter id `{adr_id}` is inconsistent with semver `{semver}`"
            )
            continue
        if adr_id in seen_ids:
            problems.append(f"{rel}: duplicate ADR id `{adr_id}` (also in {seen_ids[adr_id]})")
            continue
        if ledger.canonicalize_id(adr_id) not in graph and adr_id not in graph:
            problems.append(
                f"{rel}: `{adr_id}` has no Layer-2 graph node — its completion tally "
                f"would read as zero for want of ledger presence, not for want of work"
            )
            continue
        seen_ids[adr_id] = rel
        completed, live = _obpi_tally(graph, adr_id, ledger)
        briefs = tuple(sorted((package / "obpis").glob("OBPI-*.md")))
        rows.append(
            FoundationRow(
                id=adr_id,
                title=_extract_h1_title(text),
                semver=semver,
                package=package,
                completed_obpis=completed,
                live_obpis=live,
                brief_paths=briefs,
            )
        )
    if problems:
        raise RuntimeError(
            "BLOCKERS: Layer-1 identity incoherence in the foundation tree — "
            + " | ".join(problems)
        )
    if len(rows) != len(packages):  # pragma: no cover - defended by `problems` above
        raise RuntimeError(
            f"BLOCKERS: partition is not a bijection with on-disk packages "
            f"({len(rows)} rows vs {len(packages)} packages)"
        )
    return tuple(rows)


def compute_partition(project_root: Path, ledger: Ledger) -> Partition:
    """Partition the foundation set by ledger truth, never by frontmatter.

    A foundation demotes iff ZERO of its live OBPI children carry a Layer-2
    completion. Frontmatter ``status`` is deliberately not consulted: the
    ADR-0.0.37 investigation proved it can claim terminality a foundation has
    not earned.
    """
    rows = foundation_rows(project_root, ledger)
    demote = tuple(row for row in rows if row.completed_obpis == 0)
    grandfather = tuple(row for row in rows if row.completed_obpis > 0)
    return Partition(demote=demote, grandfather=grandfather)


def _closeout_witnessed_adr_prefixes(ledger: Ledger) -> set[str]:
    """Return ``ADR-X.Y.Z`` prefixes carrying a Layer-2 ADR closeout witness.

    Child-OBPI completion equality is NOT proof the parent ADR was closed out —
    an ADR whose every child finished can still be un-attested. The witness is
    the ADR's own ``audit_receipt_emitted`` event, which `gz closeout` writes.
    """
    # Resolve from CANONICAL GRAPH STATE, not from an event discriminator.
    #
    # Filtering `audit_receipt_emitted` on `receipt_event == 'validated'` rejects
    # bookkeeping receipts like `meta-receipt-bind`, but it still accepts a
    # `validated` receipt whose own evidence says `adr_completion='not_completed'`
    # — measured: such a receipt produced zero blockers while the graph's
    # `validated` flag was False. The graph replay is the authority on whether an
    # ADR is validated; an event's presence is not.
    graph = ledger.get_artifact_graph()
    witnessed: set[str] = set()
    for node_id, info in graph.items():
        if not info.get("validated"):
            continue
        match = _ADR_SHORT_ID_RE.match(str(node_id))
        if match:
            witnessed.add(match.group(1))
    return witnessed


def check_blockers(project_root: Path, ledger: Ledger) -> list[str]:
    """Return human-readable blockers; empty means the tree is terminal.

    FAIL-CLOSED on three states, not one. Brief Requirement 1 forbids applying
    before the Sunset prerequisites are terminal, so an *absent* prerequisite and
    an *un-attested* one are blockers just as much as a partly-finished one —
    silence on either would let the migration populate over a non-terminal tree
    and false-red the terminal-partition gate the moment OBPI-05 wires it.
    """
    by_short: dict[str, FoundationRow] = {}
    for row in foundation_rows(project_root, ledger):
        match = _ADR_SHORT_ID_RE.match(row.id)
        if match:
            by_short[match.group(1)] = row
    witnessed = _closeout_witnessed_adr_prefixes(ledger)
    blockers: list[str] = []
    for prerequisite in _SUNSET_PREREQUISITES:
        row = by_short.get(prerequisite)
        if row is None:
            blockers.append(
                f"{prerequisite} is a declared Sunset prerequisite but no such foundation "
                f"package is on disk — cannot confirm it is terminal."
            )
            continue
        if 0 < row.completed_obpis < row.live_obpis:
            blockers.append(
                f"{prerequisite} is in Pending-with-attested-work limbo "
                f"({row.completed_obpis}/{row.live_obpis} OBPIs complete) — close it out "
                f"with `uv run gz closeout {prerequisite}` before populating the manifest."
            )
            continue
        if prerequisite not in witnessed:
            blockers.append(
                f"{prerequisite} carries no Layer-2 `audit_receipt_emitted` closeout "
                f"witness ({row.completed_obpis}/{row.live_obpis} OBPIs complete). Child "
                f"completion is not ADR closeout — run `uv run gz closeout {prerequisite}`."
            )
    return blockers


def _journal_path(project_root: Path) -> Path:
    """Where the write-ahead demotion journal lives (regenerable, gitignored)."""
    return project_root / "artifacts" / "receipts" / "foundation-sunset-journal.json"


def interrupted_demotions(project_root: Path, ledger: Ledger) -> list[str]:
    """Return journaled demotions that never completed — the stranding signature.

    ``_apply_demote`` writes the pool file, THEN rmtree's the source package, THEN
    appends the ``artifact_renamed`` and ``obpi_parked`` events. An interruption
    inside that window leaves the source gone with no rename and no parking
    events, so the old ADR node survives in Layer-2 with its children pointing at
    a parent id that no longer resolves on disk — precisely the 237-record
    stranding GHI #520 recorded, which this ADR exists to finish cleaning up.

    A retry alone cannot detect it: the vanished package is absent from
    ``foundation_rows``, so the migration recomputes over the REDUCED tree and
    reports a clean, seam-neutral success. The journal is what makes the gap
    visible; without it the failure is silent by construction.
    """
    journal = _journal_path(project_root)
    if not journal.is_file():
        return []
    try:
        planned = json.loads(journal.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [f"{journal.name} is unreadable — cannot confirm the last apply completed"]
    events = list(ledger.read_all())
    renamed = {str(event.id) for event in events if event.event == "artifact_renamed"}
    parked = {str(event.id) for event in events if event.event == "obpi_parked"}
    config = GzkitConfig.load(project_root / ".gzkit.json")
    foundation_dir = project_root / config.paths.adrs / "foundation"
    pool_dir = project_root / config.paths.adrs / "pool"
    stranded: list[str] = []
    for entry in planned.get("demotions", []):
        adr_id = str(entry.get("source_id") or "")
        if not adr_id:
            continue
        expected_children = [str(c) for c in (entry.get("children") or [])]
        if adr_id not in renamed:
            if (foundation_dir / adr_id).is_dir():
                # Nothing destroyed for this entry yet. An outstanding journal
                # over an intact package means a prior apply was interrupted
                # earlier in the loop, or another apply is running concurrently.
                stranded.append(
                    f"{adr_id}: an outstanding migration journal names it while its package is "
                    f"still present — a prior apply did not complete, or a concurrent apply is "
                    f"in flight. Resolve the journal before retrying."
                )
                continue
            recovery = f"git checkout -- {config.paths.adrs}/foundation/{adr_id}"
            leftover = pool_dir / f"ADR-pool.{adr_id.split('-', 2)[2]}.md"
            if leftover.exists():
                # The pool file is written BEFORE the rmtree, so a torn write
                # leaves it behind and a naive re-run dies on a slug collision.
                recovery += f" && rm {leftover.relative_to(project_root).as_posix()}"
            stranded.append(
                f"{adr_id}: package is gone but no `artifact_renamed` event exists — an "
                f"interrupted demotion stranded it (its child OBPIs are unparked). "
                f"Recover with `{recovery}` then re-run."
            )
            continue
        # Renamed, but did every child get parked? A crash between the rename
        # append and the parking appends strands children under a parent id that
        # no longer resolves — the same GHI #520 signature, one phase later.
        unparked = [child for child in expected_children if child not in parked]
        if unparked:
            stranded.append(
                f"{adr_id}: renamed but {len(unparked)} child OBPI(s) were never parked "
                f"({', '.join(unparked[:4])}) — stranded under a parent id that no longer "
                f"resolves. Park them before retrying."
            )
    return stranded


def _write_journal(project_root: Path, plans: list[tuple[FoundationRow, dict[str, Any]]]) -> None:
    """Claim the journal EXCLUSIVELY before the first destructive write.

    ``x`` mode fails if the journal already exists, so two concurrent applies
    cannot both proceed — the second fails closed instead of racing over the same
    packages. Each entry records the child OBPIs the demotion is expected to park,
    which is what lets ``interrupted_demotions`` detect a crash between the rename
    append and the parking appends (a phase a source_id-only journal cannot see).
    """
    journal = _journal_path(project_root)
    journal.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "demotions": [
                {
                    "source_id": row.id,
                    "package": row.package.name,
                    "children": list(plan.get("parked_obpis") or []),
                }
                for row, plan in plans
            ]
        },
        indent=2,
    )
    try:
        with journal.open("x", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    except FileExistsError as exc:
        msg = (
            f"BLOCKERS: a migration journal already exists at "
            f"{journal.relative_to(project_root).as_posix()} — a prior apply did not complete "
            f"or a concurrent apply holds it. Resolve it before retrying."
        )
        raise RuntimeError(msg) from exc


def graph_probe(ledger: Ledger, source_root: Path | None = None) -> dict[str, Any]:
    """Image the corpus subgraph: node/edge counts, seams, and ADR node ids.

    Recorded before AND after the migration so the receipt carries its own
    lineage evidence. Without this the migration mutates the graph the ontology
    images and leaves no diff behind, so REQ-03's "no orphaned lineage" claim
    would rest entirely on a separate manual re-sense. A seam is an edge whose
    endpoint is not a materialized node — precisely an orphaned `@covers`/
    `@surface` or lineage edge after an ADR id changes underneath it.
    """
    from gzkit.commands.ontology import compute_seams
    from gzkit.ontology.unified import project_all

    # project_all (not project_corpus) with an explicit source_root, so the
    # source-anchor domain is composed rather than defaulted.
    #
    # HONEST LIMIT — read before trusting `seam_ids` for anchor claims:
    # project_all's compose step lands edges ONLY on materialized nodes, so an
    # `@covers`/`@surface` edge whose source-unit node was never materialized is
    # DISCARDED before compute_seams ever sees it. Measured: an isolated valid
    # `@covers` anchor yields project_all covers_edges == [] and seams == [] while
    # source fidelity still reports complete=True. A deliberately orphaned anchor
    # edge therefore does NOT surface as a seam. Seam identity is a real but
    # PARTIAL signal, which is why REQ-03's binding assertion is the
    # successor-completeness check in `rename_integrity` below — that one does not
    # depend on the anchor plane being visible.
    projection = project_all(ledger, source_root=source_root)
    graph = projection.graph
    node_ids = set(graph.node_ids())
    seams = compute_seams(graph)
    fidelity = projection.fidelity
    return {
        "node_count": len(node_ids),
        "edge_count": graph.edge_count(),
        "seam_count": len(seams),
        # Seam IDENTITIES, not just the count: a count-only comparison lets one
        # newly introduced seam be masked by one coincidentally resolved
        # pre-existing seam, so the delta could read zero across a real
        # regression.
        "seam_ids": sorted(f"{s.source_id}|{s.target_id}|{s.link_type}" for s in seams),
        "adr_node_ids": sorted(n for n in node_ids if n.startswith("ADR-")),
        # CORPUS fidelity specifically, not the aggregate. The corpus domain is
        # the one that images ADR nodes and the rename, and its `complete=False`
        # means an event discriminator is unaccounted — the migration-relevant
        # risk (this OBPI's own new event type had to be dispositioned there).
        # The aggregate additionally folds in source/OKF completeness, which is
        # structurally absent in a bare fixture tree and says nothing about
        # whether the graph can witness a rename.
        "fidelity_complete": bool(getattr(getattr(fidelity, "corpus", None), "complete", True)),
        # Source fidelity is load-bearing for REQ-03's ANCHOR conjunct: it goes
        # false precisely when a unit failed to parse, which is when the anchor
        # index is silently short. Gating corpus alone was an indefensible
        # narrowing. work/OKF are deliberately excluded — they are unrelated to
        # whether the graph can witness this rename, and are structurally absent
        # in a bare fixture tree.
        "source_fidelity_complete": bool(
            getattr(getattr(fidelity, "source", None), "complete", True)
        ),
        "aggregate_fidelity_complete": bool(getattr(fidelity, "complete", True)),
    }


_REQ_ID_RE = re.compile(r"^REQ-(\d+\.\d+\.\d+)-")


def _fidelity_blockers(probe: dict[str, Any], when: str) -> list[str]:
    """Blockers for an untrustworthy projection, checked BEFORE and AFTER."""
    blockers: list[str] = []
    if not probe.get("fidelity_complete", True):
        blockers.append(
            f"corpus rebuild fidelity is incomplete {when} the migration — an event "
            f"discriminator is unaccounted, so the graph cannot be trusted to witness the "
            f"rename. Disposition it in gzkit.ontology.corpus."
        )
    if not probe.get("source_fidelity_complete", True):
        blockers.append(
            f"source parse fidelity is incomplete {when} the migration — an unparseable "
            f"unit drops its anchors, so the dangling-anchor check ran over a short index."
        )
    return blockers


def anchor_integrity(project_root: Path, partition: Partition) -> list[str]:
    """Fail if any live `@covers`/`@surface` anchor targets a REQ being deleted.

    This is REQ-03's ANCHOR conjunct, and it is checked DIRECTLY rather than via
    seam analysis because `graph_probe` cannot see the failure: project_all's
    compose step discards an anchor edge whose source-unit node was never
    materialized, so an orphaned anchor yields ``covers_edges == []`` and
    ``seams == []`` while fidelity still reports complete. Measured, not assumed.

    Demotion rmtree's each demoted package including its ``obpis/`` briefs, so
    every REQ declared by those briefs ceases to exist. A source anchor still
    pointing at one is a dangling `@covers`/`@surface` edge by definition — which
    is exactly what REQ-03 excludes. Reading the anchor index answers that
    question without needing the projection to retain the edge.
    """
    from gzkit.ontology.source import build_source_anchor_index

    doomed_semvers = {row.semver for row in partition.demote}
    if not doomed_semvers:
        return []
    # Tier-B, regenerable, and read WITHOUT writing: never mutate a cache here.
    index = build_source_anchor_index(project_root, write=False)
    problems: list[str] = []
    if index.parse_failures:
        # An unparseable unit drops its anchors from the index, so "no doomed
        # anchors found" over an incomplete scan is not evidence of absence —
        # it is absence of evidence, immediately before a destructive deletion.
        problems.append(
            f"{len(index.parse_failures)} source unit(s) failed to parse, so their anchors "
            f"are missing from the index and cannot be checked against the deleted briefs: "
            f"{', '.join(index.parse_failures[:5])}"
        )
    for anchor in index.anchors:
        match = _REQ_ID_RE.match(anchor.req_id)
        if match and match.group(1) in doomed_semvers:
            problems.append(
                f"{anchor.source_path}:{anchor.line} anchors `{anchor.anchor_kind}` at "
                f"`{anchor.req_id}`, whose brief is in a package this migration deletes — "
                f"the anchor would dangle"
            )
    return problems


def rename_integrity(
    expected: dict[str, str], before: dict[str, Any], after: dict[str, Any]
) -> list[str]:
    """Assert every expected ``old -> ADR-pool.slug`` rename landed in Layer-2.

    This is REQ-03's binding proof, and deliberately does NOT rely on seam
    analysis: `graph_probe` cannot see a dangling anchor edge (see its docstring),
    so a seam-only check is structurally incapable of observing the failure REQ-03
    excludes. Successor-completeness is observable either way — "no removed corpus
    node left without a successor" is exactly what the REQ says.

    A removed node with no successor is the GHI #520 stranding signature; a node
    that failed to disappear means the rename never transacted at all.
    """
    problems: list[str] = []
    before_nodes = set(before["adr_node_ids"])
    after_nodes = set(after["adr_node_ids"])
    for old_id, new_id in sorted(expected.items()):
        if old_id not in before_nodes:
            # NOT a silent waiver. An expected demotion absent from the pre-image
            # means the graph never carried the node the migration is about to
            # delete on disk, so nothing can verify its successor — an unprovable
            # rename, not a trivially-satisfied one.
            problems.append(
                f"{old_id}: expected demotion is absent from the pre-migration graph, so its "
                f"rename cannot be verified — the partition and Layer-2 disagree"
            )
            continue
        if old_id in after_nodes:
            problems.append(
                f"{old_id}: still a live graph node after demotion — the rename did not transact"
            )
        if new_id not in after_nodes:
            problems.append(
                f"{old_id}: removed with no successor `{new_id}` in the graph — orphaned lineage "
                f"(the GHI #520 stranding signature)"
            )
    orphaned = (before_nodes - after_nodes) - set(expected)
    for node in sorted(orphaned):
        problems.append(f"{node}: disappeared from the graph but was not an expected demotion")
    return problems


def _grandfathered_ids(ledger: Ledger) -> set[str]:
    """Return ADR ids already carrying a ``foundation_grandfathered`` witness.

    Read so emission is idempotent: REQ-02 requires exactly one witness per
    manifest entry, and a retry after a partial apply must not append a second.
    """
    return {
        str(event.id)
        for event in ledger.read_all()
        if event.event == "foundation_grandfathered" and event.id
    }


def rename_map(partition: Partition) -> dict[str, str]:
    """Return the ``ADR-0.0.X-slug -> ADR-pool.slug`` rename the demotions perform.

    The ontology corpus subgraph tracks ADR ids, so this map is the exact node
    relabelling the re-sense diff must account for: every removed node needs a
    successor, and every edge touching a removed node must be relabelled with it
    or it is left dangling.
    """
    from gzkit.commands.adr_demote import _derive_pool_slug_from_adr_id

    return {row.id: f"ADR-pool.{_derive_pool_slug_from_adr_id(row.id)}" for row in partition.demote}


def build_manifest_entries(partition: Partition, frozen_at: str) -> list[dict[str, str]]:
    """Render the IDENTITY-ONLY grandfather manifest rows.

    No lifecycle field: lifecycle is a Layer-2 fact read live from the ledger.
    Baking it into this committed Layer-1 file is the state-doctrine drift the
    ADR-0.0.37 frontmatter-lie demonstrated.
    """
    return [
        {
            "id": row.id,
            "title": row.title,
            "semver": row.semver,
            "frozen_at": frozen_at,
        }
        for row in partition.grandfather
    ]


def _collision_disposition(pool_dir: Path, row: FoundationRow) -> tuple[str, str | None]:
    """Decide how a pool-slug collision may be resolved, or refuse it.

    Returns ``(on_collision, refusal_or_None)``.

    A collision has two very different causes and only ONE is safe:

    * **Promotion round-trip** — the existing pool file's ``promoted_to:`` names
      the very ADR being demoted. This foundation *came from* that pool entry,
      which was retained as historical intake context. Demoting is the return
      leg, so ``keep-pool`` is correct: the intake record stays and its stale
      promotion marker is reversed.
    * **Unrelated slug clash** — two different ADRs deriving the same pool slug.
      Here ``keep-pool`` would keep the OTHER ADR's file and never write this
      one's body, silently destroying the Intent/Decision content REQ-01 requires
      be preserved. That must fail closed, not resolve.

    ``_build_demote_plan``'s own GHI #558 guard governs only whether the marker is
    *reversed*; it does not stop ``keep-pool`` from discarding the body. So the
    distinction has to be made here, before the plan is built.
    """
    from gzkit.commands.adr_demote import _derive_pool_slug_from_adr_id

    target = pool_dir / f"ADR-pool.{_derive_pool_slug_from_adr_id(row.id)}.md"
    if not target.exists():
        return "fail", None
    frontmatter = _parse_simple_frontmatter(target.read_text(encoding="utf-8"))
    if frontmatter.get("promoted_to", "") == row.id:
        return "keep-pool", None
    return "fail", (
        f"{row.id}: pool slug collision with {target.name}, which was NOT promoted from "
        f"this ADR (promoted_to={frontmatter.get('promoted_to') or 'absent'!r}). Resolving "
        f"it as keep-pool would discard this foundation's Intent/Decision body — refusing."
    )


def preflight_demotions(
    project_root: Path, config: Any, ledger: Ledger, partition: Partition
) -> list[tuple[FoundationRow, dict[str, Any]]]:
    """Build and validate EVERY demotion plan before the first write.

    ``_apply_demote`` rmtree's one package at a time, so a plan that only fails
    on demotion 12 of 23 leaves a half-migrated tree. Building all plans up front
    turns a partial-failure mode into a clean refusal. This also re-imposes the
    dependent-children guard that ``adr_demote_cmd`` enforces at the CLI boundary
    (``SystemExit(3)`` unless ``--force``) — driving the lower seams directly
    would otherwise silently orphan any ADR naming a demoted foundation as
    ``parent:``.
    """
    from gzkit.commands.adr_demote import _build_demote_plan
    from gzkit.commands.common import GzCliError

    pool_dir = project_root / config.paths.adrs / "pool"
    plans: list[tuple[FoundationRow, dict[str, Any]]] = []
    problems: list[str] = []
    for row in partition.demote:
        on_collision, refusal = _collision_disposition(pool_dir, row)
        if refusal:
            problems.append(refusal)
            continue
        try:
            plan = _build_demote_plan(
                project_root,
                config,
                row.id,
                _DEMOTE_GHI,
                _DEMOTE_NOTE,
                _DEMOTE_OPERATOR,
                on_collision=on_collision,
                ledger=ledger,
            )
        except GzCliError as exc:
            problems.append(f"{row.id}: {exc}")
            continue
        children = list(plan.get("children") or [])
        if children:
            problems.append(
                f"{row.id}: {len(children)} ADR(s) name it as parent and would be "
                f"orphaned: {', '.join(children)}"
            )
            continue
        plans.append((row, plan))
    if problems:
        raise RuntimeError(
            "BLOCKERS: demotion preflight failed — no package was touched. " + " | ".join(problems)
        )
    return plans


def _demote_one(
    project_root: Path,
    ledger: Ledger,
    row: FoundationRow,
    plan: dict[str, Any],
    task_id: str | None = None,
) -> dict[str, Any]:
    """Apply one pre-validated demotion plan, attributing it to ``task_id``."""
    from gzkit.commands.adr_demote import _apply_demote

    _apply_demote(ledger, plan, task_id=task_id)
    return {
        "source_id": row.id,
        "new_id": plan["new_id"],
        "target_file": Path(plan["target_file"]).relative_to(project_root).as_posix(),
        "removed_dir": Path(plan["source_dir"]).relative_to(project_root).as_posix(),
        "parked_obpis": list(plan.get("parked_obpis", [])),
        "deleted_briefs": [p.relative_to(project_root).as_posix() for p in row.brief_paths],
    }


def _perform_writes(
    *,
    project_root: Path,
    config: Any,
    ledger: Ledger,
    partition: Partition,
    entries: list[dict[str, str]],
    manifest_text: str,
    already_witnessed: set[str],
    attestor: str,
    task_id: str | None,
    receipt: dict[str, Any],
) -> None:
    """The destructive half: demote, witness, populate. Ordering is load-bearing.

    Preflight validates EVERY demotion before the first rmtree, and the
    write-ahead journal is claimed before the first destructive write — an
    interruption is otherwise undetectable on retry. The journal is deliberately
    NOT discharged here: it is the only recovery signal for a partial apply, so it
    must outlive the postcondition checks its caller runs. Clearing it here would
    delete the evidence exactly when a failed postcondition means it is needed.
    """
    from gzkit.ledger_events import foundation_grandfathered_event

    plans = preflight_demotions(project_root, config, ledger, partition)
    _write_journal(project_root, plans)
    for row, plan in plans:
        receipt["demotions"].append(_demote_one(project_root, ledger, row, plan, task_id))
    for entry in entries:
        if entry["id"] in already_witnessed:
            # Idempotent: REQ-02 requires EXACTLY ONE witness per entry, so a
            # retry after a partial run must not append a second.
            continue
        ledger.append(
            foundation_grandfathered_event(
                adr_id=entry["id"],
                title=entry["title"],
                semver=entry["semver"],
                frozen_at=entry["frozen_at"],
                attestor=attestor,
            )
        )
        receipt["grandfathered_events"].append(entry["id"])
    manifest_path = project_root / _MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest_text, encoding="utf-8")
    golden_path = project_root / _GOLDEN_REL
    if golden_path.parent.is_dir():
        # The tamper guard is a byte comparison, so the fixture moves with the
        # data it pins — that co-edit is what keeps the guard honest.
        golden_path.write_text(manifest_text, encoding="utf-8")


def _graph_diff(receipt: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    """Compare the pre- and post-migration graph probes."""
    before, after = receipt["graph_before"], receipt["graph_after"]
    return {
        "removed_adr_nodes": sorted(set(before["adr_node_ids"]) - set(after["adr_node_ids"])),
        "added_adr_nodes": sorted(set(after["adr_node_ids"]) - set(before["adr_node_ids"])),
        "seam_delta": after["seam_count"] - before["seam_count"],
        # Identity-based, so a resolved pre-existing seam cannot mask a new one.
        "new_seam_ids": sorted(set(after["seam_ids"]) - set(before["seam_ids"])),
        # REQ-03's binding assertion — independent of anchor-plane visibility.
        # Successor-completeness verifies the OUTCOME of an apply; on a dry-run
        # nothing transacted by design, so every planned rename would read as
        # un-transacted — a false red, not a finding.
        "successor_problems": []
        if dry_run
        else rename_integrity(receipt["rename_map"], before, after),
        "fidelity_complete": after["fidelity_complete"],
    }


def _postcondition_blockers(diff: dict[str, Any]) -> list[str]:
    """Blockers derived from the post-migration graph diff."""
    blockers: list[str] = [*diff["successor_problems"]]
    new_seams = diff["new_seam_ids"]
    if new_seams:
        # The migration must not orphan lineage. Surface it in the receipt rather
        # than leaving the regression for a later manual re-sense to discover.
        blockers.append(
            f"ontology regression: the migration introduced {len(new_seams)} new "
            f"seam(s) — orphaned lineage or dangling anchor edges: "
            f"{', '.join(new_seams[:5])}"
        )
    return blockers


def run_migration(
    *,
    project_root: Path,
    receipt_dir: Path,
    dry_run: bool,
    attestor: str = "",
    attestation: str = "",
    now: datetime | None = None,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Execute (or preview) the sunset migration and write a JSON receipt.

    The prerequisite roster is deliberately NOT a parameter: a
    production-callable ``prerequisites=()`` argument disables the mandatory
    pre-migration gate exactly as a fixture does, with no boundary distinguishing
    them — a bypass around a STOP-on-BLOCKERS requirement. Tests patch
    ``_SUNSET_PREREQUISITES`` within test scope instead.
    """

    if not dry_run and not (attestor.strip() and attestation.strip()):
        # The witness binds HERE, at the library boundary — not only in the CLI
        # wrapper. The taxonomy reader accepts any foundation_grandfathered event
        # with a non-empty id and never inspects the attestor, so an unbound
        # library call would satisfy the SUPPORT gate with no human witness: the
        # exact fabrication surface ADR-0.34.0 exists to close.
        raise ValueError(
            "--apply requires a non-empty attestor AND attestation text. The Gate-5 "
            "human attestation IS the terminality witness for pre-ledger foundations; "
            "emitting these events without it would fabricate the witness."
        )

    config = GzkitConfig.load(project_root / ".gzkit.json")
    ledger = Ledger(project_root / config.paths.ledger)
    stamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H-%M-%SZ")
    frozen_at = (now or datetime.now(UTC)).strftime("%Y-%m-%d")

    blockers = [
        *interrupted_demotions(project_root, ledger),
        *check_blockers(project_root, ledger),
    ]
    if blockers and not dry_run:
        # STOP-on-BLOCKERS: fail closed BEFORE any write, per brief Requirement 1.
        raise RuntimeError("BLOCKERS: " + " | ".join(blockers))

    partition = compute_partition(project_root, ledger)
    entries = build_manifest_entries(partition, frozen_at)
    manifest_text = json.dumps(entries, indent=2) + "\n"

    receipt: dict[str, Any] = {
        "timestamp": stamp,
        "dry_run": dry_run,
        "attestor": attestor,
        "attestation": attestation,
        "blockers": blockers,
        "foundations_total": partition.total,
        "demote_count": len(partition.demote),
        "grandfather_count": len(partition.grandfather),
        "demote_roster": [
            {"id": row.id, "semver": row.semver, "briefs": len(row.brief_paths)}
            for row in partition.demote
        ],
        "grandfather_roster": entries,
        "deleted_brief_count": sum(len(row.brief_paths) for row in partition.demote),
        "deleted_briefs": [
            p.relative_to(project_root).as_posix()
            for row in partition.demote
            for p in row.brief_paths
        ],
        "demotions": [],
        "grandfathered_events": [],
        "rename_map": rename_map(partition),
    }

    already_witnessed = _grandfathered_ids(ledger)
    receipt["already_witnessed"] = sorted(already_witnessed & {e["id"] for e in entries})
    receipt["graph_before"] = graph_probe(ledger, project_root)

    # REQ-03's anchor conjunct, checked BEFORE any write so a dangling-anchor
    # migration is refused rather than reported after the fact.
    anchor_problems = anchor_integrity(project_root, partition)
    receipt["anchor_problems"] = anchor_problems
    if anchor_problems:
        receipt["blockers"] = [*receipt["blockers"], *anchor_problems]
    receipt["blockers"] = [
        *receipt["blockers"],
        *_fidelity_blockers(receipt["graph_before"], "before"),
    ]
    if receipt["blockers"] and not dry_run:
        raise RuntimeError("BLOCKERS: " + " | ".join(receipt["blockers"]))

    if not dry_run:
        _perform_writes(
            project_root=project_root,
            config=config,
            ledger=ledger,
            partition=partition,
            entries=entries,
            manifest_text=manifest_text,
            already_witnessed=already_witnessed,
            attestor=attestor,
            task_id=task_id,
            receipt=receipt,
        )

    receipt["graph_after"] = graph_probe(ledger, project_root)
    receipt["graph_diff"] = _graph_diff(receipt, dry_run)
    receipt["blockers"] = [*receipt["blockers"], *_postcondition_blockers(receipt["graph_diff"])]

    receipt_dir_abs = project_root / receipt_dir if not receipt_dir.is_absolute() else receipt_dir
    receipt_dir_abs.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir_abs / f"foundation-sunset-migration-{stamp}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = receipt_path.relative_to(project_root).as_posix()
    if not dry_run:
        if receipt["blockers"]:
            # A failed postcondition after a destructive apply: KEEP the journal
            # so the partial state stays recoverable, and refuse rather than
            # returning a receipt that reads like success.
            raise RuntimeError(
                "BLOCKERS after apply (journal retained for recovery at "
                f"{_journal_path(project_root).relative_to(project_root).as_posix()}): "
                + " | ".join(receipt["blockers"])
            )
        # Only now is every postcondition satisfied and the receipt persisted —
        # the write-ahead record has genuinely been discharged.
        _journal_path(project_root).unlink(missing_ok=True)
    return receipt


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the one-shot sunset migration."""
    parser = argparse.ArgumentParser(
        prog="python -m gzkit.foundation.sunset_migrate",
        description="Execute the ADR-0.34.0 Foundation Sunset migration.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Write changes to disk.")
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without writing (default).",
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--attestor", default="", help="Gate-5 human witness (required for --apply)."
    )
    parser.add_argument(
        "--attestation", default="", help="Gate-5 attestation text (required for --apply)."
    )
    args = parser.parse_args(argv)

    dry_run = not args.apply
    if args.apply and not (args.attestor.strip() and args.attestation.strip()):
        print(  # noqa: T201
            "BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human "
            "attestation IS the terminality witness for pre-ledger foundations; without it the "
            "backfill has no legitimate witness.",
            file=sys.stderr,
        )
        return 2

    project_root = args.project_root.resolve()
    try:
        receipt = run_migration(
            project_root=project_root,
            receipt_dir=Path("artifacts") / "receipts",
            dry_run=dry_run,
            attestor=args.attestor,
            attestation=args.attestation,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)  # noqa: T201
        return 3

    mode_label = "DRY-RUN" if dry_run else "APPLIED"
    print(  # noqa: T201
        f"{mode_label}: {receipt['foundations_total']} foundations — "
        f"{receipt['demote_count']} demote, {receipt['grandfather_count']} grandfather; "
        f"{receipt['deleted_brief_count']} OBPI brief(s) removed by demotion."
    )
    print(f"Receipt: {receipt['receipt_path']}")  # noqa: T201
    if receipt["blockers"]:
        for blocker in receipt["blockers"]:
            print(f"  BLOCKER: {blocker}", file=sys.stderr)  # noqa: T201
        # Exit non-zero: a recorded blocker that still exits 0 is a green-looking
        # run over a red result — the staging-flag anti-pattern in miniature.
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover - module entrypoint
    sys.exit(main())
