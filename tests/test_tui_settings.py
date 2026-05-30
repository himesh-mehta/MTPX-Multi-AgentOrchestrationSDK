from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from mtp.cli.tui_settings import (
    ensure_provider_entry,
    load_provider_settings,
    preferred_model_for_provider,
    provider_settings_path,
    save_provider_settings,
)


def test_provider_settings_roundtrip(tmp_path: pathlib.Path) -> None:
    db_dir = tmp_path / "session_db"
    path = provider_settings_path(db_dir)
    payload = load_provider_settings(path)
    entry = ensure_provider_entry(payload, "groq")
    entry["api_key"] = "gsk_test"
    entry["model"] = "llama-3.3-70b-versatile"
    entry["models"] = ["llama-3.3-70b-versatile"]
    save_provider_settings(path, payload)

    loaded = load_provider_settings(path)
    loaded_entry = ensure_provider_entry(loaded, "groq")
    assert loaded_entry["api_key"] == "gsk_test"
    assert loaded_entry["model"] == "llama-3.3-70b-versatile"
    assert loaded_entry["models"] == ["llama-3.3-70b-versatile"]


def test_preferred_model_falls_back_to_default(tmp_path: pathlib.Path) -> None:
    path = provider_settings_path(tmp_path / "db")
    payload = load_provider_settings(path)
    assert preferred_model_for_provider(payload, "gemini") == "gemini-2.0-flash-exp"


def test_provider_settings_path_treats_nonexistent_json_path_as_file(tmp_path: pathlib.Path) -> None:
    session_file = tmp_path / "sessions.json"

    path = provider_settings_path(session_file)

    assert path == tmp_path / "tui_provider_settings.json"
