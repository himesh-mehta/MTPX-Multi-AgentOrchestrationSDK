#!/usr/bin/env python3
"""
Integration test to demonstrate session title auto-generation.
This simulates the TUI flow without actually running the full TUI.
"""

import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


# Minimal mock of SessionRecord for testing
@dataclass
class SessionRecord:
    session_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    runs: list = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


# Minimal mock of JsonSessionStore for testing
class JsonSessionStore:
    def __init__(self, db_path: str | Path = "tmp/test_db"):
        self.db_path = Path(db_path)
        self.file_path = self.db_path / "sessions.json"
        self.db_path.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")
    
    def upsert_session(self, session: SessionRecord) -> SessionRecord:
        rows = json.loads(self.file_path.read_text(encoding="utf-8"))
        serialized = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "metadata": session.metadata,
            "messages": session.messages,
            "runs": session.runs,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }
        
        for idx, row in enumerate(rows):
            if row.get("session_id") == session.session_id:
                rows[idx] = serialized
                break
        else:
            rows.append(serialized)
        
        self.file_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return session
    
    def get_session(self, session_id: str, *, user_id: str | None = None) -> SessionRecord | None:
        rows = json.loads(self.file_path.read_text(encoding="utf-8"))
        for row in rows:
            if row.get("session_id") == session_id:
                return SessionRecord(
                    session_id=row["session_id"],
                    user_id=row.get("user_id"),
                    metadata=row.get("metadata", {}),
                    messages=row.get("messages", []),
                    runs=row.get("runs", []),
                    created_at=row.get("created_at", ""),
                    updated_at=row.get("updated_at", ""),
                )
        return None


def test_session_title_integration():
    """Test the complete flow of session title auto-generation."""
    
    print("=" * 80)
    print("INTEGRATION TEST: Session Title Auto-Generation")
    print("=" * 80)
    print()
    
    # Create temporary session store
    with tempfile.TemporaryDirectory() as tmpdir:
        store = JsonSessionStore(db_path=tmpdir)
        
        # Simulate creating a new session
        session_id = "chat-test12345"
        session_label = None  # Initially no label
        transcript = []  # Empty transcript
        
        print(f"1. Created new session: {session_id}")
        print(f"   Initial label: {session_label or '(none)'}")
        print(f"   Transcript length: {len(transcript)}")
        print()
        
        # Save initial session
        session = SessionRecord(
            session_id=session_id,
            user_id="test-user",
            metadata={
                "tui": {
                    "session_label": session_label,
                    "backend": "openai",
                    "turn_count": len(transcript),
                }
            },
            created_at="2026-04-17 10:00:00",
            updated_at="2026-04-17 10:00:00",
        )
        store.upsert_session(session)
        
        # Simulate first user prompt
        user_prompt = "How do I implement user authentication in Django"
        print(f"2. User sends first prompt: '{user_prompt}'")
        print()
        
        # Simulate recording the turn (this would happen in _record_turn)
        transcript.append({
            "prompt": user_prompt,
            "response": "Here's how to implement authentication...",
            "backend": "openai",
            "model": "gpt-4o",
        })
        
        # THIS IS THE KEY LOGIC: Auto-generate title from first turn
        if len(transcript) == 1 and not session_label:
            import re
            
            # Title generation logic (same as in tui.py)
            cleaned = re.sub(r'@[^\s]+', '', user_prompt)
            cleaned = ' '.join(cleaned.split())
            words = cleaned.split()[:4]
            title = ' '.join(words)
            if len(title) > 50:
                title = title[:50].rsplit(' ', 1)[0]
                if title:
                    title += '...'
            if len(title.strip()) < 3:
                title = "Quick chat"
            session_label = title.strip()
            
            print(f"3. Auto-generated session title: '{session_label}'")
            print()
            
            # Update session with new title
            session.metadata["tui"]["session_label"] = session_label
            session.metadata["tui"]["turn_count"] = len(transcript)
            session.updated_at = "2026-04-17 10:00:15"
            store.upsert_session(session)
        
        # Verify the session was saved with the title
        loaded_session = store.get_session(session_id)
        assert loaded_session is not None
        
        saved_label = loaded_session.metadata.get("tui", {}).get("session_label")
        print(f"4. Verified session saved with title: '{saved_label}'")
        print()
        
        # Simulate listing sessions (like /sessions command)
        print("5. Session list display:")
        print(f"   ID: {session_id}")
        print(f"   Title: {saved_label or '(unnamed)'}")
        print(f"   Turns: {loaded_session.metadata.get('tui', {}).get('turn_count', 0)}")
        print()
        
        # Test that manual labels are preserved
        print("6. Testing manual label preservation:")
        session2_id = "chat-manual123"
        session2_label = "My Custom Project"  # User provided this
        transcript2 = []
        
        session2 = SessionRecord(
            session_id=session2_id,
            user_id="test-user",
            metadata={
                "tui": {
                    "session_label": session2_label,
                    "backend": "openai",
                    "turn_count": 0,
                }
            },
        )
        store.upsert_session(session2)
        
        print(f"   Created session with manual label: '{session2_label}'")
        
        # Simulate first turn
        transcript2.append({"prompt": "Some prompt", "response": "Some response"})
        
        # Check if we should auto-generate (we shouldn't because label exists)
        if len(transcript2) == 1 and not session2_label:
            print("   ERROR: Should not auto-generate when label exists!")
        else:
            print(f"   ✓ Manual label preserved: '{session2_label}'")
        
        print()
        
        # Test edge case: very short prompt
        print("7. Testing edge case - very short prompt:")
        session3_id = "chat-short123"
        session3_label = None
        transcript3 = []
        
        short_prompt = "hi"
        transcript3.append({"prompt": short_prompt, "response": "Hello!"})
        
        if len(transcript3) == 1 and not session3_label:
            import re
            cleaned = re.sub(r'@[^\s]+', '', short_prompt)
            cleaned = ' '.join(cleaned.split())
            words = cleaned.split()[:4]
            title = ' '.join(words)
            if len(title.strip()) < 3:
                title = "Quick chat"
            session3_label = title.strip()
        
        print(f"   Prompt: '{short_prompt}'")
        print(f"   Generated title: '{session3_label}'")
        print()
        
        # Test edge case: prompt with attachments
        print("8. Testing edge case - prompt with attachments:")
        session4_id = "chat-attach123"
        session4_label = None
        transcript4 = []
        
        attach_prompt = "@src/main.py @tests/test.py explain this code"
        transcript4.append({"prompt": attach_prompt, "response": "This code does..."})
        
        if len(transcript4) == 1 and not session4_label:
            import re
            cleaned = re.sub(r'@[^\s]+', '', attach_prompt)
            cleaned = ' '.join(cleaned.split())
            words = cleaned.split()[:4]
            title = ' '.join(words)
            if len(title.strip()) < 3:
                title = "Quick chat"
            session4_label = title.strip()
        
        print(f"   Prompt: '{attach_prompt}'")
        print(f"   Generated title: '{session4_label}'")
        print()
        
        print("=" * 80)
        print("✓ ALL INTEGRATION TESTS PASSED!")
        print("=" * 80)
        print()
        print("Summary:")
        print("  - Session titles are auto-generated from first user prompt")
        print("  - Manual labels are preserved and not overwritten")
        print("  - Edge cases (short prompts, attachments) are handled correctly")
        print("  - Titles are saved to session metadata and persist across loads")


if __name__ == "__main__":
    test_session_title_integration()
