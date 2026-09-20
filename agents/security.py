import json
from pathlib import Path
from config import csv_db
from langchain_core.prompts import PromptTemplate

from models import get_llm
from schemas.security_schema import SecurityAssessment


class SecurityAgent:

    def __init__(self):
        self.llm = get_llm().with_structured_output(SecurityAssessment)

        prompt_path = Path("prompts/security.txt")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def analyse(self, network_data):

        prompt = PromptTemplate.from_template(
            """
{system_prompt}

Network Information:

{network_data}
"""
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "system_prompt": self.system_prompt,
                "network_data": json.dumps(network_data, indent=4)
            }
        )

        return response