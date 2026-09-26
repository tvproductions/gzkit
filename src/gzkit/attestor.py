"""The project's configured attestor handle (GHI #1036).

`.gzkit.json` § `authorship.attestor_handle` is the single source for the value
an omitted `--attestor` records and for what a remedy prints. It is read per
project, so gzkit's own handle and an adopter's never mix: each repository's
`.gzkit.json` carries its own, and `gz init` scaffolds none.
"""

from pathlib import Path

from gzkit.config import GzkitConfig

ATTESTOR_TOKEN = "<attestor-handle>"


def configured_attestor_handle(project_root: Path | None = None) -> str | None:
    """Return the configured handle, or None when unset, uninitialized or unreadable.

    An unreadable `.gzkit.json` yields None rather than an error: the verb that
    needs the config reports that failure itself, on its own terms.
    """
    path = (project_root or Path.cwd()) / ".gzkit.json"
    if not path.is_file():
        return None
    try:
        return GzkitConfig.load(path).authorship.attestor_handle
    except (OSError, ValueError):
        return None


def attestor_hint(project_root: Path | None = None) -> str:
    """Return the value a remedy prints for `--attestor`: the handle, else the token."""
    return configured_attestor_handle(project_root) or ATTESTOR_TOKEN
