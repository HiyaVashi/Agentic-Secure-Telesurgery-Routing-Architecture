"""
evaluation/security_accuracy.py
───────────────────────────────

Evaluates the Security Response Accuracy.

Compares the security-related workflow outputs against
the expected ground truth.

Returns a normalized score in [0,1].
"""

from evaluation.base_result import EvaluationResult


class SecurityAccuracy:

    @staticmethod
    def calculate(
        expected_output: dict,
        workflow_state: dict,
    ) -> EvaluationResult:

        score = 0

        details = {}

        total = 4

        # ---------------------------------------------------------
        # Attack Detection
        # ---------------------------------------------------------

        expected_detection = str(
            expected_output.get("security_action", "")
        ).strip().lower() != "no action"

        predicted_detection = bool(
            workflow_state.get("security_report", {})
            .get("attack_detected", False)
        )

        attack_detection = int(
            expected_detection == predicted_detection
        )

        details["attack_detection"] = {
            "expected": expected_detection,
            "predicted": predicted_detection,
            "correct": bool(attack_detection),
        }

        score += attack_detection

        # ---------------------------------------------------------
        # Attack Classification
        # ---------------------------------------------------------

        expected_attack = str(
            expected_output.get("attack_type", "")
        ).strip().lower()

        predicted_attack = str(
            workflow_state.get("security_report", {})
            .get("attack_type", "")
        ).strip().lower()

        attack_classification = int(
            expected_attack == predicted_attack
        )

        details["attack_classification"] = {
            "expected": expected_attack,
            "predicted": predicted_attack,
            "correct": bool(attack_classification),
        }

        score += attack_classification

        # ---------------------------------------------------------
        # Security Action
        # ---------------------------------------------------------

        expected_action = str(
            expected_output.get("security_action", "")
        ).strip().lower()

        predicted_action = str(
            workflow_state.get("security_report", {})
            .get("recommended_action", "")
        ).strip().lower()

        mitigation = int(
            expected_action == predicted_action
        )

        details["mitigation"] = {
            "expected": expected_action,
            "predicted": predicted_action,
            "correct": bool(mitigation),
        }

        score += mitigation

        # ---------------------------------------------------------
        # Protocol Selection
        # ---------------------------------------------------------

        expected_protocol = str(
            expected_output.get("protocol", "")
        ).strip().upper()

        predicted_protocol = str(
            workflow_state.get("protocol_status", {})
            .get("recommended_protocol", "")
        ).strip().upper()

        protocol = int(
            expected_protocol == predicted_protocol
        )

        details["protocol"] = {
            "expected": expected_protocol,
            "predicted": predicted_protocol,
            "correct": bool(protocol),
        }

        score += protocol

        # ---------------------------------------------------------

        normalized = score / total

        return EvaluationResult(

            criterion="Security Response Accuracy",

            normalized=round(normalized, 4),

            raw_score=score,

            details=details,

        )