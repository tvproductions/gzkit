"""Documentation cross-coverage scanner for CLI commands."""

from gzkit.doc_coverage.manifest import (
    CommandEntry,
    DocCoverageManifest,
    SurfaceRequirements,
    find_undeclared_commands,
    load_manifest,
)
from gzkit.doc_coverage.models import CommandCoverage, CoverageReport, OrphanedDoc, SurfaceResult
from gzkit.doc_coverage.scanner import check_surfaces_report, scan_cli_commands

__all__ = [
    "CommandCoverage",
    "CommandEntry",
    "CoverageReport",
    "DocCoverageManifest",
    "OrphanedDoc",
    "SurfaceRequirements",
    "SurfaceResult",
    "check_surfaces_report",
    "find_undeclared_commands",
    "load_manifest",
    "scan_cli_commands",
]
