"""Canonical attestation step commands — the locked provenance table.

Home of :data:`CANONICAL_STEP_COMMANDS`, extracted from
:mod:`gzkit.arb.validator` on 2026-08-22 so the table can be read without
loading the validator's dependency chain (``jsonschema``, ``pydantic``,
``gzkit.commands.common`` -> ``gzkit.sync`` -> ``gzkit.content.render``).

The ``verifier-pipe-gate`` PreToolUse hook reads this table on **every**
``Bash`` tool call; that chain cost ~95ms per call to reach a dict with no
dependencies of its own. :mod:`gzkit.arb.validator` re-exports the name, so
every existing importer is unaffected and there is still exactly one table.

It lives at ``gzkit`` top level rather than under ``gzkit.arb`` for two
reasons, both load-bearing. First, ``gzkit/arb/__init__.py`` eagerly imports
``gzkit.arb.validator``, so *any* ``gzkit.arb.*`` module — however leafy —
re-enters the chain this extraction removes; only a module outside the package
escapes it. Second, three of the four consumers already sit outside ``arb``
(``verifier_pipe_gate``, ``quality``, ``commands.obpi_complete``), so top level
matches where the table is actually read. Do not move it back under ``arb/``
without first making that ``__init__`` lazy.

**This module must stay dependency-free.** Adding an import here puts it back
on the hot path. Pinned by ``tests/arb/test_canonical_steps_leaf_import.py``.
"""

from __future__ import annotations

__all__ = ["CANONICAL_STEP_COMMANDS"]


# Canonical step-receipt provenance. A receipt whose ``step.name`` matches a
# key here MUST carry the listed ``step.command`` — otherwise the receipt
# claims to be a heavy-lane attestation label while measuring a different
# scope. Extending this table widens the provenance net; do not shrink it.
#
# ``typecheck`` is the one entry whose gate mirrors it *by construction*:
# ``quality.run_typecheck`` reads this list rather than re-spelling the command,
# so the GHI #199 divergence cannot recur there. The claim used to be made of
# all four gates in prose with nothing asserting it — and it was already false
# for ``run_tests``, which deliberately runs the ``unittest-parallel``
# accelerator while this table holds the serial attestation form. State the
# coupling per entry, never as a blanket:
#
#   typecheck -> ``quality.run_typecheck`` DERIVES from this entry
#   unittest  -> ``quality.run_tests`` deliberately DIFFERS (parallel runner)
#   coverage  -> operator-invoked; no ``gz check`` gate runs it
#   mkdocs    -> ``quality.run_mkdocs`` runs the same command, re-spelled
CANONICAL_STEP_COMMANDS: dict[str, list[str]] = {
    # Scope widened 2026-08-08 from ``src`` to the whole tree minus ``features``
    # (operator ruling). ``src``-only left the SessionStart orientation hook —
    # which runs before every agent's first response — structurally unchecked,
    # carrying five live diagnostics including a ``call-non-callable``. GHI #199
    # is not regressed by this: its defect was the ARB and gate scopes
    # DISAGREEING, not the particular scope they agreed on. ``features/`` stays
    # excluded because ``behave`` step functions annotate ``context`` attributes,
    # which ``ty`` rejects by design.
    #
    # The exclude is spelled as the BARE DIRECTORY, not ``features/**``. The glob
    # form does not match on Windows — ``ty`` reports paths with the platform
    # separator (``features\steps\foo.py``) and the forward-slash pattern never
    # fires, so all 25 in-``features`` diagnostics reached the gate and the
    # pre-push ``gz check`` failed on a tree CI had just passed. Measured
    # 2026-08-09: ``features`` exits 0 while ``features/**``, ``./features/**``,
    # ``**/features/**`` and ``features/**/*.py`` all exit 1. Linux never saw it
    # because the glob matches there, which is why six months of green CI did not
    # catch a gate that is red on a co-equal supported platform
    # (`.gzkit/rules/cross-platform.md`: "Windows, macOS, Linux — co-equal").
    "typecheck": ["uv", "run", "ty", "check", ".", "--exclude", "features"],
    "unittest": ["uv", "run", "-m", "unittest", "-q"],
    "coverage": ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-t", "."],
    "mkdocs": ["uv", "run", "mkdocs", "build", "--strict"],
    # Reserved by ADR-0.0.22 (security-sensitivity-doctrine), OBPI-05.
    # The receipt-name prefix is ``arb-step-security-``; the canonical command
    # string is left empty until the toolchain feature ADR (the one promoting
    # ``pool.agentic-security-review``) fills it. While the slot is empty,
    # ``gz obpi complete`` fails closed for any brief carrying
    # ``sensitivity: security`` — that fail-closed posture is REQ-0.0.22-05-04.
    "security": [],
    # Reserved by ADR-0.0.24 (attestation-receipt-binding), OBPI-02. Receipts
    # in the ``arb-meta-receipt-bind-`` family are emitted internally when
    # the receipt-binding gate fires successfully inside ``gz obpi complete``
    # and ``gz adr emit-receipt``. The slot is empty because the receipt is
    # not produced by a user-runnable invocation; provenance is enforced by
    # ``step.command == []`` on the emitted receipt.
    "meta-receipt-bind": [],
}
