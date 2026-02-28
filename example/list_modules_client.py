#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List connected CAEN HV modules through devman client")
    parser.add_argument("--manager-host", default="127.0.0.1", help="devman manager host")
    parser.add_argument("--manager-port", type=int, default=50250, help="devman manager port")
    parser.add_argument("--client-name", default="module-lister", help="unique client name")

    parser.add_argument("--systemtype", default="SY4527", help="CAEN SystemType enum name")
    parser.add_argument("--linktype", default="TCPIP", help="CAEN LinkType enum name")
    parser.add_argument("--address", default="192.168.1.100", help="device connection argument")
    return parser.parse_args()


def _field(board: object, name: str):
    if isinstance(board, dict):
        return board.get(name)
    return getattr(board, name)


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "generated_bridge"))

    import caenhv_devman_bridge as hv

    hv.configure_connection(
        host=args.manager_host,
        port=args.manager_port,
        client_name=args.client_name,
    )

    system_type = hv.SystemType[args.systemtype]
    link_type = hv.LinkType[args.linktype]
    open_resource = f"system_type:{system_type}"

    if not hv.acquire(open_resource):
        print(f"Failed to acquire resource: {open_resource}", file=sys.stderr)
        return 2

    try:
        with hv.Device.open(system_type, link_type, args.address) as device:
            slots = device.get_crate_map()
            print(f"Connected modules at {args.address}:")
            found = False
            for board in slots:
                if board is None:
                    continue
                found = True
                fw = _field(board, "fw_version")
                if isinstance(fw, dict):
                    fw_text = f"{fw.get('major')}.{fw.get('minor')}"
                else:
                    fw_text = str(fw)
                print(
                    f"slot={_field(board, 'slot')} model={_field(board, 'model')} "
                    f"serial={_field(board, 'serial_number')} "
                    f"channels={_field(board, 'n_channel')} fw={fw_text}"
                )
            if not found:
                print("No modules detected")
    finally:
        hv.release(open_resource)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
