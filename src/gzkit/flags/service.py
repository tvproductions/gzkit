"""FlagService — toggle router for the feature flag system.

Loads the flag registry, resolves flag values through the five-layer
precedence chain (registry default → env var → project config → test
override → runtime override), and provides the override API for testing
and development.  Implements ADR-0.0.8 Section 6.1 Layer 1.

Environment variables are read live on every ``is_enabled`` / ``evaluate``
call — never cached — so that test isolation works correctly when tests
manipulate ``os.environ`` between assertions.
"""

from __future__ import annotations

import os

from gzkit.flags.models import (
    FlagEvaluation,
    FlagSpec,
    InvalidFlagValueError,
    UnknownFlagError,
)

# Canonical boolean strings for env var parsing (case-insensitive).
_TRUE_STRINGS = frozenset({"true", "1", "yes"})
_FALSE_STRINGS = frozenset({"false", "0", "no"})


class FlagService:
    """Toggle router: registry + precedence resolution + override API.

    Precedence (highest wins):

    1. Registry default (lowest)
    2. Environment variable (``GZKIT_FLAG_<KEY>``)
    3. Project config (``.gzkit.json`` ``flags`` section)
    4. Test override (in-memory, per-test)
    5. Runtime override (in-memory, per-invocation, highest)
    """

    def __init__(
        self,
        registry: dict[str, FlagSpec],
        config_flags: dict[str, bool] | None = None,
    ) -> None:
        self._registry = registry
        self._config_flags: dict[str, bool] = dict(config_flags) if config_flags else {}
        self._test_overrides: dict[str, bool] = {}
        self._runtime_overrides: dict[str, bool] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_key(self, key: str) -> None:
        """Raise ``UnknownFlagError`` if *key* is not in the registry."""
        if key not in self._registry:
            msg = f"Unknown flag: {key!r}"
            raise UnknownFlagError(msg)

    @staticmethod
    def _env_var_name(key: str) -> str:
        """Convert a dotted flag key to its ``GZKIT_FLAG_`` env var name."""
        return "GZKIT_FLAG_" + key.replace(".", "_").upper()

    @staticmethod
    def _parse_bool_env(raw: str, key: str) -> bool:
        """Parse a raw env var string as a boolean.

        Raises ``InvalidFlagValueError`` for values outside the canonical set.
        """
        lower = raw.lower()
        if lower in _TRUE_STRINGS:
            return True
        if lower in _FALSE_STRINGS:
            return False
        env_name = "GZKIT_FLAG_" + key.replace(".", "_").upper()
        msg = f"Invalid boolean value for {env_name}: {raw!r}"
        raise InvalidFlagValueError(msg)

    def _resolve(self, key: str) -> tuple[bool, str]:
        """Walk the precedence chain and return ``(value, source_layer)``."""
        self._validate_key(key)

        # Layer 1 — registry default
        value: bool = self._registry[key].default
        source: str = "registry"

        # Layer 2 — environment variable (read live, never cached)
        env_val = os.environ.get(self._env_var_name(key))
        if env_val is not None:
            value = self._parse_bool_env(env_val, key)
            source = "env"

        # Layer 3 — project config (.gzkit.json flags section)
        if key in self._config_flags:
            value = self._config_flags[key]
            source = "config"

        # Layer 4 — test override
        if key in self._test_overrides:
            value = self._test_overrides[key]
            source = "test"

        # Layer 5 — runtime override (highest)
        if key in self._runtime_overrides:
            value = self._runtime_overrides[key]
            source = "runtime"

        return value, source

    # ------------------------------------------------------------------
    # Public query API
    # ------------------------------------------------------------------

    def is_enabled(self, key: str) -> bool:
        """Return the resolved boolean for *key*.

        Raises:
            UnknownFlagError: If *key* is not in the registry.
            InvalidFlagValueError: If the env var has a non-boolean value.
        """
        value, _ = self._resolve(key)
        return value

    def evaluate(self, key: str) -> FlagEvaluation:
        """Return a ``FlagEvaluation`` with the resolved value and source.

        Raises:
            UnknownFlagError: If *key* is not in the registry.
            InvalidFlagValueError: If the env var has a non-boolean value.
        """
        value, source = self._resolve(key)
        return FlagEvaluation(key=key, value=value, source=source)

    def list_flags(self) -> list[FlagEvaluation]:
        """Return evaluations for every registered flag, sorted by key."""
        return [self.evaluate(key) for key in sorted(self._registry)]

    # ------------------------------------------------------------------
    # Override API
    # ------------------------------------------------------------------

    def set_test_override(self, key: str, value: bool) -> None:
        """Set a test-scoped override (Layer 4).

        Raises ``UnknownFlagError`` if *key* is not in the registry.
        """
        self._validate_key(key)
        self._test_overrides[key] = value

    def clear_test_overrides(self) -> None:
        """Remove all test overrides, restoring normal precedence."""
        self._test_overrides.clear()

    def set_runtime_override(self, key: str, value: bool) -> None:
        """Set a runtime debugging override (Layer 5, highest precedence).

        Raises ``UnknownFlagError`` if *key* is not in the registry.
        """
        self._validate_key(key)
        self._runtime_overrides[key] = value
