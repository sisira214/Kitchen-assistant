try:
    from google.adk.agents.sequential_agent import SequentialAgent
except Exception:
    SequentialAgent = None  # fallback if not available

from agents.shopping_agent import missing_items_toCart_agent as shopping_agent
from agents.wallet_agent import wallet_management_agent as wallet_pay_agent

if SequentialAgent is None:
    # Fallback: export ShoppingAgent as entry (not ideal, but avoids import crash)
    agent = shopping_agent
else:
    checkout_flow = SequentialAgent(
        name="CheckoutFlow",
        sub_agents=[shopping_agent, wallet_pay_agent],
        description="Sequential checkout: first plan purchase, then pay via wallet.",
    )
    agent = checkout_flow
