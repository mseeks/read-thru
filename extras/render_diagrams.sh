#!/usr/bin/env bash
# OPTIONAL: render Mermaid sources to inline-ready SVG via mermaid-cli.
#
#   extras/render_diagrams.sh <diagrams_dir> <svg_out_dir>
#
# Uses `npx` so there's no committed Node project — it fetches mermaid-cli on
# demand. puppeteer.json (next to this script) points at a system browser;
# override its executablePath for your OS, or set PUPPETEER_EXECUTABLE_PATH.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IN="${1:?usage: render_diagrams.sh <diagrams_dir> <svg_out_dir>}"
OUT="${2:?usage: render_diagrams.sh <diagrams_dir> <svg_out_dir>}"
PCONF="$HERE/puppeteer.json"

mkdir -p "$OUT"
fail=0
for f in "$IN"/*.mmd; do
  name="$(basename "$f" .mmd)"
  if npx -y @mermaid-js/mermaid-cli -i "$f" -o "$OUT/$name.svg" -p "$PCONF" \
        -b transparent >/dev/null 2>"$OUT/$name.err"; then
    echo "ok   $name"
    rm -f "$OUT/$name.err"
  else
    echo "FAIL $name"
    sed 's/^/      /' "$OUT/$name.err" | head -8
    fail=1
  fi
done
exit $fail
