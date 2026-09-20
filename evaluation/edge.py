"""
evaluation/edge.py
──────────────────

Evaluates Edge Deployment Efficiency.

Metrics
-------
• CPU Usage
• RAM Usage
• Model Size
• Tokens/sec

Returns
-------
EvaluationResult
"""

from evaluation.base_result import EvaluationResult


class EdgeEfficiency:

    # -------------------------------------------------
    # Reference Values
    # (Modify later if required)
    # -------------------------------------------------

    MAX_CPU = 100.0          # %
    MAX_RAM = 16.0           # GB

    # Approximate model sizes (GB)
    MODEL_SIZES = {

        "llama3.2": 2.0,

        "vibethinker1.5": 4.5

    }

    IDEAL_TOKENS_PER_SEC = 40.0

    # -------------------------------------------------

    @classmethod
    def calculate(
        cls,
        metrics: dict,
        model_name: str
    ):

        cpu = metrics["cpu_percent"]

        ram = metrics["ram_gb"]

        tps = metrics["tokens_per_second"]

        model_size = cls.MODEL_SIZES.get(
            model_name.lower(),
            2.0
        )

        # ----------------------------
        # Individual Scores
        # ----------------------------

        cpu_score = max(
            0,
            1 - (cpu / cls.MAX_CPU)
        )

        ram_score = max(
            0,
            1 - (ram / cls.MAX_RAM)
        )

        model_score = max(
            0,
            1 - (model_size / 10)
        )

        tps_score = min(
            tps / cls.IDEAL_TOKENS_PER_SEC,
            1
        )

        normalized = (

            cpu_score +

            ram_score +

            model_score +

            tps_score

        ) / 4

        return EvaluationResult(

            criterion="Edge Deployment Efficiency",

            normalized=round(normalized,4),

            raw_score=round(normalized * 100,2),

            details={

                "cpu_percent": round(cpu,2),

                "ram_gb": round(ram,2),

                "model_size_gb": model_size,

                "tokens_per_second": round(tps,2),

                "cpu_score": round(cpu_score,4),

                "ram_score": round(ram_score,4),

                "model_score": round(model_score,4),

                "tps_score": round(tps_score,4)

            }

        )
    