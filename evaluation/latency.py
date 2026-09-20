"""
evaluation/latency.py
─────────────────────

Evaluates response latency.

Metrics

• TTFT
• Total Generation Time
• Average Agent Response Time

Returns

Normalized score between 0 and 1.
"""

from dataclasses import dataclass


from evaluation.base_result import EvaluationResult


class LatencyEvaluator:

    # ---------------------------------------------------------
    # Thresholds
    # (Adjust later after collecting experimental data)
    # ---------------------------------------------------------

    IDEAL_TOTAL_TIME = 5.0

    MAX_TOTAL_TIME = 20.0

    @classmethod
    def calculate(cls, metrics):

        total_time = metrics["total_generation_time"]

        ttft = metrics["ttft"]

        average_time = metrics["average_agent_time"]

        # -----------------------------------------------------
        # Normalize
        #
        # <= IDEAL → 1
        #
        # >= MAX   → 0
        #
        # Linear in-between
        # -----------------------------------------------------

        if total_time <= cls.IDEAL_TOTAL_TIME:

            normalized = 1.0

        elif total_time >= cls.MAX_TOTAL_TIME:

            normalized = 0.0

        else:

            normalized = (

                cls.MAX_TOTAL_TIME -

                total_time

            ) / (

                cls.MAX_TOTAL_TIME -

                cls.IDEAL_TOTAL_TIME

            )

        return EvaluationResult(

            criterion="Response Latency",

            normalized=round(normalized,4),

            raw_score=round(total_time,4),

            details={

                "ttft": round(ttft,4),

                "total_time": round(total_time,4),

                "average_agent_time": round(average_time,4)

            }

        )
    