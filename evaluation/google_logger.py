import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import statistics
import math

class GoogleSheetsLogger:

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def __init__(
        self,
        spreadsheet_name="Telesurgery Experiment Logs",
        credentials_path="credentials/service_account.json"
    ):

        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=self.SCOPES
        )

        client = gspread.authorize(creds)

        self.spreadsheet = client.open_by_key(
    "1tLd5AXfiaO0thImaIt9U2jxaxmkSaaf__K04N2tkx_0"
)

        self.summary = self.get_or_create_sheet("Summary")
        self.diagnosis = self.get_or_create_sheet("Diagnosis")
        self.security = self.get_or_create_sheet("Security")
        self.protocol = self.get_or_create_sheet("Protocol")
        self.feedback = self.get_or_create_sheet("Feedback")
        self.robot = self.get_or_create_sheet("Robot")
        self.workflow = self.get_or_create_sheet("Workflow_Output")
        self.statistics = self.get_or_create_sheet("Statistics")

        self.initialize_headers()

    #########################################################
    # Sheet Creation
    #########################################################

    def get_or_create_sheet(self, name):

        try:
            return self.spreadsheet.worksheet(name)

        except gspread.WorksheetNotFound:

            worksheet = self.spreadsheet.add_worksheet(
                title=name,
                rows=1000,
                cols=30
            )

            return worksheet

    #########################################################
    # Header Initialization
    #########################################################

    def initialize_headers(self):

        if self.summary.row_count > 0 and self.summary.cell(1, 1).value is None:
            self.summary.append_row([
                "Timestamp",
                "Run_ID",
                "Scenario_ID",
                "Model",
                "Diagnosis",
                "Security",
                "Protocol",
                "Feedback",
                "Robot",
                "Overall",
                "Weighted_Score",
                "Execution_Time"
            ])

        if self.diagnosis.cell(1, 1).value is None:
            self.diagnosis.append_row([
                "Run_ID",
                "Scenario_ID",
                "Prediction",
                "Ground_Truth",
                "Correct",
                "Score"
            ])

        if self.security.cell(1, 1).value is None:
            self.security.append_row([
                "Run_ID",
                "Scenario_ID",
                "Attack_Detected",
                "Expected_Attack",
                "Attack_Type",
                "Expected_Type",
                "Recommended_Action",
                "Expected_Action",
                "Score"
            ])

        if self.protocol.cell(1, 1).value is None:
            self.protocol.append_row([
                "Run_ID",
                "Scenario_ID",
                "Protocol",
                "Expected",
                "Correct",
                "Score"
            ])

        if self.feedback.cell(1, 1).value is None:
            self.feedback.append_row([
                "Run_ID",
                "Scenario_ID",
                "Action",
                "Expected",
                "Correct",
                "Score"
            ])

        if self.robot.cell(1, 1).value is None:
            self.robot.append_row([
                "Run_ID",
                "Scenario_ID",
                "Status",
                "Expected_Status",
                "Action",
                "Expected_Action",
                "Score"
            ])

        if self.workflow.cell(1, 1).value is None:
            self.workflow.append_row([
                "Run_ID",
                "Scenario_ID",
                "Doctor_Output",
                "Security_Output",
                "Protocol_Output",
                "Feedback_Output",
                "Robot_Output"
            ])

        if self.statistics.cell(1, 1).value is None:
            self.statistics.append_row([
                "Metric",
                "Value"
            ])

    #########################################################
    # Summary
    #########################################################

    def log_summary(
        self,
        run_id,
        scenario,
        evaluation,
        weighted_score,
        execution_time,
        model="Groq"
    ):

        self.summary.append_row([

            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            run_id,

            scenario["Scenario_ID"],

            model,

            evaluation["diagnosis"].score,

            evaluation["security"].score,

            evaluation["protocol"].score,

            evaluation["feedback"].score,

            evaluation["robot"].score,

            evaluation["overall_score"],

            weighted_score,

            execution_time

        ])

    #########################################################
    # Diagnosis
    #########################################################

    def log_diagnosis(
        self,
        run_id,
        scenario,
        diagnosis_eval
    ):

        self.diagnosis.append_row([

            run_id,

            scenario["Scenario_ID"],

            diagnosis_eval.predicted,

            diagnosis_eval.expected,

            diagnosis_eval.correct,

            diagnosis_eval.score

        ])

    #########################################################
    # Security
    #########################################################

    def log_security(
        self,
        run_id,
        scenario,
        security_eval
    ):

        self.security.append_row([

            run_id,

            scenario["Scenario_ID"],

            security_eval.predicted_attack_detected,

            security_eval.expected_attack_detected,

            security_eval.predicted_attack,

            security_eval.expected_attack,

            security_eval.predicted_action,

            security_eval.expected_action,

            security_eval.score

        ])

    #########################################################
    # Protocol
    #########################################################

    def log_protocol(
        self,
        run_id,
        scenario,
        protocol_eval
    ):

        self.protocol.append_row([

            run_id,

            scenario["Scenario_ID"],

            protocol_eval.predicted,

            protocol_eval.expected,

            protocol_eval.correct,

            protocol_eval.score

        ])

    #########################################################
    # Feedback
    #########################################################

    def log_feedback(
        self,
        run_id,
        scenario,
        feedback_eval
    ):

        self.feedback.append_row([

            run_id,

            scenario["Scenario_ID"],

            feedback_eval.predicted_action,

            feedback_eval.expected_action,

            feedback_eval.correct,

            feedback_eval.score

        ])

    #########################################################
    # Robot
    #########################################################

    def log_robot(
        self,
        run_id,
        scenario,
        robot_eval
    ):

        self.robot.append_row([

            run_id,

            scenario["Scenario_ID"],

            robot_eval.predicted_status,

            robot_eval.expected_status,

            robot_eval.predicted_action,

            robot_eval.expected_action,

            robot_eval.score

        ])

    #########################################################
    # Workflow Outputs
    #########################################################

    def log_workflow(
        self,
        run_id,
        scenario,
        workflow_result
    ):

        self.workflow.append_row([

            run_id,

            scenario["Scenario_ID"],

            json.dumps(workflow_result["doctor"].model_dump(), indent=2),

            json.dumps(workflow_result["security"].model_dump(), indent=2),

            json.dumps(workflow_result["protocol"].model_dump(), indent=2),

            json.dumps(workflow_result["feedback"].model_dump(), indent=2),

            json.dumps(workflow_result["robot"].model_dump(), indent=2)

        ])
        

    def update_statistics(self):

        print("===== update_statistics() called =====")

        records = self.summary.get_all_records()

        print(f"Records found: {len(records)}")

        print(records[:2])      # print first two rows

        self.statistics.append_row(["TEST", "123"])

        print("Reached end of function")

        records = self.summary.get_all_records()

        if len(records) == 0:
            return

        diagnosis = [float(r["Diagnosis"]) for r in records]
        security = [float(r["Security"]) for r in records]
        protocol = [float(r["Protocol"]) for r in records]
        feedback = [float(r["Feedback"]) for r in records]
        robot = [float(r["Robot"]) for r in records]
        overall = [float(r["Overall"]) for r in records]
        weighted = [float(r["Weighted_Score"]) for r in records]
        execution = [float(r["Execution_Time"]) for r in records]

        n = len(records)

        self.statistics.clear()

        self.statistics.append_row(["Metric", "Value"])

        stats = [
            ["Total Runs", n],

            ["Mean Diagnosis", statistics.mean(diagnosis)],
            ["Mean Security", statistics.mean(security)],
            ["Mean Protocol", statistics.mean(protocol)],
            ["Mean Feedback", statistics.mean(feedback)],
            ["Mean Robot", statistics.mean(robot)],

            ["Mean Overall", statistics.mean(overall)],
            ["Mean Weighted Score", statistics.mean(weighted)],
            ["Mean Execution Time", statistics.mean(execution)],

            ["Standard Deviation", statistics.stdev(overall) if n > 1 else 0],

            ["Minimum Overall", min(overall)],
            ["Maximum Overall", max(overall)],

            ["Success Rate (%)",
            sum(score >= 0.8 for score in overall) / n * 100]
        ]

        if n > 1:

            ci = 1.96 * statistics.stdev(overall) / math.sqrt(n)

            stats.append(["95% Confidence Interval Lower",
                        statistics.mean(overall) - ci])

            stats.append(["95% Confidence Interval Upper",
                        statistics.mean(overall) + ci])

        for row in stats:
            self.statistics.append_row(row)

    