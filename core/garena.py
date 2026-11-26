"""
Garena OAuth API
- guest_register  : buat akun guest BARU (grant_type=guest)
- token_grant     : ambil AT dari uid+password existing
- inspect_token   : resolve open_id dari AT
"""
import requests
import urllib3
from utils.random_gen import random_device_id

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLIENT_ID     = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

URL_GUEST_REGISTER = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
URL_TOKEN_GRANT    = "https://100067.connect.garena.com/oauth/guest/token:grant"
URL_INSPECT        = "https://100067.connect.garena.com/oauth/token/inspect"

_HEADERS = {
    "User-Agent":   "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
    "Content-Type": "application/x-www-form-urlencoded",
}


def guest_register(region: str = "ID") -> dict:
    """
    Buat akun guest baru via Garena.
    Return dict: { uid, password, access_token, open_id }
    """
    payload = {
        "device_id":     random_device_id(),
        "response_type": "token",
        "client_type":   "2",
        "client_secret": CLIENT_SECRET,
        "client_id":     CLIENT_ID,
        "region":        region,
    }
    resp = requests.post(
        URL_GUEST_REGISTER,
        data=payload,
        headers=_HEADERS,
        timeout=20,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception(
            f"guest_register failed [{resp.status_code}]: {resp.text[:300]}"
        )
    data = resp.json()
    if data.get("error") or data.get("error_code"):
        raise Exception(f"guest_register error: {data}")

    return {
        "uid":          str(data.get("uid") or data.get("user_id", "")),
        "password":     data.get("password") or data.get("credential", ""),
        "access_token": data.get("access_token", ""),
        "open_id":      data.get("open_id", ""),
    }


def token_grant(uid: str, password: str) -> dict:
    """
    Login guest existing — uid + password → access_token + open_id.
    """
    payload = {
        "uid":           uid,
        "password":      password,
        "response_type": "token",
        "client_type":   "2",
        "client_secret": CLIENT_SECRET,
        "client_id":     CLIENT_ID,
    }
    resp = requests.post(
        URL_TOKEN_GRANT,
        data=payload,
        headers=_HEADERS,
        timeout=20,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception(
            f"token_grant failed [{resp.status_code}]: {resp.text[:300]}"
        )
    data = resp.json()
    return {
        "access_token": data.get("access_token", ""),
        "open_id":      data.get("open_id", ""),
    }


def inspect_token(access_token: str) -> str:
    """Resolve open_id dari access_token."""
    url  = f"{URL_INSPECT}?token={access_token}"
    resp = requests.get(
        url,
        headers={"User-Agent": "GarenaMSDK/4.0.19P9"},
        timeout=10,
        verify=False,
    )
    return resp.json().get("open_id", "")
