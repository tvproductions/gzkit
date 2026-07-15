"""BDD steps for the gz handoff verb (ADR-0.0.65, OBPI-0.0.65-03).

`list` and `resume` are read-only projections over the real repository's
``.gzkit/handoffs/`` corpus, so those scenarios reuse the
``Given "the gzkit repository working tree"`` step from
``airlock_steps.py``. `create`'s fail-closed scenario also runs against the
real repository (it is refused before anything is written, so it is safe).
`create`'s success scenario reuses the ``Given "a fresh empty project
directory"`` / ``Given "the workspace has been initialized via gz init"``
steps from ``chores_distribution_steps.py`` so the authored handoff document
lands in the per-scenario tempdir rather than the real repository's handoff
corpus. All ``When``/``Then`` subprocess steps are reused verbatim from
``chores_distribution_steps.py``. No new step definitions are required.

@covers REQ-0.0.65-03-01
@covers REQ-0.0.65-03-02
@covers REQ-0.0.65-03-03
"""

from __future__ import annotations
