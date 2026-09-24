#!/usr/bin/env bash
# Install (or remove) the weekday session audit as a launchd agent.
#
# launchd rather than a cloud routine: the audit reads ~/.claude/projects, which only exists on this
# machine. launchd rather than CronCreate: that is session-only and dies with the session.
set -euo pipefail
cd "$(dirname "$0")/.."

LABEL="dev.marcjimenez.session-audit"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOGDIR="${XDG_CONFIG_HOME:-$HOME/.config}/marcjimenez/audits"

if [ "${1:-install}" = "uninstall" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "removed $LABEL"
  exit 0
fi

# Resolve the binary now and bake it in. launchd gets no interactive shell, so relying on PATH means
# the job runs whatever ~/.profile happens to resolve, which is not the build you just validated.
CLAUDE="$(command -v claude || true)"
[ -n "$CLAUDE" ] || { echo "claude CLI not on PATH" >&2; exit 1; }
echo "using $CLAUDE ($("$CLAUDE" --version 2>/dev/null | head -1))"
mkdir -p "$LOGDIR" "$(dirname "$PLIST")"
sed -e "s|__REPO__|$PWD|g" -e "s|__LOGDIR__|$LOGDIR|g" -e "s|__CLAUDE__|$CLAUDE|g" \
  scripts/session-audit.launchd.plist > "$PLIST"
plutil -lint "$PLIST" >/dev/null

# bootout first so a re-install replaces rather than stacks
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "installed $LABEL — weekdays 10:07, logs in $LOGDIR"
echo "run now:  launchctl kickstart -p gui/$(id -u)/$LABEL"
echo "remove:   ./scripts/install-session-audit.sh uninstall"
