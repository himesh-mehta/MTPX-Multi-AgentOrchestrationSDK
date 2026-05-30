#!/usr/bin/env python3
"""
Test script for session title generation functionality.
Tests various edge cases and scenarios.
"""

import re


def _generate_session_title_from_prompt(prompt: str, max_words: int = 4, max_chars: int = 50) -> str:
    """
    Generate a session title from the first user prompt.
    
    Extracts the first 3-4 meaningful words, removing:
    - Attachment references (@file syntax)
    - Extra whitespace
    - Special characters that don't add meaning
    
    Args:
        prompt: The user's first prompt
        max_words: Maximum number of words to include (default 4)
        max_chars: Maximum character length (default 50)
    
    Returns:
        A clean, readable session title
    """
    # Remove attachment references (@file syntax)
    cleaned = re.sub(r'@[^\s]+', '', prompt)
    
    # Remove extra whitespace and newlines
    cleaned = ' '.join(cleaned.split())
    
    # Extract first N words
    words = cleaned.split()[:max_words]
    title = ' '.join(words)
    
    # Truncate to max length if needed, breaking at word boundary
    if len(title) > max_chars:
        title = title[:max_chars].rsplit(' ', 1)[0]
        if title:  # Only add ellipsis if we have content
            title += '...'
    
    # Fallback for empty or very short titles
    if len(title.strip()) < 3:
        return "Quick chat"
    
    return title.strip()


def test_title_generation():
    """Run comprehensive tests on title generation."""
    
    test_cases = [
        # (input, expected_output, description)
        ("How do I implement user authentication", "How do I implement", "Normal 4-word prompt"),
        ("Fix the login bug", "Fix the login bug", "Short prompt (3 words)"),
        ("hi", "Quick chat", "Very short prompt - fallback"),
        ("hello there", "hello there", "Two word prompt"),
        ("@src/main.py @tests/test.py explain this code", "explain this code", "Prompt with attachments"),
        ("@file.py", "Quick chat", "Only attachments - fallback"),
        ("   How   do   I   fix   this   ", "How do I fix", "Extra whitespace"),
        ("supercalifragilisticexpialidocious explain this to me please", "supercalifragilisticexpialidocious explain this to", "Very long first word"),
        ("How do I implement a really complex authentication system with OAuth", "How do I implement", "Long prompt exceeding max_chars"),
        ("What is the meaning of life the universe and everything", "What is the meaning", "More than 4 words"),
        ("Debug @app.py and @utils.py issues", "Debug and issues", "Attachments in middle"),
        ("   ", "Quick chat", "Only whitespace - fallback"),
        ("\n\nHow do I\n\nfix this\n\n", "How do I fix", "Newlines and whitespace"),
        ("Implement user authentication system", "Implement user authentication system", "Exactly 4 words"),
        ("a", "Quick chat", "Single character - fallback"),
        ("ab", "Quick chat", "Two characters - fallback"),
        ("abc", "abc", "Three characters - minimum valid"),
        ("How to fix the @bug.py in production", "How to fix the", "Attachment in middle of sentence"),
        ("@README.md @CHANGELOG.md @LICENSE what do these files contain", "what do these files", "Multiple attachments at start"),
        ("Create a new feature for handling user sessions and authentication", "Create a new feature", "Long sentence"),
        ("   @file1.py   @file2.py   ", "Quick chat", "Only attachments with spaces - fallback"),
    ]
    
    print("=" * 80)
    print("SESSION TITLE GENERATION TESTS")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, (input_prompt, expected, description) in enumerate(test_cases, 1):
        result = _generate_session_title_from_prompt(input_prompt)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"Test {i}: {status}")
        print(f"  Description: {description}")
        print(f"  Input:       '{input_prompt}'")
        print(f"  Expected:    '{expected}'")
        print(f"  Got:         '{result}'")
        
        if result != expected:
            print(f"  ❌ MISMATCH!")
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0


def test_edge_cases():
    """Test additional edge cases."""
    
    print("\n" + "=" * 80)
    print("EDGE CASE TESTS")
    print("=" * 80)
    print()
    
    # Test with different max_words settings
    prompt = "How do I implement user authentication in my application"
    
    print("Testing max_words parameter:")
    for max_words in [1, 2, 3, 4, 5, 10]:
        result = _generate_session_title_from_prompt(prompt, max_words=max_words)
        print(f"  max_words={max_words}: '{result}'")
    
    print()
    
    # Test with different max_chars settings
    print("Testing max_chars parameter:")
    for max_chars in [10, 20, 30, 50, 100]:
        result = _generate_session_title_from_prompt(prompt, max_chars=max_chars)
        print(f"  max_chars={max_chars}: '{result}'")
    
    print()


def test_real_world_scenarios():
    """Test with realistic user prompts."""
    
    print("=" * 80)
    print("REAL-WORLD SCENARIO TESTS")
    print("=" * 80)
    print()
    
    real_prompts = [
        "How do I fix the authentication bug in my Django application?",
        "Explain the difference between async and sync functions in Python",
        "Help me debug @src/main.py - the login function is not working",
        "What's the best way to implement JWT authentication?",
        "Can you review @app/models.py and suggest improvements?",
        "I need to optimize the database queries in my application",
        "How do I deploy a Flask app to AWS?",
        "Explain how React hooks work with examples",
        "Debug the memory leak in @server.js",
        "What are the best practices for API design?",
    ]
    
    for i, prompt in enumerate(real_prompts, 1):
        title = _generate_session_title_from_prompt(prompt)
        print(f"{i}. Prompt: {prompt}")
        print(f"   Title:  {title}")
        print()


if __name__ == "__main__":
    # Run all tests
    success = test_title_generation()
    test_edge_cases()
    test_real_world_scenarios()
    
    print("\n" + "=" * 80)
    if success:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED - Review output above")
    print("=" * 80)
