from __future__ import annotations

import base64
from dataclasses import dataclass, field
import json
import mimetypes
import re
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from ..media import Audio, File, Image, Video
from ..protocol import ToolBatch, ToolCall, ToolSpec

USAGE_METRICS_NONE = "none"
USAGE_METRICS_BASIC = "basic"
USAGE_METRICS_RICH = "rich"

STRUCTURED_OUTPUT_NONE = "none"
STRUCTURED_OUTPUT_CLIENT_VALIDATED = "client_validated"
STRUCTURED_OUTPUT_NATIVE_JSON_OBJECT = "native_json_object"
STRUCTURED_OUTPUT_NATIVE_JSON_SCHEMA = "native_json_schema"


@dataclass(slots=True)
class ProviderCapabilities:
    provider: str
    supports_tool_calling: bool = True
    supports_parallel_tool_calls: bool = False
    input_modalities: list[str] = field(default_factory=lambda: ["text"])
    supports_tool_media_output: bool = False
    supports_finalize_streaming: bool = False
    usage_metrics_quality: str = USAGE_METRICS_BASIC
    supports_reasoning_metadata: bool = False
    structured_output_support: str = STRUCTURED_OUTPUT_NONE
    supports_native_async: bool = False
    allow_finalize_stream_fallback: bool = True

    def supports_input_modality(self, modality: str) -> bool:
        return modality in set(self.input_modalities)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "supports_tool_calling": self.supports_tool_calling,
            "supports_parallel_tool_calls": self.supports_parallel_tool_calls,
            "input_modalities": sorted(set(self.input_modalities)),
            "supports_tool_media_output": self.supports_tool_media_output,
            "supports_finalize_streaming": self.supports_finalize_streaming,
            "usage_metrics_quality": self.usage_metrics_quality,
            "supports_reasoning_metadata": self.supports_reasoning_metadata,
            "structured_output_support": self.structured_output_support,
            "supports_native_async": self.supports_native_async,
            "allow_finalize_stream_fallback": self.allow_finalize_stream_fallback,
        }


def capabilities_from_any(value: Any) -> ProviderCapabilities | None:
    if value is None:
        return None
    if isinstance(value, ProviderCapabilities):
        return value
    if isinstance(value, dict):
        provider = str(value.get("provider") or "unknown")
        input_modalities = value.get("input_modalities")
        if not isinstance(input_modalities, list):
            input_modalities = ["text"]
        normalized_modalities = [str(item) for item in input_modalities if isinstance(item, (str, int, float))]
        return ProviderCapabilities(
            provider=provider,
            supports_tool_calling=bool(value.get("supports_tool_calling", True)),
            supports_parallel_tool_calls=bool(value.get("supports_parallel_tool_calls", False)),
            input_modalities=normalized_modalities or ["text"],
            supports_tool_media_output=bool(value.get("supports_tool_media_output", False)),
            supports_finalize_streaming=bool(value.get("supports_finalize_streaming", False)),
            usage_metrics_quality=str(value.get("usage_metrics_quality", USAGE_METRICS_BASIC)),
            supports_reasoning_metadata=bool(value.get("supports_reasoning_metadata", False)),
            structured_output_support=str(value.get("structured_output_support", STRUCTURED_OUTPUT_NONE)),
            supports_native_async=bool(value.get("supports_native_async", False)),
            allow_finalize_stream_fallback=bool(value.get("allow_finalize_stream_fallback", True)),
        )
    return None


def _read_value(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def _first_int(source: Any, *keys: str) -> int | None:
    for key in keys:
        value = _coerce_int(_read_value(source, key))
        if value is not None:
            return value
    return None


def extract_usage_metrics(response: Any) -> dict[str, int]:
    usage = _read_value(response, "usage")
    if usage is None:
        usage = _read_value(response, "usage_metadata")
    if usage is None:
        usage = _read_value(response, "usageMetadata")
    if usage is None:
        return {}

    prompt_tokens = _first_int(
        usage,
        "prompt_tokens",
        "input_tokens",
        "prompt_token_count",
        "promptTokenCount",
        "inputTokenCount",
    )

    completion_tokens = _first_int(
        usage,
        "completion_tokens",
        "output_tokens",
        "candidates_token_count",
        "response_token_count",
        "completionTokenCount",
        "outputTokenCount",
        "candidatesTokenCount",
        "responseTokenCount",
    )

    total_tokens = _first_int(
        usage,
        "total_tokens",
        "total_token_count",
        "totalTokenCount",
    )
    if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
        total_tokens = prompt_tokens + completion_tokens

    reasoning_tokens: int | None = None
    completion_details = _read_value(usage, "completion_tokens_details")
    if completion_details is None:
        completion_details = _read_value(usage, "completionTokensDetails")
    if completion_details is not None:
        reasoning_tokens = _first_int(completion_details, "reasoning_tokens", "reasoningTokenCount")
    if reasoning_tokens is None:
        output_token_details = _read_value(usage, "output_token_details")
        if output_token_details is None:
            output_token_details = _read_value(usage, "outputTokenDetails")
        if output_token_details is not None:
            reasoning_tokens = _first_int(output_token_details, "reasoning", "reasoning_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = _first_int(usage, "thoughts_token_count", "thoughtsTokenCount")

    prompt_details = _read_value(usage, "prompt_tokens_details")
    if prompt_details is None:
        prompt_details = _read_value(usage, "promptTokensDetails")
    cached_input_tokens = None
    cache_write_tokens = None
    if prompt_details is not None:
        cached_input_tokens = _first_int(prompt_details, "cached_tokens", "cachedTokens")
        cache_write_tokens = _first_int(prompt_details, "cache_write_tokens", "cacheWriteTokens")
    if cached_input_tokens is None:
        cached_input_tokens = _first_int(
            usage,
            "cached_content_token_count",
            "cachedContentTokenCount",
        )

    cache_creation_input_tokens = _first_int(
        usage,
        "cache_creation_input_tokens",
        "cacheCreationInputTokens",
    )
    cache_read_input_tokens = _first_int(
        usage,
        "cache_read_input_tokens",
        "cacheReadInputTokens",
    )
    tool_use_prompt_tokens = _first_int(
        usage,
        "tool_use_prompt_token_count",
        "toolUsePromptTokenCount",
    )

    metrics: dict[str, int] = {}
    if prompt_tokens is not None:
        metrics["input_tokens"] = prompt_tokens
    if completion_tokens is not None:
        metrics["output_tokens"] = completion_tokens
    if total_tokens is not None:
        metrics["total_tokens"] = total_tokens
    if reasoning_tokens is not None:
        metrics["reasoning_tokens"] = reasoning_tokens
    if cached_input_tokens is not None:
        metrics["cached_input_tokens"] = cached_input_tokens
    if cache_write_tokens is not None:
        metrics["cache_write_tokens"] = cache_write_tokens
    if cache_creation_input_tokens is not None:
        metrics["cache_creation_input_tokens"] = cache_creation_input_tokens
    if cache_read_input_tokens is not None:
        metrics["cache_read_input_tokens"] = cache_read_input_tokens
    if tool_use_prompt_tokens is not None:
        metrics["tool_use_prompt_tokens"] = tool_use_prompt_tokens
    return metrics


def extract_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        if "$ref" in value and isinstance(value["$ref"], str):
            refs.append(value["$ref"])
        for item in value.values():
            refs.extend(extract_refs(item))
        return refs
    if isinstance(value, list):
        for item in value:
            refs.extend(extract_refs(item))
    return refs


def normalize_refs(value: Any, id_by_index: dict[int, str], current_idx: int | None = None) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if key == "$ref":
                if isinstance(item, int) and item in id_by_index:
                    normalized[key] = id_by_index[item]
                elif isinstance(item, str) and item.isdigit():
                    idx = int(item)
                    normalized[key] = id_by_index.get(idx, item)
                elif isinstance(item, str):
                    match = re.search(r"(\d+)$", item)
                    if match:
                        idx = int(match.group(1))
                        normalized[key] = id_by_index.get(idx, item)
                    elif item.lower() in ("result", "last", "last_call", "prev", "previous"):
                        # Map to previous call if available
                        target_idx = current_idx - 1 if current_idx is not None else 0
                        normalized[key] = id_by_index.get(max(0, target_idx), item)
                    else:
                        normalized[key] = item
                else:
                    normalized[key] = item
            else:
                normalized[key] = normalize_refs(item, id_by_index, current_idx)
        return normalized
    if isinstance(value, list):
        return [normalize_refs(item, id_by_index, current_idx) for item in value]
    return value


def safe_load_arguments(raw_args: str | None) -> dict[str, Any]:
    raw = raw_args or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw_arguments": raw}
    if isinstance(parsed, dict):
        return parsed
    return {"_raw_arguments": raw}


def _coerce_inline_scalar(value: str) -> Any:
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    try:
        return json.loads(stripped)
    except Exception:
        return stripped


def _schema_properties_for_tool(tool_name: str, tools: list[ToolSpec]) -> dict[str, Any]:
    for tool in tools:
        if tool.name != tool_name:
            continue
        schema = tool.input_schema if isinstance(tool.input_schema, dict) else {}
        properties = schema.get("properties")
        return properties if isinstance(properties, dict) else {}
    return {}


def _coerce_inline_argument_for_schema(value: str, schema: dict[str, Any] | None) -> Any:
    if not isinstance(schema, dict):
        return _coerce_inline_scalar(value)
    schema_type = schema.get("type")
    stripped = value.strip()
    if schema_type == "boolean":
        lowered = stripped.lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
    if schema_type == "integer":
        try:
            return int(stripped)
        except ValueError:
            return _coerce_inline_scalar(value)
    if schema_type == "number":
        try:
            return float(stripped)
        except ValueError:
            return _coerce_inline_scalar(value)
    if schema_type in {"object", "array"}:
        try:
            return json.loads(stripped)
        except Exception:
            return _coerce_inline_scalar(value)
    return _coerce_inline_scalar(value)


def clean_inline_tool_content(content: str) -> str:
    cleaned = re.sub(r"<tool_call>.*?</tool_call>", "", content, flags=re.IGNORECASE | re.DOTALL)
    return cleaned.strip()


def normalize_inline_tool_name(tool_name: str, tools: list[ToolSpec]) -> str:
    candidate = tool_name.strip()
    available = {tool.name for tool in tools}
    if candidate in available:
        return candidate
    aliases = {
        "bash": "shell.run_command",
        "shell": "shell.run_command",
        "run_command": "shell.run_command",
        "read_file": "file.read_file",
        "write_file": "file.write_file",
        "list_files": "file.list_files",
        "search_files": "file.search_in_files",
        "search_in_files": "file.search_in_files",
    }
    alias = aliases.get(candidate.lower())
    if alias in available:
        return alias
    suffix_matches = [name for name in available if name.endswith(f".{candidate}")]
    if len(suffix_matches) == 1:
        return suffix_matches[0]
    return candidate


def parse_inline_tool_calls(content: str, tools: list[ToolSpec]) -> tuple[list[dict[str, Any]], str]:
    inline_calls: list[dict[str, Any]] = []
    for idx, block_match in enumerate(
        re.finditer(r"<tool_call>\s*(.*?)\s*</tool_call>", content, flags=re.IGNORECASE | re.DOTALL),
        start=1,
    ):
        block = block_match.group(1)
        fn_match = re.search(
            r"<function=([^>\s]+)>\s*(.*?)(?:</function>|$)",
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not fn_match:
            continue
        tool_name = normalize_inline_tool_name(fn_match.group(1), tools)
        fn_body = fn_match.group(2)
        properties = _schema_properties_for_tool(tool_name, tools)
        arguments: dict[str, Any] = {}
        for param_match in re.finditer(
            r"<parameter=([^>\s]+)>\s*(.*?)(?:</parameter>|(?=<parameter=)|$)",
            fn_body,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            param_name = param_match.group(1).strip()
            if not param_name:
                continue
            if param_name not in properties and tool_name == "shell.run_command" and param_name in {"workdir", "cwd"}:
                continue
            param_value = param_match.group(2).strip()
            arguments[param_name] = _coerce_inline_argument_for_schema(param_value, properties.get(param_name))
        if tool_name:
            inline_calls.append(
                {
                    "id": f"inline_call_{idx}",
                    "name": tool_name,
                    "arguments": arguments,
                }
            )
    return inline_calls, clean_inline_tool_content(content)


def calls_to_dependency_batches(calls: list[ToolCall]) -> list[ToolBatch]:
    remaining: dict[str, ToolCall] = {call.id: call for call in calls}
    ordered_ids = [call.id for call in calls]
    done: set[str] = set()
    batches: list[ToolBatch] = []

    while remaining:
        ready_ids = [
            call_id
            for call_id in ordered_ids
            if call_id in remaining and all(dep in done for dep in remaining[call_id].depends_on)
        ]
        if not ready_ids:
            unresolved_calls = [remaining[call_id] for call_id in ordered_ids if call_id in remaining]
            batches.append(ToolBatch(mode="sequential", calls=unresolved_calls))
            break

        ready_calls = [remaining.pop(call_id) for call_id in ready_ids]
        mode = "parallel" if len(ready_calls) > 1 else "sequential"
        batches.append(ToolBatch(mode=mode, calls=ready_calls))
        done.update(ready_ids)

    return batches


def _message_content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    try:
        return json.dumps(content, default=str)
    except Exception:
        return str(content)


def _fetch_url_bytes(url: str) -> bytes | None:
    try:
        request = Request(url, headers={"User-Agent": "MTP-SDK/0.1"})
        with urlopen(request, timeout=20) as response:  # noqa: S310
            return response.read()
    except Exception:
        return None


def _guess_mime_from_path(path_or_name: str, default: str) -> str:
    guessed = mimetypes.guess_type(path_or_name)[0]
    return guessed or default


def _to_data_url(payload: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(payload).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _image_to_openai_part(image: Image) -> dict[str, Any] | None:
    if image.url:
        return {"type": "image_url", "image_url": {"url": image.url}}
    content = image.get_content_bytes()
    if content is None:
        return None
    mime_type = image.mime_type
    if mime_type is None:
        if image.format:
            mime_type = f"image/{image.format}"
        elif image.filepath:
            mime_type = _guess_mime_from_path(str(image.filepath), "image/jpeg")
        else:
            mime_type = "image/jpeg"
    image_url = _to_data_url(content, mime_type)
    part: dict[str, Any] = {"type": "image_url", "image_url": {"url": image_url}}
    if image.detail:
        part["image_url"]["detail"] = image.detail
    return part


def _audio_to_openai_part(audio: Audio) -> dict[str, Any] | None:
    content = audio.get_content_bytes()
    if content is None and audio.url:
        content = _fetch_url_bytes(audio.url)
    if content is None:
        return None
    audio_format = audio.format
    if audio_format is None:
        if audio.filepath:
            audio_format = Path(str(audio.filepath)).suffix.lstrip(".") or "wav"
        elif audio.mime_type and "/" in audio.mime_type:
            audio_format = audio.mime_type.split("/", 1)[1]
        else:
            audio_format = "wav"
    encoded = base64.b64encode(content).decode("utf-8")
    return {"type": "input_audio", "input_audio": {"data": encoded, "format": audio_format}}


def _file_to_openai_part(file: File) -> dict[str, Any] | None:
    if file.content is None and file.filepath is None and file.url is None:
        return None
    raw = file.get_content_bytes()
    if raw is None and file.url:
        raw = _fetch_url_bytes(file.url)
    if raw is None:
        return None
    filename = file.filename
    if filename is None and file.filepath is not None:
        filename = Path(str(file.filepath)).name
    if filename is None and file.url:
        filename = Path(file.url).name or "file"
    if filename is None:
        filename = "file"
    mime_type = file.mime_type or _guess_mime_from_path(filename, "application/octet-stream")
    data_url = _to_data_url(raw, mime_type)
    return {"type": "file", "file": {"filename": filename, "file_data": data_url}}


def format_openai_like_message(
    msg: dict[str, Any],
    *,
    allow_images: bool = True,
    allow_audio: bool = True,
    allow_video: bool = False,
    allow_files: bool = True,
) -> dict[str, Any] | None:
    role = msg.get("role")
    if role not in {"system", "user", "assistant", "tool"}:
        return None

    if role == "tool":
        return {
            "role": "tool",
            "tool_call_id": msg.get("tool_call_id"),
            "content": _message_content_text(msg.get("content", "")),
        }

    new_msg: dict[str, Any] = {"role": role, "content": msg.get("content") or ""}
    if "tool_calls" in msg:
        new_msg["tool_calls"] = msg["tool_calls"]

    media_parts: list[dict[str, Any]] = []
    images = msg.get("images") if isinstance(msg.get("images"), list) else None
    audios = msg.get("audios") if isinstance(msg.get("audios"), list) else None
    if audios is None and isinstance(msg.get("audio"), list):
        audios = msg.get("audio")
    videos = msg.get("videos") if isinstance(msg.get("videos"), list) else None
    files = msg.get("files") if isinstance(msg.get("files"), list) else None

    if allow_images and images:
        for image in images:
            if isinstance(image, Image):
                image_part = _image_to_openai_part(image)
                if image_part is not None:
                    media_parts.append(image_part)

    if allow_audio and audios:
        for audio in audios:
            if isinstance(audio, Audio):
                audio_part = _audio_to_openai_part(audio)
                if audio_part is not None:
                    media_parts.append(audio_part)

    if allow_video and videos:
        for video in videos:
            if isinstance(video, Video) and video.url:
                media_parts.append({"type": "text", "text": f"[video] {video.url}"})

    if allow_files and files:
        for file in files:
            if isinstance(file, File):
                file_part = _file_to_openai_part(file)
                if file_part is not None:
                    media_parts.append(file_part)

    if media_parts:
        text = _message_content_text(msg.get("content", ""))
        parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
        parts.extend(media_parts)
        new_msg["content"] = parts
    return new_msg
