from __future__ import annotations

import argparse
import os

from devman_gen.runtime.server import RuntimeFunctionSpec, serve_manager

FUNCTIONS = { 'Device_close': { 'name': 'Device_close',
                    'param_kinds': {},
                    'param_order': [],
                    'resource_template': None},
  'Device_connect': { 'name': 'Device_connect',
                      'param_kinds': {},
                      'param_order': [],
                      'resource_template': None},
  'Device_device_closed': { 'name': 'Device_device_closed',
                            'param_kinds': {},
                            'param_order': [],
                            'resource_template': None},
  'Device_exec_comm': { 'name': 'Device_exec_comm',
                        'param_kinds': {'name': 'POSITIONAL_OR_KEYWORD'},
                        'param_order': ['name'],
                        'resource_template': 'name:{name}'},
  'Device_get_bd_param': { 'name': 'Device_get_bd_param',
                           'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot_list': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['slot_list', 'name'],
                           'resource_template': 'slot_list:{slot_list}'},
  'Device_get_bd_param_info': { 'name': 'Device_get_bd_param_info',
                                'param_kinds': { 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot'],
                                'resource_template': 'slot:{slot}'},
  'Device_get_bd_param_prop': { 'name': 'Device_get_bd_param_prop',
                                'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD',
                                                 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot', 'name'],
                                'resource_template': 'slot:{slot}'},
  'Device_get_ch_name': { 'name': 'Device_get_ch_name',
                          'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                           'slot': 'POSITIONAL_OR_KEYWORD'},
                          'param_order': ['slot', 'channel_list'],
                          'resource_template': 'slot:{slot}'},
  'Device_get_ch_param': { 'name': 'Device_get_ch_param',
                           'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                            'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['slot', 'channel_list', 'name'],
                           'resource_template': 'slot:{slot}'},
  'Device_get_ch_param_info': { 'name': 'Device_get_ch_param_info',
                                'param_kinds': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                                 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot', 'channel'],
                                'resource_template': 'slot:{slot}'},
  'Device_get_ch_param_prop': { 'name': 'Device_get_ch_param_prop',
                                'param_kinds': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                                 'name': 'POSITIONAL_OR_KEYWORD',
                                                 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot', 'channel', 'name'],
                                'resource_template': 'slot:{slot}'},
  'Device_get_crate_map': { 'name': 'Device_get_crate_map',
                            'param_kinds': {},
                            'param_order': [],
                            'resource_template': None},
  'Device_get_event_data': { 'name': 'Device_get_event_data',
                             'param_kinds': {},
                             'param_order': [],
                             'resource_template': None},
  'Device_get_events_tcp_ports': { 'name': 'Device_get_events_tcp_ports',
                                   'param_kinds': {},
                                   'param_order': [],
                                   'resource_template': None},
  'Device_get_exec_comm_list': { 'name': 'Device_get_exec_comm_list',
                                 'param_kinds': {},
                                 'param_order': [],
                                 'resource_template': None},
  'Device_get_sys_prop': { 'name': 'Device_get_sys_prop',
                           'param_kinds': {'name': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['name'],
                           'resource_template': 'name:{name}'},
  'Device_get_sys_prop_info': { 'name': 'Device_get_sys_prop_info',
                                'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['name'],
                                'resource_template': 'name:{name}'},
  'Device_get_sys_prop_list': { 'name': 'Device_get_sys_prop_list',
                                'param_kinds': {},
                                'param_order': [],
                                'resource_template': None},
  'Device_open': { 'name': 'Device_open',
                   'param_kinds': { 'arg': 'POSITIONAL_OR_KEYWORD',
                                    'link_type': 'POSITIONAL_OR_KEYWORD',
                                    'password': 'POSITIONAL_OR_KEYWORD',
                                    'system_type': 'POSITIONAL_OR_KEYWORD',
                                    'username': 'POSITIONAL_OR_KEYWORD'},
                   'param_order': [ 'system_type',
                                    'link_type',
                                    'arg',
                                    'username',
                                    'password'],
                   'resource_template': 'system_type:{system_type}'},
  'Device_set_bd_param': { 'name': 'Device_set_bd_param',
                           'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot_list': 'POSITIONAL_OR_KEYWORD',
                                            'value': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['slot_list', 'name', 'value'],
                           'resource_template': 'slot_list:{slot_list}'},
  'Device_set_ch_name': { 'name': 'Device_set_ch_name',
                          'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                           'name': 'POSITIONAL_OR_KEYWORD',
                                           'slot': 'POSITIONAL_OR_KEYWORD'},
                          'param_order': ['slot', 'channel_list', 'name'],
                          'resource_template': 'slot:{slot}'},
  'Device_set_ch_param': { 'name': 'Device_set_ch_param',
                           'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                            'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot': 'POSITIONAL_OR_KEYWORD',
                                            'value': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': [ 'slot',
                                            'channel_list',
                                            'name',
                                            'value'],
                           'resource_template': 'slot:{slot}'},
  'Device_set_events_tcp_ports': { 'name': 'Device_set_events_tcp_ports',
                                   'param_kinds': { 'first': 'POSITIONAL_OR_KEYWORD',
                                                    'last': 'POSITIONAL_OR_KEYWORD'},
                                   'param_order': ['first', 'last'],
                                   'resource_template': 'first:{first}'},
  'Device_set_sys_prop': { 'name': 'Device_set_sys_prop',
                           'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD',
                                            'value': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['name', 'value'],
                           'resource_template': 'name:{name}'},
  'Device_subscribe_board_params': { 'name': 'Device_subscribe_board_params',
                                     'param_kinds': { 'param_list': 'POSITIONAL_OR_KEYWORD',
                                                      'slot': 'POSITIONAL_OR_KEYWORD'},
                                     'param_order': ['slot', 'param_list'],
                                     'resource_template': 'slot:{slot}'},
  'Device_subscribe_channel_params': { 'name': 'Device_subscribe_channel_params',
                                       'param_kinds': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                                        'param_list': 'POSITIONAL_OR_KEYWORD',
                                                        'slot': 'POSITIONAL_OR_KEYWORD'},
                                       'param_order': [ 'slot',
                                                        'channel',
                                                        'param_list'],
                                       'resource_template': 'slot:{slot}'},
  'Device_subscribe_system_params': { 'name': 'Device_subscribe_system_params',
                                      'param_kinds': { 'param_list': 'POSITIONAL_OR_KEYWORD'},
                                      'param_order': ['param_list'],
                                      'resource_template': 'param_list:{param_list}'},
  'Device_test_bd_presence': { 'name': 'Device_test_bd_presence',
                               'param_kinds': {'slot': 'POSITIONAL_OR_KEYWORD'},
                               'param_order': ['slot'],
                               'resource_template': 'slot:{slot}'},
  'Device_unsubscribe_board_params': { 'name': 'Device_unsubscribe_board_params',
                                       'param_kinds': { 'param_list': 'POSITIONAL_OR_KEYWORD',
                                                        'slot': 'POSITIONAL_OR_KEYWORD'},
                                       'param_order': ['slot', 'param_list'],
                                       'resource_template': 'slot:{slot}'},
  'Device_unsubscribe_channel_params': { 'name': 'Device_unsubscribe_channel_params',
                                         'param_kinds': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                                          'param_list': 'POSITIONAL_OR_KEYWORD',
                                                          'slot': 'POSITIONAL_OR_KEYWORD'},
                                         'param_order': [ 'slot',
                                                          'channel',
                                                          'param_list'],
                                         'resource_template': 'slot:{slot}'},
  'Device_unsubscribe_system_params': { 'name': 'Device_unsubscribe_system_params',
                                        'param_kinds': { 'param_list': 'POSITIONAL_OR_KEYWORD'},
                                        'param_order': ['param_list'],
                                        'resource_template': 'param_list:{param_list}'},
  'Error_Code': { 'name': 'Error_Code',
                  'param_kinds': {'values': 'VAR_POSITIONAL'},
                  'param_order': ['values'],
                  'resource_template': None}}


def _runtime_specs() -> dict[str, RuntimeFunctionSpec]:
    return {
        name: RuntimeFunctionSpec(
            name=data['name'],
            param_order=list(data['param_order']),
            param_kinds=dict(data.get('param_kinds', {})),
            resource_template=data['resource_template'],
        )
        for name, data in FUNCTIONS.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Run devman manager server')
    parser.add_argument('--backend-module', default=os.getenv('DEVMAN_BACKEND_MODULE'), required=False)
    parser.add_argument('--host', default=os.getenv('DEVMAN_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.getenv('DEVMAN_PORT', '50250')))
    parser.add_argument('--db', default=os.getenv('DEVMAN_DB', './ownership.db'))
    parser.add_argument('--username', default=os.getenv('DEVMAN_USERNAME', ''))
    parser.add_argument('--password', default=os.getenv('DEVMAN_PASSWORD', ''))
    args = parser.parse_args()
    if not args.backend_module:
        parser.error('--backend-module or DEVMAN_BACKEND_MODULE is required')

    if args.username or args.password:
        import importlib
        backend = importlib.import_module(args.backend_module)
        # Apply monkey-patching for default credentials if applicable
        if hasattr(backend, 'Device') and hasattr(backend.Device, 'open'):
            original_open = backend.Device.open
            @classmethod
            def wrapped_open(cls, system_type, link_type, arg, username=None, password=None):
                u = username if (username is not None and username != "") else args.username
                p = password if (password is not None and password != "") else args.password
                return original_open(system_type, link_type, arg, u, p)
            backend.Device.open = wrapped_open
        elif hasattr(backend, 'Device_open'):
            original_open = backend.Device_open
            def wrapped_open(system_type, link_type, arg, username=None, password=None):
                u = username if (username is not None and username != "") else args.username
                p = password if (password is not None and password != "") else args.password
                return original_open(system_type, link_type, arg, u, p)
            backend.Device_open = wrapped_open

    serve_manager(
        backend_module=args.backend_module,
        host=args.host,
        port=args.port,
        db_path=args.db,
        functions=_runtime_specs(),
    )


if __name__ == '__main__':
    main()
