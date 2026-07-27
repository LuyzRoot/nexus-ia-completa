"""
Simple calculator wrapper — uses core.executor.evaluate_expression for safety.
Provides calculate_expression(expression) -> dict
"""
import logging

logger = logging.getLogger("tools.calculator")

try:
    from core.executor import evaluate_expression  # type: ignore
except Exception:
    def evaluate_expression(expr: str):
        return False, "core.executor not available"

async def calculate_expression(expression: str):
    ok, result = evaluate_expression(expression)
    if ok:
        return {"expression": expression, "result": result}
    return {"expression": expression, "error": str(result)}