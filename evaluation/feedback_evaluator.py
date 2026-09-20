from schemas.feedback_schema import FeedbackDecision
from schemas.evaluation_schema import FeedbackEvaluation


class FeedbackEvaluator:

    def calculate_score(self, predicted, expected):
        return 1.0 if predicted == expected else 0.0

    def evaluate(
        self,
        feedback_result: FeedbackDecision,
        scenario,
    ):

        predicted = (
            feedback_result.action or ""
        ).strip().lower()

        expected = (
            scenario["Ground_Truth_Feedback"] or ""
        ).strip().lower()

        score = self.calculate_score(
            predicted,
            expected,
        )

        return FeedbackEvaluation(
            predicted_action=feedback_result.action,
            expected_action=scenario["Ground_Truth_Feedback"],
            correct=(predicted == expected),
            score=score,
        )