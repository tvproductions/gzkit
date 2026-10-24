#!/usr/bin/env python3
"""Create a competitor-radar monthly scan skeleton."""

from __future__ import annotations

import sys

from radar import main

if __name__ == "__main__":
    raise SystemExit(main(["new-scan", *sys.argv[1:]]))
