from schemas.protocol_schema import ProtocolDecision

from config import csv_db
class ProtocolAgent:

    def select(self, security_result, network_data):

        if security_result.attack_detected:

            return ProtocolDecision(
                protocol="QUIC",
                reason="High severity attack detected",
                expected_latency="Low",
                security_level="High"
            )

        if network_data["latency"] > 150:

            return ProtocolDecision(
                protocol="TCP",
                reason="High latency",
                expected_latency="Medium",
                security_level="Medium"
            )

        return ProtocolDecision(
            protocol="UDP",
            reason="Normal network",
            expected_latency="Low",
            security_level="Normal"
        )