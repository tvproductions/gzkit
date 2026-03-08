# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for gzkit.

Builds a single-file executable for the `gz` CLI.

Usage:
    pyinstaller gz.spec

Output:
    dist/gz.exe  (Windows)
    dist/gz      (macOS/Linux)
"""

import sys
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────
SRC = Path("src/gzkit")
TEMPLATES = [(str(SRC / "templates" / f), "gzkit/templates")
             for f in (SRC / "templates").iterdir()
             if f.suffix == ".md"]
SCHEMAS = [(str(SRC / "schemas" / f), "gzkit/schemas")
           for f in (SRC / "schemas").iterdir()
           if f.suffix == ".json"]

# Collect all non-Python data files that must be bundled
datas = TEMPLATES + SCHEMAS

# ── Analysis ─────────────────────────────────────────────────────────
a = Analysis(
    [str(SRC / "cli.py")],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "gzkit.commands.attest",
        "gzkit.commands.chores",
        "gzkit.commands.common",
        "gzkit.commands.plan",
        "gzkit.commands.state",
        "gzkit.commands.status",
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
