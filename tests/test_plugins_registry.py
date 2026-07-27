import pytest
import os
import shutil
import json
import tempfile

def test_plugins_registry_install_uninstall(tmp_path):
    reg = pytest.importorskip("plugins.registry")
    # create a fake plugin dir
    src = tmp_path / "fake_plugin"
    src.mkdir()
    (src / "__init__.py").write_text("def setup(api): pass")
    (src / "plugin.json").write_text(json.dumps({"id":"fake_plugin","name":"Fake","version":"0.1"}))
    # install
    pm = reg.install_plugin_from_path(str(src), overwrite=True)
    assert pm.id == "fake_plugin"
    try:
        listed = [p.id for p in reg.list_plugins()]
        assert "fake_plugin" in listed
        ok = reg.uninstall_plugin("fake_plugin", remove_files=True)
        assert ok
    finally:
        # cleanup installed folder if exists
        installed_dir = os.path.join(os.path.dirname(reg.__file__), "installed", "fake_plugin")
        try:
            shutil.rmtree(installed_dir, ignore_errors=True)
        except Exception:
            pass