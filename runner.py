<<<<<<< HEAD
from datasets.loader import ScenarioLoader
from adapters.scenario_adapter import ScenarioAdapter

from workflows.telesurgery_workflow import TelesurgeryWorkflow
from datetime import datetime

from evaluation.workflow_evaluator import WorkflowEvaluator
from evaluation.weighted_score import WeightedScore
from evaluation.google_logger import GoogleSheetsLogger


class WorkflowRunner:

    def __init__(self):

        self.loader = ScenarioLoader()
        self.workflow = TelesurgeryWorkflow()

        self.evaluator = WorkflowEvaluator()
        self.score = WeightedScore()

        self.google_logger = GoogleSheetsLogger()

    ############################################################
    # Run Single Scenario
    ############################################################

    def run(self, scenario_id):

        # -----------------------------
        # Load Scenario
        # -----------------------------

        scenario = self.loader.get_scenario(scenario_id)

        if scenario is None:
            raise ValueError(f"Scenario '{scenario_id}' not found.")

        run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S")

        # -----------------------------
        # Convert CSV Row
        # -----------------------------

        patient = ScenarioAdapter.to_patient_data(scenario)
        network = ScenarioAdapter.to_network_data(scenario)

        # -----------------------------
        # Execute Workflow
        # -----------------------------

        workflow_result = self.workflow.run(
            patient=patient,
            traffic=network
        )

        # -----------------------------
        # Evaluate Workflow
        # -----------------------------

        evaluation = self.evaluator.evaluate(
            workflow_result,
            scenario
        )

        # -----------------------------
        # Calculate Weighted Score
        # -----------------------------

        weighted_score = self.score.calculate(evaluation)

        execution_time = workflow_result.get("execution_time", 0)

        # -----------------------------
        # Log Results
        # -----------------------------

        self.google_logger.log_summary(
            run_id,
            scenario,
            evaluation,
            weighted_score,
            execution_time
        )

        self.google_logger.log_diagnosis(
            run_id,
            scenario,
            evaluation["diagnosis"]
        )

        self.google_logger.log_security(
            run_id,
            scenario,
            evaluation["security"]
        )

        self.google_logger.log_protocol(
            run_id,
            scenario,
            evaluation["protocol"]
        )

        self.google_logger.log_feedback(
            run_id,
            scenario,
            evaluation["feedback"]
        )

        self.google_logger.log_robot(
            run_id,
            scenario,
            evaluation["robot"]
        )

        self.google_logger.log_workflow(
            run_id,
            scenario,
            workflow_result
        )

        return {
            "scenario": scenario,
            "workflow": workflow_result,
            "evaluation": evaluation,
            "weighted_score": weighted_score
        }

    ############################################################
    # Run All Scenarios
    ############################################################

    def run_all(self):

        scenarios = self.loader.get_all_scenarios()

        print(f"Found {len(scenarios)} scenarios.")

        for scenario in scenarios:

            print(f"Running {scenario['Scenario_ID']}...")

            try:
                self.run(scenario["Scenario_ID"])

            except Exception as e:
                print(f"Failed {scenario['Scenario_ID']}: {e}")

        print("Updating statistics...")

        self.google_logger.update_statistics()

        print("All scenarios completed.")


############################################################
# Main
############################################################

if __name__ == "__main__":

    runner = WorkflowRunner()

    # Run every scenario in scenarios.csv
=======
from datasets.loader import ScenarioLoader
from adapters.scenario_adapter import ScenarioAdapter

from workflows.telesurgery_workflow import TelesurgeryWorkflow
from datetime import datetime

from evaluation.workflow_evaluator import WorkflowEvaluator
from evaluation.weighted_score import WeightedScore
from evaluation.google_logger import GoogleSheetsLogger


class WorkflowRunner:

    def __init__(self):

        self.loader = ScenarioLoader()
        self.workflow = TelesurgeryWorkflow()

        self.evaluator = WorkflowEvaluator()
        self.score = WeightedScore()

        self.google_logger = GoogleSheetsLogger()

    ############################################################
    # Run Single Scenario
    ############################################################

    def run(self, scenario_id):

        # -----------------------------
        # Load Scenario
        # -----------------------------

        scenario = self.loader.get_scenario(scenario_id)

        if scenario is None:
            raise ValueError(f"Scenario '{scenario_id}' not found.")

        run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S")

        # -----------------------------
        # Convert CSV Row
        # -----------------------------

        patient = ScenarioAdapter.to_patient_data(scenario)
        network = ScenarioAdapter.to_network_data(scenario)

        # -----------------------------
        # Execute Workflow
        # -----------------------------

        workflow_result = self.workflow.run(
            patient=patient,
            traffic=network
        )

        # -----------------------------
        # Evaluate Workflow
        # -----------------------------

        evaluation = self.evaluator.evaluate(
            workflow_result,
            scenario
        )

        # -----------------------------
        # Calculate Weighted Score
        # -----------------------------

        weighted_score = self.score.calculate(evaluation)

        execution_time = workflow_result.get("execution_time", 0)

        # -----------------------------
        # Log Results
        # -----------------------------

        self.google_logger.log_summary(
            run_id,
            scenario,
            evaluation,
            weighted_score,
            execution_time
        )

        self.google_logger.log_diagnosis(
            run_id,
            scenario,
            evaluation["diagnosis"]
        )

        self.google_logger.log_security(
            run_id,
            scenario,
            evaluation["security"]
        )

        self.google_logger.log_protocol(
            run_id,
            scenario,
            evaluation["protocol"]
        )

        self.google_logger.log_feedback(
            run_id,
            scenario,
            evaluation["feedback"]
        )

        self.google_logger.log_robot(
            run_id,
            scenario,
            evaluation["robot"]
        )

        self.google_logger.log_workflow(
            run_id,
            scenario,
            workflow_result
        )

        return {
            "scenario": scenario,
            "workflow": workflow_result,
            "evaluation": evaluation,
            "weighted_score": weighted_score
        }

    ############################################################
    # Run All Scenarios
    ############################################################

    def run_all(self):

        scenarios = self.loader.get_all_scenarios()

        print(f"Found {len(scenarios)} scenarios.")

        for scenario in scenarios:

            print(f"Running {scenario['Scenario_ID']}...")

            try:
                self.run(scenario["Scenario_ID"])

            except Exception as e:
                print(f"Failed {scenario['Scenario_ID']}: {e}")

        print("Updating statistics...")

        self.google_logger.update_statistics()

        print("All scenarios completed.")


############################################################
# Main
############################################################

if __name__ == "__main__":

    runner = WorkflowRunner()

    # Run every scenario in scenarios.csv
>>>>>>> a622173226c4d140cf54d90651d3ec0bdfa4d2dc
    runner.run_all()