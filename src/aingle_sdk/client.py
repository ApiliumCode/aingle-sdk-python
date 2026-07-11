"""
AIngle Cortex client.

A small, synchronous HTTP client for the AIngle Cortex REST API, the verifiable
memory cortex for AI agents. Built on httpx.
"""

from __future__ import annotations

import json as _json
from typing import Any, Dict, List, Optional

import httpx

from .types import (
    AIngleError,
    BatchInsertResult,
    CreateTriple,
    Health,
    MemoryStats,
    PredicatesResult,
    QueryResult,
    RecallResult,
    RememberResponse,
    Stats,
    SubjectsResult,
    Triple,
    TripleList,
    Value,
    parse_batch_insert,
    parse_health,
    parse_memory_stats,
    parse_query_result,
    parse_recall_result,
    parse_stats,
    parse_triple,
    parse_triple_list,
)

DEFAULT_BASE_URL = "http://127.0.0.1:19090"
DEFAULT_TIMEOUT = 30.0


class AIngleClient:
    """
    Client for the AIngle Cortex REST API.

    Example:
        ```python
        from aingle_sdk import AIngleClient

        client = AIngleClient()
        result = client.remember("note", {"text": "buy milk"}, tags=["todo"])
        hits = client.recall(text="milk")
        print(hits[0].data)
        ```
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        token: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._http = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    def __enter__(self) -> "AIngleClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    # --- internal helpers -------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
    ) -> Any:
        clean_params = None
        if params is not None:
            clean_params = {
                k: (_json.dumps(v) if isinstance(v, (dict, bool)) else v)
                for k, v in params.items()
                if v is not None
            }

        try:
            response = self._http.request(
                method,
                path,
                params=clean_params,
                json=json,
            )
        except httpx.HTTPError as exc:  # network / transport failure
            raise AIngleError(0, str(exc)) from exc

        if response.status_code >= 400:
            raise AIngleError(response.status_code, self._error_message(response))

        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    @staticmethod
    def _error_message(response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            return response.text or response.reason_phrase
        if isinstance(body, dict):
            for key in ("message", "error", "detail"):
                val = body.get(key)
                if isinstance(val, str):
                    return val
        return response.text or response.reason_phrase

    # --- health & stats ---------------------------------------------------

    def health(self) -> Health:
        """GET /api/v1/health"""
        return parse_health(self._request("GET", "/api/v1/health"))

    def stats(self) -> Stats:
        """GET /api/v1/stats"""
        return parse_stats(self._request("GET", "/api/v1/stats"))

    # --- memory -----------------------------------------------------------

    def remember(
        self,
        entry_type: str,
        data: Any,
        *,
        tags: Optional[List[str]] = None,
        importance: float = 0.0,
        embedding: Optional[List[float]] = None,
    ) -> RememberResponse:
        """POST /api/v1/memory/remember"""
        body: Dict[str, Any] = {
            "entry_type": entry_type,
            "data": data,
            "tags": tags or [],
            "importance": importance,
        }
        if embedding is not None:
            body["embedding"] = embedding
        raw = self._request("POST", "/api/v1/memory/remember", json=body)
        return RememberResponse(id=raw["id"])

    def recall(
        self,
        *,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        entry_type: Optional[str] = None,
        min_importance: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> List[RecallResult]:
        """POST /api/v1/memory/recall"""
        body: Dict[str, Any] = {"tags": tags or []}
        if text is not None:
            body["text"] = text
        if entry_type is not None:
            body["entry_type"] = entry_type
        if min_importance is not None:
            body["min_importance"] = min_importance
        if limit is not None:
            body["limit"] = limit
        raw = self._request("POST", "/api/v1/memory/recall", json=body)
        return [parse_recall_result(r) for r in raw]

    def search(
        self,
        *,
        embedding: List[float],
        k: int,
        min_similarity: float = 0.0,
        entry_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[RecallResult]:
        """POST /api/v1/memory/search (vector / semantic search)"""
        body: Dict[str, Any] = {
            "embedding": embedding,
            "k": k,
            "min_similarity": min_similarity,
        }
        if entry_type is not None:
            body["entry_type"] = entry_type
        if tags is not None:
            body["tags"] = tags
        raw = self._request("POST", "/api/v1/memory/search", json=body)
        return [parse_recall_result(r) for r in raw]

    def memory_stats(self) -> MemoryStats:
        """GET /api/v1/memory/stats"""
        return parse_memory_stats(self._request("GET", "/api/v1/memory/stats"))

    def forget(self, id: str) -> None:
        """DELETE /api/v1/memory/{id}"""
        self._request("DELETE", f"/api/v1/memory/{id}")

    # --- triples ----------------------------------------------------------

    def create_triple(
        self, subject: str, predicate: str, object: Value
    ) -> Triple:
        """POST /api/v1/triples"""
        body = {"subject": subject, "predicate": predicate, "object": object}
        return parse_triple(self._request("POST", "/api/v1/triples", json=body))

    def list_triples(
        self,
        *,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object: Optional[Value] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> TripleList:
        """GET /api/v1/triples"""
        params: Dict[str, Any] = {
            "subject": subject,
            "predicate": predicate,
            "object": object,
            "limit": limit,
            "offset": offset,
        }
        return parse_triple_list(
            self._request("GET", "/api/v1/triples", params=params)
        )

    def create_triples(self, triples: List[CreateTriple]) -> BatchInsertResult:
        """POST /api/v1/triples/batch"""
        body = {
            "triples": [
                {
                    "subject": t.subject,
                    "predicate": t.predicate,
                    "object": t.object,
                }
                for t in triples
            ]
        }
        return parse_batch_insert(
            self._request("POST", "/api/v1/triples/batch", json=body)
        )

    def get_triple(self, id: str) -> Triple:
        """GET /api/v1/triples/{id}"""
        return parse_triple(self._request("GET", f"/api/v1/triples/{id}"))

    def delete_triple(self, id: str) -> None:
        """DELETE /api/v1/triples/{id}"""
        self._request("DELETE", f"/api/v1/triples/{id}")

    # --- query ------------------------------------------------------------

    def query(
        self,
        *,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object: Optional[Value] = None,
        limit: Optional[int] = None,
    ) -> QueryResult:
        """POST /api/v1/query"""
        body: Dict[str, Any] = {}
        if subject is not None:
            body["subject"] = subject
        if predicate is not None:
            body["predicate"] = predicate
        if object is not None:
            body["object"] = object
        if limit is not None:
            body["limit"] = limit
        return parse_query_result(
            self._request("POST", "/api/v1/query", json=body)
        )

    def subjects(
        self,
        *,
        predicate: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> SubjectsResult:
        """GET /api/v1/query/subjects"""
        params = {"predicate": predicate, "limit": limit}
        raw = self._request("GET", "/api/v1/query/subjects", params=params)
        return SubjectsResult(
            subjects=list(raw.get("subjects", [])), total=raw.get("total", 0)
        )

    def predicates(
        self,
        *,
        subject: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> PredicatesResult:
        """GET /api/v1/query/predicates"""
        params = {"subject": subject, "limit": limit}
        raw = self._request("GET", "/api/v1/query/predicates", params=params)
        return PredicatesResult(
            predicates=list(raw.get("predicates", [])), total=raw.get("total", 0)
        )
