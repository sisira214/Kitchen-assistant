import os
import csv
import datetime
from typing import List, Dict

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from dotenv import load_dotenv
from openai import OpenAI
import csv
import datetime

from tools.fridge_tools import (
    get_fridge_inventory,
    find_expiring_items,
    get_allergen_info,
    update_inventory_after_use,
)

# -------------------- SETUP --------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FRIDGE_CSV_PATH = "C:/Users/sashi/OneDrive/Documents/mcp_a2a/Data/fridge.csv"
DATE_FMT = "%Y-%m-%d"





# -------------------- FRIDGE AGENT --------------------

fridge_agent = Agent(
    name="fridge_agent",
    description=(
        "Acts as a local fridge database. Shares inventory data, "
        "tracks expiry, allergens, and updates ingredient usage."
    ),
    model=LiteLlm(
        model="openai/gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    instruction="""
You are the Fridge Agent.

You DO NOT generate recipes or nutrition advice.
You ONLY:
- Read fridge inventory
- Share inventory data with other agents
- Update ingredient quantities after usage
- Identify expiring items
- Return allergen and diet metadata

Always rely on tools for inventory state.
Never hallucinate ingredients.
""",
    tools=[
        get_fridge_inventory,
        find_expiring_items,
        get_allergen_info,
        update_inventory_after_use,
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
)

agent = fridge_agent
# -------------------- A2A SERVER --------------------


