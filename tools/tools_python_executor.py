"""
Safe expression evaluator wrapper around core.executor.evaluate_expression.
Only evaluate simple expressions (arithmetic, literals). DO NOT run run_script_untrusted here.
- evaluate_expression(expression) -> {"ok": bool, "result" | "error"}
"""
import logging

logger = logging.getLogger("tools.python_executor")

try:
    from core.executor import evaluate_expression, run_script_untrusted  # type: ignore
except Exception:
    # provide a minimal fallback if core.executor is not present
    def evaluate_expression(expr: str):
        return False, "core.executor not available"

    def run_script_untrusted(script: str, timeout_seconds: int = 5):
        raise NotImplementedError("run_script_untrusted not available")

async def evaluate_expression_async(expression: str):
    ok, result = evaluate_expression(expression)
    if ok:
        return {"ok": True, "result": result}
    return {"ok": False, "error": result}