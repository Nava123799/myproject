"""Core library functions.

This module holds the actual logic, kept free of any CLI or I/O concerns so it
can be imported and tested in isolation.
"""

from __future__ import annotations

import re
import unicodedata

_NON_WORD = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Turn arbitrary text into a lowercase, hyphen-separated URL slug.

    Accented characters are folded to their ASCII base (``café`` -> ``cafe``),
    runs of non-alphanumeric characters collapse into a single ``-``, and
    leading/trailing separators are stripped.

    Args:
        text: The text to convert.

    Returns:
        The slug, or an empty string if the input has no usable characters.

    Raises:
        TypeError: If ``text`` is not a string.

    Examples:
        >>> slugify("Hello, World!")
        'hello-world'
        >>> slugify("  Café  au   Lait  ")
        'cafe-au-lait'
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")

    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return _NON_WORD.sub("-", ascii_only.lower()).strip("-")
