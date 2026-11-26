"""
Random generators — password, nickname, device_id
"""
import random
import string
import hashlib
import time

PASS_PREFIX = "Dbeckkz1a"


def random_password(uid: str = "") -> str:
    """
    Format: Dbeckkz1a_{md5(uid+timestamp+random)}
    Contoh: Dbeckkz1a_733e5b9363d772a61045fb2e10f87d7a
    """
    seed   = f"{uid}{time.time()}{random.random()}"
    suffix = hashlib.md5(seed.encode()).hexdigest()
    return f"{PASS_PREFIX}_{suffix}"


def random_nickname(prefix: str = "", total_length: int = 8) -> str:
    """
    Alphanum 8 char, mix upper+lower+digit.
    Contoh: rYLTHvzP
    """
    chars     = string.ascii_letters + string.digits
    remaining = max(1, total_length - len(prefix))
    body      = "".join(random.choices(chars, k=remaining))
    return (prefix + body)[:total_length]


def random_device_id() -> str:
    """32 hex char lowercase."""
    return "".join(random.choices("0123456789abcdef", k=32))


def random_external_uid() -> str:
    return str(random.randint(1_000_000_000, 9_999_999_999))
