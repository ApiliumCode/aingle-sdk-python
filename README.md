# AIngle SDK for Python

Official Python SDK for [AIngle](https://apilium.com) - the ultra-light distributed ledger for IoT devices.

## Installation

```bash
pip install aingle-sdk
```

## Quick Start

```python
import asyncio
from aingle_sdk import AIngleClient

async def main():
    async with AIngleClient(node_url="http://localhost:8080") as client:
        # Create an entry
        hash = await client.create_entry({
            "type": "sensor_reading",
            "value": 23.5,
            "unit": "celsius",
        })
        print(f"Created entry: {hash}")

        # Retrieve an entry
        entry = await client.get_entry(hash)
        print(entry)

        # Get node info
        info = await client.get_node_info()
        print(f"Node version: {info.version}")

asyncio.run(main())
```

## Subscribe to Real-time Updates

```python
import asyncio
from aingle_sdk import AIngleClient

async def main():
    client = AIngleClient()
    await client.connect()

    def on_entry(entry):
        print(f"New entry: {entry.hash}")

    unsubscribe = await client.subscribe(on_entry)

    # Keep running for 60 seconds
    await asyncio.sleep(60)

    unsubscribe()
    await client.disconnect()

asyncio.run(main())
```

## API Reference

### AIngleClient

| Method | Description |
|--------|-------------|
| `connect()` | Connect to the AIngle node |
| `disconnect()` | Disconnect from the node |
| `create_entry(data)` | Create a new entry |
| `get_entry(hash)` | Retrieve an entry by hash |
| `get_node_info()` | Get node information |
| `subscribe(callback)` | Subscribe to real-time updates |

### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `node_url` | `str` | `http://localhost:8080` | Node URL |
| `ws_url` | `str` | `ws://localhost:8081` | WebSocket URL |
| `timeout` | `float` | `30.0` | Request timeout (seconds) |
| `debug` | `bool` | `False` | Enable debug logging |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=aingle_sdk

# Type checking
mypy src

# Linting
ruff check src

# Format code
black src
```

## License

Apache-2.0 - see [LICENSE](LICENSE)

## Links

- [AIngle Core](https://github.com/ApiliumCode/aingle)
- [Documentation](https://docs.apilium.com)
- [Discord](https://discord.gg/apilium)
