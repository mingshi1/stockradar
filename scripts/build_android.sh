#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage:"
  echo "  ./scripts/build_android.sh /path/PySide6-android.whl /path/shiboken6-android.whl"
  exit 1
fi

PYSIDE_WHEEL="$1"
SHIBOKEN_WHEEL="$2"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

python -m pip install -r requirements-android.txt

pyside6-android-deploy \
  --name "StockEventRadar" \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --extra-modules=Widgets,PrintSupport,Network \
  -f

echo "Android deployment command finished."
echo "The generated APK/AAB location is reported by pyside6-android-deploy."
