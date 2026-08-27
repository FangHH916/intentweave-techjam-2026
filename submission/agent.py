"""Standalone TechJam entry file; export: Agent."""

from __future__ import annotations

from pathlib import Path
import sys


SOURCE = Path(__file__).resolve().parent / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from intentweave.agent import Agent  # noqa: E402

__all__ = ["Agent"]
