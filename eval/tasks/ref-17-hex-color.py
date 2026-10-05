"""Reference solution for task 17 - T1-hex-color."""
import re

_SHORT = re.compile(r"\A#([0-9A-Fa-f]{3})\Z")
_LONG = re.compile(r"\A#([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?\Z")
_RESERVED_TONES = {"000000", "FFFFFF"}
_DEGENERATE_ALPHA = ("00", "FF")


def is_valid_brand_color(color):
    """Return True only for a hex value the brand toolkit may ship."""
    if not isinstance(color, str):
        return False
    if color != color.strip():
        return False
    short = _SHORT.match(color)
    if short is not None:
        rgb = "".join(digit * 2 for digit in short.group(1))
        return rgb.upper() not in _RESERVED_TONES
    long = _LONG.match(color)
    if long is None:
        return False
    rgb, alpha = long.group(1), long.group(2)
    if rgb.upper() in _RESERVED_TONES:
        return False
    if alpha is not None and alpha.upper() in _DEGENERATE_ALPHA:
        return False
    return True
