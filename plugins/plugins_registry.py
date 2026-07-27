import json
import os
import shutil
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("plugins.registry")

INSTALLED_DIR = os.path.join(os.path.dirname(__file__), "installed")
REGISTRY_FILE = os.path.join(INSTALLED_DIR, "plugins.json")
_LOCK = threading.Lock()


@dataclass
class PluginMeta:
    id: str
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    enabled: bool = True
    path: Optional[str] = None
    metadata: Optional[dict] = None


def ensure_installed_dir():
    os.makedirs(INSTALLED_DIR, exist_ok=True)


def load_registry() -> Dict[str, PluginMeta]:
    ensure_installed_dir()
    if not os.path.exists(REGISTRY_FILE):
        return {}
    with _LOCK:
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            out = {}
            for pid, spec in data.items():
                out[pid] = PluginMeta(**spec)
            return out
        except Exception as exc:
            logger.exception("Failed to load plugin registry: %s", exc)
            return {}


def save_registry(reg: Dict[str, PluginMeta]) -> None:
    ensure_installed_dir()
    with _LOCK:
        try:
            serializable = {pid: asdict(meta) for pid, meta in reg.items()}
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.exception("Failed to save plugin registry: %s", exc)


def list_plugins() -> List[PluginMeta]:
    reg = load_registry()
    return list(reg.values())


def get_plugin(plugin_id: str) -> Optional[PluginMeta]:
    reg = load_registry()
    return reg.get(plugin_id)


def register_plugin_metadata(meta: PluginMeta) -> None:
    reg = load_registry()
    meta.path = meta.path or meta.id
    reg[meta.id] = meta
    save_registry(reg)


def enable_plugin(plugin_id: str) -> bool:
    reg = load_registry()
    p = reg.get(plugin_id)
    if not p:
        return False
    p.enabled = True
    save_registry(reg)
    return True


def disable_plugin(plugin_id: str) -> bool:
    reg = load_registry()
    p = reg.get(plugin_id)
    if not p:
        return False
    p.enabled = False
    save_registry(reg)
    return True


def install_plugin_from_path(src_path: str, plugin_id: Optional[str] = None, overwrite: bool = False) -> PluginMeta:
    ensure_installed_dir()
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    base_name = plugin_id or os.path.basename(os.path.abspath(src_path)).lower()
    dest = os.path.join(INSTALLED_DIR, base_name)
    if os.path.exists(dest):
        if not overwrite:
            raise FileExistsError(dest)
        shutil.rmtree(dest)
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dest)
    else:
        raise RuntimeError("src_path must be a directory (extract zip first)")

    meta_file = os.path.join(dest, "plugin.json")
    metadata = {}
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            logger.exception("Failed to parse plugin.json in %s", dest)
    pm = PluginMeta(
        id=metadata.get("id", base_name),
        name=metadata.get("name", metadata.get("id", base_name)),
        version=metadata.get("version"),
        description=metadata.get("description"),
        author=metadata.get("author"),
        enabled=metadata.get("enabled", True),
        path=base_name,
        metadata=metadata,
    )
    register_plugin_metadata(pm)
    return pm


def uninstall_plugin(plugin_id: str, remove_files: bool = True) -> bool:
    reg = load_registry()
    p = reg.get(plugin_id)
    if not p:
        return False
    if remove_files and p.path:
        try:
            shutil.rmtree(os.path.join(INSTALLED_DIR, p.path), ignore_errors=True)
        except Exception:
            logger.exception("Failed to remove plugin files for %s", plugin_id)
    reg.pop(plugin_id, None)
    save_registry(reg)
    return True