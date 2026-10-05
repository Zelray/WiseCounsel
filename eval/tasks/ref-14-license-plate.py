"""Reference solution for task 14 - T1-license-plate."""
import re

# Letter positions exclude the stamped-metal confusables I, O, and Q.
_LETTERS = r"[A-HJ-NPR-Z]"
_MODERN = re.compile(r"\A" + _LETTERS + r"{3}[0-9]{4}\Z")
_VINTAGE = re.compile(r"\A" + _LETTERS + r"{2}[0-9]{4}\Z")
_RESERVED_PREFIXES = ("DP", "CX")


def is_valid_plate(plate):
    """Return True only for a passenger plate this state could have issued."""
    if not isinstance(plate, str):
        return False
    if plate != plate.strip():
        return False
    if _MODERN.match(plate) is None and _VINTAGE.match(plate) is None:
        return False
    if plate[:2] in _RESERVED_PREFIXES:
        return False
    return True
