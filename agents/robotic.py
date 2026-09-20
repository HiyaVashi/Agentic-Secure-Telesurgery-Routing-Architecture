"""
agents/robotic.py
──────────────────
Robotic Arm Agent — Rule-Based Executor

Takes practical directives from the Feedback Agent and executes surgical tasks,
reporting whether each step is completed or paused based on stability assessments.

Unlike the other agents, the Robotic Arm Agent does NOT use an LLM. It is a
deterministic executor — a deliberate design choice that matches the paper's
description: the robotic arm receives commands and acts on them. Introducing
LLM reasoning at the execution layer would add latency that is unacceptable
in a live surgical environment.

If the arm fails or is placed on hold, the Backup Surgeon Agent is activated
by the workflow orchestrator (not by this agent directly).

Paper reference:
  • Section III-C  — Robotic Arm Agent description (implicit in workflow)
  • Section IV-B-1 — "Robotic Arm carries out surgical tasks, indicating whether
                      each step is completed or paused based on stability assessments"
  • Algorithm 2    — Steps 8–10
  • Eq. (16)       — Y(t) = argmax σ(fAI(Xp(t), Ud(t); W))
"""

import time
from datetime import datetime, timezone
from enum import Enum
from utils.logger import setup_logger


class RoboticStatus(str, Enum):
    OPERATING = "operating"
    ON_HOLD   = "on_hold"
    FAILED    = "failed"
    COMPLETED = "completed"


class RoboticArmAgent:
    """
    Robotic Arm Agent — stateful step executor.

    Maintains internal step counter and status across multiple workflow cycles,
    enabling the system to resume from the correct step after a Backup Surgeon
    takeover or network restoration.
    """

    def __init__(self) -> None:
        self.log          = setup_logger("agents.robotic")
        self.status       = RoboticStatus.OPERATING
        self.current_step = 0
        self.step_history: list[dict] = []
        self.log.info("Robotic Arm Agent initialised.")

    # ─────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────

    def run(self, feedback: dict) -> dict:
        """
        Execute the robotic arm instruction produced by the Feedback Agent.

        Args:
            feedback: Output dict from FeedbackAgent.run(). Must contain:
                - proceed_with_surgery (bool)
                - robotic_arm_command  (dict with action, speed, target_step)
                - hold_reason          (str | None)
                - safety_level         (str)

        Returns:
            Dict with: status, step_completed, step_number, step_name,
            remarks, failure (bool), execution_time_ms.
        """
        command        = feedback.get("robotic_arm_command", {})
        action         = command.get("action", "pause")
        speed          = command.get("speed", "normal")
        target_step    = command.get("target_step", f"step_{self.current_step + 1}")
        proceed        = feedback.get("proceed_with_surgery", False)
        safety_level   = feedback.get("safety_level", "safe")

        # ── Halt path: emergency stop ─────────────────────────────
        if action == "abort" or safety_level == "halt":
            self.status = RoboticStatus.FAILED
            reason      = feedback.get("hold_reason", "Emergency halt by Feedback Agent")
            self.log.error(f"ROBOTIC ARM ABORT | reason: {reason}")
            return self._record_step(
                completed=False,
                failure=True,
                remarks=reason,
            )

        # ── Hold / pause path ─────────────────────────────────────
        if not proceed or action == "pause":
            self.status = RoboticStatus.ON_HOLD
            reason      = feedback.get("hold_reason", "Operation paused by Feedback Agent")
            self.log.warning(f"Robotic arm ON HOLD | reason: {reason}")
            return self._record_step(
                completed=False,
                failure=False,
                remarks=reason,
            )

        # ── Execute path ──────────────────────────────────────────
        start_ms = time.monotonic() * 1000
        self.current_step += 1
        self.status = RoboticStatus.OPERATING

        # Simulate execution tick (removed in real hardware integration)
        time.sleep(0.01)

        elapsed_ms = (time.monotonic() * 1000) - start_ms

        self.log.info(
            f"✓ Step {self.current_step} COMPLETE | "
            f"target='{target_step}' speed={speed} "
            f"exec={elapsed_ms:.1f}ms"
        )

        return self._record_step(
            completed=True,
            failure=False,
            remarks=f"Step {self.current_step} '{target_step}' completed successfully.",
            step_name=target_step,
            execution_time_ms=round(elapsed_ms, 2),
        )

    def reset(self) -> None:
        """Reset arm state between surgical procedures."""
        self.current_step = 0
        self.status       = RoboticStatus.OPERATING
        self.step_history  = []
        self.log.info("Robotic Arm state reset.")

    def needs_backup(self) -> bool:
        """Return True if the backup surgeon should be activated."""
        return self.status in (RoboticStatus.ON_HOLD, RoboticStatus.FAILED)

    # ─────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────

    def _record_step(
        self,
        completed:         bool,
        failure:           bool,
        remarks:           str,
        step_name:         str  = "",
        execution_time_ms: float = 0.0,
    ) -> dict:
        record = {
            "status":             self.status.value,
            "step_completed":     completed,
            "step_number":        self.current_step,
            "step_name":          step_name or f"step_{self.current_step}",
            "remarks":            remarks,
            "failure":            failure,
            "execution_time_ms":  execution_time_ms,
            "timestamp":          datetime.now(timezone.utc).isoformat(),
        }
        self.step_history.append(record)
        return record
