# What is missing

What this port does not have yet, most likely to matter first. Measured on macOS 26, Apple M4, Vulkan through MoltenVK.

## Where the port is

1. The installer accepts the European disc (`UCES-00842`) and decrypts `EBOOT.BIN` (tag `0xC0CB167C`, the older header layout with a 0x90-byte key table). The disc keeps no PGD data.
2. Under the interpreter (no recompiled code yet), the logos and the title menu play at 60 frames a second and full speed, the frame loop held to one flip a vblank as in Sparta (`frame_vblanks`, `flips_wait_for_vblank`).
3. At boot the game looks for its profile save, `UCES00842PROFILE00`.

**Not done yet:** the recompiled code (`scripts/generate.sh`, then `scripts/build.sh`); a new game; Android; Windows; a release.

## Known gaps

### Imports with no implementation

Two of the game's 199 imports (`OLYMPUS_LIST_STUBS=1`), the same two as Ghost of Sparta's: `LoadExecForUser::sceKernelLoadExec` and one of `sceAtrac3plus`. Neither has been seen called yet.

### Downloadable content

None is known for this game.
