import subprocess
import os
import aiofiles
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class TerminalTool:
    """Execute terminal commands"""
    async def execute(self, command: str, cwd: str = None) -> dict:
        try:
            result = subprocess.run(
                command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30
            )
            return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.TimeoutExpired:
            return {"error": "Command timeout"}
        except Exception as e:
            logger.error(f"Terminal error: {e}")
            return {"error": str(e)}

class FileSystemTool:
    """File system operations"""
    async def read(self, path: str) -> str:
        try:
            async with aiofiles.open(path, "r") as f:
                return await f.read()
        except Exception as e:
            return f"Error: {e}"
    
    async def write(self, path: str, content: str) -> dict:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            async with aiofiles.open(path, "w") as f:
                await f.write(content)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"error": str(e)}
    
    async def list_dir(self, path: str = ".") -> List[str]:
        try:
            return os.listdir(path)
        except Exception as e:
            return []
    
    async def delete(self, path: str) -> dict:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            return {"status": "deleted", "path": path}
        except Exception as e:
            return {"error": str(e)}

class BrowserTool:
    """Web browser automation"""
    async def navigate(self, url: str) -> dict:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30)
                return {"url": url, "status": response.status_code, "content": response.text[:1000]}
        except Exception as e:
            return {"error": str(e)}

class GitHubTool:
    """GitHub API interactions"""
    async def get_repo(self, owner: str, repo: str, token: str = None) -> dict:
        try:
            import httpx
            headers = {"Authorization": f"token {token}"} if token else {}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}", headers=headers
                )
                return response.json()
        except Exception as e:
            return {"error": str(e)}

class DockerTool:
    """Docker operations"""
    async def run(self, image: str, command: str = None) -> dict:
        try:
            cmd = f"docker run {image}"
            if command:
                cmd += f" {command}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {"status": "success" if result.returncode == 0 else "error", "output": result.stdout}
        except Exception as e:
            return {"error": str(e)}

class PythonTool:
    """Execute Python code"""
    async def execute(self, code: str) -> dict:
        try:
            result = subprocess.run(
                ["python", "-c", code], capture_output=True, text=True, timeout=10
            )
            return {"status": "success" if result.returncode == 0 else "error", "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout"}
        except Exception as e:
            return {"error": str(e)}

class ShellTool:
    """Shell script execution"""
    async def execute(self, script: str, shell: str = "/bin/bash") -> dict:
        try:
            result = subprocess.run(
                script, shell=True, capture_output=True, text=True, timeout=30, executable=shell
            )
            return {"status": "success" if result.returncode == 0 else "error", "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"error": "Script timeout"}
        except Exception as e:
            return {"error": str(e)}
