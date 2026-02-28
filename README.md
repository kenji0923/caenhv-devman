# CAEN HV Device Manager (devman) Bridge

This project provides a bridge and management layer for CAEN High Voltage systems, allowing for resource ownership and remote control.

## Prerequisites

- Python 3.x
- `caen_libs.caenhvwrapper` (The backend library for CAEN HV)
- `devman_gen` runtime package (provides the `serve_manager` and base client logic)

## Running the Server

The server manages resource ownership and routes requests to the CAEN HV backend.

### Basic Command

```bash
python3 generated_bridge/caenhv_devman_bridge/server.py --backend-module caen_libs.caenhvwrapper
```

### Configuration Options

The server can be configured via command-line arguments or environment variables:

| Argument | Environment Variable | Default | Description |
| :--- | :--- | :--- | :--- |
| `--backend-module` | `DEVMAN_BACKEND_MODULE` | (Required) | The Python module implementing the device backend. |
| `--host` | `DEVMAN_HOST` | `127.0.0.1` | The host address to bind the server to. |
| `--port` | `DEVMAN_PORT` | `50250` | The port to listen on. |
| `--db` | `DEVMAN_DB` | `./ownership.db` | Path to the SQLite database for tracking ownership. |
| `--username` | `DEVMAN_USERNAME` | `""` | Default username for device connection. |
| `--password` | `DEVMAN_PASSWORD` | `""` | Default password for device connection. |

## Using the Clients

Example client scripts are located in the `example/` directory. These scripts demonstrate how to acquire resources and interact with the HV system.

### Listing Modules
Use `example/list_modules_client.py` to see detected boards in a crate:

```bash
python3 example/list_modules_client.py --address <crate_ip_address>
```

### Acquiring Ownership
Use `example/owner_slot2_ch23.py` to hold ownership of a specific channel, preventing other clients from modifying it:

```bash
python3 example/owner_slot2_ch23.py --hold-seconds 60
```

### Testing Conflicts
Use `example/contender_try_set_10v.py` to verify that ownership is respected. Run this while another client holds the resource to see it fail:

```bash
python3 example/contender_try_set_10v.py --address <crate_ip_address>
```

## Running Tests

Live ownership tests can be run using `pytest`. These require a running manager and access to a device (or a mock backend).

```bash
export DEVMAN_DEVICE_ADDR="192.168.1.100"
pytest tests/test_live_ownership.py
```
