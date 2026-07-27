import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TerminalTool:
    """Execute terminal commands"""
    
    async def execute(self, command: str, cwd: str = None) -> dict:
        """Execute shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timeout"}
        except Exception as e:
            logger.error(f"Terminal error: {e}")
            return {"error": str(e)}
