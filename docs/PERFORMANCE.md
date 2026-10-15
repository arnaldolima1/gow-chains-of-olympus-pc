# Performance work

Where the frame time goes, what was done, what was tried and dropped, and what is next. Written to be picked up by whoever continues: a person or a coding agent. Ghost of Sparta's [docs/PERFORMANCE.md](https://github.com/arnaldolima1/gow-ghost-of-sparta-pc/blob/main/docs/PERFORMANCE.md) is the longer history of the same work on the same engine and framework; read it too. Its numbers and lessons apply here.

The target device is a **Moto g84 5G** (Snapdragon 695: two Cortex-A78 at 2.2 GHz, six Cortex-A55; Adreno 619; Android 15), the slowest machine the port should run well on. On an Apple M4 the game runs at full speed with time to spare; the Mac is where correctness is checked, the phone is where speed is measured.

Framework changes go into PortableKit (`portablekit/`, the fork's `sparta` branch, which both Olympus and Sparta track), so whatever is gained here is gained in Sparta too once its submodule is moved.

## Start here (state on 2026-10-15)

- **Released: 0.1.0** (macOS and Android), the first release, with the recompiled code and START skipping movies.
- **On the phone at ×2,** most of the game runs at 60 fps and 100% speed. The heaviest fights dip to **96–98%** with frame skip on (49–55 fps shown). The game thread is the limit, not the GPU: `guest` ~9.3 ms + `render` ~7.3 ms ≈ 16.6 ms against 16.7 ms a frame, GPU ~10 ms.
- **Done this round** (PortableKit `73a6d93`, on `sparta`): display lists read through a host window, and triangle indices written in place. About 0.6 ms a frame on the phone. See [done](#done).
- **Tried and dropped:** a cache of decoded vertices (branch `decode-cache-experiment`), and GPU vertex decode (`OLYMPUS_GPU_DECODE=1`). See [tried and dropped](#tried-and-dropped).
- **Next, recommended:** the "cold" slow paths in the recompiler ([next, item 1](#1-recompiler-cold-slow-paths-recommended)): the game's own code is about half the game thread, and this is the smallest change there with a measured static gain. Then NEON skinning ([item 2](#2-neon-skinning)).
- **Sparta has not been rebuilt with `73a6d93` yet.** Move its submodule to the `sparta` branch head, build, and check it on the phone.
- The owner runs the long builds unless they say otherwise. Here they are short: regenerating takes about 80 s, the macOS dev build about 2 minutes with ccache, the Android build about 8 minutes.

## How to measure

Always the same stretch of play, measured before anything is changed.

There is no scripted benchmark for this game yet (Sparta has `scripts/bench_android.sh`, which plays the boat fight through scripted input). Until there is, the player goes to a heavy fight by hand and the profile is taken from the Mac:

```bash
# A debuggable build. It is signed with a test key, so it does not install over the release app.
cd <a path without spaces>/olympus          # FFmpeg's configure fails on a path with spaces: see below
DEBUGGABLE=1 scripts/build_android.sh && scripts/run_android.sh

# The [perf] line once a second, in the app's log, through env.txt in its storage:
printf 'OLYMPUS_PERF=log\n' > /tmp/env.txt
adb push /tmp/env.txt /data/local/tmp/olympus-env.txt
adb shell "run-as io.olympus sh -c 'cp /data/local/tmp/olympus-env.txt files/env.txt'"
# (the app reads it when it starts)

adb shell setprop security.perf_harden 0       # once per boot, for simpleperf
# With the game in a heavy fight:
adb shell "simpleperf record --app io.olympus -g --duration 15 -f 2000 -o /data/local/tmp/p.data"
adb pull /data/local/tmp/p.data build/bench/NAME.data
adb shell run-as io.olympus cat files/OlympusNative.log | grep '\[perf\] fps' | tail -16

tools/perf/profile_report.py cycles   build/bench/NAME.data
tools/perf/profile_report.py children build/bench/NAME.data "GeState::draw_primitive"
tools/perf/profile_report.py lines    build/bench/NAME.data "VulkanRenderer::submit("
```

- `profile_report.py` reads symbols from `build/android/native/bin/libmain.so`: report before building anything else.
- On the `[perf]` line, `guest` is the game thread outside display lists (recompiled code, HLE, kernel), `render` the game thread inside display lists, `wait` time it waits, `gpu` GPU time a frame.
- **Two fights are never the same.** Compare **absolute cycles of the functions a change touched**, never totals or percentages: one run had 20% more vertex decoding than the run before simply because more was on screen.
- **Paths with spaces.** FFmpeg's `configure`, which the Android and release builds run, fails when the checkout's path has a space in it. Build through a symlink without spaces (the scripts keep the path they were started from).

## Where the time goes

A heavy fight, ×2, frame skip on, after `73a6d93`. The game thread, 15 s:

| Part | Gcycles in 15 s | Share |
| --- | --- | --- |
| Recompiled game code (`recomp_unit_*` itself) | ~14.2–14.8 | ~49% |
| Display lists (`GeState::execute`) | ~12.2–13.2 | ~43% |
| ↳ `draw_primitive` (decode, batching, submit) | ~8.3–9.1 | |
| ↳ `VulkanRenderer::submit` | ~5.0–5.3 | |
| ↳ `decode_vertices` | ~2.4–2.7 | |
| ↳ block transfers (`memmove` from the transfer sink) | ~0.4 | work the PSP really asks for |
| Presents | ~1.1 | |

- **The game's code has no hot spot.** Time is spread over dozens of units, the hottest (0003) at under 4% of the thread. Calls to the slow paths of guest memory access are rare (`aot_store8_slow` 0.01%). What would make it faster is better code from the recompiler everywhere, not one fix.
- **Vertex decoding is mostly skinning:** `decode_run<3,1,3>` (float weights, skinned characters) costs about twice `decode_run<0,1,3>` (unskinned level geometry).
- **`submit`'s own lines:** the hottest are the texture source lookup (framebuffer extract and descriptor, `texture_descriptor`), the pass and target bookkeeping (`snapshot_guest_words`), and the vertex conversion loop into the mapped buffer (`to_gpu`).

## Done

**Display lists read through a host window** (PortableKit `73a6d93`). `GeState::execute` read every command word through `GuestMemory::contains` and an out-of-line `load32`. It now keeps a host pointer to a 1 KiB window of the list and looks it up again only when the list leaves it. `OLYMPUS_NO_LIST_WINDOW=1` restores the old reads. Phone: `load32` + `contains` 0.83 → **0.17** Gcycles in 15 s.

**Triangle indices written in place** (same commit). `triangle_indices` wrote through `push_back`, and a batched prim's indices were copied again one by one to add the batch's base. `append_triangle_indices` sizes the output once and writes the indices with the base added; an unindexed prim with all its vertices decoded skips the lookup and the clamp. Phone: `triangle_indices` + `send_draw`'s own code 1.39 → **0.85** Gcycles, in a run with more draws. Tests: `portablekit_render_tests`, with a new test for the appended form.

**This game's profile** (`host/olympus_profile.cpp`): `frame_writeback = false` as in Sparta (not yet checked that nothing in this game reads its picture back with the CPU: if the pause screen shows garbage, that is the first suspect), and `start_skips_movies = true`.

## Tried and dropped

**A cache of decoded vertices** (PortableKit branch `decode-cache-experiment`). Unskinned draws whose guest bytes are unchanged copy their decoded vertices from the last time instead of decoding again; bytes compared whole, so a hit is exact. Correct (`OLYMPUS_CHECK_DECODE_CACHE=1`: 600 000 hits, none different) and 63% of lookups hit, but it **does not pay**: the unskinned decode it targets barely moved (`decode_run<0,1,3>` 1.15% → 1.19% of the thread), and the lookup (`std::unordered_map`), compare and copy cost about what they saved. The hits are small, cheap draws; the expensive decode is skinning, which it cannot reuse. Only a cache that keeps vertices **on the GPU** (no decode, no copy into the batch, no conversion, no upload) could pay, and that is a much larger renderer change: batching, frame interpolation and draw replay all assume vertices pass through the CPU every frame.

**GPU vertex decode** (`OLYMPUS_GPU_DECODE=1`, already in PortableKit). Skinning moves to the vertex shader, but raw draws are not batched, so `render` went **up** (7 → 10–12 ms), and the GPU became the limit (~17 ms a frame): **76–83%** speed. The same as Sparta found. Not worth more on this phone.

**From Sparta, still true here:** a render thread does not pay on this phone (memory bound: handing the vertices over costs what it saves); guest registers held in locals spill to the stack while every guest access has a call in its slow path.

## Next

### 1. Recompiler: cold slow paths (recommended)

From Sparta's [item 4 experiment](https://github.com/arnaldolima1/gow-ghost-of-sparta-pc/blob/main/docs/PERFORMANCE.md#4-guest-registers-in-locals-experiment-done): move the slow paths of `AotFastView` (`slow_->load32(...)` and the like) out of line into `[[gnu::noinline, gnu::cold, clang::preserve_most]]` helpers, so a call on the slow path no longer clobbers the caller's registers. Static counts for arm64: −6% instructions, −9% stack traffic in unit 0172 of Sparta; never measured running. Steps:

1. Make it in PortableKit, behind a switch (generator option or compile definition), on a branch.
2. Check compile time and memory of the heaviest units with the NDK clang and Apple clang; `psprecomp_tests`.
3. Regenerate and rebuild this game (`scripts/generate.sh`, `scripts/build.sh`), run it on the Mac, captures.
4. Android build; phone profile in a heavy fight; compare **`recomp_unit_` cycles** with the numbers above.
5. If it pays, the same for Sparta, and then think about item 4b in Sparta's document (guest memory accesses with no call at all), which is what lets guest registers live in host registers.

### 2. NEON skinning

`decode_run<3,1,3>` is about 2.4% of the game thread: per vertex, a weighted sum of up to eight 3×4 bone matrices, done in scalar code. Blending the matrices with NEON (or blending the vertex once per bone with four-wide multiplies) should roughly halve it: about 0.3 ms a frame at most. Small and low risk; keep the scalar path behind a switch and compare with `OLYMPUS_CHECK_DECODE`.

### 3. Smaller per-draw costs in `submit`

From Sparta's item 5, still open: `texture_descriptor`'s per-list memo is a `std::map` keyed by seven fields; `find_framebuffer_texture` could reject a texture in main RAM before looking at any target; `multiply(view, world)` per draw could wait for either matrix to change. A few tenths of a millisecond each.

### Ideas, not measured

- **`vector<Vertex>` zeroed before it is filled.** `decode_vertices` resizes its output, which zero-fills 40 bytes a vertex that the decoder then overwrites (`__append`, 0.65% of the thread). Avoiding it means a vector that does not value-initialise, touching every user of `DrawCall::vertices`.
- **Loading stutter.** Single seconds with `guest` at ~37 ms, or the GPU at 15–24 ms with many frames skipped, appear when an area loads or something is drawn for the first time (new pipelines). Not investigated; check whether they repeat on a second visit (the pipeline cache is kept in `pipeline_cache.bin`).

## Lessons

- **Measure, then change.** Two of the three changes tried this round were plausible and did not pay.
- **Absolute cycles of the touched functions,** not totals: fights differ from run to run.
- On this phone the cost to watch is **memory traffic**: a cache that copies instead of computing saves little.
