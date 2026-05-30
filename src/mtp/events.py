from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class EventStreamContext:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    sequence: int = 0

    def emit(self, event_type: str, **payload: Any) -> dict[str, Any]:
        self.sequence += 1
        reserved = {"type", "timestamp", "run_id", "sequence", "data"}
        flat_payload = {key: value for key, value in payload.items() if key not in reserved}
        return {
            "type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "run_id": self.run_id,
            "sequence": self.sequence,
            "data": dict(payload),
            **flat_payload,
        }
