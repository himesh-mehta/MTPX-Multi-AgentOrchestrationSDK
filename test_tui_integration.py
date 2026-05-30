#!/usr/bin/env python3
"""Integration test for TUI with new input box UI."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mtp.cli.tui_completers import (
    build_prompt_prefix_html_with_box,
    build_prompt_prefix_html,
)
from mtp.cli.tui_theme import (
    input_box_top,
    input_box_bottom,
    get_term_width,
)


class MockState:
    """Mock TUIState for testing."""
    def __init__(self):
        self.backend = "codex"
        self.session_id = "chat-b87744abcd"
        self.cwd = type('obj', (object,), {'name': 'MTPX'})()


def test_prompt_prefix_html():
    """Test the simplified prompt prefix HTML."""
    print("\n=== Test: Prompt Prefix HTML ===")
    state = MockState()
    prefix = build_prompt_prefix_html(state)
    print(f"Prompt prefix HTML: {prefix}")
    print("Expected: Simple arrow with styling")


def test_prompt_prefix_with_box():
    """Test the box-based prompt prefix."""
    print("\n=== Test: Prompt Prefix with Box ===")
    state = MockState()
    top, prompt_html, bottom = build_prompt_prefix_html_with_box(state)
    
    print("Top border:")
    print(top)
    print("\nPrompt HTML:")
    print(f"  {prompt_html}")
    print("\nBottom border:")
    print(bottom)


def test_backend_variations():
    """Test different backend configurations."""
    print("\n=== Test: Backend Variations ===")
    
    # Codex backend
    state = MockState()
    state.backend = "codex"
    top, _, bottom = build_prompt_prefix_html_with_box(state)
    print("\nCodex backend:")
    print(top)
    
    # MTP-OpenAI backend
    state.backend = "mtp-openai"
    top, _, bottom = build_prompt_prefix_html_with_box(state)
    print("\nMTP-OpenAI backend:")
    print(top)


def test_session_id_variations():
    """Test different session ID formats."""
    print("\n=== Test: Session ID Variations ===")
    
    state = MockState()
    
    # Short session ID
    state.session_id = "chat-abc123"
    top, _, _ = build_prompt_prefix_html_with_box(state)
    print("\nShort session ID:")
    print(top)
    
    # Long session ID
    state.session_id = "chat-verylongsessionid12345678"
    top, _, _ = build_prompt_prefix_html_with_box(state)
    print("\nLong session ID:")
    print(top)
    
    # Session ID with special format
    state.session_id = "session-2024-01-15-abc123def456"
    top, _, _ = build_prompt_prefix_html_with_box(state)
    print("\nSpecial format session ID:")
    print(top)


def test_visual_simulation():
    """Simulate the actual TUI input flow."""
    print("\n=== Test: Visual Simulation ===")
    print("\nSimulating user input flow:\n")
    
    state = MockState()
    top, prompt_html, bottom = build_prompt_prefix_html_with_box(state)
    
    # Simulate the input box appearing
    print(top)
    print(f"│ ❯ [User would type here: 'explain @src/mtp/agent.py']")
    print(bottom)
    
    print("\n[Agent response would appear here]\n")
    
    # Next prompt
    print(top)
    print(f"│ ❯ [User would type here: '/help']")
    print(bottom)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MTP TUI Integration Tests - Input Box UI")
    print("="*70)
    
    test_prompt_prefix_html()
    test_prompt_prefix_with_box()
    test_backend_variations()
    test_session_id_variations()
    test_visual_simulation()
    
    print("\n" + "="*70)
    print("All integration tests completed successfully!")
    print("="*70 + "\n")
