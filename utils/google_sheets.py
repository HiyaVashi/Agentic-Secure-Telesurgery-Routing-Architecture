import gspread

from google.oauth2.service_account import Credentials

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(
    settings.GOOGLE_CREDENTIALS,
    scopes=SCOPES
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(settings.SPREADSHEET_ID)

class GoogleSheetsLogger:

    def __init__(self):
        self.summary = spreadsheet.worksheet("Summary")

        self.doctor = spreadsheet.worksheet("Doctor")

        self.security = spreadsheet.worksheet("Security")

        self.protocol = spreadsheet.worksheet("Protocol")

        self.feedback = spreadsheet.worksheet("Feedback")

        self.robotic = spreadsheet.worksheet("Robotic")

        self.evaluation = spreadsheet.worksheet("Evaluation")

        self.workflow = spreadsheet.worksheet("Workflow_log")

    def log_doctor(
        self,
        run_id,
        timestamp,
        patient_id,
        diagnosis,
        priority,
        confidence,
        response_time,
        status,
        remarks
):

        self.doctor.append_row([
            run_id,
            timestamp,
            patient_id,
            diagnosis,
            priority,
            confidence,
            response_time,
            status,
            remarks
        ])

    def log_security(
        self,
        run_id,
        timestamp,
        traffic_samples,
        threat_detected,
        threat_type,
        severity,
        action_taken,
        response_time,
        status
):

        self.security.append_row([
            run_id,
            timestamp,
            traffic_samples,
            threat_detected,
            threat_type,
            severity,
            action_taken,
            response_time,
            status
        ])

    def log_protocol(
    self,
    run_id,
    timestamp,
    current_protocol,
    selected_protocol,
    reason,
    network_latency,
    packet_loss,
    jitter,
    response_time,
    status
):
        """
        Logs Protocol Agent information to the Protocol worksheet.
        """

        self.protocol.append_row([
            run_id,
            timestamp,
            current_protocol,
            selected_protocol,
            reason,
            network_latency,
            packet_loss,
            jitter,
            response_time,
            status
        ])

    def log_feedback(
    self,
    run_id,
    timestamp,
    safety_level,
    decision,
    reason,
    response_time,
    status
):
        """
        Logs Feedback Agent information to the Feedback worksheet.
        """

        self.feedback.append_row([
            run_id,
            timestamp,
            safety_level,
            decision,
            reason,
            response_time,
            status
        ])

    def log_robotic(
    self,
    run_id,
    timestamp,
    current_step,
    executed_action,
    status,
    failure,
    backup_triggered,
    remarks
):
        """
        Logs Robotic Agent information to the Robotic worksheet.
        """

        self.robotic.append_row([
            run_id,
            timestamp,
            current_step,
            executed_action,
            status,
            failure,
            backup_triggered,
            remarks
        ])

    def log_summary(
    self,
    run_id,
    timestamp,
    scenario_id,
    model,
    patient_id,
    diagnosis,
    surgery_type,
    final_status,
    backup_required,
    total_errors,
    overall_score,
    execution_time
):
        """
        Logs overall workflow summary to the Summary worksheet.
        """

        self.summary.append_row([
            run_id,
            timestamp,
            scenario_id,
            model,
            patient_id,
            diagnosis,
            surgery_type,
            final_status,
            backup_required,
            total_errors,
            overall_score,
            execution_time
        ])

    def log_evaluation(
    self,
    run_id,
    model,
    response_latency,
    edge_efficiency,
    workflow_accuracy,
    security_accuracy,
    clinical_hallucination,
    operational_robustness,
    overall_score
):
        """
        Logs evaluation metrics to the Evaluation worksheet.
        """

        self.evaluation.append_row([
            run_id,
            model,
            response_latency,
            edge_efficiency,
            workflow_accuracy,
            security_accuracy,
            clinical_hallucination,
            operational_robustness,
            overall_score
        ])

    def log_workflow(
    self,
    timestamp,
    run_id,
    stage,
    event,
    result,
    duration
):
        """
        Logs workflow events to the Workflow Log worksheet.
        """

        self.workflow.append_row([
            timestamp,
            run_id,
            stage,
            event,
            result,
            duration
        ])

sheet_logger = GoogleSheetsLogger()
