"""Per-claim ``population`` declarations for the qc negative-control claims (GHI #1007).

Split from the registration table for the reason ``_qc_claim_exemptions`` is: a
control wires a fixture to a gate, while a population is a judgment about what set
the gate's claim ranges over, and it carries the bar that judgment was made against.

**The bar.** A claim declares a population callable when its subject is a set
DECLARED ON ANOTHER SURFACE — a config list, a glob, a generator's write set, a
registry — so the set can grow without the witness being edited. The callable reads
that surface itself and never through the witness's own reader, which would narrow
in step with the witness. A claim absent from this map registers with
``population=None`` (UNDECLARED) and is disclosed by ``gz validate
--population-controls`` until someone reads its gate and declares it.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from gzkit.enforcement import POPULATION_NONE

from . import _qc_nc_hooks as _hk
from . import _qc_nc_population as _pc

QC_CLAIM_POPULATIONS: dict[str, Callable[[], Sequence[str]] | str] = {
    # Every type in `.pre-commit-config.yaml` `default_install_hook_types`, plus the
    # gate's own pre-push. The witness read one of four (GHI #851).
    "session-green-gate-delivery": _hk.hook_type_population,
    # Every claim whose population is undeclared, read from the registry directly.
    "population-controls": _pc.undeclared_claim_population,
    # Admission is one membership test applied uniformly over the list; the refuse
    # claim above carries the per-member proof, so this control ranges over no set.
    "population-controls-disclosed": POPULATION_NONE,
    # One evaluation, answered or not, by whatever sits under artifacts/justify/. The
    # forms of false evidence are the gate's own cases, not a set another surface
    # declares; the refuse control plants all of them at once (GHI #996).
    "evaluation-justify-binding": POPULATION_NONE,
    "evaluation-justify-binding-qualified": POPULATION_NONE,
}
