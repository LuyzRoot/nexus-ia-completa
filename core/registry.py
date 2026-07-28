import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

class Registry:
    """Discover and register components (apis, plugins, skills, agents, tools, prompts).

    Discovery strategy: look for directories at repository root with given names and
    import modules under them. A component is considered present if it is a
    subdirectory containing __init__.py.
    """
    def __init__(self, root: Path = None):
        self.root = root or Path(__file__).resolve().parents[1]
        self.components: Dict[str, List[str]] = {}
        self.names = [
            "apis",
            "plugins",
            "skills",
            "agents",
            "tools",
            "prompts",
        ]

    def discover(self, name: str):
        p = self.root / name
        found = []
        if not p.exists():
            logger.debug("No directory %s", p)
            self.components[name] = []
            return []
        for child in p.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                module_name = f"{name}.{child.name}"
                try:
                    importlib.import_module(module_name)
                    found.append(child.name)
                    logger.info("Discovered %s: %s", name, child.name)
                except Exception as e:
                    logger.warning("Failed to import %s: %s", module_name, e)
        self.components[name] = found
        return found

    def discover_all(self):
        for n in self.names:
            self.discover(n)

    def summary(self):
        return {k: v for k, v in self.components.items()}
