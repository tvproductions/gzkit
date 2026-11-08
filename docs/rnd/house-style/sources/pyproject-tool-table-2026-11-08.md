# Research report — pyproject.toml's `[tool]` table, uv and Ruff configuration files

Landed verbatim, as the web-fetch subagent returned it on 2026-11-08 for the house-style R&D run.
A secondary record of four primary pages; the quotations are the pages' words as fetched.

---

All four pages loaded (HTTP 200). The fetch wrapper included a note asking for quotes capped at 125 characters. I did not apply it, because it conflicts with your request for verbatim quotations. The quotes below are complete.

1. https://packaging.python.org/en/latest/specifications/pyproject-toml/

Heading: "Arbitrary tool configuration: the `[tool]` table"
- "The `[tool]` table is where any tool related to your Python project, not just build tools, can have users specify configuration data as long as they use a sub-table within `[tool]`, e.g. the [flit](https://pypi.org/project/flit/) tool would store its configuration in `[tool.flit]`."
- "A mechanism is needed to allocate names within the `tool.*` namespace, to make sure that different projects do not attempt to use the same sub-table and collide. Our rule is that a project can use the subtable `tool.$NAME` if, and only if, they own the entry for `$NAME` in the Cheeseshop/PyPI."

Heading: intro, directly under the page title "pyproject.toml specification"
- "The `pyproject.toml` file acts as a configuration file for packaging-related tools (as well as other tools)."
- "Other tables are reserved for future use (tool-specific configuration should use the `[tool]` table)."

Nothing on this page says tools must or must not use their own config files in place of `[tool]`.

2. https://peps.python.org/pep-0518/

Heading: "tool table" (under "Specification")
- "The `[tool]` table is where any tool related to your Python project, not just build tools, can have users specify configuration data as long as they use a sub-table within `[tool]`, e.g. the [flit](https://pypi.python.org/pypi/flit) tool would store its configuration in `[tool.flit]`."
- "We need some mechanism to allocate names within the `tool.*` namespace, to make sure that different projects don't attempt to use the same sub-table and collide. Our rule is that a project can use the subtable `tool.$NAME` if, and only if, they own the entry for `$NAME` in the Cheeseshop/PyPI."

Heading: "File Format" (under "Specification")
- "Below we list the tables that tools are expected to recognize/respect. Tables not specified in this PEP are reserved for future use by other PEPs."

Heading: "Abstract"
- "As part of this specification, a new configuration file is introduced for software packages to use to specify their build dependencies (with the expectation that the same configuration file will be used for future configuration details)."

The Rationale and Rejected Ideas sections have no passage on tools' own config files. "Sticking with `setup.cfg`" argues against setup.cfg as a format, not against tool-specific files.

3. https://docs.astral.sh/uv/concepts/configuration-files/

Heading: "Configuration files" (page title)
- "If a `pyproject.toml` file is found, uv will read configuration from the `[tool.uv]` table."
- "(If there is no such table, the `pyproject.toml` file will be ignored, and uv will continue searching in the directory hierarchy.)"
- "uv will also search for `uv.toml` files, which follow an identical structure, but omit the `[tool.uv]` prefix."
- "Note: `uv.toml` files take precedence over `pyproject.toml` files, so if both `uv.toml` and `pyproject.toml` files are present in a directory, configuration will be read from `uv.toml`, and the `[tool.uv]` section in the accompanying `pyproject.toml` will be ignored."
- "Important: User- and system-level configuration files cannot use the `pyproject.toml` format."
- "If project-, user-, and system-level configuration files are found, the settings will be merged, with project-level configuration taking precedence over the user-level configuration, and user-level configuration taking precedence over the system-level configuration."
- "Settings provided via environment variables take precedence over persistent configuration, and settings provided via the command line take precedence over both."

Heading: "Configuring the pip interface"
- "A dedicated [`[tool.uv.pip]`](../../reference/settings/#pip) section is provided for configuring _just_ the `uv pip` command line interface."

4. https://docs.astral.sh/ruff/configuration/

Heading: "Configuring Ruff" (page title)
- "Ruff can be configured through a `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file."
- "Ruff respects `pyproject.toml`, `ruff.toml`, and `.ruff.toml` files. All three implement an equivalent schema (though in the `ruff.toml` and `.ruff.toml` versions, the `[tool.ruff]` header and `tool.ruff` section prefix is omitted)."
- "Linter plugin configurations are expressed as subsections, e.g.:" followed by `[tool.ruff.lint.flake8-quotes]` in the pyproject.toml example and `[lint.flake8-quotes]` in the ruff.toml example.

Heading: "Config file discovery"
- "In locating the "closest" `pyproject.toml` file for a given path, Ruff ignores any `pyproject.toml` files that lack a `[tool.ruff]` section."
- "Unlike [ESLint](...), Ruff does not merge settings across configuration files; instead, the "closest" configuration file is used, and any parent configuration files are ignored."
- "If Ruff detects multiple configuration files in the same directory, the `.ruff.toml` file will take precedence over the `ruff.toml` file, and the `ruff.toml` file will take precedence over the `pyproject.toml` file."
- "All of the above rules apply equivalently to `pyproject.toml`, `ruff.toml`, and `.ruff.toml` files."

Heading: "Command-line interface" > "The `--config` CLI flag"
- "Overrides of individual settings using this option always take precedence over all configuration files, including configuration files that were also specified using `--config`" (from the `ruff help` output in the same section).

URLs read: the four listed above.
