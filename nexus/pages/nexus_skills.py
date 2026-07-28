import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional

from nexus.pages.skill_manager import get_skill_manager, SkillManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skills", tags=["skills"])


async def _ensure_loaded(manager: SkillManager):
    # Lazy load skills if not loaded
    skills = await manager.get_skills()
    if not skills:
        await manager.load_all()


@router.get("/")
async def list_skills(manager: SkillManager = Depends(get_skill_manager)) -> Dict[str, Any]:
    await _ensure_loaded(manager)
    return {"skills": await manager.get_skills(), "total": len((await manager.get_skills()))}


@router.get("/{skill_name}")
async def get_skill(skill_name: str, manager: SkillManager = Depends(get_skill_manager)) -> Dict[str, Any]:
    await _ensure_loaded(manager)
    skills = await manager.get_skills()
    if skill_name not in skills:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_name}")
    return skills[skill_name]


@router.post("/{skill_name}/execute")
async def execute_skill(skill_name: str, action: str, params: Optional[dict] = None, manager: SkillManager = Depends(get_skill_manager)):
    await _ensure_loaded(manager)
    try:
        result = await manager.execute_skill(skill_name, action, **(params or {}))
        return {"skill": skill_name, "action": action, "result": result}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Skill execution error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_skills(manager: SkillManager = Depends(get_skill_manager)):
    await manager.reload()
    return {"message": "Skills reloaded", "skills": await manager.get_skills()}
