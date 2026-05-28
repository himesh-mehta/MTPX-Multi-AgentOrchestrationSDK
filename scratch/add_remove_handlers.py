import re

path = "src/mtp/cli/tui_app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

methods = """
    def on_input_area_remove_last_attachment(self, event) -> None:
        if hasattr(self, "_pending_attachments") and self._pending_attachments:
            self._pending_attachments.pop()
            container = self.query_one("#attachment-container")
            if container.children:
                container.children[-1].remove()
            if not self._pending_attachments:
                container.remove_class("visible")

    def on_attachment_badge_remove_attachment(self, event) -> None:
        if hasattr(self, "_pending_attachments") and event.filename in self._pending_attachments:
            self._pending_attachments.remove(event.filename)
            if not self._pending_attachments:
                self.query_one("#attachment-container").remove_class("visible")

"""

if "def on_input_area_remove_last_attachment" not in content:
    content = content.replace("    def action_hide_suggestions(self) -> None:", methods + "    def action_hide_suggestions(self) -> None:")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
