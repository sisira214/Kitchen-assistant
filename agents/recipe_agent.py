import os
from dotenv import load_dotenv

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.llm_agent import Agent

from tools.recipe_tools import (
    extract_ingredients,            
    extract_preferences,
    search_recipes,
    rank_recipes,
    check_fridge_availability,
    generate_recommendation,
    generate_cooking_steps_llm,
)

#from tools.shopping_tools import get_market_prices, recommend_purchase_plan
from tools.state_tools import get_selected_recipe, compute_missing_ingredients, update_pantry

llm = LiteLlm(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

recipe_agent = Agent(
    name="recipe_recommender_agent",
    model=llm,
    description="Recommends recipes from CSV only",
    tools=[
        extract_ingredients,
        extract_preferences,
        search_recipes,
        rank_recipes,
        check_fridge_availability,
        generate_recommendation,
        generate_cooking_steps_llm,
    ],
    instruction="""
You are a Recipe Recommendation Agent. You help users find recipes based on ingredients and dietary preferences.
Follow these internal steps:
1. load_recipe_db() - Load the recipe database from CSV.
2. extract_ingredients(state) - Find ingredients mentioned in the user message.
3. extract_preferences(state) - Extract dietary restrictions, max cooking time, and cuisine preferences.
4. search_recipes(state) - Find matching recipes in the database.
5. Check_fridge_availability(state) - Identify missing ingredients from the fridge.
6. rank_recipes(state) - Order recipes by relevance.
7. generate_recommendation(state) - Create a detailed recipe recommendation response.
8. generate_cooking_steps_llm(recipe) - Generate cooking steps for the selected recipe.

CRITICAL RULES:
- You MUST call tools to compute the answer
- You MUST return the exact text from state["response"]
- You are NOT allowed to say "sorry" or invent explanations
- If matched_recipes is empty, say so ONLY via generate_recommendation


Output MUST include:
- matched_recipes
- missing_ingredients

Only answer recipe-related queries.
Do not invent recipes or ingredients.
Use only the CSV database.

Only answer recipe-related queries. Do not make up recipes or ingredients not in the database.The agent should use the tools in the specified order to process user requests effectively.It should take into account dietary restrictions, cooking time, and cuisine preferences when recommending recipes. agent should respond in a friendly and helpful manner, providing clear instructions or suggestions based on the user's input.  Agent should not make up any recipes or ingredients that are not present in the database. It should provide the recipie in detail.
"""
)

agent = recipe_agent
