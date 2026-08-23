"""Runtime invariant monitor for OBPI state transitions (ADR-0.31.0 OBPI-03).

Pure classifier that validates status transitions against OBPI-01's
CANONICAL_TRANSITIONS. Consumed by the frontmatter reconciler to refuse
silent status drift (GHI #348 class) at the write boundary.

Parent ADR Decision item 4 (verbatim): "A single invariant monitor. Every read
or write to the artifact graph passes through one monitor that asserts: (a) the
operation names a transition declared in (2); (b) preconditions are satisfied;
(c) the witness requirement is met. A frontmatter hand-edit that is not backed
by a declared transition is either rejected (no matching transition allowed) or
auto-emits the transition (so receipts and state never disagree). Today the
reconciler silently picks a winner; the monitor would refuse to let them
disagree in the first place."
"""

from __future__ import annotations

from gzkit.core.obpi_state_machine import CANONICAL_TRANSITIONS, OBPIState


class TransitionMonitor:
    """Classifier for OBPI state transitions against declared canonical transitions."""

    def __init__(self) -> None:
        """Initialize with OBPI-01's CANONICAL_TRANSITIONS."""
        # Build a set of allowed (from_state, to_state) pairs for O(1) lookup.
        self._allowed_transitions: set[tuple[OBPIState, OBPIState]] = {
            (t.from_state, t.to_state) for t in CANONICAL_TRANSITIONS
        }
        # Adjacency for multi-hop reachability (GHI #867). Built once here rather
        # than walked per query: the coarse frontmatter projection asks this on
        # every reconciled brief.
        self._outgoing: dict[OBPIState, list[OBPIState]] = {}
        for source, target in self._allowed_transitions:
            self._outgoing.setdefault(source, []).append(target)

    def is_allowed(self, from_state: OBPIState, to_state: OBPIState) -> bool:
        """Return True if the transition is declared in CANONICAL_TRANSITIONS.

        Args:
            from_state: The current OBPI state.
            to_state: The requested target state.

        Returns:
            True if the (from_state, to_state) pair matches a declared transition;
            False otherwise.

        """
        return (from_state, to_state) in self._allowed_transitions

    def is_reachable(self, from_state: OBPIState, to_state: OBPIState) -> bool:
        """Return True if *to_state* is reachable from *from_state* by declared transitions.

        The frontmatter vocabulary is a COARSE PROJECTION of this state machine.
        It can name ``DRAFTED``, ``IMPLEMENTING``, ``ATTESTED``, ``WITHDRAWN`` and
        ``SUPERSEDED``; it has no term for ``PLANNED``, ``VERIFIED`` or ``SYNCED``
        (``frontmatter_coherence._map_vocab_to_obpi_state``). One frontmatter hop
        therefore spans several canonical transitions, so the write boundary must
        ask reachability rather than :meth:`is_allowed`, which tests single-hop
        membership and refuses every legal coarse move whose fine path crosses a
        state the vocabulary cannot name. Measured before GHI #867: an OBPI that
        launched the pipeline and did not complete could never be reconciled
        ``Draft -> Active`` — the reconciler refused the only write that could
        satisfy the validator demanding the two agree, and the tree was unpushable.

        Every protection :meth:`is_allowed` gave that boundary survives, because
        reachability is DIRECTIONAL: terminal states declare no outgoing
        transition and so reach nothing (the GHI #348 clobber class), and the
        machine declares no backward edge, so a later state never reaches an
        earlier one. Self-reachability requires a real cycle and is not seeded.

        Args:
            from_state: The current OBPI state.
            to_state: The requested target state.

        Returns:
            True if some path of declared transitions leads from *from_state* to
            *to_state*; False otherwise.

        """
        seen: set[OBPIState] = set()
        frontier = [from_state]
        while frontier:
            for successor in self._outgoing.get(frontier.pop(), ()):
                if successor == to_state:
                    return True
                if successor not in seen:
                    seen.add(successor)
                    frontier.append(successor)
        return False
