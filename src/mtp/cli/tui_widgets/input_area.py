"""Input Area Widget — Auto-expanding text input with prompt prefix.

Provides a styled TextArea for user input with dynamic height,
submit-on-Enter, and visual prompt indicators.
"""
from __future__ import annotations

from pathlib import Path

from textual.widgets import TextArea, Static
from textual.containers import Vertical
from textual.message import Message
from textual.app import ComposeResult
from textual import events
from rich.text import Text


class PromptLabel(Static):
    """Displays the prompt prefix: cwd mtp:backend:session ❯"""

    DEFAULT_CSS = """
    PromptLabel {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def update_label(self, cwd_name: str, backend: str, session_short: str) -> None:
        backend_short = "cdx" if backend == "codex" else backend[:3]
        label = Text()
        label.append(f"{cwd_name} ", style="dim #71717a")
        label.append("mtp", style="bold #c084fc")
        label.append(":", style="dim #71717a")
        label.append(backend_short, style="#0e7490")
        label.append(":", style="dim #71717a")
        label.append(session_short, style="#2dd4bf")
        label.append(" ❯ ", style="bold #ec4899")
        self.update(label)


class InputArea(TextArea):
    """Auto-expanding input area with Enter-to-submit behavior.

    - Enter submits (unless Shift+Enter for newline).
    - Tab is passed through (not used for indentation).
    - Ctrl+key combos bubble up to the App for global bindings.
    """

    # Let Ctrl key combos bubble to the App instead of being eaten
    BINDINGS = []

    DEFAULT_CSS = """
    InputArea {
        height: auto;
        min-height: 3;
        max-height: 10;
        border: tall $accent 40%;
        background: $surface;
        padding: 0 1;
    }
    InputArea:focus {
        border: tall $accent;
    }
    """

    class Submitted(Message):
        """Emitted when the user presses Enter to submit."""
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def __init__(self, **kwargs) -> None:
        super().__init__(
            language=None,
            theme="monokai",
            soft_wrap=True,
            show_line_numbers=False,
            tab_behavior="focus",  # Tab moves focus instead of inserting indent
            **kwargs,
        )

    async def _on_key(self, event: events.Key) -> None:
        # In Textual 8.x, modifiers are encoded in the key name:
        #   plain Enter  →  "enter"
        #   Shift+Enter  →  "shift+enter"
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            value = self.text.strip()
            if value:
                self.post_message(self.Submitted(value))
                self.text = ""
            return

        # Let Ctrl-combos bubble up to the App for global bindings
        if event.key.startswith("ctrl+"):
            return  # Don't consume — let it bubble

        # All other keys: let TextArea handle normally
        return


class InputPanel(Vertical):
    """Container for prompt label + input area with box-drawing border."""

    DEFAULT_CSS = """
    InputPanel {
        height: auto;
        max-height: 14;
        dock: bottom;
        padding: 0;
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield PromptLabel(id="prompt-label")
        yield InputArea(id="chat-input")
