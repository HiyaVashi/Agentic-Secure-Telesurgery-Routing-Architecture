"""
dataset/runner.py
───────────────────────────────────────────────────────────────
Runs the complete telesurgery benchmark.

Pipeline
--------
CSV
 ↓
Loader
 ↓
Parser
 ↓
Workflow
 ↓
Evaluation
 ↓
Google Sheets
 ↓
Next Scenario
"""

from evaluation.evaluator import Evaluator
from utils.logger import setup_logger

from dataset.loader import DatasetLoader
from dataset.parser import DatasetParser

logger = setup_logger("dataset.runner")


class DatasetRunner:
    """
    Executes the entire benchmark dataset.
    """

    def __init__(
        self,
        workflow,
        dataset_path,
    ):

        self.workflow = workflow

        self.loader = DatasetLoader(
            dataset_path
        )

    def run(self):

        rows = self.loader.load()

        logger.info(
            "=" * 70
        )

        logger.info(
            f"Starting Dataset Benchmark "
            f"({len(rows)} scenarios)"
        )

        logger.info(
            "=" * 70
        )

        successful = 0
        failed = 0

        results = []

        for index, row in enumerate(rows, start=1):

            logger.info(
                "-" * 70
            )

            logger.info(
                f"Scenario "
                f"{index}/{len(rows)}"
            )

            logger.info(
                f"Scenario ID : "
                f"{row['Scenario_ID']}"
            )

            logger.info(
                f"{row['Scenario']}"
            )

            try:

                scenario = DatasetParser.parse(
                    row
                )

                workflow_result = self.workflow.run(

                    diagnosis=scenario[
                        "diagnosis"
                    ],

                    traffic_data=scenario[
                        "traffic_data"
                    ],

                    network_metrics=scenario[
                        "network_metrics"
                    ],

                )

                latency_metrics = self.workflow._collect_latency_metrics()

                edge_metrics = self.workflow._collect_edge_metrics()

                evaluation = Evaluator.evaluate(
                    workflow_state=workflow_result,
                    expected_output=scenario["expected_output"],
                    latency_metrics=latency_metrics,
                    edge_metrics=edge_metrics,
                    model_name=workflow_result["model"],
                )

                workflow_result[
                    "expected_output"
                ] = scenario[
                    "expected_output"
                ]

                workflow_result[
                    "scenario_id"
                ] = scenario[
                    "scenario_id"
                ]

                workflow_result[
                    "difficulty"
                ] = scenario[
                    "difficulty"
                ]

                workflow_result[
                    "notes"
                ] = scenario[
                    "notes"
                ]

                results.append(
                    workflow_result
                )

                successful += 1

                logger.info(
                    "✓ Scenario completed."
                )

            except Exception as exc:

                failed += 1

                logger.exception(
                    f"Scenario failed: {exc}"
                )

        logger.info(
            "=" * 70
        )

        logger.info(
            "DATASET BENCHMARK FINISHED"
        )

        logger.info(
            f"Successful : {successful}"
        )

        logger.info(
            f"Failed     : {failed}"
        )

        logger.info(
            "=" * 70
        )

        return results