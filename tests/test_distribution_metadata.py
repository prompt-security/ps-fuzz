import os
import subprocess
import sys
from importlib.metadata import metadata
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_installed_distribution_requires_python_310_or_newer():
    """Published package metadata must refuse Python 3.9 installs."""
    requires_python = metadata("prompt-security-fuzzer")["Requires-Python"]
    supported = SpecifierSet(requires_python)

    assert Version("3.9") not in supported
    assert Version("3.10") in supported


def test_release_version_comes_from_pkg_version_environment():
    """PEP 621 metadata must not override the tag-derived release version."""
    environment = os.environ.copy()
    environment["PKG_VERSION"] = "2.1.1"

    result = subprocess.run(
        [sys.executable, "setup.py", "--version"],
        cwd=PROJECT_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines()[-1] == "2.1.1"
