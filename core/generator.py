"""
Core pipeline — satu fungsi generate_guest_account() menggabungkan semua step:
  1. Garena guest:register  → uid + garena_pass + AT + open_id
  2. token_grant jika AT kosong
  3. inspect_token jika open_id kosong
  4. MajorRegister          → set nickname
  5. MajorLogin             → JWT
  6. Rarity scoring
  7. Build result dict
"""
import time
from datetime import datetime, timezone

from core.garena    import guest_register, token_grant, inspect_token
from core.major     import major_register, major_login
from core.rarity    import compute_rarity, extract_jwt_meta
from utils.random_gen import random_password, random_nickname

DEFAULT_REGION      = "ID"
DEFAULT_NAME_PREFIX = ""


def generate_guest_account(
    region:      str = DEFAULT_REGION,
    name_prefix: str = DEFAULT_NAME_PREFIX,
) -> dict:
    """
    Full pipeline — buat satu akun guest FF baru.
    Return dict siap JSON (format identik dengan contoh output).
    """
    t0 = time.perf_counter()

    # ── Step 1: Garena register ──────────────────────────────────────
    reg       = guest_register(region)
    uid       = reg["uid"]
    g_pass    = reg["password"]
    at        = reg["access_token"]
    open_id   = reg["open_id"]

    # ── Step 2: Fallback grant jika AT kosong ────────────────────────
    if not at:
        grant   = token_grant(uid, g_pass)
        at      = grant["access_token"]
        open_id = grant["open_id"]

    # ── Step 3: Fallback inspect jika open_id kosong ─────────────────
    if not open_id:
        open_id = inspect_token(at)

    # ── Step 4: Custom password + nickname ───────────────────────────
    custom_pass = random_password(uid)
    nickname    = random_nickname(prefix=name_prefix, total_length=8)

    # ── Step 5: MajorRegister (set nickname, best-effort) ────────────
    major_register(at, open_id, nickname, region)

    # ── Step 6: MajorLogin → JWT ─────────────────────────────────────
    jwt_token = major_login(at, open_id, region)

    # ── Step 7: Rarity + JWT meta ────────────────────────────────────
    rarity_score, rarity_name, rarity_reason = compute_rarity(jwt_token)
    meta = extract_jwt_meta(jwt_token)

    account_id    = meta["account_id"] or uid
    name_resolved = meta["nickname"]   or nickname
    is_ghost      = meta["is_ghost"]

    # Unik label logic (bisa dikembangkan)
    is_unik    = rarity_score >= 50
    unik_label = rarity_name if is_unik else ""

    elapsed = round(time.perf_counter() - t0, 2)

    return {
        "access_token":  at,
        "account_id":    account_id,
        "created_at":    datetime.now(timezone.utc).isoformat(),
        "is_ghost":      is_ghost,
        "is_unik":       is_unik,
        "jwt_token":     jwt_token,
        "name":          name_resolved,
        "open_id":       open_id,
        "password":      custom_pass,
        "rarity":        rarity_name,
        "rarity_reason": rarity_reason,
        "rarity_score":  rarity_score,
        "region":        region,
        "status":        "success",
        "uid":           uid,
        "unik_label":    unik_label,
        "_elapsed_sec":  elapsed,  # internal, strip sebelum response
    }
