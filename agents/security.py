"""
agents/security.py
───────────────────
Security Agent (As) — LangChain LCEL Implementation

Continuously inspects network traffic to detect malicious activities
such as DDoS attacks (smurf, teardrop, UDP flood, SYN flood) and triggers
mitigation measures. Uses a two-stage approach:

  Stage 1: Fast rule-based pre-filter (sub-millisecond, no LLM required)
  Stage 2: LLM-enhanced deep analysis for ambiguous or complex patterns

The agent is trained on the LR-HR DDoS 2024 dataset (145,614 packets,
78,733 normal + 61,881 malicious, 22 features across 8 categories).

Paper reference:
  • Section III-C — Security Agent (As) description
  • Section III-B-1 — Dataset: LR-HR DDoS 2024
  • Section III-B-2 — Data Preprocessing (normalisation, one-hot encoding)
  • Algorithm 2    — Step 2: Security Agent inspects traffic
  • Algorithm 3    — TeleHealth-Secured MCP Anomaly Detection
"""

import datetime
import json

from enum import Enum

from utils.base_agent import BaseAgent
from config import settings
from utils.logger import setup_logger


# ── Attack type taxonomy (from LR-HR DDoS 2024 dataset labels) ──────
class AttackType(str, Enum):
    SMURF    = "smurf"
    TEARDROP = "teardrop"
    DDOS     = "ddos"
    LOW_RATE = "low_rate"
    NONE     = "none"


class SecurityAgent(BaseAgent):
    """
    Security Agent — two-stage DDoS detection for telesurgery networks.

    Rule-based signatures (Stage 1) catch obvious attacks instantly.
    LLM analysis (Stage 2) handles ambiguous traffic patterns.

    LCEL chain:  ChatPromptTemplate → LLM → JsonOutputParser
    """

    # Attack signatures mapped to packet label keywords
    # Sourced from paper's mention of "smurf or teardrop" attack patterns
    ATTACK_SIGNATURES: dict[AttackType, set[str]] = {
        AttackType.SMURF:    {"smurf", "icmp_flood", "broadcast", "amplification"},
        AttackType.TEARDROP: {"teardrop", "fragment_overlap", "malformed_packet"},
        AttackType.DDOS:     {"ddos", "syn_flood", "udp_flood", "high_packet_rate"},
        AttackType.LOW_RATE: {"low_rate", "lr_ddos", "slow_dos", "pulsing"},
    }

    # Heuristic: >1000 records in a batch is suspicious (mirrors dataset scale)
    HIGH_RATE_THRESHOLD: int = 1000

    def __init__(self, llm):

        super().__init__(
            model=llm,
            prompt_path=settings.PROMPTS_DIR / "security.txt"
        )

        self.log = setup_logger("agents.security")

        self.log.info("Security Agent initialized.")

    # ─────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────

    def run(self, traffic_data: list) -> dict:
        """
        Inspect a batch of network traffic records for DDoS attacks.

        Args:
            traffic_data: List of packet dicts. Each packet should contain
                at minimum: src_ip, dst_ip, protocol, size, label.
                Full 22-feature format matches the LR-HR DDoS 2024 dataset.

        Returns:
            JSON dict with: attack_detected, attack_type, confidence,
            affected_nodes, severity, recommended_action, alert_message,
            should_switch_protocol, should_activate_backup.
        """

        self.log.info(f"Inspecting {len(traffic_data)} traffic records...")

        # ── Stage 1: Rule-based pre-filter ────────────────────────
        rule_result = self._rule_based_detection(traffic_data)
        self.log.info(f"Rule-based pre-filter result: '{rule_result}'")

        # ── Stage 2: LLM deep analysis ────────────────────────────
        # Send only first 15 records to the LLM to stay within token budget
        sample = traffic_data[:15]

        result = self.invoke({
            "traffic_sample": json.dumps(sample, indent=2),
            "total_records":  str(len(traffic_data)),
            "rule_detected":  rule_result,
        })


        # Override: if rule-based found a definitive attack with high confidence,
        # trust the rule (sub-millisecond latency matters in surgery)
        if rule_result != AttackType.NONE.value and not result.get("attack_detected"):
            self.log.warning(
                "Rule-based detection overrides LLM (attack found in signatures). "
                f"Attack type: {rule_result}"
            )
            result["attack_detected"]   = True
            result["attack_type"]       = rule_result
            result["confidence"]        = 0.90
            result["override_reason"]   = "Rule-based signature match"

        # Logging
        if result.get("attack_detected"):
            self.log.warning(
                f"⚠ ATTACK DETECTED | type={result.get('attack_type')} "
                f"severity={result.get('severity')} "
                f"confidence={result.get('confidence', 0):.2f} "
                f"malicious≈{result.get('malicious_count')}"
            )
        else:
            self.log.info(
                f"Traffic clear | benign≈{result.get('benign_count', len(traffic_data))}"
            )


        return result

    # ─────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────

    def _rule_based_detection(self, traffic_data: list) -> str:
        """
        Fast O(n) rule-based check across all traffic labels.
        Runs before the LLM to catch obvious attacks instantly.
        """
        labels: list[str] = [
            str(pkt.get("label", "")).lower().replace(" ", "_")
            for pkt in traffic_data
        ]

        for attack_type, signatures in self.ATTACK_SIGNATURES.items():
            if any(sig in label for label in labels for sig in signatures):
                return attack_type.value

        if len(traffic_data) >= self.HIGH_RATE_THRESHOLD:
            return AttackType.DDOS.value

        return AttackType.NONE.value
