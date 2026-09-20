"""
evaluation/hallucination.py
───────────────────────────

Evaluates the Clinical Hallucination Rate.

Compares the Doctor Agent output against the expected
ground-truth diagnosis and surgical recommendation.

Returns a normalized score in [0,1].
"""

from evaluation.base_result import EvaluationResult


class ClinicalHallucination:

    @staticmethod
    def calculate(
        expected_output: dict,
        workflow_state: dict,
    ) -> EvaluationResult:

        score = 0

        details = {}

        total = 3

        # ---------------------------------------------------------
        # Diagnosis
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("diagnosis", "")
        ).strip().lower()

        predicted = str(
            workflow_state.get("diagnosis", {})
            .get("diagnosis", "")
        ).strip().lower()

        diagnosis = int(expected == predicted)

        details["diagnosis"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(diagnosis),
        }

        score += diagnosis

        # ---------------------------------------------------------
        # Surgical Plan
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("surgery_type", "")
        ).strip().lower()

        predicted = str(
            workflow_state.get("surgery_plan", {})
            .get("surgery_type", "")
        ).strip().lower()

        surgery = int(expected == predicted)

        details["surgical_plan"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(surgery),
        }

        score += surgery

        # ---------------------------------------------------------
        # Priority / Risk
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("priority", "")
        ).strip().lower()

        predicted = str(
            workflow_state.get("surgery_plan", {})
            .get("priority", "")
        ).strip().lower()

        priority = int(expected == predicted)

        details["priority"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(priority),
        }

        score += priority

        # ---------------------------------------------------------

        normalized = score / total

        return EvaluationResult(

            criterion="Clinical Hallucination Rate",

            normalized=round(normalized, 4),

            raw_score=score,

            details=details,

        )