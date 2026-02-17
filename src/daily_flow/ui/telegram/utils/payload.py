import base64
import json
import os
import time
from typing import Any

_OPT_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_OPT_TTL_SEC = 15 * 60  # 15 хв

def _token(nbytes: int = 9) -> str:
    return base64.urlsafe_b64encode(os.urandom(nbytes)).decode("ascii").rstrip("=")

def _cache_set(val: dict[str, Any]) -> str:
    k = _token()
    _OPT_CACHE[k] = (time.time() + _OPT_TTL_SEC, val)
    return k

def _cache_get(k: str) -> dict[str, Any]:
    item = _OPT_CACHE.get(k)
    if not item:
        return {}
    exp, val = item
    if time.time() > exp:
        _OPT_CACHE.pop(k, None)
        return {}
    return val

def _cache_gc() -> None:
    now = time.time()
    dead = [k for k, (exp, _) in _OPT_CACHE.items() if exp < now]
    for k in dead:
        _OPT_CACHE.pop(k, None)

def pack_optional(data: dict[str, Any] | None) -> str:
    if not data:
        return ""

    _cache_gc()
    key = _cache_set(data)
    return f"k:{key}"

def unpack_optional(payload: str) -> dict[str, Any]:
    if not payload:
        return {}
    if payload.startswith("k:"):
        return _cache_get(payload[2:])

    raw = base64.urlsafe_b64decode(payload.encode("ascii"))
    return json.loads(raw.decode("utf-8"))
