#!/usr/bin/env bash
# Org installer (Linux/macOS): install the log-tfidf-reducer wrapper (`logreduce`)
# and register its skill into all AI agents (Claude Code, Cursor, Codex, .agents).
#
# Uses `uv` (preferred) to install the package as an isolated tool, then runs
# `logreduce-skill --install` to drop SKILL.md into each agent's skills dir.
#
# The `logreduce` command auto-downloads the correct binary for this OS on first
# use, so nothing else is needed.
#
# SOURCE controls where the package comes from. For org rollout, pass the Git URL
# (the package lives in the `log_tfidf_reducer` subdirectory):
#
#   ./install.sh --source "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
#
# With no --source, it installs from this local folder (handy for testing).
#
# Usage:
#   ./install.sh [--source SRC] [--agents all|claude,cursor,...] [--scope user|project]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE=""
AGENTS="all"
SCOPE="user"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="$2"; shift 2 ;;
    --agents) AGENTS="$2"; shift 2 ;;
    --scope)  SCOPE="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$SOURCE" ]] && SOURCE="$SCRIPT_DIR"

have() { command -v "$1" >/dev/null 2>&1; }

echo "Installing log-tfidf-reducer from: $SOURCE"

if ! have uv && ! have pip && ! have pip3; then
  echo "uv not found; installing uv (https://astral.sh/uv)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  export PATH="$HOME/.local/bin:$PATH"
fi

if have uv; then
  # --native-tls uses the system cert store (needed behind TLS-inspecting proxies).
  uv tool install --native-tls --force "$SOURCE"
  uv tool update-shell >/dev/null 2>&1 || true
elif have pip; then
  echo "uv not available; falling back to pip install --user..."
  pip install --user --upgrade "$SOURCE"
elif have pip3; then
  pip3 install --user --upgrade "$SOURCE"
else
  echo "ERROR: could not install (no uv/pip available)." >&2
  exit 1
fi

echo "Registering the skill with agents: $AGENTS (scope=$SCOPE)..."
if have logreduce-skill; then
  logreduce-skill --install --agents "$AGENTS" --scope "$SCOPE"
else
  echo "(logreduce-skill not on PATH yet; invoking via python module)"
  python3 -m log_tfidf_reducer.installer --install --agents "$AGENTS" --scope "$SCOPE"
fi

echo ""
echo "Done. Open a new shell so PATH refreshes, then run: logreduce --version"
