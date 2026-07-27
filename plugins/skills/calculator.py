from .base import Skill

class CalculatorSkill:
    name = "calculator"

    def run(self, input: dict):
        expr = input.get("expression")
        if not expr:
            return {"error": "no expression provided"}
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
