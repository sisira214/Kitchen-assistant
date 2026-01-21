
# Kitchen Assistant – Multi-Agent System using Google ADK

A stateful, multi-agent kitchen assistant built with **Google ADK**, exposing selected capabilities via an **MCP server** so multiple users (or agents) can interact with each other’s agents.  

The system supports:

- 🍳 **Recipe recommendation**  
- 🛒 **Ingredient shopping**  
- 💰 **Wallet-based checkout simulation**

---

## 🏗️ Core Design Principles

- **RootAgent**: Pure orchestrator (no tools)  
- **Sub-agents**: Own tools and logic  
- **Stateful tools**: Manage selections, pantry, and wallet  
- **Stateless tools**: Handle extraction, search, and ranking  
- **SequentialAgent**: Used where execution order matters (e.g., checkout)  

---

## 🧩 Agents

| Agent | Responsibility |
|-------|----------------|
| **RootAgent** | Routes user intent to the correct sub-agent |
| **RecipeAgent** | Extracts preferences, searches & recommends recipes |
| **ShoppingAgent** | Computes missing ingredients & shopping plans |
| **WalletPayAgent** | Simulates wallet payment lifecycle |
| **CheckoutFlow** | Sequential flow: Shopping → Wallet |

---

## 📁 Project Structure

```text
Kitchen-assistant/
├── Data/
│   ├── fridge.csv
│   ├── ingredients.csv
│   └── recipies.csv
├── agents/
│   ├── root_agent.py
│   ├── recipe_agent.py
│   ├── shopping_agent.py
│   ├── wallet_agent.py
│   ├── checkout_flow.py
│   └── ...
├── servers/
│   ├── fridge_uvicorn.py
├── state/
├── tools/
├── requirements.txt
└── .env.example
````

---

## ⚙️ Installation

1. **Create and activate a virtual environment** (recommended)

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set environment variables**
   Create a `.env` file and add:

```env
OPENAI_API_KEY=your_openai_key_here
RECIPE_CSV_PATH
INGREDIENTS_CSV_PATH
FRDIGE_CSV_PATH
```

---

## 🚀 Running the Agents (Web Interface)

1. Open a terminal in the project folder.
2. Start the ADK web interface on port `8010`:

```bash
adk web --port 8010
```

3. Open your browser and go to [http://localhost:8010](http://localhost:8010).
4. Select the agents you want to run (RootAgent, RecipeAgent, ShoppingAgent, etc.) from the ADK dashboard.
5. RootAgent will automatically route requests to the correct sub-agents.

> ✅ This approach allows multiple users or agents to interact through the MCP server.

---

## 🔄 Stateful vs Stateless Tools

**Stateless Tools**

* Pure computation
* Safe to retry
* No memory
* Examples: `extract_ingredients_from_text`, `search_recipes`, `rank_recipes`

**Stateful Tools**

* Read/write session state
* Affect future behavior

---

## 🧪 Known Limitations

* In-memory session state (resets on restart)
* Mock shopping inventory
* Simulated wallet (no real payments)
* Single-process concurrency only

---

## 📌 Why This Design is ADK-Aligned

* No private ADK internals used
* RootAgent handles orchestration only
* SequentialAgent used only where order matters
* Clean separation of tools vs agents
* MCP isolated from agent logic

---

## 📜 License

This project is licensed under the **MIT License**. 

```

Do you want me to add that?
```
