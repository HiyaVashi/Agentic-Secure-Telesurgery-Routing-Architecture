from schemas.robotic_schema import RoboticResponse
from schemas.evaluation_schema import RobotEvaluation


class RobotEvaluator:

    def calculate_score(
        self,
        predicted_status,
        expected_status,
        predicted_action,
        expected_action,
    ):
        """
        Score:
        0.5 -> Robot status
        0.5 -> Robot action
        """

        score = 0.0

        if predicted_status == expected_status:
            score += 0.5

        if predicted_action == expected_action:
            score += 0.5

        return score

    def evaluate(
        self,
        robot_result: RoboticResponse,
        scenario,
    ):

        predicted_status = (
            robot_result.status or ""
        ).strip().lower()

        predicted_action = (
            robot_result.action or ""
        ).strip().lower()

        # Assuming successful execution is the expected status
        expected_status = "success"

        expected_action = (
            scenario["Ground_Truth_Robot_Action"] or ""
        ).strip().lower()

        score = self.calculate_score(
            predicted_status,
            expected_status,
            predicted_action,
            expected_action,
        )

        return RobotEvaluation(
            predicted_status=robot_result.status,
            expected_status="SUCCESS",

            predicted_action=robot_result.action,
            expected_action=scenario["Ground_Truth_Robot_Action"],

            status_correct=(predicted_status == expected_status),
            action_correct=(predicted_action == expected_action),

            score=score,
        )