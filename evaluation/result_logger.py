import os
import csv


class ResultLogger:

    def __init__(self, filename="results/experiment_results.csv"):

        self.filename = filename

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if not os.path.exists(filename):

            with open(filename, "w", newline="", encoding="utf-8") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Scenario_ID",
                    "Model",

                    "Diagnosis_Score",
                    "Security_Score",
                    "Protocol_Score",
                    "Feedback_Score",
                    "Robot_Score",

                    "Overall_Score",
                    "Weighted_Distance",

                    "Execution_Time"
                ])

    def log(
        self,
        scenario_id,
        model,
        workflow_result,
        weighted_distance,
        execution_time
    ):

        with open(self.filename, "a", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([

                scenario_id,

                model,

                workflow_result["diagnosis"].score,
                workflow_result["security"].score,
                workflow_result["protocol"].score,
                workflow_result["feedback"].score,
                workflow_result["robot"].score,

                workflow_result["overall_score"],

                weighted_distance,

                execution_time

            ])