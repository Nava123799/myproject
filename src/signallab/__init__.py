"""signallab - a small digital-signal-processing toolkit.

The public API is deliberately narrow: signal generation, spectrum analysis and
plotting. Nothing here touches the filesystem, so every function is trivially
testable.
"""

from __future__ import annotations

from signallab.signals import Signal, chirp, sine, square, with_white_noise
from signallab.spectrum import amplitude_spectrum, dominant_frequency

__version__ = "0.2.0"

__all__ = [
    "Signal",
    "__version__",
    "amplitude_spectrum",
    "chirp",
    "dominant_frequency",
    "sine",
    "square",
    "with_white_noise",
]
