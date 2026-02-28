#!/usr/bin/env python3
from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acquire and hold slot2:channel23 ownership")
    parser.add_argument("--manager-host", default="127.0.0.1")
    parser.add_argument("--manager-port", type=int, default=50250)
    parser.add_argument("--client-name", default="owner-slot2-ch23")
    parser.add_argument("--resource", default="slot2:channel23")
    parser.add_argument("--hold-seconds", type=int, default=120)
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
    if not acquired:
        print("Ownership not acquired; exiting.")
        return 2

    stop = False

    def _stop(_signum, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    print(f"Holding ownership for up to {args.hold_seconds}s. Press Ctrl+C to release early.")
    start = time.time()
    try:
        while not stop and (time.time() - start) < args.hold_seconds:
            time.sleep(0.2)
    finally:
        released = hv.release(args.resource)
        print(f"release({args.resource}) -> {released}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
