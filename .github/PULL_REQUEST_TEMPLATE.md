<!--
  Title: Conventional Commits, e.g. `fix(dock): keep the icon highlight after a drag`.
  The PR is squash-merged and the title becomes the commit on main.
  Guide: https://github.com/Crown-OS/.github/blob/main/CONTRIBUTING.md
-->

## Closes

<!-- Closes #<n> | Fixes #<n>. Small, self-explanatory changes may skip this. -->

Closes #

## Summary

<!-- What does this change do, and why? -->

## Testing

<!-- CI runs fmt, build, clippy and tests. Describe what CI cannot check:
     which compositor you ran under, what you did, what you observed. -->

## Cross-repo changes

<!-- Does this need, or break, another Crown-OS repository? Link the companion
     PRs so a maintainer can merge them in dependency order. Otherwise "None". -->

None

## Checklist

- [ ] The PR title follows Conventional Commits
- [ ] Every commit is signed off (`git commit -s`, DCO)
- [ ] `cargo fmt` and `cargo test` pass locally, and no new clippy warnings are added
- [ ] Tests are added or updated for changed behaviour
- [ ] Docs are updated if behaviour, config, env vars or keybindings changed
- [ ] CodeRabbit comments are addressed or answered
