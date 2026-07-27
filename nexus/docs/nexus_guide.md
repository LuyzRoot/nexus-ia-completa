# NEXUS IA v2.0 - Architecture Guide

## 🎯 Sistema de Skills

### Como adicionar uma nova Skill:

1. Crie um arquivo em `nexus/skills/nexus_skill_seuanome.py`
2. Defina uma classe `Skill` com os atributos:
   - `name`: Nome da skill
   - `version`: Versão
   - `description`: Descrição
   - `enabled`: Boolean
3. Implemente o método `execute(action, **kwargs)`

### Exemplo:
```python
class Skill:
    name = "calculator"
    version = "1.0.0"
    description = "Math operations"
    enabled = True
    
    async def execute(self, action: str, **kwargs):
        if action == "sum":
            return kwargs['a'] + kwargs['b']
```

4. A skill será **automaticamente carregada**!

---

## 🔌 Sistema de APIs (LLM Providers)

### Como adicionar uma nova API:

1. Crie um arquivo em `nexus/apis/nexus_seuapi.py`
2. Defina uma classe `Provider` com:
   - `name`: Nome do provider
   - `version`: Versão
   - `description`: Descrição
   - `endpoints`: Lista de endpoints
3. Implemente `async def chat(messages, **kwargs)`

### Exemplo:
```python
class Provider:
    name = "minha_ia"
    version = "1.0.0"
    description = "My IA Provider"
    endpoints = ["chat"]
    
    async def chat(self, messages, **kwargs):
        # Lógica da sua IA
        return "response"
```

4. Será **automaticamente reconhecido**!

---

## 📡 Endpoints

### Skills
- `GET /skills/` - Listar todas as skills
- `GET /skills/{skill_name}` - Info da skill
- `POST /skills/{skill_name}/execute` - Executar skill
- `POST /skills/reload` - Recarregar skills

### APIs
- `GET /apis/` - Listar todas as APIs
- `GET /apis/{api_name}` - Info da API
- `POST /apis/{api_name}/chat` - Chat com API
- `GET /apis/{api_name}/status` - Status da API
- `POST /apis/reload` - Recarregar APIs
