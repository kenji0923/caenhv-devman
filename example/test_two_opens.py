from __future__ import annotations

from caen_libs import caenhvwrapper as hv

ADDRESS = "192.168.1.23"
USERNAME = "FanLabAdmin"
PASSWORD = "g_e=2.002"
SYSTEM = hv.SystemType.SY4527
LINK = hv.LinkType.TCPIP

d1 = None
d2 = None

print("Opening first session...")
try:
    d1 = hv.Device.open(SYSTEM, LINK, ADDRESS, USERNAME, PASSWORD)
    print("first open: OK")
except Exception as exc:
    print("first open: FAIL", type(exc).__name__, exc)
    raise SystemExit(1)

print("Opening second concurrent session...")
try:
    d2 = hv.Device.open(SYSTEM, LINK, ADDRESS, USERNAME, PASSWORD)
    print("second open: OK")
except Exception as exc:
    print("second open: FAIL", type(exc).__name__, exc)

print("Closing...")
for i, dev in enumerate([d2, d1], start=1):
    if dev is None:
        continue
    try:
        dev.close()
        print(f"close {i}: OK")
    except Exception as exc:
        print(f"close {i}: FAIL", type(exc).__name__, exc)
