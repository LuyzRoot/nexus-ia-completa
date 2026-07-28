#!/usr/bin/env bash
set -euo pipefail

# scripts/setup_complete.sh
# Script para preparar o ambiente do repositório nexus-ia-completa
# - cria virtualenv em .venv
# - instala dependencies do requirements.txt
# - copia .env.example -> .env se .env não existir
# - opcional: roda migrations do Alembic se chamado com --migrate


echo "=== Iniciando setup de nexus-ia-completa ==="

# 1) Verifica python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERRO: python3 não encontrado. Instale o Python 3.8+ e rode novamente." >&2
  exit 1
fi

PYVER=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
echo "Python detectado: $PYVER"

# Parse optional flags
RUN_MIGRATIONS=0
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --migrate)
      RUN_MIGRATIONS=1
      shift
      ;;
    *)
      echo "Opção desconhecida: $1"
      echo "Uso: ./scripts/setup_complete.sh [--migrate]"
      exit 1
      ;;
  esac
done

# 2) Cria e ativa virtualenv
if [ -d ".venv" ]; then
  echo ".venv já existe. Você pode ativar com: source .venv/bin/activate"
else
  echo "Criando virtualenv em .venv..."
  python3 -m venv .venv
  echo "Virtualenv criado em .venv"
fi

# Ativa o venv para instalar pacotes
# Note: ativar dentro de script não persiste na sessão do usuário, mostramos instrução ao final.
source .venv/bin/activate

# 3) Atualiza pip e instala requirements
echo "Atualizando pip e instalando requirements..."
pip install --upgrade pip setuptools wheel
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
  echo "Dependências do requirements.txt instaladas"
else
  echo "Aviso: requirements.txt não encontrado na raiz. Pulei instalação de requirements." >&2
fi

# 4) Copia .env.example -> .env se necessário
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo ".env criado a partir de .env.example — edite .env com suas chaves (OPENAI_KEY, DATABASE_URL, etc)."
  else
    echo "Aviso: não há .env nem .env.example — crie .env manualmente conforme README." >&2
  fi
else
  echo ".env já existe — mantendo o arquivo atual."
fi

# 5) Frontend (opcional)
if [ -d "frontend" ]; then
  echo "Pasta frontend detectada. Se você pretende rodar o frontend agora, execute:
  cd frontend && npm install && npm run dev  # ou yarn && yarn dev"
fi

# 6) Migrations (opcional)
if [ "$RUN_MIGRATIONS" -eq 1 ]; then
  echo "\nOpção --migrate detectada: tentando rodar migrations Alembic (alembic upgrade head)"
  # Ensure alembic is installed in the venv
  if ! python -c "import alembic" >/dev/null 2>&1; then
    echo "Alembic não encontrado no venv — instalando alembic..."
    pip install alembic
  fi

  # If alembic.ini is missing, warn the user (we added a template alembic.ini at repo root)
  if [ ! -f alembic.ini ]; then
    echo "Aviso: alembic.ini não encontrado na raiz do repo. Criando a partir do template alembic.ini (se presente)."
    if [ -f alembic.ini ]; then
      echo "alembic.ini já presente"
    else
      echo "Template alembic.ini não encontrado — crie um alembic.ini ou verifique database/alembic_env_template.py"
    fi
  fi

  # Run alembic upgrade head
  if command -v alembic >/dev/null 2>&1; then
    echo "Rodando: alembic upgrade head"
    alembic upgrade head
  else
    # If alembic binary not in PATH but installed in python, call via -m
    echo "Executando alembic via python -m alembic upgrade head"
    python -m alembic upgrade head
  fi
fi

# 7) Banco de dados (opcional)
# Não rodamos create_all por padrão. Use scripts/manage_db.sh init para criar tabelas em dev.


echo "\nSetup concluído (passos automatizados). Próximos passos sugeridos:"
echo "1) Ative o venv: source .venv/bin/activate"
echo "2) Edite .env e preencha as variáveis necessárias"
echo "3) Se você rodou --migrate, verifique se as migrations aplicaram sem erros"
echo "4) Inicie o backend: python nexus_main.py  (ver README para comando exato)"

echo "Se quiser que eu execute alterações adicionais (ex: ajustar alembic.ini, configurar um SQLite 'dev.db', ou adaptar para Windows), diga o que prefere e eu atualizo os arquivos." 

exit 0
