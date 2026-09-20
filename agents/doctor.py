import json
from pathlib import Path
from config import csv_db
from langchain_core.prompts import PromptTemplate
from config import csv_db
from datetime import datetime
import uuid
from models import get_llm
from schemas.doctor_schema import DoctorDiagnosis
from utils.logger import get_logger

logger = get_logger(__name__)


class DoctorAgent:

    def __init__(self):
        self.llm = get_llm().with_structured_output(DoctorDiagnosis)

        prompt_path = Path("prompts/doctor.txt")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

        logger.info("Doctor Agent initialized.")

    def diagnose(self, patient_data):

        logger.info(
            f"Generating diagnosis for patient {patient_data['patient_id']}"
        )

        prompt = PromptTemplate.from_template(
            """
{system_prompt}

Patient Information:

{patient_data}
"""
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "system_prompt": self.system_prompt,
                "patient_data": json.dumps(patient_data, indent=4)
            }
        )

        logger.info("Diagnosis completed successfully.")

        return response

