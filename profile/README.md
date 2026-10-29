# **CrownOS** - Not yet another Linux Distro

CrownOS is an **Agentic Linux desktop OS** written in Rust with advanced _computer use_ capabilities. We are redesigning everything above the kernel like compositor, shell, bar, dock, notifications, settings and a multi device bridge for the agentic era tuned for automation, customization and polished user experience out of the box unlike any other linux distros. 


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
                                      crownos-ipc
                         (Custom IPC communication protocol)

           crownui                                       llts-protocol
         (UI Toolkit)                                 (Network Protocol)
              │                                                │
              ▼                           ┌────────────────────┼────────────────────┐
        crownos-settings                  │                    │                    │
          (System Apps)                   ▼                    ▼                    ▼
              │                      crowncrate-linux   crowncrate-chrome  crowncrate-android
              ▼
         crownos-config
   (Global system config manager)

```

| Repository | Description |
| --- | --- |
| [`crownos-iso`](https://github.com/Crown-OS/crownos-iso) | Linux installation image |
| [`crowndesktop`](https://github.com/Crown-OS/crowndesktop) | Desktop environment |
| [`crownpositor`](https://github.com/Crown-OS/crownpositor) | Wayland compositor |
| [`crownbar`](https://github.com/Crown-OS/crownbar) | Desktop status bar |
| [`crowndock`](https://github.com/Crown-OS/crowndock) | Application dock |
| [`crownotify`](https://github.com/Crown-OS/crownotify) | Notification system |
| [`crownlauncher`](https://github.com/Crown-OS/crownlauncher) | Application launcher |
| [`crowndictator`](https://github.com/Crown-OS/crowndictator) | Voice dictation for CrownOS |
| [`crownui`](https://github.com/Crown-OS/crownui) | App framework for Wayland |
| [`crownos-settings`](https://github.com/Crown-OS/crownos-settings) | System settings application |
| [`lls-protocol`](https://github.com/Crown-OS/lls-protocol) | Network transmission protocol for CrownConnect |
| [`crownconnect-linux`](https://github.com/Crown-OS/crownconnect-linux) | Linux client for the CrownConnect bridge |
| [`crowncrate-chrome`](https://github.com/Crown-OS/crowncrate-chrome) | Browser plugin bridge for CrownConnect |
| [`crownconnect-android`](https://github.com/Crown-OS/crownconnect-android) | Android client for CrownConnect |
