"""Command-line interface for signallab."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from signallab import __version__
from signallab.signals import Signal, chirp, sine, square, with_white_noise
from signallab.spectrum import dominant_frequency, peak_amplitude


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="signallab",
        description="Generate a test signal and analyse it in the frequency domain.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--type",
        dest="kind",
        choices=["sine", "square", "chirp"],
        default="sine",
        help="Waveform to generate.",
    )
    parser.add_argument("--freq", type=float, default=50.0, help="Frequency in Hz.")
    parser.add_argument(
        "--freq-end",
        type=float,
        default=None,
        help="End frequency for --type chirp (defaults to 8x --freq).",
    )
    parser.add_argument("--fs", type=float, default=1000.0, help="Sample rate in Hz.")
    parser.add_argument("--duration", type=float, default=1.0, help="Duration in seconds.")
    parser.add_argument("--amplitude", type=float, default=1.0, help="Peak amplitude.")
    parser.add_argument(
        "--snr",
        type=float,
        default=None,
        help="If set, add white Gaussian noise at this SNR in dB.",
    )
    parser.add_argument("--out", type=Path, default=None, help="Save the figure to this path.")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _make_signal(args: argparse.Namespace) -> Signal:
    """Build the signal described by parsed CLI arguments."""
    if args.kind == "sine":
        signal = sine(
            freq=args.freq,
            fs=args.fs,
            duration=args.duration,
            amplitude=args.amplitude,
        )
    elif args.kind == "square":
        signal = square(
            freq=args.freq,
            fs=args.fs,
            duration=args.duration,
            amplitude=args.amplitude,
        )
    else:
        signal = chirp(
            f_start=args.freq,
            f_end=args.freq_end if args.freq_end is not None else args.freq * 8.0,
            fs=args.fs,
            duration=args.duration,
            amplitude=args.amplitude,
        )

    if args.snr is not None:
        signal = with_white_noise(signal, snr_db=args.snr)

    return signal


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        signal = _make_signal(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Skip the DC bin: anything below one bin width is just numerical noise at 0 Hz.
    ff_bin = signal.fs / len(signal)
    f_peak = dominant_frequency(signal, min_freq=ff_bin)
    a_peak = peak_amplitude(signal)

    print(f"signal      : {signal.name}")
    print(f"samples     : {len(signal)}")
    print(f"sample rate : {signal.fs:g} Hz")
    print(f"duration    : {signal.duration:g} s")
    print(f"peak freq   : {f_peak:.1f} Hz")
    print(f"peak ampl.  : {a_peak:.3f}")

    if args.out is not None:
        from signallab.plotting import save_overview

        args.out.parent.mkdir(parents=True, exist_ok=True)
        save_overview(signal, str(args.out))
        print(f"figure      : {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
