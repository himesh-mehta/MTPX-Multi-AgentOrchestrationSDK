from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from mtp import JsonSessionStore
from mtp.cli.tui_settings import (
    ensure_provider_entry,
    load_provider_settings,
    provider_settings_path,
    save_provider_settings,
)
from mtp.cli.tui_state import TUIState, new_session_id
from mtp.cli.tui_thinking import apply_thinking_value, get_thinking_capability


def _make_state(tmp_path: pathlib.Path, *, backend: str, model: str) -> TUIState:
    store = JsonSessionStore(db_path=tmp_path, session_table="sessions")
    if backend != "codex":
        settings_path = provider_settings_path(store.file_path)
        payload = load_provider_settings(settings_path)
        entry = ensure_provider_entry(payload, backend)
        entry["model"] = model
        save_provider_settings(settings_path, payload)

    return TUIState(
        backend=backend,
        codex_model="gpt-5.4",
        openai_model="gpt-4o",
        max_rounds=4,
        cwd=tmp_path,
        autoresearch=False,
        research_instructions=None,
        reasoning_effort="medium",
        harness_mode="code",
        codex_sandbox_mode="workspace-write",
        last_usage_lines=[],
        transcript=[],
        session_store=store,
        session_id=new_session_id(),
        session_label=None,
        user_id=None,
    )


def test_codex_reasoning_capability_exposes_levels(tmp_path: pathlib.Path) -> None:
    state = _make_state(tmp_path, backend="codex", model="gpt-5.4")

    capability = get_thinking_capability(state)

    assert capability is not None
    assert capability.label == "reasoning"
    assert [option.value for option in capability.options] == ["none", "low", "medium", "high", "xhigh"]
    assert capability.current_value == "medium"


def test_xiaomi_thinking_capability_is_toggle_for_supported_model(tmp_path: pathlib.Path) -> None:
    state = _make_state(tmp_path, backend="xiaomi", model="mimo-v2.5-pro")
    settings_path = provider_settings_path(state.session_store.file_path)
    payload = load_provider_settings(settings_path)
    entry = ensure_provider_entry(payload, "xiaomi")
    entry["thinking_mode"] = "disabled"
    save_provider_settings(settings_path, payload)

    capability = get_thinking_capability(state)

    assert capability is not None
    assert capability.label == "thinking"
    assert [option.label for option in capability.options] == ["on", "off"]
    assert capability.current_label == "off"


def test_xiaomi_tts_model_hides_thinking_control(tmp_path: pathlib.Path) -> None:
    state = _make_state(tmp_path, backend="xiaomi", model="mimo-v2.5-tts")

    assert get_thinking_capability(state) is None


def test_apply_xiaomi_thinking_value_persists_and_resets_agent(tmp_path: pathlib.Path) -> None:
    state = _make_state(tmp_path, backend="xiaomi", model="mimo-v2.5-pro")
    state.agent = object()

    message = apply_thinking_value(state, "off")
    settings_path = provider_settings_path(state.session_store.file_path)
    payload = load_provider_settings(settings_path)
    entry = ensure_provider_entry(payload, "xiaomi")

    assert message == "✓ Xiaomi thinking set to off"
    assert entry["thinking_mode"] == "disabled"
    assert entry["final_thinking_mode"] == "disabled"
    assert state.agent is None
