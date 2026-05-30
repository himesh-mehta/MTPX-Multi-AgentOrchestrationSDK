from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def launch() -> int:
    try:
        import streamlit  # noqa: F401
    except Exception:  # noqa: BLE001
        print("Streamlit is not installed. Install with: pip install mtpx[ui-streamlit]", file=sys.stderr)
        return 1

    app_path = Path(__file__).resolve().parent / "app.py"
    launch_cwd = Path.cwd().resolve()
    env = os.environ.copy()
    env["MTP_AGENT_OS_CWD"] = str(launch_cwd)
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    proc = subprocess.run(cmd, check=False, cwd=str(launch_cwd), env=env)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(launch())
