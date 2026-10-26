from __future__ import annotations

from pathlib import Path

import pytest

from signallab import __version__
from signallab.cli import main


def test_reports_peak_of_sine(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--type", "sine", "--freq", "50"]) == 0

    out = capsys.readouterr().out
    assert "peak freq   : 50.0 Hz" in out
    assert "peak ampl.  : 1.000" in out
    assert "samples     : 1000" in out


def test_reports_peak_of_square_wave(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--type", "square", "--freq", "40"]) == 0
    assert "peak freq   : 40.0 Hz" in capsys.readouterr().out


def test_writes_figure(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "nested" / "plot.png"

    assert main(["--freq", "50", "--out", str(target)]) == 0

    assert target.exists()
    assert target.stat().st_size > 1000  # a real PNG, not an empty file
    assert str(target) in capsys.readouterr().out


def test_adds_noise_without_breaking_peak_detection(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--freq", "50", "--snr", "20"]) == 0

    out = capsys.readouterr().out
    assert "SNR 20 dB" in out
    assert "peak freq   : 50.0 Hz" in out


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--freq", "0"], "freq must be positive"),
        (["--duration", "0"], "duration must be positive"),
    ],
)
def test_invalid_parameters_exit_nonzero(
    argv: list[str], message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(argv) == 1
    assert message in capsys.readouterr().err


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out
