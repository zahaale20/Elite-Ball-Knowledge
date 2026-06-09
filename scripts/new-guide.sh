#!/usr/bin/env bash
#
# new-guide.sh — scaffold a new guide with the next free number in a folder.
#
# Usage:
#   ./scripts/new-guide.sh <folder> "Guide Title"
#
# Example:
#   ./scripts/new-guide.sh autonomy "Swarm Coordination Under Comms Denial"
#   -> creates autonomy/30-swarm-coordination-under-comms-denial.md from the template
#
# It finds the highest NN- prefix in the folder, adds 1, slugifies the title, and
# fills the H1. It never touches existing files. See CONTRIBUTING.md for conventions.

set -euo pipefail

# --- locate repo root (parent of this script's dir) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$ROOT_DIR/templates/GUIDE_TEMPLATE.md"

# --- args ---
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <folder> \"Guide Title\"" >&2
  echo "Folders: foundations autonomy career companies engineering software \\" >&2
  echo "         mathematics mindset-and-society information-environment general \\" >&2
  echo "         compute-and-hardware space products tooling" >&2
  exit 1
fi

FOLDER="$1"
TITLE="$2"
DIR="$ROOT_DIR/$FOLDER"

if [[ ! -d "$DIR" ]]; then
  echo "Error: folder '$FOLDER' does not exist at $DIR" >&2
  echo "If you intend to create a new topic band, make the folder first (see CONTRIBUTING.md)." >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Error: template not found at $TEMPLATE" >&2
  exit 1
fi

# --- find the next free two-digit number ---
max=0
for f in "$DIR"/[0-9][0-9]-*.md; do
  [[ -e "$f" ]] || continue
  base="$(basename "$f")"
  n="$((10#${base%%-*}))"   # strip leading zeros safely
  (( n > max )) && max=$n
done
next=$(printf "%02d" $((max + 1)))

# --- slugify the title: lowercase, spaces/underscores -> hyphens, drop other punct ---
slug="$(printf '%s' "$TITLE" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"

OUT="$DIR/$next-$slug.md"

if [[ -e "$OUT" ]]; then
  echo "Error: $OUT already exists. Pick a different title." >&2
  exit 1
fi

# --- copy template and inject the H1 title, stripping the leading HTML comment ---
{
  # Replace the placeholder H1 with the real title, drop the leading HTML comment
  # block, and skip any blank lines before the first real content.
  awk -v title="# $TITLE" '
    /^<!--/ { in_comment=1 }
    in_comment { if (/-->/) in_comment=0; next }
    !started && /^[[:space:]]*$/ { next }      # skip leading blank lines
    /^# PLACEHOLDER TITLE/ { print title; started=1; next }
    { started=1; print }
  ' "$TEMPLATE"
} > "$OUT"

echo "Created $FOLDER/$next-$slug.md"
echo
echo "Next steps:"
echo "  1. Write it (see CONTRIBUTING.md for the style guide)."
echo "  2. Add a row for it to 01-mastery-curriculum.md."
echo "  3. git checkout -b add/$slug && git add \"$OUT\" && commit + open a PR."
