from __future__ import annotations

import argparse
import os

from devman_gen.runtime.server import RuntimeFunctionSpec, serve_manager

FUNCTIONS = { 'Device_get_bd_param': { 'dispatch': 'singleton',
                           'dispatch_target': 'get_bd_param',
                           'name': 'Device_get_bd_param',
                           'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot_list': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['slot_list', 'name'],
                           'resource_template': None},
  'Device_get_bd_param_info': { 'dispatch': 'singleton',
                                'dispatch_target': 'get_bd_param_info',
                                'name': 'Device_get_bd_param_info',
                                'param_kinds': { 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot'],
                                'resource_template': None},
  'Device_get_bd_param_prop': { 'dispatch': 'singleton',
                                'dispatch_target': 'get_bd_param_prop',
                                'name': 'Device_get_bd_param_prop',
                                'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD',
                                                 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot', 'name'],
                                'resource_template': None},
  'Device_get_ch_name': { 'dispatch': 'singleton',
                          'dispatch_target': 'get_ch_name',
                          'name': 'Device_get_ch_name',
                          'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                           'slot': 'POSITIONAL_OR_KEYWORD'},
                          'param_order': ['slot', 'channel_list'],
                          'resource_template': None},
  'Device_get_ch_param': { 'dispatch': 'singleton',
                           'dispatch_target': 'get_ch_param',
                           'name': 'Device_get_ch_param',
                           'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                            'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['slot', 'channel_list', 'name'],
                           'resource_template': None},
  'Device_get_ch_param_info': { 'dispatch': 'singleton',
                                'dispatch_target': 'get_ch_param_info',
                                'name': 'Device_get_ch_param_info',
                                'param_kinds': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                                 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot', 'channel'],
                                'resource_template': None},
  'Device_get_ch_param_prop': { 'dispatch': 'singleton',
                                'dispatch_target': 'get_ch_param_prop',
                                'name': 'Device_get_ch_param_prop',
                                'param_kinds': { 'channel': 'POSITIONAL_OR_KEYWORD',
                                                 'name': 'POSITIONAL_OR_KEYWORD',
                                                 'slot': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['slot', 'channel', 'name'],
                                'resource_template': None},
  'Device_get_crate_map': { 'dispatch': 'singleton',
                            'dispatch_target': 'get_crate_map',
                            'name': 'Device_get_crate_map',
                            'param_kinds': {},
                            'param_order': [],
                            'resource_template': None},
  'Device_get_event_data': { 'dispatch': 'singleton',
                             'dispatch_target': 'get_event_data',
                             'name': 'Device_get_event_data',
                             'param_kinds': {},
                             'param_order': [],
                             'resource_template': None},
  'Device_get_events_tcp_ports': { 'dispatch': 'singleton',
                                   'dispatch_target': 'get_events_tcp_ports',
                                   'name': 'Device_get_events_tcp_ports',
                                   'param_kinds': {},
                                   'param_order': [],
                                   'resource_template': None},
  'Device_get_exec_comm_list': { 'dispatch': 'singleton',
                                 'dispatch_target': 'get_exec_comm_list',
                                 'name': 'Device_get_exec_comm_list',
                                 'param_kinds': {},
                                 'param_order': [],
                                 'resource_template': None},
  'Device_get_sys_prop': { 'dispatch': 'singleton',
                           'dispatch_target': 'get_sys_prop',
                           'name': 'Device_get_sys_prop',
                           'param_kinds': {'name': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': ['name'],
                           'resource_template': None},
  'Device_get_sys_prop_info': { 'dispatch': 'singleton',
                                'dispatch_target': 'get_sys_prop_info',
                                'name': 'Device_get_sys_prop_info',
                                'param_kinds': { 'name': 'POSITIONAL_OR_KEYWORD'},
                                'param_order': ['name'],
                                'resource_template': None},
  'Device_get_sys_prop_list': { 'dispatch': 'singleton',
                                'dispatch_target': 'get_sys_prop_list',
                                'name': 'Device_get_sys_prop_list',
                                'param_kinds': {},
                                'param_order': [],
                                'resource_template': None},
  'Device_set_ch_name': { 'dispatch': 'singleton',
                          'dispatch_target': 'set_ch_name',
                          'name': 'Device_set_ch_name',
                          'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                           'name': 'POSITIONAL_OR_KEYWORD',
                                           'slot': 'POSITIONAL_OR_KEYWORD'},
                          'param_order': ['slot', 'channel_list', 'name'],
                          'resource_template': 'slot:{slot}:ch:{channel_list[]}'},
  'Device_set_ch_param': { 'dispatch': 'singleton',
                           'dispatch_target': 'set_ch_param',
                           'name': 'Device_set_ch_param',
                           'param_kinds': { 'channel_list': 'POSITIONAL_OR_KEYWORD',
                                            'name': 'POSITIONAL_OR_KEYWORD',
                                            'slot': 'POSITIONAL_OR_KEYWORD',
                                            'value': 'POSITIONAL_OR_KEYWORD'},
                           'param_order': [ 'slot',
                                            'channel_list',
                                            'name',
                                            'value'],
                           'resource_template': 'slot:{slot}:ch:{channel_list[]}'},
  'Device_test_bd_presence': { 'dispatch': 'singleton',
                               'dispatch_target': 'test_bd_presence',
                               'name': 'Device_test_bd_presence',
                               'param_kinds': {'slot': 'POSITIONAL_OR_KEYWORD'},
                               'param_order': ['slot'],
                               'resource_template': None},
  'Error_Code': { 'dispatch': 'default',
                  'dispatch_target': None,
                  'name': 'Error_Code',
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
            dispatch=data.get('dispatch', 'default'),
            dispatch_target=data.get('dispatch_target'),
        )
        for name, data in FUNCTIONS.items()
    }


def _parse_hook_args(raw_items: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in raw_items:
        if '=' not in item:
            raise ValueError(f"invalid --hook-arg '{item}', expected key=value")
        key, value = item.split('=', 1)
        key = key.strip()
        if not key:
            raise ValueError(f"invalid --hook-arg '{item}', key cannot be empty")
        result[key] = value
    return result


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ('1', 'true', 'yes', 'on')


def main() -> None:
    parser = argparse.ArgumentParser(description='Run devman manager server')
    parser.add_argument('--backend-module', default=os.getenv('DEVMAN_BACKEND_MODULE'), required=False)
    parser.add_argument('--host', default=os.getenv('DEVMAN_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.getenv('DEVMAN_PORT', '50250')))
    parser.add_argument('--db', default=os.getenv('DEVMAN_DB', './ownership.db'))
    parser.add_argument('--verbose', action='store_true', default=_env_flag('DEVMAN_VERBOSE', False))
    parser.add_argument('--init-function', default=os.getenv('DEVMAN_INIT_FUNCTION', ''))
    parser.add_argument('--deinit-function', default=os.getenv('DEVMAN_DEINIT_FUNCTION', ''))
    parser.add_argument('--init-file', default=os.getenv('DEVMAN_INIT_FILE', ''))
    parser.add_argument('--deinit-file', default=os.getenv('DEVMAN_DEINIT_FILE', ''))
    parser.add_argument('--init-file-function', default=os.getenv('DEVMAN_INIT_FILE_FUNCTION', 'init'))
    parser.add_argument('--deinit-file-function', default=os.getenv('DEVMAN_DEINIT_FILE_FUNCTION', 'deinit'))
    parser.add_argument('--singleton-function', default=os.getenv('DEVMAN_SINGLETON_FUNCTION', ''))
    parser.add_argument('--singleton-file', default=os.getenv('DEVMAN_SINGLETON_FILE', ''))
    parser.add_argument('--singleton-file-function', default=os.getenv('DEVMAN_SINGLETON_FILE_FUNCTION', 'get_singleton'))
    parser.add_argument('--hook-arg', action='append', default=[], help='key=value pair passed to hooks (repeatable)')
    args, extra_args = parser.parse_known_args()
    if not args.backend_module:
        parser.error('--backend-module or DEVMAN_BACKEND_MODULE is required')
    if args.init_file and args.init_function:
        parser.error('--init-file and --init-function are mutually exclusive')
    if args.deinit_file and args.deinit_function:
        parser.error('--deinit-file and --deinit-function are mutually exclusive')
    if args.singleton_file and args.singleton_function:
        parser.error('--singleton-file and --singleton-function are mutually exclusive')

    try:
        hook_options = _parse_hook_args(list(args.hook_arg))
    except ValueError as exc:
        parser.error(str(exc))

    serve_manager(
        backend_module=args.backend_module,
        host=args.host,
        port=args.port,
        db_path=args.db,
        functions=_runtime_specs(),
        init_function=args.init_function or None,
        deinit_function=args.deinit_function or None,
        init_file=args.init_file or None,
        deinit_file=args.deinit_file or None,
        init_file_function=args.init_file_function,
        deinit_file_function=args.deinit_file_function,
        hook_args=hook_options,
        extra_args=list(extra_args),
        singleton_function=args.singleton_function or None,
        singleton_file=args.singleton_file or None,
        singleton_file_function=args.singleton_file_function,
        verbose=bool(args.verbose),
    )


if __name__ == '__main__':
    main()
