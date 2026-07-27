# Example Skill Template
# Copy this file and modify to create new skills
# File name must start with: nexus_skill_

class Skill:
    """Example skill template"""
    
    name = "example"
    version = "1.0.0"
    description = "Example skill for testing"
    enabled = True
    
    async def execute(self, action: str, **kwargs):
        """Execute skill action"""
        if action == "test":
            return {"status": "success", "message": "Example skill works!"}
        elif action == "hello":
            return {"status": "success", "message": f"Hello {kwargs.get('name', 'World')}!"}
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
