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

from . import _qc_nc_gate_enrollment as _ge
from . import _qc_nc_hooks as _hk
from . import _qc_nc_population as _pc

QC_CLAIM_POPULATIONS: dict[str, Callable[[], Sequence[str]] | str] = {
    # Every type in `.pre-commit-config.yaml` `default_install_hook_types`, plus the
    # gate's own pre-push. The witness read one of four (GHI #851).
    "session-green-gate-delivery": _hk.hook_type_population,
    # Every claim whose population is undeclared, read from the registry directly.
    "population-controls": _pc.undeclared_claim_population,
    # Every validate scope no claim names, read from the validate and enforcement
    # registries directly (GHI #1155).
    "gate-enrollment": _ge.unenrolled_scope_population,
    "gate-enrollment-disclosed": POPULATION_NONE,
    # Admission is one membership test applied uniformly over the list; the refuse
    # claim above carries the per-member proof, so this control ranges over no set.
    "population-controls-disclosed": POPULATION_NONE,
    # One evaluation, answered or not, by whatever sits under artifacts/justify/. The
    # forms of false evidence are the gate's own cases, not a set another surface
    # declares; the refuse control plants all of them at once (GHI #996).
    "evaluation-justify-binding": POPULATION_NONE,
    "evaluation-justify-binding-qualified": POPULATION_NONE,
    # Walks a glob over docs/governance/**; the members are whatever files exist,
    # never a set another surface declares (GHI #1083).
    "doc-code-citations": POPULATION_NONE,
    "doc-code-citations-exempted": POPULATION_NONE,
    # Walks a glob over docs/design/adr/**; the members are whatever briefs exist,
    # never a set another surface declares (GHI #1196).
    "brief-size": POPULATION_NONE,
    "brief-size-grandfathered": POPULATION_NONE,
    # Reads the three catalog files the store names; the entries are whatever the
    # files hold, never a set another surface declares (drydock RO-3).
    "requirements-catalog": POPULATION_NONE,
    "requirements-catalog-edges": POPULATION_NONE,
    "requirements-catalog-coverage": POPULATION_NONE,
    "requirements-catalog-bdd": POPULATION_NONE,
    "requirements-catalog-forward-rule": POPULATION_NONE,
    # Reads the ledger's open MX sessions; the members are whatever sessions are
    # open, never a set another surface declares (GHI #1257).
    "mx-hardening": POPULATION_NONE,
    # Walks src/gzkit/** and the tests, features and briefs in code; the members are
    # whatever files exist, never a set another surface declares (drydock RO-2).
    "identity-seam": POPULATION_NONE,
    "identity-seam-baselined": POPULATION_NONE,
    # Reads the project's own manifest, workflows and sources; the members are
    # whatever the tree declares, never a set another surface declares (RO-9).
    "astral-discipline": POPULATION_NONE,
    "astral-discipline-baselined": POPULATION_NONE,
    # Walks tests/** in code; the members are whatever test files exist, never a set
    # another surface declares (GHI #808).
    "tautological-debt": POPULATION_NONE,
    # The floored keys are MKDOCS_VALIDATION_FLOOR, an in-code table the control
    # itself iterates: the fixture downgrades every key and the entrypoint requires
    # each one named, so no second surface declares the set (GHI #803).
    "docs-build-validation-floor": POPULATION_NONE,
    "tautological-debt-waived": POPULATION_NONE,
    # The sweep reads data/guard_canaries.json itself on every run and applies one
    # verdict to every canary in it, so it cannot pin a literal subset (GHI #1191).
    "guard-canary-sweep": POPULATION_NONE,
    # Each ratchet reads its subject set from the declaring surface itself on every
    # run -- the live `gz validate` parser, the ledger schema -- and applies one
    # set difference against its baseline uniformly, so it cannot pin a literal
    # subset the way GHI #851's witness did. The refuse fixtures plant every member
    # at once (GHI #1063).
    "validator-reachability": POPULATION_NONE,
    "validator-reachability-disclosed": POPULATION_NONE,
    "ledger-vocabulary-inertness": POPULATION_NONE,
    "ledger-vocabulary-inertness-disclosed": POPULATION_NONE,
}
