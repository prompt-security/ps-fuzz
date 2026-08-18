import ast
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_package_boms_require_python_310_or_newer():
    """Both published metadata sources must reject Python 3.9."""
    pyproject = (PROJECT_ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    setup_py = (PROJECT_ROOT / 'setup.py').read_text(encoding='utf-8')

    assert 'requires-python = ">=3.10"' in pyproject
    assert "python_requires='>=3.10'" in setup_py
    assert 'Python :: 3.9' not in pyproject
    assert 'Python :: 3.9' not in setup_py


def test_dependency_boms_stay_aligned_and_include_dependabot_fixes():
    """PEP 621 and setup.py must publish the same secure runtime dependencies."""
    pyproject = (PROJECT_ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    pyproject_block = pyproject.split('dependencies = [', 1)[1].split(']\n\n[project.optional-dependencies]', 1)[0]
    pyproject_dependencies = re.findall(r'^\s*"([^"]+)",?$', pyproject_block, flags=re.MULTILINE)

    setup_tree = ast.parse((PROJECT_ROOT / 'setup.py').read_text(encoding='utf-8'))
    setup_call = next(
        node for node in ast.walk(setup_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'setup'
    )
    install_requires = next(keyword.value for keyword in setup_call.keywords if keyword.arg == 'install_requires')
    setup_dependencies = [element.value for element in install_requires.elts]

    assert setup_dependencies == pyproject_dependencies
    assert {
        'langchain>=1.3.9,<2.0.0',
        'langchain-core>=1.5.4,<2.0.0',
        'python-dotenv>=1.2.2,<2.0.0',
    }.issubset(set(pyproject_dependencies))


def test_build_configuration_includes_attack_subpackages():
    """The wheel must include attack modules, not just the top-level package."""
    pyproject = (PROJECT_ROOT / 'pyproject.toml').read_text(encoding='utf-8')

    assert '[tool.setuptools.packages.find]' in pyproject
    assert 'include = ["ps_fuzz*"]' in pyproject
    assert 'packages = ["ps_fuzz"]' not in pyproject


def test_ci_only_tests_supported_python_versions():
    """The supported-version test matrix must not silently restore Python 3.9."""
    workflow = (PROJECT_ROOT / '.github' / 'workflows' / 'ci.yml').read_text(encoding='utf-8')

    assert "python-version: ['3.10', '3.11']" in workflow
    assert "'3.9'" not in workflow


def test_ci_clean_installs_the_built_release_wheel():
    """The release build must be tested as an installed artifact in CI."""
    workflow = (PROJECT_ROOT / '.github' / 'workflows' / 'ci.yml').read_text(encoding='utf-8')

    assert '- name: Verify built wheel' in workflow
    assert '.package-test-venv/bin/python -m pip install dist/*.whl' in workflow
    assert '.package-test-venv/bin/prompt-security-fuzzer --list-providers' in workflow


def test_current_development_docs_require_python_310_or_newer():
    """Setup instructions must not create an unsupported Python 3.9 environment."""
    contributing = (PROJECT_ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8')
    claude = (PROJECT_ROOT / 'claude.md').read_text(encoding='utf-8')
    readme = (PROJECT_ROOT / 'README.md').read_text(encoding='utf-8')

    assert 'Python 3.10 or later' in contributing
    assert 'python3.10 -m venv venv' in contributing
    assert 'py -3.10 -m venv venv' in contributing
    assert 'Python >= 3.10' in claude
    assert 'Python 3.10 or newer' in readme


def test_fastparquet_round_trip_with_the_resolved_runtime_dependencies(tmp_path):
    """Parquet-backed attacks must work with the NumPy version LangChain resolves."""
    import fastparquet
    import pandas as pd

    assert fastparquet.__version__
    dataset = pd.DataFrame({'prompt': ['test prompt'], 'response': ['test response']})
    dataset_path = tmp_path / 'attack-data.parquet'

    dataset.to_parquet(dataset_path, engine='fastparquet')

    assert pd.read_parquet(dataset_path, engine='fastparquet').equals(dataset)
