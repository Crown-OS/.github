#!/usr/bin/env bash
# Applies the CrownOS contribution rules to every repository in the org.
# Dry run by default; pass --apply to change anything.
#
#   scripts/enforce-contribution-rules.sh [--apply] [--require-dco] [repo ...]
#
# GitHub Free has no org rulesets, so each repository gets its own.
set -euo pipefail

readonly ORG=Crown-OS
readonly SHARED_RUST_CHECK="ci / fmt / build / clippy / test"
readonly GITHUB_ACTIONS_APP_ID=15368
declare -rA OWN_CI_CHECK=(
  [crownui]="fmt / clippy / test / bundle"
)

apply=false
require_dco=false
repos=()
for arg in "$@"; do
  case $arg in
    --apply) apply=true ;;
    --require-dco) require_dco=true ;;
    *) repos+=("$arg") ;;
  esac
done

if [ ${#repos[@]} -eq 0 ]; then
  mapfile -t repos < <(gh repo list "$ORG" --limit 200 --no-archived --source \
    --json name,defaultBranchRef --jq '.[] | select(.defaultBranchRef != null) | .name')
fi

run() {
  if $apply; then "$@" >/dev/null; else printf '  would run: %s\n' "$*"; fi
}

uses_shared_rust_ci() {
  local workflows
  workflows=$(gh api "repos/$ORG/$1/contents/.github/workflows/ci.yml" \
    -H 'Accept: application/vnd.github.raw' 2>/dev/null || true)
  [[ $workflows == *'Crown-OS/.github/.github/workflows/rust.yml'* ]]
}

required_checks_json() {
  local checks=() ci_check=${OWN_CI_CHECK[$1]:-}
  [ -z "$ci_check" ] && uses_shared_rust_ci "$1" && ci_check=$SHARED_RUST_CHECK
  [ -n "$ci_check" ] && checks+=("{\"context\":\"$ci_check\",\"integration_id\":$GITHUB_ACTIONS_APP_ID}")
  $require_dco && checks+=('{"context":"DCO"}')
  local IFS=,
  printf '[%s]' "${checks[*]}"
}

main_branch_ruleset() {
  local status_checks=$1
  jq -n --argjson checks "$status_checks" '{
    name: "main",
    target: "branch",
    enforcement: "active",
    conditions: { ref_name: { include: ["~DEFAULT_BRANCH"], exclude: [] } },
    bypass_actors: [ { actor_type: "OrganizationAdmin", actor_id: 1, bypass_mode: "always" } ],
    rules: ([
      { type: "deletion" },
      { type: "non_fast_forward" },
      { type: "pull_request", parameters: {
          required_approving_review_count: 1,
          dismiss_stale_reviews_on_push: true,
          require_code_owner_review: false,
          require_last_push_approval: true,
          required_review_thread_resolution: true,
          allowed_merge_methods: ["squash"] } }
    ] + (if ($checks | length) > 0 then [ { type: "required_status_checks", parameters: {
          strict_required_status_checks_policy: false,
          required_status_checks: $checks } } ] else [] end))
  }'
}

release_tag_ruleset() {
  jq -n '{
    name: "release tags",
    target: "tag",
    enforcement: "active",
    conditions: { ref_name: { include: ["refs/tags/v*"], exclude: [] } },
    bypass_actors: [ { actor_type: "OrganizationAdmin", actor_id: 1, bypass_mode: "always" } ],
    rules: [ { type: "creation" }, { type: "update" }, { type: "deletion" } ]
  }'
}

upsert_ruleset() {
  local repo=$1 body=$2 name existing
  name=$(jq -r .name <<<"$body")
  existing=$(gh api "repos/$ORG/$repo/rulesets" --jq ".[] | select(.name == \"$name\") | .id" 2>/dev/null || true)
  if $apply; then
    if [ -n "$existing" ]; then
      gh api -X PUT "repos/$ORG/$repo/rulesets/$existing" --input - <<<"$body" >/dev/null
    else
      gh api -X POST "repos/$ORG/$repo/rulesets" --input - <<<"$body" >/dev/null
    fi
  else
    printf '  would %s ruleset "%s":\n' "${existing:+update}${existing:-create}" "$name"
    jq -c .rules <<<"$body" | sed 's/^/    /'
  fi
}

ensure_labels() {
  local repo=$1
  while IFS='|' read -r name color description; do
    run gh label create "$name" -R "$ORG/$repo" --color "$color" --description "$description" --force
  done <<'LABELS'
bug|d73a4a|Something does not work as expected
enhancement|a2eeef|New feature or capability
performance|fbca04|Faster or lighter, no behaviour change
breaking-change|b60205|Changes a public API, protocol or config format
documentation|0075ca|Docs only
ci|ededed|Workflows, packaging or build scripts
dependencies|0366d6|Dependency updates
question|d876e3|Asks how something works
good first issue|7057ff|Scoped and mentored; a good start
help wanted|008672|Maintainers would welcome help
needs-triage|fef2c0|Not yet reviewed by a maintainer
slop|5c5c5c|Low-effort or machine-generated; will be closed
LABELS
}

configure_repository() {
  local repo=$1
  run gh api -X PATCH "repos/$ORG/$repo" \
    -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
    -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
    -F delete_branch_on_merge=true -F allow_update_branch=true -F allow_auto_merge=true \
    -F web_commit_signoff_required=true
  run gh api -X PUT "repos/$ORG/$repo/private-vulnerability-reporting"
}

$apply || echo "Dry run. Pass --apply to change ${#repos[@]} repositories."
for repo in "${repos[@]}"; do
  echo "== $repo"
  configure_repository "$repo"
  ensure_labels "$repo"
  upsert_ruleset "$repo" "$(main_branch_ruleset "$(required_checks_json "$repo")")"
  upsert_ruleset "$repo" "$(release_tag_ruleset)"
done
