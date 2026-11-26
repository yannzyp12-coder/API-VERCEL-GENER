"""
AES-128-CBC encrypt/decrypt
Key + IV hardcoded sesuai FF client
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69,
                 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50,
                 69, 51, 121, 99, 104, 106, 77, 37])


def encrypt_data(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))


def decrypt_data(data: bytes) -> bytes:
    if len(data) % 16 != 0:
        return data
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        return unpad(cipher.decrypt(data), AES.block_size)
    except Exception:
        return data
