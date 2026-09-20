"""
evaluation/base_result.py
─────────────────────────

Common result model used by all evaluation modules.
"""

from dataclasses import dataclass, field

from langchain_protocol import Any


@dataclass
class EvaluationResult:

    # Name of criterion
    criterion: str

    # Final normalized score (0–1)
    normalized: float

    # Raw score before normalization (optional)
    raw_score: float | None = None

    # Store any additional metric values
    from typing import Any

    details: dict[str, Any] = field(default_factory=dict)
    