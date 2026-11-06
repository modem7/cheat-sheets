#!/usr/bin/env bash
# Local preview: keep site/.build/content in sync with the sheets and run hugo server.
# Usage (from anywhere): ./site/scripts/dev.sh [extra hugo server args]
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
site="$(dirname "${here}")"

python3 "${here}/prepare-content.py"
python3 "${here}/prepare-content.py" --watch > /dev/null &
watcher=$!
trap 'kill "${watcher}" 2>/dev/null || true' EXIT INT TERM

hugo server --source "${site}" --disableFastRender "$@"
