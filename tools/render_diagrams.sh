#!/usr/bin/env bash
# Render mermaid sources to inline-ready SVG via mermaid-cli (system browser).
#
#   tools/render_diagrams.sh <diagrams_dir> <svg_out_dir>
#
# Uses the project-root node_modules/.bin/mmdc and puppeteer.json (which points
# at a system browser; override its executablePath for your OS).
set -euo pipefail
TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$TOOLS/.." && pwd)"
IN="${1:?usage: render_diagrams.sh <diagrams_dir> <svg_out_dir>}"
OUT="${2:?usage: render_diagrams.sh <diagrams_dir> <svg_out_dir>}"
MMDC="$PROJECT/node_modules/.bin/mmdc"
PCONF="$PROJECT/puppeteer.json"

mkdir -p "$OUT"
fail=0
for f in "$IN"/*.mmd; do
  name="$(basename "$f" .mmd)"
  if "$MMDC" -i "$f" -o "$OUT/$name.svg" -p "$PCONF" -b transparent \
        >/dev/null 2>"$OUT/$name.err"; then
    echo "ok   $name"
    rm -f "$OUT/$name.err"
  else
    echo "FAIL $name"
    sed 's/^/      /' "$OUT/$name.err" | head -8
    fail=1
  fi
done
exit $fail
