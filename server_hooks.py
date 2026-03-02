from __future__ import annotations

from threading import RLock
from typing import Any

_ACTIVE_DEVICE: Any | None = None


def _parse_extra_args(extra_args: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    i = 0
    while i < len(extra_args):
        token = extra_args[i]
        if token.startswith("--"):
            key = token[2:]
            if "=" in key:
                k, v = key.split("=", 1)
                if k:
                    result[k] = v
            elif i + 1 < len(extra_args) and not extra_args[i + 1].startswith("--"):
                result[key] = extra_args[i + 1]
                i += 1
            else:
                result[key] = "true"
        i += 1
    return result


def _pick(source: dict[str, str], *keys: str, default: str | None = None) -> str | None:
    for key in keys:
        value = source.get(key)
        if value is not None and str(value).strip() != "":
            return str(value)
    return default


def _resolve_enum(module: Any, type_name: str, raw_value: str):
    enum_type = getattr(module, type_name)
    try:
        return enum_type[raw_value]
    except Exception:
        return enum_type(int(raw_value))


def _is_recoverable_connection_error(exc: Exception) -> bool:
    text = str(exc).strip().lower()
    if not text:
        return False
    return (
        ("cfe server down" in text)
        or ("server down" in text)
        or ("connection failed" in text)
        or ("notconnected" in text)
        or text.endswith("(down)")
        or text.endswith("(notconnected)")
        or (" down " in text)
    )


class _AutoReconnectDevice:
    def __init__(
        self,
        backend: Any,
        system_type: Any,
        link_type: Any,
        address: str,
        username: str,
        password: str,
    ) -> None:
        self._backend = backend
        self._system_type = system_type
        self._link_type = link_type
        self._address = address
        self._username = username
        self._password = password
        self._lock = RLock()
        self._dev = self._open_device()

    def _open_device(self):
        return self._backend.Device.open(
            self._system_type,
            self._link_type,
            self._address,
            self._username,
            self._password,
        )

    def _reopen_device(self) -> None:
        # Open first, swap only on success so we never lose a potentially
        # still-usable existing handle when re-open fails.
        new_dev = self._open_device()
        old = self._dev
        self._dev = new_dev
        try:
            if old is not None and hasattr(old, "close"):
                old.close()
        except Exception:
            pass

    def _reconnect_in_place(self) -> bool:
        dev = self._dev
        if dev is None:
            return False
        connect_fn = getattr(dev, "connect", None)
        if not callable(connect_fn):
            return False
        try:
            connect_fn()
            return True
        except Exception:
            return False

    def close(self) -> None:
        with self._lock:
            if self._dev is None:
                return
            try:
                if hasattr(self._dev, "close"):
                    self._dev.close()
            finally:
                self._dev = None

    def __getattr__(self, name: str):
        target = getattr(self._dev, name)
        if not callable(target):
            return target

        def _wrapped(*args, **kwargs):
            with self._lock:
                method = getattr(self._dev, name)
                try:
                    return method(*args, **kwargs)
                except Exception as exc:
                    if not _is_recoverable_connection_error(exc):
                        raise
                    if self._reconnect_in_place():
                        retry_method = getattr(self._dev, name)
                        return retry_method(*args, **kwargs)
                    try:
                        self._reopen_device()
                    except Exception:
                        # Preserve the original connection error context rather
                        # than masking it with a secondary re-open/auth error.
                        raise exc
                    retry_method = getattr(self._dev, name)
                    return retry_method(*args, **kwargs)

        return _wrapped


def init(backend, hook_args, extra_args, **_kwargs):
    global _ACTIVE_DEVICE
    if _ACTIVE_DEVICE is not None:
        return _ACTIVE_DEVICE

    parsed_extra = _parse_extra_args(list(extra_args))
    opts = {**parsed_extra, **dict(hook_args)}

    address = _pick(opts, "address", "arg", "device_ip", "crate_ip")
    if not address:
        raise ValueError("missing device address; pass --hook-arg address=<ip>")

    system_name = _pick(opts, "system_type", default="SY4527")
    link_name = _pick(opts, "link_type", default="TCPIP")
    username = _pick(opts, "username", default="") or ""
    password = _pick(opts, "password", default="") or ""

    system_type = _resolve_enum(backend, "SystemType", system_name or "SY4527")
    link_type = _resolve_enum(backend, "LinkType", link_name or "TCPIP")

    _ACTIVE_DEVICE = _AutoReconnectDevice(
        backend=backend,
        system_type=system_type,
        link_type=link_type,
        address=address,
        username=username,
        password=password,
    )
    return _ACTIVE_DEVICE


def deinit(**_kwargs) -> None:
    global _ACTIVE_DEVICE
    dev = _ACTIVE_DEVICE
    _ACTIVE_DEVICE = None
    if dev is None:
        return
    if hasattr(dev, "close"):
        dev.close()
