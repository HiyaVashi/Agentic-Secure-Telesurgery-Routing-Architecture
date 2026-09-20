"""
agents/backup.py
─────────────────
Backup Surgeon Agent (Ab) — LangChain LCEL Implementation

Seamlessly assumes control of the telesurgical procedure when the primary robotic
arm fails or is placed on hold. Maintains continuity in the telesurgical procedure
by generating a precise recovery plan from the exact point of failure.

The Backup Surgeon Agent represents the γB(t) term in the combined control response:
  R(t) = αS(t) + βP(t) + γB(t)    [Eq. 3]

It is activated only when the Robotic Arm Agent reports failure or on_hold status,
as determined by the workflow orchestrator in Algorithm 2 (Steps 11–12).

Paper reference:
  • Section III-C  — Backup Surgeon Agent (Ab) description
  • Section IV-B-1 — "If there is a failure in the robotic execution, the Backup
                      Surgeon Agent is triggered automatically to maintain continuity"
  • Eq. (3)        — R(t) = αS(t) + βP(t) + γB(t)
  • Algorithm 2    — Steps 11–12
"""

import json
from utils.base_agent import BaseAgent
from config import settings
from utils.logger import setup_logger


class BackupSurgeonAgent(BaseAgent):
    """
    Backup Surgeon Agent — failover recovery planner.

    Activated by the workflow when the primary robotic arm fails or is on hold.
    Uses LLM reasoning to generate a safe, specific recovery plan tailored to
    the exact failure point and remaining surgical steps.

    LCEL chain:  ChatPromptTemplate → LLM → JsonOutputParser
    """

    def __init__(self, llm):

        super().__init__(
            model=llm,
            prompt_path=settings.PROMPTS_DIR / "backup.txt"
        )

        self.log = setup_logger("agents.backup")

        self.active = False
        self.activation_count = 0

        self.log.info(
            "Backup Surgeon Agent initialized (standby)."
        )

    # ─────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────

    def run(self, arm_result: dict, surgery_plan: dict) -> dict:
        """
        Generate a failover recovery plan when the primary robotic arm fails.

        Args:
            arm_result:   Output dict from RoboticArmAgent.run() — must contain
                          status, step_number, remarks, failure.
            surgery_plan: Output dict from DoctorAgent.run() — the original plan
                          being executed at the time of failure.

        Returns:
            JSON dict with: backup_activated, takeover_step, recovery_action,
            patient_safety_status, safety_assessment, estimated_recovery_seconds,
            continue_surgery, abort_reason, backup_protocol, steps_remaining, message.
        """
        self.active = True
        self.activation_count += 1

        failure_step   = arm_result.get("step_number", 0)
        failure_reason = arm_result.get("remarks", "Unknown robotic arm failure")
        arm_status_str = json.dumps(arm_result, indent=2)
        surgery_plan_str = json.dumps(surgery_plan, indent=2)

        self.log.warning(
            f"⚡ BACKUP SURGEON ACTIVATED (activation #{self.activation_count}) | "
            f"failed at step {failure_step} | "
            f"reason: {failure_reason}"
        )

        result = self.invoke({
            "failure_step":   str(failure_step),
            "failure_reason": failure_reason,
            "arm_status":     arm_status_str,
            "surgery_plan":   surgery_plan_str,
        })

        # Ensure backup_activated is always True (override if LLM forgets)
        result["backup_activated"]    = True
        result["activation_number"]   = self.activation_count

        self.log.info(
            f"Backup plan issued | "
            f"continue={result.get('continue_surgery')} "
            f"patient_safety={result.get('patient_safety_status')} "
            f"takeover_step={result.get('takeover_step')} "
            f"recovery_action={result.get('recovery_action')}"
        )

        if not result.get("continue_surgery"):
            self.log.error(
                f"Backup Surgeon recommends ABORT | "
                f"reason: {result.get('abort_reason')}"
            )

        return result

    def deactivate(self) -> None:
        """Deactivate backup surgeon when primary system is restored."""
        self.active = False
        self.log.info("Backup Surgeon Agent deactivated — primary system restored.")
