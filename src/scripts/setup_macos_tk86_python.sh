#!/usr/bin/env bash
# Build a Python 3.12 that links Tk 8.6 (via Homebrew tcl-tk@8) so tkinterdnd2 / tkdnd works.
#
# Prerequisites: Xcode CLT (`xcode-select -p`).
#
# Recommended (no compiling): install python.org macOS installer for 3.12.x — it bundles Tcl/Tk 8.6
# and avoids Homebrew Tk 9 + python-tk@3.12.
#
# This script alternative: brew + pyenv from source (~5–15 min first run).
#
# Usage (from repo root or anywhere):
#   bash src/scripts/setup_macos_tk86_python.sh
# Optional env:
#   PYTHON_VERSION=3.12.10              # patch level pinned for reproducibility
#   FORCE_PYENV_REINSTALL=1             # pyenv uninstall -f before install
#   SKIP_PIP_INSTALL=1                  # only build pyenv Python, no venv/pip

set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script is for macOS only." >&2
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required: https://brew.sh" >&2
  exit 1
fi

SRC_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SRC_ROOT"

PYTHON_VERSION="${PYTHON_VERSION:-3.12.10}"
TCL_BASE="$(brew --prefix tcl-tk@8)"

echo "==> Ensuring Homebrew dependencies (tcl-tk@8, pyenv, build deps)…"
brew list tcl-tk@8 >/dev/null 2>&1 || brew install tcl-tk@8
brew list pyenv >/dev/null 2>&1 || brew install pyenv
for _pkg in openssl@3 readline sqlite xz zlib; do
  brew list "$_pkg" >/dev/null 2>&1 || brew install "$_pkg"
done

export PATH="${HOME}/.pyenv/shims:${HOME}/.pyenv/bin:${PATH}"
if command -v pyenv >/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi

OPENSSL_PREFIX="$(brew --prefix openssl@3)"
export LDFLAGS="-L${TCL_BASE}/lib -L${OPENSSL_PREFIX}/lib -L$(brew --prefix readline)/lib -L$(brew --prefix sqlite)/lib -L$(brew --prefix zlib)/lib -L$(brew --prefix xz)/lib ${LDFLAGS:-}"
export CPPFLAGS="-I${OPENSSL_PREFIX}/include -I$(brew --prefix readline)/include -I$(brew --prefix sqlite)/include -I$(brew --prefix zlib)/include -I$(brew --prefix xz)/include ${CPPFLAGS:-}"
export PKG_CONFIG_PATH="${OPENSSL_PREFIX}/lib/pkgconfig:${TCL_BASE}/lib/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"

export PYTHON_CONFIGURE_OPTS="${PYTHON_CONFIGURE_OPTS:-} --with-tcltk-includes=-I${TCL_BASE}/include/tcl-tk --with-tcltk-libs=-L${TCL_BASE}/lib -ltcl8.6 -ltk8.6"

if [[ "${FORCE_PYENV_REINSTALL:-0}" == "1" ]]; then
  echo "==> Force reinstall: pyenv uninstall -f ${PYTHON_VERSION}"
  pyenv uninstall -f "${PYTHON_VERSION}" 2>/dev/null || true
fi

if pyenv versions --bare | grep -qx "${PYTHON_VERSION}"; then
  echo "==> pyenv already has ${PYTHON_VERSION}; skip build (set FORCE_PYENV_REINSTALL=1 to rebuild)."
else
  echo "==> pyenv install ${PYTHON_VERSION} (links _tkinter to tcl-tk@8 / Tk 8.6)…"
  pyenv install -s "${PYTHON_VERSION}"
fi

pyenv local "${PYTHON_VERSION}"

TK_PATCHLEVEL="$(python -c "import tkinter as tk; print(tk.Tcl().call('info', 'patchlevel'))")"
echo "==> Tk patchlevel from this interpreter: ${TK_PATCHLEVEL}"
if [[ "${TK_PATCHLEVEL}" == 9.* ]]; then
  echo "Still on Tk 9.x — wrong _tkinter. Rebuild with FORCE_PYENV_REINSTALL=1 or check PYTHON_CONFIGURE_OPTS." >&2
  exit 1
fi

if [[ "${SKIP_PIP_INSTALL:-0}" == "1" ]]; then
  echo "==> SKIP_PIP_INSTALL=1 — done."
  exit 0
fi

REQ="${REQ:-${SRC_ROOT}/requirements_spotless_film.txt}"
if [[ ! -f "$REQ" ]]; then
  echo "Missing requirements file: $REQ" >&2
  exit 1
fi

echo "==> Recreating .venv in ${SRC_ROOT}…"
python -m venv "${SRC_ROOT}/.venv" --clear
"${SRC_ROOT}/.venv/bin/python" -m pip install -U pip wheel
"${SRC_ROOT}/.venv/bin/pip" install -r "$REQ"

echo "==> Verify venv Tk patchlevel…"
"${SRC_ROOT}/.venv/bin/python" -c "import tkinter as tk; print('Tk', tk.Tcl().call('info', 'patchlevel'))"

echo "==> Done. Use: ${SRC_ROOT}/.venv/bin/python -m PyInstaller …"
