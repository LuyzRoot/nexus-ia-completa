from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import zipfile
import os
from typing import List
from plugins import registry, load_registry
from plugins.loader import PluginAPI, load_all_plugins
import shutil

router = APIRouter(prefix="/api/v1/admin/plugins", tags=["plugins_admin"])

# Replace with your actual admin dependency
try:
    from app.deps import require_admin  # adjust to your project
except Exception:
    def require_admin():
        return True


@router.get("", dependencies=[Depends(require_admin)])
def list_installed():
    return [vars(p) for p in registry.list_plugins()]


@router.post("/upload", dependencies=[Depends(require_admin)])
async def upload_and_install(file: UploadFile = File(...), use_sandbox: bool = True):
    """
    Upload a zip containing a plugin package (the zip should contain a plugin folder with __init__.py and plugin.json).
    The zip will be extracted to plugins/installed/<folder>.
    """
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files supported")

    tmpdir = tempfile.mkdtemp(prefix="plugin_upload_")
    try:
        contents = await file.read()
        zpath = os.path.join(tmpdir, "upload.zip")
        with open(zpath, "wb") as f:
            f.write(contents)
        with zipfile.ZipFile(zpath, "r") as z:
            z.extractall(tmpdir)
        # Find top-level folder(s) inside tmpdir (exclude the zip itself)
        entries = [e for e in os.listdir(tmpdir) if os.path.isdir(os.path.join(tmpdir, e))]
        if not entries:
            raise HTTPException(status_code=400, detail="Zip must contain a plugin folder")
        # install each folder found (common case: single plugin folder)
        installed = []
        for folder in entries:
            src = os.path.join(tmpdir, folder)
            try:
                pm = registry.install_plugin_from_path(src, overwrite=True)
                installed.append(vars(pm))
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc))
        # optional: load newly installed plugins (non-blocking)
        api = PluginAPI(register_skill=lambda n, h: None, register_router=lambda r: None)
        load_all_plugins(api, use_sandbox=use_sandbox)
        return {"installed": installed}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@router.post("/{plugin_id}/enable", dependencies=[Depends(require_admin)])
def enable(plugin_id: str):
    ok = registry.enable_plugin(plugin_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"ok": True}


@router.post("/{plugin_id}/disable", dependencies=[Depends(require_admin)])
def disable(plugin_id: str):
    ok = registry.disable_plugin(plugin_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"ok": True}


@router.delete("/{plugin_id}", dependencies=[Depends(require_admin)])
def uninstall(plugin_id: str):
    ok = registry.uninstall_plugin(plugin_id, remove_files=True)
    if not ok:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return JSONResponse(status_code=204, content=None)