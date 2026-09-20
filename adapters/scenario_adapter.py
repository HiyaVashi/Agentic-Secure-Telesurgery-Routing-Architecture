import pandas as pd
class ScenarioAdapter:
    """
    Converts a scenario loaded from scenarios.csv into the
    input format expected by different agents.
    """

    @staticmethod
    def clean(value, default=""):
        if pd.isna(value):
            return default
        return value

    import pandas as pd

class ScenarioAdapter:

    @staticmethod
    def clean(value, default=""):
        if pd.isna(value):
            return default
        return value

    @staticmethod
    def to_patient_data(scenario):

        return {
            "patient_id": scenario["Scenario_ID"],
            "scenario_id": scenario["Scenario_ID"],
            "scenario_name": scenario["Scenario"],

            "age": ScenarioAdapter.clean(
                scenario.get("Age"), "Unknown"
            ),

            "gender": ScenarioAdapter.clean(
                scenario.get("Gender"), "Unknown"
            ),

            "medical_history": ScenarioAdapter.clean(
                scenario.get("Medical_History"), "None"
            ),

            "symptoms": ScenarioAdapter.clean(
                scenario.get("Symptoms"), "Not Provided"
            ),

            "condition": ScenarioAdapter.clean(
                scenario.get("Patient_or_Network_Condition"), ""
            )
        }

    @staticmethod
    def to_network_data(scenario):
        """
        Convert CSV row into Security Agent input.
        """

        return {
            "scenario_id": scenario["Scenario_ID"],

            "latency": scenario.get("Latency_ms", 0),
            "packet_loss": scenario.get("Packet_Loss_%", 0),
            "attack": scenario.get("Attack", "None")
        }

    @staticmethod
    def get_ground_truth(scenario):
        """
        Returns the expected outputs for evaluation.
        """

        return {
            "diagnosis": scenario.get("Ground_Truth_Diagnosis", ""),
            "security_action": scenario.get(
                "Ground_Truth_Security_Action", ""
            ),
            "protocol": scenario.get(
                "Ground_Truth_Protocol", ""
            ),
            "feedback": scenario.get(
                "Ground_Truth_Feedback", ""
            ),
            "robot_action": scenario.get(
                "Ground_Truth_Robot_Action", ""
            ),
            "confidence": scenario.get(
                "Ground_Truth_Confidence", ""
            )
        }