from evaluation.diagnosis_evaluator import DiagnosisEvaluator
from evaluation.security_evaluator import SecurityEvaluator
from evaluation.protocol_evaluator import ProtocolEvaluator
from evaluation.feedback_evaluator import FeedbackEvaluator
from evaluation.robot_evaluator import RobotEvaluator


class WorkflowEvaluator:

    def __init__(self):
        self.diagnosis_evaluator = DiagnosisEvaluator()
        self.security_evaluator = SecurityEvaluator()
        self.protocol_evaluator = ProtocolEvaluator()
        self.feedback_evaluator = FeedbackEvaluator()
        self.robot_evaluator = RobotEvaluator()

    def evaluate(self, workflow_result, scenario):

        diagnosis_result = self.diagnosis_evaluator.evaluate(
            workflow_result["doctor"],
            scenario["Ground_Truth_Diagnosis"]
        )

        security_result = self.security_evaluator.evaluate(
            workflow_result["security"],
            scenario
        )

        protocol_result = self.protocol_evaluator.evaluate(
            workflow_result["protocol"],
            scenario
        )

        feedback_result = self.feedback_evaluator.evaluate(
            workflow_result["feedback"],
            scenario
        )

        robot_result = self.robot_evaluator.evaluate(
            workflow_result["robot"],
            scenario
        )

        overall_score = (
            diagnosis_result.score
            + security_result.score
            + protocol_result.score
            + feedback_result.score
            + robot_result.score
        ) / 5

        return {
            "diagnosis": diagnosis_result,
            "security": security_result,
            "protocol": protocol_result,
            "feedback": feedback_result,
            "robot": robot_result,
            "overall_score": overall_score,
        }