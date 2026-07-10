#!/usr/bin/env bash
# Best-effort copy of heavy gitignored build artifacts (_build, shinylive
# render cache, _freeze) from a "donor" checkout into this one, so a fresh
# worktree/workspace doesn't have to pay for a full render + shinylive
# render-cache warmup before it has something to preview.
#
# Donor resolution order (first candidate that exists and isn't this dir):
#   1. $AI_SETUP_DONOR
#   2. $CONDUCTOR_ROOT_PATH
#   3. the main git worktree (git worktree list --porcelain | head -1)
#
# Never fails the caller: every copy is best-effort, and this script always
# exits 0. Does NOT seed .venv -- see the `ai-setup` Makefile target comment
# (a copied venv's scripts carry absolute paths back to the donor, so it
# would lie about its own location; uv rebuilds a venv in ~1 min anyway).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

resolve_donor() {
	local main_worktree
	main_worktree="$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2; exit}')"
	for candidate in "${AI_SETUP_DONOR:-}" "${CONDUCTOR_ROOT_PATH:-}" "$main_worktree"; do
		if [ -n "$candidate" ] && [ -d "$candidate" ]; then
			candidate="$(cd "$candidate" && pwd)"
			if [ "$candidate" != "$ROOT" ]; then
				echo "$candidate"
				return 0
			fi
		fi
	done
	return 1
}

DONOR="$(resolve_donor || true)"
if [ -z "${DONOR:-}" ]; then
	echo "🔹 seed-caches: no usable donor found (checked \$AI_SETUP_DONOR, \$CONDUCTOR_ROOT_PATH, main worktree), skipping"
	exit 0
fi
echo "🔵 seed-caches: donor = $DONOR"

copy_artifact() {
	local rel="$1"
	local dest="$ROOT/$rel"
	local src="$DONOR/$rel"
	if [ -e "$dest" ]; then
		echo "🔹 seed-caches: $rel already present here, skipping"
		return 0
	fi
	if [ ! -e "$src" ]; then
		echo "🔹 seed-caches: donor has no $rel, skipping"
		return 0
	fi
	mkdir -p "$(dirname "$dest")"
	if cp -Rc "$src" "$dest" 2>/dev/null; then
		echo "✓ seed-caches: cloned $rel from donor (APFS clonefile)"
	elif cp -R "$src" "$dest" 2>/dev/null; then
		echo "✓ seed-caches: copied $rel from donor (clonefile unsupported, used cp -R)"
	else
		echo "🔹 seed-caches: failed to copy $rel from donor, skipping"
		rm -rf "$dest"
	fi
}

copy_artifact "_build"
copy_artifact ".quarto/shinylive-cache"
copy_artifact "_freeze"

exit 0
