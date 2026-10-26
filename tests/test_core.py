from __future__ import annotations

import pytest

from myproject import slugify


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello, World!", "hello-world"),
        ("  Café  au   Lait  ", "cafe-au-lait"),
        ("already-slugged", "already-slugged"),
        ("Multi\nLine\tText", "multi-line-text"),
        ("---leading and trailing---", "leading-and-trailing"),
        ("UPPER_case 123", "upper-case-123"),
        ("", ""),
        ("!!!", ""),
        ("中文标题", ""),
        ("naïve résumé", "naive-resume"),
    ],
)
def test_slugify(text: str, expected: str) -> None:
    assert slugify(text) == expected


def test_slugify_rejects_non_string() -> None:
    with pytest.raises(TypeError, match="text must be a str"):
        slugify(123)  # type: ignore[arg-type]
