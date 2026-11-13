#!/usr/bin/env bash
# Commits LICENSE-MIT and LICENSE-APACHE to every Crown-OS repository that has
# no license yet. Dry run by default; pass --apply to commit.
#
#   scripts/add-dual-license.sh [--apply] [repo ...]
set -euo pipefail

readonly ORG=Crown-OS
LICENSE_DIR="$(dirname "$0")/../licenses"
readonly LICENSE_DIR
readonly COMMIT_MESSAGE="chore: license under MIT OR Apache-2.0 [skip ci]"

apply=false
repos=()
for arg in "$@"; do
  case $arg in
    --apply) apply=true ;;
    *) repos+=("$arg") ;;
  esac
done

if [ ${#repos[@]} -eq 0 ]; then
  mapfile -t repos < <(gh repo list "$ORG" --limit 200 --no-archived --source \
    --json name,defaultBranchRef,licenseInfo \
    --jq '.[] | select(.defaultBranchRef != null and .licenseInfo == null) | .name')
fi

file_exists() {
  gh api "repos/$ORG/$1/contents/$2" --silent 2>/dev/null
}

commit_license_file() {
  local repo=$1 name=$2
  if file_exists "$repo" "$name"; then
    echo "  $name already present"
  elif $apply; then
    base64 -w0 "$LICENSE_DIR/$name" |
      jq -Rn --arg message "$COMMIT_MESSAGE" '{message: $message, content: input}' |
      gh api -X PUT "repos/$ORG/$repo/contents/$name" --input - --silent
    echo "  committed $name"
  else
    echo "  would commit $name"
  fi
}

$apply || echo "Dry run. Pass --apply to commit to ${#repos[@]} repositories."
for repo in "${repos[@]}"; do
  echo "== $repo"
  commit_license_file "$repo" LICENSE-MIT
  commit_license_file "$repo" LICENSE-APACHE
done
