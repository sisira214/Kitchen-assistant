# ---------------- AGENT 3 DEFINITION ----------------
# Wallet Management Agent. This agent can help user manage their budget for grocery shopping based on their total cart cost from Agent 2. 

# ---------------- AGENT 3: WALLET MANAGEMENT AGENT ----------------
from state.session_store import sessionize
from agents.fridge_agent import load_fridge, save_fridge





# Fixed wallet credentials
VALID_USER_ID = "0101"
VALID_PASSWORD = "wallet"

# Initial wallet balance
WALLET_BALANCE = 20000.0





def wallet_agent(state: dict | None = None, **kwargs) -> dict:
    """
    Wallet Management Agent

    Input (from Agent 2 / User):
        state["total_cart_cost"]       : float
        state["user_id"]               : str
        state["password"]              : str
        state["confirm_payment"]       : bool

    Output:
        state["transaction_status"]    : str
        state["remaining_balance"]     : float (if successful)
    """

    global WALLET_BALANCE

    if state is None:
        state = {}

    # Inject default credentials automatically if missing
    if "user_id" not in state:
        state["user_id"] = VALID_USER_ID
    if "password" not in state:
        state["password"] = VALID_PASSWORD
    if "confirm_payment" not in state:
        state["confirm_payment"] = True

    total_cost = state.get("total_cart_cost", 0.0)
    user_id = state["user_id"]
    password = state["password"]
    confirm = state["confirm_payment"]

    # No cart cost
    if total_cost <= 0.0:
        state["transaction_status"] = "NO_CART"
        return state

    # Authentication check
    if user_id != VALID_USER_ID or password != VALID_PASSWORD:
        state["transaction_status"] = "FAILED_AUTH"
        return state

    # Payment confirmation
    if not confirm:
        state["transaction_status"] = "CANCELLED"
        return state

    # Check wallet balance
    if WALLET_BALANCE < total_cost:
        state["transaction_status"] = "INSUFFICIENT_FUNDS"
        return state

    # Deduct the amount
    WALLET_BALANCE -= total_cost

    state["transaction_status"] = "SUCCESS"
    state["remaining_balance"] = WALLET_BALANCE

    return state

import datetime

DATE_FMT = "%Y-%m-%d"

def update_inventory_after_purchase(state: dict | None = None, **kwargs):
    """
    Adds purchased items to fridge inventory after a successful order.
    """
    if state is None:
        state = {}

    rows = load_fridge()
    today = datetime.date.today().strftime(DATE_FMT)

    # -------- COLLECT PURCHASED ITEMS --------
    purchased = []

    # cheapest_split strategy
    for block in state.get("purchase_breakdown", []):
        for item in block.get("items", []):
            purchased.append(item)

    # single_store strategy
    details = state.get("purchase_details")
    if details:
        purchased.extend(details.get("items", []))

    added = []
    skipped = []

    for item in purchased:
        name = (
            item.get("ingredient")
            or item.get("ingredient_name")
            or item.get("name")
        )

        unit = item.get("unit", "")
        quantity = float(item.get("quantity", 1))  # default = 1 unit

        if not name:
            skipped.append(item)
            continue

        # -------- UPDATE OR INSERT --------
        found = False
        for r in rows:
            if r["ingredient_name"].lower() == name.lower():
                r["quantity"] = str(float(r["quantity"]) + quantity)
                r["last_updated"] = today
                r["source"] = "purchased"
                found = True
                break

        if not found:
            rows.append({
                "ingredient_name": name,
                "quantity": str(quantity),
                "unit": unit,
                "expiry_date": "N/A",
                "category": "Uncategorized",
                "storage_location": "Pantry",
                "allergens": "",
                "diet_tags": "",
                "last_updated": today,
                "source": "purchased",
            })

        added.append(name)

    if added:
        save_fridge(rows)

    state["inventory_purchase_added"] = added
    state["inventory_purchase_skipped"] = skipped
    return state


def wallet_get_ledger(last_n: int = 10, session_id: str = "default", session=None) -> Dict[str, Any]:
    sess = sessionize(session=session, session_id=session_id)
    _wallet_init(sess)

    try:
        n = int(last_n)
    except Exception:
        n = 10
    n = max(1, min(n, 100))

    tx = sess.state.get("wallet_ledger", [])
    return {"status": "success", "count": min(len(tx), n), "transactions": tx[-n:]}

