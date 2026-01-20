import os
from dotenv import load_dotenv

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.llm_agent import Agent

from tools.shopping_tools import (
    load_ingredient_prices,
    add_missing_ingredients_to_cart,
    summarize_cart,
)

#from tools.shopping_tools import get_market_prices, recommend_purchase_plan
from tools.state_tools import get_selected_recipe, compute_missing_ingredients, update_pantry

llm = LiteLlm(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

missing_items_toCart_agent = None
try:
    missing_items_toCart_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=LiteLlm(model="openai/gpt-4o-mini",api_key=os.getenv("OPENAI_API_KEY")),# Use LiteLlm to specify the model name,
    name='missing_items_toCart_agent',
    description="Tells the missing ingredients to shopping cart with prices",
    instruction="""
You are a Shopping Cart Agent. You help users add missing ingredients to their shopping cart and summarize the total cost.
Follow these internal steps:
1. load_ingredient_prices() - Load the ingredient prices from CSV.
2. add_missing_ingredients_to_cart(state) - Add missing ingredients to shopping carrt with prices based on ingredient prices.
3. summarize_cart(state) - Summarize the shopping cart with total cost.

Input:
- missing_ingredients from Recipe Agent

Output:
- cart
- total_cart_cost


Do not make up recipes or ingredients not in the database.The agent should use the tools in the specified order to process user requests effectively.
""",
    tools=[
    load_ingredient_prices, add_missing_ingredients_to_cart, summarize_cart
],
    )
    print(f"✅ Agent '{missing_items_toCart_agent.name}' created using model '{missing_items_toCart_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({missing_items_toCart_agent.model}). Error: {e}")


agent = missing_items_toCart_agent
