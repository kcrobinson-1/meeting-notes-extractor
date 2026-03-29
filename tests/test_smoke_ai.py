import importlib.util
import tempfile
from pathlib import Path
from typing import Any

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "smoke_ai.py"
_SPEC = importlib.util.spec_from_file_location("smoke_ai_script", _MODULE_PATH)
assert _SPEC is not None
assert _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

RunningServer: Any = _MODULE.RunningServer
format_server_logs = _MODULE.format_server_logs
validate_smoke_response = _MODULE.validate_smoke_response
wait_for_server = _MODULE.wait_for_server


class _ExitedProcess:
    def poll(self) -> int:
        return 1


def _running_server_with_logs(log_text: str) -> Any:
    log_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    log_file.write(log_text)
    log_file.flush()
    return RunningServer(process=_ExitedProcess(), log_file=log_file)


def test_validate_smoke_response_accepts_extract_response_payload() -> None:
    payload = """
    {
      "summary": "AI summary",
      "decisions": [],
      "action_items": [
        {
          "task": "Finish rollback doc",
          "owner": "Bob",
          "due_date": null
        }
      ],
      "open_questions": [],
      "ambiguities": []
    }
    """

    response = validate_smoke_response(payload)

    assert response["summary"] == "AI summary"
    assert response["action_items"][0]["task"] == "Finish rollback doc"


def test_validate_smoke_response_rejects_contract_mismatches() -> None:
    with pytest.raises(
        RuntimeError, match="did not match the ExtractResponse contract"
    ):
        validate_smoke_response('{"summary": "AI summary", "decisions": []}')


def test_validate_smoke_response_requires_structured_items() -> None:
    with pytest.raises(RuntimeError, match="did not extract any structured items"):
        validate_smoke_response(
            """
            {
              "summary": "AI summary",
              "decisions": [],
              "action_items": [],
              "open_questions": [],
              "ambiguities": []
            }
            """
        )


def test_wait_for_server_includes_server_logs_when_process_exits() -> None:
    server = _running_server_with_logs("Traceback\\nserver exploded")

    try:
        with pytest.raises(RuntimeError, match="server exploded"):
            wait_for_server("http://127.0.0.1:8001/health", server)
    finally:
        server.log_file.close()


def test_format_server_logs_reports_empty_output() -> None:
    server = _running_server_with_logs("")

    try:
        assert format_server_logs(server) == "\n\nServer log output was empty."
    finally:
        server.log_file.close()
