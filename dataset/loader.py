"""
dataset/loader.py
───────────────────────────────────────────────────────────────
Loads the implementation dataset used for benchmarking the
Agentic AI Telesurgery workflow.

Responsibilities
----------------
• Read the CSV dataset.
• Validate the file exists.
• Return all rows as dictionaries.

This module intentionally performs NO parsing or preprocessing.
That responsibility belongs to parser.py.
"""

from pathlib import Path
from typing import List, Dict

import pandas as pd


class DatasetLoader:
    """
    Loads the telesurgery implementation dataset.
    """

    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)

    def load(self) -> List[Dict]:
        """
        Load the dataset.

        Returns
        -------
        List[Dict]
            One dictionary per scenario.
        """

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found:\n{self.dataset_path}"
            )

        dataframe = pd.read_csv(self.dataset_path)

        if dataframe.empty:
            raise ValueError(
                "Dataset is empty."
            )

        records = dataframe.to_dict(
            orient="records"
        )

        return records

    def size(self) -> int:
        """
        Return number of scenarios.
        """

        dataframe = pd.read_csv(
            self.dataset_path
        )

        return len(dataframe)
    