# Crown-OS/.github

Organization-level GitHub configuration for [CrownOS](https://github.com/Crown-OS).

> **This repository does not exist on GitHub yet.** Every caller workflow in
> every repo references `Crown-OS/.github/.github/workflows/*.yml@main`, so
> until it is pushed, CI fails everywhere with "workflow was not found" — which
> is why no CrownOS repo has ever run CI. Creating it is the first thing that
> has to happen.

Four things live here:

1. **Reusable workflows** that every CrownOS repository calls, so the native
   dependency list and the lint policy exist in one place instead of sixteen.
2. **`crown-versions.toml`** — the single declaration of every dependency used by
   more than one repo, enforced by `scripts/check-versions.py` in CI.
3. **Default community health files** — `CODE_OF_CONDUCT.md`, `SECURITY.md`, the
   issue templates and the pull-request template. GitHub applies these to any
   repo in the org that does not have its own, so they are maintained once
   instead of sixteen times.
4. **`profile/README.md`** — the organisation's public landing page.

## Reusable workflows

| Workflow | Used by | Does |
|---|---|---|
| `rust.yml` | the 11 Rust repos | rustfmt (blocking) · build · clippy (advisory) · test |
| `web.yml` | crownos-website | bun install · biome check · next build |
| `android.yml` | crowncrate-android | assembleDebug · unit tests · APK artifact |
| `docs.yml` | crownos-documentations | relative-link check · status-marker consistency |
| `shell.yml` | crownos-iso | shellcheck |
| `release.yml` | Rust binaries, on `v*` tags | release build · tarball · draft GitHub Release |
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

**`siblings`** — the reason this is not a one-liner, though not for the reason
it originally was. No crate declares a path dependency any more; they declare
`crownshell = "0.3"` and `crownos-config = "0.2"`. **Neither version is on
crates.io** (crownshell is published at 0.1.0 and 0.2.0 only), so a plain
checkout cannot resolve at all. `siblings` clones the named repos next to the
caller and writes a `[patch.crates-io]` overlay above both — the same overlay
`crownos-setup`'s `bootstrap.sh --dev` writes on a contributor's machine.

It is scaffolding for the pre-publish period. Once crownshell 0.3.0 and
crownos-config 0.2.0 are on crates.io, every `siblings:` line can be deleted and
CI resolves the way a stranger's clone does.

Five repos need it: crownbar, crowndock, crownotify (crownshell), crowndictator
(both) and crownpositor (crownos-config).

```yaml
    uses: Crown-OS/.github/.github/workflows/rust.yml@main
    with:
      siblings: crownshell crownos-config
```

**`packages`** — extra apt packages on top of the base Wayland/Vulkan/font/D-Bus
set. The compositor needs `libdrm-dev libinput-dev libseat-dev libudev-dev
libpixman-1-dev`; crowndictator needs `libasound2-dev libevdev-dev`;
crowncrate-linux needs `libgtk-4-dev`.

**`dbus`** — set `true` for crownotify only. Its tests register real well-known
names on the session bus, so they run under `dbus-run-session` with
`--test-threads=1`.

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

`scripts/check-fresh-clone.py` resolves a repo's dependencies in a temporary
directory where no `[patch.crates-io]` overlay can reach it — which is what a
stranger's `git clone` gets. `rust.yml` runs it on every push and writes the
result to the job summary.

It exists because the failure it detects already happened: every crate declared
a dependency version that was not published, everything still built for the
maintainer because of a patch overlay above the checkouts, and nothing caught it
because nothing ever built outside that directory.

It is advisory today — five repos cannot resolve, for a reason no contributor
can fix — and passing `--allow` lists them. Remove `continue-on-error` and the
allowlist once tier 0 is published; that is the whole point of having it.

```bash
python3 scripts/check-fresh-clone.py --all ~/src/crownos
python3 scripts/check-versions.py --lint-spec      # audit crown-versions.toml itself
```

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
- **No dependabot.** The reason previously given — "several crates pin git
  dependencies with no `rev`" — no longer holds; there are no git dependencies
  left. The current reason is that `crown-versions.toml` owns shared versions,
  so per-repo bumps would fight it. Raise versions there and propagate with
  `scripts/sync-versions.py`.

## See also

- [Contribution guide](https://github.com/Crown-OS/crownos-documentations/blob/main/CONTRIBUTING.md)
- [CrownOS documentation](https://github.com/Crown-OS/crownos-documentations)


---

## crown-versions.toml

The one place CrownOS declares dependency versions. `scripts/check-versions.py`
runs as a blocking job in `rust.yml` and fails any repo that disagrees.

It exists because the same dependency was declared four different ways across the
tree — `anyhow` as `"1"`, `"1.0.100"`, `"1.0.102"` and `"1.0.104"` — and because
`crowndictator` carried a hand-written comment claiming its Wayland pins were
"versions matched to crownshell", alignment that nothing enforced.

```bash
# check every repo below a directory
python3 scripts/check-versions.py --all ~/src/crownos

# check one repo (what CI does)
python3 scripts/check-versions.py ~/src/crownos/crownbar

# rewrite manifests to match; only the version field is touched
python3 scripts/sync-versions.py --all ~/src/crownos --dry-run
python3 scripts/sync-versions.py --all ~/src/crownos
```

It is deliberately narrow — the CrownOS crates plus dependencies two or more
repos declare. Deliberate differences go in `[exceptions]`, keyed
`"<repo>.<dep>"`, so a real decision is distinguishable from an accident. A
linter that tries to own every version becomes the thing everyone disables.

## Native dependencies are not defined here

The apt list in `rust.yml` is **generated** from
[`crownos-setup/deps.toml`](https://github.com/Crown-OS/crownos-setup), which is
also the source for the bootstrap script and the documentation tables. Editing it
here will drift. Edit `deps.toml`, run `scripts/gen.py`, and copy
`generated/ci-packages.txt` across.

That drift was real: this workflow used to install `libfontconfig-1-dev`, which
exists on neither Debian nor Ubuntu, and omitted `xwayland` for `crownpositor`
despite the compositor enabling smithay's `xwayland` feature.
