from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://token-plan-ams.xiaomimimo.com/v1"
DEFAULT_MODELS = ("mimo-v2.5-pro", "mimo-v2.5")


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _usage_dict(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump(exclude_none=True)
    if isinstance(usage, dict):
        return usage
    return dict(getattr(usage, "__dict__", {}))


def _print_result(label: str, payload: dict[str, Any]) -> None:
    print(f"\n## {label}")
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def chat_check(client: Any, model: str) -> None:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly: MiMo chat OK"}],
        temperature=0,
        max_tokens=128,
    )
    _print_result(
        f"chat {model}",
        {
            "content": response.choices[0].message.content,
            "usage": _usage_dict(response),
        },
    )


def streaming_check(client: Any, model: str) -> None:
    chunks: list[str] = []
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Count from 1 to 3, comma separated."}],
        temperature=0,
        max_tokens=128,
        stream_options={"include_usage": True},
        stream=True,
    )
    usage: dict[str, Any] = {}
    for chunk in stream:
        chunk_usage = _usage_dict(chunk)
        if chunk_usage:
            usage = chunk_usage
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            chunks.append(content)
    _print_result(f"stream {model}", {"content": "".join(chunks), "usage": usage})


def tool_call_check(client: Any, model: str) -> None:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Use the tool to get the weather for Pune."}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a city.",
                    "parameters": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                        "required": ["city"],
                    },
                },
            }
        ],
        tool_choice="auto",
        temperature=0,
        max_tokens=128,
    )
    message = response.choices[0].message
    tool_calls = getattr(message, "tool_calls", None) or []
    _print_result(
        f"tool calling {model}",
        {
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                }
                for call in tool_calls
            ],
            "usage": _usage_dict(response),
        },
    )


def multimodal_check(client: Any, model: str) -> None:
    pixel_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/ax"
        "z8WkAAAAASUVORK5CYII="
    )
    image_data = base64.b64encode(pixel_png).decode("ascii")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What kind of file is attached? Answer briefly."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                ],
            }
        ],
        temperature=0,
        max_tokens=128,
    )
    _print_result(
        f"multimodal {model}",
        {
            "content": response.choices[0].message.content,
            "usage": _usage_dict(response),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test Xiaomi MiMo OpenAI-compatible API behavior.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--models", nargs="*", default=list(DEFAULT_MODELS))
    parser.add_argument("--skip-multimodal", action="store_true")
    args = parser.parse_args()

    _load_dotenv()
    api_key = os.getenv("MIMO_API_KEY")
    if not api_key:
        raise SystemExit("MIMO_API_KEY is not set. Add it to .env or the environment.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install the OpenAI SDK first: pip install openai") from exc

    client = OpenAI(base_url=args.base_url, api_key=api_key, timeout=60.0)
    for model in args.models:
        chat_check(client, model)
        streaming_check(client, model)
        tool_call_check(client, model)
        if not args.skip_multimodal:
            try:
                multimodal_check(client, model)
            except Exception as exc:
                _print_result(f"multimodal {model}", {"supported": False, "error": str(exc)})


if __name__ == "__main__":
    main()
