import os
from dotenv import load_dotenv

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.llm_agent import Agent

from agents.recipe_agent import recipe_agent
from agents.shopping_agent import missing_items_toCart_agent as shopping_agent
from agents.wallet_agent import wallet_management_agent as wallet_pay_agent 
from agents.checkout_flow import agent as checkout_flow_agent
from agents.fridge_agent import fridge_agent

load_dotenv()

from google.adk.a2a.utils.agent_to_a2a import to_a2a



root_agent = Agent(
    name="RootAgent",
    model=LiteLlm(model="openai/gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
    description="Orchestrator: routes user requests to RecipeAgent, ShoppingAgent, WalletPayAgent, or CheckoutFlow.",
    instruction=(
        "You are RootAgent (router).\n"
        "Decide which sub-agent should handle the user:\n"
        "- Recipe queries -> RecipeAgent\n"
        "- fridge inventory -> FridgeAgent\n"
        "- Checkout (buy+pay) -> CheckoutFlow\n"
        "Delegate; do not call tools yourself.\n"
        "Keep responses short and action-focused.\n"
    ),
    sub_agents=[
        recipe_agent,
        fridge_agent,
        checkout_flow_agent,
    ],
)

agent = root_agent

# Make your agent A2A-compatible
a2a_app = to_a2a(root_agent, port=8005)