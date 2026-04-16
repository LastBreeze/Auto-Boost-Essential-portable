# Auto-Boost-Essential Portable

A fully automated AV1 encoding workflow for Windows. **One double-click** takes your raw `.mkv` files, encodes them to AV1 with consistent visual quality, and remuxes everything back together with the original audio and subtitles. No command line, no manual setup, no merging — just drop, click, relax.

Built on Trix's **SVT-AV1-Essential** with **Auto-Boost-Essential**. A great place to start with AV1 on Windows.

---

## ✨ Features

- **Zero configuration** — fully portable, no installation required
- **Visual-metric driven encoding** for consistent perceptual quality across scenes
- **Auto-renaming** — safely prepares your files for processing
- **Auto-muxing** — recombines the new AV1 video with your original audio and subtitle tracks
- **Resume support** — interruptions are handled gracefully (re-run the `.bat` to continue)
- **Automatic bt709/bt601 color space detection** to prevent color shifts
- **znver2-optimized binary** by default, with an x86-64-v3 fallback for older CPUs

---

## 🚀 Quick Start

1. **Drop** your `.mkv` files into the `Auto-Boost-Essential` `videos-input` folder.
2. **Double-click** the `.bat` file that matches your content (see below).
3. **Relax.** Encoded files appear when finished.

---

## 📁 Which `.bat` should I use?

Pick based on content type and desired quality. **CRF 30 ("medium") is the recommended starting point** — adjust from there if needed.

### Anime
| File | Quality |
|------|---------|
| `batch-anime-30-medium.bat` | Balanced |
| `batch-anime-25-high.bat` | High quality, larger files |
| `batch-anime-20-higher.bat` | Higher quality, even larger files |
| `batch-anime-18-higher-slower.bat` | Highest fidelity, slower encoding |

### Live Action / Movies / TV
| File | Quality |
|------|---------|
| `batch-liveaction-30-medium.bat` | Balanced |
| `batch-liveaction-25-high.bat` | High quality, larger files |
| `batch-liveaction-20-higher.bat` | Higher quality, even larger files |

### Sports
| File | Quality |
|------|---------|
| `batch-sports-35-medium.bat` | Optimized for fast motion efficiency |

### CRF Quality Guide
- **18–20** — Higher quality, slowest encoding, largest files
- **25** — High quality, good balance
- **30** — Medium quality, faster encoding, smaller files *(recommended starting point)*
- **35** — Lower quality, fastest encoding, smallest files

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

---

## ⚡ Choosing the fastest SVT-AV1 binary

`znver2` is the default for `SvtAv1EncApp.exe`. If your modern Intel or AMD CPU supports it, this will be the fastest option. An `x86-64-v3` build is provided for compatibility — swap the `.exe` manually from `tools\SVT-AV1-Essential builds\` if needed.

---

## 🔁 Resume Support

If the Auto-Boost script is interrupted, just re-run the `.bat` and it will pick up where it left off.

Note: SVT-AV1-Essential itself does **not** support resuming. If the *final pass* is interrupted mid-encode, that file will restart from the beginning of the final pass — but everything else resumes cleanly.

---

## 🧩 Related Projects

- **Auto-Boost-Av1an** — Supports `zones.txt` and any quarterstep-CRF SVT-AV1 fork.
- **Auto-Boost Av1an for Linux** — Linux port by `! D7M 𒉭`.

---

## 🛠 Troubleshooting

**"Unsupported compression method" during extraction** → Update your 7-Zip to the latest version.

**Encode crashes or refuses to start on a specific file** → Run `extras\lossless-intermediary.bat` to create a clean intermediate, then encode from that.
