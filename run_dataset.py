"""
run_dataset.py
───────────────────────────────────────────────────────────────
Runs the complete 40-scenario telesurgery benchmark.

Pipeline

CSV
 ↓
Dataset Loader
 ↓
Dataset Parser
 ↓
Workflow
 ↓
Evaluation
 ↓
Google Sheets
 ↓
Results

Usage

python run_dataset.py
"""

from pathlib import Path

from models.llm import get_llm

from workflows.telesurgery_workflow import TelesurgeryWorkflow

from dataset.runner import DatasetRunner

from utils.logger import setup_logger

logger = setup_logger("run_dataset")


def main():

    logger.info("=" * 80)
    logger.info("INITIALIZING DATASET BENCHMARK")
    logger.info("=" * 80)

    llm = get_llm()

    workflow = TelesurgeryWorkflow(llm)

    dataset_path = Path(
        r"D:\Research\vol 2\dataset\Implementation_Dataset.csv"
    )

    runner = DatasetRunner(

        workflow=workflow,

        dataset_path=dataset_path,

    )

    results = runner.run()

    logger.info("=" * 80)
    logger.info("BENCHMARK COMPLETE")
    logger.info(f"Total scenarios : {len(results)}")
    logger.info("=" * 80)


if __name__ == "__main__":

    main()