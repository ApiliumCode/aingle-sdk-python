"""
AIngle Client - Main entry point for interacting with AIngle network
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import httpx
import websockets
from websockets.client import WebSocketClientProtocol

from .types import Entry, EntryHash, NodeInfo


@dataclass
class AIngleClientConfig:
    """Configuration for AIngle client."""

    node_url: str = "http://localhost:8080"
    ws_url: str = "ws://localhost:8081"
    timeout: float = 30.0
    debug: bool = False


class AIngleClient:
    """
    AIngle Client for interacting with AIngle nodes.

    Example:
        ```python
        from aingle_sdk import AIngleClient

        async def main():
            client = AIngleClient(node_url="http://localhost:8080")

            # Create an entry
            hash = await client.create_entry({"data": "Hello, AIngle!"})

            # Retrieve an entry
            entry = await client.get_entry(hash)
            print(entry)

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        node_url: str = "http://localhost:8080",
        ws_url: str = "ws://localhost:8081",
        timeout: float = 30.0,
        debug: bool = False,
    ) -> None:
        self.config = AIngleClientConfig(
            node_url=node_url,
            ws_url=ws_url,
            timeout=timeout,
            debug=debug,
        )
        self._http_client: Optional[httpx.AsyncClient] = None
        self._ws: Optional[WebSocketClientProtocol] = None

    async def __aenter__(self) -> "AIngleClient":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to the AIngle node."""
        if self.config.debug:
            print(f"Connecting to {self.config.node_url}")

        self._http_client = httpx.AsyncClient(
            base_url=self.config.node_url,
            timeout=self.config.timeout,
        )

    async def disconnect(self) -> None:
        """Disconnect from the AIngle node."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        if self._ws:
            await self._ws.close()
            self._ws = None

    async def create_entry(self, data: Any) -> EntryHash:
        """
        Create a new entry in the DAG.

        Args:
            data: Entry payload (will be JSON serialized)

        Returns:
            Hash of the created entry
        """
        if not self._http_client:
            await self.connect()

        assert self._http_client is not None

        response = await self._http_client.post(
            "/api/v1/entries",
            json={"data": data},
        )
        response.raise_for_status()

        result = response.json()
        return result["hash"]

    async def get_entry(self, hash: EntryHash) -> Optional[Entry]:
        """
        Retrieve an entry by hash.

        Args:
            hash: Entry hash

        Returns:
            Entry if found, None otherwise
        """
        if not self._http_client:
            await self.connect()

        assert self._http_client is not None

        response = await self._http_client.get(f"/api/v1/entries/{hash}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return Entry(**response.json())

    async def get_node_info(self) -> NodeInfo:
        """
        Get node information.

        Returns:
            Node information
        """
        if not self._http_client:
            await self.connect()

        assert self._http_client is not None

        response = await self._http_client.get("/api/v1/info")
        response.raise_for_status()

        return NodeInfo(**response.json())

    async def subscribe(
        self,
        callback: Callable[[Entry], None],
    ) -> Callable[[], None]:
        """
        Subscribe to real-time updates.

        Args:
            callback: Function to call when new entries arrive

        Returns:
            Unsubscribe function
        """
        self._ws = await websockets.connect(self.config.ws_url)

        async def listen() -> None:
            assert self._ws is not None
            async for message in self._ws:
                import json

                entry_data = json.loads(message)
                entry = Entry(**entry_data)
                callback(entry)

        task = asyncio.create_task(listen())

        def unsubscribe() -> None:
            task.cancel()
            if self._ws:
                asyncio.create_task(self._ws.close())

        return unsubscribe
