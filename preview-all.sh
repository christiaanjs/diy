#!/usr/bin/env bash
# preview-all.sh — render all views for a project to named PNG files.
#
# Usage:
#   ./preview-all.sh <project-slug>
#
# Outputs:
#   projects/<slug>/preview-iso.png
#   projects/<slug>/preview-front.png
#   projects/<slug>/preview-back.png
#   projects/<slug>/preview-side.png
#   projects/<slug>/preview-left.png
#   projects/<slug>/preview-top.png

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <project-slug>" >&2
    exit 1
fi

SLUG="$1"
PROJ_DIR="projects/$SLUG"

if [[ ! -d "$PROJ_DIR" ]]; then
    echo "error: project '$SLUG' not found" >&2
    exit 1
fi

VIEWS=(front back side left top)

echo "--- ISO ---"
python view.py "$SLUG" --output "$PROJ_DIR/exports/preview.png"
for VIEW in "${VIEWS[@]}"; do
    echo "--- $VIEW ---"
    python view.py "$SLUG" --view "$VIEW" --output "$PROJ_DIR/exports/preview-${VIEW}.png"
done

DIAGS=(exploded elevation cutlist)
for DIAG in "${DIAGS[@]}"; do
    echo "--- $DIAG ---"
    python diag.py "$SLUG" "$DIAG" --output "$PROJ_DIR/exports/${DIAG}.png"
done

echo ""
echo "Done. Files written to $PROJ_DIR/:"
ls "$PROJ_DIR"/preview-*.png
