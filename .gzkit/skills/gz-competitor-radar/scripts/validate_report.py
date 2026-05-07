#!/usr/bin/env python3
"""Validate competitor-radar generated Markdown reports."""

from __future__ import annotations

from radar import main

if __name__ == "__main__":
    raise SystemExit(main(["validate"]))
