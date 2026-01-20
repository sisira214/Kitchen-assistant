from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

nutrition_agent = RemoteA2aAgent(
    name="nutrition_agent",
    description=(
        "An agent that provides nutritional information and advice based on user preferences and dietary needs."
    ),
    agent_card=f"https://flnjrhgv-8001.use.devtunnels.ms/{AGENT_CARD_WELL_KNOWN_PATH}",
)