"""gzkit.mx — Maintenance Hangar (MX mode) surfaces (ADR-0.0.74).

OBPI-0.0.74-01 ships the marker: the single filesystem truth-source for MX mode.
"""

from gzkit.mx import marker
from gzkit.mx.marker import Marker, is_active, is_valid, marker_path, read, write

__all__ = [
    "Marker",
    "is_active",
    "is_valid",
    "marker",
    "marker_path",
    "read",
    "write",
]
