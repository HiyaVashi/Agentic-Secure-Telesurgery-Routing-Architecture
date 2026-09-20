"""
evaluation/robustness.py
────────────────────────

Evaluates Operational Robustness of the telesurgery workflow.

Measures the system's ability to continue operating correctly
despite failures and adverse conditions.
"""

from evaluation.base_result import EvaluationResult


class OperationalRobustness:

    @classmethod
    def calculate(cls, workflow_state: dict) -> EvaluationResult:
        """
        Calculate Operational Robustness.

        Parameters
        ----------
        workflow_state : dict
            Final telesurgery workflow state.

        Returns
        -------
        EvaluationResult
        """

        score = 0
        total = 5

        details = {}

        # -----------------------------------------
        # 1. Workflow Completion
        # -----------------------------------------

        completed = workflow_state.get("completed", False)

        if completed:
            score += 1

        details["workflow_completed"] = completed

        # -----------------------------------------
        # 2. Doctor Agent
        # -----------------------------------------

        doctor_ok = (
            workflow_state.get("surgery_plan", {})
            .get("status") != "failed"
        )

        if doctor_ok:
            score += 1

        details["doctor_success"] = doctor_ok

        # -----------------------------------------
        # 3. Security Agent
        # -----------------------------------------

        security_ok = (
            workflow_state.get("security_report", {})
            .get("status") != "failed"
        )

        if security_ok:
            score += 1

        details["security_success"] = security_ok

        # -----------------------------------------
        # 4. Protocol Switcher
        # -----------------------------------------

        protocol_ok = (
            workflow_state.get("protocol_status", {})
            .get("status") != "failed"
        )

        if protocol_ok:
            score += 1

        details["protocol_success"] = protocol_ok

        # -----------------------------------------
        # 5. Recovery Logic
        # -----------------------------------------

        arm = workflow_state.get("arm_result", {})

        backup = workflow_state.get("backup_result")

        arm_failed = (

            arm.get("failure") is True

            or

            arm.get("status") == "failed"

        )

        if arm_failed:

            recovered = backup is not None

        else:

            recovered = True

        if recovered:
            score += 1

        details["backup_recovery"] = recovered

        # -----------------------------------------

        normalized = score / total

        return EvaluationResult(

            criterion="Operational Robustness",

            normalized=round(normalized, 4),

            raw_score=score,

            details=details,

        )
    