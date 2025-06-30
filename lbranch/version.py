"""Version information for lbranch."""

from pathlib import Path

_version_file = Path(__file__).parent.parent / 'VERSION'
__version__ = _version_file.read_text().strip()
