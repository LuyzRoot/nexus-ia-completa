import os
import importlib
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/apis", tags=["apis"])

class APIManager:
    """Dynamically load and manage LLM APIs"""
    
    def __init__(self):
        self.apis = {}
        self.configurations = {}
        self.load_apis()
    
    def load_apis(self):
        """Auto-detect and load APIs from apis/ directory"""
        apis_dir = os.path.join(os.path.dirname(__file__), "apis")
        
        if not os.path.exists(apis_dir):
            os.makedirs(apis_dir)
            logger.warning(f"Created APIs directory: {apis_dir}")
            return
        
        for filename in os.listdir(apis_dir):
            if filename.startswith("nexus_") and filename.endswith(".py"):
                try:
                    api_name = filename.replace("nexus_", "").replace(".py", "")
                    module_name = f"apis.{filename[:-3]}"
                    module = importlib.import_module(module_name)
                    
                    # Load API provider
                    if hasattr(module, "Provider"):
                        provider_class = getattr(module, "Provider")
                        self.apis[api_name] = provider_class
                        logger.info(f"Loaded API provider: {api_name}")
                    elif hasattr(module, api_name.title() + "Provider"):
                        provider_class = getattr(module, api_name.title() + "Provider")
                        self.apis[api_name] = provider_class
                        logger.info(f"Loaded API provider: {api_name}")
                except Exception as e:
                    logger.error(f"Error loading API {filename}: {e}")
    
    def get_apis(self) -> Dict[str, Any]:
        """Get all loaded APIs with metadata"""
        apis_info = {}
        for name, provider_class in self.apis.items():
            try:
                provider = provider_class()
                apis_info[name] = {
                    "name": name,
                    "provider": provider_class.__name__,
                    "description": getattr(provider, "description", f"{name.upper()} API Provider"),
                    "version": getattr(provider, "version", "1.0.0"),
                    "status": "configured" if self.is_configured(name) else "pending",
                    "endpoints": getattr(provider, "endpoints", []),
                }
            except Exception as e:
                logger.warning(f"Error loading API info for {name}: {e}")
                apis_info[name] = {"name": name, "status": "error", "error": str(e)}
        
        return apis_info
    
    def is_configured(self, api_name: str) -> bool:
        """Check if API is configured with credentials"""
        from nexus_config import nexus_settings
        
        config_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "ollama": "OLLAMA_BASE_URL",
        }
        
        if api_name in config_keys:
            key = config_keys[api_name]
            return bool(getattr(nexus_settings, key, None))
        
        return False
    
    async def get_api_instance(self, api_name: str):
        """Get initialized API instance"""
        if api_name not in self.apis:
            raise ValueError(f"API not found: {api_name}")
        
        provider_class = self.apis[api_name]
        return provider_class()
    
    async def chat(self, api_name: str, messages: List[Dict], **kwargs) -> str:
        """Route chat request to specific API"""
        try:
            provider = await self.get_api_instance(api_name)
            if not hasattr(provider, "chat"):
                raise ValueError(f"API {api_name} does not support chat")
            return await provider.chat(messages, **kwargs)
        except Exception as e:
            logger.error(f"API chat error: {e}")
            raise
    
    def reload_apis(self):
        """Reload all APIs dynamically"""
        self.apis.clear()
        self.load_apis()
        return self.get_apis()

# Global API manager
api_manager = APIManager()

# API Routes
@router.get("/")
async def list_apis():
    """List all available LLM APIs"""
    return {
        "apis": api_manager.get_apis(),
        "total": len(api_manager.apis)
    }

@router.get("/{api_name}")
async def get_api(api_name: str):
    """Get specific API info"""
    apis = api_manager.get_apis()
    if api_name not in apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_name}")
    return apis[api_name]

@router.post("/{api_name}/chat")
async def api_chat(api_name: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1024):
    """Send chat request to specific API"""
    try:
        result = await api_manager.chat(api_name, messages, temperature=temperature, max_tokens=max_tokens)
        return {
            "api": api_name,
            "response": result,
            "usage": {"tokens": 0}  # TODO: Add token counting
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_apis():
    """Reload all APIs (useful after adding new API files)"""
    reloaded = api_manager.reload_apis()
    return {"message": "APIs reloaded", "apis": reloaded}

@router.get("/{api_name}/status")
async def api_status(api_name: str):
    """Get API status and configuration"""
    apis = api_manager.get_apis()
    if api_name not in apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_name}")
    
    return {
        "api": api_name,
        "info": apis[api_name],
        "configured": api_manager.is_configured(api_name),
    }