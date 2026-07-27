import logging
import subprocess

logger = logging.getLogger(__name__)

class DockerTool:
    """Docker operations"""
    
    async def run(self, image: str, command: str = None) -> dict:
        """Run Docker container"""
        try:
            cmd = f"docker run {image}"
            if command:
                cmd += f" {command}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
            }
        except Exception as e:
            logger.error(f"Docker error: {e}")
            return {"error": str(e)}
    
    async def build(self, dockerfile: str, tag: str) -> dict:
        """Build Docker image"""
        try:
            cmd = f"docker build -f {dockerfile} -t {tag} ."
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
            }
        except Exception as e:
            logger.error(f"Docker error: {e}")
            return {"error": str(e)}
