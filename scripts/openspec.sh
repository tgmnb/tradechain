#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$ROOT_DIR/.local/npm/bin:$ROOT_DIR/.local/node-v20.20.1-linux-x64/bin:$PATH"

exec openspec "$@"
