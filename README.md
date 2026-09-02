# White Noise System (`ses-sistemi`)

A calibrated, schedule-driven white-noise generator for laboratory use.

`ses-sistemi` is a small desktop application (Python + Tkinter) that plays
continuous white noise through a selected audio output for a precisely timed
program — including repeated **work / rest** cycles — while keeping the host
machine awake for the whole run. It was built to deliver the 80 dB white-noise
stressor of a chronic unpredictable mild stress (CUMS) protocol in rats, and it
is documented here so that later experiments can reuse it without
reverse-engineering the code.

- **Version:** 1.0.0
- **Status:** feature-complete; in use in an ethics-approved animal-behaviour
  protocol (see *Research context*)
- **Platforms:** Windows 8/8.1 and later (64-bit), macOS on Apple Silicon
  (Intel Macs: build from source)
- **End users need no Python installation** — a single-file executable is produced
  by the included build scripts.

---

## Download

**You do not need this repository to use the application.** Download one file,
double-click it, done — no Python, no installer, no configuration.

| Platform | Download |
|---|---|
| **Windows** — 8 / 8.1 / 10 / 11, 64-bit | **[⬇ SesSistemi-windows-x64.exe](https://github.com/theiozyurt/ses-sistemi/releases/latest/download/SesSistemi-windows-x64.exe)** |
| **macOS** — Apple Silicon (M1 or later) | **[⬇ SesSistemi-macos-arm64](https://github.com/theiozyurt/ses-sistemi/releases/latest/download/SesSistemi-macos-arm64)** |

Both links always point at the newest release (about 20–25 MB each). Older
versions are on the [Releases page](https://github.com/theiozyurt/ses-sistemi/releases).

> **The v1.0.0 binaries have not been published yet.** The links above start
> working the moment the first release carries them; until then, run the
> application [from source](#installation-from-source). Remove this note when
> the release is up.

### System requirements

| | Windows | macOS |
|---|---|---|
| Operating system | Windows 8 / 8.1 or later, **64-bit** | macOS 13 (Ventura) or later |
| Processor | x86-64 | **Apple Silicon** (M1 or later) |
| Memory | ~200 MB free | ~200 MB free |
| Disk | ~30 MB | ~30 MB |
| Audio | Any output device — built-in speakers, USB interface, HDMI | Same |
| Python | **Not required** | **Not required** |
| Internet | **Not required**, at install or at run time | Same |

The macOS requirements are inherited from the Python used to produce the build,
not from the application itself. If your lab has an Intel Mac or an older macOS,
[build from source](#building-a-single-file-executable) on that machine — the
code itself has no such limit.

### First launch

Both files are **unsigned**, so each operating system warns once. This is
expected for research software that has not been through a paid signing
programme, and the warning does not reappear afterwards.

**Windows** — a blue "Windows protected your PC" panel appears:
*More info* → *Run anyway*.

**macOS** — right-click the file in Finder and choose *Open* (double-clicking
will not offer the option), or clear the quarantine flag from Terminal:

```bash
xattr -d com.apple.quarantine SesSistemi-macos-arm64
chmod +x SesSistemi-macos-arm64
```

The application is portable: it writes nothing outside its own window, installs
no services, and touches no registry keys. To remove it, delete the file.

Go to [Usage guide](#usage-guide) to set up your first session, or to
[Calibrate against a sound-level meter](#3-calibrate-against-a-sound-level-meter)
if the level matters — which, in an experiment, it does.

---

## Table of contents

- [**Download**](#download) — start here if you just want to run it
  - [System requirements](#system-requirements)
  - [First launch](#first-launch)
- [Research context](#research-context)
  - [The stressor this application delivers](#the-stressor-this-application-delivers)
  - [What this buys the protocol](#what-this-buys-the-protocol)
- [What the application does](#what-the-application-does)
- [Repository layout](#repository-layout)
- [Development requirements](#development-requirements)
- [Installation (from source)](#installation-from-source)
- [Running](#running)
- [Usage guide](#usage-guide)
  - [1. Set the exposure schedule](#1-set-the-exposure-schedule)
  - [2. Choose the audio output](#2-choose-the-audio-output)
  - [3. Calibrate against a sound-level meter](#3-calibrate-against-a-sound-level-meter)
  - [4. Run, pause, stop](#4-run-pause-stop)
  - [5. Language and theme](#5-language-and-theme)
- [Designing a protocol for a new experiment](#designing-a-protocol-for-a-new-experiment)
  - [Worked example: the 80 dB white-noise block](#worked-example-the-80-db-white-noise-block)
- [How the audio is produced](#how-the-audio-is-produced)
- [Building a single-file executable](#building-a-single-file-executable)
  - [Publishing a release](#publishing-a-release)
- [Limitations and known constraints](#limitations-and-known-constraints)
- [Safety and welfare notes](#safety-and-welfare-notes)
- [Citation](#citation)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

---

## Research context

This tool was written to deliver the white-noise stressor of the following study:

> **Effect of 3D orbital shaking (3D-OS) on the hippocampal
> FGF2/FGF10–FGFR1/2–p-AKT–BDNF axis and Piezo1/2 expression under a chronic
> unpredictable mild stress (CUMS) model in male rats**
>
> Principal investigator: Dr. Ulya Keskin, Department of Medical Pharmacology,
> Faculty of Medicine, Kütahya Health Sciences University (KSBÜ), Türkiye.
> Approved by the KSBÜ Animal Experiments Local Ethics Committee (HADYEK),
> decision no. 2026.07.02 of 23 July 2026.

### The stressor this application delivers

A CUMS paradigm works by rotating a pool of mild stressors in an order the
animal cannot anticipate. White noise is one of seven stressors in this
protocol's weekly pool, and its specification is a single line:

| Stressor | Duration | Delivery |
|---|---|---|
| White noise, **80 dB** | **3 × 1 h, light phase** | Played from a device, **verified with an SPL meter** |

Those two bold phrases are the entire reason this application exists.

**"3 × 1 h"** is a block design, not a single exposure. Running it by hand means
three separate start/stop decisions per session, on a day whose timetable was
randomised in advance — the kind of thing that drifts by ten or fifteen minutes
under real husbandry load and is never recorded accurately. Interval mode turns
it into one button press, and the application's shipped default — *1 h work /
1 h rest × 3* — **is** this block.

**"Verified with an SPL meter"** means the number that matters is 80 dB at the
cage, not a percentage on a slider. The calibration workflow below is built
around exactly that: you type in what your meter reads, and the application
tracks how far your later adjustments move you away from it.

The rest of the protocol constrains what this application deliberately does
*not* do. Each stressor is used only once per weekly block and never on two
consecutive days, and the weekly timetable is generated by someone independent
of the experimenter. Scheduling across days is therefore a randomisation
decision that belongs outside the software; the application makes a *single
session* deterministic, and the operator starts it on the day the timetable
assigns.

### What this buys the protocol

| Requirement of the protocol | How the application satisfies it |
|---|---|
| Fixed exposure duration per session | Hours / minutes / seconds entry, counted down by the app |
| Repeated on/off blocks within a session | Interval mode: *work → rest*, repeated N times |
| Stable, reproducible intensity | Volume (%) + software gain (dB), with a soft limiter, plus a meter-anchored calibration readout |
| Same stimulus every session | Synthetic Gaussian white noise generated identically on every launch |
| Unattended multi-hour runs | The host machine is prevented from sleeping for as long as the app is open |
| Reporting in a methods section | Every parameter that shapes the output is visible on one screen and can be transcribed verbatim |

Nothing in the code is specific to this study. Any protocol that needs *"X dB of
white noise for Y minutes, N times, in this room"* can use it as-is.

## What the application does

- **Timed exposure.** Enter a work duration in hours / minutes / seconds; the app
  plays for exactly that long and then stops.
- **Interval mode (work / rest cycling).** Enable the checkbox and the app runs
  `work → rest`, repeated for a chosen number of cycles. The default is
  1 h work / 1 h rest × 3 repeats — a six-hour program. Both the phase countdown
  and the total program countdown are displayed live.
- **Pause / resume / stop.** *Pause* freezes whichever phase is currently active
  (work **or** rest) and *Resume* continues from that exact point; *Stop* ends the
  whole program.
- **Volume and software gain.** A 0–100 % volume slider plus a 0 to +40 dB
  software amplifier, protected by a `tanh` soft limiter so that high gain never
  produces hard clipping, `NaN` or `Inf` samples.
- **Meter-anchored SPL estimates.** Enter what a sound-level meter reads at the
  speaker and at the animal's position; the app then tracks how far the current
  settings deviate from that reference and shows updated *estimates* for both
  positions.
- **Output device selection.** Lists the system's audio outputs and can rescan
  them without restarting (useful when a USB interface is plugged in mid-setup).
- **Sleep inhibition.** From launch until close — including rest phases and
  pauses — the computer is kept from sleeping, so a six-hour program is never cut
  short by a power setting.
- **Bilingual interface (Türkçe / English) and light / dark themes,** both
  switchable at runtime without restarting.

---

## Repository layout

```text
ses-sistemi/
├── main.py                          # The entire application (player engine + GUI)
├── requirements.txt                 # Runtime dependencies, pinned for Windows 8 support
├── requirements-build-windows.txt   # PyInstaller, needed only to build the .exe
├── ses-sistemi.spec                 # PyInstaller one-file spec (shared by both platforms)
├── build_windows.bat                # Windows build script  -> dist\SesSistemi.exe
├── build_mac.sh                     # macOS build script    -> dist/SesSistemi
├── vendor/mac_wheels/               # PyInstaller wheels for offline macOS builds
├── CITATION.cff                     # How to cite this software
├── CHANGELOG.md                     # Version history
└── LICENSE                          # MIT
```

`main.py` is deliberately a single file. It contains four units:

| Unit | Responsibility |
|---|---|
| `TRANSLATIONS` / `THEMES` | Every user-visible string and colour, in one place |
| `SleepGuard` | Keeps the OS awake (Windows API / `caffeinate`) |
| `WhiteNoisePlayer` | Noise buffer, gain, limiter, `sounddevice` output stream |
| `SoundTestApp` | Tkinter GUI, schedule building, countdowns, calibration maths |

To add a language, add one more key (e.g. `"de"`) to `TRANSLATIONS` with the same
translation keys — nothing else in the code needs to change.

---

## Development requirements

| | Version | Note |
|---|---|---|
| Python | **3.8.x, 64-bit** if you target Windows 8 / 8.1 | Newer Python and NumPy builds have no wheels for that OS. On macOS and modern Windows any current Python 3 works. |
| NumPy | 1.24.4 (pinned) | Noise synthesis |
| sounddevice | 0.4.6 (pinned) | PortAudio bindings for output |
| cffi / pycparser | 1.15.1 / 2.21 | `sounddevice` dependencies |
| Tkinter | bundled with Python | GUI |

These apply only if you run or build from source; the downloads above need none
of them. The pins in `requirements.txt` exist for **binary compatibility with
Windows 8**.
If that target is irrelevant to your setup, newer versions will normally work.

---

## Installation (from source)

**Windows**

```bat
py -3.8 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

> Linux is not an officially supported target: the audio path works, but sleep
> inhibition is intentionally disabled there (see *Limitations*).

## Running

**From source**

```bat
.venv\Scripts\python main.py          :: Windows
```

```bash
.venv/bin/python main.py              # macOS / Linux
```

**As a packaged executable** — what the person running the experiment actually
uses. Nothing on this page applies to them: they download one file from
[Download](#download) and double-click it.

---

## Usage guide

The window is laid out in two columns: scheduling and level control on the left,
output selection and run controls on the right. A full session goes through the
five steps below.

### 1. Set the exposure schedule

**Work Duration** — hours / minutes / seconds. In interval mode this is the
length of *each* work phase, not the total program.

**Interval Mode (Work / Rest Cycle)** — tick *Enable interval mode* to turn a
single exposure into a repeating block design:

```text
[ work ][ rest ][ work ][ rest ][ work ][ rest ]     repeats = 3
```

- **Rest Duration** — silence between work phases.
- **Repeat Count** — 1 to 99 cycles.
- Defaults are 1 h / 1 h / 3, i.e. a six-hour program.
- The schedule always **ends on a rest phase**; the program is reported as
  `COMPLETED` once that final rest elapses.

With interval mode off, the app behaves as a plain one-shot timer: it plays for
*Work Duration* and stops.

### 2. Choose the audio output

Pick the output device in *Audio Output*. Press **Refresh Audio Outputs** after
connecting an interface or speaker so it appears in the list. Playback will not
start if no device is selected.

> For a reproducible experiment, always drive the same amplifier and speaker
> through the same output device, and record which one in your notes — the
> application controls the *signal*, not the electro-acoustic chain after it.

### 3. Calibrate against a sound-level meter

This is the step that makes the numbers meaningful, and it is worth doing at the
start of every experimental session.

**The application cannot know the real sound pressure level in the room.** Actual
SPL depends on the amplifier, the speaker, the distance, and the acoustics of the
enclosure. What the app provides instead is a *relative* model anchored to your
own meter readings:

1. Start playback at the volume and gain you intend to use.
2. With a sound-level meter, read the level **next to the speaker** and type it
   into **Nearby Measurement (dB)**.
3. Read the level **at the position that matters** — the cage, the animal, the
   listener — and type it into **Distant Measurement (dB)**.
4. The moment you enter those values, the app snapshots the current
   *Volume (%)* and *dB Control* settings as the **reference point**.
5. Now move the sliders. The app computes how much the output has changed
   relative to the reference and adds that difference to your measured values,
   updating **Estimated nearby** and **Estimated at distance** live.

Example: you measure 75 dB near and 60 dB far. Raising *dB Control* by +10 dB
updates the labels to ~85 dB and ~70 dB. Lowering *Volume* to 50 % is folded into
the same calculation.

The change is computed as

```text
Δ dB = [ 20·log10(volume_now) + gain_now ] − [ 20·log10(volume_ref) + gain_ref ]
```

so both controls are accounted for, and the displayed values are explicitly
**estimates**, never a claimed physical measurement. Re-verify with the meter
whenever the level matters.

### 4. Run, pause, stop

| Button | Effect |
|---|---|
| **START** | Builds the schedule and begins the first work phase |
| **PAUSE** | Freezes the current phase — work *or* rest — with its countdown |
| **RESUME** | Continues from exactly where it was paused |
| **STOP** | Ends the whole program immediately |

The status field reads `READY`, `RUNNING`, `RESTING`, `PAUSED`, `COMPLETED`,
`STOPPED` or `ERROR`, and two countdowns are shown: remaining time in the current
phase, and remaining time in the whole program.

The computer is kept awake from launch to close, so nothing has to be touched
during a multi-hour run.

### 5. Language and theme

The dropdown at the top right switches between **Türkçe** and **English**; the
adjacent button toggles **light / dark** theme. Both apply instantly to every
label, button, entry, dropdown and status field.

---

## Designing a protocol for a new experiment

Use this as a checklist when the module is reused in another study.

**Before the first session**

1. Fix the hardware chain (output device → amplifier → speaker) and the geometry
   (speaker position, distance to subject, room or enclosure). Photograph it.
2. Decide the target level *at the subject's position*, not at the speaker.
3. Set *Volume* and *dB Control* until a meter at the subject's position reads the
   target, then perform the calibration in step 3 above so the on-screen estimates
   are anchored.
4. Write down the exact settings: volume %, dB control, output device, both
   measured values, meter model and weighting (A/C), and the time of day.

**Every session afterwards**

5. Re-check the meter reading before starting — speakers, cables and OS volume
   settings drift between sessions.
6. Enter the schedule and start. Do not change the sliders mid-program; a change
   during a run alters the stimulus without leaving a record.

**Reporting**

A methods section can be written directly from the interface. A minimal,
reproducible description looks like:

> White noise (synthetic Gaussian, 44.1 kHz, stereo) was delivered via
> `ses-sistemi` v1.0.0 through *&lt;output device → amplifier → speaker&gt;* positioned
> *&lt;distance&gt;* from the cage. Levels were verified with a *&lt;meter model&gt;* sound
> level meter (*&lt;weighting&gt;*) and set to *&lt;X&gt;* dB at the cage floor. Each session
> consisted of *&lt;N&gt;* cycles of *&lt;work&gt;* min exposure and *&lt;rest&gt;* min silence.

**Adapting the schedule**

- For a *single continuous exposure*: leave interval mode off.
- For *unpredictable* stressors (as in CUMS): randomise the start time and, if the
  design calls for it, the duration across days; the app makes each session
  deterministic, the *timetable* remains the experimenter's responsibility.
- For very long programs: the maximum is 99 cycles; longer studies are run as
  repeated sessions rather than one program.

---

### Worked example: the 80 dB white-noise block

The configuration this application was built for, end to end:

| Field | Value |
|---|---|
| Work Duration | 1 h 0 min 0 s |
| Interval mode | enabled |
| Rest Duration | 1 h 0 min 0 s |
| Repeat Count | 3 |
| Audio Output | the interface driving the room speaker |
| Volume / dB Control | whatever makes the meter read 80 dB at cage level |
| Nearby / Distant Measurement | the two meter readings taken at that setting |

Result: three one-hour noise exposures spread across a six-hour light-phase
window, at a level anchored to a physical measurement, with the host machine kept
awake throughout and both countdowns visible from the door of the room.

To adapt it, change one number at a time: shorter exposures (Work Duration),
denser blocks (Rest Duration), more blocks (Repeat Count), different intensity
(re-measure with the meter and re-enter both reference values).

---

## How the audio is produced

Understanding the signal path matters if you plan to modify the stimulus.

- **Source.** A 2-second stereo buffer of Gaussian white noise
  (`numpy.random.normal`, σ = 0.15) is generated at launch, at 44 100 Hz,
  `float32`, 2 channels.
- **Seamless looping.** The last 20 ms of the buffer are cross-faded into the
  first 20 ms, so the loop point produces neither a click nor an audible dip.
  The stimulus is therefore continuous, not a repeating "pulse".
- **Gain stage.** Output amplitude is `volume × 10^(gain_dB/20)`, with gain capped
  at +40 dB.
- **Soft limiter.** Every output block passes through `tanh()`, which is bounded
  on (−1, 1). High gain compresses rather than clips, and no `NaN`/`Inf` can reach
  the sound card. This does **not** increase what the speaker can physically
  produce — if the hardware runs out of headroom, you need better hardware, not
  more gain.
- **Streaming.** A `sounddevice.OutputStream` callback (blocksize 1024) reads
  through the buffer and wraps around; the buffer is never regenerated during a
  run, so the stimulus is identical from the first second to the last.
- **Sleep inhibition.** `SetThreadExecutionState` (`ES_CONTINUOUS |
  ES_SYSTEM_REQUIRED`) via `ctypes` on Windows; a background `caffeinate -i`
  process on macOS. Both are released when the app closes. On any other platform,
  or on any error, the feature disables itself silently and the rest of the
  application is unaffected.

Replacing the synthetic noise with a fixed WAV asset — for pink noise, a recorded
stressor, or a tone — means changing `WhiteNoisePlayer._create_noise_buffer()`
only; everything downstream (scheduling, gain, limiter, calibration) keeps
working unchanged.

---

## Building a single-file executable

Both platforms share `ses-sistemi.spec`.

### Windows → `dist\SesSistemi.exe`

Run on a machine that is itself compatible with the oldest Windows you target
(Windows 8 / 8.1 needs Python 3.8.x 64-bit). Cross-compiling from another OS is
not reliable.

```bat
build_windows.bat
```

The script creates a virtual environment, installs the pinned runtime
dependencies plus PyInstaller, and produces the one-file executable.

### macOS → `dist/SesSistemi`

```bash
./build_mac.sh
```

The script reuses the existing `.venv` (NumPy and sounddevice must already be
installed there), then installs PyInstaller **from `vendor/mac_wheels/` without
touching the network** — which is why those wheels are committed. If `.venv` does
not exist it is created, and you will need to install the runtime dependencies
yourself:

```bash
.venv/bin/pip install numpy sounddevice cffi
```

The resulting binary is unsigned and Apple Silicon only; distribute it with the
Gatekeeper instructions from [First launch](#first-launch).

---

### Publishing a release

The download links at the top of this file are **fixed URLs** of the form
`releases/latest/download/<asset name>`, so they never need updating — but they
only resolve if each release carries assets with exactly these names:

| Platform | Asset name |
|---|---|
| Windows | `SesSistemi-windows-x64.exe` |
| macOS (Apple Silicon) | `SesSistemi-macos-arm64` |

Renaming an asset silently breaks the links in this README. Build on each
platform, rename, then publish:

```bash
# macOS machine
./build_mac.sh
mv dist/SesSistemi dist/SesSistemi-macos-arm64

# Windows machine
#   build_windows.bat   ->   rename dist\SesSistemi.exe to SesSistemi-windows-x64.exe
```

Before writing a macOS minimum version into the requirements table, read it off
the binary you actually produced rather than trusting this file:

```bash
otool -l dist/SesSistemi-macos-arm64 | grep -A3 LC_BUILD_VERSION
```

Then create the release, attaching both files:

```bash
gh release create v1.0.0 \
  dist/SesSistemi-macos-arm64 \
  dist/SesSistemi-windows-x64.exe \
  --title "White Noise System 1.0.0" \
  --notes "See CHANGELOG.md for the full list of changes."
```

Two things to check every time:

1. **Rebuild both binaries from the tagged commit.** An executable built before
   the last code change is the easiest way to ship an application that behaves
   differently from its own documentation.
2. **The repository must be public** for anyone outside the account to follow the
   download links. While it is private, the links return 404 even for people who
   can see this README.

---

## Limitations and known constraints

- **The application does not measure sound.** All displayed dB figures are
  estimates derived from your own meter readings. Treat a sound-level meter as the
  only source of truth.
- **The +40 dB software gain is not amplification of the room.** It cannot exceed
  the physical capability of the amplifier and speaker.
- **No logging.** The program does not write a run log; exposure records are kept
  by the experimenter. (This is the most obvious next feature.)
- **The published macOS binary is Apple Silicon only.** Intel Macs and older
  macOS versions are not covered by the download and need a build from source on
  such a machine.
- **Neither binary is code-signed or notarised,** so both operating systems warn
  on first launch.
- **Sleep inhibition is Windows/macOS only** and is deliberately a no-op on Linux.
- **Screen sleep is not blocked** on Windows — only system sleep. The display may
  turn off; playback continues.
- **A single stimulus type.** White noise only, generated internally; no file
  playback, no frequency shaping.
- **Interval schedules always end with a rest phase**, which slightly lengthens
  the total program compared with a "work-last" design.

---

## Safety and welfare notes

- Sustained high sound levels carry a hearing-damage risk **for people in the
  room as well as for the animals**. Raise levels gradually and verify with a
  meter rather than trusting the on-screen estimates.
- Any use of noise as a stressor in animal research requires the approval of the
  relevant animal experiments local ethics committee (in Türkiye, HADYEK) and
  must follow the approved protocol. The study described above holds KSBÜ
  HADYEK approval no. 2026.07.02 (23 July 2026). **That approval covers that
  study only.** This repository provides a delivery tool and carries no ethical
  clearance of its own; a new protocol needs its own.
- The estimated-dB display is a convenience, not an instrument. If a level is
  part of your published methods, it must come from a calibrated meter.

---

## Citation

If this software supports work you publish, please cite it. `CITATION.cff` in the
repository root carries machine-readable metadata that GitHub and reference
managers can read directly; the human-readable form is:

> Özyurt, İ. (2026). *White Noise System (`ses-sistemi`)*, version 1.0.0
> [Computer software]. https://github.com/theiozyurt/ses-sistemi

### Related work

The 3D-OS parameters of the study above (25 RPM, 180 min/day) were carried over
from the same group's earlier maternal-separation work, which is the
methodological precedent for the intervention this tool was built alongside:

> Keskin, U., Kara, M. K., Özel, O., Kuraşı, İ. Ç., Akyol, S., Özbayer, C.,
> Arı, N. S., Tunç, Y., & Bayır, E. (2026). Moderate 3D orbital shaking mitigates
> maternal separation-induced neurodevelopmental impairments in rats.
> *Behavioural Processes, 239*, 105394.
> https://doi.org/10.1016/j.beproc.2026.105394

---

## License

Released under the MIT License — see [`LICENSE`](LICENSE). You may use, modify and
redistribute it, including in commercial and academic work, provided the copyright
notice is retained. The software is provided without warranty; see
[Limitations](#limitations-and-known-constraints) before relying on it for
measurement.

---

## Acknowledgements

This module was written for the research team of the study named in
[Research context](#research-context), whose protocol defined every requirement
the application implements:

- **Dr. Ulya Keskin** — principal investigator; Department of Medical
  Pharmacology, Faculty of Medicine, Kütahya Health Sciences University
- **Dr. Melkan Kağan Kara** — project lead
- **Dr. Serel Akyol** — co-investigator
- **Assoc. Prof. Dr. Ayşe Koçak Sezgin** — co-investigator; Department of Medical
  Biochemistry, Faculty of Medicine, Kütahya Health Sciences University
- **İsmail Özyurt** — research software (this application)

The study is conducted at the KSBÜ Faculty of Medicine Laboratory Animals
Breeding and Research Unit (DEHYUB) and KUYAM.

The 80 dB / 3 × 1 h stressor specification, the requirement to verify levels
with a sound-level meter, and the constraint that cross-day scheduling stays
with the randomisation rather than the software all come from that protocol.
Design decisions in this application follow it rather than the other way round.

---

## Contact

**İsmail Özyurt** — <ismailozyurt96@gmail.com> — https://github.com/theiozyurt

Issues and pull requests are welcome, particularly from anyone adapting the module
for a new exposure protocol.
