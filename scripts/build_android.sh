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
DEPLOY_LOG="$PROJECT_ROOT/android-deploy.log"

ANDROID_PYTHON_VERSION="${ANDROID_PYTHON_VERSION:-3.11.15}"
P4A_RELEASE="${P4A_RELEASE:-v2026.05.09}"

echo "=========================================="
echo " StockEventRadar Android Build RC4.9"
echo "=========================================="
echo
echo "Project root:"
echo "  $PROJECT_ROOT"
echo "Android target Python:"
echo "  $ANDROID_PYTHON_VERSION"
echo "python-for-android release:"
echo "  $P4A_RELEASE"
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

echo
echo "Validating Android wheel ABI/platform metadata..."

python - "$PYSIDE_WHEEL" "$SHIBOKEN_WHEEL" <<'PY'
from pathlib import Path
from packaging.utils import parse_wheel_filename
import sys

for raw_path in sys.argv[1:]:
    path = Path(raw_path)

    if not path.is_file():
        raise SystemExit(f"Wheel does not exist: {path}")

    name, version, build, tags = parse_wheel_filename(path.name)

    valid = any(
        tag.interpreter == "cp311"
        and tag.abi == "cp311"
        and tag.platform == "android_aarch64"
        for tag in tags
    )

    print(
        f"{path.name}: name={name}, version={version}, "
        f"tags={sorted(map(str, tags))}"
    )

    if not valid:
        raise SystemExit(
            f"{path.name} is not a cp311/cp311 android_aarch64 wheel."
        )

print("Android wheel ABI/platform validation: OK")
PY

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

rm -f "$MARKER" "$FOUND_LIST" "$DEPLOY_LOG"
touch "$MARKER"
: > "$FOUND_LIST"

echo
echo "Removing project Buildozer cache..."
rm -rf "$PROJECT_ROOT/.buildozer"
rm -f pysidedeploy.spec buildozer.spec

EXTRA_IGNORE_DIRS="android-wheels,android-output,deployment,dist,installer,.git,.github"

# Double protection: Buildozer officially supports SECTION_OPTION
# environment overrides. The installed Qt helper is also patched in CI.
export APP_REQUIREMENTS="python3==${ANDROID_PYTHON_VERSION},hostpython3==${ANDROID_PYTHON_VERSION},shiboken6,PySide6"
export APP_P4A_BRANCH="$P4A_RELEASE"
export BUILDOZER_LOG_LEVEL="2"

echo
echo "Buildozer overrides:"
echo "  APP_REQUIREMENTS=$APP_REQUIREMENTS"
echo "  APP_P4A_BRANCH=$APP_P4A_BRANCH"
echo "  BUILDOZER_LOG_LEVEL=$BUILDOZER_LOG_LEVEL"
echo

set +e

pyside6-android-deploy \
  --name "StockEventRadar" \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --extra-modules=Widgets,PrintSupport,Network \
  --extra-ignore-dirs="$EXTRA_IGNORE_DIRS" \
  --keep-deployment-files \
  -v \
  -f \
  2>&1 | tee "$DEPLOY_LOG"

DEPLOY_RC="${PIPESTATUS[0]}"

set -e

echo
echo "pyside6-android-deploy process return code:"
echo "  $DEPLOY_RC"

if [ -f buildozer.spec ]; then
  echo
  echo "Generated Buildozer settings:"
  grep -nE \
    '^[[:space:]]*(requirements|p4a\.branch|p4a\.bootstrap|android\.archs|android\.api|android\.minapi)[[:space:]]*=' \
    buildozer.spec || true
fi

# Qt 6.11.1 currently logs/catches some build failures in a way that can
# leave the outer deploy process with a misleading success path.
# Trust both process status AND the log content.
BUILD_FAILED=0

if [ "$DEPLOY_RC" -ne 0 ]; then
  BUILD_FAILED=1
fi

if grep -qE \
  'Buildozer failed to execute|returned non-zero exit status|RuntimeError: \[DEPLOY\].*buildozer android' \
  "$DEPLOY_LOG"; then
  BUILD_FAILED=1
fi

if [ "$BUILD_FAILED" -ne 0 ]; then
  echo
  echo "=========================================="
  echo " REAL ANDROID BUILD FAILURE DETECTED"
  echo "=========================================="
  echo
  echo "The useful error is ABOVE the final Buildozer summary."
  echo "Relevant error lines from android-deploy.log:"
  echo

  grep -nEi \
    'error:|failed|failure|exception|traceback|could not|cannot |no matching|not found|command failed|undefined reference|fatal:' \
    "$DEPLOY_LOG" \
    | tail -160 || true

  echo
  echo "Last 220 lines of the complete deploy log:"
  tail -220 "$DEPLOY_LOG" || true

  exit 20
fi

echo
echo "Android deploy command completed without a detected Buildozer failure."

echo
echo "Searching for fresh APK/AAB..."

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

for ROOT_DIR in "${SEARCH_ROOTS[@]}"; do
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

echo "Fresh APK/AAB count: $COUNT"

if [ "$COUNT" -eq 0 ]; then
  echo
  echo "Deploy did not report a failure, but no APK/AAB was found."
  echo "Last 220 lines of android-deploy.log:"
  tail -220 "$DEPLOY_LOG" || true
  exit 21
fi

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
  exit 22
fi

echo
echo "Android deployment and artifact collection completed successfully."
