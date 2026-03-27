# ruff: noqa: F821
"""PyInstaller spec file for gzkit.

Builds a single-file executable for the `gz` CLI.

Usage:
    pyinstaller gz.spec

Output:
    dist/gz.exe  (Windows)
    dist/gz      (macOS/Linux)
"""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────
SRC = Path("src/gzkit")
TEMPLATES = [(str(f), "gzkit/templates")
             for f in (SRC / "templates").iterdir()
             if f.suffix == ".md"]
SCHEMAS = [(str(f), "gzkit/schemas")
           for f in (SRC / "schemas").iterdir()
           if f.suffix == ".json"]

# Collect all non-Python data files that must be bundled
datas = TEMPLATES + SCHEMAS

# ── Analysis ─────────────────────────────────────────────────────────
a = Analysis(
    [str(SRC / "cli" / "main.py")],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # CLI package
        "gzkit.cli",
        "gzkit.cli.formatters",
        "gzkit.cli.logging",
        "gzkit.cli.main",
        "gzkit.cli.parser",
        "gzkit.cli.progress",
        # Command modules
        "gzkit.commands.adr_audit",
        "gzkit.commands.adr_promote",
        "gzkit.commands.attest",
        "gzkit.commands.audit_cmd",
        "gzkit.commands.chores",
        "gzkit.commands.cli_audit",
        "gzkit.commands.closeout",
        "gzkit.commands.common",
        "gzkit.commands.config_paths",
        "gzkit.commands.drift",
        "gzkit.commands.gates",
        "gzkit.commands.init_cmd",
        "gzkit.commands.interview_cmd",
        "gzkit.commands.obpi_cmd",
        "gzkit.commands.parity",
        "gzkit.commands.plan",
        "gzkit.commands.preflight",
        "gzkit.commands.quality",
        "gzkit.commands.readiness",
        "gzkit.commands.register",
        "gzkit.commands.roles",
        "gzkit.commands.skills_cmd",
        "gzkit.commands.specify_cmd",
        "gzkit.commands.state",
        "gzkit.commands.status",
        "gzkit.commands.sync",
        "gzkit.commands.tidy",
        "gzkit.commands.validate_cmd",
        # Core modules
        "gzkit.config",
        "gzkit.decomposition",
        "gzkit.hooks.claude",
        "gzkit.hooks.copilot",
        "gzkit.hooks.core",
        "gzkit.hooks.guards",
        "gzkit.hooks.obpi",
        "gzkit.interview",
        "gzkit.ledger",
        "gzkit.quality",
        "gzkit.skills",
        "gzkit.sync",
        "gzkit.triangle",
        "gzkit.utils",
        "gzkit.validate",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude dev/docs-only dependencies to keep binary small
        "mkdocs",
        "mkdocs_material",
        "ruff",
        "coverage",
        "pytest",
        # Exclude unused stdlib modules
        "tkinter",
        "unittest",
        "test",
    ],
    noarchive=False,
)

# ── Bundle ───────────────────────────────────────────────────────────
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="gz",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
