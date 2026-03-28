# Meeting Notes Extractor — Product Specification

## Problem

Meeting notes are often unstructured, inconsistent, and difficult to act on. Important information such as decisions, action items, and ownership can be buried in freeform text, leading to missed follow-ups and lack of clarity.

There is a need for a lightweight tool that converts raw meeting notes into structured, actionable data.

---

## Target User

* Individual contributors who take their own notes
* Small teams without formal note-taking tools
* Engineers and product managers who want quick summaries and action extraction

---

## v1 Scope

The system will:

* Accept raw meeting notes as text input
* Extract:

  * summary
  * decisions
  * action items (task, owner, due date)
  * open questions
  * ambiguities
* Return structured JSON conforming to `docs/api.md`

The system will NOT:

* Store meeting history
* Integrate with calendars, Slack, or email
* Handle file uploads (text input only)
* Provide real-time collaboration
* Guarantee perfect accuracy (best-effort extraction)

---

## Acceptance Criteria

v1 is successful when:

* users can paste notes and get structured output in under a few seconds
* output is consistently formatted according to the API schema
* action items include owners and due dates when inferable
* ambiguities are surfaced rather than hidden
* malformed inputs are rejected clearly and consistently

---

## Example Use Case

Input:

"Alice said the migration slips by 2 weeks. Bob owns the rollback doc by Friday. Do we need to notify partners?"

Expected output characteristics:

* summary of delay and assigned work
* decision that the migration is delayed
* action item that Bob writes the rollback document
* open question about notifying partners
* ambiguity that the exact migration date is unclear

---

## Non-Goals

* Building a full meeting management system
* Achieving perfect natural language understanding
* Supporting multiple input formats beyond plain text
* Handling extremely large documents or transcripts (v1)

---

## Constraints

* Must remain simple and lightweight
* Must use a single-pass extraction (no complex multi-agent workflows)
* Must be easy to run locally and deploy

---

## Near-Term Implementation Priorities

The next meaningful improvements should focus on:

* replacing the dummy extractor with a real extraction implementation
* keeping output aligned with the documented schema
* adding regression tests for realistic note samples
* making ambiguity handling explicit rather than silently guessing

---

## Future Considerations (Not v1)

* Export to Markdown or email summary
* Save and retrieve past meetings
* Integration with task tracking systems
* Confidence scoring for extracted items
* Highlighting extracted spans from original text
