"""Chat Log Widget — Scrollable message log with rich markdown rendering.

Uses Textual's RichLog for efficient rendering of user/assistant messages,
tool events, code blocks, and usage metrics.
"""
from __future__ import annotations

import re
from typing import Any

from rich.markdown import Markdown
from rich.text import Text

from textual.widgets import RichLog


class ChatMessage:
    """A single chat message for display."""

    __slots__ = ("role", "text", "model", "backend", "tool_events",
                 "warnings", "usage_lines", "timestamp", "thinking", "duration_sec")

    def __init__(
        self,
        role: str,
        text: str,
        *,
        model: str = "",
        backend: str = "",
        tool_events: list[str] | None = None,
        warnings: list[str] | None = None,
        usage_lines: list[str] | None = None,
        timestamp: str = "",
        thinking: str = "",
        duration_sec: float | None = None,
    ):
        self.role = role
        self.text = text
        self.model = model
        self.backend = backend
        self.tool_events = tool_events or []
        self.warnings = warnings or []
        self.usage_lines = usage_lines or []
        self.timestamp = timestamp
        self.thinking = thinking
        self.duration_sec = duration_sec


class ChatLog(RichLog):
    """Premium chat log with gradient-styled messages and markdown rendering."""

    DEFAULT_CSS = """
    ChatLog {
        scrollbar-size: 1 1;
        scrollbar-color: $accent 40%;
        scrollbar-color-hover: $accent 60%;
        scrollbar-color-active: $accent 80%;
    }
    """

    def __init__(self, **kwargs: Any):
        super().__init__(
            highlight=True,
            markup=True,
            wrap=True,
            auto_scroll=True,
            min_width=40,
            **kwargs,
        )

    def add_user_message(self, text: str, attachments: list[str] | None = None) -> None:
        """Render a user prompt bubble."""
        header = Text()
        header.append("  ❯ ", style="bold #ec4899")
        header.append("You", style="bold #f4f4f6")

        self.write(header)

        # Attachment badges
        if attachments:
            att_text = Text("  ")
            for att in attachments[:5]:
                att_text.append(f" 📎 {att} ", style="#38bdf8 on #1e293b")
                att_text.append(" ")
            self.write(att_text)

        # Message body
        body = Text(f"  {text}", style="#f4f4f6")
        self.write(body)
        self.write(Text(""))  # spacer

    def add_assistant_message(self, msg: ChatMessage) -> None:
        """Render an assistant response with all metadata."""
        # ── Thinking/reasoning trace ─────────────────────────────
        if msg.thinking:
            self._render_thinking(msg.thinking)

        # ── Tool events ──────────────────────────────────────────
        if msg.tool_events:
            self._render_tool_events(msg.tool_events)

        # ── Warnings ─────────────────────────────────────────────
        if msg.warnings:
            for w in msg.warnings[:3]:
                warn_text = Text()
                warn_text.append("  ⚠ ", style="bold #fbbf24")
                warn_text.append(w, style="#fbbf24")
                self.write(warn_text)

        # ── Response header ──────────────────────────────────────
        header = Text()
        header.append("  ◂ ", style="bold #8b5cf6")
        header.append("Agent", style="bold #c084fc")
        if msg.model:
            header.append(f"  {msg.model}", style="dim #71717a")
        self.write(header)

        # ── Response body (markdown) ─────────────────────────────
        if msg.text:
            try:
                md = Markdown(msg.text, code_theme="monokai")
                self.write(md)
            except Exception:
                self.write(Text(f"  {msg.text}", style="#f4f4f6"))

        # ── Usage metrics ────────────────────────────────────────
        if msg.usage_lines:
            self.write(Text(""))
            self._render_usage(msg.usage_lines, msg.duration_sec)

        self.write(Text(""))  # spacer

    def add_system_message(self, text: str, style: str = "dim #71717a") -> None:
        """Render a system/info message."""
        msg = Text(f"  {text}", style=style)
        self.write(msg)

    def add_command_result(self, text: str) -> None:
        """Render the result of a slash command."""
        # Strip any leftover ANSI from the old system
        cleaned = re.sub(r"\033\[[0-9;]*m", "", text)
        result_text = Text(f"  {cleaned}", style="#a78bfa")
        self.write(result_text)
        self.write(Text(""))

    def _render_thinking(self, thinking: str) -> None:
        """Render cognitive trace in a subtle panel."""
        header = Text()
        header.append("  ╭─ ", style="#3f3f46")
        header.append("💭 Reasoning", style="bold #38bdf8")
        header.append(" ─", style="#3f3f46")
        self.write(header)

        lines = thinking.split(" | ") if " | " in thinking else thinking.splitlines()
        display_lines = lines[:8] if len(lines) > 8 else lines
        for line in display_lines:
            trace_text = Text()
            trace_text.append("  │  ", style="#3f3f46")
            trace_text.append(line.strip()[:200], style="dim #71717a")
            self.write(trace_text)
        if len(lines) > 8:
            collapsed = Text()
            collapsed.append(f"  │  ... {len(lines) - 8} more steps", style="dim #71717a italic")
            self.write(collapsed)

        footer = Text()
        footer.append("  ╰─────", style="#3f3f46")
        self.write(footer)

    def _render_tool_events(self, events: list[str]) -> None:
        """Render tool call tree."""
        meta = Text()
        meta.append(f"  • {len(events)} tools", style="#a78bfa")
        self.write(meta)

        for i, event in enumerate(events[:5]):
            connector = "└─" if i == len(events[:5]) - 1 and len(events) <= 5 else "├─"
            tool_text = Text()
            tool_text.append(f"  │  {connector} ", style="dim #3f3f46")
            # Clean emoji prefixes
            clean = event.replace("🔧 ", "")
            tool_text.append(clean[:120], style="#2dd4bf")
            self.write(tool_text)

        if len(events) > 5:
            more = Text()
            more.append(f"  │  └─ ... {len(events) - 5} more ", style="dim #3f3f46")
            more.append("(Ctrl+T to expand)", style="dim italic #818cf8")
            self.write(more)

    def _render_usage(self, lines: list[str], duration_sec: float | None = None) -> None:
        """Render compact usage metrics."""
        metrics: list[str] = []
        for line in lines:
            if line.startswith("thinking="):
                continue  # Already rendered above
            metrics.append(line)

        if not metrics:
            return

        # Context bar
        for m in metrics:
            match = re.match(r"context_window=([\d,]+)/([\d,]+)", m)
            if match:
                used = int(match.group(1).replace(",", ""))
                total = int(match.group(2).replace(",", ""))
                self._render_context_bar(used, total, duration_sec)
                break

        # Compact metrics
        compact = "  ".join(m for m in metrics[:3] if not m.startswith("context_window="))
        if compact:
            usage_text = Text(f"  {compact}", style="dim #71717a")
            self.write(usage_text)

    def _render_context_bar(self, used: int, total: int, duration_sec: float | None = None) -> None:
        """Render a gradient context window usage bar."""
        bar_w = 20
        pct = min(1.0, used / max(1, total))
        filled = int(pct * bar_w)
        empty = bar_w - filled

        if pct < 0.6:
            color = "#34d399"
        elif pct < 0.85:
            color = "#fbbf24"
        else:
            color = "#f43f5e"

        bar = Text("  ctx ")
        bar.append("▰" * filled, style=color)
        bar.append("▱" * empty, style="dim #3f3f46")
        bar.append(f" {pct*100:.0f}% ", style=color)
        bar.append(f"{used:,} / {total:,} tokens", style="dim #71717a")
        if duration_sec is not None:
            bar.append(f"  ⏱ {duration_sec:.1f}s", style="dim #38bdf8")
        self.write(bar)
