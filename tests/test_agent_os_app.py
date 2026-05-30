from __future__ import annotations

import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from mtp.agent_os import app
from mtp.agent_os import launcher
from mtp.cli.providers import list_providers


def test_agent_os_exposes_registered_providers() -> None:
    choices = set(app._provider_choices())
    expected = {provider.name for provider in list_providers()}

    assert expected <= choices
    assert app._default_model("mock") == "simple-planner"
    assert app._default_model("anthropic") == app.DEFAULT_PROVIDER_MODELS["claude"]


def test_agent_os_event_state_drops_pre_tool_planning_text() -> None:
    state = app.RunViewState()

    app._consume_event(state, {"type": "text_chunk", "chunk": "I will inspect first. ", "source": "direct"})
    assert "".join(state.final_text_chunks) == "I will inspect first. "

    app._consume_event(state, {"type": "plan_received"})
    assert state.saw_tool_round is True
    assert state.final_text_chunks == []

    app._consume_event(state, {"type": "text_chunk", "chunk": "Final answer.", "source": "finalize_stream"})
    app._consume_event(state, {"type": "run_completed", "final_text": "Final answer."})

    assert "".join(state.final_text_chunks) == "Final answer."


def test_agent_os_event_state_merges_duplicate_direct_stream() -> None:
    state = app.RunViewState()

    app._consume_event(state, {"type": "text_chunk", "chunk": "Hello wor", "source": "direct"})
    app._consume_event(state, {"type": "text_chunk", "chunk": "world", "source": "direct"})
    app._consume_event(state, {"type": "run_completed", "final_text": "Hello world"})

    assert "".join(state.final_text_chunks) == "Hello world"


def test_launcher_passes_launch_cwd_to_streamlit(monkeypatch, tmp_path) -> None:
    calls = []

    def fake_run(cmd, check, cwd, env):
        calls.append((cmd, check, cwd, env))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(launcher.subprocess, "run", fake_run)

    assert launcher.launch() == 0
    assert calls
    cmd, check, cwd, env = calls[0]
    assert check is False
    assert cmd[:3] == [sys.executable, "-m", "streamlit"]
    assert cwd == str(tmp_path.resolve())
    assert env["MTP_AGENT_OS_CWD"] == str(tmp_path.resolve())
