from __future__ import annotations

import socket as _socket
import sys
from threading import Event, RLock, Thread
from typing import Any

_ACTIVE_DEVICE: Any | None = None
_TELEGRAF_SAMPLER: "_TelegrafSampler | None" = None
_TRIP_WATCHDOG: "TripWatchdog | None" = None

_CHANNEL_RESOURCE_RE_PATTERN = r"^slot:(\d+):ch:(\d+)$"


class TripWatchdog:
    """Monitor registered link groups and power off partners when one trips.

    CAEN-specific policy (Status bits, Pw, ramp/PDwn checks) layered on the
    generic devman-runtime registry and client leases. Runs server-side so
    linked channels stay protected even when the registering client is
    closed. Power-off bypasses ownership: off is the safe direction.
    """

    # Status bits per CAEN convention: 0 = ON, 6 = external trip, 8 = internal trip.
    ON_MASK = 1 << 0
    TRIP_MASK = (1 << 6) | (1 << 8)

    def __init__(
        self,
        device: Any,
        db: Any,
        interval_sec: float,
        is_client_live: Any | None = None,
        device_lock: Any | None = None,
    ) -> None:
        import re
        from threading import Lock

        self._device = device
        self._db = db
        self._interval_sec = float(interval_sec)
        self._is_client_live = is_client_live
        self._device_lock = device_lock if device_lock is not None else Lock()
        self._stop = Event()
        self._thread: Thread | None = None
        self._latched_groups: set[frozenset[tuple[int, int]]] = set()
        self._warned_unsync: set[tuple[str, int]] = set()
        self._resource_re = re.compile(_CHANNEL_RESOURCE_RE_PATTERN)

    def start(self) -> None:
        if self._thread is None:
            self._thread = Thread(target=self._loop, name="caenhv-trip-watchdog", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _log(self, message: str) -> None:
        from datetime import datetime

        ts = datetime.now().isoformat(timespec="seconds")
        print(f"[caenhv trip-watchdog {ts}] {message}", file=sys.stderr, flush=True)

    def _parse_members(self, resources: list[str]) -> list[tuple[int, int]]:
        members: list[tuple[int, int]] = []
        for resource in resources:
            match = self._resource_re.match(str(resource).strip())
            if match:
                members.append((int(match.group(1)), int(match.group(2))))
        return members

    def _read_status(self, slot: int, channel: int) -> int | None:
        try:
            with self._device_lock:
                values = self._device.get_ch_param(slot, [channel], "Status")
            return int(values[0])
        except Exception:
            return None

    def _power_off(self, slot: int, channel: int) -> bool:
        try:
            with self._device_lock:
                self._device.set_ch_param(slot, [channel], "Pw", 0)
            return True
        except Exception as exc:
            self._log(f"FAILED to power off {slot}:{channel}: {exc}")
            return False

    def _read_param_any(self, slot: int, channel: int, names: list[str]) -> Any | None:
        for name in names:
            try:
                with self._device_lock:
                    values = self._device.get_ch_param(slot, [channel], name)
                if isinstance(values, list) and values:
                    return values[0]
            except Exception:
                continue
        return None

    def _group_settings_synchronized(self, members: list[tuple[int, int]]) -> bool:
        """Same-name equality of RUp/RDWn plus PDwn match across the group.

        The registering client keeps mixed-polarity groups with all four ramp
        values equal, so same-name equality is a valid check for both group
        kinds. Unreadable values are treated as synchronized (cannot judge).
        """
        for names, numeric in ((["RUp", "RUP"], True), (["RDWn", "RDown", "RDWN"], True), (["PDwn", "PDWN"], False)):
            seen: set[Any] = set()
            for slot, channel in members:
                value = self._read_param_any(slot, channel, names)
                if value is None:
                    return True
                if numeric:
                    try:
                        value = round(float(value), 6)
                    except Exception:
                        return True
                else:
                    value = str(value).strip().lower()
                seen.add(value)
            if len(seen) > 1:
                return False
        return True

    def _janitor_group(self, client: str, group_idx: int, members: list[tuple[int, int]]) -> bool:
        """Apply stale-group rules to a group whose owner lease expired.

        Returns True when the group was removed. Energized groups are always
        kept: dropping protection from powered channels on inference is the
        wrong failure direction.
        """
        statuses: dict[tuple[int, int], int] = {}
        for slot, channel in members:
            status = self._read_status(slot, channel)
            if status is None:
                return False  # cannot judge: keep
            statuses[(slot, channel)] = status
        if any(status & (self.ON_MASK | self.TRIP_MASK) for status in statuses.values()):
            if not self._group_settings_synchronized(members):
                key = (client, int(group_idx))
                if key not in self._warned_unsync:
                    self._warned_unsync.add(key)
                    names = ", ".join(f"{s}:{c}" for s, c in sorted(members))
                    self._log(
                        f"WARNING: energized group [{names}] of stale client '{client}' has "
                        "unsynchronized settings; keeping protection"
                    )
            return False
        removed = self._db.remove_link_group(client, int(group_idx))
        if removed:
            names = ", ".join(f"{s}:{c}" for s, c in sorted(members))
            self._log(
                f"removed stale link group [{names}] of client '{client}': lease expired, all channels off"
            )
            self._latched_groups.discard(frozenset(members))
            self._warned_unsync.discard((client, int(group_idx)))
        return bool(removed)

    def _check_one_group(self, client: str, members: list[tuple[int, int]]) -> None:
        group_key = frozenset(members)
        statuses: dict[tuple[int, int], int] = {}
        for slot, channel in members:
            status = self._read_status(slot, channel)
            if status is not None:
                statuses[(slot, channel)] = status
        tripped = [key for key, status in statuses.items() if status & self.TRIP_MASK]
        if not tripped:
            self._latched_groups.discard(group_key)
            return
        if group_key in self._latched_groups:
            return
        self._latched_groups.add(group_key)
        powered_off: list[str] = []
        for slot, channel in sorted(members):
            if (slot, channel) in tripped:
                continue
            status = statuses.get((slot, channel))
            if status is None or not status & self.ON_MASK:
                continue
            if self._power_off(slot, channel):
                powered_off.append(f"{slot}:{channel}")
        tripped_names = ", ".join(f"{s}:{c}" for s, c in sorted(tripped))
        self._log(
            f"TRIP on {tripped_names} (group of client '{client}'); "
            f"powered off partners: {', '.join(powered_off) or 'none'}"
        )

    def check_groups_once(self) -> None:
        try:
            registered = self._db.link_groups_by_idx()
        except Exception as exc:
            self._log(f"failed to load link groups: {exc}")
            return
        for client, groups in registered.items():
            live = True
            if self._is_client_live is not None:
                try:
                    live = bool(self._is_client_live(client))
                except Exception:
                    live = True
            for group_idx, resources in sorted(groups.items()):
                members = self._parse_members(resources)
                if len(members) < 2:
                    continue
                if not live and self._janitor_group(client, group_idx, members):
                    continue
                self._check_one_group(client, members)

    def _loop(self) -> None:
        while not self._stop.wait(self._interval_sec):
            self.check_groups_once()


class _TelegrafSampler:
    """Sample all channel parameters and ship them to Telegraf.

    Runs its own thread inside the devman server process; reads go straight
    to the device singleton (the _AutoReconnectDevice lock serializes them
    against client requests). Interval is clamped to [1, 100] seconds.
    """

    MIN_INTERVAL_SEC = 1.0
    MAX_INTERVAL_SEC = 100.0

    # GUI-consistent field names for CAEN parameter names.
    _FIELD_ALIASES = {"v0set": "vset", "i0set": "iset", "rdown": "rdwn"}
    # Fields written as integers when numeric.
    _INT_FIELDS = {"status", "pw", "pon", "tripint", "tripext"}
    # Magnitude voltages displayed/logged signed on negative-polarity slots.
    _SIGNED_VOLTAGE_FIELDS = {"vset", "svmax", "vmon"}

    def __init__(
        self,
        device: Any,
        sender: Any,
        measurement: str,
        host_tag: str,
        interval_sec: float,
    ) -> None:
        self._device = device
        self._sender = sender
        self._measurement = str(measurement)
        self._host_tag = str(host_tag)
        self._interval_sec = min(self.MAX_INTERVAL_SEC, max(self.MIN_INTERVAL_SEC, float(interval_sec)))
        self._stop = Event()
        self._thread: Thread | None = None
        self._channels_by_slot: dict[int, int] = {}
        self._negative_by_slot: dict[int, bool] = {}
        self._params_by_slot: dict[int, list[str]] = {}
        self._last_error = ""

    @property
    def interval_sec(self) -> float:
        return self._interval_sec

    def start(self) -> None:
        if self._thread is None:
            self._thread = Thread(target=self._loop, name="caenhv-telegraf", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _log(self, message: str) -> None:
        print(f"[caenhv telegraf] {message}", file=sys.stderr, flush=True)

    @staticmethod
    def _board_name(board: Any) -> str:
        if isinstance(board, dict):
            for key in ("model", "name", "model_name", "description", "type"):
                value = board.get(key)
                if value is not None and str(value).strip():
                    return str(value)
            return "Board"
        return str(
            getattr(board, "model", None)
            or getattr(board, "name", None)
            or getattr(board, "model_name", None)
            or board.__class__.__name__
        )

    @staticmethod
    def _board_channels(board: Any) -> int:
        if isinstance(board, dict):
            for key in ("n_channel", "n_channels", "num_channels"):
                if key in board and board.get(key) is not None:
                    try:
                        return int(board.get(key))
                    except Exception:
                        return 0
            channels = board.get("channels")
            return len(channels) if isinstance(channels, list) else 0
        try:
            return int(getattr(board, "n_channel", 0) or 0)
        except Exception:
            return 0

    def _detect_negative(self, slot: int, board_name: str) -> bool:
        # Must mirror caenhv-client's heuristic exactly so logged signs
        # always agree with the GUI display.
        model = str(board_name).strip().upper()
        if model.endswith("DN") or (" DN" in model):
            return True
        try:
            prop = self._device.get_ch_param_prop(slot, 0, "V0Set")
        except Exception:
            return False
        if isinstance(prop, dict):
            minval, maxval = prop.get("minval"), prop.get("maxval")
        else:
            minval = getattr(prop, "minval", None)
            maxval = getattr(prop, "maxval", None)
        try:
            return minval is not None and maxval is not None and float(maxval) <= 0.0 and float(minval) < 0.0
        except Exception:
            return False

    def _scan_topology(self) -> None:
        crate_map = self._device.get_crate_map()
        channels: dict[int, int] = {}
        negative: dict[int, bool] = {}
        params: dict[int, list[str]] = {}
        for slot, board in enumerate(crate_map):
            if board is None:
                continue
            count = self._board_channels(board)
            if count <= 0:
                continue
            channels[int(slot)] = count
            negative[int(slot)] = self._detect_negative(int(slot), self._board_name(board))
            try:
                info = self._device.get_ch_param_info(int(slot), 0)
                params[int(slot)] = [str(n) for n in info] if isinstance(info, (list, tuple)) else []
            except Exception:
                params[int(slot)] = []
        self._channels_by_slot = channels
        self._negative_by_slot = negative
        self._params_by_slot = params

    def _field_for(self, param_name: str) -> str:
        lowered = str(param_name).lower()
        return self._FIELD_ALIASES.get(lowered, lowered)

    def _convert(self, field: str, value: Any, negative: bool) -> Any:
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, (int, float)):
            number = float(value)
            if field in self._SIGNED_VOLTAGE_FIELDS and negative:
                number = -abs(number)
            elif field == "imon":
                number = abs(number)
            elif field == "rup":
                # Signed slew convention: sign is the direction of signed-
                # voltage motion the parameter governs.
                number = -abs(number) if negative else abs(number)
            elif field == "rdwn":
                number = abs(number) if negative else -abs(number)
            if field in self._INT_FIELDS:
                return int(number)
            return number
        return str(value)

    def sample_once(self) -> list[str]:
        from devman_runtime.telegraf import build_line

        if not self._channels_by_slot:
            self._scan_topology()
        lines: list[str] = []
        for slot, count in sorted(self._channels_by_slot.items()):
            channel_list = list(range(count))
            negative = self._negative_by_slot.get(slot, False)
            try:
                labels = self._device.get_ch_name(slot, channel_list)
            except Exception:
                labels = [""] * count
            fields_by_channel: dict[int, dict[str, Any]] = {ch: {} for ch in channel_list}
            for param in self._params_by_slot.get(slot, []):
                try:
                    values = self._device.get_ch_param(slot, channel_list, param)
                except Exception:
                    continue
                if not isinstance(values, list):
                    continue
                field = self._field_for(param)
                for ch, value in zip(channel_list, values):
                    if value is None:
                        continue
                    fields_by_channel[ch][field] = self._convert(field, value, negative)
            for ch in channel_list:
                fields = fields_by_channel[ch]
                if not fields:
                    continue
                label = str(labels[ch]) if isinstance(labels, list) and ch < len(labels) else ""
                # Zero-pad slot/ch so Grafana's lexical tag sort orders them
                # numerically (00, 01, ... 10 instead of 0, 1, 10, 2).
                tags = {
                    "host": self._host_tag,
                    "slot": f"{int(slot):02d}",
                    "ch": f"{int(ch):02d}",
                    "name": label,
                }
                lines.append(build_line(self._measurement, tags, fields))
        return lines

    def _loop(self) -> None:
        while not self._stop.wait(self._interval_sec):
            try:
                lines = self.sample_once()
                if lines:
                    self._sender.send_lines(lines)
                if self._last_error:
                    self._log("recovered")
                    self._last_error = ""
            except Exception as exc:
                message = str(exc)
                if message != self._last_error:
                    self._log(f"sampling failed: {message}")
                    self._last_error = message
                self._channels_by_slot = {}  # rescan topology next cycle


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


def _pick_env(*keys: str, default: str | None = None) -> str | None:
    import os

    for key in keys:
        normalized = key.upper().replace("-", "_")
        candidates = [
            key,
            key.upper(),
            f"DEVMAN_{key.upper()}",
            f"DEVMAN_HOOK_ARG_{key.upper()}",
            normalized,
            f"DEVMAN_{normalized}",
            f"DEVMAN_HOOK_ARG_{normalized}",
        ]
        for env_key in candidates:
            value = os.getenv(env_key)
            if value is not None and str(value).strip() != "":
                return str(value)
    return default


def _pick_with_env(source: dict[str, str], *keys: str, default: str | None = None) -> str | None:
    """--hook-arg wins; otherwise fall back to environment variables."""
    value = _pick(source, *keys)
    if value is not None and str(value).strip() != "":
        return value
    return _pick_env(*keys, default=default)


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
        keepalive_sec: float,
    ) -> None:
        self._backend = backend
        self._system_type = system_type
        self._link_type = link_type
        self._address = address
        self._username = username
        self._password = password
        self._lock = RLock()
        self._dev = self._open_device()

        self._keepalive_sec = float(max(0.0, keepalive_sec))
        self._keepalive_stop = Event()
        self._keepalive_thread: Thread | None = None
        self._keepalive_method_name = self._pick_keepalive_method()
        if self._keepalive_sec > 0.0 and self._keepalive_method_name:
            self._keepalive_thread = Thread(target=self._keepalive_loop, daemon=True)
            self._keepalive_thread.start()

    def _open_device(self):
        return self._backend.Device.open(
            self._system_type,
            self._link_type,
            self._address,
            self._username,
            self._password,
        )

    def _pick_keepalive_method(self) -> str | None:
        for name in ("get_crate_map", "get_sys_prop_list", "get_exec_comm_list"):
            if callable(getattr(self._dev, name, None)):
                return name
        return None

    def _run_keepalive_once(self) -> None:
        method_name = self._keepalive_method_name
        if not method_name or self._dev is None:
            return
        method = getattr(self._dev, method_name, None)
        if not callable(method):
            return
        try:
            method()
            return
        except Exception as exc:
            if not _is_recoverable_connection_error(exc):
                return
            if self._reconnect_in_place():
                retry = getattr(self._dev, method_name, None)
                if callable(retry):
                    try:
                        retry()
                        return
                    except Exception:
                        pass
            try:
                self._reopen_device()
            except Exception:
                return

    def _keepalive_loop(self) -> None:
        while not self._keepalive_stop.wait(self._keepalive_sec):
            with self._lock:
                self._run_keepalive_once()

    def _reopen_device(self) -> None:
        # Open first, swap only on success so we never lose a potentially
        # still-usable existing handle when re-open fails.
        new_dev = self._open_device()
        old = self._dev
        self._dev = new_dev
        self._keepalive_method_name = self._pick_keepalive_method()
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
        self._keepalive_stop.set()
        if self._keepalive_thread is not None:
            self._keepalive_thread.join(timeout=2.0)
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

    address = _pick_with_env(opts, "address", "device_host", "arg", "device_ip", "crate_ip")
    if not address:
        raise ValueError("missing device address; pass --hook-arg address=<ip>")

    system_name = _pick_with_env(opts, "system_type", default="SY4527")
    link_name = _pick_with_env(opts, "link_type", default="TCPIP")
    username = _pick_with_env(opts, "username", default="") or ""
    password = _pick_with_env(opts, "password", default="") or ""
    keepalive_raw = _pick_with_env(opts, "keepalive_sec", default="10") or "10"
    try:
        keepalive_sec = float(keepalive_raw)
    except Exception:
        keepalive_sec = 10.0

    system_type = _resolve_enum(backend, "SystemType", system_name or "SY4527")
    link_type = _resolve_enum(backend, "LinkType", link_name or "TCPIP")

    _ACTIVE_DEVICE = _AutoReconnectDevice(
        backend=backend,
        system_type=system_type,
        link_type=link_type,
        address=address,
        username=username,
        password=password,
        keepalive_sec=keepalive_sec,
    )

    watchdog_raw = _pick_with_env(opts, "watchdog_interval_sec", default="0") or "0"
    try:
        watchdog_interval = float(watchdog_raw)
    except Exception:
        watchdog_interval = 0.0
    core = _kwargs.get("core")
    if watchdog_interval > 0.0:
        if core is None:
            print(
                "[caenhv trip-watchdog] disabled: devman-runtime does not expose "
                "the core to hooks (upgrade devman-runtime >= 0.2.0)",
                file=sys.stderr,
                flush=True,
            )
        else:
            global _TRIP_WATCHDOG
            _TRIP_WATCHDOG = TripWatchdog(
                device=_ACTIVE_DEVICE,
                db=core.db,
                interval_sec=watchdog_interval,
                is_client_live=core.is_client_live,
                device_lock=getattr(core, "_singleton_lock", None),
            )
            _TRIP_WATCHDOG.start()
            print(
                f"[caenhv trip-watchdog] started interval={watchdog_interval:.1f}s",
                file=sys.stderr,
                flush=True,
            )

    telegraf_url = _pick_with_env(opts, "telegraf_url")
    if telegraf_url:
        from devman_runtime.telegraf import TelegrafSender

        measurement = _pick_with_env(opts, "telegraf_measurement", default="caenhv") or "caenhv"
        host_tag = _pick_with_env(opts, "telegraf_host", default=_socket.gethostname()) or _socket.gethostname()
        interval_raw = _pick_with_env(opts, "telegraf_interval_sec", default="10") or "10"
        try:
            interval_sec = float(interval_raw)
        except Exception:
            interval_sec = 10.0
        global _TELEGRAF_SAMPLER
        _TELEGRAF_SAMPLER = _TelegrafSampler(
            device=_ACTIVE_DEVICE,
            sender=TelegrafSender(telegraf_url),
            measurement=measurement,
            host_tag=host_tag,
            interval_sec=interval_sec,
        )
        _TELEGRAF_SAMPLER.start()
        print(
            f"[caenhv telegraf] sampling every {_TELEGRAF_SAMPLER.interval_sec:.1f}s "
            f"-> {telegraf_url} measurement={measurement} host={host_tag}",
            file=sys.stderr,
            flush=True,
        )

    return _ACTIVE_DEVICE


def deinit(**_kwargs) -> None:
    global _ACTIVE_DEVICE, _TELEGRAF_SAMPLER, _TRIP_WATCHDOG
    watchdog = _TRIP_WATCHDOG
    _TRIP_WATCHDOG = None
    if watchdog is not None:
        watchdog.stop()
    sampler = _TELEGRAF_SAMPLER
    _TELEGRAF_SAMPLER = None
    if sampler is not None:
        sampler.stop()
    dev = _ACTIVE_DEVICE
    _ACTIVE_DEVICE = None
    if dev is None:
        return
    if hasattr(dev, "close"):
        dev.close()
