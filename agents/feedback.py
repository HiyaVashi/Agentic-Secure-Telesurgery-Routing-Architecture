import json
from pathlib import Path
from config import csv_db
from langchain_core.prompts import PromptTemplate

from models import get_llm
from schemas.feedback_schema import FeedbackDecision


class FeedbackAgent:

    def __init__(self):
        self.llm = get_llm().with_structured_output(FeedbackDecision)

        prompt_path = Path("prompts/feedback.txt")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def evaluate(self, doctor_result, security_result, protocol_result):

        prompt = PromptTemplate.from_template(
            """
{system_prompt}

Doctor Assessment:
{doctor}

Security Assessment:
{security}

Protocol Decision:
{protocol}
"""
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "system_prompt": self.system_prompt,
                "doctor": doctor_result.model_dump_json(indent=4),
                "security": security_result.model_dump_json(indent=4),
                "protocol": protocol_result.model_dump_json(indent=4),
            }
        )

        return response