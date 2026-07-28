#!/usr/bin/env bash
set -euo pipefail

# scripts/setup_complete.sh
# Script para preparar o ambiente do repositório nexus-ia-completa
# - cria virtualenv em .venv
# - instala dependencies do requirements.txt
# - copia .env.example -> .env se .env não existir
# - dá orientações finais

echo "=== Iniciando setup de nexus-ia-completa ==="

# 1) Verifica python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERRO: python3 não encontrado. Instale o Python 3.8+ e rode novamente." >&2
  exit 1
fi

PYVER=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
echo "Python detectado: $PYVER"

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

# 6) Banco de dados (opcional)
# Não rodamos migrations por segurança. Se deseja rodar migrations automaticamente, me diga qual framework (alembic, django, flask-migrate).

echo "\nSetup concluído (passos automatizados). Próximos passos sugeridos:"
echo "1) Ative o venv: source .venv/bin/activate"
echo "2) Edite .env e preencha as variáveis necessárias"
echo "3) Se houver migrations a aplicar, rode o comando apropriado (ex: alembic upgrade head ou flask db upgrade)"
echo "4) Inicie o backend: python nexus_main.py  (ver README para comando exato)"

echo "Se quiser que eu execute alterações adicionais (ex: rodar migrations, criar um SQLite 'dev.db', ou configurar Docker Compose), diga o que prefere e eu atualizo os arquivos." 

exit 0
