"""Idempotent write primitive for generated control surfaces.

``sync_all`` regenerates every derived surface on each run. Writing
unconditionally makes a *validator* that calls it mutate the tree it inspects:
``gz validate --surfaces`` establishes parity by performing a sync, so 102
canonical files -- ``AGENTS.md``, every ``.claude/rules/`` mirror, all 17 hook
scripts -- moved on every invocation. The writes are byte-identical, so
``git status`` stayed clean while mtimes churned, and that mtime churn is what
classes the ``gz check`` step as a writer and forces four read-only steps to
wait on it (GHI #890).

``sync_surfaces`` already declared this contract in three places --
``_write_bytes_if_changed``, ``_copy_if_changed`` and ``render_content_surface``
all promise *"Idempotent: bytes-identical destinations are left untouched"* --
and thirteen other writers did not honour it. This module holds the single
primitive they share, so the property holds by construction rather than by each
author remembering to apply it.

Bytes, not text, are the interface: ``Path.write_text`` with an explicit LF newline
and ``payload.encode("utf-8")`` produce identical files, and comparing bytes
keeps the check free of platform newline translation
(``.gzkit/rules/cross-platform.md``).

**The capture sink (GHI #891).** #890 made ``sync_all`` idempotent on a CLEAN
tree; it still wrote on a DRIFTED one, because parity was established by
performing a sync and putting the drift back afterwards. That residual is what
kept ``Validate default scopes`` classified ``writes``: a static ``read_only``
claim would have been false exactly when the gate is red, which is precisely
when a concurrent step would read a torn mirror. Rarity is not the property a
scheduler needs -- impossibility is.

:func:`capture_surface_writes` makes it impossible. Inside the context manager
every write, delete and directory creation in this module records its INTENT and
touches nothing, so ``sync_all`` becomes a pure renderer and the validator can
byte-compare against what it would have produced. Three helpers is the whole
membrane, which is why routing every mutation through them was the precondition
rather than an aesthetic preference: a caller that reaches past them is a hole
the sink cannot close, and nothing observes that from the outside.

The sink is a :class:`~contextvars.ContextVar`, not a module global, so a
concurrent ``gz check`` step cannot silently inherit another's capture.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SurfaceSink",
    "capture_surface_writes",
    "dir_exists",
    "ensure_dir",
    "remove_dir_if_empty",
    "remove_if_present",
    "write_if_changed",
    "write_text_if_changed",
]


class SurfaceSink(BaseModel):
    """What a captured ``sync_all`` WOULD have done to the tree.

    ``written`` holds intended bytes for every managed surface, including the
    ones already matching on disk -- an unchanged write still declares "this
    file should exist with these bytes", and dropping it would make an untouched
    file indistinguishable from one sync means to delete.

    ``removed`` holds paths sync would unlink. The two are kept mutually
    exclusive so a delete-then-write (or the reverse) resolves to the last
    intent rather than to both.

    ``created_dirs`` exists because ``sync_all`` has passes that read what
    EARLIER passes wrote. ``nested_agents_md_paths`` guards on
    ``subtree_dir.is_dir()``, so under a sink that suppresses ``mkdir`` the
    directory never appears and ``.gzkit/skills/AGENTS.md`` drops silently out
    of the plan. The old envelope hid this by genuinely writing. Recording the
    intent and answering existence questions through :func:`dir_exists` keeps
    the sink touching nothing, where letting ``mkdir`` through would have
    weakened the guarantee to "cannot write FILES" -- the rarity-for-
    impossibility trade this whole change exists to refuse.
    """

    model_config = ConfigDict(extra="forbid")

    written: dict[Path, bytes] = Field(default_factory=dict, description="Intended bytes")
    removed: set[Path] = Field(default_factory=set, description="Paths sync would unlink")
    created_dirs: set[Path] = Field(default_factory=set, description="Dirs sync would create")

    def record_write(self, path: Path, payload: bytes) -> None:
        """Record that ``path`` should hold ``payload``."""
        resolved = path.resolve()
        self.written[resolved] = payload
        self.removed.discard(resolved)

    def record_removal(self, path: Path) -> None:
        """Record that ``path`` should not exist."""
        resolved = path.resolve()
        self.removed.add(resolved)
        self.written.pop(resolved, None)

    def record_dir(self, path: Path) -> None:
        """Record that ``path`` and every parent should exist as directories.

        Parents are recorded because the real call is ``mkdir(parents=True)``,
        and a model that claims fewer directories than the thing it models is
        wrong in the direction that matters here -- ``dir_exists`` would answer
        False for a grandparent that apply mode does create.

        **No test currently kills the parent line, and that is stated rather than
        hidden.** Every directory today's branches ask about is the direct parent
        of some written file, which :func:`write_if_changed` records on its own,
        so a mutation dropping ``.parents`` leaves the suite green. It is kept as
        faithfulness to ``parents=True`` rather than deleted as unreachable: the
        alternative is a knowingly-incorrect model that happens to be unobserved,
        which is the shape this whole change exists to refuse.
        """
        resolved = path.resolve()
        self.created_dirs.add(resolved)
        self.created_dirs.update(resolved.parents)


_ACTIVE_SINK: ContextVar[SurfaceSink | None] = ContextVar("gzkit_surface_sink", default=None)


@contextmanager
def capture_surface_writes() -> Iterator[SurfaceSink]:
    """Run a block with every surface mutation recorded instead of performed.

    Reads still happen -- the helpers below compare against on-disk bytes so
    they can report whether a write WOULD have changed anything, which is what
    ``gz agent sync control-surfaces --dry-run`` prints.
    """
    sink = SurfaceSink()
    token = _ACTIVE_SINK.set(sink)
    try:
        yield sink
    finally:
        _ACTIVE_SINK.reset(token)


def remove_if_present(path: Path) -> bool:
    """Delete ``path`` if it exists, or record the intent when a sink is active.

    Returns True when the file existed, and so would have been removed.
    """
    sink = _ACTIVE_SINK.get()
    if sink is not None:
        if not path.is_file():
            return False
        sink.record_removal(path)
        return True
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    return True


def remove_dir_if_empty(path: Path) -> None:
    """Remove ``path`` when it is an empty directory, unless a sink is active.

    Guarded even though a captured run deletes nothing and so empties nothing:
    a directory that was ALREADY empty would still be collected, and "usually
    does not write" is the claim this whole change exists to replace.
    """
    if _ACTIVE_SINK.get() is not None:
        return
    try:
        path.rmdir()
    except OSError:
        return


def ensure_dir(path: Path) -> None:
    """Create ``path`` unless a sink is active.

    Redundant with :func:`write_if_changed`'s own parent creation at every
    current call site, and kept as a named no-op rather than deleted: a caller
    that creates a directory for something other than an immediate write still
    has one seam to reach for, instead of an inlined ``mkdir`` the sink cannot
    see.
    """
    sink = _ACTIVE_SINK.get()
    if sink is None:
        path.mkdir(parents=True, exist_ok=True)
        return
    sink.record_dir(path)


def dir_exists(path: Path) -> bool:
    """Return whether ``path`` is a directory, or would be one after a sync.

    The sink-aware form of ``Path.is_dir()``, for the passes that branch on a
    directory an earlier pass creates. Calling ``is_dir()`` directly inside a
    captured sync answers a question about the PRE-sync tree and quietly drops
    whatever that branch would have produced.
    """
    if path.is_dir():
        return True
    sink = _ACTIVE_SINK.get()
    return sink is not None and path.resolve() in sink.created_dirs


def write_if_changed(path: Path, payload: bytes, *, mode: int | None = None) -> bool:
    """Write ``payload`` to ``path`` only when the on-disk bytes differ.

    Args:
        path: Destination file. Parent directories are created as needed.
        payload: Exact bytes the surface should contain.
        mode: When given, the permission bits the file must carry. Applied on
            every call, including the unchanged path -- on POSIX ``chmod``
            moves ctime, never mtime, so enforcing it costs nothing a caller
            must avoid. Skipped entirely under a capture sink, where nothing is
            touched; that unconditional ``chmod`` is why 17 hook scripts moved
            ctime on every parity check while an mtime probe read clean
            (GHI #891). Windows honours only the read-only attribute here, so
            an executable bit is requested and silently not granted, and
            ``st_ctime`` there is the creation time and moves for neither arm
            (GHI #901) -- both are limits of the platform, not of this call.

    Returns:
        True when the on-disk bytes differ from ``payload``. Under a capture
        sink the answer is still computed from disk and still returned, because
        ``--dry-run`` reports which surfaces WOULD change -- the sink suppresses
        the write, never the comparison.

    """
    unchanged = path.is_file() and path.read_bytes() == payload
    sink = _ACTIVE_SINK.get()
    if sink is not None:
        sink.record_write(path, payload)
        # The unsuppressed path calls `mkdir(parents=True)` here, so a captured
        # run must claim the same directories or a later pass branching on their
        # existence answers about the pre-sync tree.
        sink.record_dir(path.parent)
        return not unchanged
    path.parent.mkdir(parents=True, exist_ok=True)
    if not unchanged:
        path.write_bytes(payload)
    if mode is not None:
        path.chmod(mode)
    return not unchanged


def write_text_if_changed(path: Path, text: str, *, mode: int | None = None) -> bool:
    """UTF-8 sibling of :func:`write_if_changed` for str-producing renderers."""
    return write_if_changed(path, text.encode("utf-8"), mode=mode)
