"""
utils/similarity.py
───────────────────

Utility functions for semantic text comparison using RapidFuzz.
"""

from rapidfuzz import fuzz


class Similarity:

    # ---------------------------------------------------------
    # Matching Thresholds
    # ---------------------------------------------------------

    DIAGNOSIS_THRESHOLD = 90
    SURGERY_THRESHOLD = 85
    RISK_THRESHOLD = 80
    GENERAL_THRESHOLD = 85

    # ---------------------------------------------------------

    @staticmethod
    def score(expected: str, predicted: str) -> float:
        """
        Returns similarity score (0–100).
        """

        expected = expected.strip().lower()
        predicted = predicted.strip().lower()

        return fuzz.token_sort_ratio(expected, predicted)

    # ---------------------------------------------------------

    @classmethod
    def compare(
        cls,
        expected: str,
        predicted: str,
        threshold: int = None
    ) -> dict:
        """
        Compare two strings and return both the similarity score
        and whether it satisfies the threshold.

        Returns
        -------
        {
            "score": 94.25,
            "match": True
        }
        """

        if threshold is None:
            threshold = cls.GENERAL_THRESHOLD

        similarity = cls.score(expected, predicted)

        return {

            "score": round(similarity, 2),
            "threshold": threshold,
            "match": similarity >= threshold

        }

    # ---------------------------------------------------------

    @classmethod
    def is_match(
        cls,
        expected: str,
        predicted: str,
        threshold: int = None
    ) -> bool:

        return cls.compare(
            expected,
            predicted,
            threshold
        )["match"]
    