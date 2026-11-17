"""Today's registries a tag's surface resolves against (RP-12 O3 task 2, rulings 112 and 123).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: a tag's surface is
written `<kind>:<name>` and resolved against the registry that holds that kind
today, since no one control registry exists until RP-13's MEL (ruling 112):

- `validator:<scope>`, a `gz validate` scope in its flag's spelling,
  `validator:hexagon-tests`; the registry's own name is the scope's stem;
- `check:<step>`, a `gz check` step's name in lower case with its spaces
  hyphenated, `check:module-size`; the registry's own name is the step's;
- `hook:<name>`, a hook script `.claude/settings.json` registers, by its file name
  with or without `.py`, or a hook id `.pre-commit-config.yaml` declares
  (ruling 123); the registry's own name is the script's file name or the id;
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

        A hook registry present that does not parse raises `ValidationError` (exit 1)
        rather than reading as empty.

        Returns:
            The registry's own name, or None.

        """
        if kind == "path":
            return self._path(name)
        readers = {
            "validator": _validator_scopes,
            "check": _check_steps,
            "hook": self._hooks,
        }
        if kind not in readers:
            return None
        if kind not in self._held:
            self._held[kind] = readers[kind]()
        held = self._held[kind]
        if kind == "hook" and f"{name}.py" in held:
            return held[f"{name}.py"]
        return held.get(name)

    def _hooks(self) -> dict[str, str]:
        """Map every hook name either registry holds to the registry's own name.

        Returns:
            Each registered script's file name and each declared id, mapped to itself.

        """
        names = {script: script for script in self._settings_scripts()}
        names.update({hook_id: hook_id for hook_id in self._pre_commit_ids()})
        return names

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
            if token.endswith(".py")
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

        Returns:
            The normalized repo-relative posix path, or None.

        """
        written = PurePosixPath(name)
        if not name or "\\" in name or written.is_absolute():
            return None
        root = self._root.resolve()
        target = root.joinpath(*written.parts).resolve()
        if target == root or not target.is_relative_to(root) or not target.exists():
            return None
        return target.relative_to(root).as_posix()
