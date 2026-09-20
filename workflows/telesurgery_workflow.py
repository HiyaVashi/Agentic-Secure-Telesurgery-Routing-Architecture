"""
workflows/telesurgery_workflow.py
──────────────────────────────────
Main Telesurgery Workflow — LangGraph StateGraph Implementation

Orchestrates all six agents in the exact sequence described in Algorithm 2
of the paper, using LangGraph's StateGraph for controlled, stateful execution.

Graph topology (mirrors N8N canvas, Fig. 4):

  [START]
     │
     ▼
  ┌──────────────┐
  │ doctor_node  │  ── Generates surgery plan
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ security_nod │  ── Inspects traffic for DDoS
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ protocol_node│  ── Selects/switches TCP/UDP/QUIC
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ feedback_node│  ── Aggregates all outputs
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ robotic_node │  ── Executes surgical instruction
  └──────┬───────┘
         │
    ┌────┴────────────────────┐
    │ needs backup?           │
    ▼ YES                     ▼ NO
  ┌──────────────┐          [END]
  │ backup_node  │
  └──────┬───────┘
         ▼
       [END]

Paper reference:
  • Fig. 4    — N8N Workflow (this file reproduces it in LangGraph)
  • Algorithm 2 — Agentic AI Telesurgery Workflow (all steps)
  • Eq. (11)(12) — Weighted aggregation + softmax final action
  • Eq. (16)  — Y(t) = argmax σ(fAI(Xp(t), Ud(t); W))
"""

import json
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from agents.backup   import BackupSurgeonAgent
from agents.doctor   import DoctorAgent
from agents.feedback import FeedbackAgent
from agents.protocol import ProtocolSwitcherAgent
from agents.robotic  import RoboticArmAgent, RoboticStatus
from agents.security import SecurityAgent
from config import settings
from evaluation.evaluator import Evaluator
from utils.logger import setup_logger
from utils.google_sheets import sheet_logger

logger = setup_logger("workflows.telesurgery")


# ─────────────────────────────────────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────────────────────────────────────

class TelesurgeryState(TypedDict, total=False):
    """
    Shared state passed through every node in the LangGraph.
    Populated progressively as each agent completes its work.
    """

    # ── Inputs (set before graph execution starts) ────────────────
    run_id:          str           # UUID for this workflow run
    timestamp:       str           # ISO-8601 start time
    model:           str           # LLM model name (e.g., "gpt-4")
    diagnosis:       dict          # Patient diagnosis data
    traffic_data:    list          # Network traffic records
    network_metrics: dict          # Latency, jitter, packet loss, etc.

    # ── Agent outputs (populated by each node) ────────────────────
    surgery_plan:    Optional[dict]   # DoctorAgent output
    security_report: Optional[dict]   # SecurityAgent output
    protocol_status: Optional[dict]   # ProtocolSwitcherAgent output
    feedback:        Optional[dict]   # FeedbackAgent output
    arm_result:      Optional[dict]   # RoboticArmAgent output
    backup_result:   Optional[dict]   # BackupSurgeonAgent output

    # ── Metadata ──────────────────────────────────────────────────
    errors:    list   # Accumulated non-fatal errors
    completed: bool   # True when workflow finishes without abort


# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW CLASS
# ─────────────────────────────────────────────────────────────────────────────

class TelesurgeryWorkflow:
    """
    LangGraph-based telesurgery workflow.

    Wraps all six agents and compiles them into a directed state graph.
    Each node is a thin wrapper that calls the corresponding agent and
    writes results back into the shared state.

    Usage:
        workflow = TelesurgeryWorkflow(llm)
        result   = workflow.run(diagnosis, traffic_data, network_metrics)
    """

    def __init__(self, llm) -> None:
        # ── Instantiate all agents ────────────────────────────────
        self.doctor_agent   = DoctorAgent(llm)
        self.security_agent = SecurityAgent(llm)
        self.protocol_agent = ProtocolSwitcherAgent(llm)
        self.feedback_agent = FeedbackAgent(llm)
        self.robotic_agent  = RoboticArmAgent()
        self.backup_agent   = BackupSurgeonAgent(llm)
        from network.key_manager import KeyManager
        from network.relay_manager import RelayManager
        from network.relay import Relay
        from network.secure_channel import SecureChannel

        # -------------------------------------------------
        # Secure Communication Layer
        # -------------------------------------------------

        self.key_manager = KeyManager()

        self.key_manager.register("Doctor")
        self.key_manager.register("Feedback")
        self.key_manager.register("Security")
        self.key_manager.register("Protocol")
        self.key_manager.register("Robotic")
        self.key_manager.register("Backup")

        self.relay_manager = RelayManager()

        self.relay_manager.add_relay(
            Relay("Relay-1", trust_score=0.91)
        )

        self.relay_manager.add_relay(
            Relay("Relay-2", trust_score=0.98)
        )

        self.relay_manager.add_relay(
            Relay("Relay-3", trust_score=0.87)
        )

        self.relay_manager.add_relay(
            Relay("Relay-4", trust_score=0.95)
        )

        self.relay_manager.add_relay(
            Relay("Relay-5", trust_score=0.93)
        )

        self.secure_channel = SecureChannel(

            self.key_manager,

            self.relay_manager,

        )

        # ── Compile the graph ─────────────────────────────────────
        self.graph = self._build_graph()
        logger.info("Telesurgery workflow compiled and ready.")

    # ─────────────────────────────────────────────────────────────
    # Public run method
    # ─────────────────────────────────────────────────────────────

    def run(
        self,
        diagnosis:       dict,
        traffic_data:    list,
        network_metrics: dict,
    ) -> dict:
        """
        Execute the full telesurgery workflow.

        Args:
            diagnosis:       Patient diagnosis dict (from data/diagnosis.json)
            traffic_data:    List of network packet dicts (from data/traffic.json)
            network_metrics: Dict with latency_ms, jitter_ms, packet_loss_pct

        Returns:
            Final TelesurgeryState dict with all agent outputs populated.
        """
        run_id = str(uuid.uuid4())[:8].upper()

    
        print(">>> ENTERED RUN() <<<")

        start = time.perf_counter()

        print(">>> PERF COUNTER OK <<<")

        logger.info(f"{'═'*60}")
        logger.info(f"  TELESURGERY WORKFLOW START  [run_id={run_id}]")
        logger.info(f"{'═'*60}")

        # Seed the initial state
        initial_state: TelesurgeryState = {
            "run_id":          run_id,
            "timestamp":       datetime.now(timezone.utc).isoformat(),
            "model":           settings.OLLAMA_MODEL,
            "diagnosis":       diagnosis,
            "traffic_data":    traffic_data,
            "network_metrics": network_metrics,
            "surgery_plan":    None,
            "security_report": None,
            "protocol_status": None,
            "feedback":        None,
            "arm_result":      None,
            "backup_result":   None,
            "errors":          [],
            "completed":       False,
        }

        # Execute the graph
        final_state: dict = self.graph.invoke(initial_state)

        execution_time = (
                    time.perf_counter()
                    - start
                )

        try:

            evaluation = self._evaluate_workflow(
                workflow_state=final_state,
            )

            print("\n===== EVALUATION =====")
            print(evaluation)
            print(type(evaluation))

            self._log_evaluation(
                final_state,
                evaluation,
            )

            self._log_summary(
                state=final_state,
                overall_score=evaluation["overall_score"],
                execution_time=execution_time,
            )

        except Exception as exc:

            logger.exception(
                f"Evaluation failed: {exc}"
            )
        
        logger.info(f"{'═'*60}")
        logger.info(f"  TELESURGERY WORKFLOW COMPLETE  [run_id={run_id}]")
        logger.info(f"{'═'*60}")

        # Persist results
        self._save_results(run_id, final_state)

        return final_state

    # ─────────────────────────────────────────────────────────────
    # Graph construction
    # ─────────────────────────────────────────────────────────────

    def _build_graph(self) -> "CompiledGraph":  # noqa: F821
        """
        Build and compile the LangGraph StateGraph.

        Nodes:
          doctor_node   → security_node → protocol_node → feedback_node
          → robotic_node → [conditional] → backup_node | END

        Returns:
            Compiled LangGraph runnable.
        """
        graph = StateGraph(TelesurgeryState)

        # ── Register nodes ────────────────────────────────────────
        graph.add_node("doctor_node",   self._doctor_node)
        graph.add_node("security_node", self._security_node)
        graph.add_node("protocol_node", self._protocol_node)
        graph.add_node("feedback_node", self._feedback_node)
        graph.add_node("robotic_node",  self._robotic_node)
        graph.add_node("backup_node",   self._backup_node)

        # ── Sequential edges (Algorithm 2, Steps 1–8) ─────────────
        graph.set_entry_point("doctor_node")
        graph.add_edge("doctor_node",   "security_node")
        graph.add_edge("security_node", "protocol_node")
        graph.add_edge("protocol_node", "feedback_node")
        graph.add_edge("feedback_node", "robotic_node")

        # ── Conditional edge: backup surgeon or end ───────────────
        graph.add_conditional_edges(
            "robotic_node",
            self._needs_backup_router,
            {
                "backup_node": "backup_node",
                END:            END,
            },
        )
        graph.add_edge("backup_node", END)

        return graph.compile()

    # ─────────────────────────────────────────────────────────────
    # Node functions  (each takes state → returns state updates)
    # ─────────────────────────────────────────────────────────────

    def _doctor_node(self, state: TelesurgeryState) -> dict:
        """
        Node 1 — Doctor Agent
        """

        logger.info("[Node 1/6] Doctor Agent processing...")
        start_time = time.perf_counter()

        try:

            # -------------------------------------------------
            # Generate surgery plan
            # -------------------------------------------------
            plan = self.doctor_agent.run(state["diagnosis"])

            logger.info("Doctor Agent output generated successfully.")
            logger.info(f"Plan Keys: {list(plan.keys())}")

            # -------------------------------------------------
            # Secure transmission
            # -------------------------------------------------
            garlic = self.secure_channel.send(
                sender="Doctor",
                receiver="Security",
                workflow_id=state["run_id"],
                message=plan,
            )

            logger.info("Doctor -> Security garlic message created.")

            plan = self.secure_channel.receive(
                garlic,
                receiver="Security",
            )

            logger.info("Doctor -> Security transmission successful.")
            logger.info(f"Received Plan Keys: {list(plan.keys())}")

            # -------------------------------------------------
            # Logging
            # -------------------------------------------------
            duration = time.perf_counter() - start_time

            self._log_doctor(
                state=state,
                plan=plan,
                status="Success",
            )

            logger.info("Doctor worksheet logged successfully.")

            self._log_workflow(
                state=state,
                stage="Doctor",
                event="Completed",
                result="Success",
                duration=duration,
            )

            logger.info("Doctor workflow log completed.")

            return {
                "surgery_plan": plan
            }

        except Exception as exc:

            logger.exception("Doctor Node failed")

            duration = time.perf_counter() - start_time

            try:
                self._log_doctor(
                    state=state,
                    plan={},
                    status="Failed",
                    remarks=str(exc),
                )
            except Exception:
                logger.exception("Failed to log Doctor worksheet.")

            try:
                self._log_workflow(
                    state=state,
                    stage="Doctor",
                    event="Completed",
                    result="Failed",
                    duration=duration,
                )
            except Exception:
                logger.exception("Failed to log workflow.")

            return {
                "surgery_plan": {
                    "error": str(exc),
                    "status": "failed",
                },
                "errors": state.get("errors", []) + [
                    f"DoctorAgent: {exc}"
                ],
            }

    def _security_node(self, state: TelesurgeryState) -> dict:
        """
        Node 2 — Security Agent
        """

        logger.info("[Node 2/6] Security Agent inspecting traffic...")
        start_time = time.perf_counter()

        try:

            report = self.security_agent.run(
                state["traffic_data"]
            )

            # Securely transmit Security -> Protocol
            garlic = self.secure_channel.send(
                sender="Security",
                receiver="Protocol",
                workflow_id=state["run_id"],
                message=report,
            )

            report = self.secure_channel.receive(
                garlic,
                receiver="Protocol",
            )

            logger.info("Security -> Protocol transmission successful.")

            duration = time.perf_counter() - start_time

            self._log_security(
                state=state,
                report=report,
                status="Success",
            )

            self._log_workflow(
                state=state,
                stage="Security",
                event="Completed",
                result="Success",
                duration=duration,
            )

            return {
                "security_report": report
            }

        except Exception as exc:

            logger.error(
                f"Security Agent error: {exc}"
            )

            duration = time.perf_counter() - start_time

            self._log_security(
                state=state,
                report={},
                status="Failed",
            )

            self._log_workflow(
                state=state,
                stage="Security",
                event="Completed",
                result="Failed",
                duration=duration,
            )

            return {

                "security_report": {

                    "attack_detected": False,

                    "error": str(exc),

                    "status": "failed",

                },

                "errors": state.get(
                    "errors",
                    [],
                ) + [

                    f"SecurityAgent: {exc}"

                ],

            }

    def _protocol_node(self, state: TelesurgeryState) -> dict:
        """
        Node 3 — Protocol Switcher
        """

        logger.info("[Node 3/6] Protocol Switcher evaluating...")
        start_time = time.perf_counter()

        try:

            status = self.protocol_agent.run(
                state["security_report"] or {},
                state["network_metrics"],
            )

            # Securely transmit Protocol -> Feedback
            garlic = self.secure_channel.send(
                sender="Protocol",
                receiver="Feedback",
                workflow_id=state["run_id"],
                message=status,
            )

            status = self.secure_channel.receive(
                garlic,
                receiver="Feedback",
            )

            logger.info("Protocol -> Feedback transmission successful.")

            duration = time.perf_counter() - start_time

            self._log_protocol(
                state=state,
                protocol_status=status,
                status="Success",
            )

            self._log_workflow(
                state=state,
                stage="Protocol",
                event="Completed",
                result="Success",
                duration=duration,
            )

            return {
                "protocol_status": status
            }

        except Exception as exc:

            logger.error(
                f"Protocol Switcher error: {exc}"
            )

            duration = time.perf_counter() - start_time

            self._log_protocol(
                state=state,
                protocol_status={},
                status="Failed",
            )

            self._log_workflow(
                state=state,
                stage="Protocol",
                event="Completed",
                result="Failed",
                duration=duration,
            )

            return {

                "protocol_status": {

                    "recommended_protocol": "TCP",

                    "error": str(exc),

                    "status": "failed",

                },

                "errors": state.get(
                    "errors",
                    [],
                ) + [

                    f"ProtocolAgent: {exc}"

                ],

            }

    def _feedback_node(self, state: TelesurgeryState) -> dict:
        """
        Node 4 — Feedback Agent
        """

        logger.info("[Node 4/6] Feedback Agent aggregating...")
        start_time = time.perf_counter()

        try:

            fb = self.feedback_agent.run(

                state["surgery_plan"] or {},

                state["security_report"] or {},

                state["protocol_status"] or {},

            )

            # Securely transmit Feedback -> Robotic
            garlic = self.secure_channel.send(
                sender="Feedback",
                receiver="Robotic",
                workflow_id=state["run_id"],
                message=fb,
            )

            fb = self.secure_channel.receive(
                garlic,
                receiver="Robotic",
            )

            logger.info("Feedback -> Robotic transmission successful.")

            duration = time.perf_counter() - start_time

            self._log_feedback(
                state=state,
                feedback=fb,
                status="Success",
            )

            self._log_workflow(
                state=state,
                stage="Feedback",
                event="Completed",
                result="Success",
                duration=duration,
            )

            return {
                "feedback": fb
            }

        except Exception as exc:

            logger.error(
                f"Feedback Agent error: {exc}"
            )

            duration = time.perf_counter() - start_time

            self._log_feedback(
                state=state,
                feedback={},
                status="Failed",
            )

            self._log_workflow(
                state=state,
                stage="Feedback",
                event="Completed",
                result="Failed",
                duration=duration,
            )

            return {

                "feedback": {

                    "proceed_with_surgery": False,

                    "safety_level": "halt",

                    "hold_reason": f"Feedback Agent error: {exc}",

                    "robotic_arm_command": {

                        "action": "pause",

                        "speed": "emergency_stop",

                        "target_step": "error_recovery",

                    },

                    "error": str(exc),

                },

                "errors": state.get(
                    "errors",
                    [],
                ) + [

                    f"FeedbackAgent: {exc}"

                ],

            }

    def _robotic_node(self, state: TelesurgeryState) -> dict:
        """Node 5 — Robotic Arm Agent: execute surgical instruction."""  
        logger.info("[Node 5/6] Robotic Arm executing...")
        start_time = time.perf_counter()

        try:
            result = self.robotic_agent.run(
                state["feedback"] or {}
            )

            duration = time.perf_counter() - start_time

            backup_triggered = self.robotic_agent.needs_backup()

            self._log_robotic(
                state=state,
                robotic_result=result,
                backup_triggered=backup_triggered,
            )

            self._log_workflow(
                state=state,
                stage="Robotic",
                event="Completed",
                result="Success",
                duration=duration,
            )

            return {
                "arm_result": result,
                "backup_required": backup_triggered,
            }
        
        except Exception as exc:

            logger.error(
                f"Robotic Arm error: {exc}"
            )

            duration = time.perf_counter() - start_time

            self._log_robotic(
                state=state,
                robotic_result={},
                backup_triggered=True,
            )

            self._log_workflow(
                state=state,
                stage="Robotic",
                event="Completed",
                result="Failed",
                duration=duration,
            )

            return {

                "arm_result": {

                    "status": "failed",

                    "step_completed": False,

                    "failure": True,

                    "remarks": f"Robotic arm exception: {exc}",

                    "step_number": self.robotic_agent.current_step,

                },

                "backup_required": True,

                "errors": state.get(
                    "errors",
                    [],
                ) + [

                    f"RoboticAgent: {exc}"

                ],

            }

    def _backup_node(self, state: TelesurgeryState) -> dict:
        """Node 6 (conditional) — Backup Surgeon Agent: failover recovery."""
        logger.info("[Node 6/6] Backup Surgeon Agent activating...")
        start_time = time.perf_counter()

        try:
            result = self.backup_agent.run(
                state["arm_result"] or {},
                state["surgery_plan"] or {},
            )

            duration = time.perf_counter() - start_time

            self._log_workflow(
                state=state,
                stage="Backup",
                event="Activated",
                result="Success",
                duration=duration,
            )

            return {
                "backup_result": result,
                "completed": True,
            }
        
        except Exception as exc:
            logger.error(f"Backup Surgeon error: {exc}")

            duration = time.perf_counter() - start_time

            self._log_workflow(
                state=state,
                stage="Backup",
                event="Activated",
                result="Failed",
                duration=duration,
            )

            return {
                "backup_result": {
                    "backup_activated": True,
                    "error": str(exc),
                    "message": f"Backup agent error: {exc}",
                },
                "errors":    state.get("errors", []) + [f"BackupAgent: {exc}"],
                "completed": True,
            }

    # ─────────────────────────────────────────────────────────────
    # Conditional router
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _needs_backup_router(state: TelesurgeryState) -> str:
        """
        Route to backup_node if the robotic arm failed or is on hold.
        Otherwise route to END.

        This mirrors Algorithm 2 Steps 11–12:
          if Robotic Arm failure or "on hold" then Activate Backup Surgeon Agent
        """
        arm = state.get("arm_result") or {}
        needs_backup = (
            arm.get("failure") is True
            or arm.get("status") in (
                RoboticStatus.ON_HOLD.value,
                RoboticStatus.FAILED.value,
            )
        )

        if needs_backup:
            logger.info(
                f"Router: arm status='{arm.get('status')}' "
                f"→ activating Backup Surgeon Agent"
            )
            return "backup_node"

        logger.info("Router: arm completed successfully → END")
        return END

    # ─────────────────────────────────────────────────────────────
    # Google Sheets Logging Helpers
    # ─────────────────────────────────────────────────────────────

    def _log_doctor(
        self,
        state: TelesurgeryState,
        plan: dict,
        status: str,
        remarks: str = "",
    ) -> None:
        """
        Log Doctor Agent results to the Doctor worksheet.
        """

        try:

            diagnosis = state.get("diagnosis", {})

            sheet_logger.log_doctor(
                run_id=state["run_id"],
                timestamp=state["timestamp"],
                patient_id=diagnosis.get("patient_id", "Unknown"),
                diagnosis=plan.get("diagnosis", "Unknown"),
                priority=plan.get("priority", "Unknown"),
                confidence=plan.get("confidence", "Unknown"),
                response_time=self.doctor_agent.metrics.get(
                    "elapsed_time",
                    0,
                ),
                status=status,
                remarks=remarks,
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Doctor worksheet: {exc}"
            )

    def _log_security(
        self,
        state: TelesurgeryState,
        report: dict,
        status: str,
    ) -> None:
        """
        Log Security Agent results to the Security worksheet.
        """

        try:

            sheet_logger.log_security(
                run_id=state["run_id"],
                timestamp=state["timestamp"],
                traffic_samples=len(state.get("traffic_data", [])),
                threat_detected=report.get("attack_detected", False),
                threat_type=report.get("attack_type", "None"),
                severity=report.get("severity", "Unknown"),
                action_taken=report.get("recommended_action", "None"),
                response_time=self.security_agent.metrics.get(
                    "elapsed_time",
                    0,
                ),
                status=status,
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Security worksheet: {exc}"
            )

    def _log_protocol(
        self,
        state: TelesurgeryState,
        protocol_status: dict,
        status: str,
    ) -> None:
        """
        Log Protocol Switcher results to the Protocol worksheet.
        """

        try:

            metrics = state.get("network_metrics", {})

            sheet_logger.log_protocol(
                run_id=state["run_id"],
                timestamp=state["timestamp"],
                current_protocol=protocol_status.get(
                    "previous_protocol",
                    "Unknown",
                ),
                selected_protocol=protocol_status.get(
                    "recommended_protocol",
                    "Unknown",
                ),
                reason=protocol_status.get(
                    "rationale",
                    "",
                ),
                network_latency=metrics.get(
                    "latency_ms",
                    0,
                ),
                packet_loss=metrics.get(
                    "packet_loss_pct",
                    0,
                ),
                jitter=metrics.get(
                    "jitter_ms",
                    0,
                ),
                response_time=self.protocol_agent.metrics.get(
                    "elapsed_time",
                    0,
                ),
                status=status,
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Protocol worksheet: {exc}"
            )

    def _log_feedback(
        self,
        state: TelesurgeryState,
        feedback: dict,
        status: str,
    ) -> None:
        """
        Log Feedback Agent results to the Feedback worksheet.
        """

        try:

            decision = (
                "Proceed"
                if feedback.get("proceed_with_surgery", False)
                else "Hold"
            )

            sheet_logger.log_feedback(
                run_id=state["run_id"],
                timestamp=state["timestamp"],
                safety_level=feedback.get(
                    "safety_level",
                    "Unknown",
                ),
                decision=decision,
                reason=feedback.get(
                    "hold_reason",
                    "",
                ),
                response_time=self.feedback_agent.metrics.get(
                    "elapsed_time",
                    0,
                ),
                status=status,
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Feedback worksheet: {exc}"
            )

    def _log_robotic(
        self,
        state: TelesurgeryState,
        robotic_result: dict,
        backup_triggered: bool,
    ) -> None:
        """
        Log Robotic Arm Agent results to the Robotic worksheet.
        """

        try:

            sheet_logger.log_robotic(
                run_id=state["run_id"],
                timestamp=state["timestamp"],
                current_step=robotic_result.get(
                    "step_number",
                    0,
                ),
                executed_action=robotic_result.get(
                    "step_name",
                    "Unknown",
                ),
                status=robotic_result.get(
                    "status",
                    "Unknown",
                ),
                failure=robotic_result.get(
                    "failure",
                    False,
                ),
                backup_triggered=backup_triggered,
                remarks=robotic_result.get(
                    "remarks",
                    "",
                ),
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Robotic worksheet: {exc}"
            )

    def _log_workflow(
        self,
        state: TelesurgeryState,
        stage: str,
        event: str,
        result: str,
        duration: float,
    ) -> None:
        """
        Log workflow execution events.
        """

        try:

            sheet_logger.log_workflow(
                timestamp=state["timestamp"],
                run_id=state["run_id"],
                stage=stage,
                event=event,
                result=result,
                duration=duration,
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Workflow worksheet: {exc}"
            )

    
    def _log_summary(
        self,
        state: TelesurgeryState,
        overall_score: float,
        execution_time: float,
    ) -> None:
        """
        Log overall workflow summary.
        """

        print(">>> ENTERED _log_summary")

        try:

            diagnosis = state.get("diagnosis", {})
            surgery_plan = state.get("surgery_plan", {})
            robotic_result = state.get("arm_result", {})

            total_errors = 0

            if state.get("security_report", {}).get("attack_detected"):
                total_errors += 1

            if robotic_result.get("failure", False):
                total_errors += 1

            backup_required = state.get("backup_required", False)

            final_status = (
                "Completed"
                if robotic_result.get("step_completed", False)
                else "Failed"
            )

            sheet_logger.log_summary(
                run_id=state["run_id"],
                timestamp=state["timestamp"],
                scenario_id=state.get("scenario_id", "N/A"),
                model=state["model"],
                patient_id=diagnosis.get("patient_id", "Unknown"),
                diagnosis=surgery_plan.get("diagnosis", "Unknown"),
                surgery_type=surgery_plan.get("surgery_type", "Unknown"),
                final_status=final_status,
                backup_required=backup_required,
                total_errors=total_errors,
                overall_score=overall_score,
                execution_time=execution_time,
            )

        except Exception as exc:

            logger.error(
                f"Failed to log Summary worksheet: {exc}"
            )

        print(">>> Summary written")

    def _log_evaluation(
        self,
        state: TelesurgeryState,
        evaluation: dict,
    ) -> None:
        """
        Log evaluation metrics to the Evaluation worksheet.
        """
        print(">>> ENTERED _log_evaluation")

        try:

            sheet_logger.log_evaluation(

                run_id=state["run_id"],

                model=state["model"],

                response_latency=evaluation[
                    "latency"
                ],

                edge_efficiency=evaluation[
                    "edge_efficiency"
                ],

                workflow_accuracy=evaluation[
                    "workflow_accuracy"
                ],

                security_accuracy=evaluation[
                    "security_accuracy"
                ],

                clinical_hallucination=evaluation[
                    "clinical_hallucination"
                ],

                operational_robustness=1.0,

                overall_score=evaluation[
                    "overall_score"
                ],

            )

        except Exception as exc:

            logger.error(
                f"Failed to log Evaluation worksheet: {exc}"
            )
        print(">>> Evaluation written")

    # ---------------------------------
    # Evaluation Helpers
    # ---------------------------------

    def _collect_latency_metrics(self) -> dict:
            """
            Collect latency metrics from all LLM agents.
            """

            agent_times = [

                self.doctor_agent.metrics.get(
                    "elapsed_time",
                    0.0,
                ),

                self.security_agent.metrics.get(
                    "elapsed_time",
                    0.0,
                ),

                self.protocol_agent.metrics.get(
                    "elapsed_time",
                    0.0,
                ),

                self.feedback_agent.metrics.get(
                    "elapsed_time",
                    0.0,
                ),

            ]

            total_generation_time = sum(agent_times)

            average_agent_time = (

                total_generation_time / len(agent_times)

                if agent_times

                else 0.0

            )

            return {

                "ttft": self.doctor_agent.metrics.get(
                    "elapsed_time",
                    0.0,
                ),

                "total_generation_time": total_generation_time,

                "average_agent_time": average_agent_time,

            }

    def _collect_edge_metrics(self) -> dict:
            """
            Collect edge deployment metrics.
            """

            import psutil

            cpu_percent = psutil.cpu_percent()

            ram_gb = (

                psutil.Process()

                .memory_info()

                .rss

                / (1024 ** 3)

            )

            tokens_per_second = 0.0

            agents = [

                self.doctor_agent,

                self.security_agent,

                self.protocol_agent,

                self.feedback_agent,

            ]

            values = [

                agent.metrics.get(
                    "tokens_per_second",
                    0.0,
                )

                for agent in agents

            ]

            if values:

                tokens_per_second = sum(values) / len(values)

            return {

                "cpu_percent": round(cpu_percent, 2),

                "ram_gb": round(ram_gb, 2),

                "tokens_per_second": round(
                    tokens_per_second,
                    2,
                ),

            }

    def _evaluate_workflow(
            self,
            workflow_state: dict,
            expected_output: dict | None = None,
        ) -> dict:
            """
            Evaluate the completed telesurgery workflow.
            """

            if expected_output is None:
                expected_output = self._load_expected_output(
                    workflow_state["diagnosis"]
                )

            latency_metrics = self._collect_latency_metrics()

            edge_metrics = self._collect_edge_metrics()

            evaluation = Evaluator.evaluate(

                workflow_state=workflow_state,

                expected_output=expected_output,

                latency_metrics=latency_metrics,

                edge_metrics=edge_metrics,

                model_name=workflow_state["model"],

            )

            return evaluation

    def _load_expected_output(
            self,
            diagnosis: dict,
        ) -> dict:
            """
            Build the expected (ground-truth) output used by the evaluator.
            """

            return {

                "diagnosis": diagnosis.get(
                    "diagnosis",
                    "",
                ),

                "patient_id": diagnosis.get(
                    "patient_id",
                    "",
                ),

                "surgery_type": diagnosis.get(
                    "recommended_surgery",
                    "",
                ),

                "priority": diagnosis.get(
                    "priority",
                    "",
                ),

            }

    
    
    # ─────────────────────────────────────────────────────────────
    # Results persistence
    # ─────────────────────────────────────────────────────────────

    def _save_results(self, run_id: str, state: dict) -> None:
        """Save the full workflow state to results/<run_id>.json."""
        out_dir: Path = settings.RESULTS_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        ts      = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"run_{run_id}_{ts}.json"

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, default=str)
            logger.info(f"Results saved → {out_path}")
        except Exception as exc:
            logger.error(f"Failed to save results: {exc}")
