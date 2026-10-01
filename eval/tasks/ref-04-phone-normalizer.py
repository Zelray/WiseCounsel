"""Reference solution for task 04 - T1-phone-normalizer."""
import re

_EXTENSION = re.compile(r"(?is)(?:^|\s)(?:x|ext)\.?\s*(\d*)\s*$")
_NON_DIGIT = re.compile(r"\D")
_LETTER = re.compile(r"[A-Za-z]")
_MIN_DIGITS = 10
_MAX_DIGITS = 11


def normalize_phone(raw):
    """Return the canonical form of a user-typed phone number, or raise ValueError."""
    if not isinstance(raw, str) or raw.strip() == "":
        raise ValueError("empty")

    text = raw.strip()
    extension = None
    ext_match = _EXTENSION.search(text)
    if ext_match:
        ext_digits = ext_match.group(1)
        if not 1 <= len(ext_digits) <= 5:
            raise ValueError("bad extension")
        extension = ext_digits
        text = text[:ext_match.start()]

    if _LETTER.search(text):
        raise ValueError("letters not allowed")

    digits = _NON_DIGIT.sub("", text)
    if digits == "":
        raise ValueError("empty")

    if len(digits) == _MAX_DIGITS and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) < _MIN_DIGITS:
        raise ValueError("too short")
    if len(digits) > _MIN_DIGITS:
        raise ValueError("too long")

    formatted = "({}) {}-{}".format(digits[0:3], digits[3:6], digits[6:10])
    if extension:
        formatted += ", ext. " + extension
    return formatted
