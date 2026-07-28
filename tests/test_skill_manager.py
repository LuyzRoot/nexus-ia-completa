import asyncio
import json
from pathlib import Path
import tempfile

import pytest

from nexus.pages.skill_manager import SkillManager


@pytest.mark.asyncio
async def test_skill_manager_load_and_execute(tmp_path: Path):
    # create skills directory
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # create sample skill package
    sample = skills_dir / "sample"
    sample.mkdir()
    manifest = sample / "manifest.json"
    manifest.write_text(json.dumps({"name": "sample", "version": "0.1.0"}))
    skill_py = sample / "skill.py"
    skill_py.write_text(
        """
import asyncio

class Skill:
    async def execute(self, action: str, **kwargs):
        return {'action': action, 'ok': True, 'kwargs': kwargs}
"""
    )

    manager = SkillManager(skills_dir=skills_dir)
    await manager.load_all()
    skills = await manager.get_skills()
    assert "sample" in skills

    res = await manager.execute_skill("sample", "do_it", foo=1)
    assert isinstance(res, dict)
    assert res["action"] == "do_it"
    assert res["ok"] is True

    # test reload
    await manager.reload()
    skills2 = await manager.get_skills()
    assert "sample" in skills2
