"""Test version consistency across files."""

import pytest
from pathlib import Path
from lbranch.version import __version__


def test_version_consistency():
    """Verify version is consistent between VERSION file and version.py."""
    # Read VERSION file
    version_file = Path(__file__).parent.parent / 'VERSION'
    file_version = version_file.read_text().strip()
    
    # Compare with hardcoded version
    assert __version__ == file_version, (
        f"Version mismatch: version.py has '{__version__}' "
        f"but VERSION file has '{file_version}'"
    )


def test_pyproject_version_consistency():
    """Verify version is consistent between pyproject.toml and version.py."""
    # Read pyproject.toml
    pyproject_file = Path(__file__).parent.parent / 'pyproject.toml'
    pyproject_content = pyproject_file.read_text()
    
    # Extract version from pyproject.toml
    import re
    match = re.search(r'^version = "(.+)"', pyproject_content, re.MULTILINE)
    assert match, "Could not find version in pyproject.toml"
    
    pyproject_version = match.group(1)
    
    # Compare with hardcoded version
    assert __version__ == pyproject_version, (
        f"Version mismatch: version.py has '{__version__}' "
        f"but pyproject.toml has '{pyproject_version}'"
    )