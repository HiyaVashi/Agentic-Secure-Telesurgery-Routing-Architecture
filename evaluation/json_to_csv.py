import json
import csv
from pathlib import Path

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RESULTS_DIR = BASE_DIR / "results"
OUTPUT_DIR = BASE_DIR / "csv_results"

OUTPUT_DIR.mkdir(exist_ok=True)

summary_csv = OUTPUT_DIR / "summary.csv"
traffic_csv = OUTPUT_DIR / "traffic.csv"

# ------------------------------------------------------------------
# Summary CSV
# ------------------------------------------------------------------

summary_fields = [

    # -----------------------------
    # Experiment Metadata
    # -----------------------------
    "Run_ID",
    "Timestamp",
    "Model",

    # -----------------------------
    # Patient
    # -----------------------------
    "Patient_ID",
    "Surgery_Type",

    # -----------------------------
    # Workflow
    # -----------------------------
    "Attack_Detected",
    "Recommended_Protocol",
    "Safety_Level",
    "Backup_Activated",
    "Completed",
    "Error_Count",

    # -----------------------------
    # Evaluation Metrics
    # -----------------------------
    "Latency",

    "Edge_Efficiency",

    "Workflow_Accuracy",

    "Security_Accuracy",

    "Clinical_Hallucination",

    "Operational_Robustness",

    "Overall_Score"

]

traffic_fields = [
    "Run_ID",
    "Packet_ID",
    "Protocol",
    "Source_IP",
    "Destination_IP",
    "Label",
    "Flow_Bytes_Per_Sec",
    "Flow_Packets_Per_Sec",
    "Packet_Loss",
    "Latency",
    "Jitter"
]

summary_rows = []
traffic_rows = []

# ------------------------------------------------------------------
# Read every JSON
# ------------------------------------------------------------------

for file in RESULTS_DIR.glob("*.json"):

    try:

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        summary_rows.append({

            "Run_ID": data.get("run_id"),

            "Timestamp": data.get("timestamp"),

            "Model": data.get("model"),

            "Patient_ID": data.get("diagnosis", {}).get("patient_id"),

            "Surgery_Type": data.get("diagnosis", {}).get("type"),

            "Attack_Detected": data.get(
                "security_report",
                {}
            ).get("attack_detected"),

            "Recommended_Protocol": data.get(
                "protocol_status",
                {}
            ).get("recommended_protocol"),

            "Safety_Level": data.get(
                "feedback",
                {}
            ).get("safety_level"),

            "Backup_Activated": data.get(
                "backup_result",
                {}
            ).get("backup_activated"),

            "Completed": data.get("completed"),

            "Error_Count": len(data.get("errors", []))
        })

        metrics = data.get("network_metrics", {})

        for packet in data.get("traffic_data", []):

            traffic_rows.append({

                "Run_ID": data.get("run_id"),

                "Packet_ID": packet.get("id"),

                "Protocol": packet.get("protocol"),

                "Source_IP": packet.get("src_ip"),

                "Destination_IP": packet.get("dst_ip"),

                "Label": packet.get("label"),

                "Flow_Bytes_Per_Sec": packet.get(
                    "flow_bytes_per_sec"
                ),

                "Flow_Packets_Per_Sec": packet.get(
                    "flow_packets_per_sec"
                ),

                "Packet_Loss": metrics.get(
                    "packet_loss_pct"
                ),

                "Latency": metrics.get(
                    "latency_ms"
                ),

                "Jitter": metrics.get(
                    "jitter_ms"
                )
            })

    except Exception as e:
        print(f"Skipped {file.name}: {e}")

# ------------------------------------------------------------------
# Save Summary CSV
# ------------------------------------------------------------------

with open(summary_csv, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=summary_fields
    )

    writer.writeheader()

    writer.writerows(summary_rows)

# ------------------------------------------------------------------
# Save Traffic CSV
# ------------------------------------------------------------------

with open(traffic_csv, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=traffic_fields
    )

    writer.writeheader()

    writer.writerows(traffic_rows)

print("-" * 60)
print("JSON → CSV Conversion Complete")
print(f"Experiments : {len(summary_rows)}")
print(f"Traffic Rows: {len(traffic_rows)}")
print(f"Saved : {summary_csv}")
print(f"Saved : {traffic_csv}")
print("-" * 60)