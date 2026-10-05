"""Reference solution for task 15 - T1-coupon-code."""
import re

CAMPAIGN_TAGS = ("SPR", "SUM", "FAL", "WIN")
FORBIDDEN_SUBSTRINGS = ("VOID", "FREE")
_BODY = re.compile(r"\A[A-Z0-9]{5}\Z")


def validate_coupon_code(code):
    """Raise ValueError unless the string is a coupon code this store issued."""
    if not isinstance(code, str):
        raise ValueError("invalid coupon code: expected text")
    if not code.strip():
        raise ValueError("empty coupon code")
    if len(code) != 9 or code[3] != "-":
        raise ValueError("invalid coupon code: expected tag-hyphen-body shape")
    tag, body = code[:3], code[4:]
    if tag not in CAMPAIGN_TAGS:
        raise ValueError("unknown campaign tag: %s" % tag)
    if _BODY.match(body) is None:
        raise ValueError("invalid coupon code: body must be caps and digits")
    for banned in FORBIDDEN_SUBSTRINGS:
        if banned in body:
            raise ValueError("reserved word %s is never issued" % banned)
    if not body[-1].isdigit():
        raise ValueError("invalid coupon code: body must end in a version digit")
    return True
