"""Documentation cross-coverage scanner for CLI commands."""

from gzkit.doc_coverage.manifest import (
    MANPAGE_DIR,
    MANPAGE_INDEX,
    CommandEntry,
    DocCoverageManifest,
    SurfaceRequirements,
    find_undeclared_commands,
    load_manifest,
    manpage_path_for,
)
from gzkit.doc_coverage.models import (
    CommandCoverage,
    CoverageReport,
    DocCoverageGapReport,
    GapItem,
    OrphanedDoc,
    OrphanedDocItem,
    SurfaceResult,
)
from gzkit.doc_coverage.runner import build_gap_report, run_doc_coverage
from gzkit.doc_coverage.scanner import check_surfaces_report, scan_cli_commands

__all__ = [
    "MANPAGE_DIR",
    "MANPAGE_INDEX",
    "CommandCoverage",
    "CommandEntry",
    "CoverageReport",
    "DocCoverageGapReport",
    "DocCoverageManifest",
    "GapItem",
    "OrphanedDoc",
    "OrphanedDocItem",
    "SurfaceRequirements",
    "SurfaceResult",
    "build_gap_report",
    "check_surfaces_report",
    "find_undeclared_commands",
    "load_manifest",
    "manpage_path_for",
    "run_doc_coverage",
    "scan_cli_commands",
]
