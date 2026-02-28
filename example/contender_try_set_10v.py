#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try conflicting ownership and 10V set on slot 2 ch 23")
    parser.add_argument("--manager-host", default="127.0.0.1")
    parser.add_argument("--manager-port", type=int, default=50250)
    parser.add_argument("--client-name", default="contender-slot2-ch23")
    parser.add_argument("--resource", default="slot2:channel23")

    parser.add_argument("--systemtype", default="SY4527")
    parser.add_argument("--linktype", default="TCPIP")
    parser.add_argument("--address", default="192.168.1.100")

    parser.add_argument("--slot", type=int, default=2)
    parser.add_argument("--channel", type=int, default=23)
    parser.add_argument("--param", default="V0Set", help="CAEN channel set-voltage parameter name")
    parser.add_argument("--voltage", type=float, default=10.0)
    return parser.parse_args()


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

    acquired = hv.acquire(args.resource)
    print(f"acquire({args.resource}) -> {acquired}")
    if acquired:
        print("UNEXPECTED: contender acquired resource; expected rejection.")
        hv.release(args.resource)
        return 3

    system_type = hv.SystemType[args.systemtype]
    link_type = hv.LinkType[args.linktype]

    print(
        f"Trying set_ch_param(slot={args.slot}, channel={args.channel}, {args.param}={args.voltage}) "
        "without ownership; expecting failure."
    )

    try:
        with hv.Device.open(system_type, link_type, args.address) as device:
            device.set_ch_param(args.slot, [args.channel], args.param, args.voltage)
    except Exception as exc:
        print(f"Expected failure received: {exc}")
        return 0

    print("UNEXPECTED: set_ch_param succeeded")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
