"""Typed exceptions for :mod:`gzkit.content.models.corpus`.

Held apart from the corpus module, which sits at the module-size guidance in
``.gzkit/rules/pythonic.md``. Each names the offending entry id, so an operator
can find the row in an append log that only ever grows.
"""


class DuplicateCorpusEntryIdError(ValueError):
    """Two corpus rows share one entry id (Algebra 1)."""

    def __init__(self, entry_id: str) -> None:
        """Name the duplicated id."""
        self.entry_id = entry_id
        super().__init__(
            f"corpus entry id {entry_id!r} appears more than once; an id is an "
            "entry's ADDRESS (ADR-0.0.37 Decision Re-Alignment part 1), so it must "
            "name exactly one row (Algebra 1). Two rows at one address make the "
            "Algebra 5 fold ambiguous: it keys liveness by id, so one row's verdict "
            "overwrites the other's and BOTH can leave the effective corpus (GHI "
            "#874). The store is append-only, so resolve this by appending a row "
            "with a fresh id, never by editing the log"
        )


class DoubleTombstonePointerError(ValueError):
    """A corpus row populates both ``retires`` and ``supersedes`` (Algebra 3)."""

    def __init__(self, entry_id: str, retires: str, supersedes: str) -> None:
        """Name the row and both pointers."""
        self.entry_id = entry_id
        super().__init__(
            f"corpus entry {entry_id!r} populates both 'retires' "
            f"({retires!r}) and 'supersedes' ({supersedes!r}); "
            "an entry may hold at most one tombstone pointer (Algebra 3)"
        )


class SelfTombstoneError(ValueError):
    """A corpus row names itself as its tombstone target (Algebra 2)."""

    def __init__(self, entry_id: str) -> None:
        """Name the self-targeting row."""
        self.entry_id = entry_id
        super().__init__(
            f"corpus entry {entry_id!r} names itself as its tombstone "
            "target; a tombstone must name a STRICTLY EARLIER entry (Algebra 2)"
        )


class UnknownTombstoneTargetError(ValueError):
    """A corpus row's tombstone target names no entry in the log (Algebra 2)."""

    def __init__(self, entry_id: str, target: str) -> None:
        """Name the row and its unknown target."""
        self.entry_id = entry_id
        self.target = target
        super().__init__(
            f"corpus entry {entry_id!r} names unknown tombstone target "
            f"{target!r}; no entry in the log carries that id (Algebra 2)"
        )


class ForwardTombstoneReferenceError(ValueError):
    """A corpus row's tombstone target appears later in the append log (Algebra 2)."""

    def __init__(self, entry_id: str, target: str) -> None:
        """Name the row and its later target."""
        self.entry_id = entry_id
        self.target = target
        super().__init__(
            f"corpus entry {entry_id!r} forward-references tombstone target "
            f"{target!r}, which appears LATER in the append log; a tombstone "
            "must name a strictly earlier entry (Algebra 2)"
        )


class SecondLiveTombstoneError(ValueError):
    """Two live tombstones target the same corpus entry (Algebra 7)."""

    def __init__(self, entry_id: str, target: str, claimant: str) -> None:
        """Name the second tombstone, its target and the tombstone already retiring it."""
        self.entry_id = entry_id
        self.target = target
        self.claimant = claimant
        super().__init__(
            f"corpus entry {entry_id!r} is a second LIVE tombstone targeting "
            f"{target!r}, which {claimant!r} already retires; at most one "
            "live tombstone may target an entry, so a double-retire is never "
            "silently folded into an un-retirement (Algebra 7). To retire "
            f"{target!r} again, first retire {claimant!r}"
        )


class UnresolvedTombstoneLivenessError(ValueError):
    """A tombstone's own liveness is unresolved when its target is folded."""

    def __init__(self, entry_id: str, tombstone_id: str) -> None:
        """Name the targeted row and the unresolved tombstone."""
        self.entry_id = entry_id
        self.tombstone_id = tombstone_id
        super().__init__(
            f"corpus entry {entry_id!r} is targeted by tombstone "
            f"{tombstone_id!r}, whose own liveness is UNRESOLVED at that point "
            "in the reverse pass; the append log is out of order (a tombstone "
            "must strictly follow its target, Algebra 2) or carries duplicate "
            "entry ids, so liveness is not computable for this corpus"
        )


class UnknownCorpusSectionError(ValueError):
    """A corpus row's section resolves to no Pillar in the contract."""

    def __init__(self, entry_id: str, section: str) -> None:
        """Name the row and its unresolved section."""
        self.entry_id = entry_id
        self.section = section
        super().__init__(
            f"corpus entry {entry_id!r} section {section!r} resolves to no Pillar in the contract"
        )
