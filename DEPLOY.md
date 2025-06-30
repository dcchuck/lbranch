# Deployment Guide

## Quick Deploy

```bash
# 1. Update version
./update-version.sh 0.1.3

# 2. Build and upload to PyPI
rm -rf dist/ build/
python -m build
python -m twine upload dist/* -u __token__ -p $PYPI_TOKEN

# 3. Tag release
git tag v0.1.3 && git push --tags

# 4. Update Homebrew
# See ../homebrew-lbranch/README.md
```
