"""Command modules extracted from cli.py."""

from gzkit.commands.attest import attest
from gzkit.commands.plan import plan_cmd
from gzkit.commands.state import state, state_repair
from gzkit.commands.status import adr_status_cmd, status

COMMAND_REGISTRY: dict[str, object] = {
    "plan": plan_cmd,
    "attest": attest,
    "state": state,
    "state_repair": state_repair,
    "status": status,
    "adr-status": adr_status_cmd,
}
