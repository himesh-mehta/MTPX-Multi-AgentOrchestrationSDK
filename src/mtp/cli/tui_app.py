"""MTP TUI App — Main Textual Application.

Async-first, modular Textual App replacing the monolithic tui.py loop.
All LLM calls run in Worker threads; UI never blocks.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.worker import Worker, WorkerState

from .tui_state import (
    TUIState, ChatResult, active_model_name,
    new_session_id, generate_session_title_from_prompt,
    resolve_model, resolve_reasoning,
    MODEL_PRESETS, REASONING_SHORTCUTS,
)
from .tui_widgets.chat_log import ChatLog, ChatMessage
from .tui_widgets.input_area import InputPanel, InputArea, PromptLabel, AttachmentBadge
from .tui_widgets.status_bar import StatusBar
from .tui_widgets.sidebar import Sidebar, SessionInfo, ToolEventLog
from .tui_widgets.spinner_widget import SpinnerWidget
from .tui_widgets.boot_screen import BootScreen, BootInfo
from .tui_commands import MTPCommandProvider, parse_slash_command
from .tui_workers import (
    save_tui_session, record_turn, collect_prompt_attachments,
    run_prompt_blocking, switch_backend,
)


class MTPApp(App):
    """MTP Terminal UI — Async Textual Application."""

    TITLE = "MTP TUI"
    SUB_TITLE = "Model Tool Protocol"
    CSS_PATH = "tui_app.tcss"
    COMMANDS = {MTPCommandProvider}

    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Commands", show=False, priority=True),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar", show=False, priority=True),
        Binding("ctrl+l", "clear_chat", "Clear", show=False, priority=True),
        Binding("ctrl+d", "quit", "Quit", show=False, priority=True),
        Binding("ctrl+w", "cycle_sandbox", "Sandbox", show=False, priority=True),
        Binding("escape", "hide_suggestions", "Hide Suggestions", show=False),
    ]

    def __init__(self, state: TUIState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = state
        self._pending_raw_prompt: str = ""
        self._history_index: int | None = None
        self._history_draft: str = ""
        self._pending_attachments: list[str] = []  # Track the raw prompt for recording

    @property
    def state(self) -> TUIState:
        return self._state

    # ── Compose ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="main-container"):
                yield BootScreen(id="boot-screen")
                yield ChatLog(id="chat-log")
                yield SpinnerWidget(id="spinner")
                yield InputPanel(id="input-panel")
            yield Sidebar(id="sidebar")
        yield StatusBar(id="status-bar")

    # ── Mount ────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self._refresh_status_bar()
        self._refresh_prompt_label()
        self._show_boot_info()
        self.set_timer(2.5, self._dismiss_boot)
        self.set_timer(0.5, self._focus_input)

    def _focus_input(self) -> None:
        try:
            self.query_one("#chat-input", InputArea).focus()
        except Exception:
            pass

    def _show_boot_info(self) -> None:
        try:
            from mtp import __version__
        except Exception:
            __version__ = "0.0.0"
        model = active_model_name(self._state)
        sid = self._state.session_id.split("-")[-1][:8]
        cwd = str(self._state.cwd.name or self._state.cwd)
        boot_info = self.query_one("#boot-info", BootInfo)
        boot_info.set_info(
            version=__version__, backend=self._state.backend,
            model=model, session_short=sid, cwd=cwd,
        )

    def _dismiss_boot(self) -> None:
        try:
            self.query_one("#boot-screen", BootScreen).display = False
        except Exception:
            pass
        # Write a compact welcome header into the ChatLog so it's not blank
        try:
            chat_log = self.query_one("#chat-log", ChatLog)
            from rich.text import Text
            welcome = Text()
            welcome.append("  ╭─ ", style="#3f3f46")
            welcome.append("MTP TUI", style="bold #c084fc")
            welcome.append(" ready", style="#71717a")
            welcome.append(" ─────────────────────────────────────╮\n", style="#3f3f46")
            welcome.append("  │  ", style="#3f3f46")
            welcome.append("Type a prompt", style="#f4f4f6")
            welcome.append(" to start chatting  ·  ", style="#71717a")
            welcome.append("@file", style="#38bdf8")
            welcome.append(" to attach  ·  ", style="#71717a")
            welcome.append("/help", style="#818cf8")
            welcome.append(" for commands\n", style="#71717a")
            welcome.append("  │  ", style="#3f3f46")
            model = active_model_name(self._state)
            welcome.append(f"{self._state.backend}", style="#34d399")
            welcome.append(" · ", style="#3f3f46")
            welcome.append(f"{model}", style="#fbbf24")
            welcome.append(" · ", style="#3f3f46")
            welcome.append(f"mode={self._state.harness_mode}", style="#818cf8")
            welcome.append(" · ", style="#3f3f46")
            welcome.append(f"sandbox={self._state.codex_sandbox_mode}", style="#2dd4bf")
            welcome.append("\n", style="")
            welcome.append("  ╰─────────────────────────────────────────────────────╯", style="#3f3f46")
            chat_log.write(welcome)
        except Exception:
            pass

    # ── UI refresh helpers ───────────────────────────────────────────────

    def _refresh_status_bar(self) -> None:
        try:
            self.query_one("#status-bar", StatusBar).update_status(
                backend=self._state.backend,
                model=active_model_name(self._state),
                session_id=self._state.session_id,
                mode=self._state.harness_mode,
                reasoning=self._state.reasoning_effort,
                turn_count=len(self._state.transcript),
                sandbox_mode=self._state.codex_sandbox_mode,
            )
        except Exception:
            pass

    def _refresh_prompt_label(self) -> None:
        try:
            label = self.query_one("#prompt-label", PromptLabel)
            cwd_name = self._state.cwd.name or str(self._state.cwd)
            sid_short = self._state.session_id.split("-")[-1][:6]
            label.update_label(cwd_name, self._state.backend, sid_short)
        except Exception:
            pass

    def _refresh_sidebar(self) -> None:
        try:
            self.query_one("#session-info", SessionInfo).update_info(
                session_id=self._state.session_id,
                label=self._state.session_label or "",
                backend=self._state.backend,
                model=active_model_name(self._state),
                turn_count=len(self._state.transcript),
                mode=self._state.harness_mode,
            )
            self.query_one("#tool-event-log", ToolEventLog).update_events(
                self._state.last_tool_events
            )
        except Exception:
            pass

    # ── Input handling ───────────────────────────────────────────────────

    def on_input_area_submitted(self, event: InputArea.Submitted) -> None:
        raw = event.value.strip()
        self._history_index = None
        self._history_draft = ""
        
        if self._pending_attachments:
            raw = " ".join([f"@{att}" for att in self._pending_attachments]) + " " + raw
            self._pending_attachments.clear()
            container = self.query_one("#attachment-container")
            for child in container.children:
                child.remove()
            container.remove_class("visible")
            
        raw = raw.strip()
        if not raw:
            return

        parsed = parse_slash_command(raw)
        if parsed is not None:
            cmd, arg = parsed
            self._dispatch_command(cmd, arg)
            return

        self._send_prompt(raw)



    # ── History & Autocomplete ──────────────────────────────────────────────

    def action_hide_suggestions(self) -> None:
        try:
            option_list = self.query_one("#suggestion-list", OptionList)
            if option_list.has_class("visible"):
                option_list.remove_class("visible")
                self.query_one("#chat-input", InputArea).focus()
        except Exception:
            pass

    def on_input_area_history_navigate(self, event: InputArea.HistoryNavigate) -> None:
        turns = self._state.transcript
        if not turns:
            return
        
        input_area = self.query_one("#chat-input", InputArea)
        
        if self._history_index is None:
            if event.direction == -1:
                self._history_index = len(turns) - 1
                self._history_draft = input_area.text
            else:
                return
        else:
            self._history_index += event.direction
            
        if self._history_index < 0:
            self._history_index = 0
        elif self._history_index >= len(turns):
            self._history_index = None
            input_area.text = self._history_draft
            # Textual TextArea cursor location requires row, col
            lines = input_area.text.split("\n")
            input_area.cursor_location = (len(lines) - 1, len(lines[-1]))
            return
            
        input_area.text = turns[self._history_index].prompt
        if event.direction == -1:
            input_area.cursor_location = (0, 0)
        else:
            lines = input_area.text.split("\n")
            input_area.cursor_location = (len(lines) - 1, len(lines[-1]))

    def on_input_area_tab_pressed(self, event: InputArea.TabPressed) -> None:
        input_area = self.query_one("#chat-input", InputArea)
        cursor_row, cursor_col = input_area.cursor_location
        lines = input_area.text.split("\n")
        current_line = lines[cursor_row][:cursor_col]
        words = current_line.split()
        if not words:
            return
            
        last_word = words[-1]
        if last_word.startswith("@"):
            partial = last_word[1:]
            self._show_file_suggestions(partial)
        elif last_word.startswith("/"):
            partial = last_word
            self._show_command_suggestions(partial)

    def _show_file_suggestions(self, partial: str) -> None:
        import os
        from pathlib import Path
        cwd = self._state.cwd
        matches = []
        try:
            for root, dirs, files in os.walk(cwd):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"__pycache__", "node_modules", "venv", ".venv", ".git"}]
                rel_root = Path(root).relative_to(cwd)
                if str(rel_root) == ".":
                    rel_root = Path("")
                for f in files:
                    if f.startswith("."): continue
                    rel_path = (rel_root / f).as_posix()
                    if partial.lower() in rel_path.lower():
                        matches.append(rel_path)
                if len(rel_root.parts) >= 2:
                    dirs.clear()
        except Exception:
            pass
            
        matches.sort()
        matches = matches[:20]
        if not matches:
            return
            
        self._populate_and_show_suggestions(matches, prefix="@")

    def _show_command_suggestions(self, partial: str) -> None:
        from .tui_completers import CommandCompleter
        completer = CommandCompleter()
        cmds = completer._COMMANDS
        matches = [cmd for cmd in cmds if cmd.startswith(partial.lower())]
        if not matches:
            return
        self._populate_and_show_suggestions(matches, prefix="")

    def _populate_and_show_suggestions(self, matches: list[str], prefix: str) -> None:
        option_list = self.query_one("#suggestion-list", OptionList)
        option_list.clear_options()
        for m in matches:
            option_list.add_option(f"{prefix}{m}")
        
        option_list.add_class("visible")
        option_list.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        option_list = event.option_list
        option_list.remove_class("visible")
        selected = str(event.option.prompt)
        
        input_area = self.query_one("#chat-input", InputArea)
        input_area.focus()
        
        cursor_row, cursor_col = input_area.cursor_location
        lines = input_area.text.split("\n")
        current_line = lines[cursor_row][:cursor_col]
        words = current_line.split()
        if not words:
            return
            
        last_word = words[-1]
        
        if selected.startswith("@"):
            start_idx = current_line.rfind(last_word)
            new_line = current_line[:start_idx]
            lines[cursor_row] = new_line + lines[cursor_row][cursor_col:]
            input_area.text = "\n".join(lines)
            input_area.cursor_location = (cursor_row, start_idx)
            
            filename = selected[1:]
            if filename not in self._pending_attachments:
                self._pending_attachments.append(filename)
                from .tui_widgets.input_area import AttachmentBadge
                container = self.query_one("#attachment-container")
                container.mount(AttachmentBadge(f"📎 {filename}"))
                container.add_class("visible")
        else:
            start_idx = current_line.rfind(last_word)
            new_line = current_line[:start_idx] + selected + " "
            lines[cursor_row] = new_line + lines[cursor_row][cursor_col:]
            input_area.text = "\n".join(lines)
            input_area.cursor_location = (cursor_row, start_idx + len(selected) + 1)

    def _send_prompt(self, raw: str) -> None:
        chat_log = self.query_one("#chat-log", ChatLog)
        spinner = self.query_one("#spinner", SpinnerWidget)

        expanded, attachments, att_warnings = collect_prompt_attachments(
            raw, self._state.cwd
        )

        chat_log.add_user_message(raw, attachments)

        model = active_model_name(self._state)
        chat_log.add_system_message(
            f"> {self._state.backend} · {model} · mode={self._state.harness_mode}"
        )

        spinner.start("Thinking")

        # Store raw prompt for turn recording
        self._pending_raw_prompt = raw

        self.run_worker(
            self._run_llm_worker(expanded, attachments, att_warnings),
            name="llm_call", thread=True, exclusive=True,
        )

    async def _run_llm_worker(
        self, expanded_prompt: str, attachments: list[str], att_warnings: list[str],
    ) -> ChatResult:
        """Worker coroutine — runs blocking LLM call in thread."""
        result = run_prompt_blocking(self._state, expanded_prompt)
        result.attachments = attachments
        result.warnings = [*att_warnings, *result.warnings]
        return result

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "llm_call":
            return

        spinner = self.query_one("#spinner", SpinnerWidget)

        if event.state == WorkerState.SUCCESS:
            spinner.stop()
            result: ChatResult = event.worker.result

            # Record the turn with the original raw prompt
            record_turn(self._state, self._pending_raw_prompt, result)

            # Auto-generate title from first prompt
            if len(self._state.transcript) == 1 and not self._state.session_label:
                self._state.session_label = generate_session_title_from_prompt(
                    self._state.transcript[0].prompt
                )
                save_tui_session(self._state)

            # Extract thinking from usage lines
            thinking = ""
            for uline in result.usage_lines:
                if uline.startswith("thinking="):
                    thinking = uline.replace("thinking=", "").strip()
                    break

            # Render response
            chat_log = self.query_one("#chat-log", ChatLog)
            chat_log.add_assistant_message(ChatMessage(
                role="assistant", text=result.text,
                model=active_model_name(self._state),
                backend=self._state.backend,
                tool_events=result.tool_events,
                warnings=result.warnings,
                usage_lines=result.usage_lines,
                thinking=thinking,
            ))

            self._state.last_tool_events = list(result.tool_events)
            self._state.last_warnings = list(result.warnings)
            self._refresh_status_bar()
            self._refresh_sidebar()

        elif event.state == WorkerState.ERROR:
            spinner.stop()
            self.query_one("#chat-log", ChatLog).add_system_message(
                f"⚡ Error: {event.worker.error}", style="bold #f43f5e"
            )

        elif event.state == WorkerState.CANCELLED:
            spinner.stop()
            self.query_one("#chat-log", ChatLog).add_system_message(
                "⚡ Request cancelled.", style="#fbbf24"
            )

    # ── Command dispatch (from slash commands and CommandPalette) ─────────

    def action_cmd_dispatch(self, cmd: str, arg: str) -> None:
        """Central action handler called by CommandPalette entries."""
        self._dispatch_command(cmd, arg)

    def _dispatch_command(self, cmd: str, arg: str) -> None:
        """Route a command name + argument to the appropriate handler."""
        chat_log = self.query_one("#chat-log", ChatLog)
        s = self._state

        if cmd == "help":
            chat_log.add_system_message(self._build_help_text())
        elif cmd == "exit":
            self.exit()
        elif cmd == "clear":
            chat_log.clear()
        elif cmd == "status":
            chat_log.add_system_message(self._build_status_text())
        elif cmd == "sessions":
            chat_log.add_system_message(self._build_sessions_text())
        elif cmd == "history":
            limit = int(arg) if arg and arg.isdigit() else None
            chat_log.add_system_message(self._build_history_text(limit))
        elif cmd == "models":
            chat_log.add_system_message(self._build_models_text())
        elif cmd == "tools":
            chat_log.add_system_message(self._build_tools_text())
        elif cmd == "new" or cmd == "reset":
            s.session_id = new_session_id()
            s.session_label = arg or None
            s.transcript = []
            s.last_usage_lines = []
            s.agent = None
            s.codex_session_id = None
            save_tui_session(s)
            chat_log.add_command_result(
                f"✓ New session {s.session_id}" + (f" ({arg})" if arg else "")
            )
            self._refresh_status_bar()
            self._refresh_prompt_label()
        elif cmd == "backend":
            if not arg:
                chat_log.add_system_message(self._build_providers_text())
            else:
                result = switch_backend(s, arg)
                chat_log.add_command_result(result)
                self._refresh_status_bar()
                self._refresh_prompt_label()
                self._refresh_sidebar()
        elif cmd == "model":
            if not arg:
                chat_log.add_system_message(self._build_models_text())
            else:
                self._handle_model_switch(arg)
        elif cmd == "reasoning":
            resolved = resolve_reasoning(arg) if arg else None
            if resolved:
                s.reasoning_effort = resolved
                save_tui_session(s)
                chat_log.add_command_result(f"✓ Reasoning set to {resolved}")
            else:
                chat_log.add_command_result("Usage: /reasoning <none|low|medium|high|xhigh>")
            self._refresh_status_bar()
        elif cmd == "mode":
            from .tui_harness_policy import normalize_harness_mode, HARNESS_MODES
            if not arg:
                chat_log.add_command_result(
                    f"Mode: {s.harness_mode}  Available: {', '.join(HARNESS_MODES)}"
                )
            else:
                try:
                    s.harness_mode = normalize_harness_mode(arg)
                    s.agent = None
                    save_tui_session(s)
                    chat_log.add_command_result(f"✓ Mode set to {s.harness_mode}")
                except ValueError:
                    chat_log.add_command_result(f"Available: {', '.join(HARNESS_MODES)}")
            self._refresh_status_bar()
        elif cmd == "rounds":
            if arg and arg.isdigit() and int(arg) >= 1:
                s.max_rounds = int(arg)
                save_tui_session(s)
                chat_log.add_command_result(f"✓ max_rounds set to {arg}")
            else:
                chat_log.add_command_result("Usage: /rounds <positive-int>")
        elif cmd == "cd":
            if not arg:
                chat_log.add_command_result("Usage: /cd <dir>")
            else:
                target = Path(arg).expanduser().resolve()
                if target.exists() and target.is_dir():
                    s.cwd = target
                    s.agent = None
                    save_tui_session(s)
                    chat_log.add_command_result(f"✓ cwd set to {target}")
                    self._refresh_prompt_label()
                else:
                    chat_log.add_command_result(f"✗ Not found: {target}")
        elif cmd == "autoresearch":
            s.autoresearch = arg.lower() == "on"
            s.agent = None
            save_tui_session(s)
            chat_log.add_command_result(f"✓ autoresearch={s.autoresearch}")
        elif cmd == "research":
            s.research_instructions = arg or None
            s.agent = None
            save_tui_session(s)
            chat_log.add_command_result("✓ research_instructions updated")
        elif cmd == "sandbox":
            self._handle_sandbox(arg)
        elif cmd == "apikey":
            self._handle_apikey(arg)
        elif cmd == "load":
            if not arg:
                chat_log.add_command_result("Usage: /load <session_id>")
            else:
                chat_log.add_system_message(f"Loading session: {arg}...")
                try:
                    from . import tui as old_tui
                    result = old_tui._load_session_hierarchical(s, arg)
                    cleaned = re.sub(r"\033\[[0-9;]*m", "", result or "")
                    chat_log.add_command_result(cleaned)
                except Exception as e:
                    chat_log.add_command_result(f"Load failed: {e}")
                self._refresh_status_bar()
                self._refresh_prompt_label()
        elif cmd == "open":
            if not arg:
                chat_log.add_command_result("Usage: /open <session_id>")
            else:
                chat_log.add_system_message(f"Session viewer not yet in Textual. Use legacy mode (MTP_TUI_LEGACY=1).")
        elif cmd == "codex-login":
            from . import tui_codex_backend as codex_backend
            codex_bin = s.codex_bin or codex_backend.detect_codex_bin()
            if codex_bin:
                rc = codex_backend.run_codex_login(codex_bin)
                chat_log.add_command_result("✓ Login completed" if rc == 0 else f"Login exited: {rc}")
            else:
                chat_log.add_command_result("Codex CLI not found")
        elif cmd == "compose":
            chat_log.add_system_message("Compose: use Shift+Enter for newlines, Enter to submit.")
        elif cmd == "cat":
            chat_log.add_command_result("Cat companion not available in Textual mode.")
        elif cmd == "unknown":
            chat_log.add_command_result("Unknown command. Press Ctrl+P for available commands.")
        else:
            chat_log.add_command_result(f"Unknown: /{cmd}")

    # ── Model / Sandbox / API key handlers ───────────────────────────────

    def _handle_model_switch(self, arg: str) -> None:
        chat_log = self.query_one("#chat-log", ChatLog)
        s = self._state
        resolved = resolve_model(arg)

        if s.backend == "codex":
            s.codex_model = None if resolved.lower() in {"default", "auto"} else resolved
            save_tui_session(s)
            chat_log.add_command_result(f"✓ Codex model: {s.codex_model or '(default)'}")
        else:
            from .tui_settings import (
                provider_settings_path, load_provider_settings,
                ensure_provider_entry, save_provider_settings,
            )
            settings_path = provider_settings_path(s.session_store.file_path)
            settings = load_provider_settings(settings_path)
            entry = ensure_provider_entry(settings, s.backend)
            entry["model"] = resolved
            save_provider_settings(settings_path, settings)
            s.agent = None
            save_tui_session(s)
            chat_log.add_command_result(f"✓ {s.backend} model: {resolved}")
        self._refresh_status_bar()

    def _handle_sandbox(self, arg: str) -> None:
        chat_log = self.query_one("#chat-log", ChatLog)
        s = self._state
        if not arg:
            modes = ["read-only", "workspace-write", "danger-full-access"]
            idx = modes.index(s.codex_sandbox_mode) if s.codex_sandbox_mode in modes else 1
            s.codex_sandbox_mode = modes[(idx + 1) % len(modes)]
        else:
            mode_map = {
                "readonly": "read-only", "read-only": "read-only",
                "write": "workspace-write", "workspace-write": "workspace-write",
                "full": "danger-full-access", "danger-full-access": "danger-full-access",
            }
            s.codex_sandbox_mode = mode_map.get(arg.lower(), arg.lower())
        save_tui_session(s)
        icons = {"read-only": "🔒", "workspace-write": "✓", "danger-full-access": "⚠"}
        icon = icons.get(s.codex_sandbox_mode, "?")
        chat_log.add_command_result(f"✓ Sandbox: {s.codex_sandbox_mode} {icon}")
        self._refresh_status_bar()

    def _handle_apikey(self, arg: str) -> None:
        chat_log = self.query_one("#chat-log", ChatLog)
        try:
            from . import tui as old_tui
            result = old_tui._handle_apikey_command(self._state, arg)
            if result:
                cleaned = re.sub(r"\033\[[0-9;]*m", "", result)
                chat_log.add_command_result(cleaned)
        except Exception as e:
            chat_log.add_command_result(f"Error: {e}")

    # ── Text builders ────────────────────────────────────────────────────

    def _build_help_text(self) -> str:
        return (
            "━━━ Command Reference ━━━\n\n"
            "Navigation\n"
            "  /help         Show this reference\n"
            "  /exit         Quit TUI\n"
            "  /clear        Clear chat log\n"
            "  /status       Show session state\n"
            "  /new [label]  Start fresh session\n"
            "  /load <id>    Load saved session\n"
            "  /sessions     List saved sessions\n"
            "  /history [n]  Show recent turns\n"
            "  /tools        Show last tool events\n\n"
            "Backend & Model\n"
            "  /backend <p>  Switch provider\n"
            "  /model <name> Switch model\n"
            "  /models       Show all models\n"
            "  /apikey       Manage API keys\n"
            "  /reasoning <level>  Set reasoning\n"
            "  /mode <mode>  Set harness mode\n"
            "  /rounds <n>   Set max rounds\n"
            "  /sandbox      Cycle sandbox mode\n\n"
            "Keys\n"
            "  Ctrl+P  Command palette\n"
            "  Ctrl+B  Toggle sidebar\n"
            "  Ctrl+L  Clear screen\n"
            "  Ctrl+D  Quit\n"
            "  Ctrl+W  Cycle sandbox\n\n"
            "Prompt: @path/to/file to attach context"
        )

    def _build_status_text(self) -> str:
        s = self._state
        return (
            f"━━━ Session Status ━━━\n"
            f"  session    {s.session_id}\n"
            f"  label      {s.session_label or '(none)'}\n"
            f"  backend    {s.backend}\n"
            f"  model      {active_model_name(s)}\n"
            f"  mode       {s.harness_mode}\n"
            f"  reasoning  {s.reasoning_effort}\n"
            f"  sandbox    {s.codex_sandbox_mode}\n"
            f"  rounds     {s.max_rounds}\n"
            f"  cwd        {s.cwd}\n"
            f"  turns      {len(s.transcript)}\n"
            f"  autoresearch {s.autoresearch}"
        )

    def _build_sessions_text(self) -> str:
        import json
        from mtp import SessionRecord
        sessions: list[SessionRecord] = []
        try:
            if self._state.session_store.file_path.exists():
                rows = json.loads(
                    self._state.session_store.file_path.read_text(encoding="utf-8")
                )
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict):
                            sessions.append(SessionRecord.from_dict(row))
            sessions.sort(key=lambda x: x.updated_at, reverse=True)
        except Exception:
            return "No saved sessions."
        if not sessions:
            return "No saved sessions."
        lines = ["━━━ Saved Sessions ━━━"]
        for rec in sessions[:15]:
            tui = rec.metadata.get("tui", {}) if isinstance(rec.metadata, dict) else {}
            tui = tui if isinstance(tui, dict) else {}
            label = tui.get("session_label", "(unnamed)")
            turns = tui.get("turn_count", 0)
            sid = rec.session_id.split("-")[-1][:8]
            active = " ● ACTIVE" if rec.session_id == self._state.session_id else ""
            lines.append(f"  {sid}  {label}  ({turns} turns){active}")
        return "\n".join(lines)

    def _build_history_text(self, limit: int | None = None) -> str:
        turns = self._state.transcript[-limit:] if limit else self._state.transcript
        if not turns:
            return "No turns yet."
        lines = ["━━━ Chat History ━━━"]
        for i, t in enumerate(turns, 1):
            p = t.prompt.replace("\n", " ")[:80]
            r = t.response.replace("\n", " ")[:80]
            lines.append(f"  #{i} {t.created_at} · {t.backend}")
            lines.append(f"    ❯ {p}")
            lines.append(f"    ◂ {r}")
        return "\n".join(lines)

    def _build_models_text(self) -> str:
        lines = ["━━━ Available Models ━━━\n", "Codex Models:"]
        for i, (m, d) in enumerate(MODEL_PRESETS, 1):
            active = "●" if m == self._state.codex_model else "○"
            lines.append(f"  {active} [{i}] {m}  {d}")
        lines.append(f"\nReasoning: {self._state.reasoning_effort}")
        lines.append(
            "Levels: " + " ".join(f"[{k}]={v}" for k, v in REASONING_SHORTCUTS.items())
        )
        lines.append(f"\nUsage: /model <name>  or  /model add <provider> <name>")
        return "\n".join(lines)

    def _build_tools_text(self) -> str:
        if not self._state.last_tool_events:
            return "No tool events from last turn."
        lines = [f"━━━ Tool Events ({len(self._state.last_tool_events)}) ━━━"]
        for e in self._state.last_tool_events:
            lines.append(f"  ├─ {e}")
        if self._state.last_warnings:
            lines.append(f"\nWarnings ({len(self._state.last_warnings)}):")
            for w in self._state.last_warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)

    def _build_providers_text(self) -> str:
        from .tui_provider_factory import SUPPORTED_TUI_PROVIDERS
        lines = ["━━━ Available Providers ━━━"]
        active = self._state.backend
        lines.append(f"  {'●' if active == 'codex' else '○'} codex")
        for p in sorted(SUPPORTED_TUI_PROVIDERS):
            marker = "●" if p == active else "○"
            lines.append(f"  {marker} {p}")
        lines.append(f"\nUsage: /backend <provider>")
        return "\n".join(lines)

    # ── Action bindings ──────────────────────────────────────────────────

    def action_toggle_sidebar(self) -> None:
        self.query_one("#sidebar", Sidebar).toggle()
        self._refresh_sidebar()

    def action_clear_chat(self) -> None:
        self.query_one("#chat-log", ChatLog).clear()

    def action_cycle_sandbox(self) -> None:
        self._handle_sandbox("")
