from __future__ import annotations

import numpy as np
import pytest

from signallab import chirp, sine, square, with_white_noise
from signallab.signals import Signal


def test_time_axis_has_exact_sample_count() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0)
    assert len(signal) == 1000
    assert signal.duration == pytest.approx(1.0)
    assert signal.t[0] == 0.0
    assert signal.t[1] == pytest.approx(0.001)


def test_sine_matches_analytic_formula() -> None:
    signal = sine(freq=25.0, fs=1000.0, duration=0.5, amplitude=2.0)
    expected = 2.0 * np.sin(2 * np.pi * 25.0 * signal.t)
    np.testing.assert_allclose(signal.y, expected, atol=1e-12)


def test_sine_is_zero_mean_over_whole_periods() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0)
    assert abs(float(signal.y.mean())) < 1e-12


@pytest.mark.parametrize("freq", [0.0, -10.0])
def test_sine_rejects_non_positive_frequency(freq: float) -> None:
    with pytest.raises(ValueError, match="freq must be positive"):
        sine(freq=freq)


@pytest.mark.parametrize(("fs", "duration"), [(0.0, 1.0), (1000.0, 0.0), (10.0, 0.01)])
def test_generators_reject_bad_grid(fs: float, duration: float) -> None:
    with pytest.raises(ValueError, match="fs must be positive|duration must be positive|too short"):
        sine(freq=1.0, fs=fs, duration=duration)


def test_square_only_takes_two_values() -> None:
    signal = square(freq=10.0, fs=1000.0, duration=1.0, amplitude=3.0)
    assert set(np.unique(signal.y)) == {-3.0, 3.0}


def test_chirp_frequency_increases() -> None:
    signal = chirp(f_start=10.0, f_end=100.0, fs=1000.0, duration=1.0)
    # Zero crossings in the second half must outnumber those in the first half.
    crossings = np.flatnonzero(np.diff(np.signbit(signal.y)))
    midpoint = len(signal) // 2
    assert (crossings > midpoint).sum() > (crossings <= midpoint).sum()


def test_white_noise_reaches_target_snr() -> None:
    clean = sine(freq=50.0, fs=1000.0, duration=1.0)
    noisy = with_white_noise(clean, snr_db=20.0, seed=42)

    noise = noisy.y - clean.y
    measured_snr = 10 * np.log10(np.mean(clean.y**2) / np.mean(noise**2))
    assert measured_snr == pytest.approx(20.0, abs=1.0)


def test_white_noise_is_reproducible() -> None:
    clean = sine(freq=50.0, fs=1000.0, duration=0.1)
    first = with_white_noise(clean, snr_db=10.0, seed=7)
    second = with_white_noise(clean, snr_db=10.0, seed=7)
    np.testing.assert_array_equal(first.y, second.y)


def test_noise_rejects_silent_signal() -> None:
    silent = Signal(t=np.arange(10) / 1000.0, y=np.zeros(10), fs=1000.0)
    with pytest.raises(ValueError, match="all-zero"):
        with_white_noise(silent, snr_db=10.0)


def test_signal_validates_shape_and_length() -> None:
    with pytest.raises(ValueError, match="same shape"):
        Signal(t=np.zeros(10), y=np.zeros(5), fs=1000.0)
    with pytest.raises(ValueError, match="at least 2 samples"):
        Signal(t=np.zeros(1), y=np.zeros(1), fs=1000.0)
    with pytest.raises(ValueError, match="fs must be positive"):
        Signal(t=np.zeros(10), y=np.zeros(10), fs=0.0)
