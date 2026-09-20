from schemas.robotic_schema import RoboticResponse

from config import csv_db
class RoboticAgent:

    def execute(self, feedback_result):

        if feedback_result.proceed:

            return RoboticResponse(
                status="SUCCESS",
                action="Executing Surgery",
                message="Robotic arm has started the procedure."
            )

        elif feedback_result.action.lower() == "pause":

            return RoboticResponse(
                status="PAUSED",
                action="Pause Surgery",
                message="Waiting for network recovery."
            )

        else:

            return RoboticResponse(
                status="ABORTED",
                action="Abort Surgery",
                message="Emergency stop activated."
            )