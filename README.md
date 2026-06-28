# Auto-Boost-Essential Portable

A fully automated AV1 encoding workflow for Windows. **One double-click** takes your raw `.mkv` files, encodes them to AV1 with consistent visual quality, and remuxes everything back together with the original audio and subtitles. No command line, no manual setup, no merging — just drop, click, relax.

Built on Trix's **SVT-AV1-Essential** with **Auto-Boost-Essential**. A great place to start with AV1 on Windows.

---

## ✨ Features

- **Zero configuration** — fully portable, no installation required
- **Visual-metric driven encoding** for consistent perceptual quality across scenes
- **Interactive Batch Builder** — answer a few simple questions and it writes a custom encode script for you
- **Auto-renaming** — safely prepares your files for processing
- **Auto-muxing** — recombines the new AV1 video with your original audio and subtitle tracks
- **Resume support** — interruptions are handled gracefully (re-run the `.bat` to continue)
- **Photon-noise** added to the final pass to mitigate banding
- **Automatic bt709/bt601 color space detection** to prevent color shifts
- **Dark-scene quality boost** to reduce banding and detail loss in shadows and night scenes
- **Choice of quality metric** — SSIMULACRA 2 (accurate) or XPSNR (fast)
- **AVX-512 support** for CPUs that have it
- **znver2-optimized binary** by default, with an x86-64-v3 fallback for older CPUs

---

## 🚀 Quick Start

1. **Drop** your video files (`.mkv`, `.mp4`, `.m2ts`) into the `videos-input` folder.
2. **Double-click** a `.bat` file (see below). The easiest path is the included `batch-30-medium-XPSNR-START-HERE.bat`.
3. **Relax.** Encoded files appear in the `videos-output` folder when finished.

> 💡 New to this? Just run `batch-30-medium-XPSNR-START-HERE.bat`. It uses sensible defaults and is the perfect first encode.

---

## 🛠 Make Your Own Encode Script — `bat-builder.bat`

Instead of hunting for the right preset, you can now **build your own** custom encode script by answering a few plain-English questions.

**Double-click `bat-builder.bat`** and it will walk you through 5 quick steps:

1. **Quality Level (CRF)** — the balance between file size and visual quality. Lower number = better quality + bigger file. Start at **30** if unsure.
2. **Fidelity / Detail Preservation** — how hard the encoder works to keep fine detail (textures, grain, fine lines). Start at **0**; bump it up if textures look soft.
3. **Dark Scene Quality Boost** — adds extra quality to dark/night scenes to fight banding and blocking in shadows. Start at **20**.
4. **Quality Metric** — **SSIMULACRA 2** (slower, more accurate) or **XPSNR** (faster, less accurate).
5. **AVX-512 Support** — only say Yes if you're sure your CPU supports AVX-512. If unsure, leave it off.

When you're done, it saves a ready-to-run `.bat` file (e.g. `batbuilder-ssimulacra2-d0-crf30.bat`) right in the main folder. Just double-click it to encode.

> Want to tweak it further by hand? Open any generated `.bat` in Notepad++ and edit the settings at the top.

---

## 📊 CRF Quality Guide

CRF controls the trade-off between quality and file size:

| CRF | Quality | Notes |
|-----|---------|-------|
| 20 | Higher | Very high quality, slowest, largest files |
| 25 | High | Great quality, good balance |
| 30 | Medium | Good quality, faster, smaller files *(recommended starting point)* |
| 35 | Low | Lower quality, fast, small files |
| 40 | Lower | Lowest quality, fastest, smallest files |

**CRF 30 is the recommended starting point.** Adjust from there based on how the result looks.

---

## 🧰 Extras

Located in the `extras\` folder:

- **`lossless-intermediary.bat`** — Converts a problematic source into a clean lossless intermediate file for stable encoding. Place your `.mkv` in the `tools` folder before running.
- **`encode-opus.audio.bat`** — Extracts audio from your MKVs and re-encodes to high-quality, space-saving Opus, using all CPU threads.
- **`photon-noise-test.bat`** — Preview how various photon-noise levels (2, 4, 6, 8, 10) will look in your AV1 encode.
- **`forced-aspect-remux.bat`** — Copies forced aspect ratio metadata from the source to the AV1 output after encoding.
- **`compare.bat`** — Auto-generates a [slow.pics](https://slow.pics) link to compare two MKV files. Uses oxipng lossless compression to speed up uploads.
- **`compress-folders.bat`** — On Windows 10/11, NTFS-compresses the VapourSynth and tools folders, saving roughly 60% disk space.

The `prefilter\` folder contains scripts for sources that need denoising, debanding, or downscaling.

The `audio-encoding\` folder contains scripts for compressing and re-encoding audio tracks.

---

## 🔁 Resume Support

If the Auto-Boost script is interrupted, just re-run the `.bat` and it will pick up where it left off.

Note: SVT-AV1-Essential itself does **not** support resuming. If the *final pass* is interrupted mid-encode, that file will restart from the beginning of the final pass — but everything else resumes cleanly.

---

## 📝 Script Modifications

`Auto-Boost-Essential.py` is kept **near-vanilla**. The only modification is the addition of `photon-noise` on the final pass to mitigate banding. No further changes are planned.

---

## 🧩 Related Projects

- [**Auto-Boost-Av1an**](https://github.com/LastBreeze/Auto-Boost-Av1an-portable) — Supports `zones.txt` and any quarterstep-CRF SVT-AV1 fork.
- [**Auto-Boost Av1an for Linux**](https://github.com/abdalrahmanx9/Auto-Boost-Av1an-Linux) — Linux port by `! D7M 𒉭`.

---

## 🛠 Troubleshooting

**"Unsupported compression method" during extraction** → Update your 7-Zip to the latest version.

**Encode crashes or refuses to start on a specific file** → Run `extras\lossless-intermediary.bat` to create a clean intermediate, then encode from that.
