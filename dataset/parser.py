"""
dataset/parser.py
──────────────────────────────────────────────────────────────
Converts one dataset row into the inputs required by the
Agentic AI Telesurgery workflow.

Responsibilities
----------------
• Build diagnosis dictionary.
• Build traffic data.
• Build network metrics.
• Build expected output (ground truth).

This module does NOT execute the workflow.
"""

from typing import Dict, Any
import pandas as pd


class DatasetParser:
    """
    Converts one CSV row into workflow inputs.
    """

    @staticmethod
    def _clean(value, default="Unknown"):
        """
        Replace NaN/None with a default value.
        """

        if pd.isna(value):
            return default

        return value

    @classmethod
    def parse(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse one dataset row.

        Returns
        -------
        {
            diagnosis,
            traffic_data,
            network_metrics,
            expected_output
        }
        """

        diagnosis = {

            "patient_id":
                cls._clean(row["Scenario_ID"]),

            "scenario":
                cls._clean(row["Scenario"]),

            "condition":
                cls._clean(
                    row["Patient_or_Network_Condition"]
                ),

            "age":
                cls._clean(row["Age"]),

            "gender":
                cls._clean(row["Gender"]),

            "medical_history":
                cls._clean(
                    row["Medical_History"]
                ),

            "symptoms":
                cls._clean(
                    row["Symptoms"]
                ),
        }

        traffic_data = [

            {

                "packet_id": 1,

                "attack":
                    cls._clean(
                        row["Attack"],
                        default="None"
                    ),

                "source_ip":
                    "192.168.1.10",

                "destination_ip":
                    "192.168.1.20",

                "protocol":
                    "TCP",

            }

        ]

        network_metrics = {

            "latency_ms":

                float(
                    cls._clean(
                        row["Latency_ms"],
                        default=0
                    )
                ),

            "packet_loss_pct":

                float(
                    cls._clean(
                        row["Packet_Loss_%"],
                        default=0
                    )
                ),

            "jitter_ms": 5.0,

        }

        expected_output = {

            "diagnosis":

                cls._clean(
                    row["Ground_Truth_Diagnosis"]
                ),

            "security_action":

                cls._clean(
                    row["Ground_Truth_Security_Action"]
                ),

            "protocol":

                cls._clean(
                    row["Ground_Truth_Protocol"]
                ),

            "feedback":

                cls._clean(
                    row["Ground_Truth_Feedback"]
                ),

            "robot_action":

                cls._clean(
                    row["Ground_Truth_Robot_Action"]
                ),

            "confidence":
                    cls._clean(
                        row["Ground_Truth_Confidence"],
                        default=0
                    ),
        }

        return {

            "scenario_id":
                cls._clean(
                    row["Scenario_ID"]
                ),

            "difficulty":
                cls._clean(
                    row["Difficulty"]
                ),

            "requires_reasoning":
                cls._clean(
                    row["Requires_Reasoning"]
                ),

            "notes":
                cls._clean(
                    row["Notes"],
                    default=""
                ),

            "diagnosis":
                diagnosis,

            "traffic_data":
                traffic_data,

            "network_metrics":
                network_metrics,

            "expected_output":
                expected_output,

        }