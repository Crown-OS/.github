# CrownOS

A Wayland-native Linux desktop written from scratch in Rust — compositor, shell,
bar, dock, notifications, settings and a phone bridge — plus the Arch-based
distribution that ships them.

> **CrownOS is early.** It builds and it runs, and it is not yet something you
> install on your only laptop. The
> [project status page](https://github.com/Crown-OS/crownos-documentations/blob/main/docs/00-overview/project-status.md)
> says exactly what works today, component by component. Nothing here describes
> software that does not exist.

## Start here

| You are… | Go to |
|---|---|
| curious what this is | [What is CrownOS](https://github.com/Crown-OS/crownos-documentations/blob/main/docs/00-overview/what-is-crownos.md) |
| setting up any Linux machine | [crownos-setup](https://github.com/Crown-OS/crownOs-setup) — one script, any distribution |
| wanting to build and run it | [Build and run](https://github.com/Crown-OS/crownos-documentations/blob/main/docs/10-getting-started/build-and-run.md) |
| wanting to contribute | [CONTRIBUTING.md](https://github.com/Crown-OS/crownos-documentations/blob/main/CONTRIBUTING.md) |
| wanting to test and report bugs | [Project status](https://github.com/Crown-OS/crownos-documentations/blob/main/docs/00-overview/project-status.md), then open an issue on the component's repo |

## The pieces

```
                      crownpositor          the Wayland compositor; it *is* the
                    (the Wayland server)    session, and spawns the rest
                            │
              ┌─────────────┼──────────────┬──────────────┐
           crownbar     crowndock      crownotify    crowndictator
              └─────────────┴──────────────┴──────────────┘
                            │  all built on
                       crownshell            layer-shell + Vello framework

     crownos-config   settings schema, read live by everything above
     crownuikit       widget kit (xilem) for the settings surfaces
     crowncrate-*     phone bridge: Linux daemon, Android and Chrome clients
     lls-protocol     low-latency screen-streaming protocol
     crownos-iso      the installation image
     crownos-setup    native dependencies and toolchain, on any distribution
```

## Repositories

| Repo | What it is |
|---|---|
| [crownpositor](https://github.com/Crown-OS/crownpositor) | Tiling Wayland compositor, built on Smithay |
| [crownshell](https://github.com/Crown-OS/crownshell) | Layer-shell + Vello framework every surface is built on |
| [crownos-config](https://github.com/Crown-OS/crownos-config) | Shared settings schema, live-reloading |
| [crownbar](https://github.com/Crown-OS/crownbar) · [crowndock](https://github.com/Crown-OS/crowndock) · [crownotify](https://github.com/Crown-OS/crownotify) | Bar, dock, notification daemon |
| [crowndictator](https://github.com/Crown-OS/crowndictator) | Push-to-talk voice dictation |
| [crownuikit](https://github.com/Crown-OS/crownuikit) · [crownlauncher](https://github.com/Crown-OS/crownlauncher) | Widget kit; application launcher |
| [crowncrate-linux](https://github.com/Crown-OS/crowncrate-linux) · [crowncrate-android](https://github.com/Crown-OS/crowncrate-android) | Phone bridge |
| [lls-protocol](https://github.com/Crown-OS/lls-protocol) | Low-latency streaming protocol |
| [crownos-iso](https://github.com/Crown-OS/crownos-iso) · [crownos-setup](https://github.com/Crown-OS/crownOs-setup) · [crownos-website](https://github.com/Crown-OS/crownos-website) | Image, machine setup, website |
| [crownos-documentations](https://github.com/Crown-OS/crownos-documentations) | Every doc, for every repo |

## Licence

MIT, except [crownos-iso](https://github.com/Crown-OS/crownos-iso), which is
GPL-3.0-or-later because it derives from Arch Linux's archiso profile.
