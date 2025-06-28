"""
lbranch - A Git utility that shows recently checked out branches in chronological order.
"""

from pathlib import Path
from .main import main

# Read version from VERSION file
_version_file = Path(__file__).parent.parent / 'VERSION'
__version__ = _version_file.read_text().strip()

__all__ = ['main']
