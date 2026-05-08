"""Spinner Widget — Animated loading indicator.

Provides a smooth cyberpunk-themed spinner for background task indication
using Textual's reactive timer system.
"""
from __future__ import annotations

import time

from textual.widgets import Static
from rich.text import Text


# ── Spinner frame presets ────────────────────────────────────────────────────

SPINNER_FRAMES = {
    "dots": "⠋⠙⠚⠔⠤⠢⠖⠲⠴⠦⠧⠇⠏",
    "bar":  "▰▱▱▱▱▱▱|▰▰▱▱▱▱▱|▰▰▰▱▱▱▱|▰▰▰▰▱▱▱|▰▰▰▰▰▱▱|▰▰▰▰▰▰▱|▰▰▰▰▰▰▰",
    "braille": "⢄⢂⢁⡁⡈⡐⡠",
}

# Cyberpunk gradient for spinner frame coloring
SPIN_GRADIENT = [
    (236, 72, 153),   # Hot Pink
    (217, 70, 239),   # Fuchsia
    (192, 132, 252),  # Purple
    (147, 51, 234),   # Violet
    (129, 140, 248),  # Indigo
    (59, 130, 246),   # Blue
    (56, 189, 248),   # Sky
    (6, 182, 212),    # Cyan
    (45, 212, 191),   # Teal
]


class SpinnerWidget(Static):
    """Animated spinner with elapsed time display."""

    DEFAULT_CSS = """
    SpinnerWidget {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        display: none;
    }
    SpinnerWidget.active {
        display: block;
    }
    """

    def __init__(self, label: str = "Thinking", preset: str = "dots", **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._preset = preset
        frames_str = SPINNER_FRAMES.get(preset, SPINNER_FRAMES["dots"])
        self._frames = list(frames_str) if "|" not in frames_str else frames_str.split("|")
        self._idx = 0
        self._start_time = 0.0
        self._timer = None

        # Build oscillating color sequence
        self._colors = SPIN_GRADIENT + SPIN_GRADIENT[-2:0:-1]

    def start(self, label: str | None = None) -> None:
        """Start the spinner animation."""
        if label:
            self._label = label
        self._idx = 0
        self._start_time = time.monotonic()
        self.add_class("active")
        if self._timer is None:
            self._timer = self.set_interval(0.08, self._tick)
        else:
            self._timer.resume()
        self._tick()

    def stop(self) -> None:
        """Stop the spinner and hide it."""
        self.remove_class("active")
        if self._timer is not None:
            self._timer.pause()

    def _tick(self) -> None:
        frame = self._frames[self._idx % len(self._frames)]
        r, g, b = self._colors[self._idx % len(self._colors)]
        elapsed = time.monotonic() - self._start_time

        text = Text()
        text.append(f"  {frame} ", style=f"bold rgb({r},{g},{b})")
        text.append(f"{self._label}...", style="#0e7490")
        text.append(f" {elapsed:.1f}s", style="dim #71717a")
        self.update(text)
        self._idx += 1

    def update_label(self, label: str) -> None:
        """Update the spinner label while it's running."""
        self._label = label
