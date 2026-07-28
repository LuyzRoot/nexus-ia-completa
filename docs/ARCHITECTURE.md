# Architecture notes

This document describes the high-level architecture introduced in the refactor/structure branch.

- Registry-based auto-discovery for apis/, plugins/, skills/, agents/, tools/, prompts/
- Centralized configuration in config/
- Main entrypoint: main.py
- LLM router in llm/
- Sample components exist under apis/local, plugins/sample_plugin, skills/sample_skill, agents/sample_agent

Next steps:
- Gradual migration of existing code into new packages
- Automated import rewrites and tests
