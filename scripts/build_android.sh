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
FOUND_LIST="$PROJECT_ROOT/.android-artifacts-found.txt"

# The official Qt Android wheels used by this workflow are cp311,
# so python-for-android must build a matching Python 3.11 runtime.
ANDROID_PYTHON_VERSION="${ANDROID_PYTHON_VERSION:-3.11.15}"

echo "=========================================="
echo " StockEventRadar Android Build"
echo "=========================================="
echo
echo "Project root:"
echo "  $PROJECT_ROOT"
echo "Android target Python:"
echo "  $ANDROID_PYTHON_VERSION"
echo

python --version

python - <<'PY'
import sys
import PySide6
import PySide6.QtCore

print("Host Python:", sys.version)
print("PySide6:", PySide6.__version__)
print("Qt:", PySide6.QtCore.__version__)
print("PySide6 path:", PySide6.__file__)

if sys.version_info[:2] != (3, 11):
    raise SystemExit(
        "Android host environment must use Python 3.11 "
        "for the cp311 Android wheels."
    )
PY

echo
echo "Android wheels:"
ls -lh "$PYSIDE_WHEEL" "$SHIBOKEN_WHEEL"

case "$(basename "$PYSIDE_WHEEL")" in
  *cp311*android_aarch64.whl) ;;
  *)
    echo "ERROR: PySide Android wheel is not the expected cp311 aarch64 wheel."
    exit 10
    ;;
esac

case "$(basename "$SHIBOKEN_WHEEL")" in
  *cp311*android_aarch64.whl) ;;
  *)
    echo "ERROR: Shiboken Android wheel is not the expected cp311 aarch64 wheel."
    exit 11
    ;;
esac

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

rm -f "$MARKER" "$FOUND_LIST"
touch "$MARKER"
: > "$FOUND_LIST"

# CRITICAL:
# RC4.6 showed p4a selecting Python 3.14.2 even though the Qt Android
# wheel is cp311. Remove that stale distribution before rebuilding.
echo
echo "Removing stale Buildozer/p4a project cache..."
rm -rf "$PROJECT_ROOT/.buildozer"

rm -f pysidedeploy.spec buildozer.spec

EXTRA_IGNORE_DIRS="android-wheels,android-output,deployment,dist,installer,.git,.github"

echo
echo "Ignored non-app directories:"
echo "  $EXTRA_IGNORE_DIRS"

# Buildozer supports overriding buildozer.spec values with SECTION_TOKEN
# environment variables. Qt 6.11.1 writes unpinned:
#   requirements = python3,shiboken6,PySide6
# Pin BOTH target python and hostpython to the cp311 runtime.
export APP_REQUIREMENTS="python3==${ANDROID_PYTHON_VERSION},hostpython3==${ANDROID_PYTHON_VERSION},shiboken6,PySide6"

echo
echo "Buildozer requirements override:"
echo "  APP_REQUIREMENTS=$APP_REQUIREMENTS"
echo

pyside6-android-deploy \
  --name "StockEventRadar" \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --extra-modules=Widgets,PrintSupport,Network \
  --extra-ignore-dirs="$EXTRA_IGNORE_DIRS" \
  --keep-deployment-files \
  -v \
  -f

echo
echo "pyside6-android-deploy returned success."
echo

if [ -f buildozer.spec ]; then
  echo "Generated buildozer requirements line:"
  grep -nE '^[[:space:]]*requirements[[:space:]]*=' buildozer.spec || true

  echo
  echo "Environment override remains:"
  echo "  APP_REQUIREMENTS=$APP_REQUIREMENTS"
fi

echo
echo "Checking p4a Python version evidence..."

if find "$PROJECT_ROOT/.buildozer" -type f -o -type d 2>/dev/null \
  | grep -E '3\.14(\.|/|_)' >/dev/null 2>&1; then
  echo "ERROR: Python 3.14 artifacts are still present in the fresh Android build."
  echo "The cp311 PySide6 Android wheel requires the target runtime to stay on Python 3.11."
  find "$PROJECT_ROOT/.buildozer" \
    \( -type f -o -type d \) \
    2>/dev/null \
    | grep -E '3\.14(\.|/|_)' \
    | head -100 || true
  exit 12
fi

echo "No Python 3.14 paths detected in fresh project build cache."

echo
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

for ROOT_DIR in "${SEARCH_ROOTS[@]}"; do
  echo
  echo "Scanning: $ROOT_DIR"

  find -L "$ROOT_DIR" \
    -type f \
    \( -iname "*.apk" -o -iname "*.aab" \) \
    -newer "$MARKER" \
    -print 2>/dev/null \
    | tee -a "$FOUND_LIST" || true
done

sort -u "$FOUND_LIST" -o "$FOUND_LIST"

COUNT="$(grep -c . "$FOUND_LIST" || true)"

echo
echo "Fresh APK/AAB count: $COUNT"

if [ "$COUNT" -eq 0 ]; then
  echo
  echo "No fresh APK/AAB was found."
  echo
  echo "Buildozer configuration:"
  if [ -f buildozer.spec ]; then
    grep -nE \
      'requirements|p4a\.branch|p4a\.bootstrap|android\.archs|android\.api|android\.minapi|bin_dir' \
      buildozer.spec || true
  fi

  echo
  echo "Python recipe/download evidence:"
  find "$PROJECT_ROOT/.buildozer" \
    -maxdepth 8 \
    \( -iname "*python3*" -o -iname "*hostpython3*" \) \
    -print 2>/dev/null \
    | head -200 || true

  echo
  echo "Recent Buildozer/Gradle output-like paths:"
  find "$PROJECT_ROOT/.buildozer" \
    -type d \
    \( -name bin -o -name outputs -o -name apk -o -name bundle -o -name dists \) \
    -print 2>/dev/null || true

  echo
  echo "Recent large files under project:"
  find "$PROJECT_ROOT" \
    -type f \
    -newer "$MARKER" \
    -size +1M \
    -printf '%TY-%Tm-%Td %TH:%TM:%TS %10s %p\n' \
    2>/dev/null \
    | sort \
    | tail -150 || true

  exit 2
fi

echo
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

echo
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

echo
echo "Android deployment and artifact collection completed successfully."
