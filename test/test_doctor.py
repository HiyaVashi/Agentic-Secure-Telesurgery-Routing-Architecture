from models.llm import get_llm
from agents.doctor import DoctorAgent
import json

llm = get_llm()

doctor = DoctorAgent(llm)

with open("diagnosis.json") as f:
    diagnosis = json.load(f)[0]

result = doctor.run(diagnosis)

print(result)