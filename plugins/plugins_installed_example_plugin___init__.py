from fastapi import APIRouter
from pydantic import BaseModel

# Simple skill handler that plugins can register
def example_skill_handler(payload: dict):
    # Simple demonstration logic
    user_text = payload.get("text", "")
    return {"reply": f"Plugin echo: {user_text}"}

# Optional FastAPI router exposed by plugin
router = APIRouter(prefix="/api/v1/plugins/example", tags=["plugin.example"])

class EchoIn(BaseModel):
    text: str

@router.post("/echo")
def echo(payload: EchoIn):
    return {"echo": payload.text}

def setup(api):
    """
    Called by host with PluginAPI instance.
    Register a skill and a fastapi router to demonstrate capabilities.
    """
    # register skill
    api.add_skill("example.echo", example_skill_handler)
    # register router (host should include the router in app)
    api.add_router(router)