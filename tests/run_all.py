"""Minimal test runner (no pytest needed -- this sandbox's system Python
has bs4/requests installed, but the separately-installed `pytest` binary
runs in its own isolated venv without them, and pip can't reach PyPI from
here to fix that). This runner does exactly what pytest would: import
every test_*.py module and call every test_* function, reporting
pass/fail/error for each. Run with: python3 tests/run_all.py
"""

from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR.parent))


def discover_test_functions(module):
    return [
        (name, getattr(module, name))
        for name in dir(module)
        if name.startswith("test_") and callable(getattr(module, name))
    ]


def main() -> int:
    test_files = sorted(TESTS_DIR.glob("test_*.py"))
    total = 0
    failed = 0

    for test_file in test_files:
        module_name = f"tests.{test_file.stem}"
        module = importlib.import_module(module_name)

        for name, func in discover_test_functions(module):
            total += 1
            label = f"{test_file.name}::{name}"
            try:
                func()
                print(f"PASS  {label}")
            except Exception:  # noqa: BLE001
                failed += 1
                print(f"FAIL  {label}")
                traceback.print_exc()

    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
