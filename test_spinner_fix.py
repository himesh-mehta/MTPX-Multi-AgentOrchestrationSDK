#!/usr/bin/env python3
"""
Test script to verify the TUI spinner fix.

This script simulates the spinner behavior to ensure:
1. Long labels are truncated to prevent line wrapping
2. Spinner updates in place using carriage return
3. No duplicate lines are printed
"""

import sys
import time
import threading


def get_term_width():
    """Get terminal width."""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def strip_ansi(text):
    """Strip ANSI escape codes from text."""
    import re
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


class TestSpinner:
    """Test spinner with label truncation."""
    
    def __init__(self, label: str):
        self._label = label
        self._running = False
        self._thread = None
        self._start_time = 0.0
        self._frames = ['⠋', '⠙', '⠚', '⠒', '⠂', '⠂', '⠒', '⠲', '⠴', '⠦', '⠖', '⠒']
        self._delay = 0.08
    
    def start(self):
        self._running = True
        self._start_time = time.monotonic()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        # Clear the spinner line
        sys.stdout.write(f"\r{' ' * get_term_width()}\r")
        sys.stdout.flush()
    
    def _spin(self):
        idx = 0
        while self._running:
            frame = self._frames[idx % len(self._frames)]
            elapsed = time.monotonic() - self._start_time
            elapsed_str = f" {elapsed:.1f}s"
            
            # Calculate available width for label to prevent line wrapping
            term_width = get_term_width()
            max_label_width = max(40, term_width - 25)
            
            # Truncate label if needed
            label_stripped = strip_ansi(self._label)
            if len(label_stripped) > max_label_width:
                label = label_stripped[:max_label_width - 3] + "..."
            else:
                label = self._label
            
            sys.stdout.write(f"\r  {frame} Active Tool ❯ {label}...{elapsed_str}")
            sys.stdout.flush()
            idx += 1
            time.sleep(self._delay)


def test_short_label():
    """Test spinner with short label (should not truncate)."""
    print("\n=== Test 1: Short Label ===")
    spinner = TestSpinner("project.inspect")
    spinner.start()
    time.sleep(3)
    spinner.stop()
    print("✓ project.inspect completed\n")


def test_long_label():
    """Test spinner with long label (should truncate)."""
    print("\n=== Test 2: Long Label (Should Truncate) ===")
    long_label = "project.inspect: User wants a batch call including project.inspect to get current workspace overview alongside the Linux version search"
    spinner = TestSpinner(long_label)
    spinner.start()
    time.sleep(3)
    spinner.stop()
    print("✓ project.inspect completed\n")


def test_multiple_spinners():
    """Test multiple spinners in sequence (simulating batch tool calls)."""
    print("\n=== Test 3: Multiple Spinners (Batch Tool Calls) ===")
    
    tools = [
        ("project.inspect", "User wants a batch call including project.inspect to get current workspace overview", 2),
        ("fs.search", "Search for references to Windows .exe download links or version numbers in the codebase", 2),
        ("fs.read_text", "Read the download section of the landing page to see the Windows exe version", 1),
    ]
    
    for tool_name, reasoning, duration in tools:
        label = f"{tool_name}: {reasoning}"
        spinner = TestSpinner(label)
        spinner.start()
        time.sleep(duration)
        spinner.stop()
        print(f"✓ {tool_name} completed")
    
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("TUI Spinner Fix Verification")
    print("=" * 60)
    print(f"Terminal Width: {get_term_width()} columns")
    
    test_short_label()
    test_long_label()
    test_multiple_spinners()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nExpected behavior:")
    print("- Each spinner should show ONE line that updates in place")
    print("- Long labels should be truncated with '...'")
    print("- No duplicate lines should be printed")
    print("- Spinner should animate smoothly")


if __name__ == "__main__":
    main()
