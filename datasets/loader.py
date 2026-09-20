# datasets/loader.py

import pandas as pd


class ScenarioLoader:
    """
    Loads and manages telesurgery evaluation scenarios
    from the scenarios.csv dataset.
    """

    def __init__(self, csv_path="datasets/scenarios.csv"):
        try:
            self.df = pd.read_csv(csv_path)
            self.df.fillna("", inplace=True)

            # Remove leading/trailing spaces from column names
            self.df.columns = self.df.columns.str.strip()

        except FileNotFoundError:
            raise FileNotFoundError(f"Scenario file not found: {csv_path}")

    def get_all_scenarios(self):
        """
        Returns all scenarios as a list of dictionaries.
        """
        return self.df.to_dict(orient="records")

    def get_scenario(self, scenario_id):
        """
        Returns a single scenario by Scenario_ID.

        Example:
            loader.get_scenario("TC01")
        """
        scenario = self.df[
            self.df["Scenario_ID"].astype(str).str.upper() == scenario_id.upper()
        ]

        if scenario.empty:
            raise ValueError(f"Scenario '{scenario_id}' not found.")

        return scenario.iloc[0].to_dict()

    def get_scenarios_by_attack(self, attack):
        """
        Returns all scenarios with the specified attack type.

        Example:
            loader.get_scenarios_by_attack("DDoS")
        """
        filtered = self.df[
            self.df["Attack"].astype(str).str.lower() == attack.lower()
        ]

        return filtered.to_dict(orient="records")

    def get_scenarios_by_difficulty(self, difficulty):
        """
        Returns all scenarios with the specified difficulty.

        Example:
            loader.get_scenarios_by_difficulty("Hard")
        """
        filtered = self.df[
            self.df["Difficulty"].astype(str).str.lower() == difficulty.lower()
        ]

        return filtered.to_dict(orient="records")

    def total_scenarios(self):
        """
        Returns the total number of scenarios.
        """
        return len(self.df)

    def scenario_exists(self, scenario_id):
        """
        Checks whether a scenario exists.
        """
        return scenario_id.upper() in self.df["Scenario_ID"].astype(str).str.upper().values