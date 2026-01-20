

# mcp_server/servers/uvicorn_server.py

from google.adk.a2a.utils.agent_to_a2a import to_a2a

# NOTE: fix the typo if your file is nutrition_agent.py (not nutition_agent.py)
from agents.fridge_agent import agent as fridge_agent

a2a_app = to_a2a(fridge_agent, port=8001)