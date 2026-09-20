import json
import time
from database.csv_database import CSVDatabase

db = CSVDatabase()

from agents.doctor import DoctorAgent
from agents.security import SecurityAgent
from agents.protocol import ProtocolAgent
from agents.feedback import FeedbackAgent
from agents.robotic import RoboticAgent

from utils.logger import get_logger

logger = get_logger(__name__)


class TelesurgeryWorkflow:

    def __init__(self):

        logger.info("Initializing Telesurgery Workflow...")

        self.doctor = DoctorAgent()
        self.security = SecurityAgent()
        self.protocol = ProtocolAgent()
        self.feedback = FeedbackAgent()
        self.robot = RoboticAgent()
        self.db = CSVDatabase()
        logger.info("All agents initialized successfully.")

    def run(self, patient=None, traffic=None):

        workflow_start = time.time()

        logger.info("=" * 70)
        logger.info("WORKFLOW STARTED")
        logger.info("=" * 70)

        # -------------------------------------------------
        # Load Patient Data
        # -------------------------------------------------

        logger.info("Loading patient data...")

        if patient is None:
            with open("data/diagnosis.json", "r", encoding="utf-8") as f:
                patient = json.load(f)

        logger.info("Patient data loaded successfully.")

        logger.info("PATIENT INFORMATION")
        logger.info(f"Patient ID : {patient.get('patient_id')}")
        logger.info(f"Age        : {patient.get('age')}")
        logger.info(f"Gender     : {patient.get('gender')}")
        logger.info(f"Symptoms   : {patient.get('symptoms')}")
        logger.info(f"History    : {patient.get('history')}")

        # -------------------------------------------------
        # Load Network Data
        # -------------------------------------------------

        logger.info("Loading network traffic data...")

        if traffic is None:
            with open("data/traffic.json", "r", encoding="utf-8") as f:
                traffic = json.load(f)

        logger.info("Network data loaded successfully.")

        logger.info("NETWORK INFORMATION")
        logger.info(f"Latency       : {traffic.get('latency')}")
        logger.info(f"Packet Loss   : {traffic.get('packet_loss')}")
        logger.info(f"Bandwidth     : {traffic.get('bandwidth')}")
        logger.info(f"Attack Status : {traffic.get('attack_detected')}")

        # -------------------------------------------------
        # Doctor Agent
        # -------------------------------------------------

        logger.info("-" * 60)
        logger.info("Passing Patient Data -> Doctor Agent")
        logger.info("-" * 60)

        doctor_result = self.doctor.diagnose(patient)

        logger.info("Doctor Agent completed successfully.")

        doctor_data = doctor_result.model_dump()

        doctor_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        doctor_data["patient_id"] = patient["patient_id"]

        self.db.append(
            "doctor_log.csv",
            doctor_data
        )

        # -------------------------------------------------
        # Security Agent
        # -------------------------------------------------

        logger.info("-" * 60)
        logger.info("Passing Traffic Data -> Security Agent")
        logger.info("-" * 60)

        security_result = self.security.analyse(traffic)
        security_data = security_result.model_dump()

        security_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        security_data["patient_id"] = patient["patient_id"]

        self.db.append(
            "security_log.csv",
            security_data
        )

        logger.info("Security Agent completed successfully.")

        # -------------------------------------------------
        # Protocol Switcher
        # -------------------------------------------------

        logger.info("-" * 60)
        logger.info("Passing Security Result -> Protocol Switcher")
        logger.info("-" * 60)

        protocol_result = self.protocol.select(
            security_result,
            traffic
        )
        protocol_data = protocol_result.model_dump()

        protocol_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        protocol_data["patient_id"] = patient["patient_id"]

        self.db.append(
            "protocol_log.csv",
            protocol_data
        )

        logger.info("Protocol selected successfully.")

        # -------------------------------------------------
        # Feedback Agent
        # -------------------------------------------------

        logger.info("-" * 60)
        logger.info("Passing Results -> Feedback Agent")
        logger.info("-" * 60)

        feedback_result = self.feedback.evaluate(
            doctor_result,
            security_result,
            protocol_result
        )
        feedback_data = feedback_result.model_dump()

        feedback_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        feedback_data["patient_id"] = patient["patient_id"]

        self.db.append(
            "feedback_log.csv",
            feedback_data
        )

        logger.info("Feedback generated successfully.")

        # -------------------------------------------------
        # Robotic Agent
        # -------------------------------------------------

        logger.info("-" * 60)
        logger.info("Passing Decision -> Robotic Agent")
        logger.info("-" * 60)

        robot_result = self.robot.execute(feedback_result)

        robot_data = robot_result.model_dump()

        robot_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        robot_data["patient_id"] = patient["patient_id"]

        self.db.append(
            "robotic_log.csv",
            robot_data
        )

        logger.info("Robotic Agent execution completed.")

        # -------------------------------------------------
        # Final Results
        # -------------------------------------------------

        logger.info("=" * 70)
        logger.info("FINAL WORKFLOW RESULTS")
        logger.info("=" * 70)

        logger.info(f"Diagnosis           : {doctor_result.diagnosis}")
        logger.info(f"Recommended Surgery : {doctor_result.recommended_surgery}")
        logger.info(f"Urgency             : {doctor_result.urgency}")
        logger.info(f"Risk Level          : {doctor_result.risk_level}")

        logger.info(f"Attack Detected     : {security_result.attack_detected}")
        logger.info(f"Attack Type         : {security_result.attack_type}")
        logger.info(f"Severity            : {security_result.severity}")

        logger.info(f"Selected Protocol   : {protocol_result.protocol}")
        logger.info(f"Protocol Reason     : {protocol_result.reason}")
        logger.info(f"Expected Latency    : {protocol_result.expected_latency}")
        logger.info(f"Security Level      : {protocol_result.security_level}")

        logger.info(f"Action              : {feedback_result.action}")
        logger.info(f"Proceed             : {feedback_result.proceed}")
        logger.info(f"Reason              : {feedback_result.reason}")
        logger.info(f"Confidence          : {feedback_result.confidence}")

        logger.info(f"Robot Status        : {robot_result.status}")
        logger.info(f"Robot Action        : {robot_result.action}")

        workflow_end = time.time()

        logger.info("=" * 70)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info(f"Total Execution Time : {workflow_end - workflow_start:.2f} sec")
        logger.info("=" * 70)

        return {

    "doctor": doctor_result,

    "security": security_result,

    "protocol": protocol_result,

    "feedback": feedback_result,

    "robot": robot_result,

    "execution_time": workflow_end - workflow_start

}