"""Today's registries a tag's surface resolves against (RP-12 O3 task 2, rulings 112 and 123).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: a tag's surface is
written `<kind>:<name>` and resolved against the registry that holds that kind
today, since no one control registry exists until RP-13's MEL (ruling 112):

- `validator:<scope>`, a `gz validate` scope in its flag's spelling,
  `validator:hexagon-tests`; the registry's own name is the scope's stem;
- `check:<step>`, a `gz check` step's name in lower case with its spaces
  hyphenated, `check:module-size`; the registry's own name is the step's;
- `hook:<name>`, a hook script `.claude/settings.json` registers, by its file name
  with or without its suffix, or a hook id `.pre-commit-config.yaml` declares,
  written bare or as `hook:settings:<script>` or `hook:pre-commit:<id>`; the
  registry's own name records its registry, `settings:<script file>` or
  `pre-commit:<id>`, and a bare name both hold is refused (rulings 123 and 127);
- `path:<repo path>`, a path in the tree under the project root, written with
  forward slashes; the registry's own name is the normalized repo path.

The command reads these registries and passes the writer what they hold, so the
writer in `gzkit.mx.tag_out` reads none itself (ruling 119). This module is that
adapter: a concrete `SurfaceRegistry`, taking the project root as a parameter.
"""

import json
import shlex
from pathlib import Path, PurePosixPath

import yaml

from gzkit.commands.quality import _build_check_steps
from gzkit.commands.validate_cmd import VALIDATOR_REGISTRY
from gzkit.core.exceptions import ValidationError

_SETTINGS = PurePosixPath(".claude/settings.json")
_PRE_COMMIT = PurePosixPath(".pre-commit-config.yaml")


def _unreadable(registry: PurePosixPath, why: str) -> ValidationError:
    return ValidationError(
        f"{registry} cannot be read as a hook registry: {why}. A `hook:` surface resolves "
        "against the scripts .claude/settings.json registers and the ids "
        ".pre-commit-config.yaml declares (RP-12 ruling 123), so a registry that does not "
        "parse cannot say what a hook is. Repair the file, then issue the tag again."
    )


def _as_spelled(root: Path, parts: tuple[str, ...]) -> str:
    """Spell an existing repo path as the tree's directory entries spell it.

    `Path.resolve` keeps the case a path was written in on a case-insensitive
    volume, so each part is matched against its parent's entries, exactly first,
    then without regard to case.

    Returns:
        The repo-relative posix path in the tree's own spelling.

    """
    spelled: list[str] = []
    here = root
    for part in parts:
        names = [entry.name for entry in here.iterdir()]
        exact = part if part in names else None
        folded = [name for name in names if name.casefold() == part.casefold()]
        name = exact or (folded[0] if len(folded) == 1 else part)
        spelled.append(name)
        here /= name
    return PurePosixPath(*spelled).as_posix()


def _validator_scopes() -> dict[str, str]:
    """Map each `gz validate` scope's flag spelling to its stem.

    Returns:
        The flag spelling, `hexagon-tests`, against the stem, `hexagon_tests`.

    """
    return {entry.stem.replace("_", "-"): entry.stem for entry in VALIDATOR_REGISTRY}


def _check_steps() -> dict[str, str]:
    """Map each `gz check` step's written form to its display name.

    Returns:
        `module-size` against `Module size`.

    """
    return {name.lower().replace(" ", "-"): name for name, _runner in _build_check_steps()}


class ProjectSurfaces:
    """The `SurfaceRegistry` port backed by the project's own registries."""

    def __init__(self, project_root: Path) -> None:
        """Hold the project root the registries are read under; nothing is read yet."""
        self._root = project_root
        self._held: dict[str, dict[str, str]] = {}

    def resolve(self, kind: str, name: str) -> str | None:
        """Return the registry's own name for ``kind:name``, or None when it holds none.

        A hook registry present that does not parse, or a bare hook name both
        registries hold, raises `ValidationError` (exit 1) rather than guessing.

        Returns:
            The registry's own name, or None.

        """
        if kind == "path":
            return self._path(name)
        if kind == "hook":
            return self._hook(name)
        readers = {"validator": _validator_scopes, "check": _check_steps}
        if kind not in readers:
            return None
        if kind not in self._held:
            self._held[kind] = readers[kind]()
        return self._held[kind].get(name)

    def _hook(self, name: str) -> str | None:
        """Resolve a hook by its registry, `settings:<script>` or `pre-commit:<id>` (ruling 127).

        A bare name resolves when one registry alone holds it; a script is named by
        its file name with or without its suffix.

        Returns:
            The registry's own name, prefixed by its registry, or None.

        Raises:
            ValidationError: Both registries hold the bare name, or two scripts share it.

        """
        if "hook" not in self._held:
            self._held["hook"] = {
                **{f"settings:{script}": script for script in self._settings_scripts()},
                **{f"pre-commit:{hook_id}": hook_id for hook_id in self._pre_commit_ids()},
            }
        held = self._held["hook"]
        registry, colon, rest = name.partition(":")
        if colon and registry in {"settings", "pre-commit"}:
            wanted, written = (registry,), rest
        else:
            wanted, written = ("settings", "pre-commit"), name
        found = sorted(
            own
            for own, held_name in held.items()
            if own.partition(":")[0] in wanted
            and written in {held_name, PurePosixPath(held_name).stem}
        )
        if len(found) > 1:
            msg = (
                f"Hook {name!r} names more than one registered hook ({', '.join(found)}), so "
                "the tag could isolate the wrong control; a hook surface names the registry "
                "it comes from (RP-12 ruling 127). Issue it again with one of "
                f"{', '.join(f'hook:{own}' for own in found)}."
            )
            raise ValidationError(msg)
        return found[0] if found else None

    def _settings_scripts(self) -> set[str]:
        path = self._root.joinpath(*_SETTINGS.parts)
        if not path.is_file():
            return set()
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise _unreadable(_SETTINGS, str(exc)) from exc
        hooks = settings.get("hooks", {}) if isinstance(settings, dict) else {}
        commands = [
            hook.get("command", "")
            for groups in (hooks.values() if isinstance(hooks, dict) else [])
            for group in groups
            if isinstance(group, dict)
            for hook in group.get("hooks", [])
            if isinstance(hook, dict)
        ]
        return {
            PurePosixPath(token).name
            for command in commands
            if isinstance(command, str)
            for token in shlex.split(command)
            if "/" in token and "." in PurePosixPath(token).name
        }

    def _pre_commit_ids(self) -> set[str]:
        path = self._root.joinpath(*_PRE_COMMIT.parts)
        if not path.is_file():
            return set()
        try:
            config = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            raise _unreadable(_PRE_COMMIT, str(exc)) from exc
        repos = config.get("repos", []) if isinstance(config, dict) else []
        return {
            str(hook["id"])
            for repo in repos
            if isinstance(repo, dict)
            for hook in repo.get("hooks", [])
            if isinstance(hook, dict) and "id" in hook
        }

    def _path(self, name: str) -> str | None:
        """Resolve a repo path in the tree, refusing one that escapes the root.

        The registry's own name is the tree's own spelling (ruling 123), so on a
        case-insensitive volume `SRC/Stamp.py` names `src/stamp.py` and one tag-out
        per surface holds however the path is written (ruling 122).

        Returns:
            The normalized repo-relative posix path, as the tree spells it, or None.

        """
        written = PurePosixPath(name)
        if not name or "\\" in name or written.is_absolute():
            return None
        root = self._root.resolve()
        target = root.joinpath(*written.parts).resolve()
        if target == root or not target.is_relative_to(root) or not target.exists():
            return None
        return _as_spelled(root, target.relative_to(root).parts)
