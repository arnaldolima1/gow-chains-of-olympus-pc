# Where work stopped

2026-10-15. What is missing in the game is in [MISSING.md](MISSING.md); this page is where to pick the work up.

## State

- **0.1.0** is published for macOS (Apple Silicon) and Android, built on a Mac: recompiled (193 units, 19 guest break traps), 60 fps on an Apple M4, START skips movies.
- **Windows:** never built yet. [WINDOWS.md](WINDOWS.md) has the steps, the ones Sparta's Windows build used.
- **PortableKit:** pinned at `73a6d93` on the fork's `sparta` branch.
- The read-mes follow Sparta's layout in English and Brazilian Portuguese.

## Next

1. **First Windows build** (WINDOWS.md), then a Windows release with `scripts\release_windows.ps1` and `scripts\publish_release_windows.ps1`. Update WINDOWS.md with what actually happens.
2. **Fights with many enemies** were felt to slow down, as in Sparta: measure with `OLYMPUS_PERF=log` (guest against render milliseconds) before guessing.
3. The rest of the game past its opening; the pause screen with `frame_writeback = false` (MISSING.md).

## Decisions waiting

- The fork's `konoha` branch (Naruto's port) holds seven framework fixes ahead of `sparta`: the GE colour mask, depth tests in through mode, block transfers into drawn framebuffers, the alpha test's never/always, and more. They reach this port when `konoha` is merged into `sparta` (after a full Sparta check) and the submodule moves.

## Development layout

Beside the checkout: `../work` is the private `sparta-work` repository on its `olympus` branch (the Android release key). Its `keys/release.env` names the keystore by a macOS path: fix it before building an APK on another machine.
