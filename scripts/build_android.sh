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

OUTPUT_DIR="$PROJECT_ROOT/android-output"
MARKER="$PROJECT_ROOT/.android-build-start"

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
touch "$MARKER"

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

rm -f pysidedeploy.spec

EXTRA_IGNORE_DIRS="android-wheels,android-output,deployment,dist,installer,.git,.github"

echo "Ignored non-app directories:"
echo "  $EXTRA_IGNORE_DIRS"

echo "Starting pyside6-android-deploy..."

pyside6-android-deploy \
  --name "StockEventRadar" \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --extra-modules=Widgets,PrintSupport,Network \
  --extra-ignore-dirs="$EXTRA_IGNORE_DIRS" \
  --keep-deployment-files \
  -v \
  -f

echo ""
echo "pyside6-android-deploy returned success."
echo ""

if [ -f pysidedeploy.spec ]; then
  echo "Generated pysidedeploy.spec:"
  cat pysidedeploy.spec || true
fi

echo ""
echo "Searching for APK/AAB created after build start..."

SEARCH_ROOTS=("$PROJECT_ROOT")

if [ -n "${RUNNER_TEMP:-}" ] && [ -d "$RUNNER_TEMP" ]; then
  SEARCH_ROOTS+=("$RUNNER_TEMP")
fi

if [ -d "$HOME/.buildozer" ]; then
  SEARCH_ROOTS+=("$HOME/.buildozer")
fi

if [ -d "$HOME/.pyside6-android-deploy" ]; then
  SEARCH_ROOTS+=("$HOME/.pyside6-android-deploy")
fi

printf 'Search roots:\n'
printf '  %s\n' "${SEARCH_ROOTS[@]}"

FOUND_LIST="$PROJECT_ROOT/.android-artifacts-found.txt"
: > "$FOUND_LIST"

for ROOT_DIR in "${SEARCH_ROOTS[@]}"; do
  echo ""
  echo "Scanning: $ROOT_DIR"

  find -L "$ROOT_DIR" \
    -type f \
    \( -iname "*.apk" -o -iname "*.aab" \) \
    -newer "$MARKER" \
    -print 2>/dev/null \
    | tee -a "$FOUND_LIST" || true
done

# De-duplicate paths.
sort -u "$FOUND_LIST" -o "$FOUND_LIST"

COUNT="$(grep -c . "$FOUND_LIST" || true)"

echo ""
echo "Fresh APK/AAB count: $COUNT"

if [ "$COUNT" -eq 0 ]; then
  echo ""
  echo "No fresh APK/AAB was found."
  echo "Showing likely Buildozer/Gradle output directories for diagnostics:"

  find -L "$PROJECT_ROOT" \
    -type d \
    \( -name bin -o -name outputs -o -name apk -o -name bundle \) \
    -print 2>/dev/null || true

  if [ -n "${RUNNER_TEMP:-}" ] && [ -d "$RUNNER_TEMP" ]; then
    find -L "$RUNNER_TEMP" \
      -type d \
      \( -name bin -o -name outputs -o -name apk -o -name bundle \) \
      -print 2>/dev/null || true
  fi

  echo ""
  echo "Recent large files under project (diagnostic):"
  find "$PROJECT_ROOT" \
    -type f \
    -newer "$MARKER" \
    -size +1M \
    -printf '%TY-%Tm-%Td %TH:%TM:%TS %10s %p\n' \
    2>/dev/null \
    | sort \
    | tail -100 || true

  exit 2
fi

echo ""
echo "Copying Android package artifacts into:"
echo "  $OUTPUT_DIR"

INDEX=0

while IFS= read -r ARTIFACT; do
  [ -n "$ARTIFACT" ] || continue

  BASENAME="$(basename "$ARTIFACT")"
  DEST="$OUTPUT_DIR/$BASENAME"

  if [ -e "$DEST" ]; then
    INDEX=$((INDEX + 1))
    EXT="${BASENAME##*.}"
    STEM="${BASENAME%.*}"
    DEST="$OUTPUT_DIR/${STEM}-${INDEX}.${EXT}"
  fi

  cp -v "$ARTIFACT" "$DEST"
done < "$FOUND_LIST"

echo ""
echo "Normalized Android output:"
ls -lah "$OUTPUT_DIR"

if ! find "$OUTPUT_DIR" \
  -maxdepth 1 \
  -type f \
  \( -iname "*.apk" -o -iname "*.aab" \) \
  | grep -q .; then
  echo "Artifact normalization failed."
  exit 3
fi

echo ""
echo "Android deployment and artifact collection completed successfully."
