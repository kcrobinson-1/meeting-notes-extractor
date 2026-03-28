import re
from collections.abc import Callable
from datetime import date, timedelta

from app.extractors.base import MeetingNotesExtractor
from app.schemas import ActionItem, ExtractRequest, ExtractResponse

WEEKDAY_NAMES = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

ACTION_PATTERNS = (
    re.compile(
        r"^(?P<owner>[A-Z][a-z]+) owns (?P<task>.+?)(?: by (?P<due>[^.?!]+))?$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?P<owner>[A-Z][a-z]+) will (?P<task>.+?)(?: by (?P<due>[^.?!]+))?$",
        re.IGNORECASE,
    ),
)

DECISION_KEYWORDS = (
    "decided",
    "agreed",
    "approved",
    "delay",
    "delayed",
    "slips by",
)


class DeterministicMeetingNotesExtractor(MeetingNotesExtractor):
    def __init__(
        self, reference_date_provider: Callable[[], date] = date.today
    ) -> None:
        self._reference_date_provider = reference_date_provider

    def extract(self, request: ExtractRequest) -> ExtractResponse:
        sentences = self._split_sentences(request.notes_text)
        decisions: list[str] = []
        action_items: list[ActionItem] = []
        open_questions: list[str] = []
        ambiguities: list[str] = []
        reference_date = request.meeting_date or self._reference_date_provider()

        for sentence in sentences:
            if self._is_question(sentence):
                open_questions.append(
                    self._clean_sentence(sentence, keep_question_mark=True)
                )
                continue

            action_item, action_ambiguities = self._extract_action_item(
                sentence, reference_date
            )
            if action_item is not None:
                action_items.append(action_item)
                ambiguities.extend(action_ambiguities)
                continue

            decision = self._extract_decision(sentence)
            if decision is not None:
                decisions.append(decision)

        if not decisions and not action_items and not open_questions:
            ambiguities.append("No structured items could be confidently extracted.")

        summary = self._build_summary(
            meeting_title=request.meeting_title,
            decisions=decisions,
            action_items=action_items,
            open_questions=open_questions,
        )

        return ExtractResponse(
            summary=summary,
            decisions=decisions,
            action_items=action_items,
            open_questions=open_questions,
            ambiguities=ambiguities,
        )

    def _split_sentences(self, notes_text: str) -> list[str]:
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.?!])\s+", notes_text.strip())
            if sentence.strip()
        ]

    def _is_question(self, sentence: str) -> bool:
        return sentence.rstrip().endswith("?")

    def _extract_action_item(
        self, sentence: str, reference_date: date
    ) -> tuple[ActionItem | None, list[str]]:
        for pattern in ACTION_PATTERNS:
            match = pattern.match(self._clean_sentence(sentence))
            if match is None:
                continue

            task = match.group("task").strip()
            owner = self._normalize_name(match.group("owner"))
            due_phrase = match.group("due")
            due_date, ambiguity = self._parse_due_date(due_phrase, reference_date, task)

            return (
                ActionItem(task=task, owner=owner, due_date=due_date),
                [ambiguity] if ambiguity else [],
            )

        return None, []

    def _extract_decision(self, sentence: str) -> str | None:
        cleaned = self._clean_sentence(sentence)
        candidate = self._strip_attribution(cleaned)

        if any(keyword in candidate.lower() for keyword in DECISION_KEYWORDS):
            return candidate

        return None

    def _strip_attribution(self, sentence: str) -> str:
        match = re.match(r"^[A-Z][a-z]+ said (.+)$", sentence, re.IGNORECASE)
        if match is None:
            return sentence

        attributed_clause = match.group(1).strip()
        return attributed_clause[:1].upper() + attributed_clause[1:]

    def _parse_due_date(
        self, due_phrase: str | None, reference_date: date, task: str
    ) -> tuple[date | None, str | None]:
        if due_phrase is None:
            return None, None

        normalized = due_phrase.strip()

        try:
            return date.fromisoformat(normalized), None
        except ValueError:
            pass

        weekday = WEEKDAY_NAMES.get(normalized.lower())
        if weekday is None:
            return (
                None,
                f'Could not normalize due date "{normalized}" for task "{task}".',
            )

        return self._next_weekday(reference_date, weekday), None

    def _next_weekday(self, start: date, target_weekday: int) -> date:
        offset = (target_weekday - start.weekday()) % 7
        if offset == 0:
            offset = 7
        return start + timedelta(days=offset)

    def _build_summary(
        self,
        meeting_title: str | None,
        decisions: list[str],
        action_items: list[ActionItem],
        open_questions: list[str],
    ) -> str:
        topic = (
            f'The meeting "{meeting_title}" covered'
            if meeting_title
            else "The meeting notes covered"
        )

        highlights: list[str] = []

        if decisions:
            highlights.append(decisions[0].lower())

        if action_items:
            first_item = action_items[0]
            owner_text = first_item.owner or "someone"
            highlights.append(f"{owner_text} owning {first_item.task}")

        if open_questions:
            question_topic = open_questions[0].rstrip("?").lower()
            highlights.append(f"an open question about {question_topic}")

        if not highlights:
            return f"{topic} follow-up items that still need clarification."

        return f"{topic} " + ", ".join(highlights[:3]) + "."

    def _clean_sentence(self, sentence: str, keep_question_mark: bool = False) -> str:
        cleaned = sentence.strip()
        if keep_question_mark:
            return cleaned
        return cleaned.rstrip(".?!").strip()

    def _normalize_name(self, name: str) -> str:
        normalized = name.strip()
        return normalized[:1].upper() + normalized[1:]
