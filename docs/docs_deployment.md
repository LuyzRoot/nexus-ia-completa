# Deployment

Opções suportadas:
- Docker Compose (desenvolvimento)
- Kubernetes (produção, recomendado)
- Deploys gerenciados (Cloud Run, ECS) com adaptadores

Docker Compose (exemplo)
- Exemplo para serviços auxiliares já em `monitoring/docker-compose.yml`.
- Para dev, use Postgres local:
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: nexus
      POSTGRES_PASSWORD: nexus
      POSTGRES_DB: nexus
    ports: ["5432:5432"]