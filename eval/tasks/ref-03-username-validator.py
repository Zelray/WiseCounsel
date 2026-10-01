"""Reference solution for task 03 - T1-username-validator."""
import re

MIN_LENGTH = 3
MAX_LENGTH = 20
RESERVED_NAMES = {"admin", "administrator", "root", "moderator", "support", "system"}
_ALLOWED_CHARS = re.compile(r"\A[A-Za-z0-9_]+\Z")


def validate_username(username):
    """Return True only for a name the signup form may accept, else False."""
    if not isinstance(username, str):
        return False
    if username != username.strip():
        return False
    if not MIN_LENGTH <= len(username) <= MAX_LENGTH:
        return False
    if _ALLOWED_CHARS.match(username) is None:
        return False
    if not (username[0].isascii() and username[0].isalpha()):
        return False
    if username.lower() in RESERVED_NAMES:
        return False
    run_length = 1
    for previous, current in zip(username, username[1:]):
        run_length = run_length + 1 if previous == current else 1
        if run_length > 2:
            return False
    return True
