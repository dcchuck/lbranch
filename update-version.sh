#!/bin/bash

# Script to update version across all files
# Usage: ./update-version.sh <new-version>

if [ -z "$1" ]; then
    echo "Usage: $0 <new-version>"
    echo "Example: $0 0.1.2"
    exit 1
fi

NEW_VERSION="$1"

# Update VERSION file
echo "$NEW_VERSION" > VERSION
echo "✓ Updated VERSION file to $NEW_VERSION"

# Update pyproject.toml
if [ -f pyproject.toml ]; then
    # Use sed to update the version line
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS requires backup extension
        sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    else
        # Linux
        sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    fi
    echo "✓ Updated pyproject.toml to $NEW_VERSION"
fi

echo "✓ Version updated to $NEW_VERSION in all files"
echo ""
echo "Python files now read version from VERSION file automatically."