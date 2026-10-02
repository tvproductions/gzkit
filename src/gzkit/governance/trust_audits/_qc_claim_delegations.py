"""Per-claim ``delegates_to`` declarations for the qc negative-control claims (GHI #1155).

Split from the registration table for the reason ``_qc_claim_exemptions`` is: a control
wires a fixture to a gate, while a delegation states where that gate's verdict is decided.

**The bar.** A claim declares the command its control drives when that control launches a
subprocess whose exit and output decide the verdict. Its shim's gzkit imports then locate
or launch the command (``chores._resolve_chore_dir``, ``quality.run_command``), so the
derived ``gate_targets`` named that plumbing as the gate (GHI #1155 (d), ``module-size``
and ``tautological-debt``), and an empty tuple could not say "out of process" because it
also means the entrypoint is the gate. A declared delegation clears ``gate_targets``.

Each value names the command as the control runs it, never as the ``gz check`` step runs
it: where the two differ, that divergence is a finding about the control, and writing the
step's command here would hide it.
"""

from __future__ import annotations

_CHORE_SCRIPT = "chore script {}"

QC_CLAIM_DELEGATIONS: dict[str, str] = {
    "lint": "uv run ruff check .",
    "format": "uv run ruff format --check .",
    "typecheck": "uv run ty check .",
    "test": "uv run -m unittest discover tests",
    "behave": "python -m behave",
    "module-size": _CHORE_SCRIPT.format("module-sloc-cap-radon/check_module_size.py"),
    "tautological-debt": _CHORE_SCRIPT.format(
        "decommission-tautological-tests/check_debt_target.py"
    ),
    "tautological-debt-waived": _CHORE_SCRIPT.format(
        "decommission-tautological-tests/check_debt_target.py"
    ),
    "validator-reachability": _CHORE_SCRIPT.format(
        "control-surface-validator-reachability/check_reachability.py"
    ),
    "validator-reachability-disclosed": _CHORE_SCRIPT.format(
        "control-surface-validator-reachability/check_reachability.py"
    ),
    "ledger-vocabulary-inertness": _CHORE_SCRIPT.format(
        "ledger-vocabulary-inertness/check_ledger_inertness.py"
    ),
    "ledger-vocabulary-inertness-disclosed": _CHORE_SCRIPT.format(
        "ledger-vocabulary-inertness/check_ledger_inertness.py"
    ),
    "skill-audit": "python -m gzkit skill audit",
    "parity-check": "python -m gzkit parity check",
    "readiness-audit": "python -m gzkit readiness audit --json",
    "cli-audit": "python -m gzkit cli audit",
    "preflight": "python -m gzkit preflight",
}
