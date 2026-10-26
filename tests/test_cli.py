from __future__ import annotations

import pytest

from myproject import __version__
from myproject.cli import main


def test_cli_slugifies_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Hello", "World"]) == 0
    assert capsys.readouterr().out == "hello-world\n"


def test_cli_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", _FakeStdin(["First Line\n", "\n", "Second Line\n"]))
    assert main([]) == 0
    assert capsys.readouterr().out == "first-line\nsecond-line\n"


def test_cli_prints_help_without_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", _FakeStdin([], tty=True))
    assert main([]) == 2
    assert "usage: myproject" in capsys.readouterr().err


def test_cli_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


class _FakeStdin:
    """Minimal stand-in for ``sys.stdin`` supporting iteration and ``isatty``."""

    def __init__(self, lines: list[str], tty: bool = False) -> None:
        self._lines = lines
        self._tty = tty

    def __iter__(self):
        return iter(self._lines)

    def isatty(self) -> bool:
        return self._tty
