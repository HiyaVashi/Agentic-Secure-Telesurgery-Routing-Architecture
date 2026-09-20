import json

from agents.security import SecurityAgent
from models.llm import get_llm

llm = get_llm()

security = SecurityAgent(llm)

with open("traffic.json", "r") as f:
    traffic = json.load(f)

packets = traffic["packets"]

result = security.run(packets)

print(json.dumps(result, indent=4))