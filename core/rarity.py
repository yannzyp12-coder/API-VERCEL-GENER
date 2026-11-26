"""
Rarity scoring dari JWT payload
LEGENDARY / EPIC / RARE / UNCOMMON / COMMON
"""
import base64
import json

_TABLE = [
    (90, "LEGENDARY", "Score:90+"),
    (70, "EPIC",      "Score:70+"),
    (50, "RARE",      "Score:50+"),
    (30, "UNCOMMON",  "Score:30+"),
    (0,  "COMMON",    "Score:0"),
]


def _decode_payload(jwt_token: str) -> dict:
    try:
        part    = jwt_token.split(".")[1]
        padding = 4 - len(part) % 4
        padded  = part + ("=" * (padding % 4))
        return json.loads(base64.b64decode(padded).decode("utf-8", errors="ignore"))
    except Exception:
        return {}


def compute_rarity(jwt_token: str) -> tuple:
    """
    Return: (score: int, rarity: str, reason: str)
    """
    payload = _decode_payload(jwt_token)
    score   = 0

    # Avatar score
    avatar = payload.get("reg_avatar", 0)
    if avatar > 102000010:
        score += 40
    elif avatar > 102000005:
        score += 20
    else:
        score += 5

    # Emulator penalty
    if payload.get("is_emulator", False):
        score -= 20

    # Country bonus
    cc = payload.get("country_code", "")
    if cc in ("JP", "US", "SG"):
        score += 30
    elif cc in ("EU", "TW", "CIS"):
        score += 15

    # Lock region bonus
    if payload.get("lock_region"):
        score += 10

    score = max(0, min(score, 100))

    rarity_name   = "COMMON"
    rarity_reason = "Score:0"
    for threshold, name, reason in _TABLE:
        if score >= threshold:
            rarity_name   = name
            rarity_reason = reason
            break

    return score, rarity_name, rarity_reason


def decode_nickname(raw: str) -> str:
    """
    Nickname dari JWT kadang base64-encoded.
    Decode kalau bisa, fallback ke raw.
    """
    try:
        padding = 4 - len(raw) % 4
        decoded = base64.b64decode(raw + "=" * (padding % 4)).decode("utf-8", errors="ignore")
        if decoded.isprintable() and len(decoded) >= 2:
            return decoded
    except Exception:
        pass
    return raw


def extract_jwt_meta(jwt_token: str) -> dict:
    """
    Ambil metadata penting dari JWT payload.
    Return dict: { account_id, nickname, country_code, is_ghost, lock_region, reg_avatar }
    """
    payload = _decode_payload(jwt_token)
    return {
        "account_id":   str(payload.get("account_id", "")),
        "nickname":     decode_nickname(payload.get("nickname", "")),
        "country_code": payload.get("country_code", ""),
        "is_ghost":     payload.get("is_ghost", False),
        "lock_region":  payload.get("lock_region", ""),
        "reg_avatar":   payload.get("reg_avatar", 0),
    }
