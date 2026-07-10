#!/usr/bin/env bash
# Render the site in SHARDS parallel local jobs and merge the results into
# _build/. Mirrors the CI matrix build (scripts/ci-shard.py splits the
# render list, scripts/ci-merge.py stitches shard outputs back together) but
# fans out locally by cloning this worktree instead of using separate CI
# runners.
#
# Renders can't share one checkout: each shard rewrites _quarto.yml's render
# list in place (scripts/ci-shard.py), so each shard needs its own clone.
# Clones use APFS clonefile (cp -Rc) so they're near-instant and share disk
# blocks with the source until either copy is modified (copy-on-write).
#
# The clone's .venv is NOT recreated: its scripts/binaries carry absolute
# shebangs pointing back at THIS worktree's .venv, so they keep working from
# inside the clone.
#
# Env vars:
#   SHARDS       number of parallel shards (default 6)
#   QUARTO_PATH  path to the quarto binary to use
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SHARDS="${SHARDS:-6}"
QUARTO_PATH="${QUARTO_PATH:-quarto}"
QUARTO_PATH="${QUARTO_PATH/#\~/$HOME}" # expand a leading ~ (not done by the shell inside a quoted env var)
SCRATCH="${TMPDIR:-/tmp}/site-parallel-$$"

mkdir -p "$SCRATCH/out"
echo "🔵 site-parallel: $SHARDS shards, scratch dir $SCRATCH"

cleanup() {
	rm -rf "$SCRATCH"
}
trap cleanup EXIT

# Ensure shinylive web assets exist once up front (cached under
# ~/Library/Caches/shinylive, shared by every clone) so shards don't race
# each other downloading them.
. .venv/bin/activate
shinylive extension base-htmldeps --sw-dir . > /dev/null

pids=()
shards_list=()
for k in $(seq 1 "$SHARDS"); do
	clone="$SCRATCH/$k"
	echo "🔹 cloning worktree for shard $k/$SHARDS -> $clone"
	cp -Rc . "$clone"
	rm -rf "$clone/_build"
	(
		cd "$clone"
		python3 scripts/ci-shard.py --shard "$k" --count "$SHARDS"
		. .venv/bin/activate
		"$QUARTO_PATH" render --output-dir "$SCRATCH/out/$k"
	) > "$SCRATCH/shard-$k.log" 2>&1 &
	pids+=("$!")
	shards_list+=("$k")
done

fail=0
for i in "${!pids[@]}"; do
	pid="${pids[$i]}"
	k="${shards_list[$i]}"
	if wait "$pid"; then
		echo "✓ shard $k finished"
	else
		echo "❌ shard $k failed (log: $SCRATCH/shard-$k.log)"
		echo "----- tail of shard $k log -----"
		tail -80 "$SCRATCH/shard-$k.log" || true
		echo "---------------------------------"
		fail=1
	fi
done

if [ "$fail" -ne 0 ]; then
	echo "❌ site-parallel: one or more shards failed; aborting merge"
	exit 1
fi

echo "🔵 merging shard outputs into _build/"
python3 scripts/ci-merge.py --shards "$SCRATCH/out" --out _build

echo "✓ site-parallel complete"
