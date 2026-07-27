import importlib
import sys
import os
import logging
import traceback
from typing import Optional, Callable, Any
from types import ModuleType
import multiprocessing
import queue

from plugins.registry import INSTALLED_DIR, load_registry, get_plugin

logger = logging.getLogger("plugins.loader")


class PluginAPI:
    def __init__(self, register_skill: Optional[Callable[[str, Callable], None]] = None, register_router: Optional[Callable[[Any], None]] = None, logger=None):
        self.register_skill = register_skill or (lambda name, fn: logger and logger.warning("No register_skill provided"))
        self.register_router = register_router or (lambda router: logger and logger.warning("No register_router provided"))
        self.logger = logger or logging.getLogger("plugins.api")

    def add_skill(self, name: str, handler: Callable):
        return self.register_skill(name, handler)

    def add_router(self, router):
        return self.register_router(router)


def _import_module_from_path(module_name: str, path: str) -> Optional[ModuleType]:
    try:
        if path not in sys.path:
            sys.path.insert(0, path)
        return importlib.import_module(module_name)
    except Exception:
        logger.exception("Failed to import module %s from %s", module_name, path)
        return None


def load_plugin_module(plugin_id: str, api: Optional[PluginAPI] = None, use_sandbox: bool = False, sandbox_timeout: int = 5) -> Optional[ModuleType]:
    meta = get_plugin(plugin_id)
    if not meta:
        logger.warning("Plugin %s not found in registry", plugin_id)
        return None
    if not meta.enabled:
        logger.info("Plugin %s is disabled; skipping load", plugin_id)
        return None

    pkg_path = os.path.join(INSTALLED_DIR, meta.path)
    if not os.path.isdir(pkg_path):
        logger.warning("Plugin path %s does not exist for %s", pkg_path, plugin_id)
        return None

    module_name = f"plugins.installed.{meta.path}"
    parent_dir = os.path.dirname(INSTALLED_DIR)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    mod = _import_module_from_path(module_name, parent_dir)
    if not mod:
        return None

    try:
        setup_fn = getattr(mod, "setup", None)
        if callable(setup_fn):
            if use_sandbox:
                success, result_or_err = run_in_sandbox(setup_fn, (api,), timeout=sandbox_timeout)
                if not success:
                    logger.warning("Plugin %s setup failed in sandbox: %s", plugin_id, result_or_err)
                else:
                    logger.info("Plugin %s setup completed (sandbox)", plugin_id)
            else:
                try:
                    setup_fn(api)
                    logger.info("Plugin %s setup completed", plugin_id)
                except Exception:
                    logger.exception("Plugin %s setup() raised exception", plugin_id)
                    return None
    except Exception:
        logger.exception("Error during plugin %s initialization", plugin_id)
        return None

    return mod


def load_all_plugins(api: Optional[PluginAPI] = None, use_sandbox: bool = False, sandbox_timeout: int = 5):
    reg = load_registry()
    for pid, meta in reg.items():
        if not meta.enabled:
            continue
        try:
            load_plugin_module(pid, api=api, use_sandbox=use_sandbox, sandbox_timeout=sandbox_timeout)
        except Exception:
            logger.exception("Failed to load plugin %s", pid)


def _worker_call(fn, args, q):
    try:
        res = fn(*args)
        q.put(("ok", res))
    except Exception as exc:
        tb = traceback.format_exc()
        q.put(("err", {"error": str(exc), "traceback": tb}))


def run_in_sandbox(fn: Callable, args: tuple = (), timeout: int = 5):
    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_worker_call, args=(fn, args, q))
    p.start()
    try:
        res = q.get(timeout=timeout)
        p.join(timeout=1)
        if res[0] == "ok":
            return True, res[1]
        return False, res[1]
    except queue.Empty:
        p.terminate()
        return False, {"error": "timeout", "traceback": None}
    except Exception as exc:
        p.terminate()
        return False, {"error": str(exc)}