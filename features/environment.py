"""Behave environment hooks for isolated BDD scenarios."""

from __future__ import annotations

import os

# Neutralize ambient color-forcing at environment-module import — which behave
# loads BEFORE any step module — so the pop lands ahead of the step files'
# ``from gzkit.cli import main``. That import constructs the module-level
# ``gzkit.commands.common.console`` singleton, which reads ``FORCE_COLOR`` once
# at import time and freezes ``force_terminal``. Modern terminals (Ghostty)
# export ``FORCE_COLOR=3``; left set, the frozen singleton emits ANSI SGR codes
# — color and bold — into behave's in-process captured output, breaking every
# plain-substring step assertion. A ``before_all`` hook is too late: the
# singleton is already frozen by then. This is the behave analog of
# ``tests/__init__.py`` popping FORCE_COLOR before ``unittest`` imports gzkit.
os.environ.pop("FORCE_COLOR", None)

import logging  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402

# Scenarios whose observable IS a warning — the `--receipt-shape` warn-only path,
# where emitting the record is the behavior under test. Their logs must not reach
# the root logger: `_invoke` runs the CLI in-process under `redirect_stderr`, but
# logging handlers hold the ORIGINAL stream, so warnings bypass the redirect and
# land on real stderr. `gates._print_command_output` then writes that stderr into
# `audit/proofs/gates.txt` unconditionally — pass or fail — so an exercised
# guardrail becomes indistinguishable from an ignored one in the artifact that
# attests Gate 4 (GHI #726).
EXPECTED_WARNING_TAG = "expected-warning"

# Armed at the `gzkit` parent rather than a list of emitter names: a name list is
# a second registry to drift, and the tag is already scenario-scoped. The cost is
# that an UNRELATED gzkit warning inside a tagged scenario is also captured —
# accepted because the tag is narrow and the alternative rots.
_ARMED_LOGGER = "gzkit"


class _ExpectedWarnings(logging.Handler):
    """Collect the warnings a tagged scenario exists to provoke."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def arm_expected_warnings(context, scenario) -> None:
    """Divert `gzkit` warnings into a buffer for scenarios tagged as expecting them."""
    context._expected_warnings = None
    if EXPECTED_WARNING_TAG not in getattr(scenario, "tags", ()):
        return
    logger = logging.getLogger(_ARMED_LOGGER)
    handler = _ExpectedWarnings()
    context._expected_warnings = (logger, handler, logger.propagate)
    logger.addHandler(handler)
    logger.propagate = False


def disarm_expected_warnings(context, scenario) -> None:
    """Restore propagation and fail the scenario if its expected warning never fired.

    Silence is the failure mode that matters here. A capture that tolerates zero
    records is a blanket mute, and the negative control it wraps would keep
    passing after the warn-only path stopped warning at all.
    """
    armed = getattr(context, "_expected_warnings", None)
    context._expected_warnings = None
    if armed is None:
        return
    logger, handler, propagate = armed
    logger.removeHandler(handler)
    logger.propagate = propagate
    if not handler.records:
        raise AssertionError(
            f"Scenario '{getattr(scenario, 'name', '<unknown>')}' is tagged "
            f"@{EXPECTED_WARNING_TAG} but emitted no '{_ARMED_LOGGER}' warning. "
            "The tag asserts a warn-only guardrail fires; capturing nothing means "
            "either the guardrail regressed or the tag is stale — and leaving it "
            "would mute a real warning for free (GHI #726). Next step: run "
            f"`uv run -m behave --name '{getattr(scenario, 'name', '')}'` to see "
            "what the path now emits, then fix the guardrail or drop the tag."
        )


def before_scenario(context, scenario) -> None:
    """Run each scenario in an isolated temporary workspace."""
    context._original_cwd = Path.cwd()
    context._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-behave-"))
    os.chdir(context._tmpdir)
    arm_expected_warnings(context, scenario)


def after_scenario(context, scenario) -> None:
    """Restore cwd, clean up the temporary workspace, and unset env overrides."""
    # A step that calls ``patcher.start()`` without a matching ``stop()`` leaves
    # the patch installed for the REST OF THE PROCESS, and step modules routinely
    # patch by module attribute -- ``mock.patch("<mod>.subprocess.run", ...)``
    # rebinds the singleton ``subprocess`` module's ``run``, so the reach is
    # global, not module-local. Left standing, such a patch silently satisfies a
    # LATER feature's precondition: `features/patch_release.feature` passed in CI
    # only because `evaluation_feedback_loop.feature` ran first and left a fake
    # `gh` behind, and both scenarios failed the moment Behave sharding (GHI #906)
    # put them in different processes. Tearing down here binds patcher lifetime to
    # the scenario that started it, so a scenario's preconditions must be its own.
    mock.patch.stopall()
    os.chdir(context._original_cwd)
    shutil.rmtree(context._tmpdir, ignore_errors=True)
    if hasattr(context, "_orig_arb_receipts_root"):
        if context._orig_arb_receipts_root is None:
            os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
        else:
            os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = context._orig_arb_receipts_root
    # Last: cleanup above must run even when the expected-warning assertion trips.
    disarm_expected_warnings(context, scenario)
