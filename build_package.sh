#!/bin/bash
set -e # Exit immediately in case of error, do not ignore errors

echo "Installing required Python packaging tools ..."
python -m pip install --upgrade pip setuptools wheel

echo "Cleaning up previous builds..."
rm -rf build/ dist/ *.egg-info

echo "Building the package..."
python setup.py sdist bdist_wheel

echo "Build output:"
ls dist

# Optional Step 5: Install the package locally for testing
# Uncomment the line below to enable installation after build
# pip install dist/*.whl

echo "Package built successfully."
