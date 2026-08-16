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

echo "Project root:"
echo "  $PROJECT_ROOT"

echo "Python:"
python --version

echo "Desktop PySide6 deploy tool:"
python - <<'PY'
import PySide6
import PySide6.QtCore

print("PySide6", PySide6.__version__)
print("Qt", PySide6.QtCore.__version__)
print(PySide6.__file__)
PY

echo "Android wheels:"
ls -lh "$PYSIDE_WHEEL" "$SHIBOKEN_WHEEL"

# Never reuse a desktop deployment spec for Android.
rm -f pysidedeploy.spec

# The deploy tool scans the application project directory for Python files.
# Explicitly ignore build/download/output folders that are not application code.
EXTRA_IGNORE_DIRS="android-wheels,android-output,deployment,dist,installer,.git,.github"

echo "Ignored non-app directories:"
echo "  $EXTRA_IGNORE_DIRS"

pyside6-android-deploy \
  --name "StockEventRadar" \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --extra-modules=Widgets,PrintSupport,Network \
  --extra-ignore-dirs="$EXTRA_IGNORE_DIRS" \
  --keep-deployment-files \
  -v \
  -f

echo "Android deployment command finished."

find . \
  -maxdepth 8 \
  \( -name "*.apk" -o -name "*.aab" \) \
  -print
