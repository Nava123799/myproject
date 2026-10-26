from __future__ import annotations

import pytest

from signallab import amplitude_spectrum, dominant_frequency, sine
from signallab.spectrum import band_power, peak_amplitude


def test_spectrum_length_and_axis_range() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0)
    freqs, amps = amplitude_spectrum(signal)

    assert len(freqs) == len(signal) // 2 + 1
    assert freqs[0] == 0.0
    assert freqs[-1] == pytest.approx(signal.fs / 2.0)
    assert len(amps) == len(freqs)


def test_sine_peak_frequency_and_amplitude() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0, amplitude=2.5)

    assert dominant_frequency(signal, min_freq=1.0) == pytest.approx(50.0)
    assert peak_amplitude(signal, min_freq=1.0) == pytest.approx(2.5, rel=1e-6)


@pytest.mark.parametrize("freq", [10.0, 50.0, 125.0, 250.0])
def test_peak_detection_is_exact_on_bin_centres(freq: float) -> None:
    signal = sine(freq=freq, fs=1000.0, duration=1.0)
    assert dominant_frequency(signal, min_freq=1.0) == pytest.approx(freq)


def test_dc_offset_does_not_leak_into_spectrum() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0)
    with_offset = type(signal)(t=signal.t, y=signal.y + 5.0, fs=signal.fs, name="offset")

    freqs, amps = amplitude_spectrum(with_offset)
    assert amps[0] < 1e-9  # mean removed, so the DC bin collapses


def test_dc_bin_kept_when_asked() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0)
    with_offset = type(signal)(t=signal.t, y=signal.y + 5.0, fs=signal.fs, name="offset")

    _, amps = amplitude_spectrum(with_offset, remove_dc=False)
    assert amps[0] == pytest.approx(5.0, rel=1e-6)


def test_band_power_of_pure_sine_is_half_amplitude_squared() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0, amplitude=2.0)

    power = band_power(signal, f_low=40.0, f_high=60.0)
    assert power == pytest.approx(2.0**2 / 2.0, rel=1e-6)


def test_band_power_excludes_out_of_band_energy() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=1.0)

    assert band_power(signal, f_low=200.0, f_high=300.0) == pytest.approx(0.0, abs=1e-9)


def test_band_power_rejects_inverted_band() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=0.1)
    with pytest.raises(ValueError, match="must not exceed"):
        band_power(signal, f_low=100.0, f_high=10.0)


def test_dominant_frequency_returns_zero_when_no_bin_qualifies() -> None:
    signal = sine(freq=50.0, fs=1000.0, duration=0.1)
    assert dominant_frequency(signal, min_freq=1e9) == 0.0
