from __future__ import annotations

import inspect
import types
from dataclasses import dataclass
from typing import Any, Callable, Literal, Union, get_args, get_origin, get_type_hints

from .protocol import ToolRiskLevel, ToolSpec
from .runtime import RegisteredTool, ToolkitLoader


@dataclass(slots=True)
class ToolMeta:
    name: str | None = None
    description: str | None = None
    input_schema: dict[str, Any] | None = None
    risk_level: ToolRiskLevel = ToolRiskLevel.READ_ONLY
    cost_hint: str = "unknown"
    side_effects: str = "none"
    cache_ttl_seconds: int = 0
    tags: list[str] | None = None


def mtp_tool(
    *,
    name: str | None = None,
    description: str | None = None,
    input_schema: dict[str, Any] | None = None,
    risk_level: ToolRiskLevel = ToolRiskLevel.READ_ONLY,
    cost_hint: str = "unknown",
    side_effects: str = "none",
    cache_ttl_seconds: int = 0,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for marking a Python function as an MTP tool with metadata.
    """

    def _decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            fn,
            "__mtp_tool_meta__",
            ToolMeta(
                name=name,
                description=description,
                input_schema=input_schema,
                risk_level=risk_level,
                cost_hint=cost_hint,
                side_effects=side_effects,
                cache_ttl_seconds=cache_ttl_seconds,
                tags=tags,
            ),
        )
        return fn

    return _decorator


def _annotation_to_json_schema(annotation: Any) -> dict[str, Any]:
    if annotation is inspect._empty:
        return {"type": "string"}
    if annotation is Any:
        return {}
    if annotation is None or annotation is type(None):
        return {"type": "null"}

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Literal:
        return {"enum": list(args)}
    if origin in {Union, types.UnionType}:
        schemas = [_annotation_to_json_schema(arg) for arg in args]
        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for schema in schemas:
            key = repr(sorted(schema.items()))
            if key not in seen:
                seen.add(key)
                deduped.append(schema)
        if len(deduped) == 1:
            return deduped[0]
        return {"anyOf": deduped}
    if annotation in {str}:
        return {"type": "string"}
    if annotation in {int}:
        return {"type": "integer"}
    if annotation in {float}:
        return {"type": "number"}
    if annotation in {bool}:
        return {"type": "boolean"}
    if annotation in {dict}:
        return {"type": "object"}
    if annotation in {list, tuple, set}:
        return {"type": "array"}
    if origin is list:
        item_schema = _annotation_to_json_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": item_schema}
    if origin is dict:
        return {"type": "object"}
    if origin is tuple:
        return {"type": "array"}
    if origin is set:
        item_schema = _annotation_to_json_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": item_schema, "uniqueItems": True}

    return {"type": "string"}


def _infer_input_schema(fn: Callable[..., Any]) -> dict[str, Any]:
    signature = inspect.signature(fn)
    try:
        type_hints = get_type_hints(fn)
    except Exception:
        type_hints = {}
    properties: dict[str, Any] = {}
    required: list[str] = []

    for name, param in signature.parameters.items():
        if name in {"self", "cls"}:
            continue
        if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        annotation = type_hints.get(name, param.annotation)
        properties[name] = _annotation_to_json_schema(annotation)
        if param.default is inspect._empty:
            required.append(name)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return schema


def tool_spec_from_callable(fn: Callable[..., Any], *, namespace: str | None = None) -> ToolSpec:
    meta: ToolMeta = getattr(fn, "__mtp_tool_meta__", ToolMeta())
    base_name = meta.name or fn.__name__
    tool_name = f"{namespace}.{base_name}" if namespace else base_name
    description = meta.description or (inspect.getdoc(fn) or f"Tool function {base_name}.")
    schema = meta.input_schema or _infer_input_schema(fn)
    return ToolSpec(
        name=tool_name,
        description=description,
        input_schema=schema,
        tags=meta.tags or [],
        risk_level=meta.risk_level,
        cost_hint=meta.cost_hint,
        side_effects=meta.side_effects,
        cache_ttl_seconds=meta.cache_ttl_seconds,
    )


class FunctionToolkit(ToolkitLoader):
    """
    Build a ToolkitLoader from plain Python functions.

    Example:
        toolkit = FunctionToolkit("mathx", [add, multiply])
    """

    def __init__(self, name: str, functions: list[Callable[..., Any]]) -> None:
        self.name = name
        self.functions = functions

    def list_tool_specs(self) -> list[ToolSpec]:
        return [tool_spec_from_callable(fn, namespace=self.name) for fn in self.functions]

    def load_tools(self) -> list[RegisteredTool]:
        specs = {spec.name: spec for spec in self.list_tool_specs()}
        registered: list[RegisteredTool] = []
        for fn in self.functions:
            base_name = getattr(getattr(fn, "__mtp_tool_meta__", ToolMeta()), "name") or fn.__name__
            tool_name = f"{self.name}.{base_name}"
            registered.append(RegisteredTool(spec=specs[tool_name], handler=fn))
        return registered


def toolkit_from_functions(name: str, *functions: Callable[..., Any]) -> FunctionToolkit:
    return FunctionToolkit(name=name, functions=list(functions))
