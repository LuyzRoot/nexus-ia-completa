"""
Model / provider defaults and helper utilities.
Centralizes provider names and default models.
"""

from typing import List, Dict

DEFAULT_PROVIDER_PRIORITY: List[str] = ["anthropic", "openai", "gemini", "mock"]

# Friendly display names + metadata optionally used by admin UI
PROVIDER_METADATA: Dict[str, dict] = {
    "anthropic": {"label": "Anthropic Claude", "supports_tools": True, "supports_streaming": True},
    "openai": {"label": "OpenAI", "supports_tools": True, "supports_streaming": True},
    "gemini": {"label": "Google Gemini", "supports_tools": True, "supports_streaming": True},
    "mock": {"label": "Mock Provider (dev)", "supports_tools": False, "supports_streaming": False},
}

# Known models per provider (suggestions)
DEFAULT_MODELS: Dict[str, str] = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
}