#!/usr/bin/env bash
# Compute a stable content key for everything the `quartodoc` Makefile target
# depends on, so that target can skip its (slow) body when nothing relevant
# has changed since the last successful run.
#
# Inputs hashed:
#   - the py-shiny submodule's checked-out commit
#   - _renderer.py (custom quartodoc renderer)
#   - py-shiny/docs/_quartodoc-*.yml (quartodoc config)
#   - requirements.txt (pins quartodoc/griffe/etc versions)
#
# Prints the key to stdout. Callers compare it against `.quartodoc-stamp`.
set -euo pipefail
cd "$(dirname "$0")/.."

submodule_commit=$(git -C py-shiny rev-parse HEAD 2>/dev/null || echo "no-submodule")
renderer_hash=$(shasum -a 256 _renderer.py | awk '{print $1}')
quartodoc_yml_hash=$(cat py-shiny/docs/_quartodoc-*.yml 2>/dev/null | shasum -a 256 | awk '{print $1}')
requirements_hash=$(shasum -a 256 requirements.txt | awk '{print $1}')

printf '%s\n%s\n%s\n%s\n' \
	"$submodule_commit" "$renderer_hash" "$quartodoc_yml_hash" "$requirements_hash" \
	| shasum -a 256 | awk '{print $1}'
