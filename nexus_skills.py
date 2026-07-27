import os
import importlib
import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skills", tags=["skills"])

class SkillManager:
    """Dynamically load and manage skills"""
    
    def __init__(self):
        self.skills = {}
        self.load_skills()
    
    def load_skills(self):
        """Auto-detect and load skills from skills/ directory"""
        skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        
        if not os.path.exists(skills_dir):
            os.makedirs(skills_dir)
            logger.warning(f"Created skills directory: {skills_dir}")
            return
        
        for filename in os.listdir(skills_dir):
            if filename.startswith("nexus_skill_") and filename.endswith(".py"):
                try:
                    skill_name = filename.replace("nexus_skill_", "").replace(".py", "")
                    module_name = f"skills.{filename[:-3]}"
                    module = importlib.import_module(module_name)
                    
                    # Load skill class
                    if hasattr(module, "Skill"):
                        skill_class = getattr(module, "Skill")
                        self.skills[skill_name] = skill_class()
                        logger.info(f"Loaded skill: {skill_name}")
                except Exception as e:
                    logger.error(f"Error loading skill {filename}: {e}")
    
    def get_skills(self) -> Dict[str, Any]:
        """Get all loaded skills with metadata"""
        return {
            name: {
                "name": name,
                "description": getattr(skill, "description", "No description"),
                "version": getattr(skill, "version", "1.0.0"),
                "enabled": getattr(skill, "enabled", True),
            }
            for name, skill in self.skills.items()
        }
    
    async def execute_skill(self, skill_name: str, action: str, **kwargs) -> Any:
        """Execute a specific skill"""
        if skill_name not in self.skills:
            raise ValueError(f"Skill not found: {skill_name}")
        
        skill = self.skills[skill_name]
        if not hasattr(skill, "execute"):
            raise ValueError(f"Skill {skill_name} does not have execute method")
        
        return await skill.execute(action, **kwargs)
    
    def reload_skills(self):
        """Reload all skills dynamically"""
        self.skills.clear()
        self.load_skills()
        return self.get_skills()

# Global skill manager
skill_manager = SkillManager()

# API Routes
@router.get("/")
async def list_skills():
    """List all available skills"""
    return {
        "skills": skill_manager.get_skills(),
        "total": len(skill_manager.skills)
    }

@router.get("/{skill_name}")
async def get_skill(skill_name: str):
    """Get specific skill info"""
    skills = skill_manager.get_skills()
    if skill_name not in skills:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_name}")
    return skills[skill_name]

@router.post("/{skill_name}/execute")
async def execute_skill(skill_name: str, action: str, params: dict = None):
    """Execute a skill action"""
    try:
        result = await skill_manager.execute_skill(skill_name, action, **(params or {}))
        return {"skill": skill_name, "action": action, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Skill execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_skills():
    """Reload all skills (useful after adding new skills)"""
    reloaded = skill_manager.reload_skills()
    return {"message": "Skills reloaded", "skills": reloaded}