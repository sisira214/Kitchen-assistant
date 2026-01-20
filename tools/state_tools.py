from __future__ import annotations

from typing import Any, Dict, List, Optional

from state.session_store import sessionize

def select_recipe(recipe_name: str, session_id: str = "default", session=None) -> Dict[str, Any]:
    sess = sessionize(session=session, session_id=session_id)
    sess.state["selected_recipe"] = recipe_name
    return {"status": "success", "selected_recipe": recipe_name}

def get_selected_recipe(session_id: str = "default", session=None) -> Dict[str, Any]:
    sess = sessionize(session=session, session_id=session_id)
    return {"status": "success", "selected_recipe": sess.state.get("selected_recipe")}

def update_pantry(items: List[str], session_id: str = "default", session=None) -> Dict[str, Any]:
    sess = sessionize(session=session, session_id=session_id)
    pantry = set(sess.state.get("pantry", []))
    for x in items:
        if x and str(x).strip():
            pantry.add(str(x).strip().lower())
    sess.state["pantry"] = sorted(pantry)
    return {"status": "success", "pantry": sess.state["pantry"]}

def compute_missing_ingredients(
    recipe_ingredients: List[str],
    session_id: str = "default",
    session=None
) -> Dict[str, Any]:
    sess = sessionize(session=session, session_id=session_id)
    pantry = set(sess.state.get("pantry", []))
    missing = [i for i in recipe_ingredients if i not in pantry]
    sess.state["missing_ingredients"] = missing
    return {"status": "success", "missing_ingredients": missing}
