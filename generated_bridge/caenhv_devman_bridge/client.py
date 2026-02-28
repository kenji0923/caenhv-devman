from __future__ import annotations

import os
from typing import Any

from devman_gen.runtime.client import ManagerClient

try:
    from caen_libs.caenhvwrapper import *
    from caen_libs._caenhvwrappertypes import *
    from caen_libs.caenhvwrapperflags import *
except Exception:
    pass

_PARAM_ORDER = { 'Device_close': [],
  'Device_connect': [],
  'Device_device_closed': [],
  'Device_exec_comm': ['name'],
  'Device_get_bd_param': ['slot_list', 'name'],
  'Device_get_bd_param_info': ['slot'],
  'Device_get_bd_param_prop': ['slot', 'name'],
  'Device_get_ch_name': ['slot', 'channel_list'],
  'Device_get_ch_param': ['slot', 'channel_list', 'name'],
  'Device_get_ch_param_info': ['slot', 'channel'],
  'Device_get_ch_param_prop': ['slot', 'channel', 'name'],
  'Device_get_crate_map': [],
  'Device_get_event_data': [],
  'Device_get_events_tcp_ports': [],
  'Device_get_exec_comm_list': [],
  'Device_get_sys_prop': ['name'],
  'Device_get_sys_prop_info': ['name'],
  'Device_get_sys_prop_list': [],
  'Device_open': ['system_type', 'link_type', 'arg', 'username', 'password'],
  'Device_set_bd_param': ['slot_list', 'name', 'value'],
  'Device_set_ch_name': ['slot', 'channel_list', 'name'],
  'Device_set_ch_param': ['slot', 'channel_list', 'name', 'value'],
  'Device_set_events_tcp_ports': ['first', 'last'],
  'Device_set_sys_prop': ['name', 'value'],
  'Device_subscribe_board_params': ['slot', 'param_list'],
  'Device_subscribe_channel_params': ['slot', 'channel', 'param_list'],
  'Device_subscribe_system_params': ['param_list'],
  'Device_test_bd_presence': ['slot'],
  'Device_unsubscribe_board_params': ['slot', 'param_list'],
  'Device_unsubscribe_channel_params': ['slot', 'channel', 'param_list'],
  'Device_unsubscribe_system_params': ['param_list'],
  'Error_Code': ['values']}
_PARAM_KINDS = { 'Device_close': {},
  'Device_connect': {},
  'Device_device_closed': {},
  'Device_exec_comm': {'name': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_bd_param': { 'name': 'POSITIONAL_OR_KEYWORD',
                           'slot_list': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_bd_param_info': {'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_bd_param_prop': { 'name': 'POSITIONAL_OR_KEYWORD',
                                'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_ch_name': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                          'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_ch_param': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                           'name': 'POSITIONAL_OR_KEYWORD',
                           'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_ch_param_info': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_ch_param_prop': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                'name': 'POSITIONAL_OR_KEYWORD',
                                'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_crate_map': {},
  'Device_get_event_data': {},
  'Device_get_events_tcp_ports': {},
  'Device_get_exec_comm_list': {},
  'Device_get_sys_prop': {'name': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_sys_prop_info': {'name': 'POSITIONAL_OR_KEYWORD'},
  'Device_get_sys_prop_list': {},
  'Device_open': { 'arg': 'POSITIONAL_OR_KEYWORD',
                   'link_type': 'POSITIONAL_OR_KEYWORD',
                   'password': 'POSITIONAL_OR_KEYWORD',
                   'system_type': 'POSITIONAL_OR_KEYWORD',
                   'username': 'POSITIONAL_OR_KEYWORD'},
  'Device_set_bd_param': { 'name': 'POSITIONAL_OR_KEYWORD',
                           'slot_list': 'POSITIONAL_OR_KEYWORD',
                           'value': 'POSITIONAL_OR_KEYWORD'},
  'Device_set_ch_name': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                          'name': 'POSITIONAL_OR_KEYWORD',
                          'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_set_ch_param': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                           'name': 'POSITIONAL_OR_KEYWORD',
                           'slot': 'POSITIONAL_OR_KEYWORD',
                           'value': 'POSITIONAL_OR_KEYWORD'},
  'Device_set_events_tcp_ports': { 'first': 'POSITIONAL_OR_KEYWORD',
                                   'last': 'POSITIONAL_OR_KEYWORD'},
  'Device_set_sys_prop': { 'name': 'POSITIONAL_OR_KEYWORD',
                           'value': 'POSITIONAL_OR_KEYWORD'},
  'Device_subscribe_board_params': { 'param_list': 'POSITIONAL_OR_KEYWORD',
                                     'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_subscribe_channel_params': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                       'param_list': 'POSITIONAL_OR_KEYWORD',
                                       'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_subscribe_system_params': {'param_list': 'POSITIONAL_OR_KEYWORD'},
  'Device_test_bd_presence': {'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_unsubscribe_board_params': { 'param_list': 'POSITIONAL_OR_KEYWORD',
                                       'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_unsubscribe_channel_params': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                         'param_list': 'POSITIONAL_OR_KEYWORD',
                                         'slot': 'POSITIONAL_OR_KEYWORD'},
  'Device_unsubscribe_system_params': {'param_list': 'POSITIONAL_OR_KEYWORD'},
  'Error_Code': {'values': 'VAR_POSITIONAL'}}
_RESOURCE_TEMPLATES = { 'Device_close': None,
  'Device_connect': None,
  'Device_device_closed': None,
  'Device_exec_comm': 'name:{name}',
  'Device_get_bd_param': 'slot_list:{slot_list}',
  'Device_get_bd_param_info': 'slot:{slot}',
  'Device_get_bd_param_prop': 'slot:{slot}',
  'Device_get_ch_name': 'slot:{slot}',
  'Device_get_ch_param': 'slot:{slot}',
  'Device_get_ch_param_info': 'slot:{slot}',
  'Device_get_ch_param_prop': 'slot:{slot}',
  'Device_get_crate_map': None,
  'Device_get_event_data': None,
  'Device_get_events_tcp_ports': None,
  'Device_get_exec_comm_list': None,
  'Device_get_sys_prop': 'name:{name}',
  'Device_get_sys_prop_info': 'name:{name}',
  'Device_get_sys_prop_list': None,
  'Device_open': 'system_type:{system_type}',
  'Device_set_bd_param': 'slot_list:{slot_list}',
  'Device_set_ch_name': 'slot:{slot}',
  'Device_set_ch_param': 'slot:{slot}',
  'Device_set_events_tcp_ports': 'first:{first}',
  'Device_set_sys_prop': 'name:{name}',
  'Device_subscribe_board_params': 'slot:{slot}',
  'Device_subscribe_channel_params': 'slot:{slot}',
  'Device_subscribe_system_params': 'param_list:{param_list}',
  'Device_test_bd_presence': 'slot:{slot}',
  'Device_unsubscribe_board_params': 'slot:{slot}',
  'Device_unsubscribe_channel_params': 'slot:{slot}',
  'Device_unsubscribe_system_params': 'param_list:{param_list}',
  'Error_Code': None}

_CLIENT = ManagerClient(
    host=os.getenv("DEVMAN_HOST", "127.0.0.1"),
    port=int(os.getenv("DEVMAN_PORT", "50250")),
    client_name=os.getenv("DEVMAN_CLIENT", "anonymous"),
)


def configure_connection(host: str, port: int, client_name: str, timeout: float = 5.0) -> None:
    global _CLIENT
    _CLIENT = ManagerClient(host=host, port=port, client_name=client_name, timeout=timeout)


def acquire(resource: str) -> bool:
    return _CLIENT.acquire(resource)


def release(resource: str) -> bool:
    return _CLIENT.release(resource)


def _pack_call_args(function: str, local_vars: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    order = _PARAM_ORDER[function]
    kinds = _PARAM_KINDS[function]
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    for name in order:
        if name not in local_vars or name in ('self', 'cls'):
            continue
        kind = kinds.get(name, 'POSITIONAL_OR_KEYWORD')
        value = local_vars[name]
        if kind == 'VAR_POSITIONAL':
            args.extend(list(value))
        elif kind == 'VAR_KEYWORD':
            kwargs.update(dict(value))
        elif kind == 'KEYWORD_ONLY':
            kwargs[name] = value
        else:
            args.append(value)
    return args, kwargs


def _resources_for(function: str, local_vars: dict[str, Any]) -> list[str]:
    template = _RESOURCE_TEMPLATES.get(function)
    if not template:
        return []
    context = dict(local_vars)
    context.pop('kwargs', None)
    return [template.format(**context)]


def Device_close():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_close", _locals)
    _resources = _resources_for("Device_close", _locals)
    return _CLIENT.invoke("Device_close", _args, _kwargs, _resources)

def Device_connect():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_connect", _locals)
    _resources = _resources_for("Device_connect", _locals)
    return _CLIENT.invoke("Device_connect", _args, _kwargs, _resources)

def Device_device_closed():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_device_closed", _locals)
    _resources = _resources_for("Device_device_closed", _locals)
    return _CLIENT.invoke("Device_device_closed", _args, _kwargs, _resources)

def Device_exec_comm(name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_exec_comm", _locals)
    _resources = _resources_for("Device_exec_comm", _locals)
    return _CLIENT.invoke("Device_exec_comm", _args, _kwargs, _resources)

def Device_get_bd_param(slot_list: collections.abc.Sequence[int], name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_bd_param", _locals)
    _resources = _resources_for("Device_get_bd_param", _locals)
    return _CLIENT.invoke("Device_get_bd_param", _args, _kwargs, _resources)

def Device_get_bd_param_info(slot: int):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_bd_param_info", _locals)
    _resources = _resources_for("Device_get_bd_param_info", _locals)
    return _CLIENT.invoke("Device_get_bd_param_info", _args, _kwargs, _resources)

def Device_get_bd_param_prop(slot: int, name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_bd_param_prop", _locals)
    _resources = _resources_for("Device_get_bd_param_prop", _locals)
    return _CLIENT.invoke("Device_get_bd_param_prop", _args, _kwargs, _resources)

def Device_get_ch_name(slot: int, channel_list: collections.abc.Sequence[int]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_ch_name", _locals)
    _resources = _resources_for("Device_get_ch_name", _locals)
    return _CLIENT.invoke("Device_get_ch_name", _args, _kwargs, _resources)

def Device_get_ch_param(slot: int, channel_list: collections.abc.Sequence[int], name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_ch_param", _locals)
    _resources = _resources_for("Device_get_ch_param", _locals)
    return _CLIENT.invoke("Device_get_ch_param", _args, _kwargs, _resources)

def Device_get_ch_param_info(slot: int, channel: int):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_ch_param_info", _locals)
    _resources = _resources_for("Device_get_ch_param_info", _locals)
    return _CLIENT.invoke("Device_get_ch_param_info", _args, _kwargs, _resources)

def Device_get_ch_param_prop(slot: int, channel: int, name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_ch_param_prop", _locals)
    _resources = _resources_for("Device_get_ch_param_prop", _locals)
    return _CLIENT.invoke("Device_get_ch_param_prop", _args, _kwargs, _resources)

def Device_get_crate_map():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_crate_map", _locals)
    _resources = _resources_for("Device_get_crate_map", _locals)
    return _CLIENT.invoke("Device_get_crate_map", _args, _kwargs, _resources)

def Device_get_event_data():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_event_data", _locals)
    _resources = _resources_for("Device_get_event_data", _locals)
    return _CLIENT.invoke("Device_get_event_data", _args, _kwargs, _resources)

def Device_get_events_tcp_ports():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_events_tcp_ports", _locals)
    _resources = _resources_for("Device_get_events_tcp_ports", _locals)
    return _CLIENT.invoke("Device_get_events_tcp_ports", _args, _kwargs, _resources)

def Device_get_exec_comm_list():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_exec_comm_list", _locals)
    _resources = _resources_for("Device_get_exec_comm_list", _locals)
    return _CLIENT.invoke("Device_get_exec_comm_list", _args, _kwargs, _resources)

def Device_get_sys_prop(name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_sys_prop", _locals)
    _resources = _resources_for("Device_get_sys_prop", _locals)
    return _CLIENT.invoke("Device_get_sys_prop", _args, _kwargs, _resources)

def Device_get_sys_prop_info(name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_sys_prop_info", _locals)
    _resources = _resources_for("Device_get_sys_prop_info", _locals)
    return _CLIENT.invoke("Device_get_sys_prop_info", _args, _kwargs, _resources)

def Device_get_sys_prop_list():
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_get_sys_prop_list", _locals)
    _resources = _resources_for("Device_get_sys_prop_list", _locals)
    return _CLIENT.invoke("Device_get_sys_prop_list", _args, _kwargs, _resources)

def Device_open(system_type: caen_libs._caenhvwrappertypes.SystemType, link_type: caen_libs._caenhvwrappertypes.LinkType, arg: str, username: str = '', password: str = ''):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_open", _locals)
    _resources = _resources_for("Device_open", _locals)
    return _CLIENT.invoke("Device_open", _args, _kwargs, _resources)

def Device_set_bd_param(slot_list: collections.abc.Sequence[int], name: str, value: str | float | int | None):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_set_bd_param", _locals)
    _resources = _resources_for("Device_set_bd_param", _locals)
    return _CLIENT.invoke("Device_set_bd_param", _args, _kwargs, _resources)

def Device_set_ch_name(slot: int, channel_list: collections.abc.Sequence[int], name: str):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_set_ch_name", _locals)
    _resources = _resources_for("Device_set_ch_name", _locals)
    return _CLIENT.invoke("Device_set_ch_name", _args, _kwargs, _resources)

def Device_set_ch_param(slot: int, channel_list: collections.abc.Sequence[int], name: str, value: str | float | int | None):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_set_ch_param", _locals)
    _resources = _resources_for("Device_set_ch_param", _locals)
    return _CLIENT.invoke("Device_set_ch_param", _args, _kwargs, _resources)

def Device_set_events_tcp_ports(first: int, last: int):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_set_events_tcp_ports", _locals)
    _resources = _resources_for("Device_set_events_tcp_ports", _locals)
    return _CLIENT.invoke("Device_set_events_tcp_ports", _args, _kwargs, _resources)

def Device_set_sys_prop(name: str, value: str | float | int | bool):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_set_sys_prop", _locals)
    _resources = _resources_for("Device_set_sys_prop", _locals)
    return _CLIENT.invoke("Device_set_sys_prop", _args, _kwargs, _resources)

def Device_subscribe_board_params(slot: int, param_list: collections.abc.Sequence[str]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_subscribe_board_params", _locals)
    _resources = _resources_for("Device_subscribe_board_params", _locals)
    return _CLIENT.invoke("Device_subscribe_board_params", _args, _kwargs, _resources)

def Device_subscribe_channel_params(slot: int, channel: int, param_list: collections.abc.Sequence[str]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_subscribe_channel_params", _locals)
    _resources = _resources_for("Device_subscribe_channel_params", _locals)
    return _CLIENT.invoke("Device_subscribe_channel_params", _args, _kwargs, _resources)

def Device_subscribe_system_params(param_list: collections.abc.Sequence[str]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_subscribe_system_params", _locals)
    _resources = _resources_for("Device_subscribe_system_params", _locals)
    return _CLIENT.invoke("Device_subscribe_system_params", _args, _kwargs, _resources)

def Device_test_bd_presence(slot: int):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_test_bd_presence", _locals)
    _resources = _resources_for("Device_test_bd_presence", _locals)
    return _CLIENT.invoke("Device_test_bd_presence", _args, _kwargs, _resources)

def Device_unsubscribe_board_params(slot: int, param_list: collections.abc.Sequence[str]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_unsubscribe_board_params", _locals)
    _resources = _resources_for("Device_unsubscribe_board_params", _locals)
    return _CLIENT.invoke("Device_unsubscribe_board_params", _args, _kwargs, _resources)

def Device_unsubscribe_channel_params(slot: int, channel: int, param_list: collections.abc.Sequence[str]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_unsubscribe_channel_params", _locals)
    _resources = _resources_for("Device_unsubscribe_channel_params", _locals)
    return _CLIENT.invoke("Device_unsubscribe_channel_params", _args, _kwargs, _resources)

def Device_unsubscribe_system_params(param_list: collections.abc.Sequence[str]):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Device_unsubscribe_system_params", _locals)
    _resources = _resources_for("Device_unsubscribe_system_params", _locals)
    return _CLIENT.invoke("Device_unsubscribe_system_params", _args, _kwargs, _resources)

def Error_Code(*values):
    _locals = locals()
    _args, _kwargs = _pack_call_args("Error_Code", _locals)
    _resources = _resources_for("Error_Code", _locals)
    return _CLIENT.invoke("Error_Code", _args, _kwargs, _resources)


class Device:
    def __init__(self, handle: str) -> None:
        self._handle = handle

    @classmethod
    def open(cls, system_type: caen_libs._caenhvwrappertypes.SystemType, link_type: caen_libs._caenhvwrappertypes.LinkType, arg: str, username: str = '', password: str = ''):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_open', _locals)
        _resources = _resources_for('Device_open', _locals)
        _result = _CLIENT.invoke('Device_open', _args, _kwargs, _resources)
        if isinstance(_result, dict) and '__devman_handle__' in _result:
            return cls(str(_result['__devman_handle__']))
        raise RuntimeError('manager did not return a device handle')

    def close(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_close', _locals)
        _resources = _resources_for('Device_close', _locals)
        return _CLIENT.invoke('Device_close', _args, _kwargs, _resources, handle=self._handle)

    def connect(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_connect', _locals)
        _resources = _resources_for('Device_connect', _locals)
        return _CLIENT.invoke('Device_connect', _args, _kwargs, _resources, handle=self._handle)

    def device_closed(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_device_closed', _locals)
        _resources = _resources_for('Device_device_closed', _locals)
        return _CLIENT.invoke('Device_device_closed', _args, _kwargs, _resources, handle=self._handle)

    def exec_comm(self, name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_exec_comm', _locals)
        _resources = _resources_for('Device_exec_comm', _locals)
        return _CLIENT.invoke('Device_exec_comm', _args, _kwargs, _resources, handle=self._handle)

    def get_bd_param(self, slot_list: collections.abc.Sequence[int], name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_bd_param', _locals)
        _resources = _resources_for('Device_get_bd_param', _locals)
        return _CLIENT.invoke('Device_get_bd_param', _args, _kwargs, _resources, handle=self._handle)

    def get_bd_param_info(self, slot: int):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_bd_param_info', _locals)
        _resources = _resources_for('Device_get_bd_param_info', _locals)
        return _CLIENT.invoke('Device_get_bd_param_info', _args, _kwargs, _resources, handle=self._handle)

    def get_bd_param_prop(self, slot: int, name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_bd_param_prop', _locals)
        _resources = _resources_for('Device_get_bd_param_prop', _locals)
        return _CLIENT.invoke('Device_get_bd_param_prop', _args, _kwargs, _resources, handle=self._handle)

    def get_ch_name(self, slot: int, channel_list: collections.abc.Sequence[int]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_ch_name', _locals)
        _resources = _resources_for('Device_get_ch_name', _locals)
        return _CLIENT.invoke('Device_get_ch_name', _args, _kwargs, _resources, handle=self._handle)

    def get_ch_param(self, slot: int, channel_list: collections.abc.Sequence[int], name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_ch_param', _locals)
        _resources = _resources_for('Device_get_ch_param', _locals)
        return _CLIENT.invoke('Device_get_ch_param', _args, _kwargs, _resources, handle=self._handle)

    def get_ch_param_info(self, slot: int, channel: int):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_ch_param_info', _locals)
        _resources = _resources_for('Device_get_ch_param_info', _locals)
        return _CLIENT.invoke('Device_get_ch_param_info', _args, _kwargs, _resources, handle=self._handle)

    def get_ch_param_prop(self, slot: int, channel: int, name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_ch_param_prop', _locals)
        _resources = _resources_for('Device_get_ch_param_prop', _locals)
        return _CLIENT.invoke('Device_get_ch_param_prop', _args, _kwargs, _resources, handle=self._handle)

    def get_crate_map(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_crate_map', _locals)
        _resources = _resources_for('Device_get_crate_map', _locals)
        return _CLIENT.invoke('Device_get_crate_map', _args, _kwargs, _resources, handle=self._handle)

    def get_event_data(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_event_data', _locals)
        _resources = _resources_for('Device_get_event_data', _locals)
        return _CLIENT.invoke('Device_get_event_data', _args, _kwargs, _resources, handle=self._handle)

    def get_events_tcp_ports(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_events_tcp_ports', _locals)
        _resources = _resources_for('Device_get_events_tcp_ports', _locals)
        return _CLIENT.invoke('Device_get_events_tcp_ports', _args, _kwargs, _resources, handle=self._handle)

    def get_exec_comm_list(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_exec_comm_list', _locals)
        _resources = _resources_for('Device_get_exec_comm_list', _locals)
        return _CLIENT.invoke('Device_get_exec_comm_list', _args, _kwargs, _resources, handle=self._handle)

    def get_sys_prop(self, name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_sys_prop', _locals)
        _resources = _resources_for('Device_get_sys_prop', _locals)
        return _CLIENT.invoke('Device_get_sys_prop', _args, _kwargs, _resources, handle=self._handle)

    def get_sys_prop_info(self, name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_sys_prop_info', _locals)
        _resources = _resources_for('Device_get_sys_prop_info', _locals)
        return _CLIENT.invoke('Device_get_sys_prop_info', _args, _kwargs, _resources, handle=self._handle)

    def get_sys_prop_list(self):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_get_sys_prop_list', _locals)
        _resources = _resources_for('Device_get_sys_prop_list', _locals)
        return _CLIENT.invoke('Device_get_sys_prop_list', _args, _kwargs, _resources, handle=self._handle)

    def set_bd_param(self, slot_list: collections.abc.Sequence[int], name: str, value: str | float | int | None):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_set_bd_param', _locals)
        _resources = _resources_for('Device_set_bd_param', _locals)
        return _CLIENT.invoke('Device_set_bd_param', _args, _kwargs, _resources, handle=self._handle)

    def set_ch_name(self, slot: int, channel_list: collections.abc.Sequence[int], name: str):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_set_ch_name', _locals)
        _resources = _resources_for('Device_set_ch_name', _locals)
        return _CLIENT.invoke('Device_set_ch_name', _args, _kwargs, _resources, handle=self._handle)

    def set_ch_param(self, slot: int, channel_list: collections.abc.Sequence[int], name: str, value: str | float | int | None):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_set_ch_param', _locals)
        _resources = _resources_for('Device_set_ch_param', _locals)
        return _CLIENT.invoke('Device_set_ch_param', _args, _kwargs, _resources, handle=self._handle)

    def set_events_tcp_ports(self, first: int, last: int):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_set_events_tcp_ports', _locals)
        _resources = _resources_for('Device_set_events_tcp_ports', _locals)
        return _CLIENT.invoke('Device_set_events_tcp_ports', _args, _kwargs, _resources, handle=self._handle)

    def set_sys_prop(self, name: str, value: str | float | int | bool):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_set_sys_prop', _locals)
        _resources = _resources_for('Device_set_sys_prop', _locals)
        return _CLIENT.invoke('Device_set_sys_prop', _args, _kwargs, _resources, handle=self._handle)

    def subscribe_board_params(self, slot: int, param_list: collections.abc.Sequence[str]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_subscribe_board_params', _locals)
        _resources = _resources_for('Device_subscribe_board_params', _locals)
        return _CLIENT.invoke('Device_subscribe_board_params', _args, _kwargs, _resources, handle=self._handle)

    def subscribe_channel_params(self, slot: int, channel: int, param_list: collections.abc.Sequence[str]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_subscribe_channel_params', _locals)
        _resources = _resources_for('Device_subscribe_channel_params', _locals)
        return _CLIENT.invoke('Device_subscribe_channel_params', _args, _kwargs, _resources, handle=self._handle)

    def subscribe_system_params(self, param_list: collections.abc.Sequence[str]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_subscribe_system_params', _locals)
        _resources = _resources_for('Device_subscribe_system_params', _locals)
        return _CLIENT.invoke('Device_subscribe_system_params', _args, _kwargs, _resources, handle=self._handle)

    def test_bd_presence(self, slot: int):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_test_bd_presence', _locals)
        _resources = _resources_for('Device_test_bd_presence', _locals)
        return _CLIENT.invoke('Device_test_bd_presence', _args, _kwargs, _resources, handle=self._handle)

    def unsubscribe_board_params(self, slot: int, param_list: collections.abc.Sequence[str]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_unsubscribe_board_params', _locals)
        _resources = _resources_for('Device_unsubscribe_board_params', _locals)
        return _CLIENT.invoke('Device_unsubscribe_board_params', _args, _kwargs, _resources, handle=self._handle)

    def unsubscribe_channel_params(self, slot: int, channel: int, param_list: collections.abc.Sequence[str]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_unsubscribe_channel_params', _locals)
        _resources = _resources_for('Device_unsubscribe_channel_params', _locals)
        return _CLIENT.invoke('Device_unsubscribe_channel_params', _args, _kwargs, _resources, handle=self._handle)

    def unsubscribe_system_params(self, param_list: collections.abc.Sequence[str]):
        _locals = locals()
        _args, _kwargs = _pack_call_args('Device_unsubscribe_system_params', _locals)
        _resources = _resources_for('Device_unsubscribe_system_params', _locals)
        return _CLIENT.invoke('Device_unsubscribe_system_params', _args, _kwargs, _resources, handle=self._handle)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class _LibProxy:
    def sw_release(self) -> str:
        try:
            value = _CLIENT.invoke('lib.sw_release', [], {}, [])
            return str(value)
        except Exception:
            return 'managed'

lib = _LibProxy()
