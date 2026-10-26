"""Frequency-domain analysis."""

from __future__ import annotations

import numpy as np

from signallab.signals import FloatArray, Signal


def amplitude_spectrum(signal: Signal, *, remove_dc: bool = True) -> tuple[FloatArray, FloatArray]:
    """Compute the single-sided amplitude spectrum of ``signal``.

    A real sine of peak amplitude ``A`` that falls exactly on a bin produces
    ``|X[k]| = A * N / 2``, so the scaling factor ``2 / N`` recovers ``A``.
    The DC bin and (for even ``N``) the Nyquist bin are halved because they have
    no mirrored counterpart to fold back from.

    Args:
        signal: The signal to analyse.
        remove_dc: Subtract the mean first, so a constant offset does not
            dominate the plot. Set to ``False`` to keep it.

    Returns:
        Tuple of ``(freqs, amps)``, both of length ``N // 2 + 1``. ``freqs``
        runs from 0 to ``fs / 2`` inclusive.

    Note:
        No window is applied, so a component that is *not* an integer number of
        periods long will leak energy into neighbouring bins. Pick a duration
        equal to a whole number of periods for clean peaks, or add a Hann
        window later (see the roadmap in the README).
    """
    y = signal.y.astype(np.float64, copy=True)
    if remove_dc:
        y -= y.mean()

    n = y.size
    spec = np.fft.rfft(y)
    freqs = np.fft.rfftfreq(n, d=1.0 / signal.fs)
    amps = np.abs(spec) * (2.0 / n)

    amps[0] *= 0.5
    if n % 2 == 0:
        amps[-1] *= 0.5

    return freqs, amps


def dominant_frequency(signal: Signal, *, min_freq: float = 0.0) -> float:
    """Return the frequency with the largest amplitude, ignoring DC leakage.

    Args:
        signal: The signal to analyse.
        min_freq: Ignore bins below this frequency. The default of 0 keeps the
            DC bin in play; pass a small positive value (e.g. 1 Hz) to skip it.

    Returns:
        The dominant frequency in Hz, or 0.0 if no bin qualifies.
    """
    freqs, amps = amplitude_spectrum(signal)

    mask = freqs >= min_freq
    if not mask.any():
        return 0.0

    candidate_freqs = freqs[mask]
    candidate_amps = amps[mask]
    return float(candidate_freqs[int(np.argmax(candidate_amps))])


def peak_amplitude(signal: Signal, *, min_freq: float = 0.0) -> float:
    """Return the amplitude of the dominant component, in the units of the signal."""
    freqs, amps = amplitude_spectrum(signal)
    mask = freqs >= min_freq
    if not mask.any():
        return 0.0
    return float(amps[mask].max())


def band_power(signal: Signal, *, f_low: float, f_high: float) -> float:
    """Sum the power in ``[f_low, f_high]`` using Parseval's relation on the FFT.

    Useful for answering "how much energy sits in the noise band" instead of
    eyeballing the plot.

    Args:
        signal: The signal to analyse.
        f_low: Lower band edge in Hz, inclusive.
        f_high: Upper band edge in Hz, inclusive.

    Returns:
        Total power in the band.
    """
    if f_low > f_high:
        raise ValueError(f"f_low ({f_low}) must not exceed f_high ({f_high})")

    freqs, amps = amplitude_spectrum(signal)
    mask = (freqs >= f_low) & (freqs <= f_high)
    # Convert single-sided amplitudes back to power: |A|^2 / 2 for each component.
    return float(np.sum(amps[mask] ** 2) / 2.0)
