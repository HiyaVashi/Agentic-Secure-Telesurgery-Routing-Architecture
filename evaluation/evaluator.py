"""
evaluation/evaluator.py
───────────────────────

Central evaluation engine.

Collects the outputs produced by the telesurgery workflow,
evaluates every criterion and computes the final weighted score.
"""

from evaluation.edge import EdgeEfficiency
from evaluation.hallucination import ClinicalHallucination
from evaluation.latency import LatencyEvaluator
from evaluation.overall_score import OverallScore
from evaluation.security_accuracy import SecurityAccuracy
from evaluation.workflow_accuracy import WorkflowAccuracy


class Evaluator:
    """
    Central evaluation orchestrator.
    """

    @classmethod
    def evaluate(
        cls,
        *,
        workflow_state: dict,
        expected_output: dict,
        latency_metrics: dict,
        edge_metrics: dict,
        model_name: str,
    ) -> dict:
        """
        Evaluate an entire telesurgery workflow.

        Parameters
        ----------
        workflow_state : dict
            Final workflow state.

        expected_output : dict
            Ground truth values.

        latency_metrics : dict
            Measured latency values.

        edge_metrics : dict
            CPU, RAM and Tokens/sec.

        model_name : str
            Name of the model being evaluated.

        Returns
        -------
        dict
            Complete evaluation report.
        """

        # ---------------------------------------------------------
        # Latency
        # ---------------------------------------------------------

        latency = LatencyEvaluator.calculate(
            latency_metrics
        )

        # ---------------------------------------------------------
        # Edge Deployment Efficiency
        # ---------------------------------------------------------

        edge = EdgeEfficiency.calculate(
            edge_metrics,
            model_name
        )

        # ---------------------------------------------------------
        # Workflow Accuracy
        # ---------------------------------------------------------

        workflow = WorkflowAccuracy.calculate(

            expected_output,

            workflow_state

        )

        # ---------------------------------------------------------
        # Security Accuracy
        # ---------------------------------------------------------

        security = SecurityAccuracy.calculate(

            expected_output,

            workflow_state

        )

        # ---------------------------------------------------------
        # Clinical Hallucination
        # ---------------------------------------------------------

        hallucination = ClinicalHallucination.calculate(

            expected_output,

            workflow_state

        )

        # ---------------------------------------------------------
        # Overall Score
        # ---------------------------------------------------------

        overall = OverallScore.calculate(

            {

                "response_latency":
                    latency.normalized,

                "edge_efficiency":
                    edge.normalized,

                "operational_robustness":
                    1.0,          # Placeholder until robustness.py

                "workflow_accuracy":
                    workflow.normalized,

                "clinical_hallucination":
                    hallucination.normalized,

                "security_accuracy":
                    security.normalized,

            }

        )

        return {

            "latency": latency,

            "edge_efficiency": edge,

            "workflow_accuracy": workflow,

            "security_accuracy": security,

            "clinical_hallucination": hallucination,

            "operational_robustness": None,

            "overall_score": overall,

        }
    