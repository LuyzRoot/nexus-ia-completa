import asyncio
import json
import logging
import sys
from pathlib import Path
import importlib.util
import types
from typing import Any, Dict, Optional

from config.paths import SKILLS_DIR
from config.settings import settings

logger = logging.getLogger(__name__)


class SkillLoadError(Exception):
    pass


def _is_package_dir(p: Path) -> bool:
    return p.is_dir() and any((p / fname).exists() for fname in ("manifest.json", "skill.py", "__init__.py"))


class SkillWrapper:
    def __init__(self, name: str, module: types.ModuleType, meta: dict):
        self.name = name
        self.module = module
        self.meta = meta or {}
        inst = getattr(module, "Skill", None)
        if callable(inst):
            try:
                self.instance = inst()
            except Exception:
                # fallback: keep the class/function as-is
                self.instance = inst
        else:
            # module-level functions or objects
            self.instance = module

    async def execute(self, action: str, **kwargs) -> Any:
        target = getattr(self.instance, "execute", None)
        if target is None:
            raise SkillLoadError("Skill has no execute method")
        if asyncio.iscoroutinefunction(target):
            return await target(action, **kwargs)
        else:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: target(action, **kwargs))


class SkillManager:
    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = Path(skills_dir or SKILLS_DIR)
        self._skills: Dict[str, SkillWrapper] = {}
        self._lock = asyncio.Lock()
        self._loaded_modules: Dict[str, types.ModuleType] = {}

    async def discover(self) -> Dict[str, dict]:
        found: Dict[str, dict] = {}
        if not self.skills_dir.exists():
            logger.debug("Skills directory not found: %s", self.skills_dir)
            return found
        for child in sorted(self.skills_dir.iterdir()):
            try:
                if _is_package_dir(child):
                    meta = await self._read_manifest(child)
                    name = meta.get("name") or child.name
                    found[name] = {"path": str(child), "meta": meta}
            except Exception:
                logger.exception("Error reading skill %s", child)
        return found

    async def _read_manifest(self, path: Path) -> dict:
        manifest = path / "manifest.json"
        if manifest.exists():
            try:
                return json.loads(manifest.read_text(encoding="utf-8"))
            except Exception:
                logger.exception("Invalid manifest in %s", path)
                return {}
        return {"name": path.name, "version": "0.0.0"}

    async def load_all(self) -> None:
        async with self._lock:
            discovered = await self.discover()
            for name, info in discovered.items():
                if name in self._skills:
                    continue
                try:
                    wrapper = await self._load_skill_from_path(Path(info["path"]), name)
                    self._skills[name] = wrapper
                    logger.info("Loaded skill %s", name)
                except Exception:
                    logger.exception("Failed to load skill %s", name)

    async def _load_skill_from_path(self, path: Path, name: str) -> SkillWrapper:
        candidate = None
        if (path / "skill.py").exists():
            candidate = path / "skill.py"
        elif (path / "__init__.py").exists():
            candidate = path / "__init__.py"
        else:
            raise SkillLoadError("No skill entry point")
        spec = importlib.util.spec_from_file_location(f"nexus.skills.{name}", candidate)
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        if loader is None:
            raise SkillLoadError("Cannot load module spec")
        # exec module
        loader.exec_module(module)
        # register
        self._loaded_modules[name] = module
        meta = await self._read_manifest(path)
        return SkillWrapper(name=name, module=module, meta=meta)

    async def get_skills(self) -> Dict[str, dict]:
        async with self._lock:
            return {n: {"name": n, "meta": w.meta} for n, w in self._skills.items()}

    async def execute_skill(self, name: str, action: str, **kwargs) -> Any:
        async with self._lock:
            if name not in self._skills:
                raise KeyError("skill not loaded")
            wrapper = self._skills[name]
        # release lock during execution
        return await wrapper.execute(action, **kwargs)

    async def reload(self) -> None:
        async with self._lock:
            # call on_unload if present
            for w in list(self._skills.values()):
                try:
                    on_unload = getattr(w.instance, "on_unload", None)
                    if callable(on_unload):
                        res = on_unload()
                        if asyncio.iscoroutine(res):
                            await res
                except Exception:
                    logger.exception("Error during skill on_unload for %s", w.name)
            self._skills.clear()
            # remove loaded modules to force reload
            for name, module in list(self._loaded_modules.items()):
                try:
                    sys.modules.pop(module.__name__, None)
                except Exception:
                    pass
            self._loaded_modules.clear()
            await self.load_all()


# simple singleton factory for DI
_skill_manager_singleton: Optional[SkillManager] = None


def get_skill_manager() -> SkillManager:
    global _skill_manager_singleton
    if _skill_manager_singleton is None:
        _skill_manager_singleton = SkillManager()
    return _skill_manager_singleton
