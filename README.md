# AIngle SDK for Python

Python SDK for [AIngle](https://apilium.com), the verifiable memory cortex for
AI agents. AIngle Cortex is a semantic graph plus vector memory served over a
REST API, so your agents can remember, recall, and reason over durable,
queryable knowledge.

## Installation

```bash
pip install aingle-sdk
```

## Quick Start

```python
from aingle_sdk import AIngleClient

client = AIngleClient()  # defaults to http://127.0.0.1:19090

# Remember a note.
saved = client.remember(
    "note",
    {"text": "Ada prefers dark roast coffee"},
    tags=["preference"],
    importance=0.7,
)
print("stored id:", saved.id)

# Recall it later by semantic text.
hits = client.recall(text="what coffee does Ada like?", limit=5)
for hit in hits:
    print(hit.relevance, hit.data)
```

## Configuration

| Parameter  | Type            | Default                     | Description                          |
|------------|-----------------|-----------------------------|--------------------------------------|
| `base_url` | `str`           | `http://127.0.0.1:19090`    | AIngle Cortex base URL.              |
| `token`    | `str` or `None` | `None`                      | Optional bearer token for a namespace. |
| `timeout`  | `float`         | `30.0`                      | Request timeout in seconds.          |

Pass a token when a namespace requires authentication:

```python
client = AIngleClient(base_url="https://cortex.example.com", token="my-token")
```

## API Reference

All methods are synchronous and raise `AIngleError(status, message)` on any
non-2xx response.

### Health and stats

| Method           | Description                            |
|------------------|----------------------------------------|
| `health()`       | Service health and component status.   |
| `stats()`        | Graph and server statistics.           |

### Memory

| Method                                                  | Description                              |
|---------------------------------------------------------|------------------------------------------|
| `remember(entry_type, data, *, tags, importance, embedding)` | Store a memory, returns `{ id }`.   |
| `recall(*, text, tags, entry_type, min_importance, limit)`   | Recall memories by text or tags.    |
| `search(*, embedding, k, min_similarity, entry_type, tags)`  | Vector / semantic search.           |
| `memory_stats()`                                        | Short and long term memory counts.       |
| `forget(id)`                                            | Delete a memory by id.                   |

### Triples (semantic graph)

The triple `object` is an untagged value: `str`, `int`, `float`, `bool`, or a
node reference `{"node": "http://example.org/thing"}`. Use the `node_ref`
helper to build a node reference.

```python
from aingle_sdk import node_ref

client.create_triple("ada", "likes", "coffee")
client.create_triple("ada", "knows", node_ref("http://example.org/grace"))
```

| Method                                                       | Description                       |
|--------------------------------------------------------------|-----------------------------------|
| `create_triple(subject, predicate, object)`                  | Insert one triple.                |
| `list_triples(*, subject, predicate, object, limit, offset)` | List triples with filters.        |
| `get_triple(id)`                                             | Fetch a triple by id.             |
| `delete_triple(id)`                                          | Delete a triple by id.            |

### Query

| Method                                          | Description                          |
|-------------------------------------------------|--------------------------------------|
| `query(*, subject, predicate, object, limit)`   | Pattern match over triples.          |
| `subjects(*, predicate, limit)`                 | Distinct subjects, optional filter.  |
| `predicates(*, subject, limit)`                 | Distinct predicates, optional filter. |

## Error handling

```python
from aingle_sdk import AIngleClient, AIngleError

client = AIngleClient()
try:
    client.get_triple("does-not-exist")
except AIngleError as err:
    print(err.status, err.message)
```

## Development

```bash
# Install dev dependencies.
pip install -e ".[dev]"

# Run tests.
pytest

# Type checking.
mypy src

# Linting.
ruff check src
```

## License

Apache-2.0, see [LICENSE](LICENSE).

## Links

- [AIngle Core](https://github.com/ApiliumCode/aingle)
- [Documentation](https://docs.apilium.com)
