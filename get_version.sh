#!/bin/bash
# This script determines the current package version based on Git tags and commits.

set -e # Exit immediately in case of error, do not ignore errors

# Determine the package version from Git
current_commit=$(git rev-parse HEAD)
latest_tag_commit=$(git rev-list -n 1 --tags --abbrev=0)

if [ "$current_commit" == "$latest_tag_commit" ]; then
    PKG_VERSION=$(git describe --tags --abbrev=0)
else
    commit_hash=$(git rev-parse --short HEAD)
    date=$(date +%Y%m%d)
    PKG_VERSION="0.0.1.dev${date}+${commit_hash}"
fi

echo $PKG_VERSION
