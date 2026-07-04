#!/usr/bin/env bash
# Regenerate the CAEN HV devman bridge packages from spec.json.
#
# - Server package -> generated_bridge/caenhv-devman-server (this repo)
# - Client package -> the caenhv-devman-client repo checkout given by
#   CLIENT_REPO (default: sibling checkout used as caenhv-client submodule)
#
# devman-gen only regenerates src/; pyproject/README/LICENSE/workflows in
# both destinations are repo-owned and preserved.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEVMAN_GEN="${DEVMAN_GEN:-$HERE/../devman-gen}"
CLIENT_REPO="${CLIENT_REPO:-$HERE/../caenhv-client/caenhv-devman-client}"

SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

PYTHONPATH="$DEVMAN_GEN/src" python3 -m devman_gen.cli generate \
  --spec "$HERE/spec.json" \
  --output "$SCRATCH" \
  --package-name caenhv-devman

rsync -a --delete "$SCRATCH/caenhv-devman-server/src/" "$HERE/generated_bridge/caenhv-devman-server/src/"
rsync -a --delete "$SCRATCH/caenhv-devman-client/src/" "$CLIENT_REPO/src/"

echo "regenerated: server -> $HERE/generated_bridge/caenhv-devman-server"
echo "regenerated: client -> $CLIENT_REPO"
