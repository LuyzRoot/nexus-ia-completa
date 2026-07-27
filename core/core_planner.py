name=core/planner.py
"""
Planning helpers: attempt to create an actionable plan from a user goal.
Tries to call the LLM if available; otherwise uses a deterministic heuristic split.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger("core.planner")

try:
    from core.llm import llm_router  # try to reuse the router we created earlier
    _HAS_LLM = True
except Exception:
    llm_router = None
    _HAS_LLM = False


async def generate_plan(goal: str, steps: int = 5) -> Dict[str, Any]:
    """
    Returns a dict with 'goal' and 'steps': list of {'title', 'detail'}.
    If LLM available, prompts it for a plan. Otherwise returns a heuristic plan.
    """
    if _HAS_LLM and llm_router:
        system = {"role": "system", "content": "You are a planner that decomposes a goal into actionable steps, concise and ordered."}
        user = {"role": "user", "content": f"Goal: {goal}\nPlease output a JSON array of {steps} steps with title and description."}
        try:
            resp = await llm_router.generate([system, user], temperature=0.1)
            # Try to parse JSON from resp.text
            import json
            try:
                parsed = json.loads(resp.text)
                return {"goal": goal, "steps": parsed}
            except Exception:
                # fallback to plain text splitting
                logger.debug("Planner: LLM returned non-JSON, using fallback parsing")
        except Exception as exc:
            logger.warning("Planner LLM call failed: %s", exc)

    # Heuristic fallback: split sentences and generate short tasks
    import re
    sentences = [s.strip() for s in re.split(r"[.!?\n]+", goal) if s.strip()]
    steps_out = []
    for i in range(min(steps, max(1, len(sentences)))):
        title = f"Step {i+1}"
        detail = sentences[i] if i < len(sentences) else f"Subtask {i+1} for goal"
        steps_out.append({"title": title, "detail": detail})
    # pad if necessary
    while len(steps_out) < steps:
        idx = len(steps_out) + 1
        steps_out.append({"title": f"Step {idx}", "detail": "Further refinement required."})
    return {"goal": goal, "steps": steps_out}