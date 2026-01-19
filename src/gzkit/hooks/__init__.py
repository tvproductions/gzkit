"""Hook infrastructure for multi-agent governance enforcement.

Hooks are triggered after agent tool use to record governance events.
"""

from gzkit.hooks.core import (
    is_governance_artifact,
    record_artifact_edit,
    run_light_validation,
)
from gzkit.hooks.guards import forbid_pytest

__all__ = [
    "is_governance_artifact",
    "record_artifact_edit",
    "run_light_validation",
    "forbid_pytest",
]
