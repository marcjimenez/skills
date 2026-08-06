#!/usr/bin/env bash
# Structural guard for the marcjimenez plugin. Run from the repo root: bash scripts/validate.sh
# Checks manifests parse, every SKILL.md has valid frontmatter, every /marcjimenez:<name> reference
# resolves to a real skill, and no stale references remain. Exit non-zero on any failure.
# Each skill is a folder one level under skills/ (skills/<name>/SKILL.md).
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
note() { printf '  %s\n' "$1"; }
err()  { printf 'FAIL: %s\n' "$1"; fail=1; }

echo "== JSON manifests parse =="
for j in .claude-plugin/marketplace.json plugins/marcjimenez/.claude-plugin/plugin.json; do
  python3 -m json.tool "$j" >/dev/null && note "ok $j" || err "invalid JSON: $j"
done

echo "== SKILL.md frontmatter (name + description) =="
count=0
while IFS= read -r f; do
  count=$((count+1))
  head -1 "$f" | grep -qx -- '---' || { err "no frontmatter: $f"; continue; }
  fm="$(awk 'NR>1{if($0=="---")exit; print}' "$f")"
  printf '%s\n' "$fm" | grep -q '^name:' || err "missing name: $f"
  printf '%s\n' "$fm" | grep -q '^description:' || err "missing description: $f"
done < <(find plugins/marcjimenez/skills -name SKILL.md)
note "$count skills"
[ "$count" -eq 11 ] || err "expected 11 skills, found $count"

echo "== /marcjimenez:<name> references resolve =="
for name in $(grep -rho '/marcjimenez:[a-z][a-z-]*' plugins/marcjimenez | sed 's|/marcjimenez:||' | sort -u); do
  if find plugins/marcjimenez/skills -type d -name "$name" | grep -q .; then note "ok /marcjimenez:$name"; else err "dangling reference /marcjimenez:$name"; fi
done

echo "== no stale references =="
if grep -rniE 'marc-workflow|langgraph-agent|joinkudos' plugins/marcjimenez README.md .claude-plugin >/dev/null; then
  err "stale reference (marc-workflow/langgraph-agent/joinkudos) present"
else
  note "clean"
fi

echo
[ "$fail" -eq 0 ] && echo "VALIDATE OK" || { echo "VALIDATE FAILED"; exit 1; }
