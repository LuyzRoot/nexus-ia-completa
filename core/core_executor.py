name=core/executor.py
"""
Executor seguro (limitado) para executar pequenas expressões/trechos Python.
IMPORTANTE: executar código arbitrário é perigoso. Este executor é intencionalmente restritivo:
- evaluate_expression(expression): aceita apenas expressões aritméticas e literais (numéricas, tuples, lists, dicts)
- run_script(...) is a placeholder that requires a controlled environment (not implemented by default)
Use python_executor tool only if you are confident about sandboxing (Docker, separate process, careful quotas).
"""
import ast
from typing import Any, Tuple

# Allowed AST node types for safe expression evaluation
_ALLOWED_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Num,
    ast.Constant,
    ast.operator,
    ast.unaryop,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.Load,
    ast.Tuple,
    ast.List,
    ast.Dict,
    ast.ListComp,
    ast.DictComp,
    ast.comprehension,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Call,  # we will disallow calls at runtime, but keep for safety checks
    ast.Name,  # names like True/False/None allowed only
}


class UnsafeExpressionError(Exception):
    pass


def _validate_expr_node(node: ast.AST):
    """
    Walk AST and ensure only allowed nodes present.
    Simple conservative check.
    """
    for n in ast.walk(node):
        if type(n) not in _ALLOWED_NODES:
            raise UnsafeExpressionError(f"Disallowed node type: {type(n).__name__}")
        # disallow names except True/False/None
        if isinstance(n, ast.Name):
            if n.id not in ("True", "False", "None"):
                raise UnsafeExpressionError(f"Disallowed name: {n.id}")
        # disallow function calls (dangerous)
        if isinstance(n, ast.Call):
            raise UnsafeExpressionError("Function calls are not allowed in safe evaluation")


def evaluate_expression(expression: str) -> Tuple[bool, Any]:
    """
    Evaluate a Python expression safely (very limited).
    Returns (ok, result_or_error_message).
    """
    try:
        tree = ast.parse(expression, mode="eval")
        _validate_expr_node(tree)
        # Use literal_eval as safer fallback (works for literals/tuples/dicts/lists)
        try:
            from ast import literal_eval
            result = literal_eval(tree)
            return True, result
        except Exception:
            # as a last resort, compile+eval in restricted namespace (no builtins)
            code = compile(tree, "<safe>", "eval")
            result = eval(code, {"__builtins__": {}}, {})
            return True, result
    except UnsafeExpressionError as e:
        return False, f"Unsafe expression: {e}"
    except Exception as e:
        return False, f"Evaluation error: {e}"


def run_script_untrusted(script: str, timeout_seconds: int = 5) -> Tuple[bool, str]:
    """
    Placeholder for running a full script in a sandboxed environment.
    Implement this with a separate process, container, or restricted runtime when enabling in production.
    Currently raises NotImplementedError to avoid accidental insecure execution.
    """
    raise NotImplementedError("run_script_untrusted is not implemented for safety. Use a secure sandbox.")