# Meeting Notes Extractor — Architecture

## Overview

This project is a small FastAPI service that accepts raw meeting notes and returns structured extracted data.

The system is intentionally simple:

* FastAPI app for request handling and validation
* pluggable extraction layer responsible for interpreting notes and returning validated structured output

---

## High-Level Flow

```text
Client sends POST request with meeting notes and optional metadata
→ FastAPI validates request payload
→ Extraction module selects an extraction strategy and interprets the notes
→ FastAPI validates response schema
→ Client receives structured output
```

---

## System Components

### FastAPI App

Responsibilities:

* expose HTTP endpoints
* validate request bodies
* call extraction logic
* validate and return structured responses
* handle errors consistently

Planned implementation:

* FastAPI
* Pydantic models for request and response schemas
* thin route handlers
* no persistence in v1

### Extraction Layer

Responsibilities:

* define extraction strategies
* interpret note text into the response schema
* parse and validate extracted output
* surface ambiguities instead of hiding uncertainty

Planned implementation:

* isolated module such as `extractor.py`
* one main extraction function called by the route layer
* strategy selection happens inside the extraction layer
* deterministic extraction is the default current implementation
* AI extraction remains stubbed until model integration is added
* no agent framework in v1
* single-pass extraction workflow

---

## Design Principles

* schema-first: `docs/api.md` defines the contract
* small, explicit modules
* minimal dependencies
* no hidden magic or unnecessary abstractions
* route handlers should remain thin
* logic changes should be covered by tests

---

## API Boundaries

### Frontend to Backend

Clients should know only:

* endpoint URL
* request schema
* response schema
* error shape

Clients should not know prompt details or model behavior.

### Backend to LLM

The extraction layer owns:

* extraction strategy selection
* extraction rules
* output validation
* fallback behavior
* interpretation of optional meeting metadata

The rest of the application should not be tightly coupled to any specific extraction strategy.

---

## Implementation Boundaries

Keep these boundaries intact as the project grows:

* request and response validation stay in Pydantic models
* HTTP handlers stay thin and delegate work to the extraction layer
* extraction logic owns prompt construction, model calls, and output normalization
* tests should cover the API surface and lower-level extraction or schema behavior separately
* docs should stay split by purpose rather than repeating the same facts in multiple files

---

## Error Handling Strategy

Expected categories:

* validation errors for malformed requests
* extraction errors for invalid model output
* infrastructure errors for network or API failures

Goals:

* return clear HTTP status codes
* avoid leaking internal implementation details
* keep failures explicit and debuggable

---

## Non-Goals for v1

This architecture does not include:

* database or persistence layer
* background jobs
* authentication or user accounts
* file uploads
* streaming responses
* agent frameworks or orchestration systems

---

## Likely Near-Term Extensions

These may be added later if the project grows:

* saved meeting history
* export to Markdown or email
* confidence metadata
* traceability from extracted item back to source text
* simple eval harness for regression testing
