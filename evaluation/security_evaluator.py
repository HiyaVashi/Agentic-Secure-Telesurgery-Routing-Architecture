from schemas.security_schema import SecurityAssessment
from schemas.evaluation_schema import SecurityEvaluation
import pandas as pd

class SecurityEvaluator:

    def calculate_score(
        self,
        predicted_detected,
        expected_detected,
        predicted_attack,
        expected_attack,
        predicted_action,
        expected_action,
    ):
        score = 0.0

        if predicted_detected == expected_detected:
            score += 0.4

        if predicted_attack == expected_attack:
            score += 0.3

        if predicted_action == expected_action:
            score += 0.3

        return score

    def evaluate(self, security_result: SecurityAssessment, scenario):

    # Expected values from dataset
        attack_value = scenario.get("Attack", "")

        if pd.isna(attack_value):
            attack_value = "None"

        expected_attack = str(attack_value).strip().lower()

        expected_detected = expected_attack != "none"

        action_value = scenario.get("Ground_Truth_Security_Action", "")

        if pd.isna(action_value):
            action_value = ""

        expected_action = str(action_value).strip().lower()

    # Predicted values
        predicted_detected = security_result.attack_detected

        predicted_attack = (
            security_result.attack_type or ""
        ).strip().lower()

        predicted_action = (
            security_result.recommended_action or ""
        ).strip().lower()

    # Score
        score = self.calculate_score(
            predicted_detected,
            expected_detected,
            predicted_attack,
            expected_attack,
            predicted_action,
            expected_action,
        )

        return SecurityEvaluation(
            predicted_attack_detected=predicted_detected,
            expected_attack_detected=expected_detected,

            predicted_attack=security_result.attack_type,
            expected_attack=expected_attack,

            predicted_action=security_result.recommended_action,
            expected_action=expected_action,

            attack_detection_correct=predicted_detected == expected_detected,
            attack_type_correct=predicted_attack == expected_attack,
            action_correct=predicted_action == expected_action,

            score=score,
        )