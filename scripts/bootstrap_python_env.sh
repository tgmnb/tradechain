#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

LOCAL_PYTHON_USER="$ROOT_DIR/.local/python-user"
GET_PIP_PATH="$ROOT_DIR/.local/downloads/get-pip.py"
PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
LOCAL_SITE_PACKAGES="$LOCAL_PYTHON_USER/lib/python${PYTHON_VERSION}/site-packages"

mkdir -p "$ROOT_DIR/.local/downloads" "$LOCAL_PYTHON_USER"

if [[ ! -f "$GET_PIP_PATH" ]]; then
  python3 -c "import urllib.request; data=urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py').read(); open('$GET_PIP_PATH','wb').write(data)"
fi

if [[ ! -d "$LOCAL_SITE_PACKAGES/pip" ]]; then
  PYTHONUSERBASE="$LOCAL_PYTHON_USER" python3 "$GET_PIP_PATH" --user --break-system-packages
fi

if [[ ! -x "$LOCAL_PYTHON_USER/bin/virtualenv" ]]; then
  PYTHONPATH="$LOCAL_SITE_PACKAGES" python3 -m pip install --target "$LOCAL_SITE_PACKAGES" virtualenv
fi

PYTHONPATH="$LOCAL_SITE_PACKAGES" python3 -m virtualenv "$ROOT_DIR/.venv"
