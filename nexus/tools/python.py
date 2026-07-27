import logging

logger = logging.getLogger(__name__)

class PythonTool:
    """Execute Python code"""
    
    async def execute(self, code: str) -> dict:
        """Execute Python code safely"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout"}
        except Exception as e:
            logger.error(f"Python execution error: {e}")
            return {"error": str(e)}
