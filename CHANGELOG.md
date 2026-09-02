# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- README: a Download section with fixed `releases/latest/download/` links for
  Windows and macOS, per-platform system requirements, and first-launch
  instructions for the unsigned binaries — so an experimenter never has to touch
  the repository.
- README: a release-publishing procedure that fixes the two asset names the
  download links depend on, and a reminder to rebuild both binaries from the
  tagged commit.

### Changed

- "Requirements" renamed to "Development requirements" to separate it from the
  end-user system requirements.
- Platform claim corrected: the published macOS binary is Apple Silicon only;
  Intel Macs need a build from source.

## [1.0.0] - 2026-09-02

First tagged release. The application is feature-complete and delivers the 80 dB
white-noise stressor of an ethics-approved CUMS protocol in rats (KSBÜ HADYEK
decision no. 2026.07.02).

### Added

- Interval mode: a repeating work / rest cycle with a configurable repeat count
  (default 1 h work / 1 h rest × 3), with per-phase and whole-program countdowns.
- Pause / Resume that freezes and restores whichever phase is active, and Stop
  that ends the whole program.
- Bilingual interface (Türkçe / English), switchable at runtime from a single
  `TRANSLATIONS` dictionary.
- Light and dark themes, switchable at runtime, defined centrally in `THEMES`.
- Sleep inhibition for the lifetime of the application window:
  `SetThreadExecutionState` on Windows, `caffeinate` on macOS; a silent no-op
  elsewhere.
- Two-column window layout replacing the previous tall single-column form.
- macOS single-file build (`build_mac.sh`) using the PyInstaller wheels vendored
  in `vendor/mac_wheels/`, so the build needs no network access.
- Research documentation: English README covering the calibration workflow,
  protocol design for new experiments, and the signal chain; plus `LICENSE`,
  `CITATION.cff` and this changelog.

### Changed

- The sound pressure level estimate now folds in the volume percentage as well as
  the dB gain. Previously the estimate tracked only the dB control and silently
  ignored volume changes, which could misreport the level by tens of dB.
- Calibration is now expressed as two reference *measurements* (near the speaker
  and at the subject's position) plus a live estimate of the deviation from that
  reference, rather than as a claimed absolute target level.
- Loop point of the noise buffer is cross-faded over 20 ms, removing an audible
  dip and click at the wrap-around.

### Fixed

- High gain settings no longer hard-clip; a `tanh` soft limiter bounds the output
  and prevents `NaN`/`Inf` samples from reaching the audio device.

## [0.3.0] - 2026-08-17

### Added

- Windows single-file executable build (`build_windows.bat`, `ses-sistemi.spec`).

## [0.2.0] - 2026-08-17

### Changed

- Dependencies pinned (NumPy 1.24.4, sounddevice 0.4.6) for binary compatibility
  with Windows 8 / 8.1 on Python 3.8.x 64-bit.

## [0.1.0] - 2026-08-17

### Added

- Initial white noise application: timed playback, output device selection,
  volume control and a calibrated dB gain stage.
