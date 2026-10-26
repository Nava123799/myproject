"""Matplotlib visualisation helpers.

Figures are the visible output of this project, so the plotting code lives in
its own module instead of being scattered through the CLI. Every function
accepts an optional ``ax`` so callers can compose multi-panel figures.
"""

from __future__ import annotations

import matplotlib

# Use the non-interactive Agg backend so the CLI works over SSH, in CI and in
# tests where no display exists. Swap in "TkAgg" locally if you want a window.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from signallab.signals import Signal
from signallab.spectrum import amplitude_spectrum  # noqa: E402

_COLOR_TIME = "#1f77b4"
_COLOR_SPEC = "#d62728"


def plot_signal(signal: Signal, *, ax: Axes | None = None) -> Axes:
    """Draw the time-domain waveform of ``signal``."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 3))

    ax.plot(signal.t, signal.y, color=_COLOR_TIME, linewidth=1.2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Time domain - {signal.name}")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(float(signal.t[0]), float(signal.t[-1]))
    return ax


def plot_spectrum(signal: Signal, *, ax: Axes | None = None, f_max: float | None = None) -> Axes:
    """Draw the single-sided amplitude spectrum of ``signal``.

    Only the lower part of the axis is shown by default (up to a quarter of the
    sample rate) because the interesting content of a baseband signal almost
    always sits there; pass ``f_max`` to override.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 3))

    freqs, amps = amplitude_spectrum(signal)
    ax.plot(freqs, amps, color=_COLOR_SPEC, linewidth=1.2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Amplitude spectrum - {signal.name}")
    ax.grid(True, alpha=0.3)

    limit = f_max if f_max is not None else signal.fs / 4.0
    ax.set_xlim(0.0, min(limit, signal.fs / 2.0))
    ax.set_ylim(bottom=0.0)
    return ax


def save_overview(signal: Signal, path: str, *, dpi: int = 150) -> str:
    """Save a two-panel (time domain + spectrum) figure to ``path``.

    Args:
        signal: The signal to plot.
        path: Destination file, e.g. ``docs/images/sine.png``.
        dpi: Output resolution.

    Returns:
        The path that was written.
    """
    fig, axes = plt.subplots(2, 1, figsize=(9, 6))
    plot_signal(signal, ax=axes[0])
    plot_spectrum(signal, ax=axes[1])
    fig.suptitle(signal.name, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path


def close_all() -> None:
    """Close every open figure. Handy in tests to keep memory flat."""
    plt.close("all")


__all__ = ["Figure", "close_all", "plot_signal", "plot_spectrum", "save_overview"]
