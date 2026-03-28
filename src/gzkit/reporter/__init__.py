"""Reporter module — centralized Rich rendering for gzkit CLI output.

Pure rendering layer: data in, Rich renderables out. No IO, no ledger,
no business logic. OutputFormatter (cli/formatters.py) handles mode routing.
"""

from gzkit.reporter.panels import ceremony_panel
from gzkit.reporter.presets import ColumnDef, kv_table, list_table, status_table

__all__ = [
    "ColumnDef",
    "ceremony_panel",
    "kv_table",
    "list_table",
    "status_table",
]
