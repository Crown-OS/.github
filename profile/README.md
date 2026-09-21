# **CrownOS** - Not yet another Linux Distro

CrownOS is an **Agentic Linux desktop OS** written in **Rust**.
We are redesigning everything like 
compositor, shell, bar, dock, notifications, settings and a phone bridge
for high performance, fluid animations and polished user experience.

## Dependency Graph

```text
                                      crownos-iso
                               (Linux Installation Image)
                                           │
                                           ▼
                                     crowndesktop
                                (Desktop Environment)
                                           │
                                           ▼
                                      crownpositor
                                    (Wayland Server)
                                           │
             ┌──────────────┬──────────────┼──────────────┬──────────────┐
             │              │              │              │              │
             ▼              ▼              ▼              ▼              ▼
          crownbar       crowndock      crownotify    crownlauncher  crowndictator
             │              │              │              │              │
             └──────────────┴──────────────┼──────────────┴──────────────┘
                                           │
                                           ▼
                                       crownshell
                                   (Shell Framework)


          crownuikit                                     lls-protocol
         (UI Toolkit)                                 (Network Protocol)
              │                                                │
              ▼                           ┌────────────────────┼────────────────────┐
        crownsettings                     │                    │                    │
        (System Apps)                     ▼                    ▼                    ▼
                                  crowncrate-linux   crowncrate-chrome  crowncrate-android

```

| Repository | Description |
| --- | --- |
| [`crownos-iso`](https://github.com/Crown-OS/crownos-iso?utm_source=gemini) | Linux installation image |
| [`crowndesktop`](https://github.com/Crown-OS/crowndesktop?utm_source=gemini) | Desktop environment |
| [`crownpositor`](https://www.google.com/search?q=https://github.com/Crown-OS/crownpositor&utm_source=gemini) | Wayland compositor |
| [`crownbar`](https://www.google.com/search?q=https://github.com/Crown-OS/crownbar&utm_source=gemini) | Desktop status bar |
| [`crowndock`](https://www.google.com/search?q=https://github.com/Crown-OS/crowndock&utm_source=gemini) | Application dock |
| [`crownotify`](https://www.google.com/search?q=https://github.com/Crown-OS/crownotify&utm_source=gemini) | Notification system |
| [`crownlauncher`](https://github.com/Crown-OS/crownlauncher?utm_source=gemini) | Application launcher |
| [`crowndictator`](https://www.google.com/search?q=https://github.com/Crown-OS/crowndictator&utm_source=gemini) | System control and automation |
| [`crownshell`](https://github.com/Crown-OS/crownshell?utm_source=gemini) | Framework for building CrownOS shell components |
| [`crownuikit`](https://www.google.com/search?q=https://github.com/Crown-OS/crownuikit&utm_source=gemini) | UI toolkit for system applications |
| [`crownsettings`](https://www.google.com/search?q=https://github.com/Crown-OS/crownsettings&utm_source=gemini) | System settings application |
| [`lls-protocol`](https://github.com/Crown-OS/lls-protocol?utm_source=gemini) | Network transmission protocol for CrownConnect |
| [`crowncrate-linux`](https://github.com/Crown-OS/crowncrate-linux?utm_source=gemini) | Linux client for the CrownConnect bridge |
| [`crowncrate-chrome`](https://github.com/Crown-OS/crowncrate-chrome?utm_source=gemini) | Browser plugin bridge for CrownConnect |
| [`crowncrate-android`](https://github.com/Crown-OS/crowncrate-android?utm_source=gemini) | Phone client for the CrownConnect bridge |
