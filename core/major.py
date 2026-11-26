"""
MajorLogin + MajorRegister
- major_register : set nickname di akun baru
- major_login    : ambil JWT token
"""
import os
import sys
import time
import requests
import urllib3
from datetime import datetime

# Proto path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "proto"))
import my_pb2       # noqa: E402
import output_pb2   # noqa: E402

from core.crypto   import encrypt_data, decrypt_data
from core.ip_pool  import random_ip
from utils.random_gen import random_device_id

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RELEASE_VER  = os.environ.get("RELEASE_VERSION", "OB55")
GAME_VERSION = os.environ.get("GAME_VERSION", "1.111.1")

URL_MAJOR_LOGIN    = "https://loginbp.ppmainecoonghj.com/MajorLogin"
URL_MAJOR_REGISTER = "https://loginbp.ppmainecoonghj.com/MajorRegister"

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "JP": "ja",
    "VN": "vi", "TH": "th", "BD": "bn", "PK": "ur",
    "TW": "zh", "CIS": "ru", "SAC": "es", "BR": "pt",
    "SG": "en", "US": "en", "EU": "en", "LK": "en",
}

_UNITY_HEADERS = {
    "User-Agent":      "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
    "Content-Type":    "application/octet-stream",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA":            "v1 1",
    "ReleaseVersion":  RELEASE_VER,
}


def _build_game_proto(access_token: str, open_id: str,
                      region: str, platform: int,
                      nickname: str = "") -> bytes:
    lang = REGION_LANG.get(region, "en")
    game = my_pb2.GameData()
    game.timestamp        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    game.game_name        = "free fire"
    game.game_version     = 1
    game.version_code     = GAME_VERSION
    game.os_info          = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
    game.device_type      = "Handheld"
    game.network_provider = "Verizon Wireless"
    game.connection_type  = "WIFI"
    game.screen_width     = 1280
    game.screen_height    = 960
    game.dpi              = "240"
    game.cpu_info         = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
    game.total_ram        = 5951
    game.gpu_name         = "Adreno (TM) 640"
    game.gpu_version      = "OpenGL ES 3.0"
    game.user_id          = f"Guest|{random_device_id()}"
    game.ip_address       = random_ip()
    game.language         = lang
    game.open_id          = open_id
    game.access_token     = access_token
    game.platform_type    = platform
    game.field_99         = str(platform)
    game.field_100        = str(platform)
    if nickname and hasattr(game, "nickname"):
        game.nickname = nickname
    return game.SerializeToString()


def major_register(access_token: str, open_id: str,
                   nickname: str, region: str = "ID") -> bool:
    """
    Set nickname akun baru via MajorRegister.
    Return True kalau berhasil, False kalau gagal (non-fatal).
    """
    try:
        raw  = _build_game_proto(access_token, open_id, region, 4, nickname)
        enc  = encrypt_data(raw)
        resp = requests.post(
            URL_MAJOR_REGISTER,
            data=enc,
            headers=_UNITY_HEADERS,
            verify=False,
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False


def major_login(access_token: str, open_id: str, region: str = "ID") -> str:
    """
    Coba platform 1-9, return JWT pertama yang valid.
    Raise Exception kalau semua platform gagal.
    """
    for platform in range(1, 10):
        try:
            raw  = _build_game_proto(access_token, open_id, region, platform)
            enc  = encrypt_data(raw)
            resp = requests.post(
                URL_MAJOR_LOGIN,
                data=enc,
                headers=_UNITY_HEADERS,
                verify=False,
                timeout=10,
            )
            if resp.status_code != 200:
                time.sleep(0.05)
                continue

            dec = decrypt_data(resp.content)

            # Coba protobuf parse dulu
            try:
                msg = output_pb2.Garena_420()
                msg.ParseFromString(dec)
                if msg.token:
                    return msg.token
            except Exception:
                pass

            # Fallback: scan raw bytes untuk "eyJ" (JWT header)
            text  = dec.decode("utf-8", errors="ignore")
            start = text.find("eyJ")
            if start != -1:
                end = start
                while end < len(text) and text[end] not in ['"', ' ', '\n', '\r', '\t', '\x00']:
                    end += 1
                candidate = text[start:end]
                if candidate.count(".") >= 2:
                    return candidate

        except Exception:
            pass

        time.sleep(0.05)

    raise Exception("MajorLogin: no JWT found after all platforms (1-9)")
