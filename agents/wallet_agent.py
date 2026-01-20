import os
from dotenv import load_dotenv

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.llm_agent import Agent

from tools.wallet_tools import wallet_agent, update_inventory_after_purchase

load_dotenv()

llm = LiteLlm(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

wallet_management_agent = None
try:
    wallet_management_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=LiteLlm(model="openai/gpt-4o-mini",api_key=os.getenv("OPENAI_API_KEY")), # Use LiteLlm to specify the model name,
    name='rwallet_management_agent',
    description="Allows user to manage their wallet for grocery shopping",
    instruction="""
You are a Wallet Management Agent. You help users to order missing items by getting the total cost from agent 2.
Follow these internal steps:
1. wallet_agent(state) - Manage wallet balance and process payment for the shopping cart.
2. update_inventory_after_purchase(state) - Update fridge inventory after successful purchase.

Input:
- total_cart_cost from Cart Agent

Authenticate user and process payment.

The agent should use the tools in the specified order to process user requests effectively. 
""",
    tools=[
    wallet_agent, update_inventory_after_purchase
],
    )
    print(f"✅ Agent  created using model ''.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({wallet_management_agent.model}). Error: {e}")
    
agent = wallet_management_agent
