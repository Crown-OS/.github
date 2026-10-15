# Crown-OS/.github

Organization-level GitHub configuration for [CrownOS](https://github.com/Crown-OS).

Three things live here:

1. **Reusable workflows** that every CrownOS repository calls, and the
   `prepare-workspace` action they share, so the native dependency list, the
   sibling checkout and the lint policy exist in one place instead of sixteen.
2. **Default community health files** — `CODE_OF_CONDUCT.md`, `SECURITY.md`, the
   issue templates and the pull-request template. GitHub applies these to any
   repo in the org that does not have its own, so they are maintained once
   instead of sixteen times.
3. **`profile/README.md`** — the organisation's public landing page.

## Reusable workflows

`crownOs` deliberately does not use these: it carries its own `ci.yml`, because
with one caller a reusable workflow costs a second checkout, a second place to
look when CI breaks and `@main` version skew, for no reuse at all. `docs.yml` was
retired with the documentation repository -- the docs live in `crownOs` now and
its own CI checks their links.

| Workflow | Used by | Does |
|---|---|---|
| `rust.yml` | every component in crownos-iso's `components.txt` · crownos-iso | rustfmt (blocking) · build · clippy (advisory) · test |
| `web.yml` | crownos-website | bun install · biome check · next build |
| `android.yml` | crowncrate-android | assembleDebug · unit tests · APK artifact |
| `shell.yml` | — | shellcheck |
| `release.yml` | Rust binaries, on `v*` tags | release build · tarball · draft GitHub Release |
| `arch-package.yml` | every component, on `v*` tags | release build · `.pkg.tar.zst` · published GitHub Release for crownos-iso |
| `publish.yml` | Rust crates, on `v*` tags | tag/manifest check · dry run · `cargo publish` |

### Calling one

Each repo carries a thin `.github/workflows/ci.yml`:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    uses: Crown-OS/.github/.github/workflows/rust.yml@main
```

The doubled `.github/.github/` is not a typo — the first is this repository's
name, the second is the directory inside it.

### Inputs that matter

**`packages`** — extra pacman packages on top of the base Wayland/Vulkan/font/
D-Bus set in `prepare-workspace`. Every job runs in an `archlinux` container,
so CI builds against the same libraries the ISO ships, and `arch-package.yml`
can read runtime dependencies straight off `pacman -Qqo`.

**`dbus`** — set `true` for crownotify only. Its tests register real well-known
names on the session bus, so they run under `dbus-run-session` with
`--test-threads=1`.

**`test`** — set `false` for a repository whose tests need a live compositor.

### Sibling path dependencies

Components depend on each other by `path = "../crownos-config"`.
`prepare-workspace` checks the caller out into a directory named after itself,
then scans every `Cargo.toml` and clones each missing sibling flat next to it
from `Crown-OS/<dir>` — repeatedly, so siblings of siblings resolve too. A
directory whose repository is named differently is mapped through `aliases`
(`llts-protocol=lls-protocol` by default).

## Lint policy

**rustfmt blocks. Clippy does not.**

Roughly 15,000 lines of Rust have never been linted, so turning on
`-D warnings` today would make every repository red for reasons unrelated to
the change being reviewed. Clippy runs on every PR and writes its findings to
the job summary; it just does not fail the build yet.

When the backlog is cleared, the change is one line in `rust.yml` — remove the
`continue-on-error` and add `-- -D warnings`. Nothing in the individual repos
needs touching.

## Does a fresh clone build?

Yes — and it no longer needs a script to prove it. `check-fresh-clone.py` existed
because every crate declared a dependency version that was not published, so the
tree only built on one machine, behind an overlay nobody else had. The workspace
merge removed the condition: `cargo build` in a clean clone of `crownOs` resolves
by path and needs no setup at all.

What replaced it is `cargo tree --workspace --duplicates`, one line in that
repo's CI, which surfaces the version skew `crown-versions.toml` used to police
with 212 lines of Python.

## Build status

Every Rust crate in the organisation compiles. Verified on the pinned 1.88.0
toolchain with the dependency overlay in place: all eleven pass
`cargo check --all-targets`. `crowncrate-linux` and `lls-protocol`, previously
documented here as red on purpose, both build; `crowndictator` needed OpenSSL
development headers added to `crownos-setup`'s dependency manifest, because
`ort` pulls `ureq` with native-tls.

None of that is visible on GitHub yet — the fixes are local and unpushed.

## What is deliberately not here

- **No deploy for crownos-website.** It has no `output: "export"` in
  `next.config.ts`, so a static Pages deploy cannot work without a source
  change. CI builds it; deployment is a separate decision.
- **No automatic crates.io publish.** `publish.yml` exists and nine repos call
  it on a `v*` tag, but cross-repo ordering is manual and deliberately so: tier 0
  (crownos-config, crownshell, crownuikit, crownlauncher, crowncrate-linux,
  lls-*) must be live before tier 1 (crownbar, crowndock, crownotify,
  crowndictator, crownpositor-config), which must be live before crownpositor.
  Note that publishing crownshell 0.3.0 freezes the misspelled `predule` module
  as permanent public API — 0.3.0 is a breaking bump and therefore the last
  cheap moment to add a `prelude` alias and deprecate the typo.
- **No ISO nightly.** The profile is still unmodified upstream Arch, so a
  nightly would publish a generic rescue image. `crownos-iso/build.sh` builds it
  on demand from any distribution.
- **No CODEOWNERS.** Review is a human reading the diff; there is no branch
  protection to enforce ownership.
- **No dependabot — but the reason it was blocked has gone.** The old objections
  were git dependencies with no `rev` (there are none left) and
  `crown-versions.toml` fighting per-repo bumps (it is deleted). With one
  workspace and one `[workspace.dependencies]` table, a bump is a single edit in
  a single file, which is exactly the shape dependabot handles well. Worth
  enabling on `crownOs`; it is simply not done yet.

## See also

- [Contribution guide](https://github.com/Crown-OS/crownOs/blob/main/CONTRIBUTING.md)
- [CrownOS documentation](https://github.com/Crown-OS/crownOs/tree/main/docs)


---

## Where dependency versions live now

In `crownOs`'s root `Cargo.toml`, as `[workspace.dependencies]`. Cargo enforces
what a linter used to: there is one declaration and nine `workspace = true`
references, so two members cannot disagree.

`crown-versions.toml`, `check-versions.py` and `sync-versions.py` are deleted.
They were a good answer to a problem that no longer exists — the same dependency
declared four different ways across four repos — and keeping them would have
meant maintaining a second, weaker copy of what the workspace already
guarantees.

## Native dependencies

Build dependencies are pacman packages: the base set lives in
`.github/actions/prepare-workspace/action.yml`, per-repo extras in each caller's
`packages:` input. `release.yml` and `publish.yml` still run on Ubuntu with apt.
