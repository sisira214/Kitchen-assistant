from google.adk.agents.llm_agent import Agent

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import os
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- CONFIG ----------------

RECIPE_CSV_PATH = "C:/Users/sashi/OneDrive/Documents/langgraphProjects/a2aRecipie/Data/recipies.csv"
INGREDIENTS_CSV_PATH = "C:/Users/sashi/OneDrive/Documents/langgraphProjects/a2aRecipie/Data/ingredients.csv"

FRIDGE_CSV_PATH = "C:/Users/sashi/OneDrive/Documents/langgraphProjects/a2aRecipie/Data/fridge.csv"


# ---------------- DATA ----------------

def load_recipe_db():
    df = pd.read_csv(RECIPE_CSV_PATH)

    recipes = []
    for _, row in df.iterrows():
        # Ensure no missing fields
        ingredients = [i.strip().lower() for i in str(row.get("ingredients", "")).split(",") if i]
        dietary = [d.strip().lower() for d in str(row.get("dietary", "none")).split(",") if d]
        cuisine = str(row.get("cuisine", "")).strip().lower()
        cooking_time = int(row.get("cooking_time", 999))

        # Provide default quantities and units if missing
        quantities = str(row.get("ingredient_quantities", "")).split(",")
        if len(quantities) != len(ingredients):
            quantities = ["1"] * len(ingredients)  # default 1

        units = str(row.get("ingredient_units", "")).split(",")
        if len(units) != len(ingredients):
            units = ["unit"] * len(ingredients)  # default "unit"

        recipes.append({
            "name": str(row.get("name", "Unknown")),
            "ingredients": ingredients,
            "dietary": dietary,
            "cuisine": cuisine,
            "cooking_time": cooking_time,
            "ingredient_quantities": quantities,
            "ingredient_units": units,
        })
    return recipes


def load_fridge_inventory():
    df = pd.read_csv(FRIDGE_CSV_PATH)

    fridge = {}
    for _, row in df.iterrows():
        name = str(row["ingredient_name"]).strip().lower()
        fridge[name] = {
            "quantity": float(row.get("quantity", 0)),
            "unit": str(row.get("unit", "")).strip(),
            "expiry_date": str(row.get("expiry_date", "")),
            "category": str(row.get("category", "")),
            "storage_location": str(row.get("storage_location", "")),
            "allergens": str(row.get("allergens", "")),
            "diet_tags": [d.strip().lower() for d in str(row.get("diet_tags", "")).split(",") if d],
            "last_updated": str(row.get("last_updated", "")),
            "source": str(row.get("source", "")),
        }
    return fridge



def get_user_text(state) -> str:
    if not state:
        return ""

    if isinstance(state, dict) and state.get("input"):
        return str(state["input"]).lower()

    messages = state.get("messages", [])
    if messages:
        last = messages[-1]
        if isinstance(last, dict):
            return str(last.get("content", "")).lower()

    return ""


# ---------------- TOOLS (ORDER UNCHANGED) ----------------

def extract_ingredients(state: dict | None = None, **kwargs):
    if state is None:
        state = {}

    text = get_user_text(state)
    fridge = load_fridge_inventory()

    state["ingredients"] = [ing for ing in fridge.keys() if ing in text]
    state["fridge_inventory"] = fridge
    return state



def extract_preferences(state: dict | None = None, **kwargs):
    if state is None:
        state = {}
    text = get_user_text(state)

    dietary = []
    if "vegetarian" in text:
        dietary.append("vegetarian")
    if "vegan" in text:
        dietary.append("vegan")

    # If no dietary preference is given, default to 'none'
    if not dietary:
        dietary = ["none"]

    time_match = re.search(r"(\d+)\s*minutes?", text)

    state["dietary_restrictions"] = dietary
    state["max_cooking_time"] = int(time_match.group(1)) if time_match else 999
    state["cuisine_preference"] = (
        "indian" if "indian" in text else
        "italian" if "italian" in text else
        "asian" if "asian" in text else ""
    )
    return state


def search_recipes(state: dict | None = None, **kwargs):
    if state is None:
        state = {}
    recipes = load_recipe_db()

    state_ing = set(state.get("ingredients", []))
    state_diet = set(state.get("dietary_restrictions", ["none"]))
    cuisine = state.get("cuisine_preference", "").lower()
    max_time = state.get("max_cooking_time", 999)

    results = []

    for r in recipes:
        if r["cooking_time"] > max_time:
            continue
        if state_diet and not state_diet.issubset(set(r["dietary"])):
            continue
        if state_ing and set(r["ingredients"]).isdisjoint(state_ing):
            continue
        if cuisine and r["cuisine"] != cuisine:
            continue
        results.append(r)

    state["matched_recipes"] = results
    return state


def rank_recipes(state: dict | None = None, **kwargs):
    if state is None:
        state = {}
    recipes = state.get("matched_recipes", [])
    recipes.sort(
        key=lambda r: len(set(r["ingredients"]).intersection(state.get("ingredients", []))),
        reverse=True
    )
    state["matched_recipes"] = recipes
    return state


def check_fridge_availability(state: dict | None = None, **kwargs):
    if state is None:
        state = {}

    if not state.get("matched_recipes"):
        state["missing_ingredients"] = []
        return state

    fridge = state.get("fridge_inventory", {})
    recipe = state["matched_recipes"][0]

    missing = []

    for ing, qty, unit in zip(
        recipe["ingredients"],
        recipe["ingredient_quantities"],
        recipe["ingredient_units"]
    ):
        fridge_item = fridge.get(ing)

        if not fridge_item or fridge_item["quantity"] <= 0:
            missing.append({
                "ingredient": ing,
                "required_quantity": qty,
                "unit": unit,
                "reason": "not_in_fridge"
            })

    state["missing_ingredients"] = missing
    return state



def generate_recommendation(state: dict | None = None, **kwargs):
    if state is None:
        state = {}
    if not state.get("matched_recipes"):
        state["response"] = "❌ No recipes found matching your preferences."
        return state

    r = state["matched_recipes"][0]

    response = (
        f"🍛 {r['name']}\n"
        f"🌍 Cuisine: {r['cuisine'].title()}\n"
        f"⏱ {r['cooking_time']} minutes\n\n"
        f"Ingredients:\n"
    )

    for i, q, u in zip(r["ingredients"], r["ingredient_quantities"], r["ingredient_units"]):
        response += f"- {i}: {q} {u}\n"

    state["selected_recipe"] = r
    state["response"] = response
    return state


def generate_cooking_steps_llm(state: dict | None = None, **kwargs) -> str:
    if state is None:
        state = {}

    # Pick first matched recipe if nothing is explicitly selected
    recipe = state.get("selected_recipe") or (state.get("matched_recipes") or [None])[0]

    if not recipe:
        return "❌ No recipe available to generate cooking steps."

    ingredient_text = "\n".join(
        [
            f"- {i}: {q} {u}"
            for i, q, u in zip(
                recipe["ingredients"],
                recipe.get("ingredient_quantities", ["1"] * len(recipe["ingredients"])),
                recipe.get("ingredient_units", ["unit"] * len(recipe["ingredients"])),
            )
        ]
    )

    prompt = f"""
You are a professional chef.

Generate step-by-step cooking instructions for the following recipe.

STRICT RULES:
- Use ONLY the ingredients listed below
- Do NOT add or assume any extra ingredients
- Do NOT mention ingredients not listed
- Follow Indian cooking style if cuisine is Indian
- Provide clear numbered steps

Recipe Name: {recipe['name']}
Cuisine: {recipe['cuisine']}
Cooking Time: {recipe['cooking_time']} minutes

Ingredients:
{ingredient_text}

Output only the cooking steps.
"""

    response = client.chat.completions.create(
        model="gpt-4o-msini",
        messages=[
            {"role": "system", "content": "You generate cooking instructions from structured data only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3
    )

    steps = response.choices[0].message.content.strip()

    return f"""
🍽️ Recipe: {recipe['name']}
🌍 Cuisine: {recipe['cuisine']}
⏱️ Cooking Time: {recipe['cooking_time']} minutes

🧾 Ingredients:
{ingredient_text}

👩‍🍳 Cooking Instructions:
{steps}
"""