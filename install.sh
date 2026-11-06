#!/bin/sh
# Install the uk-law skill for Codex and other agents that read ~/.agents/skills (and ~/.codex/skills).
# Usage: curl -fsSL https://raw.githubusercontent.com/flaviohtavares/uk-law-tools/main/install.sh | sh
set -eu
REPO="https://github.com/flaviohtavares/uk-law-tools"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --quiet --depth 1 "$REPO" "$TMP/tools"
for DEST in "$HOME/.agents/skills" "${CODEX_HOME:-$HOME/.codex}/skills"; do
  mkdir -p "$DEST"
  rm -rf "$DEST/uk-law"
  cp -R "$TMP/tools/plugins/uk-law/skills/uk-law" "$DEST/uk-law"
  echo "Installed the uk-law skill in $DEST/uk-law"
done
echo "Restart your agent, then ask it about UK law."
