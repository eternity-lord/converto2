# ROUND 2 — completion pass (v7.0)

Round 1 fixed verification semantics and probing cost. Round 2 closes the issues that
still made the shipped program *look* broken on a real Windows machine and that the
automated suite did not catch. Everything below was executed on this machine; nothing
is claimed from a mock.

## Environment

| Item | Value |
|---|---|
| OS | Windows 11 x64 |
| Python | 3.14.5 (CPython) |
| Qt | PySide6 6.12.0 |
| FFmpeg / ffprobe | 7.1.1 (`C:\Program Files\FFmpeg`) |
| GPU | Intel HD Graphics 4600 (Haswell) — QSV supported, output is CPU-decode/Hybrid except for 8-bit H.264 |
| Automated suite | **104 passed, 0 failed**, no interpreter crash |

## 1. Every successful conversion was reported as “Warning” — fixed

**Symptom:** outputs were correct but verification always returned
`Missing / wrong color_transfer; Missing / wrong color_primaries`, so every file
landed in the yellow *Warning* state. The user only saw warnings for perfect files.

**Cause:** neither the bundled libx264 nor `h264_qsv` writes the matrix, transfer and
primaries into the SPS VUI from `-colorspace/-color_primaries/-color_trc` alone with
FFmpeg 7.1; MP4 has no `colr` atom here, so ffprobe sees only the matrix.

**Fix:** the pipeline rewrites the encoded H.264/HEVC VUI with the
`h264_metadata` / `hevc_metadata` bitstream filter (`app/core/pipeline.py`). This is
encoder-independent, costs no re-encode, and makes `color_space`, `color_transfer`,
`color_primaries` and `color_range` verifiable. CPU and QSV outputs now pass.

**Evidence:** all eight standard frame rates in `tests/test_integration.py` pass the
full policy check again; the end-to-end table below shows `bt709/bt709/bt709` for HD
and `smpte170m/smpte170m/smpte170m` for SD.

## 2. Unstable / mixed-camera sources got a needless retry

**Symptom:** a VFR source produced a first output with an audio/video duration
difference just over the 40 ms policy, so the worker spent a second full CPU encode
with `-bf 0`.

**Fix:** unstable or unverified cadence no longer uses the hardware `vpp_qsv`
frame-rate conversion; it keeps GPU *encoding* but converts cadence with the CPU
`fps` filter, which reconstructs a true single PTS cluster more accurately. Stable
files still use the full GPU path.

## 3. The queue auto-paused on every encode — fixed

**Symptom:** the Round 1 guard paused all jobs after 10 s above 95 % CPU. A video
encoder legitimately uses every core, so every real encode paused itself and waited
for a human to press Resume — observed in the end-to-end run (two files remained
“Waiting”, one “Paused”, no finish event).

**Fix:** `SustainedLoadGuard` now distinguishes pressure types:

- **RAM above 92 % for 10 s** → pause the queue (memory exhaustion can destabilise
  the desktop) and notify.
- **CPU above 97 % for 15 s** → throttle dispatch to one job and log it; when load
  falls below 85 % the limit is released automatically. The encoder is never
  suspended for using the CPU it was asked to use.

## 4. Native crash from the temperature probe — fixed

**Symptom:** the test process and the end-to-end script occasionally died with
`Windows fatal exception: access violation` inside `probe_temperature`, or emitted
Qt `IUnknown` teardown errors.

**Cause:** in-process `pythoncom`/`wmi` COM called from a short-lived worker thread
while the GUI thread was busy.

**Fix:** `cpu_temperature()` now uses the bounded subprocess helper to query CIM via
PowerShell (`timeout=8`), so a driver/COM fault is isolated. The 1 Hz CPU/RAM guard
now hands results to the GUI thread through a locked state object instead of
cross-thread Qt signals, so it cannot touch a destroyed window. The suite and the
end-to-end run complete with **no native crash and empty stderr**.

## 5. UI defects found by rendering every page

- **Empty-square icons:** the sidebar/header used Unicode pictographs missing from
  Poppins; they are now anti-aliased line icons drawn with `QPainter`
  (`app/ui/widgets/common.py:icon`), used by navigation, search, header and queue
  buttons. Wide/high-DPI safe.
- **Title bar wrapped** the window title onto two lines; it is single-line now and
  can be retitled at runtime.
- **Toggle association:** side-by-side toggles stretched across the row so a caption
  appeared detached from its switch. Toggles now size to caption + switch.
- **Log cards overlapped:** rebuilding the card list used `deleteLater()` only, so
  old cards were still painted over the new ones. They are detached immediately;
  long file names are single-line and elided with a tooltip. A **per-file filter**
  (All files / one file) joins the level pills, search, export and auto-scroll, and
  the page renders immediately instead of waiting for the next 350 ms poll.
- **Encoding summary was blank on first open** because of the 0.5 s refresh throttle;
  opening the window now forces a refresh.
- **Persian mode was only half translated.** 140+ strings (settings, advanced,
  logs/table headers, encoding window, preset descriptions, audio notes, support,
  status text) go through `tr()` now, and the encoding window has a `retranslate()`
  path because it is not rebuilt on language change.
- **Primary actions could be scrolled out of view.** *Add folder / Analyze files /
  Start Fix / Stop all* now live in a fixed footer under the scrollable options, with
  a wider glowing primary button.
- **First job after launch used the CPU fallback** while the hardware probe was still
  running. A valid capability cache is loaded synchronously at startup, so an
  immediate start uses QSV; the background probe still refreshes it.
- High-DPI fractional scaling uses `PassThrough`; the bundled `booster.svg` replaces
  the generated letter icon for the window and tray.

## 6. End-to-end acceptance run (real files, real QSV, real UI queue)

`tools/e2e_check.py` creates four deliberately hostile sources in a folder with a
Persian name, scans it through `MainWindow` exactly like the *Start Fix* button, and
verifies every produced file with the same policy used by the app.

| Source (synthetic stand-in) | Source condition | Result | Output video | Output audio |
|---|---|---|---|---|
| `mixed_vfr.mp4` | 50 fps container, VFR selection cadence, avg 21.07 fps | **TV-Safe ✓** | 640×360 **25 CFR**, High, yuv420p, avc1, smpte170m ×3 | AAC-LC 2ch 48 kHz |
| `tenbit_422.mp4` | 10-bit 4:2:2 AVC, 25 fps | **TV-Safe ✓** | 640×360 **25 CFR**, High, yuv420p, 4:2:0 | AAC-LC 2ch 48 kHz |
| `interlaced.mp4` | 50i interlaced, 720×576 | **TV-Safe ✓** | 720×576 **25 CFR** progressive, High | AAC-LC 2ch 48 kHz |
| `فیلم فارسی ۱۰۸۰.mp4` | 1920×1080 59.94p, AC-3 5.1 96 kHz | **TV-Safe ✓** | 1920×1080 **59.94 CFR**, level **4.2**, bt709 ×3 | AAC-LC **2ch 48 kHz** (downmixed) |

All four: `avg_frame_rate == r_frame_rate`, single cadence cluster, positive start
times, no extra streams, `moov` before `mdat`, and zero policy violations. The queue
finished by itself and the safety guard did not pause it.

A real live capture of the Encoding window during that run (QSV pipeline, preview,
frame counter, speed, ETA and sparkline):
[encoding_live.png](screenshots/en/encoding_live.png).

The report is reproducible with:

```powershell
python tools\e2e_check.py     # writes e2e_report.json
```

## 7. Honest limits of this round

- The four sources are **synthetic stand-ins**; the user's `Khanum 1.mp4` /
  `Agha 1.mp4` are still not present, so genuine EDIUS/Voukoder camera mixes were not
  re-run here.
- Physical TV playback, long-film soak, FAT32 splitting on real media, Windows
  power-plan/service/Defender tweaks and clipboard/dialogs still need manual checks.
- The EXE was **not** rebuilt in this environment: `pip install pyinstaller` cannot
  reach PyPI from here. The existing `EdiusBooster.spec` is unchanged and remains the
  documented build path.
- GPU utilisation still reads **N/A** (no vendor counters); the dashboard chart shows
  CPU/speed honestly.
- The design remains a close interpretation of the reference image, not pixel-identical.
