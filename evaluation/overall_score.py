"""
evaluation/overall_score.py
───────────────────────────
Computes the Overall Performance Score using the
Weighted Geometric Mean.

Paper Formula
-------------

                n
Score = Π (x_i ^ w_i)
        i=1

where

x_i = Normalized score of criterion i
w_i = Weight of criterion i

Constraints
-----------
• All scores must be normalized to [0,1]
• Sum of weights must equal 1
"""

from math import prod


class OverallScore:

    """
    Computes the weighted geometric mean of all evaluation criteria.
    """

    # -------------------------------------------------------------
    # Criterion Weights
    # (Modify later if required by your paper)
    # -------------------------------------------------------------

    WEIGHTS = {

        "response_latency": 0.15,

        "edge_efficiency": 0.15,

        "operational_robustness": 0.20,

        "workflow_accuracy": 0.20,

        "clinical_hallucination": 0.15,

        "security_accuracy": 0.15,
    }

    # -------------------------------------------------------------

    @classmethod
    def calculate(cls, scores: dict) -> float:
        """
        Calculate the weighted geometric mean.

        Parameters
        ----------
        scores

        Example

        {
            "response_latency":0.93,
            "edge_efficiency":0.88,
            "operational_robustness":0.84,
            "workflow_accuracy":0.91,
            "clinical_hallucination":0.97,
            "security_accuracy":0.90
        }

        Returns
        -------
        float
            Overall performance score.
        """

        # ---------------------------------------------------------
        # Validate Keys
        # ---------------------------------------------------------

        missing = set(cls.WEIGHTS) - set(scores)

        if missing:
            raise ValueError(
                f"Missing evaluation scores: {sorted(missing)}"
            )

        # ---------------------------------------------------------
        # Validate Weight Sum
        # ---------------------------------------------------------

        weight_sum = sum(cls.WEIGHTS.values())

        if abs(weight_sum - 1.0) > 1e-9:
            raise ValueError(
                f"Weights must sum to 1. Current sum = {weight_sum}"
            )

        # ---------------------------------------------------------
        # Validate Score Range
        # ---------------------------------------------------------

        for criterion, score in scores.items():

            if not (0.0 <= score <= 1.0):

                raise ValueError(
                    f"{criterion} must be normalized between 0 and 1."
                )

        # ---------------------------------------------------------
        # Weighted Geometric Mean
        # ---------------------------------------------------------

        overall_score = prod(

            scores[criterion] ** weight

            for criterion, weight in cls.WEIGHTS.items()

        )

        return round(overall_score, 4)
    