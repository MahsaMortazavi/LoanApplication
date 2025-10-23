import hmac, os, re
from hashlib import sha256
from cryptography.fernet import Fernet, InvalidToken

SSN_ENC_KEY_ENV  = "SSN_ENC_KEY"   # 32-byte urlsafe base64 key (Fernet)
SSN_HASH_KEY_ENV = "SSN_HASH_KEY"  # HMAC key (arbitrary bytes)

_ssn_fernet = None
_hash_key = None

SSN_RE = re.compile(r"^\d{9}$|^\d{3}-\d{2}-\d{4}$")

def _normalize_ssn(ssn: str) -> str:
    # remove dashes/spaces so formats compare the same
    s = re.sub(r"[-\s]", "", ssn)
    if not re.fullmatch(r"\d{9}", s):
        raise ValueError("Invalid SSN format")
    return s

def _get_fernet() -> Fernet:
    global _ssn_fernet
    if _ssn_fernet is None:
        key = os.environ.get(SSN_ENC_KEY_ENV)
        if not key:
            raise RuntimeError(f"Missing env {SSN_ENC_KEY_ENV}")
        _ssn_fernet = Fernet(key.encode("utf-8"))
    return _ssn_fernet

def _get_hash_key() -> bytes:
    global _hash_key
    if _hash_key is None:
        k = os.environ.get(SSN_HASH_KEY_ENV)
        if not k:
            raise RuntimeError(f"Missing env {SSN_HASH_KEY_ENV}")
        _hash_key = k.encode("utf-8")
    return _hash_key

def hash_ssn(ssn: str) -> str:
    s = _normalize_ssn(ssn)
    hk = _get_hash_key()
    mac = hmac.new(hk, s.encode("utf-8"), sha256).hexdigest()  # 64 hex chars
    return mac

def encrypt_ssn(ssn: str) -> str:
    s = _normalize_ssn(ssn)
    f = _get_fernet()
    token = f.encrypt(s.encode("utf-8"))  # bytes
    return token.decode("utf-8")          # store as text
