"""
AIngle SDK Type Definitions
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


# Type aliases
EntryHash = str
AgentPubKey = str
Timestamp = int


@dataclass
class Entry:
    """Entry in the AIngle DAG."""

    hash: EntryHash
    author: AgentPubKey
    parents: List[EntryHash]
    data: Any
    timestamp: Timestamp
    sequence: int
    signature: str


@dataclass
class NodeInfo:
    """Node information."""

    node_id: str
    version: str
    uptime: int
    entries_count: int
    peers_count: int
    storage_backend: str
    features: List[str]


@dataclass
class PeerInfo:
    """Peer information."""

    peer_id: str
    address: str
    quality: int
    last_seen: Timestamp
    latest_seq: int


@dataclass
class SyncStatus:
    """Sync status."""

    syncing: bool
    pending: int
    last_sync: Timestamp


class ErrorCode(Enum):
    """Error codes."""

    CONNECTION_FAILED = "CONNECTION_FAILED"
    TIMEOUT = "TIMEOUT"
    NOT_FOUND = "NOT_FOUND"
    INVALID_ENTRY = "INVALID_ENTRY"
    STORAGE_ERROR = "STORAGE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    AUTH_ERROR = "AUTH_ERROR"


class AIngleError(Exception):
    """SDK Error."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.cause = cause
