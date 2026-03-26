"""Documentation cross-coverage scanner for CLI commands."""

from gzkit.doc_coverage.models import CommandCoverage, CoverageReport, OrphanedDoc, SurfaceResult
from gzkit.doc_coverage.scanner import check_surfaces_report, scan_cli_commands

__all__ = [
    "CommandCoverage",
    "CoverageReport",
    "OrphanedDoc",
    "SurfaceResult",
    "check_surfaces_report",
    "scan_cli_commands",
]
