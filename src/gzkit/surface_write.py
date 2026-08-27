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
"""

from pathlib import Path

__all__ = ["write_if_changed", "write_text_if_changed"]


def write_if_changed(path: Path, payload: bytes, *, mode: int | None = None) -> bool:
    """Write ``payload`` to ``path`` only when the on-disk bytes differ.

    Args:
        path: Destination file. Parent directories are created as needed.
        payload: Exact bytes the surface should contain.
        mode: When given, the permission bits the file must carry. Applied on
            every call, including the unchanged path -- ``chmod`` moves ctime,
            never mtime, so enforcing it costs nothing a caller must avoid.

    Returns:
        True when the file was written, False when it already matched.

    """
    path.parent.mkdir(parents=True, exist_ok=True)
    unchanged = path.is_file() and path.read_bytes() == payload
    if not unchanged:
        path.write_bytes(payload)
    if mode is not None:
        path.chmod(mode)
    return not unchanged


def write_text_if_changed(path: Path, text: str, *, mode: int | None = None) -> bool:
    """UTF-8 sibling of :func:`write_if_changed` for str-producing renderers."""
    return write_if_changed(path, text.encode("utf-8"), mode=mode)
