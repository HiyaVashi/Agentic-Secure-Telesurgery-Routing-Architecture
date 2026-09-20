"""
agents/feedback.py
───────────────────
Feedback Agent (Af) — LangChain LCEL Implementation

Aggregates outputs from the Doctor Agent, Security Agent, and Protocol Switcher
and produces a single, final instruction for the Robotic Arm Agent.

Implements the weighted aggregation from the paper:
  O(t)  = W · [Ad(t), As(t), Ap(t), Af(t), Ab(t)]^T     [Eq. 11]
  Y(t)  = argmax σ(O(t))                                   [Eq. 12]

Provides corrective and adaptive feedback to robotic actuators to maintain
precision, safety, and reliability of ongoing surgical tasks.

Paper reference:
  • Section III-C  — Feedback Agent (Af) description
  • Section III-D  — Secure Adaptive Control Layer, Eq. (13)
  • Eq. (3)        — R(t) = αS(t) + βP(t) + γB(t)
  • Eq. (11)(12)   — Weighted aggregation + softmax decision
  • Algorithm 2    — Steps 6–7: Feedback Agent aggregates outputs
"""

import json
from utils.base_agent import BaseAgent
from config import settings
from utils.logger import setup_logger

class FeedbackAgent(BaseAgent):
    """
    Feedback Agent — synthesises all agent outputs into one robotic arm command.

    The agent respects the α (doctor), β (security), γ (protocol) weighting
    coefficients from config.py so that surgical safety and threat response
    are always appropriately prioritised.

    LCEL chain:  ChatPromptTemplate → LLM → JsonOutputParser
    """

    def __init__(self, llm):

        super().__init__(
            model=llm,
            prompt_path=settings.PROMPTS_DIR / "feedback.txt"
        )

        self.log = setup_logger("agents.feedback")

        self.weights_str = json.dumps(
            {
                "doctor_agent": settings.WEIGHT_DOCTOR,
                "security_agent": settings.WEIGHT_SECURITY,
                "protocol_switcher": settings.WEIGHT_PROTOCOL,
                "feedback_bias": settings.WEIGHT_FEEDBACK,
            },
            indent=2,
        )

        self.log.info("Feedback Agent initialized.")

    # ─────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────

    def run(
        self,
        surgery_plan:    dict,
        security_report: dict,
        protocol_status: dict,
    ) -> dict:
        """
        Aggregate all agent outputs and produce the final robotic arm instruction.

        Args:
            surgery_plan:    Output from DoctorAgent.run()
            security_report: Output from SecurityAgent.run()
            protocol_status: Output from ProtocolSwitcherAgent.run()

        Returns:
            JSON dict with: final_instruction, proceed_with_surgery,
            hold_reason, safety_level, corrective_actions,
            robotic_arm_command, feedback_summary, anomaly_score,
            agent_weights_applied.
        """
        self.log.info(
            f"Aggregating inputs | "
            f"attack={security_report.get('attack_detected')} "
            f"protocol={protocol_status.get('recommended_protocol', protocol_status.get('current_protocol'))} "
            f"surgery_type={surgery_plan.get('surgery_type')}"
        )

        result= self.invoke({
            "surgery_plan":    json.dumps(surgery_plan, indent=2),
            "security_report": json.dumps(security_report, indent=2),
            "protocol_status": json.dumps(protocol_status, indent=2),
            "weights":         self.weights_str,
            "weight_doctor":   str(settings.WEIGHT_DOCTOR),
            "weight_security": str(settings.WEIGHT_SECURITY),
            "weight_protocol": str(settings.WEIGHT_PROTOCOL),
        })

        # ── Safety guard: if attack is critical, force halt ───────
        if (security_report.get("attack_detected")
                and security_report.get("severity") == "critical"):
            if result.get("safety_level") != "halt":
                self.log.warning(
                    "Critical attack severity — overriding safety_level to 'halt'"
                )
                result["safety_level"]        = "halt"
                result["proceed_with_surgery"] = False
                result["hold_reason"] = (
                    result.get("hold_reason")
                    or "Critical DDoS attack: surgery halted for patient safety"
                )
                result["robotic_arm_command"] = {
                    "action": "pause",
                    "speed":  "emergency_stop",
                    "target_step": "halt_pending_network_restoration",
                }

        action = result.get("robotic_arm_command", {}).get("action", "unknown")
        self.log.info(
            f"Feedback decision | "
            f"action={action} "
            f"safety={result.get('safety_level')} "
            f"proceed={result.get('proceed_with_surgery')} "
            f"anomaly_score={result.get('anomaly_score', 'N/A')}"
        )
        return result
