import math


class WeightedScore:

    def __init__(self):

        self.weights = {
            "diagnosis": 0.30,
            "security": 0.20,
            "protocol": 0.20,
            "feedback": 0.15,
            "robot": 0.15
        }

    def calculate(self, evaluation):

        score = 1.0

        for criterion, weight in self.weights.items():

            x = evaluation[criterion].score

            score *= math.pow(x, weight)

        return score