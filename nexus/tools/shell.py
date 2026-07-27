import subprocess
import logging

logger = logging.getLogger(__name__)

class ShellTool:
    """Shell script execution"""
    
    async def execute(self, script: str, shell: str = "/bin/bash") -> dict:
        """Execute shell script"""
        try:
            result = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                executable=shell
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Script timeout"}
        except Exception as e:
            logger.error(f"Shell error: {e}")
            return {"error": str(e)}
