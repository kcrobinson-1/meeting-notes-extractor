# Meeting Notes Extractor API

## Overview

This API extracts structured information from raw meeting notes.

## Endpoint

### POST /extract

Extract structured meeting data from freeform notes.

## Request

```json
{
  "meeting_title": "Platform sync",
  "meeting_date": "2026-03-27",
  "notes_text": "Alice said the migration slips by 2 weeks. Bob owns the rollback doc by Friday."
}
```

### Fields

* `meeting_title` (string, optional): Title of the meeting. Blank strings are rejected.
* `meeting_date` (string, optional): ISO date string in `YYYY-MM-DD` format
* `notes_text` (string, required): Raw meeting notes. Blank strings are rejected.
* Additional request fields are rejected

## Response

```json
{
  "summary": "The team delayed the migration by two weeks and assigned follow-up documentation.",
  "decisions": [
    "Delay the migration by two weeks"
  ],
  "action_items": [
    {
      "task": "Write rollback document",
      "owner": "Bob",
      "due_date": "2026-04-03"
    }
  ],
  "open_questions": [
    "Does the new migration date affect the partner launch?"
  ],
  "ambiguities": [
    "Due date for migration not explicitly stated"
  ]
}
```

### Fields

* `summary` (string): Concise summary of the meeting
* `decisions` (string[]): Key decisions made
* `action_items` (object[]): List of tasks

  * `task` (string): Description of the task
  * `owner` (string, optional): Responsible person
  * `due_date` (string, optional): ISO date string
* `open_questions` (string[]): Outstanding questions
* `ambiguities` (string[]): Unclear or inferred information

## Error Handling

* `422 Unprocessable Entity`: Malformed JSON, validation errors, or unsupported request fields
* `500 Internal Server Error`: Unexpected failures

## Example

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  --data @examples/extract-request.json
```

FastAPI also exposes a generated OpenAPI schema for this API at `GET /openapi.json`.
