import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.settings import get_openai_api_key

STARTUP_TIMEOUT_SECONDS = 20
REQUEST_TIMEOUT_SECONDS = 30
REQUIRED_RESPONSE_KEYS = {
    "summary",
    "decisions",
    "action_items",
    "open_questions",
    "ambiguities",
}


@dataclass
class RunningServer:
    process: subprocess.Popen[str]
    log_file: TextIO


def main() -> int:
    request_path = Path(
        os.getenv("SMOKE_AI_REQUEST", "examples/extract-request.json")
    ).resolve()
    host = os.getenv("SMOKE_AI_HOST", "127.0.0.1")
    port = int(os.getenv("SMOKE_AI_PORT", "8001"))
    base_url = f"http://{host}:{port}"

    get_openai_api_key()

    if not request_path.exists():
        print(f"Smoke AI request file not found: {request_path}", file=sys.stderr)
        return 1

    server = start_server(host=host, port=port)

    try:
        wait_for_server(f"{base_url}/health", server)
        response_body = post_json(
            url=f"{base_url}/extract",
            payload=request_path.read_text(encoding="utf-8"),
            server=server,
        )
        print(json.dumps(validate_smoke_response(response_body), indent=2))
        return 0
    finally:
        stop_server(server)


def start_server(host: str, port: int) -> RunningServer:
    server_env = os.environ.copy()
    server_env["EXTRACTOR_STRATEGY"] = "ai"
    log_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")

    return RunningServer(
        process=subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                host,
                "--port",
                str(port),
            ],
            env=server_env,
            stdout=log_file,
            stderr=log_file,
            text=True,
        ),
        log_file=log_file,
    )


def wait_for_server(health_url: str, server: RunningServer) -> None:
    deadline = time.time() + STARTUP_TIMEOUT_SECONDS

    while time.time() < deadline:
        if server.process.poll() is not None:
            raise RuntimeError(
                "AI smoke server exited before the health check succeeded."
                + format_server_logs(server)
            )
        try:
            with urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    return
        except URLError:
            time.sleep(0.25)

    raise RuntimeError(
        f"Timed out waiting for AI smoke server at {health_url}."
        + format_server_logs(server)
    )


def post_json(url: str, payload: str, server: RunningServer) -> str:
    request = Request(
        url,
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        parsed_url = urlparse(url)
        raise RuntimeError(
            f"AI smoke request failed for {parsed_url.path}: HTTP {exc.code}: {body}"
            + format_server_logs(server)
        ) from exc


def validate_smoke_response(response_body: str) -> dict[str, Any]:
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI smoke response was not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("AI smoke response must be a JSON object.")

    payload_keys = set(payload)
    missing_keys = REQUIRED_RESPONSE_KEYS - payload_keys
    extra_keys = payload_keys - REQUIRED_RESPONSE_KEYS
    if missing_keys or extra_keys:
        details: list[str] = []
        if missing_keys:
            details.append("missing keys: " + ", ".join(sorted(missing_keys)))
        if extra_keys:
            details.append("unexpected keys: " + ", ".join(sorted(extra_keys)))
        raise RuntimeError(
            "AI smoke response did not match the ExtractResponse contract ("
            + "; ".join(details)
            + ")."
        )

    summary = payload["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise RuntimeError("AI smoke response summary must be a non-empty string.")

    for key in ("decisions", "action_items", "open_questions", "ambiguities"):
        if not isinstance(payload[key], list):
            raise RuntimeError(f"AI smoke response field '{key}' must be a list.")

    if payload["action_items"]:
        for index, action_item in enumerate(payload["action_items"], start=1):
            if not isinstance(action_item, dict):
                raise RuntimeError(
                    f"AI smoke response action item #{index} must be an object."
                )
            task = action_item.get("task")
            owner = action_item.get("owner")
            due_date = action_item.get("due_date")
            if not isinstance(task, str) or not task.strip():
                raise RuntimeError(
                    "AI smoke response action item "
                    f"#{index} must include a non-empty task."
                )
            if owner is not None and not isinstance(owner, str):
                raise RuntimeError(
                    "AI smoke response action item "
                    f"#{index} owner must be a string or null."
                )
            if due_date is not None and not isinstance(due_date, str):
                raise RuntimeError(
                    "AI smoke response action item "
                    f"#{index} due_date must be a string or null."
                )

    structured_fields = (
        "decisions",
        "action_items",
        "open_questions",
        "ambiguities",
    )
    if not any(payload[key] for key in structured_fields):
        raise RuntimeError(
            "AI smoke response did not extract any structured items "
            "from the sample payload."
        )

    return payload


def format_server_logs(server: RunningServer) -> str:
    server.log_file.flush()
    server.log_file.seek(0)
    log_output = server.log_file.read().strip()
    if not log_output:
        return "\n\nServer log output was empty."

    log_lines = log_output.splitlines()
    tail = "\n".join(log_lines[-20:])
    return "\n\nServer log tail:\n" + tail


def stop_server(server: RunningServer) -> None:
    if server.process.poll() is None:
        server.process.terminate()
        try:
            server.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.process.kill()
            server.process.wait(timeout=5)

    server.log_file.close()


if __name__ == "__main__":
    raise SystemExit(main())
