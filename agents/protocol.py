"""
agents/protocol.py
───────────────────
Protocol Switcher Agent (Ap) — LangChain LCEL Implementation

Dynamically selects the optimal network protocol (TCP / UDP / QUIC) based on
current network conditions and the Security Agent's threat report.

The agent uses a hybrid approach:
  Fast path:  Deterministic rule-based switching (no LLM, sub-millisecond)
  Deep path:  LLM-based reasoning for ambiguous network states

The rule thresholds are defined in config.py and derived from the paper:
  • Attack detected     → TCP  → UDP  + reroute to backup server
  • High jitter/loss   → any  → QUIC  (resilient multiplexed streams)
  • Stable link        → any  → TCP   (restored for ordering guarantees)

Paper reference:
  • Section III-C  — Protocol Switcher (Ap) description
  • Section III-D  — Secure Adaptive Control Layer
  • Eq. (3)        — R(t) = αS(t) + βP(t) + γB(t)
  • Eq. (13)       — A(t) = fcontrol(C(t), Af(t), Rb(t), Qp(N(t)))
  • Algorithm 2    — Steps 3–5: protocol switching logic
"""

import json
from datetime import datetime, timezone
from enum import Enum
from utils.base_agent import BaseAgent
from config import settings
from utils.logger import setup_logger

class Protocol(str, Enum):
    TCP  = "TCP"
    UDP  = "UDP"
    QUIC = "QUIC"


class ProtocolSwitcherAgent(BaseAgent):
    """
    Protocol Switcher — hybrid rule-based + LLM protocol selection.

    Maintains stateful tracking of the current protocol across workflow cycles
    so the LLM reasoning can factor in recent history.
    """

    def __init__(self, llm):

        super().__init__(
            model=llm,
            prompt_path=settings.PROMPTS_DIR / "protocol.txt"
        )

        self.log = setup_logger("agents.protocol")

    # Stateful protocol tracking
        self.current_protocol = Protocol.TCP
        self.switch_history = []

        self.log.info(
            f"Protocol Switcher initialized. "
            f"Starting protocol: {self.current_protocol.value}"
        )

    # ─────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────

    def run(self, security_report: dict, network_metrics: dict) -> dict:
        """
        Evaluate current network conditions and select the optimal protocol.

        Args:
            security_report:  Output dict from SecurityAgent.run()
            network_metrics:  Dict with keys:
                - latency_ms       (float)
                - jitter_ms        (float)
                - packet_loss_pct  (float)
                - bandwidth_mbps   (float)
                - link_quality     (str)

        Returns:
            JSON dict with: previous_protocol, recommended_protocol,
            action_taken, rerouted, backup_server, rationale,
            protocol_quality_scores, status.
        """

        attack_detected = security_report.get("attack_detected", False)
        attack_type     = security_report.get("attack_type", "none")
        packet_loss     = float(network_metrics.get("packet_loss_pct", 0.0))
        jitter_ms       = float(network_metrics.get("jitter_ms", 0.0))
        latency_ms      = float(network_metrics.get("latency_ms", 50.0))

        self.log.info(
            f"Evaluating protocol | current={self.current_protocol} "
            f"attack={attack_detected} loss={packet_loss}% "
            f"jitter={jitter_ms}ms latency={latency_ms}ms"
        )

        # ── Fast rule-based decision ──────────────────────────────
        fast_decision = self._fast_rule_decision(
            attack_detected, packet_loss, jitter_ms, latency_ms
        )

        if fast_decision["definitive"]:
            # Definitive case — apply immediately, skip LLM
            self.log.info(
                f"Fast-path switch: {self.current_protocol} → "
                f"{fast_decision['protocol']} | {fast_decision['reason']}"
            )
            result = self._build_result(
                fast_decision["protocol"],
                fast_decision["action"],
                fast_decision["rerouted"],
                fast_decision["reason"],
            )


            return result

        # ── LLM reasoning for ambiguous states ────────────────────
        result = self.invoke({
            "current_protocol": self.current_protocol.value,
            "security_report": json.dumps(security_report, separators=(",", ":")),
            "latency_ms": str(latency_ms),
            "jitter_ms": str(jitter_ms),
            "packet_loss_pct": str(packet_loss),
            "bandwidth_mbps": str(network_metrics.get("bandwidth_mbps", 0)),
            "link_quality": str(network_metrics.get("link_quality", "unknown"))
        })

        # Apply the LLM's recommendation
        recommended = result.get("recommended_protocol", self.current_protocol.value)
        try:
            new_protocol = Protocol(recommended)
        except ValueError:
            new_protocol = self.current_protocol

        result["previous_protocol"] = self.current_protocol.value
        self._apply_protocol(new_protocol, result.get("rerouted", False))

        self.log.info(
            f"LLM protocol decision: {result.get('previous_protocol')} → "
            f"{new_protocol} | {result.get('action_taken')}"
        )

        return result
            

    # ─────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────

    def _fast_rule_decision(
        self,
        attack_detected: bool,
        packet_loss:     float,
        jitter_ms:       float,
        latency_ms:      float,
    ) -> dict:
        """
        Deterministic rule-based decisions that are unambiguous.
        Returns definitive=True only for clear-cut cases.
        """
        if attack_detected:
            return {
                "definitive": True,
                "protocol":   Protocol.UDP,
                "action":     "switched_TCP→UDP_rerouted",
                "rerouted":   True,
                "reason":     f"DDoS attack detected — immediate switch to UDP + reroute",
            }

        if (packet_loss > settings.PACKET_LOSS_THRESHOLD_PCT
                or jitter_ms > settings.JITTER_THRESHOLD_MS):
            return {
                "definitive": True,
                "protocol":   Protocol.QUIC,
                "action":     "switched_to_QUIC_degraded_link",
                "rerouted":   False,
                "reason":     (
                    f"Degraded link: loss={packet_loss}% jitter={jitter_ms}ms — "
                    "switching to QUIC for resilience"
                ),
            }

        if (latency_ms < settings.LATENCY_STABLE_MS
                and self.current_protocol != Protocol.TCP):
            return {
                "definitive": True,
                "protocol":   Protocol.TCP,
                "action":     "restored_to_TCP_stable_link",
                "rerouted":   False,
                "reason":     f"Link stable (latency={latency_ms}ms) — restoring TCP",
            }

        # Ambiguous — let LLM decide
        return {"definitive": False}

    def _build_result(
        self,
        new_protocol: Protocol,
        action:       str,
        rerouted:     bool,
        rationale:    str,
    ) -> dict:
        prev = self.current_protocol.value
        self._apply_protocol(new_protocol, rerouted)
        return {
            "previous_protocol":    prev,
            "recommended_protocol": new_protocol.value,
            "action_taken":         action,
            "rerouted":             rerouted,
            "backup_server":        settings.BACKUP_SERVER if rerouted else None,
            "rationale":            rationale,
            "protocol_quality_scores": self._quality_scores(new_protocol),
            "estimated_latency_improvement_ms": 0,
            "status":               "switched" if prev != new_protocol.value else "stable",
            "timestamp":            datetime.now(timezone.utc).isoformat(),
        }

    def _apply_protocol(self, new_protocol: Protocol, rerouted: bool) -> None:
        """Update state and record history."""
        self.switch_history.append({
            "from":     self.current_protocol.value,
            "to":       new_protocol.value,
            "rerouted": rerouted,
            "ts":       datetime.now(timezone.utc).isoformat(),
        })
        self.current_protocol = new_protocol

    def _quality_scores(self, chosen: Protocol) -> dict:
        """Heuristic quality scores — give the chosen protocol the highest score."""
        scores = {Protocol.TCP: 0.6, Protocol.UDP: 0.5, Protocol.QUIC: 0.55}
        scores[chosen] = 0.90
        return {p.value: round(s, 2) for p, s in scores.items()}
