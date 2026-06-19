from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from ..tui_thinking import ThinkingCapability


class ThinkingDialog(ModalScreen[str | None]):
    """Modal picker for thinking / reasoning modes."""

    DEFAULT_CSS = """
    ThinkingDialog {
        align: center middle;
        background: rgba(12, 12, 14, 0.75);
    }
    #thinking-dialog {
        width: 44;
        height: auto;
        background: #18181b;
        border: tall #c084fc;
        padding: 1 1 0 1;
    }
    #thinking-dialog-title {
        padding: 0 1 1 1;
        color: #f4f4f6;
    }
    #thinking-dialog-help {
        padding: 0 1 1 1;
        color: #71717a;
    }
    #thinking-dialog-options {
        height: auto;
        max-height: 10;
        background: #18181b;
        border: none;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, capability: ThinkingCapability) -> None:
        super().__init__()
        self._capability = capability

    def compose(self) -> ComposeResult:
        title = f"Select {self._capability.label}"
        help_text = "Click or press Enter to apply."
        with Center():
            with Vertical(id="thinking-dialog"):
                yield Static(title, id="thinking-dialog-title")
                yield Static(help_text, id="thinking-dialog-help")
                yield OptionList(id="thinking-dialog-options")

    def on_mount(self) -> None:
        option_list = self.query_one("#thinking-dialog-options", OptionList)
        for option in self._capability.options:
            prefix = "● " if option.value == self._capability.current_value else "○ "
            option_list.add_option(Option(f"{prefix}{option.label}", id=option.value))
        current_index = next(
            (index for index, option in enumerate(self._capability.options) if option.value == self._capability.current_value),
            0,
        )
        option_list.highlighted = current_index
        option_list.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option_id)

    def action_cancel(self) -> None:
        self.dismiss(None)
