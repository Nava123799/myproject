"""Discrete-time signal generation.

Every generator returns a :class:`Signal`, a frozen dataclass holding the time
axis, the samples and the sample rate. Keeping these three together (instead of
passing ``fs`` around separately) removes a whole class of bugs where a signal
is analysed at the wrong rate.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _time_axis(fs: float, duration: float) -> FloatArray:
    """Build a sampling grid of ``round(fs * duration)`` points spaced ``1/fs`` apart.

    Rounding the number of samples (rather than using ``arange`` with a float
    step) keeps the length exact and avoids the off-by-one accumulation error
    that makes later FFT bins drift off the true frequency.
    """
    if fs <= 0:
        raise ValueError(f"fs must be positive, got {fs}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    n_samples = int(round(fs * duration))
    if n_samples < 2:
        raise ValueError(f"signal too short: {n_samples} sample(s), need at least 2")

    return np.arange(n_samples, dtype=np.float64) / fs


@dataclass(frozen=True, slots=True)
class Signal:
    """A uniformly sampled real-valued signal.

    Attributes:
        t: Sample times in seconds, starting at 0.
        y: Sample values, same length as ``t``.
        fs: Sample rate in Hz.
        name: Human-readable label used in plot titles.
    """

    t: FloatArray
    y: FloatArray
    fs: float
    name: str = "signal"

    def __post_init__(self) -> None:
        if self.t.shape != self.y.shape:
            raise ValueError(
                f"t and y must have the same shape, got {self.t.shape} and {self.y.shape}"
            )
        if self.t.size < 2:
            raise ValueError("a signal needs at least 2 samples")
        if self.fs <= 0:
            raise ValueError(f"fs must be positive, got {self.fs}")

    def __len__(self) -> int:
        return int(self.y.size)

    @property
    def duration(self) -> float:
        """Total duration in seconds, including the final sample interval."""
        return len(self) / self.fs


def sine(
    *,
    freq: float,
    fs: float = 1000.0,
    duration: float = 1.0,
    amplitude: float = 1.0,
    phase: float = 0.0,
) -> Signal:
    """Generate ``amplitude * sin(2*pi*freq*t + phase)``.

    Args:
        freq: Frequency in Hz.
        fs: Sample rate in Hz.
        duration: Length in seconds.
        amplitude: Peak amplitude.
        phase: Initial phase in radians.

    Returns:
        The sampled sine wave.

    Raises:
        ValueError: If ``freq`` is not positive.
    """
    if freq <= 0:
        raise ValueError(f"freq must be positive, got {freq}")

    t = _time_axis(fs, duration)
    y = amplitude * np.sin(2.0 * np.pi * freq * t + phase)
    return Signal(t=t, y=y, fs=fs, name=f"sine {freq:g} Hz")


def square(
    *,
    freq: float,
    fs: float = 1000.0,
    duration: float = 1.0,
    amplitude: float = 1.0,
) -> Signal:
    """Generate a square wave by taking the sign of an underlying sine.

    Using ``sign(sin(...))`` instead of a modulo trick keeps the duty cycle at
    exactly 50% even when the period is not an integer number of samples.
    """
    if freq <= 0:
        raise ValueError(f"freq must be positive, got {freq}")

    t = _time_axis(fs, duration)
    # np.sign() would yield 0 wherever the sine is exactly zero (t = 0, T/2, ...),
    # which a square wave never does; compare against zero to keep it two-valued.
    y = np.where(np.sin(2.0 * np.pi * freq * t) >= 0.0, amplitude, -amplitude)
    return Signal(t=t, y=y, fs=fs, name=f"square {freq:g} Hz")


def chirp(
    *,
    f_start: float,
    f_end: float,
    fs: float = 1000.0,
    duration: float = 1.0,
    amplitude: float = 1.0,
) -> Signal:
    """Generate a linear frequency sweep from ``f_start`` to ``f_end``.

    The instantaneous frequency is ``f_start + (f_end - f_start) * t / duration``.
    Phase is its integral, which is why the argument below contains the
    ``(f_end - f_start) * t**2 / (2 * duration)`` term rather than a plain
    product of time and frequency.
    """
    if f_start <= 0 or f_end <= 0:
        raise ValueError(f"frequencies must be positive, got {f_start} and {f_end}")

    t = _time_axis(fs, duration)
    sweep = (f_end - f_start) / duration
    phase = 2.0 * np.pi * (f_start * t + 0.5 * sweep * t**2)
    y = amplitude * np.sin(phase)
    return Signal(t=t, y=y, fs=fs, name=f"chirp {f_start:g}-{f_end:g} Hz")


def with_white_noise(signal: Signal, *, snr_db: float, seed: int | None = 0) -> Signal:
    """Return a copy of ``signal`` with additive white Gaussian noise.

    The noise power is derived from the measured power of the input, so the
    requested SNR holds for any amplitude. A fixed default ``seed`` keeps runs
    reproducible, which matters when figures end up in a README.

    Args:
        signal: The clean signal.
        snr_db: Target signal-to-noise ratio in dB.
        seed: Seed for the random generator, or ``None`` for fresh entropy.

    Returns:
        A new signal with noise added.
    """
    power = float(np.mean(signal.y**2))
    if power == 0.0:
        raise ValueError("cannot add noise to an all-zero signal")

    snr_linear = 10.0 ** (snr_db / 10.0)
    noise_power = power / snr_linear
    rng = np.random.default_rng(seed)
    noise = rng.normal(scale=np.sqrt(noise_power), size=signal.y.shape)

    return Signal(
        t=signal.t,
        y=signal.y + noise,
        fs=signal.fs,
        name=f"{signal.name} (SNR {snr_db:g} dB)",
    )
