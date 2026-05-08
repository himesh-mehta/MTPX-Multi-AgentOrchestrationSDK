"""Status Bar Widget — Bottom bar with model, session, and mode info.

Provides real-time contextual information about the active session.
"""
from __future__ import annotations

from textual.widgets import Static
from rich.text import Text


class StatusBar(Static):
    """Bottom status bar showing model, backend, session, and key hints."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: #18181b;
        color: #71717a;
        padding: 0 2;
    }
    """

    def update_status(
        self,
        *,
        backend: str = "codex",
        model: str = "",
        session_id: str = "",
        mode: str = "code",
        reasoning: str = "medium",
        turn_count: int = 0,
        sandbox_mode: str = "workspace-write",
    ) -> None:
        bar = Text()

        # Backend + model
        bar.append(" ● ", style="bold #34d399" if backend != "codex" else "bold #c084fc")
        bar.append(backend, style="bold #c084fc")
        if model:
            bar.append(f"  {model}", style="#fbbf24")

        bar.append("  │  ", style="dim #3f3f46")

        # Mode
        bar.append(f"mode:{mode}", style="#818cf8")
        bar.append("  │  ", style="dim #3f3f46")

        # Session
        sid_short = session_id.split("-")[-1][:6] if session_id else "—"
        bar.append(f"session:{sid_short}", style="#2dd4bf")
        bar.append(f"  turns:{turn_count}", style="dim #71717a")

        bar.append("  │  ", style="dim #3f3f46")

        # Reasoning (codex only)
        if backend == "codex":
            bar.append(f"reasoning:{reasoning}", style="#d8b4fe")
            bar.append("  │  ", style="dim #3f3f46")

        # Sandbox mode
        sandbox_colors = {
            "read-only": ("#fbbf24", "🔒"),
            "workspace-write": ("#34d399", "✓"),
            "danger-full-access": ("#f43f5e", "⚠"),
        }
        color, icon = sandbox_colors.get(sandbox_mode, ("#71717a", "?"))
        bar.append(f"{icon} {sandbox_mode}", style=color)

        # Key hints (right-aligned conceptually, but left here for simplicity)
        bar.append("  │  ", style="dim #3f3f46")
        bar.append("Ctrl+P", style="#818cf8")
        bar.append(" commands  ", style="dim #71717a")
        bar.append("Ctrl+B", style="#818cf8")
        bar.append(" sidebar", style="dim #71717a")

        self.update(bar)
