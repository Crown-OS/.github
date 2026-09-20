# **CrownOS** - Not yet another Linux Distro

It is a **Agentic Linux desktop** written from scratch in **Rust**.
We are reinventing everything like 
compositor, shell, bar, dock, notifications, settings and a phone bridge
for high performance, fluid animations and polished user experience.

## Start here

| You are… | Go to |
|---|---|
| curious what this is | [crownOs](https://github.com/Crown-OS/crownOs) — the desktop, and how it fits together |
| setting up any Linux machine | [crownOs-setup](https://github.com/Crown-OS/crownOs-setup) — one script, any distribution |
| wanting to build and run it | [Build it](https://github.com/Crown-OS/crownOs#build-it) |
| wanting to contribute | [CONTRIBUTING.md](https://github.com/Crown-OS/crownOs/blob/main/CONTRIBUTING.md) |
| wanting to test and report bugs | [What is verified](https://github.com/Crown-OS/crownOs#verified-not-assumed), then open an issue on [crownOs](https://github.com/Crown-OS/crownOs/issues) |

## Dependency Graph

```
                      crownpositor           the session that spawns the rest
                    (the Wayland server)
                            │
              ┌─────────────┼──────────────┬──────────────┐
           crownbar     crowndock      crownotify    crowndictator
              └─────────────┴──────────────┴──────────────┘
                            │  all built on
                       crownshell            layer-shell + Vello framework

     crownos-config   Global config manager, read live by all system apps
     crownuikit       UI framework to build beautiful high perfomance apps for wayland 
     crowncrate-*     phone bridge: Linux daemon, Android and Chrome clients
     lls-protocol     low-latency screen-streaming protocol
     crownos-iso      the installation image
     crownos-setup    native dependencies and toolchain, on any distribution

     everything above the crowncrate line lives in one repo: Crown-OS/crownOs
```

## Repositories

| Repo | What it is |
|---|---|
| [crownOs](https://github.com/Crown-OS/crownOs) | **The desktop.** Nine crates in one workspace: compositor, shell framework, bar, dock, notifications, dictation, config schema, widget kit — and the documentation |
| [crownOs-setup](https://github.com/Crown-OS/crownOs-setup) | Native dependencies and toolchain, on any distribution |
| [crownos-iso](https://github.com/Crown-OS/crownos-iso) · [crownos-website](https://github.com/Crown-OS/crownos-website) | Installation image; website |
| [crowncrate-linux](https://github.com/Crown-OS/crowncrate-linux) · [crowncrate-android](https://github.com/Crown-OS/crowncrate-android) | Phone bridge |
| [lls-protocol](https://github.com/Crown-OS/lls-protocol) | Low-latency streaming protocol |
| [crownlauncher](https://github.com/Crown-OS/crownlauncher) | Application launcher |

The per-crate repositories — crownshell, crownos-config, crownbar, crowndock,
crownotify, crowndictator, crownuikit, crownpositor — are **archived**. Their
URLs still resolve and their history is intact; the code moved into `crownOs` so
that a change crossing two crates is one commit, one review and one CI run.
Crate names on crates.io are unchanged.

## Licence

MIT, except [crownos-iso](https://github.com/Crown-OS/crownos-iso), which is
GPL-3.0-or-later because it derives from Arch Linux's archiso profile.
