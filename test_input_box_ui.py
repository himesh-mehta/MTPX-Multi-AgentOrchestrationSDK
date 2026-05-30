#!/usr/bin/env python3
"""Visual test for the new input box UI."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mtp.cli.tui_theme import (
    input_box_top,
    input_box_bottom,
    box_separator,
    C_BORDER,
    C_PROMPT_ARROW,
    C_DIM,
    C_TEXT,
    SYM_V,
    SYM_PROMPT_ARROW,
    RESET,
    get_term_width,
)


def test_basic_box():
    """Test basic input box without label."""
    print("\n=== Test 1: Basic Input Box ===")
    w = get_term_width()
    print(input_box_top(width=w))
    print(f"{C_BORDER}{SYM_V}{RESET} {C_PROMPT_ARROW}{SYM_PROMPT_ARROW}{RESET} {C_TEXT}This is where user input would appear{RESET}")
    print(input_box_bottom(width=w))


def test_labeled_box():
    """Test input box with session label."""
    print("\n=== Test 2: Input Box with Label ===")
    w = get_term_width()
    print(input_box_top(width=w, label="mtp:cdx:b87744"))
    print(f"{C_BORDER}{SYM_V}{RESET} {C_PROMPT_ARROW}{SYM_PROMPT_ARROW}{RESET} {C_TEXT}User input here{RESET}")
    print(input_box_bottom(width=w))


def test_placeholder():
    """Test input box with placeholder text."""
    print("\n=== Test 3: Input Box with Placeholder ===")
    w = get_term_width()
    print(input_box_top(width=w, label="mtp:oai:a1b2c3"))
    print(f"{C_BORDER}{SYM_V}{RESET} {C_PROMPT_ARROW}{SYM_PROMPT_ARROW}{RESET} {C_DIM}Type your message or @file to attach{RESET}")
    print(input_box_bottom(width=w))


def test_compose_mode():
    """Test compose mode box."""
    print("\n=== Test 4: Compose Mode Box ===")
    w = get_term_width()
    print(input_box_top(width=w, label="compose mode"))
    print(f"{C_BORDER}{SYM_V}{RESET} {C_DIM}Type multiple lines. Use /send to submit or /cancel to abort.{RESET}")
    print(box_separator(width=w))
    print(f"{C_BORDER}{SYM_V}{RESET} {C_DIM}...{RESET} {C_TEXT}Line 1 of user input{RESET}")
    print(f"{C_BORDER}{SYM_V}{RESET} {C_DIM}...{RESET} {C_TEXT}Line 2 of user input{RESET}")
    print(f"{C_BORDER}{SYM_V}{RESET} {C_DIM}...{RESET} {C_TEXT}Line 3 of user input{RESET}")
    print(input_box_bottom(width=w))


def test_various_widths():
    """Test input box at various widths."""
    print("\n=== Test 5: Various Terminal Widths ===")
    for width in [60, 80, 100, 120]:
        print(f"\nWidth: {width}")
        print(input_box_top(width=width, label="mtp:cdx:test"))
        print(f"{C_BORDER}{SYM_V}{RESET} {C_PROMPT_ARROW}{SYM_PROMPT_ARROW}{RESET} {C_TEXT}Input at width {width}{RESET}")
        print(input_box_bottom(width=width))


def test_long_label():
    """Test input box with a long label."""
    print("\n=== Test 6: Long Label Handling ===")
    w = get_term_width()
    long_label = "mtp:codex:session-with-very-long-id-12345678"
    print(input_box_top(width=w, label=long_label))
    print(f"{C_BORDER}{SYM_V}{RESET} {C_PROMPT_ARROW}{SYM_PROMPT_ARROW}{RESET} {C_TEXT}Input with long label{RESET}")
    print(input_box_bottom(width=w))


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MTP TUI Input Box UI - Visual Tests")
    print("="*60)
    
    test_basic_box()
    test_labeled_box()
    test_placeholder()
    test_compose_mode()
    test_various_widths()
    test_long_label()
    
    print("\n" + "="*60)
    print("All visual tests completed!")
    print("="*60 + "\n")
