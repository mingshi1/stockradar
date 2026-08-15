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

rm -f pysidedeploy.spec

pyside6-android-deploy \
  --name "StockEventRadar" \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --extra-modules=Widgets,PrintSupport,Network \
  --keep-deployment-files \
  -v \
  -f

echo "Android deployment command finished."
find . -maxdepth 5 \( -name "*.apk" -o -name "*.aab" \) -print
