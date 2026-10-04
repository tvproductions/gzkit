#!/usr/bin/env python3
"""Render competitor-radar Markdown reports from JSON."""

from __future__ import annotations

from radar import main

if __name__ == "__main__":
    raise SystemExit(main(["render"]))
