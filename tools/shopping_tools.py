# ---------------- AGENT 2 DEFINITION ----------------
# After getting the ingredients that are not present in fridge we can call another agent to suggest nearby stores to buy those ingredients from. I have ingredients data in 
# form of csv file which contains the following columns: ingredient,store,price_per_unit,unit example data is rice,Walmart,1.2,grams
import pandas as pd

INGREDIENTS_CSV_PATH = "C:/Users/sashi/OneDrive/Documents/recipeAgent/Data/ingredients.csv"



def load_ingredient_prices():
    return pd.read_csv(INGREDIENTS_CSV_PATH).to_dict(orient="records")




# ---------------- AGENT 2 TOOL ----------------

def add_missing_ingredients_to_cart(state: dict | None = None, **kwargs):
    """
    Agent 2: Market / Ingredient Purchase Agent

    Input (from Agent 1):
        state["missing_ingredients"] = [
            {"ingredient": "rice", "quantity": "200", "unit": "grams"}
        ]

    Output:
        state["cart"]
        state["total_cart_cost"]
    """

    # If nothing is missing, no need to shop
    if state is None:
        state = {}

    if state.get("missing_ingredients") is None:
        state["missing_ingredients"] = []

    if not state.get("missing_ingredients"):
        state["cart"] = []
        state["total_cart_cost"] = 0.0
        return state


    prices = load_ingredient_prices()

    cart = []
    total_cost = 0.0

    for item in state["missing_ingredients"]:
        ingredient = item["ingredient"]
        quantity = float(item["quantity"])
        unit = item["unit"]

        matches = [
            p for p in prices
            if p["ingredient"] == ingredient and p["unit"] == unit
        ]

        if not matches:
            continue

        best_option = min(matches, key=lambda x: float(x["price_per_unit"]))
        price_per_unit = float(best_option["price_per_unit"])
        cost = quantity * price_per_unit

        cart.append({
            "ingredient": ingredient,
            "store": best_option["store"],
            "quantity": quantity,
            "unit": unit,
            "price_per_unit": price_per_unit,
            "cost": round(cost, 2)
        })

        total_cost += cost

    state["cart"] = cart
    state["total_cart_cost"] = round(total_cost, 2)
    return state

# ---------------- OPTIONAL SUMMARY TOOL ----------------

def summarize_cart(state: dict | None = None, **kwargs):
    """
    Generates a human-readable cart summary.
    """

    if state is None:
        state = {}

    cart = state.get("cart", [])

    if not cart:
        state["cart_summary"] = "🛒 No ingredients need to be purchased."
        state["total_cart_cost"] = 0.0
        return state

    total_cost = state.get("total_cart_cost", 0.0)

    summary = "🛒 Ingredients added to cart:\n"

    for item in cart:
        summary += (
            f"- {item['ingredient']} from {item['store']}: "
            f"{item['quantity']} {item['unit']} × "
            f"{item['price_per_unit']} = ${item['cost']}\n"
        )

    summary += f"\n💰 Total Cost: ${total_cost}"

    state["cart_summary"] = summary
    state["total_cart_cost"] = total_cost
    return state