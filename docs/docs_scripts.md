# Scripts — NEXUS IA

Esta página lista e documenta os scripts utilitários (bash / Python / CLI) usados para desenvolvimento, ingestão, treinamento, inferência, monitoramento e operações do NEXUS IA. Também inclui convenções, templates e boas práticas para escrever e manter scripts no projeto.

Sumário
- Visão geral
- Localização e convenção de nomes
- Categorias de scripts (com exemplos e comandos)
  - Desenvolvimento / Dev server
  - Banco de dados / Migrações
  - Ingestão de datasets / RAG
  - Treinamento
  - Inferência / Servidores
  - Monitoramento / Observabilidade
  - Administração / Plugins
  - Utilitários (backup, limpeza, pacotes)
- Template de script robusto (bash)
- Como tornar scripts executáveis e seguros
- Execução em ambientes (Docker / Compose / Windows)
- Boas práticas e checklist
- Quero os scripts prontos — opções

---

## Visão geral

Scripts são ferramentas de automação para tarefas repetitivas: iniciar servidores em dev, rodar ingestão, treinar modelos, criar backup, rodar migrações, instalar plugins e etc. No NEXUS, organizamos scripts por área de responsabilidade para facilitar descoberta e manutenção.

Preferimos scripts idempotentes, pequenos e testáveis. Scripts pesados (treinamento, geração de imagens) devem ser executados em nodos separados (GPU) ou via jobs.

---

## Localização e convenção de nomes

- Diretório principal para scripts operacionais: `/scripts/` na raiz do repositório.
- Scripts específicos de cada submódulo ficam dentro do subdiretório do módulo, por exemplo:
  - `datasets/` (scripts para ingestão): `datasets/ingest.py`, `datasets/scripts/`
  - `training/` (treinamento): `training/scripts/train_lm.sh`
  - `monitoring/` (dev stack): `monitoring/docker-compose.yml`
  - `inference/` (server start): `inference/server.py`, `scripts/start_inference.sh`
- Convenção de nomes:
  - `verb_noun.sh` (bash) ou `verb_noun.py` (Python CLI). Ex.: `run_dev.sh`, `ingest_dataset.sh`, `train_lm.sh`.
  - Sufixo `.sh` para scripts shell, `.py` para utilitários Python (com CLI via argparse / Typer / Click).

---

## Categorias de scripts (exemplos e comandos)

Abaixo, lista de scripts comuns com caminho sugerido, breve descrição e exemplo de execução.

### Desenvolvimento / Dev server
- scripts/run_dev.sh
  - Inicia backend FastAPI e frontend Vite (modo desenvolvimento), com carregamento de variáveis de `.env`.
  - Exemplo:
    ```bash
    ./scripts/run_dev.sh
    # ou
    ./scripts/run_dev.sh --backend-port 8000 --frontend-port 5173
    ```

### Banco de dados / Migrações
- scripts/manage_db.sh
  - Wrapper para operações de DB: criar DB dev, rodar migrations Alembic, aplicar seed.
  - Exemplos:
    ```bash
    ./scripts/manage_db.sh init         # create_all ou alembic upgrade head (dev)
    ./scripts/manage_db.sh migrate     # alembic revision --autogenerate && alembic upgrade head
    ./scripts/manage_db.sh drop        # DROP ALL TABLES (apenas dev)
    ```

### Ingestão de datasets / RAG
- datasets/ingest.py
  - Ingestão de documentos para o RAG index (chunking, embeddings, index add).
  - Exemplo:
    ```bash
    python datasets/ingest.py --paths datasets/data/* --namespace my_dataset --chunk-size 1000 --overlap 200
    ```

- scripts/ingest_dataset.sh (wrapper)
  - Exemplo:
    ```bash
    ./scripts/ingest_dataset.sh datasets/data/ my_dataset
    ```

### Treinamento
- training/prepare_data.py
- training/fine_tune_lm.py
- training/finetune_embeddings.py
- training/train_reranker.py
- training/scripts/train_lm.sh
  - Exemplos:
    ```bash
    python training/prepare_data.py --input datasets/data/myset.jsonl --out training/data/processed
    python training/fine_tune_lm.py --train-file training/data/processed/train.jsonl --validation-file training/data/processed/val.jsonl --model-name-or-path gpt2 --output-dir outputs/lm_finetune
    ./training/scripts/train_lm.sh
    ```

### Inferência / Servidores
- inference/server.py (FastAPI app)
- scripts/start_inference.sh
  - Exemplo:
    ```bash
    ./scripts/start_inference.sh --port 8001 --workers 1
    # ou com uvicorn
    uvicorn inference.server:app --host 0.0.0.0 --port 8001 --workers 1
    ```

### Monitoramento / Observabilidade
- monitoring/docker-compose.yml — levanta Prometheus + Grafana (dev)
  - Exemplo:
    ```bash
    cd monitoring
    docker compose up -d
    ```

- scripts/monitor_stack.sh — wrapper que sobe a stack de observabilidade local

### Administração / Plugins
- plugins/registry.py contem helpers programáticos.
- app/api/plugins_admin.py endpoints para upload/install plugins.
- scripts/install_plugin.sh — extrai zip e chama API de upload ou usa `plugins.registry.install_plugin_from_path`.

### Utilitários
- scripts/backup_db.sh — dump do banco (pg_dump) para pasta de backups.
- scripts/restore_db.sh — restaura a partir de dump (apenas dev/test).
- scripts/cleanup_tmp.sh — limpa caches / arquivos temporários.

---

## Template de script robusto (bash)

Use este template para scripts shell. Ele cobre opções básicas: fail fast, parsing de flags, help, carregamento de `.env`, logs e limpeza.

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Defaults
VERBOSE=0
ENV_FILE=".env"
SCRIPT_NAME="$(basename "$0")"

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [--env .env] [--verbose] command [args...]

Commands:
  init         Initialize environment (dev)
  migrate      Run alembic migrations
  help         Show this message

Environment:
  Load variables from .env by default. Set ENV_FILE to change.
EOF
}

log() {
  local level="$1"; shift
  echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] [$level] $*"
}

# Parse args (simple)
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENV_FILE="$2"; shift 2;;
    --verbose) VERBOSE=1; shift;;
    help|-h|--help) usage; exit 0;;
    *) break;;
  esac
done

# Load env file if present
if [[ -f "$ENV_FILE" ]]; then
  # Avoid exporting secrets to process list unnecessarily
  set -a; source "$ENV_FILE"; set +a
  log INFO "Loaded env from $ENV_FILE"
fi

# Command dispatch
COMMAND="${1:-help}"; shift || true

case "$COMMAND" in
  init)
    log INFO "Initializing (dev) ..."
    # Example: create DB + migrate
    python -c "from app.database import utils; utils.init_db(create_tables=True)"
    ;;
  migrate)
    log INFO "Running alembic upgrade head ..."
    alembic upgrade head
    ;;
  *)
    usage
    exit 1
    ;;
esac