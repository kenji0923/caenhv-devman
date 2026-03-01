from caen_libs import caenhvwrapper as hv

address = "192.168.1.23"
trials = [
    ("SY4527", "TCPIP", "FanLabAdmin", "g_e=2.002"),
]

for sys_name, link_name, user, pwd in trials:
    print("---")
    print("trial", sys_name, link_name, f"user={user!r}")
    try:
        system_type = hv.SystemType[sys_name]
        link_type = hv.LinkType[link_name]
        dev = hv.Device.open(system_type, link_type, address, user, pwd)
        print("open=OK")
        try:
            dev.close()
            print("close=OK")
        except Exception as exc:
            print("close=FAIL", type(exc).__name__, exc)
    except Exception as exc:
        print("open=FAIL", type(exc).__name__, exc)

