"""Reference solution for task 16 - T1-postal-code."""
import re

_MARKETS = {
    "NV": re.compile(r"\A[0-9]{4} [A-Z]{2}\Z"),
    "KE": re.compile(r"\A[A-Z]{2}-[1-9][0-9]{3}\Z"),
    "ZR": re.compile(r"\A[1-6][0-9]{5}\Z"),
}
_NV_TERRITORY_OPENINGS = ("Q", "X")


def is_valid_postal_code(code, country):
    """Return True only for a well-formed postal code in one of our markets."""
    if not isinstance(code, str) or not isinstance(country, str):
        return False
    market = _MARKETS.get(country.upper())
    if market is None:
        return False
    if code != code.strip():
        return False
    if market.match(code) is None:
        return False
    if country.upper() == "NV" and code[5] in _NV_TERRITORY_OPENINGS:
        return False
    return True
