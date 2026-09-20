from schemas.protocol_schema import ProtocolDecision
from schemas.evaluation_schema import ProtocolEvaluation


class ProtocolEvaluator:

    def calculate_score(self, predicted, expected):
        """
        Returns:
            1.0 -> Correct protocol selected
            0.0 -> Incorrect protocol selected
        """

        return 1.0 if predicted == expected else 0.0

    def evaluate(
        self,
        protocol_result: ProtocolDecision,
        scenario
    ):

        predicted = (
            protocol_result.protocol or ""
        ).strip().lower()

        expected = (
            scenario["Ground_Truth_Protocol"] or ""
        ).strip().lower()

        score = self.calculate_score(
            predicted,
            expected
        )

        return ProtocolEvaluation(
            predicted=protocol_result.protocol,
            expected=scenario["Ground_Truth_Protocol"],
            correct=(predicted == expected),
            score=score
        )