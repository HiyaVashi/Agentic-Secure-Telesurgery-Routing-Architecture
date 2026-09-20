"""
app.py
───────
Telesurgery-LangChain — Main Entry Point

Bootstraps the full agentic telesurgery system:
  1. Parses CLI arguments
  2. Loads patient diagnosis + network traffic from data/
  3. Initialises the selected Ollama model
   (Llama 3.2 or VibeThinker 1.5)
  4. Compiles and runs the LangGraph telesurgery workflow
  5. Prints a structured results summary to stdout
  6. JSON results are auto-saved to results/ by the workflow

Usage:
    # Default — run Case 1 (heart surgery) with Llama 3.2 / vibethinker 1.5
    python app.py --model llama
    python app.py --model vibethinker

    # Choose a diagnosis case (0=heart, 1=brain, 2=orthopedic)
    python app.py --case 1

    # Use local Ollama instead of Gemini
    python app.py --llm ollama

    # Combine both flags
    python app.py --case 2 --llm ollama

    # Run all three diagnosis cases back-to-back
    python app.py --all

Environment / .env:
    GEMINI_API_KEY=<your_key>        required when --llm gemini (default)
    DEFAULT_LLM=gemini               override via .env
    OLLAMA_MODEL=llama3.2            override Ollama model name

Paper reference:
    This file orchestrates the workflow described in Fig. 4 (N8N Workflow)
    and Algorithm 2 (Agentic AI Telesurgery Workflow) of:
    "Agentic Architecture Enabling Secure and Fault Tolerant Telesurgery"
"""

import argparse
import json
import sys
from pathlib import Path

# ── Ensure project root is on sys.path when run directly ─────────────
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from models.llm import get_llm
from utils.logger import setup_logger
from workflows.telesurgery_workflow import TelesurgeryWorkflow

logger = setup_logger("app")


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────

def load_diagnosis(case_index: int = 0) -> dict:
    """
    Load a patient diagnosis from data/diagnosis.json.

    Args:
        case_index: 0 = heart (default), 1 = brain, 2 = orthopedic

    Returns:
        Single diagnosis dict ready for DoctorAgent.run()
    """
    path = settings.DATA_DIR / "diagnosis.json"
    if not path.exists():
        raise FileNotFoundError(f"Diagnosis data not found: {path}")

    cases: list = json.loads(path.read_text(encoding="utf-8"))

    if case_index >= len(cases):
        logger.warning(
            f"Case index {case_index} out of range "
            f"(only {len(cases)} cases available). Defaulting to case 0."
        )
        case_index = 0

    chosen = cases[case_index]
    logger.info(
        f"Loaded diagnosis | case={case_index} "
        f"patient={chosen.get('patient_id')} "
        f"type={chosen.get('type')}"
    )
    return chosen


def load_traffic() -> tuple[list, dict]:
    """
    Load network traffic records and link metrics from data/traffic.json.

    Returns:
        Tuple of (packets list, network_metrics dict) ready for the workflow.
    """
    path = settings.DATA_DIR / "traffic.json"
    if not path.exists():
        raise FileNotFoundError(f"Traffic data not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    packets         = raw.get("packets", [])
    network_metrics = raw.get("network_metrics", {
        "latency_ms": 85.0,
        "jitter_ms": 45.0,
        "packet_loss_pct": 3.2,
        "bandwidth_mbps": 12.5,
        "link_quality": "degraded",
    })

    normal_count    = sum(1 for p in packets if p.get("label") == "normal")
    malicious_count = len(packets) - normal_count

    logger.info(
        f"Loaded traffic | total={len(packets)} "
        f"normal={normal_count} malicious={malicious_count} "
        f"latency={network_metrics.get('latency_ms')}ms "
        f"jitter={network_metrics.get('jitter_ms')}ms "
        f"loss={network_metrics.get('packet_loss_pct')}%"
    )
    return packets, network_metrics


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS PRINTER
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(state: dict) -> None:
    """
    Print a human-readable summary of the completed workflow run.

    Args:
        state: Final TelesurgeryState dict returned by TelesurgeryWorkflow.run()
    """
    sep  = "═" * 62
    sep2 = "─" * 62

    plan     = state.get("surgery_plan")    or {}
    sec      = state.get("security_report") or {}
    proto    = state.get("protocol_status") or {}
    fb       = state.get("feedback")        or {}
    arm      = state.get("arm_result")      or {}
    backup   = state.get("backup_result")
    errors   = state.get("errors", [])

    print(f"\n{sep}")
    print(f"  TELESURGERY WORKFLOW — RESULTS SUMMARY")
    print(f"  Run ID    : {state.get('run_id', 'N/A')}")
    print(f"  Timestamp : {state.get('timestamp', 'N/A')}")
    print(f"  Model     : {state.get('model', settings.OLLAMA_MODEL)}")
    print(sep)

    # ── Surgery Plan ──────────────────────────────────────────────
    print(f"\n{'[1] DOCTOR AGENT — Surgery Plan':}")
    print(sep2)
    print(f"  Patient ID       : {plan.get('patient_id', 'N/A')}")
    print(f"  Surgery Type     : {plan.get('surgery_type', 'N/A')}")
    print(f"  Risk Level       : {plan.get('risk_level', 'N/A')}")
    print(f"  Duration (est.)  : {plan.get('estimated_duration_minutes', 'N/A')} min")
    print(f"  Protocol Pref.   : {plan.get('protocol_preference', 'N/A')}")
    steps = plan.get("surgical_steps", [])
    if steps:
        print(f"  Surgical Steps   :")
        for i, step in enumerate(steps, 1):
            print(f"    {i:>2}. {step}")
    tools = plan.get("required_tools", [])
    if tools:
        print(f"  Required Tools   : {', '.join(tools)}")

    # ── Security Report ───────────────────────────────────────────
    print(f"\n[2] SECURITY AGENT — Threat Report")
    print(sep2)
    attack = sec.get("attack_detected", False)
    print(f"  Attack Detected  : {'⚠  YES' if attack else '✓  No'}")
    if attack:
        print(f"  Attack Type      : {sec.get('attack_type', 'N/A').upper()}")
        print(f"  Severity         : {sec.get('severity', 'N/A').upper()}")
        print(f"  Confidence       : {sec.get('confidence', 0):.0%}")
        print(f"  Malicious Pkts   : {sec.get('malicious_count', 'N/A')}")
        affected = sec.get("affected_nodes", [])
        if affected:
            print(f"  Affected Nodes   : {', '.join(affected)}")
        print(f"  Alert            : {sec.get('alert_message', 'N/A')}")
    else:
        print(f"  Benign Packets   : {sec.get('benign_count', 'N/A')}")

    # ── Protocol Status ───────────────────────────────────────────
    print(f"\n[3] PROTOCOL SWITCHER — Network Adaptation")
    print(sep2)
    prev_proto = proto.get("previous_protocol", "N/A")
    curr_proto = proto.get("recommended_protocol",
                  proto.get("current_protocol", "N/A"))
    switched   = prev_proto != curr_proto
    print(f"  Previous Protocol: {prev_proto}")
    print(f"  Current Protocol : {curr_proto}{'  ← SWITCHED' if switched else '  (no change)'}")
    print(f"  Action Taken     : {proto.get('action_taken', 'N/A')}")
    print(f"  Rerouted         : {'Yes → ' + str(proto.get('backup_server')) if proto.get('rerouted') else 'No'}")
    print(f"  Status           : {proto.get('status', 'N/A')}")
    if proto.get("rationale"):
        print(f"  Rationale        : {proto.get('rationale')}")

    # ── Feedback Decision ─────────────────────────────────────────
    print(f"\n[4] FEEDBACK AGENT — Aggregated Decision")
    print(sep2)
    cmd = fb.get("robotic_arm_command", {})
    print(f"  Safety Level     : {fb.get('safety_level', 'N/A').upper()}")
    print(f"  Proceed Surgery  : {'✓  Yes' if fb.get('proceed_with_surgery') else '✗  No'}")
    if fb.get("hold_reason"):
        print(f"  Hold Reason      : {fb.get('hold_reason')}")
    print(f"  Arm Command      : action={cmd.get('action', 'N/A')}  "
          f"speed={cmd.get('speed', 'N/A')}")
    print(f"  Target Step      : {cmd.get('target_step', 'N/A')}")
    if fb.get("anomaly_score") is not None:
        print(f"  Anomaly Score    : {fb.get('anomaly_score'):.4f}")
    corrections = fb.get("corrective_actions", [])
    if corrections:
        print(f"  Corrections      :")
        for c in corrections:
            print(f"    • {c}")
    if fb.get("feedback_summary"):
        summary_lines = str(fb["feedback_summary"]).split(". ")
        print(f"  Summary          : {summary_lines[0]}.")

    # ── Robotic Arm Result ────────────────────────────────────────
    print(f"\n[5] ROBOTIC ARM AGENT — Execution Result")
    print(sep2)
    completed = arm.get("step_completed", False)
    print(f"  Status           : {arm.get('status', 'N/A').upper()}")
    print(f"  Step Completed   : {'✓  Yes' if completed else '✗  No'}")
    print(f"  Step Number      : {arm.get('step_number', 'N/A')}")
    print(f"  Step Name        : {arm.get('step_name', 'N/A')}")
    print(f"  Remarks          : {arm.get('remarks', 'N/A')}")
    if arm.get("execution_time_ms"):
        print(f"  Execution Time   : {arm.get('execution_time_ms')} ms")

    # ── Backup Surgeon ────────────────────────────────────────────
    print(f"\n[6] BACKUP SURGEON AGENT")
    print(sep2)
    if backup:
        print(f"  Status           : ⚡ ACTIVATED (activation #{backup.get('activation_number', 1)})")
        print(f"  Takeover Step    : {backup.get('takeover_step', 'N/A')}")
        print(f"  Recovery Action  : {backup.get('recovery_action', 'N/A')}")
        print(f"  Patient Safety   : {backup.get('patient_safety_status', 'N/A').upper()}")
        print(f"  Continue Surgery : {'Yes' if backup.get('continue_surgery') else 'No — ABORT'}")
        if not backup.get("continue_surgery") and backup.get("abort_reason"):
            print(f"  Abort Reason     : {backup.get('abort_reason')}")
        print(f"  Backup Protocol  : {backup.get('backup_protocol', 'N/A')}")
        est = backup.get("estimated_recovery_seconds")
        if est:
            print(f"  Est. Recovery    : {est}s")
        if backup.get("message"):
            print(f"  Message          : {backup.get('message')}")
    else:
        print(f"  Status           : ✓  Standby (not needed — arm completed successfully)")

    # ── Errors ────────────────────────────────────────────────────
    if errors:
        print(f"\n⚠  NON-FATAL ERRORS DURING RUN")
        print(sep2)
        for err in errors:
            print(f"  • {err}")

    # ── Final outcome ─────────────────────────────────────────────
    print(f"\n{sep}")
    outcome = "COMPLETED" if state.get("completed") or not backup else "COMPLETED (via backup)"
    if errors:
        outcome = "COMPLETED WITH WARNINGS"
    if arm.get("failure") and not backup:
        outcome = "FAILED — NO BACKUP ACTIVATED"
    print(f"  FINAL OUTCOME    : {outcome}")
    print(f"  Results saved to : {settings.RESULTS_DIR}/")
    print(f"{sep}\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Telesurgery-LangChain — Agentic AI telesurgery system.\n"
            "Runs the full multi-agent workflow: Doctor → Security → Protocol → "
            "Feedback → Robotic Arm → [Backup Surgeon]."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python app.py --model llama       # heart surgery, llama\n"
            "python app.py --model vibethinker  # heart surgery, Vibethinker\n"
            "  python app.py --case 1         # brain surgery\n"
            "  python app.py --case 2         # orthopedic surgery\n"
            "  python app.py --model llama     # use local Ollama model\n"
            "  python app.py --all            # run all 3 cases\n"
        ),
    )
    parser.add_argument(
        "--case", "-c",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Diagnosis case index: 0=heart (default), 1=brain, 2=orthopedic",
    )
    parser.add_argument(
    "--model", "-m",
    type=str,
    default=None,
    choices=["llama", "vibethinker"],
    help="Model to use for this run."
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all three diagnosis cases sequentially",
    )
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# SINGLE RUN
# ─────────────────────────────────────────────────────────────────────────────

def run_single(workflow: TelesurgeryWorkflow, case_index: int) -> dict:
    """Execute one workflow run for a given diagnosis case."""
    diagnosis                  = load_diagnosis(case_index)
    traffic_data, net_metrics  = load_traffic()

    logger.info(
        f"Starting workflow | case={case_index} "
        f"patient={diagnosis.get('patient_id')} "
        f"surgery={diagnosis.get('type')}"
    )

    state = workflow.run(
        diagnosis       = diagnosis,
        traffic_data    = traffic_data,
        network_metrics = net_metrics,
    )

    print_summary(state)
    return state


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    # ── Override Ollama model if --model was passed ───────────────
    if args.model:

        if args.model == "llama":
            settings.OLLAMA_MODEL = "llama3.2:3b"

        elif args.model == "vibethinker":
            settings.OLLAMA_MODEL = "vibethinker:1.5"

        logger.info(
            f"Model overridden via CLI: {settings.OLLAMA_MODEL}"
        )

    # ── Banner ────────────────────────────────────────────────────
    print("\n" + "═" * 62)
    print("  TELESURGERY-LANGCHAIN")
    print("  Agentic AI — Secure & Fault-Tolerant Telesurgery")
    print("  Paper: 'Agentic Architecture Enabling Secure and")
    print("          Fault Tolerant Telesurgery'")
    print("\n" + "═" * 62)
    print("  TELESURGERY-LANGCHAIN")
    print("  Agentic AI — Secure & Fault-Tolerant Telesurgery")
    print("═" * 62)

    print(f"  Model       : {settings.OLLAMA_MODEL}")
    print(f"  Ollama URL  : {settings.OLLAMA_BASE_URL}")
    print(f"  Temperature : {settings.OLLAMA_TEMPERATURE}")

    print("═" * 62 + "\n")
    # ── Initialise LLM ────────────────────────────────────────────
    try:
        llm = get_llm()
    except Exception as exc:
        logger.error(str(exc))
        print(f"\nError: {exc}")
        sys.exit(1)

    # ── Compile workflow (shared across runs) ─────────────────────
    logger.info("Compiling LangGraph workflow...")
    workflow = TelesurgeryWorkflow(llm)

    # ── Run ───────────────────────────────────────────────────────
    if args.all:
        logger.info("Running all 3 diagnosis cases...")
        for idx in range(3):
            print(f"\n{'▶' * 3}  CASE {idx}  {'▶' * 3}\n")
            run_single(workflow, idx)
    else:
        run_single(workflow, args.case)


if __name__ == "__main__":
    main()
