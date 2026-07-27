import os
import aiofiles
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class FileSystemTool:
    """File system operations"""
    
    async def read(self, path: str) -> str:
        """Read file"""
        try:
            async with aiofiles.open(path, "r") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Read error: {e}")
            return f"Error: {e}"
    
    async def write(self, path: str, content: str) -> dict:
        """Write file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            async with aiofiles.open(path, "w") as f:
                await f.write(content)
            return {"status": "success", "path": path}
        except Exception as e:
            logger.error(f"Write error: {e}")
            return {"error": str(e)}
    
    async def list_dir(self, path: str = ".") -> List[str]:
        """List directory contents"""
        try:
            return os.listdir(path)
        except Exception as e:
            logger.error(f"List error: {e}")
            return []
    
    async def delete(self, path: str) -> dict:
        """Delete file or directory"""
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            return {"status": "deleted", "path": path}
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return {"error": str(e)}
