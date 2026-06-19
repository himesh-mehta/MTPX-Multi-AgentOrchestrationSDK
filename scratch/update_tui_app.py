import re

def update_file():
    path = "src/mtp/cli/tui_app.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add OptionList and events to imports
    if "from textual.widgets.option_list import OptionList" not in content:
        content = content.replace("from textual.app import App, ComposeResult\n", "from textual.app import App, ComposeResult\nfrom textual.widgets.option_list import OptionList\n")
    if "from .tui_widgets.input_area import InputPanel, InputArea, PromptLabel" in content:
        content = content.replace(
            "from .tui_widgets.input_area import InputPanel, InputArea, PromptLabel\n",
            "from .tui_widgets.input_area import InputPanel, InputArea, PromptLabel, AttachmentBadge\n"
        )

    # 2. Add bindings
    if "Binding(\"escape\", \"hide_suggestions\"" not in content:
        content = content.replace(
            "Binding(\"ctrl+w\", \"cycle_sandbox\", \"Sandbox\", show=False, priority=True),\n    ]",
            "Binding(\"ctrl+w\", \"cycle_sandbox\", \"Sandbox\", show=False, priority=True),\n        Binding(\"escape\", \"hide_suggestions\", \"Hide Suggestions\", show=False),\n    ]"
        )

    # 3. Add history state initialization
    if "self._history_index" not in content:
        content = content.replace(
            "self._pending_raw_prompt: str = \"\"",
            "self._pending_raw_prompt: str = \"\"\n        self._history_index: int | None = None\n        self._history_draft: str = \"\"\n        self._pending_attachments: list[str] = []"
        )

    # 4. Modify on_input_area_submitted to handle badges
    handler_old = """    def on_input_area_submitted(self, event: InputArea.Submitted) -> None:
        raw = event.value.strip()
        if not raw:
            return"""
    
    handler_new = """    def on_input_area_submitted(self, event: InputArea.Submitted) -> None:
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
            return"""
    content = content.replace(handler_old, handler_new)

    # 5. Add new methods for history and autocomplete
    methods_insertion = """

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
            lines = input_area.text.split("\\n")
            input_area.cursor_location = (len(lines) - 1, len(lines[-1]))
            return
            
        input_area.text = turns[self._history_index].prompt
        if event.direction == -1:
            input_area.cursor_location = (0, 0)
        else:
            lines = input_area.text.split("\\n")
            input_area.cursor_location = (len(lines) - 1, len(lines[-1]))

    def on_input_area_tab_pressed(self, event: InputArea.TabPressed) -> None:
        input_area = self.query_one("#chat-input", InputArea)
        cursor_row, cursor_col = input_area.cursor_location
        lines = input_area.text.split("\\n")
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
        lines = input_area.text.split("\\n")
        current_line = lines[cursor_row][:cursor_col]
        words = current_line.split()
        if not words:
            return
            
        last_word = words[-1]
        
        if selected.startswith("@"):
            start_idx = current_line.rfind(last_word)
            new_line = current_line[:start_idx]
            lines[cursor_row] = new_line + lines[cursor_row][cursor_col:]
            input_area.text = "\\n".join(lines)
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
            input_area.text = "\\n".join(lines)
            input_area.cursor_location = (cursor_row, start_idx + len(selected) + 1)
"""
    if "def action_hide_suggestions" not in content:
        content = content.replace("    def _send_prompt(self, raw: str) -> None:", methods_insertion + "\n    def _send_prompt(self, raw: str) -> None:")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

update_file()
