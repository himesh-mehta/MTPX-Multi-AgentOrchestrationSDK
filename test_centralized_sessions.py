#!/usr/bin/env python3
"""
Test centralized session storage with directory grouping.
"""

import json
import tempfile
from pathlib import Path
from collections import defaultdict


def simulate_session_grouping():
    """Simulate how sessions will be grouped by directory."""
    
    print("=" * 80)
    print("CENTRALIZED SESSION STORAGE - DIRECTORY GROUPING DEMO")
    print("=" * 80)
    print()
    
    # Simulate sessions from different directories
    sessions = [
        {
            "session_id": "chat-abc123",
            "metadata": {
                "tui": {
                    "session_label": "Fix authentication bug",
                    "cwd": "/home/user/projects/webapp",
                    "backend": "openai",
                    "turn_count": 5,
                    "updated_at": "2026-04-17 10:30:00"
                }
            }
        },
        {
            "session_id": "chat-def456",
            "metadata": {
                "tui": {
                    "session_label": "Implement user login",
                    "cwd": "/home/user/projects/webapp",
                    "backend": "groq",
                    "turn_count": 3,
                    "updated_at": "2026-04-17 11:00:00"
                }
            }
        },
        {
            "session_id": "chat-ghi789",
            "metadata": {
                "tui": {
                    "session_label": "Debug API endpoint",
                    "cwd": "/home/user/projects/api-service",
                    "backend": "claude",
                    "turn_count": 7,
                    "updated_at": "2026-04-17 09:15:00"
                }
            }
        },
        {
            "session_id": "chat-jkl012",
            "metadata": {
                "tui": {
                    "session_label": "Optimize database queries",
                    "cwd": "/home/user/projects/webapp",
                    "backend": "openai",
                    "turn_count": 2,
                    "updated_at": "2026-04-17 14:20:00"
                }
            }
        },
        {
            "session_id": "chat-mno345",
            "metadata": {
                "tui": {
                    "session_label": "Setup CI/CD pipeline",
                    "cwd": "/home/user/projects/devops",
                    "backend": "codex",
                    "turn_count": 4,
                    "updated_at": "2026-04-17 08:45:00"
                }
            }
        },
    ]
    
    # Current working directory
    current_cwd = "/home/user/projects/webapp"
    
    print("SCENARIO:")
    print(f"  Current directory: {current_cwd}")
    print(f"  Total sessions: {len(sessions)}")
    print(f"  All sessions stored in: ~/.mtp/sessions/")
    print()
    
    # Group sessions by directory
    sessions_by_dir = defaultdict(list)
    for session in sessions:
        cwd = session["metadata"]["tui"]["cwd"]
        sessions_by_dir[cwd].append(session)
    
    print("SESSIONS GROUPED BY DIRECTORY:")
    print()
    
    # Sort: current directory first, then alphabetically
    sorted_dirs = sorted(sessions_by_dir.keys(), key=lambda d: (d != current_cwd, d))
    
    for dir_path in sorted_dirs:
        dir_sessions = sessions_by_dir[dir_path]
        is_current = dir_path == current_cwd
        dir_name = Path(dir_path).name
        
        if is_current:
            print(f"  ● {dir_name} (current directory)")
        else:
            print(f"  ○ {dir_name}")
        
        for session in dir_sessions:
            meta = session["metadata"]["tui"]
            sid_short = session["session_id"].split("-")[-1][:8]
            label = meta["session_label"]
            backend = meta["backend"]
            turns = meta["turn_count"]
            updated = meta["updated_at"]
            
            print(f"    {sid_short} {label}")
            print(f"      {backend} • {turns} turns • {updated}")
        
        print()
    
    print("=" * 80)
    print("KEY BENEFITS:")
    print("=" * 80)
    print()
    print("✓ All sessions stored in ONE central location (~/.mtp/sessions/)")
    print("✓ Sessions from current directory shown FIRST")
    print("✓ Easy to see which sessions belong to which project")
    print("✓ No more scattered session databases across directories")
    print("✓ Sessions persist even if you delete project directories")
    print()
    
    print("=" * 80)
    print("MIGRATION:")
    print("=" * 80)
    print()
    print("Old behavior:")
    print("  • Each directory had its own tmp/mtp_tui_sessions/")
    print("  • Sessions were isolated per directory")
    print("  • Hard to find sessions across projects")
    print()
    print("New behavior:")
    print("  • All sessions in ~/.mtp/sessions/")
    print("  • Grouped by directory when displayed")
    print("  • Current directory sessions shown first")
    print()


if __name__ == "__main__":
    simulate_session_grouping()
