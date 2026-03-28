# meeting-notes-extractor

A minimal FastAPI service for turning freeform meeting notes into structured output.

## Current Status

The extraction endpoint is still stubbed. It validates the request shape and returns
a schema-correct dummy response that uses the provided meeting metadata, which gives
us a stable API surface to build against before adding real extraction logic.

## Quick Start

```bash
make venv
make run
```

The service exposes `GET /health` and returns:

```json
{"status":"ok"}
```

Useful local commands:

```bash
make lint
make typecheck
make test
make build
make clean
make reset-venv
make compile-deps
make smoke
```

Use `make reset-venv` when you want to rebuild the virtual environment from scratch
after dependency or interpreter issues.
Use `make compile-deps` after changing `pyproject.toml` so the committed dependency
lockfile stays in sync.
Use `make smoke` to post the checked-in sample request to a running local server.

## Docs Map

- [docs/api.md](docs/api.md): request and response contract for `POST /extract`
- [docs/dev.md](docs/dev.md): local setup, `make` workflow, and contributor guidance
- [docs/architecture.md](docs/architecture.md): system boundaries and extension points
- [docs/product.md](docs/product.md): product goals, acceptance criteria, and near-term priorities
