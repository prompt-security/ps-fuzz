from importlib.metadata import metadata

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def test_installed_distribution_requires_python_310_or_newer():
    """Published package metadata must refuse Python 3.9 installs."""
    requires_python = metadata("prompt-security-fuzzer")["Requires-Python"]
    supported = SpecifierSet(requires_python)

    assert Version("3.9") not in supported
    assert Version("3.10") in supported
