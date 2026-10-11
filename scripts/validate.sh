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
[ "$count" -eq 17 ] || err "expected 17 skills, found $count"

echo "== /marcjimenez:<name> references resolve =="
for name in $(grep -rho '/marcjimenez:[a-z][a-z-]*' plugins/marcjimenez | sed 's|/marcjimenez:||' | sort -u); do
  if find plugins/marcjimenez/skills -type d -name "$name" | grep -q .; then note "ok /marcjimenez:$name"; else err "dangling reference /marcjimenez:$name"; fi
done

echo "== invocation posture: frontmatter matches README =="
# Frontmatter only. The string also appears in writing-for-agents' prose, which is not a flag.
flagged=""
for f in plugins/marcjimenez/skills/*/SKILL.md; do
  if awk 'NR>1{if($0=="---")exit; print}' "$f" | grep -q '^disable-model-invocation: *true'; then
    flagged="$flagged$(basename "$(dirname "$f")")
"
  fi
done
flagged="$(printf '%s' "$flagged" | sort)"
documented="$(grep -oE '`/?marcjimenez:[a-z][a-z-]*` *\| *user only' README.md 2>/dev/null \
  | sed -E 's|.*marcjimenez:([a-z-]*)`.*|\1|' | sort || true)"
if [ "$flagged" = "$documented" ]; then
  note "ok user-only: $(printf '%s' "$flagged" | tr '\n' ' ')"
else
  err "README 'user only' rows disagree with disable-model-invocation frontmatter"
  note "flagged:    $(printf '%s' "$flagged" | tr '\n' ' ')"
  note "documented: $(printf '%s' "$documented" | tr '\n' ' ')"
fi

echo "== no skill invokes a user-only skill =="
# The Skill tool refuses to launch a skill carrying disable-model-invocation, so a handoff
# into one always errors at runtime. Guard the pairing, not just the flag.
handoffs="$(grep -rhoiE 'nvoke `/marcjimenez:[a-z][a-z-]*`' plugins/marcjimenez/skills 2>/dev/null \
  | sed -E 's|.*marcjimenez:([a-z-]*)`|\1|' | sort -u || true)"
for name in $handoffs; do
  if printf '%s\n' "$flagged" | grep -qx "$name"; then
    err "handoff into user-only skill: /marcjimenez:$name (the Skill tool will refuse it)"
  else
    note "ok handoff -> /marcjimenez:$name"
  fi
done

echo "== REPO_KEY derivation is identical everywhere =="
# It is copy-pasted into every skill that needs it because a skill cannot import. It drifted into two
# variants once, which is how every Conductor workspace ended up with its own cache. Compare the WHOLE
# block from its first comment line, and pin the count so a block deleted outright cannot pass.
key_expected=11
key_block() {
  awk '/^# One cache per REPOSITORY/{p=1} p{print} p&&/not in a git repository/{exit}' "$1"
}
key_files="$(grep -rl '^# One cache per REPOSITORY' plugins | sort)"
key_count="$(printf '%s\n' "$key_files" | grep -c .)"
key_sums="$(for f in $key_files; do key_block "$f" | md5 -q 2>/dev/null || key_block "$f" | md5sum | cut -d" " -f1; done | sort -u)"
if [ "$key_count" -ne "$key_expected" ]; then
  err "expected $key_expected copies of the REPO_KEY block, found $key_count"
  note "a skill lost its copy, or a new one gained it — bump key_expected deliberately"
elif [ "$(printf '%s\n' "$key_sums" | grep -c .)" -ne 1 ]; then
  err "REPO_KEY derivation has drifted across $key_count files"
  for f in $key_files; do
    s="$(key_block "$f" | md5 -q 2>/dev/null || key_block "$f" | md5sum | cut -d" " -f1)"
    note "  $s  $f"
  done
else
  note "ok $key_count files, one block"
fi
grep -rn 'rev-parse --show-toplevel' plugins >/dev/null \
  && err "--show-toplevel returns the worktree, not the repo; use --git-common-dir" \
  || note "ok no --show-toplevel"

echo "== no stale references =="
if grep -rniE 'marc-workflow|langgraph-agent|joinkudos' plugins/marcjimenez README.md .claude-plugin >/dev/null; then
  err "stale reference (marc-workflow/langgraph-agent/joinkudos) present"
else
  note "clean"
fi

echo
[ "$fail" -eq 0 ] && echo "VALIDATE OK" || { echo "VALIDATE FAILED"; exit 1; }
