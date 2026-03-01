from __future__ import annotations

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

    # CAEN Device.open() already establishes the connection for this backend.
    # Calling connect() again may raise an "already connected" error.
    dev = backend.Device.open(system_type, link_type, address, username, password)
    _ACTIVE_DEVICE = dev
    return dev


def deinit(**_kwargs) -> None:
    global _ACTIVE_DEVICE
    dev = _ACTIVE_DEVICE
    _ACTIVE_DEVICE = None
    if dev is None:
        return
    if hasattr(dev, "close"):
        dev.close()
