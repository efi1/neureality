#!/usr/bin/env bash
set -euo pipefail

# Detect project root (directory of script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try to detect package name
if [[ -f "$PROJECT_ROOT/setup.py" ]]; then
    PACKAGE_NAME=$(python "$PROJECT_ROOT/setup.py" --name)
elif [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    PACKAGE_NAME=$(grep -E '^\s*name\s*=' "$PROJECT_ROOT/pyproject.toml" | head -1 | cut -d '"' -f2)
else
    echo "❌ No setup.py or pyproject.toml found."
    exit 1
fi

echo "🧹 Cleaning package: $PACKAGE_NAME"

# Uninstall from venv
pip uninstall -y "$PACKAGE_NAME" || true

# Remove build artifacts
rm -rf \
  "$PROJECT_ROOT/build" \
  "$PROJECT_ROOT/dist" \
  "$PROJECT_ROOT"/*.egg-info \
  "$PROJECT_ROOT"/**/*.egg-info 2>/dev/null || true

echo "✅ Package $PACKAGE_NAME removed."
