"""Per-cut parity proof for the ``VALIDATOR_REGISTRY`` collapse (#618, step 2).

Sanity-Reduction cut #618 collapses six hand-synced enumerations
(``_default_scope_runners`` / ``_explicit_scope_runners`` dicts, the
``_collect_errors`` tier dicts, the ``_resolve_scopes`` lists, and ``validate()``'s
``_other_scopes_active`` predicate) into one ``VALIDATOR_REGISTRY``. The campaign
mandate (build-to-1.0 § E.4) is *dispatch identical before/after*: any collapse
that silently drops or re-tiers a scope is the #394 self-include failure class
this track exists to kill.

This proof pins the registry against the dispatch truth measured from the
pre-collapse code (the "before" snapshot). The golden literals below are that
snapshot; the assertions prove the post-collapse registry reproduces them
exactly. It complements the step-1 fence (``test_validate_dispatch_consistency``):
the fence pins signature ↔ runner ↔ parser-lambda parity; this pins the registry
as the single source those surfaces now derive from.
"""

from __future__ import annotations

import inspect
import unittest
from pathlib import Path

from gzkit.commands import validate_cmd

# --- Golden "before" snapshot (measured from the pre-collapse dispatch) ---------

# Default-tier scopes run on the no-flag (`gz check`) path. Order is load-bearing:
# it is the error-collection iteration order of the former `_default_scope_runners`.
_GOLDEN_DEFAULT_ORDER: tuple[str, ...] = (
    "manifest",
    "surfaces",
    "ledger",
    "instructions",
    "briefs",
    "documents",
    "personas",
    "frontmatter",
    "version",
    "taxonomy",
    "invariant_coherence",
)

# Default-tier scopes ADDED after the "before" snapshot was taken.
#
# The golden above is evidence: it is the measured pre-collapse dispatch, and its
# value as a migration proof depends on staying pristine. Appending new scopes to
# it would erase the boundary between "what the collapse had to reproduce" and
# "what was added later" — the snapshot would silently stop being a snapshot.
# Legitimate post-snapshot growth is recorded here instead, so the assertion can
# still prove the collapse dropped nothing while the registry keeps growing.
#
#   rule_version_markers — enforces the rule-version-marker invariant declared by
#   skill-surface-sync.md § Non-negotiable rules #2 but never mechanized
#   (Pass A conflict-matrix re-run, 2026-07-16).
#   invariant_witness — resolves every registered invariant's structural_witness to a
#   real command. The validator existed from GHI #623 with no CLI wiring at all; its
#   only caller was its own fence test until GHI #746 registered it here.
_POST_SNAPSHOT_DEFAULT_ADDITIONS: tuple[str, ...] = (
    "rule_version_markers",
    "invariant_witness",
    # wheel_path_literals — environment-rooted path literals in wheel-shipped
    # instruction text (GHI #900). DEFAULT tier deliberately, on the same
    # reasoning as its neighbour below: `--distribution` proved the bytes
    # ARRIVE and read green for as long as four shipped files told adopters to
    # open a path that existed on one laptop. A flag-gated resolvability check
    # would be inert in exactly the situation that produced the defect — nobody
    # was running a check they had not yet thought to write.
    "wheel_path_literals",
    # corpus_retirement_witness — a Layer-1 tombstone with no Layer-2 witness
    # (GHI #885, GHI #878). DEFAULT tier deliberately: the class it catches
    # produced seven live instances on `main` while every gate read green, so a
    # flag-gated check nobody runs would be inert exactly where inertness caused
    # the defect.
    "corpus_retirement_witness",
)

# Explicit-tier scopes run only when their flag is set. Set-parity is what the
# dispatch contract pins; the order is unified onto registry order (no test pins
# the multi-scope output order, confirmed pre-cut).
# Explicit-tier scopes ADDED after the "before" snapshot was taken.
#
# Same doctrine as `_POST_SNAPSHOT_DEFAULT_ADDITIONS` above, applied to the
# explicit tier: the golden set is measured evidence of the pre-collapse
# dispatch, so appending to it would erase the boundary between "what the
# collapse had to reproduce" and "what was added later". The default tier had
# this hatch from the start; the explicit tier did not, so the first genuinely
# new explicit scope had nowhere honest to go (GHI #741).
#
#   persona_witness — witnesses AGENTS.md § Persona ("Every agent frame MUST
#   include a Persona") for ADRs. The MUST was convention-only while its sibling
#   section `## Why foundation tier?` was mechanically enforced; 44 ADRs reached
#   the grandfather roster, 42 of them past Gate 5 (GHI #741).
#
#   qc_binding, fidelity_presence, waiver_ratchet — newly REGISTERED, not newly
#   created. They predate the snapshot but were never in `_explicit_scope_runners`
#   because they dispatched through the early-return chain alone, which is exactly
#   why the registry's "single source of validate dispatch" header was false. The
#   hatch is still the honest home: the golden set is measured evidence of the
#   pre-collapse runner dict, and these were never in it.
#   status_writer_coverage — genuinely new (GHI #669), not merely newly
#   registered. It audits that every `status:` writer under `src/gzkit/**`
#   consults the single invariant monitor ADR-0.31.0 Decision item 4 declares.
#   Explicit tier because it is a src/-scoped structural audit, like its
#   neighbours, and it is `in_check` from the outset — a scope that discovers
#   convention-only enforcement would be an odd thing to leave outside the gate.
#   transcribed_adr_counts — genuinely new (GHI #768). It refuses a transcribed
#   ADR OBPI count in prose declared live, the Layer-3-becomes-source-of-truth
#   shape AGENTS.md § Architectural Boundaries 6 names. Explicit tier rather than
#   default because its subject is an opt-in registry of docs/ surfaces, not a
#   whole-tree sweep — the filed GHI's binding constraint is that most of the 135
#   `N/M` figures in docs/ are dated records that must NOT be rewritten, so a
#   default-tier whole-corpus scope would be the wrong shape. `in_check` from the
#   outset: a fence that only runs when asked is the convention it replaces.
#   pool_interview — genuinely new (GHI #719). A pool ADR's Step-0 interview JSON
#   had no reader at all, while the non-pool path (`gz interview adr --from`)
#   fails closed on every use — the same artifact type carrying a different
#   governance guarantee purely by kind. Explicit tier because its subject is one
#   named directory (`docs/design/adr/pool/*-interview.json`), not a whole-tree
#   sweep, so it sits beside `pool_adr_isolation` rather than in the default tier.
#   `in_check` from the outset: the defect IS the asymmetry, and a pool-side gate
#   that runs only when an operator remembers the flag would leave the two
#   guarantees exactly as unequal as the GHI found them.
_POST_SNAPSHOT_EXPLICIT_ADDITIONS: frozenset[str] = frozenset(
    {
        # GHI #877 (reopened): producer-side contract parity, sibling of
        # `event_schemas`/`event_handlers` and tiered with them.
        "producer_fields",
        "persona_witness",
        "qc_binding",
        "fidelity_presence",
        "waiver_ratchet",
        "config_registry",
        "status_writer_coverage",
        "transcribed_adr_counts",
        "pool_interview",
        "gate_callers",
        "exemption_controls",
        # Interpreter-pin coherence. Explicit tier because its subject is a
        # named population (`.github/workflows/**` declarations) rather than a
        # whole-tree sweep. `in_check` from the outset: the drift it catches is
        # invisible on a clean tree, so a gate that runs only when an operator
        # remembers the flag would never fire on the commit that introduced it.
        "python_version_pins",
    }
)

_GOLDEN_EXPLICIT_SET: frozenset[str] = frozenset(
    {
        "interviews",
        "decomposition",
        "requirements",
        "commit_trailers",
        "type_ignores",
        "cli_alignment",
        "event_handlers",
        "event_schemas",  # GHI #581 — factory/model ↔ schema coupling at the validator tier
        "validator_fields",
        # GHI #725 — commit-authorship policy; opt-in per project, so it is
        # explicit-tier rather than default like its sibling surface checks.
        "authorship",
        "utf8_prefix",
        "line_endings",
        "test_tiers",
        "pydantic_models",
        "class_size",
        "version_release",
        "pool_adr_isolation",
        "behave_req_tags",
        "skill_alignment",
        "advisory_scorecard",
        "complexity_doctrine_links",
        "complexity_thresholds",
        "reconcile_freshness",
        "insights_shape",
        "instructions_files_budget",
        "agents_md_map_conformance",
        "adr_status_fresh",
        "obpi_lifecycle_coherence",  # GHI #584 — orphaned obpi_created census
        "adversarial_validation",  # GHI #676 — Step-4b verdict capture
        "red_parity",  # GHI #642 — BEHAVIOR-REQ falsifiability witness
        "session_green_gate",
        "orientation_freshness",
        "brief_headings",
        "brief_cross_references",
        "brief_demo_section",
        "chores_layout",
        "unscoped_rules",
        "sensitivity",
        "doc_surface_parity",
        "absorption_duplicates",
        "orphaned_implementation",
        "evaluation_justify_binding",
        "intrinsic_attestation",
        "advisor_proof_binding",
        "lock_exchange_coupling",
        "distribution",
        "changelog",
        "bullet_retention",
        "surface_weight",
        "pointer_anchors",
        "surface_fidelity",
        "vendor_manifest",
        "setpoint_coherence",
        "rendition_freshness",
        "rendition_floor_coherence",
        "kind_invariance",
        "receipt_shape",
        "brief_reconcile",
        "brief_structure",
        "router_tables",
        "req_kind_discipline",
        "ontology_purity",
        "brief_command_shape",
        "tautological_test_audit",
        "task_envelope_coherence",
        "closeout_proof",
        "okf_conformance",
        "deprecated_verb_prescription",
    }
)

# Registry stems DELIBERATELY excluded from the `_other_scopes_active` predicate
# in the pre-collapse code. `sensitivity`, `evaluation_justify_binding`, and
# `unscoped_rules` are legitimately excluded — they own a solo early-return
# lifecycle and must not count as "another scope active". The remaining five
# (`invariant_coherence`, `session_green_gate`, `intrinsic_attestation`,
# `advisor_proof_binding`, `lock_exchange_coupling`) are regular aggregate scopes
# whose exclusion is a PRE-EXISTING anomaly (combining them with a solo scope
# would drop them). This cut preserves the membership exactly; the anomaly is
# flagged for separate routing, not healed here.
_GOLDEN_OTHER_SCOPES_EXCLUDED: frozenset[str] = frozenset(
    {
        "invariant_coherence",
        "session_green_gate",
        "intrinsic_attestation",
        "advisor_proof_binding",
        "lock_exchange_coupling",
        "sensitivity",
        "evaluation_justify_binding",
        "unscoped_rules",
    }
)

# Stems excluded from `_other_scopes_active` AFTER the snapshot was taken. Same
# doctrine as `_POST_SNAPSHOT_EXPLICIT_ADDITIONS` (GHI #741): the golden above is
# measured evidence of the pre-collapse predicate, so appending to it would erase
# the boundary between what the collapse had to reproduce and what came later.
#
#   qc_binding, fidelity_presence, waiver_ratchet — registered so the registry is
#   genuinely the single source of validate dispatch. Each owns a solo
#   early-return lifecycle exactly as `sensitivity` and `unscoped_rules` do, so
#   each is excluded for the SAME legitimate reason: counting itself as "another
#   scope active" would make the #704 combined-scope refusal fire against a solo
#   invocation.
#   gate_callers — same shape (GHI #785): a solo early-return lifecycle, so
#   counting itself as "another scope active" would fire the #704 refusal
#   against `gz validate --gate-callers` run alone.
#   config_registry — same shape (GHI #929): the config-registry declaration gate
#   owns a solo early-return lifecycle exactly as `waiver_ratchet` does, so it is
#   excluded for the same legitimate reason. It is the companion gate to
#   `waiver_ratchet`; between them the two are exhaustive over `data/*.json`.
_POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED: frozenset[str] = frozenset(
    {
        "qc_binding",
        "fidelity_presence",
        "waiver_ratchet",
        "config_registry",
        "gate_callers",
        "exemption_controls",
    }
)


class TestValidatorRegistryParity(unittest.TestCase):
    """The collapsed registry reproduces the pre-collapse dispatch exactly."""

    def _registry(self) -> tuple:
        return validate_cmd.VALIDATOR_REGISTRY

    def test_default_tier_order_preserved(self) -> None:
        """The collapse reproduced the snapshot; later additions append after it.

        Asserts the golden is a *prefix* of the live order, so the migration
        proof still holds (nothing dropped, nothing re-ordered) while genuinely
        new scopes are admitted through `_POST_SNAPSHOT_DEFAULT_ADDITIONS`
        rather than by mutating the evidence.
        """
        order = tuple(e.stem for e in self._registry() if e.tier == "default")
        self.assertEqual(
            order[: len(_GOLDEN_DEFAULT_ORDER)],
            _GOLDEN_DEFAULT_ORDER,
            "default-tier stems (and their collection order) must match the "
            "pre-collapse `_default_scope_runners` exactly",
        )
        self.assertEqual(
            order[len(_GOLDEN_DEFAULT_ORDER) :],
            _POST_SNAPSHOT_DEFAULT_ADDITIONS,
            "a default-tier scope added after the snapshot must be declared in "
            "`_POST_SNAPSHOT_DEFAULT_ADDITIONS` — an undeclared one is drift",
        )

    def test_explicit_tier_set_preserved(self) -> None:
        got = frozenset(e.stem for e in self._registry() if e.tier == "explicit")
        self.assertEqual(
            got - _POST_SNAPSHOT_EXPLICIT_ADDITIONS,
            _GOLDEN_EXPLICIT_SET,
            "explicit-tier stem set must match the pre-collapse "
            "`_explicit_scope_runners` exactly (no scope dropped or re-tiered)",
        )
        self.assertEqual(
            got & _POST_SNAPSHOT_EXPLICIT_ADDITIONS,
            _POST_SNAPSHOT_EXPLICIT_ADDITIONS,
            "an explicit-tier scope added after the snapshot must be declared in "
            "`_POST_SNAPSHOT_EXPLICIT_ADDITIONS` — an undeclared one is drift, and "
            "a declared-but-absent one means the scope was dropped",
        )

    def test_no_unknown_tier(self) -> None:
        bad = sorted({e.stem for e in self._registry() if e.tier not in ("default", "explicit")})
        self.assertEqual(bad, [], f"every registry entry must declare a known tier: {bad}")

    def test_other_scopes_active_membership_preserved(self) -> None:
        excluded = frozenset(e.stem for e in self._registry() if not e.in_other_scopes)
        self.assertEqual(
            excluded - _POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED,
            _GOLDEN_OTHER_SCOPES_EXCLUDED,
            "the `_other_scopes_active` exclusion set must be preserved byte-for-byte "
            "— changing it alters whether a solo early-return scope runs solo",
        )
        self.assertEqual(
            excluded & _POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED,
            _POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED,
            "a stem excluded from `_other_scopes_active` after the snapshot must be "
            "declared in `_POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED` — an undeclared one "
            "is drift, and a declared-but-included one means the exclusion was lost",
        )

    def test_derived_runner_dicts_match_registry_tiers(self) -> None:
        # The fence reads these two functions; they must stay registry-faithful.
        default_keys = set(validate_cmd._default_scope_runners(Path("."), None))
        explicit_keys = set(validate_cmd._explicit_scope_runners(Path(".")))
        self.assertEqual(
            default_keys,
            {e.stem for e in self._registry() if e.tier == "default"},
            "_default_scope_runners must enumerate exactly the default-tier registry stems",
        )
        self.assertEqual(
            explicit_keys,
            {e.stem for e in self._registry() if e.tier == "explicit"},
            "_explicit_scope_runners must enumerate exactly the explicit-tier registry stems",
        )

    def test_every_registry_stem_has_a_check_param(self) -> None:
        # Closes the loop with the step-1 fence: a registry runner the CLI cannot
        # reach (no check_* param) is dead. The fence asserts the inverse too.
        params = {
            n[len("check_") :]
            for n in inspect.signature(validate_cmd.validate).parameters
            if n.startswith("check_")
        }
        orphans = sorted(e.stem for e in self._registry() if e.stem not in params)
        self.assertEqual(
            orphans,
            [],
            f"these registry stems have no check_* param on validate(): {orphans}",
        )


if __name__ == "__main__":
    unittest.main()
