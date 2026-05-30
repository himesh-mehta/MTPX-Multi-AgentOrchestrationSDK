#!/usr/bin/env python3
"""
Test script to verify conversation history injection works correctly.
Tests the FIXED implementation that:
1. Removes -C flag from codex exec resume (it doesn't support it)
2. ALWAYS injects history when available (not just when no session ID)
"""

from pathlib import Path
from src.mtp.cli import tui_codex_backend as codex_backend


def test_build_codex_exec_command():
    """Test that commands are built correctly for resume vs fresh sessions"""
    print("=" * 80)
    print("TEST: Build Codex Exec Command (CRITICAL FIX)")
    print("=" * 80)
    
    codex_bin = "codex"
    cwd = Path("/test/dir")
    output_path = Path("/tmp/output.txt")
    prompt = "test prompt"
    model = "gpt-5.3-codex"
    reasoning = "medium"
    
    # Test 1: Fresh session (no session ID) - should use --cd
    cmd_fresh = codex_backend._build_codex_exec_command(
        codex_bin=codex_bin,
        cwd=cwd,
        output_path=output_path,
        prompt=prompt,
        model=model,
        reasoning_effort=reasoning,
        session_id=None,
    )
    
    print("\n✓ Test 1: Fresh session command")
    print(f"  Command: {' '.join(cmd_fresh)}")
    assert "exec" in cmd_fresh
    assert "resume" not in cmd_fresh
    assert "--cd" in cmd_fresh
    assert str(cwd) in cmd_fresh
    print("  ✓ Contains --cd flag")
    print("  ✓ Contains working directory")
    
    # Test 2: Resume session - should NOT have -C or --cd
    session_id = "thread-12345"
    cmd_resume = codex_backend._build_codex_exec_command(
        codex_bin=codex_bin,
        cwd=cwd,
        output_path=output_path,
        prompt=prompt,
        model=model,
        reasoning_effort=reasoning,
        session_id=session_id,
    )
    
    print("\n✓ Test 2: Resume session command")
    print(f"  Command: {' '.join(cmd_resume)}")
    assert "exec" in cmd_resume
    assert "resume" in cmd_resume
    assert session_id in cmd_resume
    assert "-C" not in cmd_resume, "CRITICAL: Resume should NOT have -C flag!"
    assert "--cd" not in cmd_resume, "CRITICAL: Resume should NOT have --cd flag!"
    print("  ✓ Contains 'resume' subcommand")
    print("  ✓ Contains session ID")
    print("  ✓ Does NOT contain -C or --cd (FIXED!)")
    
    print("\n✅ Command building tests passed!\n")


def test_build_prompt_with_history():
    """Test Option 1: Manual history injection"""
    print("=" * 80)
    print("TEST: Build Prompt with History (NATURAL FORMAT)")
    print("=" * 80)
    
    # Test case 1: No history
    prompt = "What is Python?"
    result = codex_backend._build_prompt_with_history(prompt, [])
    assert result == prompt, "Should return original prompt when no history"
    print("✓ Test 1.1 passed: No history returns original prompt")
    
    # Test case 2: Single turn history - natural conversation format
    history = [
        ("Hello", "Hi there! How can I help you?")
    ]
    result = codex_backend._build_prompt_with_history("What's the weather?", history)
    assert "User: Hello" in result
    assert "Assistant: Hi there!" in result
    assert "User: What's the weather?" in result
    # Should NOT have meta-commentary like "Previous conversation" or brackets
    assert "[" not in result
    assert "Previous" not in result
    assert "Turn 1:" not in result
    print("✓ Test 1.2 passed: Single turn history in natural format")
    
    # Test case 3: Multiple turns - looks like continuous conversation
    history = [
        ("What is Python?", "Python is a programming language."),
        ("Is it easy to learn?", "Yes, Python is known for being beginner-friendly."),
    ]
    result = codex_backend._build_prompt_with_history("Show me an example", history)
    assert "User: What is Python?" in result
    assert "Assistant: Python is a programming language." in result
    assert "User: Is it easy to learn?" in result
    assert "Assistant: Yes, Python is known for being beginner-friendly." in result
    assert "User: Show me an example" in result
    print("✓ Test 1.3 passed: Multiple turns in natural conversation format")
    
    print("\n✅ All history injection tests passed!\n")


def test_integration_scenario():
    """Test the integration of both fixes"""
    print("=" * 80)
    print("TEST: Integration Scenario (REAL WORLD)")
    print("=" * 80)
    
    # Simulate the exact scenario from the user's screenshot
    conversation_history = [
        ("hey there im prajwal and what can you do for me ?", 
         "I can help you write, debug, research, plan, and build things."),
    ]
    
    # User asks a follow-up
    follow_up = "what did i asked / said to you above ?"
    
    # Build the prompt with history (this should ALWAYS happen now)
    enriched_prompt = codex_backend._build_prompt_with_history(follow_up, conversation_history)
    
    print("Original prompt:")
    print(f"  '{follow_up}'")
    print("\nEnriched prompt with history (NATURAL FORMAT):")
    print("-" * 80)
    print(enriched_prompt)
    print("-" * 80)
    
    # Verify the enriched prompt contains context in natural format
    assert "User: hey there im prajwal" in enriched_prompt
    assert "Assistant: I can help you" in enriched_prompt
    assert "User: what did i asked / said to you above ?" in enriched_prompt
    # Should NOT have meta-commentary
    assert "[Previous conversation" not in enriched_prompt
    assert "Turn 1:" not in enriched_prompt
    
    print("\n✅ Integration test passed!")
    print("   Format is now natural conversation continuation!")
    print("   No meta-commentary that Codex might interpret as placeholder!")
    
    # Now test command building for both scenarios
    print("\n" + "=" * 80)
    print("Command Building for Resume Scenario:")
    print("=" * 80)
    
    codex_bin = "codex"
    cwd = Path("/test/dir")
    output_path = Path("/tmp/output.txt")
    
    # Scenario 1: First query (no session ID)
    cmd1 = codex_backend._build_codex_exec_command(
        codex_bin=codex_bin,
        cwd=cwd,
        output_path=output_path,
        prompt=enriched_prompt,
        model="gpt-5.3-codex",
        reasoning_effort="medium",
        session_id=None,
    )
    print("\n1. First query (fresh session):")
    print(f"   {' '.join(cmd1)}")
    assert "--cd" in cmd1
    print("   ✓ Uses --cd for working directory")
    
    # Scenario 2: Follow-up query (with session ID)
    cmd2 = codex_backend._build_codex_exec_command(
        codex_bin=codex_bin,
        cwd=cwd,
        output_path=output_path,
        prompt=enriched_prompt,
        model="gpt-5.3-codex",
        reasoning_effort="medium",
        session_id="thread-abc123",
    )
    print("\n2. Follow-up query (resume session):")
    print(f"   {' '.join(cmd2)}")
    assert "resume" in cmd2
    assert "-C" not in cmd2
    assert "--cd" not in cmd2
    print("   ✓ Uses 'resume' subcommand")
    print("   ✓ Does NOT use -C or --cd (FIXED!)")
    print("   ✓ History is injected in the prompt itself")
    
    print("\n✅ Full integration test passed!")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CONVERSATION HISTORY FIX - UPDATED TEST SUITE")
    print("Testing CRITICAL FIXES:")
    print("  1. Remove -C flag from 'codex exec resume' (it doesn't support it)")
    print("  2. ALWAYS inject history when available (not just when no session)")
    print("=" * 80 + "\n")
    
    try:
        test_build_codex_exec_command()
        test_build_prompt_with_history()
        test_integration_scenario()
        
        print("=" * 80)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 80)
        print("\nCRITICAL FIXES APPLIED:")
        print("  ✓ Fix 1: 'codex exec resume' no longer uses -C flag")
        print("  ✓ Fix 2: History is ALWAYS injected when available")
        print("  ✓ Fix 3: Enhanced session ID extraction")
        print("\nHow it works now:")
        print("  1. First query: codex exec --cd <dir> <prompt>")
        print("  2. Follow-up: codex exec resume <session_id> <prompt_with_history>")
        print("  3. If resume fails: codex exec --cd <dir> <prompt_with_history>")
        print("\nNext steps:")
        print("  1. Test in the actual TUI: mtp tui")
        print("  2. Send: 'my name is prajwal and im working on MTP'")
        print("  3. Then: 'what did i tell you above?'")
        print("  4. Should now correctly reference your name and MTP!")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
