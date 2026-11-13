"""Guard against re-introducing the unrelated ``tk`` PyPI package.

``tkinter`` ships with the Python standard library. The PyPI distribution
named ``tk`` is an unrelated third-party package ("TensorKit") and must
never be installed by ``make install`` or bundled by PyInstaller.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"
FORBIDDEN = {"tk"}


def _requirement_names(text: str) -> set[str]:
    names: set[str] = set()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line)
        if match:
            names.add(re.sub(r"[-_.]+", "-", match.group(0)).lower())
    return names


def test_requirements_do_not_pin_third_party_tk() -> None:
    names = _requirement_names(REQUIREMENTS.read_text(encoding="utf-8"))
    assert not names & FORBIDDEN


def test_parser_detects_forbidden_name() -> None:
    assert "tk" in _requirement_names("tk==0.1.0  # wrong package\n")
    assert "tk" not in _requirement_names("tkinter-tooltip==1.0\n")


def _top_level_imports(source: str) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".")[0])
    return modules


def test_no_module_imports_the_tk_distribution() -> None:
    sources = sorted(ROOT.glob("*.py"))
    assert sources, "expected the application modules next to requirements.txt"
    for path in sources:
        imports = _top_level_imports(path.read_text(encoding="utf-8"))
        assert "tk" not in imports, path.name
