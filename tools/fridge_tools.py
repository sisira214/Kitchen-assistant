import os
import csv
import datetime
from typing import List, Dict

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from dotenv import load_dotenv
from openai import OpenAI
import csv
import datetime

# -------------------- SETUP --------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FRIDGE_CSV_PATH = "C:/Users/sashi/OneDrive/Documents/mcp_a2a/Data/fridge.csv"
DATE_FMT = "%Y-%m-%d"


# -------------------- HELPERS --------------------

def load_fridge():
    with open(FRIDGE_CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_fridge(rows):
    with open(FRIDGE_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# -------------------- TOOLS --------------------

def get_fridge_inventory(state: dict | None = None, **kwargs):
    """
    Shares fridge inventory with other agents.
    Optional filters read from state.
    """
    if state is None:
        state = {}

    category = state.get("category")
    storage = state.get("storage_location")

    rows = load_fridge()

    if category:
        rows = [r for r in rows if r["category"].lower() == category.lower()]

    if storage:
        rows = [
            r for r in rows
            if r["storage_location"].lower() == storage.lower()
        ]

    state["fridge_inventory"] = rows
    return state


def find_expiring_items(state: dict | None = None, **kwargs):
    """
    Finds ingredients expiring within N days.
    Used by Waste Reduction Agent.
    """
    if state is None:
        state = {}

    days = state.get("expiry_window_days", 3)
    today = datetime.date.today()

    expiring = []
    skipped = []
    for r in load_fridge():
        raw_expiry = (r.get("expiry_date") or "").strip()

        # 🚑 HARD GUARD
        if raw_expiry in ("", "N/A", "NA", "null", "None"):
            skipped.append(r["ingredient_name"])
            continue

        try:
            expiry = datetime.datetime.strptime(
                raw_expiry, DATE_FMT
            ).date()
        except ValueError:
            skipped.append(r["ingredient_name"])
            continue

        if (expiry - today).days <= days:
            expiring.append(r)

    state["expiring_items"] = expiring
    state["expiry_skipped_items"] = skipped
    return state


def get_allergen_info(state: dict | None = None, **kwargs):
    """
    Returns allergen metadata for extracted ingredients.
    Used by Allergy & Safety Agent.
    """
    if state is None:
        state = {}

    ingredients = state.get("ingredients", [])
    rows = load_fridge()

    allergen_map = {}

    for ing in ingredients:
        for r in rows:
            if r["ingredient_name"].lower() == ing.lower():
                allergen_map[ing] = {
                    "allergens": r["allergens"],
                    "diet_tags": r["diet_tags"]
                }
                break

    state["ingredient_allergens"] = allergen_map
    return state


def update_inventory_after_use(state: dict | None = None, **kwargs):
    """
    Deducts quantities after recipe execution.
    Schema-safe and non-throwing.
    """
    if state is None:
        state = {}

    used_items = state.get("used_ingredients", [])
    rows = load_fridge()

    updated_items = []
    skipped_items = []

    for used in used_items:
        # ---- NORMALIZE NAME ----
        name = (
            used.get("ingredient")
            or used.get("ingredient_name")
            or used.get("name")
        )

        # ---- NORMALIZE QUANTITY ----
        qty = (
            used.get("quantity")
            or used.get("qty")
            or used.get("used_quantity")
        )

        if not name or qty is None:
            skipped_items.append(used)
            continue

        try:
            qty = float(qty)
        except (TypeError, ValueError):
            skipped_items.append(used)
            continue

        for r in rows:
            if r["ingredient_name"].lower() == name.lower():
                r["quantity"] = str(
                    max(0, float(r["quantity"]) - qty)
                )
                r["last_updated"] = datetime.date.today().strftime(DATE_FMT)
                updated_items.append(name)
                break

    if updated_items:
        save_fridge(rows)

    state["inventory_updated"] = updated_items
    state["inventory_update_skipped"] = skipped_items
    return state