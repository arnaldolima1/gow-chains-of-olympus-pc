# What is missing

What this port does not have yet, most likely to matter first. Measured on macOS 26, Apple M4, Vulkan through MoltenVK, and on a Moto g84 (Android 15, Adreno 619).

## Where the port is

1. The installer accepts the European disc (`UCES-00842`) and decrypts `EBOOT.BIN` (tag `0xC0CB167C`, the older header layout with a 0x90-byte key table). The disc keeps no PGD data.
2. The recompiled code (`scripts/generate.sh`: 193 units; only 19 `break` traps are left to the interpreter) plays at 60 frames a second and full speed on the Mac, the frame loop held to one flip a vblank as in Sparta (`frame_vblanks`, `flips_wait_for_vblank`).
3. A new game starts and its opening was played by hand on the Mac and on the phone, graphics looking right. On the phone the heaviest fights run at 96–98% speed: see [PERFORMANCE.md](PERFORMANCE.md).
4. START skips the pre-rendered movies (`start_skips_movies`).
5. At boot the game looks for its profile save, `UCES00842PROFILE00`.

**Not verified:** most of the game past its opening; that nothing reads the shown picture back with the CPU (`frame_writeback = false`, as in Sparta: the pause screen would show garbage); Windows.

## Known gaps

### Imports with no implementation

Two of the game's 199 imports (`OLYMPUS_LIST_STUBS=1`), the same two as Ghost of Sparta's: `LoadExecForUser::sceKernelLoadExec` and one of `sceAtrac3plus`. Neither has been seen called yet.

### Downloadable content

None is known for this game.
