"""
evaluation/workflow_accuracy.py
───────────────────────────────

Evaluates Workflow Decision Accuracy.

Compares the actual workflow outputs against the
expected ground truth.

Doctor
Security
Protocol
Feedback
Robotic Arm

Each component contributes equally.
"""

from evaluation.base_result import EvaluationResult


class WorkflowAccuracy:

    @staticmethod
    def calculate(
        expected_output: dict,
        workflow_state: dict,
    ) -> EvaluationResult:

        score = 0

        details = {}

        # ---------------------------------------------------------
        # Doctor
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("diagnosis", "")
        ).strip().lower()

        predicted = str(
            workflow_state.get("diagnosis", {})
            .get("diagnosis", "")
        ).strip().lower()

        doctor = int(expected == predicted)

        details["doctor"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(doctor),
        }

        score += doctor

        # ---------------------------------------------------------
        # Security
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("security_action", "")
        ).strip().lower()

        predicted = str(
            workflow_state.get("security_report", {})
            .get("recommended_action", "")
        ).strip().lower()

        security = int(expected == predicted)

        details["security"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(security),
        }

        score += security

        # ---------------------------------------------------------
        # Protocol
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("protocol", "")
        ).strip().upper()

        predicted = str(
            workflow_state.get("protocol_status", {})
            .get("recommended_protocol", "")
        ).strip().upper()

        protocol = int(expected == predicted)

        details["protocol"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(protocol),
        }

        score += protocol

        # ---------------------------------------------------------
        # Feedback
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("feedback", "")
        ).strip().lower()

        predicted = (
            "proceed"
            if workflow_state.get("feedback", {})
            .get("proceed_with_surgery", False)
            else "hold"
        )

        feedback = int(expected == predicted)

        details["feedback"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(feedback),
        }

        score += feedback

        # ---------------------------------------------------------
        # Robotic Arm
        # ---------------------------------------------------------

        expected = str(
            expected_output.get("robot_action", "")
        ).strip().lower()

        predicted = str(
            workflow_state.get("arm_result", {})
            .get("step_name", "")
        ).strip().lower()

        robot = int(expected == predicted)

        details["robot"] = {
            "expected": expected,
            "predicted": predicted,
            "correct": bool(robot),
        }

        score += robot

        # ---------------------------------------------------------

        normalized = score / 5

        return EvaluationResult(

            criterion="Workflow Decision Accuracy",

            normalized=round(normalized, 4),

            raw_score=score,

            details=details,

        )