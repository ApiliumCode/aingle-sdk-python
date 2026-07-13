"""
AIngle Cortex SDK type definitions.

Typed request/response models for the AIngle Cortex REST API, implemented with
plain dataclasses to keep the package dependency-light.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

# A triple's ``object`` is an untagged union serialized as the raw JSON value:
#   string  -> "hello"
#   integer -> 42
#   float   -> 4.2
#   boolean -> true
#   node ref (IRI) -> {"node": "http://example.org/thing"}
Value = Union[str, int, float, bool, Dict[str, str]]


def node_ref(iri: str) -> Dict[str, str]:
    """Build a node-reference (IRI) object Value: ``{"node": iri}``."""
    return {"node": iri}


class AIngleError(Exception):
    """Typed error raised for non-2xx responses from the AIngle Cortex API."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"[{status}] {message}")
        self.status = status
        self.message = message


# --- Health & stats -------------------------------------------------------


@dataclass
class ComponentHealth:
    status: str
    message: Optional[str] = None


@dataclass
class HealthComponents:
    graph: ComponentHealth
    logic: ComponentHealth


@dataclass
class Health:
    status: str
    components: HealthComponents


@dataclass
class GraphStats:
    triple_count: int
    subject_count: int
    predicate_count: int
    object_count: int


@dataclass
class ServerStats:
    connected_clients: int
    uptime_seconds: int
    version: str


@dataclass
class Stats:
    graph: GraphStats
    server: ServerStats


# --- Memory ---------------------------------------------------------------


@dataclass
class RememberResponse:
    id: str


@dataclass
class RecallResult:
    id: str
    entry_type: str
    data: Any
    tags: List[str]
    importance: float
    relevance: float
    source: str
    created_at: str
    last_accessed: str
    access_count: int


@dataclass
class MemoryStats:
    stm_count: int
    stm_capacity: int
    ltm_entity_count: int
    ltm_link_count: int
    total_memory_bytes: int


# --- Triples --------------------------------------------------------------


@dataclass
class Triple:
    subject: str
    predicate: str
    object: Value
    id: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class CreateTriple:
    subject: str
    predicate: str
    object: Value


@dataclass
class TripleList:
    triples: List[Triple]
    total: int
    limit: int
    offset: int


@dataclass
class BatchInsertResult:
    inserted: List[Triple]
    total: int
    duplicates: int


# --- Query ----------------------------------------------------------------


@dataclass
class QueryResult:
    matches: List[Triple]
    total: int
    pattern: Any


@dataclass
class SubjectsResult:
    subjects: List[str]
    total: int


@dataclass
class PredicatesResult:
    predicates: List[str]
    total: int


def _component(raw: Dict[str, Any]) -> ComponentHealth:
    return ComponentHealth(status=raw["status"], message=raw.get("message"))


def parse_health(raw: Dict[str, Any]) -> Health:
    comps = raw.get("components", {})
    return Health(
        status=raw["status"],
        components=HealthComponents(
            graph=_component(comps.get("graph", {})),
            logic=_component(comps.get("logic", {})),
        ),
    )


def parse_stats(raw: Dict[str, Any]) -> Stats:
    g = raw.get("graph", {})
    s = raw.get("server", {})
    return Stats(
        graph=GraphStats(
            triple_count=g.get("triple_count", 0),
            subject_count=g.get("subject_count", 0),
            predicate_count=g.get("predicate_count", 0),
            object_count=g.get("object_count", 0),
        ),
        server=ServerStats(
            connected_clients=s.get("connected_clients", 0),
            uptime_seconds=s.get("uptime_seconds", 0),
            version=s.get("version", ""),
        ),
    )


def parse_recall_result(raw: Dict[str, Any]) -> RecallResult:
    return RecallResult(
        id=raw["id"],
        entry_type=raw["entry_type"],
        data=raw.get("data"),
        tags=list(raw.get("tags", [])),
        importance=raw.get("importance", 0.0),
        relevance=raw.get("relevance", 0.0),
        source=raw.get("source", ""),
        created_at=raw.get("created_at", ""),
        last_accessed=raw.get("last_accessed", ""),
        access_count=raw.get("access_count", 0),
    )


def parse_memory_stats(raw: Dict[str, Any]) -> MemoryStats:
    return MemoryStats(
        stm_count=raw.get("stm_count", 0),
        stm_capacity=raw.get("stm_capacity", 0),
        ltm_entity_count=raw.get("ltm_entity_count", 0),
        ltm_link_count=raw.get("ltm_link_count", 0),
        total_memory_bytes=raw.get("total_memory_bytes", 0),
    )


def parse_triple(raw: Dict[str, Any]) -> Triple:
    return Triple(
        subject=raw["subject"],
        predicate=raw["predicate"],
        object=raw["object"],
        id=raw.get("id"),
        created_at=raw.get("created_at"),
    )


def parse_triple_list(raw: Dict[str, Any]) -> TripleList:
    return TripleList(
        triples=[parse_triple(t) for t in raw.get("triples", [])],
        total=raw.get("total", 0),
        limit=raw.get("limit", 0),
        offset=raw.get("offset", 0),
    )


def parse_batch_insert(raw: Dict[str, Any]) -> BatchInsertResult:
    return BatchInsertResult(
        inserted=[parse_triple(t) for t in raw.get("inserted", [])],
        total=raw.get("total", 0),
        duplicates=raw.get("duplicates", 0),
    )


def parse_query_result(raw: Dict[str, Any]) -> QueryResult:
    return QueryResult(
        matches=[parse_triple(t) for t in raw.get("matches", [])],
        total=raw.get("total", 0),
        pattern=raw.get("pattern"),
    )
