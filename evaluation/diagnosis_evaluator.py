from schemas.evaluation_schema import DiagnosisEvaluation
def normalize_diagnosis(text):
    if text is None:
        return ""

    text = str(text).lower().strip()

    synonyms = {
        "acute appendicitis": "appendicitis",
        "normal appendicitis": "appendicitis",
        "appendicitis": "appendicitis",
    }

    return synonyms.get(text, text)

class DiagnosisEvaluator:
    def calculate_score(self, predicted, expected):
        return 1.0 if predicted == expected else 0.0
    def evaluate(self, doctor_result, ground_truth):

        predicted = normalize_diagnosis(doctor_result.diagnosis)
        expected = normalize_diagnosis(ground_truth)

        correct = predicted == expected

        score = 1.0 if correct else 0.0

        return DiagnosisEvaluation(
            predicted=doctor_result.diagnosis,
            expected=ground_truth,
            correct=correct,
            score=1.0 if correct else 0.0
        )

    